#!/usr/bin/env python3
"""Preflight de build nativo Windows do disco 1.00; nunca baixa arquivos do jogo."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil

DISC_100_SHA256 = "269642a56f3c70be74df41049876887d07aedd4171ce18a481a05067b1b8564e"
UPSTREAM_FILES = (
    "CMakeLists.txt", "src/boot_main.cpp", "src/hle_extra.cpp",
    "src/tm_inflate.cpp", "src/vdec_mf.cpp", "src/vdec_hle.cpp",
    "src/gen/ppu_hle_nids.cpp", "src/gen/spu_jobs.c",
)
RUNTIME_FILES = (
    "runtime/ppu/ppu_loader.cpp", "runtime/ppu/ppu_hle.cpp",
    "runtime/ppu/ppu_sysprx.cpp", "runtime/ppu/ppu_fs.cpp",
    "include/ps3emu/ps3types.h",
)

def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def missing_spurs_job_symbols(upstream):
    """Conta definições reais presentes em fontes SPU, não extern/protótipos."""
    root = Path(upstream)
    registry = root / "src/gen/spu_jobs.c"
    if not registry.is_file():
        return []
    wanted = set(re.findall(
        r"extern\s+void\s+(job_[A-Za-z0-9_]+)\s*\(",
        registry.read_text(encoding="utf-8", errors="replace")))
    found = set()
    for path in (root / "src/spu_gen").rglob("*.c"):
        source = path.read_text(encoding="utf-8", errors="replace")
        for name in wanted:
            pattern = r"(?m)^\s*void\s+" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{"
            if re.search(pattern, source):
                found.add(name)
    return sorted(wanted - found)


def validate_jobqueue_manifest(upstream):
    """Prova a origem dos símbolos pelos hashes de fontes geradas localmente."""
    from prepare_jobqueue import expected_jobs, verify_generated_source

    root = Path(upstream)
    registry = root / "src/gen/spu_jobs.c"
    if not registry.is_file():
        return ["src/gen/spu_jobs.c não encontrado"]
    # Nos testes unitários anteriores o registro pode ser intencionalmente vazio.
    source = registry.read_text(encoding="utf-8", errors="replace")
    if "spu_workload_register_img" not in source:
        return []
    try:
        expected = expected_jobs(registry)
    except ValueError as exc:
        return ["Registro JobQueue inconsistente: " + str(exc)]
    path = root / "src/spu_gen/local-jobqueue-report.json"
    if not path.is_file():
        return ["Manifesto verificado ausente: execute prepare_jobqueue.py com os 15 dumps locais"]
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
        jobs = report["jobs"]
        if report.get("verified") is not True or report.get("job_count") != 15:
            return ["Manifesto não confirma 15 jobs SPURS reais"]
        keys = [row["fingerprint"] for row in jobs]
        if len(keys) != 15 or set(keys) != set(expected):
            return ["Manifesto não corresponde aos 15 fingerprints do registro"]
        for row in jobs:
            fp = row["fingerprint"]
            src = root / "src/spu_gen" / ("job_" + fp) / "spu_recomp.c"
            if not verify_generated_source(src, fp):
                return ["Job levantado sem funções definidas: " + fp]
            sha = hashlib.sha256(src.read_bytes()).hexdigest()
            if sha != row["source_sha256"]:
                return ["Job levantado alterado após validação: " + fp]
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return ["Manifesto JobQueue inválido: " + str(exc)]
    return []


def inspect(upstream, runtime, eboot=None, *, is_windows=None, command=None):
    """Somente verifica; não altera arquivos e não executa processos."""
    upstream, runtime = Path(upstream), Path(runtime)
    failures, warnings = [], []
    if is_windows is None:
        is_windows = os.name == "nt"
    if command is None:
        command = shutil.which
    if not is_windows:
        failures.append("Host não é Windows; upstream exige D3D12/clang-cl e bibliotecas Windows")
    for tool in ("cmake", "ninja", "clang-cl"):
        if not command(tool):
            failures.append("Ferramenta ausente no PATH: " + tool)
    if not upstream.is_dir():
        failures.append("Checkout upstream sp00nznet não encontrado: " + str(upstream))
    else:
        for rel in UPSTREAM_FILES:
            if not (upstream / rel).is_file():
                failures.append("Arquivo upstream ausente: " + rel)
    if not runtime.is_dir():
        failures.append("Checkout ps3recomp não encontrado: " + str(runtime))
    else:
        for rel in RUNTIME_FILES:
            if not (runtime / rel).is_file():
                failures.append("Arquivo runtime ausente: " + rel)
        if not (runtime / "build/ps3recomp_runtime.lib").is_file():
            failures.append("Runtime não compilado: build/ps3recomp_runtime.lib")
    ppu = list((upstream / "src/recomp").glob("*.cpp"))
    spu = list((upstream / "src/spu_gen").rglob("*.c"))
    if not ppu:
        failures.append("PPU gerado ausente: src/recomp/*.cpp (gerar com seu disco 1.00)")
    if not (upstream / "src/recomp/ppu_recomp.h").is_file():
        failures.append("Cabeçalho PPU ausente: src/recomp/ppu_recomp.h")
    if not spu:
        failures.append("SPU gerado ausente: src/spu_gen/**/*.c (gerar localmente)")
    missing_jobs = missing_spurs_job_symbols(upstream)
    if missing_jobs:
        failures.append(
            "Módulos JobQueue SPURS faltantes: " + str(len(missing_jobs)) +
            " símbolo(s), por exemplo " + ", ".join(missing_jobs[:3]))
    if not (upstream / "src/gen/spu_jobs.c").is_file():
        failures.append("Registro de JobQueue SPURS ausente: src/gen/spu_jobs.c")
    jobqueue_errors = validate_jobqueue_manifest(upstream)
    failures.extend(jobqueue_errors)
    version = "not-provided"
    if eboot is None:
        failures.append("Informe --eboot com EBOOT.ELF original do disco 1.00")
    elif not Path(eboot).is_file():
        failures.append("EBOOT.ELF não encontrado: " + str(eboot))
        version = "missing"
    else:
        try:
            digest = file_digest(eboot)
        except OSError as exc:
            failures.append("Falha lendo EBOOT.ELF: " + str(exc))
            version = "unreadable"
        else:
            version = "disc-1.00" if digest == DISC_100_SHA256 else "unknown-or-update"
            if version != "disc-1.00":
                failures.append("EBOOT incompatível com o upstream 1.00: SHA-256 " + digest + "; não misturar com 1.06")
    warnings.append("Confira a proveniência local dos arquivos C++ gerados; este teste NÃO comprova vínculo com o ELF")
    warnings.append("Preflight aprovado não prova boot, gráficos, controles ou gameplay")
    return {"ready": not failures, "target": "BCUS98106-disc-1.00",
            "upstream": str(upstream), "runtime": str(runtime),
            "eboot_version": version, "generated_ppu_files": len(ppu),
            "generated_spu_files": len(spu), "missing_job_symbols": missing_jobs, "jobqueue_manifest_errors": jobqueue_errors, "errors": failures, "warnings": warnings}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--eboot", type=Path, help="EBOOT.ELF legal da sua cópia do disco 1.00")
    p.add_argument("--strict", action="store_true", help="Retorna código 2 se algo estiver faltando")
    a = p.parse_args(argv)
    result = inspect(a.upstream, a.runtime, a.eboot)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if a.strict and not result["ready"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
