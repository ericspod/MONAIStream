# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable
import torch

from monaistream.gstreamer import Gst, GstBase, GObject
from monaistream.gstreamer.utils import (
    get_video_pad_template,
    get_buffer_tensor,
    map_buffer_to_tensor,
    DEFAULT_CAPS_STR,
)

__all__ = ["TensorVideomixer"]


class TensorData:
    def __init__(self):
        self.tensors = []
        self.pts = 0
        self.eos = True


class TensorVideomixer(GstBase.Aggregator):
    """
    Example usage:

    gst-launch-1.0 tensorvideomixer name=mixer ! video/x-raw,format={RGB},width=400,height=400 ! jpegenc ! filesink location=img.jpg \
        videotestsrc num-buffers=1 ! video/x-raw,format={RGB},width=400,height=400 ! mixer. \
        videotestsrc num-buffers=1 pattern=ball ! video/x-raw,format={RGB},width=400,height=400 ! mixer. \
        videotestsrc num-buffers=1 pattern=snow ! video/x-raw,format={RGB},width=400,height=400 ! mixer.

    It seems necessary to specify the output caps for the mixer as it currently is without any cap negotiation.
    """

    __gstmetadata__ = ("Tensor Mixer", "Transform", "Description", "Author")

    __gsttemplates__ = (
        Gst.PadTemplate.new_with_gtype(
            "sink_%u",
            Gst.PadDirection.SINK,
            Gst.PadPresence.REQUEST,
            Gst.Caps.from_string(DEFAULT_CAPS_STR),
            GstBase.AggregatorPad.__gtype__,
        ),
        Gst.PadTemplate.new_with_gtype(
            "src",
            Gst.PadDirection.SRC,
            Gst.PadPresence.ALWAYS,
            Gst.Caps.from_string(DEFAULT_CAPS_STR),
            GstBase.AggregatorPad.__gtype__,
        ),
    )

    def __init__(self):
        super().__init__()
        self.callback = lambda x: torch.mean(torch.stack(x).float(), axis=0).byte()

    def mix_buffers(self, agg, pad, bdata):
        buf = pad.pop_buffer()

        if buf:
            tensor = get_buffer_tensor(buf, Gst.MapFlags.READ, pad.get_current_caps())

            bdata.tensors.append(tensor)
            bdata.pts = buf.pts

            bdata.eos = False

        return True

    def do_aggregate(self, timeout):
        bdata = TensorData()

        self.foreach_sink_pad(self.mix_buffers, bdata)

        if bdata.tensors:
            output = self.callback(bdata.tensors)
            print(output.shape)
            data = output.cpu().numpy().tobytes()

            outbuf = Gst.Buffer.new_allocate(None, len(data), None)
            outbuf.fill(0, data)
            outbuf.pts = bdata.pts
            self.finish_buffer(outbuf)

        # We are EOS when no pad was ready to be aggregated,
        # this would obviously not work for live
        if bdata.eos:
            return Gst.FlowReturn.EOS
        return Gst.FlowReturn.OK


GObject.type_register(TensorVideomixer)
__gstelementfactory__ = ("tensorvideomixer", Gst.Rank.NONE, TensorVideomixer)
