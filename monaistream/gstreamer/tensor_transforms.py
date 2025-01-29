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

from monaistream.gstreamer import Gst, GstBase, GObject
from monaistream.gstreamer.utils import get_video_pad_template
from monaistream.gstreamer.utils import map_buffer_to_tensor

__all__ = ["TensorInplaceTransform"] #["TensorCallbackTransform"]


class TensorInplaceTransform(GstBase.BaseTransform):
    """ """

    __gstmetadata__ = ("Tensor Inplace Transform", "Transform", "Description", "Author")

    __gsttemplates__ = (
        get_video_pad_template("src", Gst.PadDirection.SRC),
        get_video_pad_template("sink", Gst.PadDirection.SINK),
    )

    def do_transform_ip(self, buffer: Gst.Buffer) -> Gst.FlowReturn:
        """ """
        with map_buffer_to_tensor(buffer, Gst.MapFlags.WRITE, self.sinkpad.get_current_caps()) as image_array:
            height, width, _ = image_array.shape
            image_array[: height // 2, : width // 2] = 128

        return Gst.FlowReturn.OK
    

GObject.type_register(TensorInplaceTransform)
__gstelementfactory__ = ("tensorinplacetransform", Gst.Rank.NONE, TensorInplaceTransform)


# class TensorCallbackTransform(GstBase.BaseTransform):
#     """ """

#     __gstmetadata__ = ("Tensor Callback Transform", "Transform", "Description", "Author")  # TODO: correct info

#     __gsttemplates__ = (
#         get_video_pad_template("src", Gst.PadDirection.SRC),
#         get_video_pad_template("sink", Gst.PadDirection.SINK),
#     )

#     def __init__(self, trans_fn: Callable):
#         super().__init__()
#         self.trans_fn = trans_fn

#     def do_transform(self, inbuf: Gst.Buffer, outbuf: Gst.Buffer) -> Gst.FlowReturn:
#         """ """

#         with map_buffer_to_tensor(inbuf, Gst.MapFlags.READ, self.srcpad.get_current_caps()) as intensor:
#             with map_buffer_to_tensor(outbuf, Gst.MapFlags.WRITE, self.sinkpad.get_current_caps()) as outtensor:
#                 outtensor[:]=self.trans_fn(intensor)

#         return Gst.FlowReturn.OK


# GObject.type_register(TensorCallbackTransform)
# __gstelementfactory__ = ("tensorcallbacktransform", Gst.Rank.NONE, TensorCallbackTransform)
