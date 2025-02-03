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
import unittest
from tempfile import TemporaryDirectory

import torch
from monai.handlers import MeanSquaredError, from_engine
from monai.bundle import ConfigWorkflow
from monai.utils import CommonKeys
from parameterized import parameterized

from monaistream.gstreamer import Gst
from monaistream import InferenceEngine
from monaistream.gstreamer.launch import default_loop_runner
from tests.utils import SkipIfNoModule

DEVICES = ["cpu"]
if torch.cuda.is_available:
    DEVICES.append("cuda:0")


@SkipIfNoModule("ignite")
class TestNumpyInplaceTransform(unittest.TestCase):
    def setUp(self):
        self.rand_input = torch.rand(1, 16, 16)

    @parameterized.expand(DEVICES)
    def test_single_input(self, device):
        net = torch.nn.Identity()
        engine = InferenceEngine(network=net, device=device)

        result = engine(self.rand_input)

        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, self.rand_input.shape)
        self.assertEqual(result.device, torch.device(device))

    @parameterized.expand(DEVICES)
    def test_two_inputs(self, device):
        net = torch.nn.Identity()
        engine = InferenceEngine(network=net, device=device)

        result1 = engine(self.rand_input.to(device))
        result2 = engine(self.rand_input.to(device))

        self.assertIsInstance(result1, torch.Tensor)
        self.assertIsInstance(result2, torch.Tensor)

        self.assertEqual(result1.shape, self.rand_input.shape)
        self.assertEqual(result2.shape, self.rand_input.shape)

        self.assertEqual(engine.state.iteration, 1)

    @parameterized.expand(DEVICES)
    def test_metric(self, device):
        net = torch.nn.Identity()
        metric = MeanSquaredError(output_transform=from_engine([CommonKeys.IMAGE, CommonKeys.PRED]))
        engine = InferenceEngine(network=net, device=device, key_val_metric={"mse": metric},use_interrupt=False)

        result, mets = engine(self.rand_input.to(device), include_metrics=True)

        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, self.rand_input.shape)
        self.assertIsInstance(mets, dict)
        self.assertIn("mse", mets)
        self.assertEqual(mets["mse"], 0)

    def test_bundle_stream(self):
        bundle_dir=os.path.dirname(__file__)+"/test_bundles/blur"
        bw=ConfigWorkflow(bundle_dir+"/configs/stream.json",bundle_dir+"/configs/metadata.json",workflow_type="infer")

        bw.initialize()
        cb=bw.run()
        self.assertEqual(len(cb), 1)
        self.assertIsInstance(cb[0],InferenceEngine)

        with TemporaryDirectory() as td:
            pipeline=Gst.parse_launch(f"videotestsrc num-buffers=1 ! tensorcallbacktransform name=t ! jpegenc ! filesink location={td}/img.jpg")

            tcbt=pipeline.get_by_name("t")
            tcbt.trans_fn=cb[0]

            default_loop_runner(pipeline,None)
            self.assertTrue(os.path.isfile(os.path.join(td, "img.jpg")))


if __name__ == "__main__":
    unittest.main()
