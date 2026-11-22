import hashlib
import tempfile
import unittest
from pathlib import Path
from check_elf_version import KNOWN, classify_hash, classify_file

class IdentityTests(unittest.TestCase):
    def test_two_distinct_targets(self):
        self.assertEqual(len({info["sha256"] for info in KNOWN.values()}), 2)
        for name, info in KNOWN.items():
            self.assertEqual(classify_hash(info["sha256"]), name)

    def test_unknown_is_rejected(self):
        self.assertEqual(classify_hash("0" * 64), "unknown")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.elf"
            path.write_bytes(b"synthetic-not-game-data")
            result = classify_file(path)
            self.assertEqual(result["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(result["version"], "unknown")
            self.assertFalse(result["matched"])

if __name__ == "__main__":
    unittest.main()
