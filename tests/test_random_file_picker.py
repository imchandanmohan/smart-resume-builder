import sys
import os
import unittest
from src.utils.random_speaker_picker import get_random_speaker_folder
# Add the root project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

class TestRandomFilePicker(unittest.TestCase):
    def test_returns_speaker_folder(self):
        speaker = get_random_speaker_folder()
        print("Speaker returned:", speaker)
        assert speaker is not None, "Function should return a speaker folder name"
        assert isinstance(speaker, str), "Returned value should be a string"
        assert speaker.startswith("en_speaker_"), "Speaker folder name should start with 'en_speaker_'"


if __name__ == "__main__":
    unittest.main()
