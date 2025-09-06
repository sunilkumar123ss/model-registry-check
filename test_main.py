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

    def test_valid_manifest(self):
        self.assertEqual(verify({"entries": [self.entry]}, self.root)["production"], {"demo": "1.0.0"})

    def test_tampering(self):
        (self.root / "artifact.json").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify({"entries": [self.entry]}, self.root)

    def test_duplicate_production_and_missing_evaluation(self):
        second = copy.deepcopy(self.entry)
        second["version"] = "1.1.0"
        with self.assertRaisesRegex(ValueError, "one production"):
            verify({"entries": [self.entry, second]}, self.root)
        del second["evaluation"]
        with self.assertRaisesRegex(ValueError, "dataset"):
            verify({"entries": [second]}, self.root)

