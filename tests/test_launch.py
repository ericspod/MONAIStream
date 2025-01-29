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
import os
import unittest
from tempfile import TemporaryDirectory

from tests.utils import SkipIfNoModule
from subprocess import CalledProcessError, check_output, STDOUT

from monaistream.gstreamer.launch import launch


@SkipIfNoModule("gi")
class TestLaunch(unittest.TestCase):
    def test_simple_pipeline(self):
        """
        Test a simple pipeline with the launch program.
        """

        with TemporaryDirectory() as tempdir:
            launch(f"videotestsrc num-buffers=1 ! jpegenc ! filesink location={tempdir}/img.jpg")

            assert os.path.isfile(f"{tempdir}/img.jpg")

    def test_split_pipeline(self):
        """
        Test a pipeline defined as a list of components.
        """

        with self.subTest("Transforms in separate strings"):
            with TemporaryDirectory() as tempdir:
                launch(["videotestsrc num-buffers=1", "jpegenc", f"filesink location={tempdir}/img.jpg"])

                assert os.path.isfile(f"{tempdir}/img.jpg")

        with self.subTest("Transforms and arguments split into separate strings"):
            with TemporaryDirectory() as tempdir:
                launch(
                    ["videotestsrc", "num-buffers=1", "!", "jpegenc", "!", "filesink", f"location={tempdir}/img.jpg"]
                )

                assert os.path.isfile(f"{tempdir}/img.jpg")

    def test_launch_program(self):
        import monaistream.gstreamer

        pipeline = "-m monaistream.gstreamer.launch videotestsrc num-buffers=1 ! jpegenc ! filesink location=img.jpg"

        with TemporaryDirectory() as td:
            try:
                check_output([sys.executable] + list(pipeline.split()), cwd=td, stderr=STDOUT)
            except CalledProcessError as cpe:
                print(f"Output {sys.executable}:\n{cpe.output!r}\n{cpe.stderr!r}", file=sys.stderr, flush=True)
                raise

            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))


if __name__ == "__main__":
    unittest.main()
