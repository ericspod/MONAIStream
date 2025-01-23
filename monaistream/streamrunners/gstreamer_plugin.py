import inspect

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstBase", "1.0")
from gi.repository import Gst, GLib, GObject, GstBase

import numpy as np


FORMATS = "{RGBx,BGRx,xRGB,xBGR,RGBA,BGRA,ARGB,ABGR,RGB,BGR}"


def register(runner_type, runner_alias):
    RunnerType = GObject.type_register(runner_type)
    if not Gst.Element.register(None, runner_alias, Gst.Rank.NONE, RunnerType):
        raise RuntimeError(f"Failed to register {runner_alias}; you may be missing gst-python plugins")



class GstInPlaceStreamRunner(GstBase.BaseTransform):
    """
    TODO:
     - specify source/sink one of several ways:
       - pipeline descriptor string
       - presets that look up descriptor strings (with argument specification)
     - move runner class inside a factory class
       - the runner is constructed

    TODO: Turn into usage guidelines

    Gst.init()

    class MyInPlaceOp(GstInPlaceStreamRunner):

        def do_op(self, data):
            data += 1

    def run_pipeline(src_descriptor, dest_descriptor):

        register(MyInPlaceOp, 'myop')

        pipeline_descriptor = (
            f'{src_descriptor} '
            '! rtph264depay '
            '! avdec_h264 '
            '! videoconvert '
            '! queue '
            '! myop '
            '! queue '
            '! videoconvert '
            '! x264enc tune=zerolatency '
            '! rtph264pay '
            f'! {dest_descriptor}'
        )

        pipeline = Gst.parse_launch(pipeline_descriptor)

        pipeline.set_state(Gst.State.PLAYING)

        loop = GLib.MainLoop()
        try:
            print("running loop")
            loop.run()
        except KeyboardInterrupt:
            raise
        finally:
            pipeline.set_state(Gst.State.NULL)

    if __name__ == '__main__':

        run_pipeline(
            'udpsrc address=0.0.0.0 port=5001 caps=application/x-rtp,media=video,payout=96,encoding-name=H264',
            'udpsink host=255.255.255.255 port=5002'
        )
    """

    GST_PLUGIN_NAME = "gstinplacestreamrunner"

    __gstmetadata__ = ("Gst In Place Stream Runner", "Transform", "Description", "Author")

    __gsttemplates__ = (
        Gst.PadTemplate.new(
           "src", Gst.PadDirection.SRC, Gst.PadPresence.ALWAYS, Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")
        ),
        Gst.PadTemplate.new(
           "sink", Gst.PadDirection.SINK, Gst.PadPresence.ALWAYS, Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")
        ),
    )

    __gstproperties__ = {}

    def do_op(self, data):
        raise NotImplementedError()

    def do_transform_ip(self, buffer: Gst.Buffer) -> Gst.FlowReturn:
        print("do_transform_ip")

        cstruct = self.srcpad.get_current_caps().get_structure(0)
        height = cstruct.get_value("height")
        width = cstruct.get_value("width")
        format = cstruct.get_value("format")

        is_mapped, map_info = buffer.map(Gst.MapFlags.WRITE)

        if is_mapped:
            data = np.ndarray((height, width, len(format)), dtype=np.uint8, buffer=map_info.data)
            data = self.do_op(data)
            buffer.unmap(map_info)
        else:
            raise RuntimeError("Mapping failed")

        return Gst.FlowReturn.OK


class GstAdaptorStreamRunner(GstBase.BaseTransform):
    """
    TODO:
     - specify source/sink one of several ways:
       - pipeline descriptor string
       - presets that look up descriptor strings (with argument specification)
     - move runner class inside a factory class
       - the runner is constructed

    TODO: Turn into usage guidelines

    Gst.init()

    class MyAdaptorOp(GstAdaptorStreamRunner):

        def do_op(self, src_data, snk_data):
            snk_data[...] = src_data[:snk_data.shape[0], :snk_data.shape[1], :]

    def run_pipeline(src_descriptor, dest_descriptor):

        register(MyAdaptorOp, 'myop')

        pipeline_descriptor = (
            f'{src_descriptor} '
            '! rtph264depay '
            '! avdec_h264 '
            '! videoconvert '
            '! queue '
            '! myop '
            '! queue '
            '! videoconvert '
            '! x264enc tune=zerolatency '
            '! rtph264pay '
            f'! {dest_descriptor}'
        )

        pipeline = Gst.parse_launch(pipeline_descriptor)

        pipeline.set_state(Gst.State.PLAYING)

        loop = GLib.MainLoop()
        try:
            print("running loop")
            loop.run()
        except KeyboardInterrupt:
            raise
        finally:
            pipeline.set_state(Gst.State.NULL)

    if __name__ == '__main__':

        run_pipeline(
            'udpsrc address=0.0.0.0 port=5001 caps=application/x-rtp,media=video,payout=96,encoding-name=H264',
            'udpsink host=255.255.255.255 port=5002'
        )
    """

    GST_PLUGIN_NAME = "gstadaptorstreamrunner"

    __gstmetadata__ = ("Adaptor Stream Runner", "Transform", "Description", "Author")

    __gsttemplates__ = (
        Gst.PadTemplate.new(
           "sink", Gst.PadDirection.SINK, Gst.PadPresence.ALWAYS, Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")
        ),
        Gst.PadTemplate.new(
           "src", Gst.PadDirection.SRC, Gst.PadPresence.ALWAYS, Gst.Caps.from_string(f"video/x-raw,format={FORMATS}")
        ),
    )
    def __init__(self, width=None, height=None):
        super().__init__()
        self.width = width
        self.height = height

    def do_op(self, data):
        raise NotImplementedError()

    def do_get_property(self, prop):
        if prop.name == "width":
            return self.width
        elif prop.name == "height":
            return self.height
        else:
            raise AttributeError(f"No such property {prop.name}")

    def do_set_property(self, prop, value):
        if prop.name == "width":
            self.width = value
        elif prop.name == "height":
            self.height = value
        else:
            raise AttributeError(f"No such property {prop.name}")

    def do_transform(self, in_buffer: Gst.Buffer, out_buffer: Gst.Buffer) -> Gst.FlowReturn:

        in_cstruct = self.sinkpad.get_current_caps().get_structure(0)
        in_height = in_cstruct.get_value("height")
        in_width = in_cstruct.get_value("width")
        in_format = in_cstruct.get_value("format")

        out_cstruct = self.srcpad.get_current_caps().get_structure(0)
        out_height = out_cstruct.get_value("height")
        out_width = out_cstruct.get_value("width")
        out_format = out_cstruct.get_value("format")

        print(f"from ({in_height, in_width, in_format}) to ({out_height, out_width, out_format})")

        snk_is_mapped, snk_map_info = in_buffer.map(Gst.MapFlags.READ)
        src_is_mapped, src_map_info = out_buffer.map(Gst.MapFlags.WRITE)

        if snk_is_mapped and src_is_mapped:
            in_data = np.ndarray((in_height, in_width, len(in_format)), dtype=np.uint8, buffer=snk_map_info.data)
            out_data = np.ndarray((out_height, out_width, len(out_format)), dtype=np.uint8, buffer=src_map_info.data)
            self.do_op(in_data, out_data)
            in_buffer.unmap(snk_map_info)
            out_buffer.unmap(src_map_info)
        else:
            raise RuntimeError("Mapping failed: source mapping status={src_is_mapped}; sink mapping status={sink_is_mapped}")

        return Gst.FlowReturn.OK
