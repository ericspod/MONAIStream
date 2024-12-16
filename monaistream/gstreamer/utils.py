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

from contextlib import contextmanager
import numpy as np

from gi.repository import Gst, GstVideo

__all__ = ["BYTE_FORMATS", "get_dtype_from_bits", "map_buffer_to_numpy"]


BYTE_FORMATS = "{RGBx,BGRx,xRGB,xBGR,RGBA,BGRA,ARGB,ABGR,RGB,BGR,GRAY8,GRAY16_BE,GRAY16_LE}"


def get_video_pad_template(
    name, direction=Gst.PadDirection.SRC, presence=Gst.PadPresence.ALWAYS, caps_str=f"video/x-raw,format={BYTE_FORMATS}"
):
    return Gst.PadTemplate.new(name, direction, presence, Gst.Caps.from_string(caps_str))


def get_dtype_from_bits(bits):
    if bits == 8:
        return np.uint8
    elif bits == 16:
        return np.uint16
    elif bits == 32:
        return np.uint32  # TODO: or float32?
    else:
        raise ValueError(f"No obvious dtype for data items of size {bits}.")


def get_components(cformat):
    if cformat in ("RGB","BGR"):
        return 3
    if cformat in ("RGBx","BGRx","xRGB","xBGR","RGBA","BGRA","ARGB","ABGR"):
        return 4
    if cformat in ("GRAY8","GRAY16_BE","GRAY16_LE"):
        return 1

    raise ValueError(f"Format `{cformat}` does not have a known number of components.") 
    

@contextmanager
def map_buffer_to_numpy(buffer, flags, caps, dtype=None):
    cstruct = caps.get_structure(0)
    height = cstruct.get_value("height")
    width = cstruct.get_value("width")
    cformat = cstruct.get_value("format")

    fstruct = GstVideo.video_format_from_string(cformat)
    ifstruct = GstVideo.video_format_get_info(fstruct)

    if dtype is None:
        dtype = get_dtype_from_bits(ifstruct.bits)

    dtype=np.dtype(dtype)
    is_mapped, map_info = buffer.map(flags)
    if not is_mapped:
        raise ValueError(f"Buffer {buffer} failed to map with flags `{flags}`.")

    shape = (height, width, get_components(cformat))

    expected_size = np.product(shape) * dtype.itemsize
    if expected_size != buffer.get_size():
        raise ValueError(
            f"Buffer size {buffer.get_size()} does not match expected size {expected_size} for shape {shape} and format {cformat}."
        )

    # TODO: byte order for gray formats

    try:
        yield np.ndarray(shape, dtype=dtype, buffer=map_info.data)
    finally:
        buffer.unmap(map_info)
