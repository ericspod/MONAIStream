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

import sys
import traceback
import monaistream.gstreamer
import gi
from gi.repository import Gst, GLib


def default_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    if message.type == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err, debug,file=sys.stderr)
        loop.quit()
    elif message.type == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print(err, debug,file=sys.stderr)

    return True

def launch(args):
    args=list(map(str,args))
    if not args:
        raise ValueError("No arguments provided, a list of elements or a pipeline string is required.")
    
    if len(args)==1:
        command=args[0]
    elif "!" in args:
        command = " ".join(args)
    else:
        command = " ! ".join(args)

    pipeline = Gst.parse_launch(command)

    loop = GLib.MainLoop()
    
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", default_message, loop)

    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        raise
    finally:
        pipeline.set_state(Gst.State.NULL)
        if loop and loop.is_running():
            loop.quit()

    # bus = pipeline.get_bus()
    # bus.add_signal_watch()

    # pipeline.set_state(Gst.State.PLAYING)

    # loop = GLib.MainLoop()

    # bus.connect("message", on_message, loop)

    # try:
    #     loop.run()
    # except Exception:
    #     traceback.print_exc()
    #     loop.quit()

    # # Stop Pipeline
    # pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    launch(sys.argv[1:])


# python -m monaistream.gstreamer.launch videotestsrc num-buffers=1 ! video/x-raw,width=1280,height=720 ! jpegenc ! multifilesink location="img_%06d.jpg"