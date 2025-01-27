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

"""
This module contains code for GStreamer related components and plugins. It contains the utility definitions for use with
extension classes as well as Python based plugins which can be loaded with the gst-python module. This module requires
a list of directories be provided in the environment variable GST_PLUGIN_PATH. In these directories it looks for a 
subdirectory called "python" in which it expects plugin source files to load. This module adds its directory to this
variable and has a "python" symlink linking to its directory so that this mechanism works on import.
"""

import os

from monai.utils.module import optional_import

gi, HAS_GI = optional_import("gi")

if HAS_GI:
    plugin_path = os.environ.get("GST_PLUGIN_PATH", None)
    if plugin_path:
        plugin_path += ":" + os.path.dirname(__file__)
    else:
        plugin_path = os.path.dirname(__file__)

    os.environ["GST_PLUGIN_PATH"] = plugin_path  # set the plugin path so that this directory is searched

    gi.require_version("Gst", "1.0")
    gi.require_version("GstBase", "1.0")
    gi.require_version("GstVideo", "1.0")
    from gi.repository import Gst

    Gst.init([])
    # use GST_DEBUG instead https://gstreamer.freedesktop.org/documentation/gstreamer/running.html
    # Gst.debug_set_active(True)
    # Gst.debug_set_default_threshold(5)

    from monaistream.gstreamer.numpy_transforms import *
    from monaistream.gstreamer.utils import *

    # TODO: import more things here

# Silently import nothing if gi not present? If gi not present don't annoy user with warning on every import.
