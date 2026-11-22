"""Testes sintéticos de SPURS JobQueue: zero bytes reais de jogos."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from prepare_jobqueue import (
    fnv1a64, expected_jobs, inspect_dumps, lift_commands,
    generate, verify_generated_source, MAX_LOCAL_STORE,
)


def setup_fixture(root, n=15):
    upstream = root / "upstream"
    dumps = root / "dumps"
    runtime = root / "runtime"
    (upstream / "src/gen").mkdir(parents=True)
    (runtime / "tools").mkdir(parents=True)
    for name in ("find_spu_functions.py", "spu_lifter.py"):
        (runtime / "tools" / name).touch()
    dumps.mkdir()
    entries = []
    for i in range(n):
        # Bytes não comerciais, distintos, alinhados ao tamanho de palavra SPU.
        raw = bytes([i, 42, i ^ 83, 99, i + 1, 0, 0, 1])
        fp = f"{fnv1a64(raw):016X}"
        (dumps / f"spujob_{fp}_{len(raw)}.bin").write_bytes(raw)
        entries.append(
            f"spu_workload_register_img(0x{fp}ULL, job_{fp}_spu_func_00000000, "
            f"{i + 13}, \"job_{fp}\");")
    (upstream / "src/gen/spu_jobs.c").write_text("\n".join(entries), encoding="utf-8")
    return upstream, runtime, dumps


class JobqueueTests(unittest.TestCase):
    def test_fnv_reference_basis(self):
        self.assertEqual(fnv1a64(b""), 1469598103934665603)
        self.assertNotEqual(fnv1a64(b"aaaa"), fnv1a64(b"aaab"))

    def test_all_15_synthetic_dumps(self):
        with tempfile.TemporaryDirectory() as tmp:
            upstream, _, dumps = setup_fixture(Path(tmp))
            report = inspect_dumps(upstream, dumps)
            self.assertTrue(report["ready"])
            self.assertEqual(report["expected"], 15)
            self.assertEqual(len(report["matched"]), 15)
            self.assertFalse(report["missing"])

    def test_missing_and_bad_size_and_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            upstream, _, dumps = setup_fixture(Path(tmp))
            paths = sorted(dumps.iterdir())
            paths[0].unlink()
            broken = paths[1]
            broken.write_bytes(b"not same")
            report = inspect_dumps(upstream, dumps)
            self.assertFalse(report["ready"])
            self.assertEqual(len(report["missing"]), 2)
            self.assertTrue(any("FNV" in err for err in report["invalid"]))
            first = paths[2]
            first.rename(first.with_name(first.name.replace("_8.bin", "_262145.bin")))
            report2 = inspect_dumps(upstream, dumps)
            self.assertTrue(any("tamanho declarado inválido" in err
                                for err in report2["invalid"]))

    def test_parser_detects_modified_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            upstream, _, dumps = setup_fixture(Path(tmp))
            registry = upstream / "src/gen/spu_jobs.c"
            lines = registry.read_text().splitlines()
            registry.write_text("\n".join(lines[:-1]))
            with self.assertRaisesRegex(ValueError, "15 jobs"):
                expected_jobs(registry)

    def test_commands_are_raw_and_target_expected_symbols(self):
        with tempfile.TemporaryDirectory() as tmp:
            upstream, runtime, dumps = setup_fixture(Path(tmp))
            report = inspect_dumps(upstream, dumps)
            fp, data = sorted(report["matched"].items())[0]
            out, commands = lift_commands(runtime, upstream, fp, data["file"])
            self.assertEqual(len(commands), 2)
            self.assertIn("--raw", commands[0])
            self.assertIn("--functions", commands[1])
            self.assertIn("job_" + fp + "_", commands[1])
            self.assertTrue(out.name.endswith(fp))

    def test_generation_checks_actual_definitions_and_includes(self):
        with tempfile.TemporaryDirectory() as tmp:
            upstream, runtime, dumps = setup_fixture(Path(tmp))
            report = inspect_dumps(upstream, dumps)
            invocations = []
            def fake_runner(command, **kwargs):
                invocations.append(command)
                if command[1].endswith("spu_lifter.py"):
                    prefix = command[command.index("--symbol-prefix") + 1]
                    outdir = Path(command[command.index("--output") + 1])
                    (outdir / "spu_recomp.h").write_text(
                        '#include "../../runtime/spu/spu_context.h"\n', encoding="utf-8")
                    (outdir / "spu_recomp.c").write_text(
                        '#include "../../runtime/spu/spu_helpers.h"\n'
                        f"void {prefix}spu_func_00000000(spu_context* ctx) {{}}\n"
                        f"void {prefix}spu_recomp_register(void) {{}}\n",
                        encoding="utf-8")
                return SimpleNamespace(returncode=0)
            manifest = generate(upstream, runtime, report, runner=fake_runner)
            self.assertTrue(manifest.is_file())
            self.assertEqual(len(invocations), 30)
            for fp in report["matched"]:
                source = upstream / "src/spu_gen" / ("job_" + fp) / "spu_recomp.c"
                self.assertTrue(verify_generated_source(source, fp))
                self.assertIn('#include "spu_helpers.h"', source.read_text())
                self.assertNotIn("../../runtime/", source.read_text())
            with self.assertRaisesRegex(ValueError, "--overwrite"):
                generate(upstream, runtime, report, runner=fake_runner)

    def test_fake_declarations_do_not_count_as_lifted(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "spu_recomp.c"
            source.write_text(
                "extern void job_1234567890123456_spu_func_00000000(spu_context*);\n"
                "/* void job_1234567890123456_spu_recomp_register(void) {} */\n")
            self.assertFalse(verify_generated_source(source, "1234567890123456"))

    def test_max_ls_is_bounded(self):
        self.assertEqual(MAX_LOCAL_STORE, 0x40000)


if __name__ == "__main__":
    unittest.main()
