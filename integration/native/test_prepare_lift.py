"""Tests synthetic only: never include game data or run the real lifter."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from doctor import DISC_100_SHA256
from prepare_lift import execute, plan_steps, validate_output, RUNTIME_TOOLS


class LiftTests(unittest.TestCase):
    def test_plan_targets_the_verified_100_addresses(self):
        steps = plan_steps("twistedmetal", "ps3recomp", "EBOOT.ELF", jobs=3)
        self.assertEqual([name for name, _ in steps], [
            "load_ppu", "find_ppu_functions", "extract_spu", "recarve_spu",
            "lift_ppu", "patch_ppu", "lift_embedded_spu"])
        self.assertIn("0xF21930", steps[4][1])
        self.assertIn("0xC79C6C", steps[4][1])
        self.assertIn("3", steps[4][1])
        self.assertIn("--constructor", steps[6][1])
        self.assertTrue(all(isinstance(cmd, list) for _, cmd in steps if cmd))

    def test_reject_synthetic_elf_before_any_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            elf = root / "EBOOT.ELF"
            elf.write_bytes(b"synthetic non-game fixture")
            with self.assertRaisesRegex(ValueError, "hash errado"):
                execute(root / "upstream", root / "runtime", elf)
            self.assertFalse((root / "upstream/meta").exists())

    def test_run_stages_use_mock_subprocess_and_never_execute_game(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            upstream, runtime = root / "tm", root / "ps3recomp"
            elf = root / "EBOOT.ELF"
            elf.write_bytes(b"synthetic sample protected by mocked hash")
            (upstream / "tools").mkdir(parents=True)
            (upstream / "tools/post_lift.py").touch()
            (runtime / "tools").mkdir(parents=True)
            for name in RUNTIME_TOOLS:
                (runtime / "tools" / name).touch()
            observed = []
            def fake_run(cmd, **_kwargs):
                observed.append(Path(cmd[1]).name)
                if cmd[1].endswith("ppu_lifter.py"):
                    ppu = upstream / "src/recomp"
                    ppu.mkdir(parents=True, exist_ok=True)
                    (ppu / "ppu_recomp.h").write_text("/* fake header */")
                    (ppu / "ppu_recomp_000.cpp").write_text("/* fake C++ */")
                if cmd[1].endswith("build_spu_workloads.py"):
                    spu = upstream / "src/spu_gen/image"
                    spu.mkdir(parents=True, exist_ok=True)
                    (spu / "spu_recomp.c").write_text("/* fake SPU */")
                    (upstream / "src/spu_gen/embedded_spu_workloads.c").write_text("/* fake registry */")
                return SimpleNamespace(returncode=0)
            with patch("prepare_lift.file_digest", return_value=DISC_100_SHA256), \
                 patch("prepare_lift.recarve_images", return_value={"spu_images": 1}):
                result = execute(upstream, runtime, elf, jobs=2, run=fake_run)
            self.assertTrue(result["generated"])
            self.assertEqual(result["jobqueue_15_status"], "not-covered; need observed job binaries")
            self.assertEqual(len(observed), 6)
            self.assertTrue((upstream / "meta/local-lift-report.json").is_file())

    def test_reject_overwrite_without_explicit_consent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            upstream, runtime = root / "tm", root / "ps3recomp"
            elf = root / "EBOOT.ELF"
            elf.write_bytes(b"synthetic sample")
            (upstream / "src/recomp").mkdir(parents=True)
            (upstream / "src/recomp/chunk.cpp").write_text("synthetic")
            (upstream / "tools").mkdir(parents=True)
            (upstream / "tools/post_lift.py").touch()
            (runtime / "tools").mkdir(parents=True)
            for name in RUNTIME_TOOLS:
                (runtime / "tools" / name).touch()
            with patch("prepare_lift.file_digest", return_value=DISC_100_SHA256):
                with self.assertRaisesRegex(ValueError, "--overwrite"):
                    execute(upstream, runtime, elf)

    def test_output_requires_ppu_and_spu(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(validate_output(Path(tmp))["generated"])


if __name__ == "__main__":
    unittest.main()
