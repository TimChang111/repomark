import unittest
from pathlib import Path
import tempfile
from repomark.cli import is_text_file, estimate_tokens, pack_repository

class TestRepoMark(unittest.TestCase):
    def test_estimate_tokens(self):
        text = "Hello world, this is a test string."
        self.assertGreater(estimate_tokens(text), 0)

    def test_text_file_detection(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"plain text content")
            txt_path = Path(f.name)

        self.assertTrue(is_text_file(txt_path))
        txt_path.unlink()

    def test_pack_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_file = Path(tmpdir) / "app.py"
            sample_file.write_text("print('hello')", encoding="utf-8")

            result = pack_repository(Path(tmpdir))
            self.assertIn("app.py", result)
            self.assertIn("print('hello')", result)

if __name__ == "__main__":
    unittest.main()
