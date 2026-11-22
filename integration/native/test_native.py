import hashlib
import tempfile
import unittest
from pathlib import Path
from doctor import inspect, DISC_100_SHA256, UPSTREAM_FILES, RUNTIME_FILES, file_digest
from build_windows import build_commands

class NativePortTests(unittest.TestCase):
    def make_tree(self, root):
        upstream, runtime = root / "twistedmetal", root / "ps3recomp"
        for rel in UPSTREAM_FILES + ("src/recomp/code.cpp", "src/recomp/ppu_recomp.h",
                                      "src/spu_gen/job/spu_recomp.c"):
            path = upstream / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        for rel in RUNTIME_FILES + ("build/ps3recomp_runtime.lib",):
            path = runtime / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return upstream, runtime

    def test_missing_eboot_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            up, rt = self.make_tree(Path(folder))
            result = inspect(up, rt, is_windows=True, command=lambda _: "/fake")
            self.assertFalse(result["ready"])
            self.assertEqual(result["generated_ppu_files"], 1)
            self.assertEqual(result["generated_spu_files"], 1)
            self.assertTrue(any("EBOOT" in error for error in result["errors"]))

    def test_unknown_elf_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            up, rt = self.make_tree(Path(folder))
            elf = Path(folder) / "EBOOT.ELF"
            elf.write_bytes(b"synthetic test input, not a game")
            self.assertEqual(file_digest(elf), hashlib.sha256(elf.read_bytes()).hexdigest())
            self.assertNotEqual(file_digest(elf), DISC_100_SHA256)
            out = inspect(up, rt, elf, is_windows=True, command=lambda _: "/fake")
            self.assertFalse(out["ready"])
            self.assertEqual(out["eboot_version"], "unknown-or-update")

    def test_missing_generated_code_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            up, rt = self.make_tree(Path(folder))
            (up / "src/recomp/code.cpp").unlink()
            (rt / "build/ps3recomp_runtime.lib").unlink()
            out = inspect(up, rt, is_windows=True, command=lambda _: "/fake")
            self.assertTrue(any("PPU gerado" in e for e in out["errors"]))
            self.assertTrue(any("Runtime não compilado" in e for e in out["errors"]))

    def test_cmake_uses_explicit_runtime(self):
        cmds = build_commands("workspace/twistedmetal", "workspace/ps3recomp", "workspace/build")
        self.assertEqual(len(cmds), 2)
        self.assertIn("Ninja", cmds[0])
        self.assertIn("-DCMAKE_CXX_COMPILER=clang-cl", cmds[0])
        self.assertTrue(any(a.startswith("-DPS3RECOMP_RUNTIME_LIB=") for a in cmds[0]))

if __name__ == "__main__":
    unittest.main()
