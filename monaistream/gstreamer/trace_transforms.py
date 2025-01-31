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


from time import perf_counter
from gi.repository import GObject, Gst, GstBase

from monaistream.gstreamer.utils import get_video_pad_template, map_buffer_to_numpy

__all__ = ["PrintTransform"]


class PrintTransform(GstBase.BaseTransform):
    """ """

    __gstmetadata__ = ("Print Transform", "Transform", "Description", "Author")

    __gsttemplates__ = (
        get_video_pad_template("src", Gst.PadDirection.SRC),
        get_video_pad_template("sink", Gst.PadDirection.SINK),
    )

    def do_transform_ip(self, buffer: Gst.Buffer) -> Gst.FlowReturn:
        """ """
        with map_buffer_to_numpy(buffer, Gst.MapFlags.READ, self.sinkpad.get_current_caps()) as image_array:
            height, width, _ = image_array.shape
            imin = image_array.min()
            imax = image_array.max()

        print(f"{perf_counter():20} dim={width}x{height} min={imin} max={imax}")

        return Gst.FlowReturn.OK


GObject.type_register(PrintTransform)
__gstelementfactory__ = ("printtransform", Gst.Rank.NONE, PrintTransform)
