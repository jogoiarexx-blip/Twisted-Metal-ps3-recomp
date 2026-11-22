#!/usr/bin/env python3
"""Configura/compila upstream Windows com gates, sem tocar no boot probe 1.06."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from doctor import inspect

def build_commands(upstream, runtime, build_dir):
    upstream = Path(upstream).resolve()
    runtime = Path(runtime).resolve()
    out = Path(build_dir).resolve()
    return [
        ["cmake", "-S", str(upstream), "-B", str(out), "-G", "Ninja",
         "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_COMPILER=clang-cl",
         "-DCMAKE_CXX_COMPILER=clang-cl", "-DPS3RECOMP_DIR=" + str(runtime),
         "-DPS3RECOMP_RUNTIME_LIB=" + str(runtime / "build/ps3recomp_runtime.lib")],
        ["cmake", "--build", str(out), "--config", "Release"],
    ]

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--eboot", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path,
                        help="Por padrão usa build-native no checkout upstream")
    parser.add_argument("--run", action="store_true",
                        help="Executar o .exe compilado com seu EBOOT.ELF local")
    args = parser.parse_args(argv)
    report = inspect(args.upstream, args.runtime, args.eboot)
    if not report["ready"]:
        print("Preflight REPROVADO; não será compilado:", file=sys.stderr)
        for error in report["errors"]:
            print("- " + error, file=sys.stderr)
        return 2
    out = (args.build_dir or args.upstream / "build-native").resolve()
    if out == args.upstream.resolve() or out == args.runtime.resolve():
        print("Diretório de build inseguro", file=sys.stderr)
        return 2
    for command in build_commands(args.upstream, args.runtime, out):
        print("Executando:", " ".join(command), flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode:
            return result.returncode
    if args.run:
        executable = out / "twistedmetal.exe"
        if not executable.is_file():
            print("Build não produziu: " + str(executable), file=sys.stderr)
            return 3
        return subprocess.run([str(executable), str(args.eboot.resolve())],
                              cwd=str(args.upstream.resolve()), env=os.environ.copy(),
                              check=False).returncode
    return 0

if __name__ == "__main__":
    sys.exit(main())
