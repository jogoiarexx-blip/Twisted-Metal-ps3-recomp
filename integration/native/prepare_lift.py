#!/usr/bin/env python3
"""Reproduz o lift PPU e de SPUs EMBUTIDOS do disco BCUS98106 1.00 no PC local.

Não decifra EBOOT.BIN, não baixa arquivos comerciais, não publica resultados.
Os 15 SPURS JobQueue jobs observados em execução NÃO são extraídos do EBOOT
por este pipeline; consulte doctor.py para verificar os símbolos faltantes.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from doctor import DISC_100_SHA256, file_digest

RUNTIME_TOOLS = (
    "ppu_loader.py", "find_functions.py", "extract_spu_images.py",
    "ppu_lifter.py", "build_spu_workloads.py",
)


def plan_steps(upstream, runtime, eboot, jobs=8):
    """Comandos de produção: paths absolutos, sem shell e sem cópia do ELF."""
    upstream, runtime, eboot = (Path(p).resolve() for p in (upstream, runtime, eboot))
    tools = runtime / "tools"
    meta = upstream / "meta"
    gen = upstream / "src/recomp"
    spugen = upstream / "src/spu_gen"
    spudir = meta / "spu"
    imports = meta / (eboot.stem + ".imports.json")
    return [
        ("load_ppu", [sys.executable, str(tools / "ppu_loader.py"),
                      str(eboot), "-o", str(meta)]),
        ("find_ppu_functions", [sys.executable, str(tools / "find_functions.py"),
                                str(eboot), "--output", str(meta / "functions.json")]),
        ("extract_spu", [sys.executable, str(tools / "extract_spu_images.py"),
                         str(eboot), "--output", str(spudir)]),
        ("recarve_spu", None),  # função Python segura, lê a cópia local do usuário
        ("lift_ppu", [sys.executable, str(tools / "ppu_lifter.py"), str(eboot),
                      "--functions", str(meta / "functions.json"),
                      "--hle-stubs", str(imports),
                      "--toc", "0xF21930", "--code-end", "0xC79C6C",
                      "--output", str(gen), "-j", str(jobs)]),
        ("patch_ppu", [sys.executable, str(upstream / "tools/post_lift.py")]),
        ("lift_embedded_spu", [
            sys.executable, str(tools / "build_spu_workloads.py"),
            "--images", str(spudir), "--lifted", str(spugen),
            "--out", str(spugen / "embedded_spu_workloads.c"),
            "--register-fn", "tm_embedded_spu_register_all",
            "--constructor", "--title", "Twisted Metal BCUS98106 1.00"
        ]),
    ]


def recarve_images(upstream, runtime, eboot):
    """Confere extensão das imagens com a regra usada pelo runtime SPU."""
    tools_dir = str((Path(runtime) / "tools").resolve())
    sys.path.insert(0, tools_dir)
    try:
        from build_spu_workloads import img_size, is_spu_elf
    finally:
        sys.path.pop(0)
    raw = Path(eboot).read_bytes()
    imgs = sorted((Path(upstream) / "meta/spu").glob("*.elf"))
    if not imgs:
        raise ValueError("Nenhuma imagem SPU extraída")
    changed = 0
    for path in imgs:
        m = re.search(r"_at_([0-9A-Fa-f]{8})\.elf$", path.name)
        if not m:
            raise ValueError("Nome de imagem SPU inesperado: " + path.name)
        off = int(m.group(1), 16)
        if off < 0 or off >= len(raw):
            raise ValueError("Offset SPU fora do ELF: " + path.name)
        candidate = raw[off:off + 0x80000]
        if not is_spu_elf(candidate):
            raise ValueError("Cabeçalho SPU inválido: " + path.name)
        size = img_size(candidate)
        if size < 0x34 or off + size > len(raw):
            raise ValueError("Tamanho de SPU inválido: " + path.name)
        new = raw[off:off + size]
        if path.read_bytes() != new:
            path.write_bytes(new)
            changed += 1
    return {"spu_images": len(imgs), "resized": changed}


def validate_output(upstream):
    root = Path(upstream)
    ppu = sorted((root / "src/recomp").glob("*.cpp"))
    spu = sorted((root / "src/spu_gen").rglob("spu_recomp.c"))
    header = root / "src/recomp/ppu_recomp.h"
    registry = root / "src/spu_gen/embedded_spu_workloads.c"
    errors = []
    if not ppu or not all(p.stat().st_size > 0 for p in ppu):
        errors.append("Nenhum chunk PPU C++ válido")
    if not header.is_file() or header.stat().st_size == 0:
        errors.append("Cabeçalho PPU não gerado")
    if not spu:
        errors.append("SPUs embutidos não levantados")
    if not registry.is_file() or registry.stat().st_size == 0:
        errors.append("Registro SPU embutido ausente")
    return {"ppu_chunks": len(ppu), "embedded_spu_sources": len(spu),
            "errors": errors, "generated": not errors,
            "jobqueue_15_status": "not-covered; need observed job binaries"}


def execute(upstream, runtime, eboot, jobs=8, overwrite=False, run=None):
    upstream, runtime, eboot = (Path(p).resolve() for p in (upstream, runtime, eboot))
    if not eboot.is_file() or file_digest(eboot) != DISC_100_SHA256:
        raise ValueError("ELF ausente ou hash errado: exige disco original 1.00")
    for name in RUNTIME_TOOLS:
        if not (runtime / "tools" / name).is_file():
            raise ValueError("Ferramenta ps3recomp ausente: " + name)
    if not (upstream / "tools/post_lift.py").is_file():
        raise ValueError("O upstream não contém tools/post_lift.py")
    if (upstream / "src/recomp").exists() and list((upstream / "src/recomp").glob("*.cpp")) and not overwrite:
        raise ValueError("PPU já gerado; use --overwrite para recompilar conscientemente")
    if (upstream / "src/spu_gen").exists() and list((upstream / "src/spu_gen").rglob("spu_recomp.c")) and not overwrite:
        raise ValueError("SPU já gerado; use --overwrite para recompilar conscientemente")
    if run is None:
        run = subprocess.run
    (upstream / "meta").mkdir(parents=True, exist_ok=True)
    for name, command in plan_steps(upstream, runtime, eboot, jobs):
        print("==> ", name, flush=True)
        if name == "recarve_spu":
            print(recarve_images(upstream, runtime, eboot), flush=True)
            continue
        result = run(command, cwd=str(upstream), check=False)
        if result.returncode:
            raise RuntimeError("Falha em " + name + " (exit " + str(result.returncode) + ")")
    result = validate_output(upstream)
    if result["errors"]:
        raise RuntimeError("Arquivos incompletos: " + "; ".join(result["errors"]))
    report = (upstream / "meta" / "local-lift-report.json")
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("PPU e SPUs embutidos gerados; NÃO inclui jobs SPURS observados em execução.")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--eboot", type=Path, required=True)
    p.add_argument("--jobs", type=int, default=8)
    p.add_argument("--plan", action="store_true",
                   help="Somente mostrar comandos; não lê o ELF nem cria arquivos")
    p.add_argument("--overwrite", action="store_true",
                   help="Autoriza re-gerar artefatos PPU/SPU locais existentes")
    a = p.parse_args(argv)
    if not 1 <= a.jobs <= 64:
        p.error("--jobs deve estar entre 1 e 64")
    if a.plan:
        for name, command in plan_steps(a.upstream, a.runtime, a.eboot, a.jobs):
            print(name + ": " + ("[recarve Python local]" if command is None
                                 else subprocess.list2cmdline(command)))
        return 0
    try:
        print(json.dumps(execute(a.upstream, a.runtime, a.eboot, a.jobs,
                                 a.overwrite), ensure_ascii=False, indent=2))
    except (OSError, RuntimeError, ValueError) as exc:
        print("FALHA: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
