
import os
import tempfile
import unittest
import uuid
from pathlib import Path

from astra_ai.types import AgentAudio, AgentImage, AgentText
from transformers.testing_utils import (
    require_soundfile,
    require_torch,
    require_vision,
)
from transformers.utils import (
    is_soundfile_availble,
)

import torch
from PIL import Image


if is_soundfile_availble():
    import soundfile as sf


def get_new_path(suffix="") -> str:
    directory = tempfile.mkdtemp()
    return os.path.join(directory, str(uuid.uuid4()) + suffix)


@require_soundfile
@require_torch
class AgentAudioTests(unittest.TestCase):
    def test_from_tensor(self):
        tensor = torch.rand(12, dtype=torch.float64) - 0.5
        agent_type = AgentAudio(tensor)
        path = str(agent_type.to_string())

        # Ensure that the tensor and the agent_type's tensor are the same
        self.assertTrue(torch.allclose(tensor, agent_type.to_raw(), atol=1e-4))

        del agent_type

        # Ensure the path remains even after the object deletion
        self.assertTrue(os.path.exists(path))

        # Ensure that the file contains the same value as the original tensor
        new_tensor, _ = sf.read(path)
        self.assertTrue(torch.allclose(tensor, torch.tensor(new_tensor), atol=1e-4))

    def test_from_string(self):
        tensor = torch.rand(12, dtype=torch.float64) - 0.5
        path = get_new_path(suffix=".wav")
        sf.write(path, tensor, 16000)

        agent_type = AgentAudio(path)

        self.assertTrue(torch.allclose(tensor, agent_type.to_raw(), atol=1e-4))
        self.assertEqual(agent_type.to_string(), path)


@require_vision
@require_torch
class AgentImageTests(unittest.TestCase):
    def test_from_tensor(self):
        tensor = torch.randint(0, 256, (64, 64, 3))
        agent_type = AgentImage(tensor)
        path = str(agent_type.to_string())

        # Ensure that the tensor and the agent_type's tensor are the same
        self.assertTrue(torch.allclose(tensor, agent_type._tensor, atol=1e-4))

        self.assertIsInstance(agent_type.to_raw(), Image.Image)

        # Ensure the path remains even after the object deletion
        del agent_type
        self.assertTrue(os.path.exists(path))

    def test_from_string(self):
        path = Path("tests/fixtures/000000039769.png")
        image = Image.open(path)
        agent_type = AgentImage(path)

        self.assertTrue(path.samefile(agent_type.to_string()))
        self.assertTrue(image == agent_type.to_raw())

        # Ensure the path remains even after the object deletion
        del agent_type
        self.assertTrue(os.path.exists(path))

    def test_from_image(self):
        path = Path("tests/fixtures/000000039769.png")
        image = Image.open(path)
        agent_type = AgentImage(image)

        self.assertFalse(path.samefile(agent_type.to_string()))
        self.assertTrue(image == agent_type.to_raw())

        # Ensure the path remains even after the object deletion
        del agent_type
        self.assertTrue(os.path.exists(path))


class AgentTextTests(unittest.TestCase):
    def test_from_string(self):
        string = "Hey!"
        agent_type = AgentText(string)

        self.assertEqual(string, agent_type.to_string())
        self.assertEqual(string, agent_type.to_raw())
        self.assertEqual(string, agent_type)
