

import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from transformers import is_torch_available
from transformers.testing_utils import get_tests_dir, require_torch
from astra_ai.types import AGENT_TYPE_MAPPING

from astra_ai.default_tools import FinalAnswerTool

from .test_tools import ToolTesterMixin


if is_torch_available():
    import torch


class FinalAnswerToolTester(unittest.TestCase, ToolTesterMixin):
    def setUp(self):
        self.inputs = {"answer": "Final answer"}
        self.tool = FinalAnswerTool()

    def test_exact_match_arg(self):
        result = self.tool("Final answer")
        self.assertEqual(result, "Final answer")

    def test_exact_match_kwarg(self):
        result = self.tool(answer=self.inputs["answer"])
        self.assertEqual(result, "Final answer")

    def create_inputs(self):
        inputs_text = {"answer": "Text input"}
        inputs_image = {
            "answer": Image.open(
                Path(get_tests_dir("fixtures")) / "000000039769.png"
            ).resize((512, 512))
        }
        inputs_audio = {"answer": torch.Tensor(np.ones(3000))}
        return {"string": inputs_text, "image": inputs_image, "audio": inputs_audio}

    @require_torch
    def test_agent_type_output(self):
        inputs = self.create_inputs()
        for input_type, input in inputs.items():
            output = self.tool(**input, sanitize_inputs_outputs=True)
            agent_type = AGENT_TYPE_MAPPING[input_type]
            self.assertTrue(isinstance(output, agent_type))
