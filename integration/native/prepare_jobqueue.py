#!/usr/bin/env python3
"""Valida e levanta jobs SPURS JobQueue a partir de dumps locais do runtime.

Alvo: BCUS98106 disco 1.00; os dumps vêm de SPU_DUMP_MISS do próprio usuário.
Não extrai, baixa nem incorpora recursos proprietários ao repositório.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REGISTER = re.compile(
    r"spu_workload_register_img\s*\(\s*0x([0-9A-Fa-f]{16})ULL\s*,\s*"
    r"job_([0-9A-Fa-f]{16})_spu_func_00000000\b")
DUMP_NAME = re.compile(r"spujob_([0-9A-Fa-f]{16})_(\d+)\.bin$", re.I)
MAX_LOCAL_STORE = 256 * 1024


def fnv1a64(data):
    # Precisamente a base e multiplicador de runtime/spu/spu_workload.c.
    h = 1469598103934665603
    for byte in data:
        h = ((h ^ byte) * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h


def expected_jobs(registry):
    text = Path(registry).read_text(encoding="utf-8")
    pairs = REGISTER.findall(text)
    if len(pairs) != 15:
        raise ValueError("Registro esperado deve conter 15 jobs; encontrado: " + str(len(pairs)))
    result = {}
    for key, symbol in pairs:
        if key.upper() != symbol.upper():
            raise ValueError("Fingerprint do registro difere do nome do símbolo: " + key)
        if key.upper() in result:
            raise ValueError("Fingerprint duplicado no registro: " + key)
        result[key.upper()] = "job_" + key.upper()
    return result


def inspect_dumps(upstream, dumps_dir):
    root = Path(upstream)
    dumps_dir = Path(dumps_dir)
    expected = expected_jobs(root / "src/gen/spu_jobs.c")
    matches, invalid, unrecognized = {}, [], []
    if not dumps_dir.is_dir():
        return {"expected": len(expected), "matched": {}, "missing": sorted(expected),
                "invalid": ["Diretório não encontrado: " + str(dumps_dir)],
                "unrecognized": [], "ready": False}
    for path in sorted(dumps_dir.iterdir()):
        if not path.is_file():
            continue
        match = DUMP_NAME.fullmatch(path.name)
        if not match:
            # Não lê outros arquivos; não altera nada.
            continue
        fp, claimed_len = match.groups()
        fp = fp.upper()
        length = int(claimed_len)
        if path.is_symlink():
            invalid.append(path.name + ": links simbólicos não são aceitos")
            continue
        if length < 4 or length > MAX_LOCAL_STORE or length % 4:
            invalid.append(path.name + ": tamanho declarado inválido para LS SPU")
            continue
        if path.stat().st_size != length:
            invalid.append(path.name + ": tamanho real não corresponde ao nome")
            continue
        data = path.read_bytes()
        actual = f"{fnv1a64(data):016X}"
        if actual != fp:
            invalid.append(path.name + ": FNV real " + actual + " diferente do nome")
            continue
        if fp not in expected:
            unrecognized.append(path.name + ": fingerprint válido mas não registrado neste port")
            continue
        if fp in matches:
            invalid.append(path.name + ": fingerprint duplicado")
            continue
        matches[fp] = {"file": str(path.resolve()), "bytes": length,
                       "sha256": hashlib.sha256(data).hexdigest()}
    missing = sorted(set(expected) - set(matches))
    return {"expected": len(expected), "matched": matches, "missing": missing,
            "invalid": invalid, "unrecognized": unrecognized,
            "ready": not missing and not invalid}


def lift_commands(runtime, upstream, fingerprint, dump_file):
    runtime = Path(runtime).resolve()
    upstream = Path(upstream).resolve()
    outdir = upstream / "src/spu_gen" / ("job_" + fingerprint)
    fnlist = outdir / "functions.json"
    detector = runtime / "tools/find_spu_functions.py"
    lifter = runtime / "tools/spu_lifter.py"
    return outdir, [
        [sys.executable, str(detector), str(dump_file),
         "--raw", "--base", "0", "--out", str(fnlist)],
        [sys.executable, str(lifter), str(dump_file),
         "--base", "0", "--functions", str(fnlist),
         "--symbol-prefix", "job_" + fingerprint + "_",
         "--output", str(outdir)]
    ]


def verify_generated_source(source, fingerprint):
    if not source.is_file():
        return False
    text = source.read_text(encoding="utf-8", errors="replace")
    # Definição real de função, não declaração extern, comentário ou protótipo.
    for symbol in ("job_" + fingerprint + "_spu_func_00000000",
                   "job_" + fingerprint + "_spu_recomp_register"):
        pattern = r"(?m)^\s*void\s+" + re.escape(symbol) + r"\s*\([^;{}]*\)\s*\{"
        if not re.search(pattern, text):
            return False
    return True


def generate(upstream, runtime, report, *, overwrite=False, runner=None):
    if not report["ready"]:
        raise ValueError("Dumps incompletos/inválidos: não foi iniciado nenhum lift")
    upstream, runtime = Path(upstream), Path(runtime)
    for tool in ("find_spu_functions.py", "spu_lifter.py"):
        if not (runtime / "tools" / tool).is_file():
            raise ValueError("Ferramenta ps3recomp ausente: " + tool)
    steps = []
    for fp, meta in sorted(report["matched"].items()):
        outdir, commands = lift_commands(runtime, upstream, fp, meta["file"])
        source = outdir / "spu_recomp.c"
        if source.exists() and not overwrite:
            raise ValueError(str(source) + ": já existe; use --overwrite")
        steps.append((fp, meta, outdir, source, commands))
    if runner is None:
        runner = subprocess.run
    generated = []
    for fp, meta, outdir, source, commands in steps:
        outdir.mkdir(parents=True, exist_ok=True)
        for cmd in commands:
            result = runner(cmd, check=False, cwd=str(Path(upstream).resolve()))
            if result.returncode:
                raise RuntimeError("Lifting JobQueue " + fp + " falhou (exit " +
                                   str(result.returncode) + ")")
        if not verify_generated_source(source, fp):
            raise RuntimeError("Símbolos SPU reais não encontrados após lift: " + fp)
        generated.append({"fingerprint": fp, "size": meta["bytes"],
                          "input_sha256": meta["sha256"],
                          "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    manifest = Path(upstream) / "src/spu_gen/local-jobqueue-report.json"
    manifest.write_text(json.dumps(
        {"target": "BCUS98106 disc 1.00", "job_count": len(generated),
         "jobs": generated, "verified": True}, indent=2), encoding="utf-8")
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--dumps", type=Path, required=True,
                   help="Pasta local produzida com SPU_DUMP_MISS")
    p.add_argument("--check", action="store_true", help="Somente valida arquivos, sem gerar código")
    p.add_argument("--plan", action="store_true", help="Exibe os comandos sem gravar arquivos")
    p.add_argument("--overwrite", action="store_true", help="Permite regenerar SPU já levantado")
    args = p.parse_args(argv)
    try:
        report = inspect_dumps(args.upstream, args.dumps)
        summary = {k: v for k, v in report.items() if k != "matched"}
        summary["matched_count"] = len(report["matched"])
        summary["matched_fingerprints"] = sorted(report["matched"])
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if not report["ready"]:
            return 2
        if args.check:
            return 0
        if args.plan:
            for fp, meta in sorted(report["matched"].items()):
                _, commands = lift_commands(args.runtime, args.upstream, fp, meta["file"])
                for command in commands:
                    print(subprocess.list2cmdline(command))
            return 0
        manifest = generate(args.upstream, args.runtime, report, overwrite=args.overwrite)
        print("Fontes SPU levantadas localmente; manifesto: " + str(manifest))
    except (OSError, RuntimeError, ValueError) as exc:
        print("ERRO: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
