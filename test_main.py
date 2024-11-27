import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from main import verify


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "artifact.json").write_text('{"synthetic":true}', encoding="utf-8")
        digest = hashlib.sha256((self.root / "artifact.json").read_bytes()).hexdigest()
        self.entry = dict(name="demo", version="1.0.0", stage="production", artifact="artifact.json",
                          sha256=digest, evaluation={"dataset": "synthetic-v1", "metrics": {"accuracy": 0.8}})

    def test_rejects_nonobject_evaluation(self):
        for value in ([], None, "invalid"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "evaluation must"):
                verify({"entries": [dict(self.entry, evaluation=value)]}, self.root)

    def test_rejects_nonobject_manifest_and_entry(self):
        for value in ([], {"entries": [None]}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify(value, self.root)

