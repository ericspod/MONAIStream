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
    def test_import(self):
        """
        Test importation of the transform.
        """
        from monaistream.gstreamer import NumpyInplaceTransform

    def test_pipeline(self):
        """
        Test the transform can be loaded with `parse_launchv`.
        """
        from gi.repository import Gst

        pipeline = Gst.parse_launchv(["videotestsrc", "numpyinplacetransform"])
        self.assertIsNotNone(pipeline)

    def test_gst_launch(self):
        """
        Test launching a separate pipeline subprocess with gst-launch-1.0 correctly imports the transform.
        """
        pipeline = "videotestsrc num-buffers=1 ! numpyinplacetransform ! jpegenc ! filesink location=img.jpg"

        with TemporaryDirectory() as td:
            try:
                check_call(["gst-launch-1.0"] + list(pipeline.split()), cwd=td)
            except CalledProcessError as cpe:
                print("Output gst-launch-1.0:\n", repr(cpe.output), file=sys.stderr)
                raise

            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))


if __name__ == "__main__":
    unittest.main()
