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
import unittest
from subprocess import CalledProcessError, check_output, STDOUT
from tempfile import TemporaryDirectory

from tests.utils import SkipIfNoModule


@SkipIfNoModule("gi")
class TestTensorInplaceTransform(unittest.TestCase):
    def test_import(self):
        """
        Test importation of the transform.
        """
        from monaistream.gstreamer.tensor_transforms import TensorInplaceTransform

    def test_pipeline(self):
        """
        Test the transform can be loaded with `parse_launchv`.
        """
        from monaistream.gstreamer import Gst

        self.assertIn("GST_PLUGIN_PATH", os.environ)

        pipeline = Gst.parse_launchv(["videotestsrc", "tensorinplacetransform"])
        self.assertIsNotNone(pipeline)

    def test_gst_launch(self):
        """
        Test launching a separate pipeline subprocess with gst-launch-1.0 correctly imports the transform.
        """
        import monaistream.gstreamer

        pipeline = "videotestsrc num-buffers=1 ! tensorinplacetransform ! jpegenc ! filesink location=img.jpg"

        with TemporaryDirectory() as td:
            try:
                check_output(["gst-launch-1.0"] + list(pipeline.split()), cwd=td, stderr=STDOUT)
            except CalledProcessError as cpe:
                print(f"Output gst-launch-1.0:\n{cpe.output!r}\n{cpe.stderr!r}", file=sys.stderr, flush=True)
                raise

            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))


class TestTensorVideoMixer(unittest.TestCase):
    def test_gst_launch(self):
        import monaistream.gstreamer

        pipeline = """
        gst-launch-1.0 tensorvideomixer name=mixer ! video/x-raw,format={RGB},width=400,height=400 ! jpegenc ! filesink location=img.jpg \
        videotestsrc num-buffers=1 ! video/x-raw,format={RGB},width=400,height=400 ! mixer. \
        videotestsrc num-buffers=1 pattern=ball ! video/x-raw,format={RGB},width=400,height=400 ! mixer. \
        videotestsrc num-buffers=1 pattern=snow ! video/x-raw,format={RGB},width=400,height=400 ! mixer.
        """

        with TemporaryDirectory() as td:
            try:
                check_output(pipeline.strip().split(" "), cwd=td, stderr=STDOUT)
            except CalledProcessError as cpe:
                print(f"Output gst-launch-1.0:\n{cpe.output!r}\n{cpe.stderr!r}", file=sys.stderr, flush=True)
                raise

            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))
            self.assertTrue(os.path.getsize("img.jpg") > 1024)  # file must be large enough to be a valid jpg


if __name__ == "__main__":
    unittest.main()
