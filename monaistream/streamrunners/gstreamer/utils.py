from dataclasses import dataclass

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject


def parse_node_entry(entry):
    element = Gst.parse_bin_from_description_full(
        entry.description, False, None, Gst.ParseFlags.NO_SINGLE_ELEMENT_BINS)

    if not element:
        raise ValueError(f"Failed to parse element {entry.description}")

    return element



def register(runner_type, runner_alias):
    RunnerType = GObject.type_register(runner_type)
    if not Gst.Element.register(None, runner_alias, Gst.Rank.NONE, RunnerType):
        raise ValueError(f"Failed to register {runner_alias}; you may be missing gst-python plugins")



def create_registerable_plugin(base_type, class_name, inputs, outputs, do_op):
    # TODO: is this class actually gstreamer specific?
    def init_with_do_op(self):
        base_type.__init__(self, inputs=inputs, outputs=outputs, do_op=do_op)

    sub_class_type = type(
        class_name,
        (base_type,),
        {
            "__init__": init_with_do_op,
        }
    )

    return sub_class_type



def run_pipeline(pipeline):
    pipeline.set_state(Gst.State.PLAYING)

    loop = GLib.MainLoop()
    try:
        print("running loop")
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("shutting down")
        if pipeline:
            pipeline.send_event(Gst.Event.new_eos())
            bus = pipeline.get_bus()
            msg = bus.timed_pop_filtered(2 * Gst.SECOND, Gst.MessageType.EOS)
            pipeline.set_state(Gst.State.NULL)
            # pipeline.get_state(Gst.CLOCK_TIME_NONE)
        if loop and loop.is_running():
            loop.quit()



@dataclass(frozen=True)
class PadEntry:
    name: str
    format: str



@dataclass(frozen=True)
class SubnetEntry:
    name: str
    description: str
