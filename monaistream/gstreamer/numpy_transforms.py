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


from gi.repository import GObject, Gst, GstBase

from monaistream.gstreamer.utils import (get_video_pad_template,
                                         map_buffer_to_numpy)

__all__=["NumpyInplaceTransform"]

class NumpyInplaceTransform(GstBase.BaseTransform):
    """ 
    """
    __gstmetadata__ = ("Numpy Inplace Transform", "Transform", "Description", "Author")

    __gsttemplates__ = (
        get_video_pad_template("src", Gst.PadDirection.SRC),
        get_video_pad_template("sink", Gst.PadDirection.SINK),
    )

    def do_transform_ip(self, buffer: Gst.Buffer) -> Gst.FlowReturn:
        """ 
        """
        with map_buffer_to_numpy(buffer, Gst.MapFlags.WRITE, self.sinkpad.get_current_caps()) as image_array:
            height, width, _ = image_array.shape
            image_array[: height // 2, : width // 2] = 128

        return Gst.FlowReturn.OK


GObject.type_register(NumpyInplaceTransform)
__gstelementfactory__ = ("numpyinplacetransform", Gst.Rank.NONE, NumpyInplaceTransform)
