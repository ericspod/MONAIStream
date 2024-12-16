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

import os
import sys
from tempfile import TemporaryDirectory
from subprocess import check_call, CalledProcessError
import unittest
from tests.utils import SkipIfNoModule


@SkipIfNoModule("gi")
class TestNumpyInplaceTransform(unittest.TestCase):
    # def setUp(self):
    #     cwd = os.getcwd()
    #     self.plink = os.path.join(cwd, "python")
    #     self.made_link = False
    #     if not os.path.isdir(self.plink):
    #         os.symlink(os.path.join(cwd, "monaistream", "gstreamer"), self.plink)
    #         self.made_link = True

    # def tearDown(self):
    #     if self.made_link:
    #         os.unlink(self.plink)

    def test_import(self):
        import monaistream

        print(monaistream)
        from monaistream.gstreamer import NumpyInplaceTransform

    def test_pipeline(self):
        from gi.repository import Gst

        Gst.parse_launchv(["videotestsrc", "numpyinplacetransform"])

        # old_val=os.environ.get("GST_PLUGIN_PATH", None)
        # os.environ["GST_PLUGIN_PATH"]= os.getcwd()
        # try:
        #     import monaistream.gstreamer
        #     from gi.repository import Gst

        #     Gst.parse_launchv(["videotestsrc", "numpyinplacetransform"])
        # finally:
        #     if old_val:
        #         os.environ["GST_PLUGIN_PATH"]=old_val
        #     else:
        #         os.environ.pop("GST_PLUGIN_PATH")

    def test_gst_launch(self):
        pipeline = "videotestsrc num-buffers=1 ! numpyinplacetransform ! jpegenc ! filesink location=img.jpg"

        with TemporaryDirectory() as td:
            try:
                check_call(["gst-launch-1.0"] + list(pipeline.split()), cwd=td)
            except CalledProcessError as cpe:
                print("Output gst-launch-1.0:\n", repr(cpe.output), file=sys.stderr)
                raise

            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))

    # def test_gst_launch(self):
    #     with TemporaryDirectory() as td:
    #         pipeline = (
    #             "videotestsrc num-buffers=1 ! video/x-raw ! numpyinplacetransform ! jpegenc ! filesink location=img.jpg"
    #         )
    #         env = os.environ.copy()
    #         env["PYTHONPATH"] = env["GST_PLUGIN_PATH"] = os.getcwd()

    #         try:
    #             check_call(["gst-launch-1.0"] + list(pipeline.split()), env=env, cwd=td)
    #         except CalledProcessError as cpe:
    #             print("Output gst-launch-1.0:\n", repr(cpe.output), file=sys.stderr)
    #             raise

    #         self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))


if __name__ == "__main__":
    unittest.main()
