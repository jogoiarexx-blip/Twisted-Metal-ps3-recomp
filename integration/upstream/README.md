# Twisted Metal 2012 — integration of the two public upstream projects

**Status: isolated host-only crossfeed. Not a playable recomp.**

The user project's latest documented boot probe (v0.15) uses an ELF **associated with** the update 1.06 (origin not definitively proven). `sp00nznet/twistedmetal` uses disc **1.00**, and its game addresses **must not** be copied into the 1.06 probe. The public FranklinCG ZIP is a source/research export, not a complete native port.

## What was added, and what was not

1. **sp00nznet inflater candidate**: `tm_inflate.cpp` is a self-contained zlib/DEFLATE decoder, adapted with attribution and game-derived test bytes removed. `tm_inflate_test.cpp` runs **synthetic** stored, zlib/DEFLATE and raw-DEFLATE cases with output bounds. This code is *not* hooked into guest memory or the game's SPURS decompression path.
2. **FranklinCG SPURS regression**: `franklin_taskset_probe.c` tests 128-task bitsets, BE32 fields and bounds with a **synthetic guest layout**; its contract is in JSON. It does not implement a scheduler or prove any native game integration.
3. **ELF identity check**: `check_elf_version.py` rejects unknown/mismatched EBOOT ELF hashes before using hard-coded function addresses. The entry code and TOC differ by version. `test_elf_version.py` checks classification.
4. **CI checks**: these tests run alongside the existing local boot-probe compilation and LV2/SPURS/heap regression suite. A green CI means *host-only tests pass*, not that the game runs.

Run checks locally from the repository root:

```bash
g++ -std=c++17 -O2 -Wall -Wextra -Werror integration/upstream/tm_inflate.cpp integration/upstream/tm_inflate_test.cpp -o /tmp/tm_inflate_test
/tmp/tm_inflate_test
cc -std=c11 -O2 -Wall -Wextra -Werror integration/upstream/franklin_taskset_probe.c -o /tmp/tm_taskset_probe
/tmp/tm_taskset_probe
python3 -m unittest discover -s integration/upstream -p 'test_*.py' -v
```

On Windows, run the same tests using equivalent `clang-cl`/`clang++` or MSVC commands. **The native game** will require a Windows build with clang-cl, Visual Studio, Ninja and CMake.

Validate your **own locally decrypted** ELF (no uploading files or keys):

```bash
python3 integration/upstream/check_elf_version.py /path/to/EBOOT.elf --require disc-1.00
# To target the existing v0.15 boot probe:
python3 integration/upstream/check_elf_version.py /path/to/EBOOT.elf --require update-1.06-candidate
```

Unknown/mismatched identity exits with code 2. Do not bypass the mismatch by changing the target label.

## Path to an actual native Windows .exe

| Gate | Action | Acceptance evidence |
|---|---|---|
| 1. Correct target | Prioritize **disc 1.00** as an independent baseline; preserve v0.15's 1.06 experiment separately | Local hash and trace match, no cross-version offsets |
| 2. Lift + link | Use `sp00nznet/ps3recomp` (`ydkj-master-bringup` runtime branch), generate the 1.00 PPU/SPU code using **your own lawful disc files**, and adapt upstream `boot_main.cpp` / `CMakeLists.txt` | A real Windows executable launches and logs entry |
| 3. Initialization | Validate HLE imports, guest memory/TLS, FIOS file I/O, archive decompression and guest render flip | Trace reaches and displays the genuine menu |
| 4. Frame loop | Investigate the documented SPURS post-FX NIDs `0x7FDF4FEF` and `0x9FCB567B`, Taskset2/job dispatch, Edge geometry ring, RSX FIFO and D3D12 presents | Real 3D world, HUD and consecutive frame progression |
| 5. Input/audio | Implement genuine pad input, sound bank playback, save handling, and verify reproducible combat | One controlled playable arena session |
| 6. Port update 1.06 | Re-lift 1.06 independently, regenerate import/function maps and validate each hook's actual guest address | Same verified minimum gameplay under 1.06 |

**Critical missing inputs**: the sp00nznet ZIP excludes generated `src/recomp/` (~295 MB) and `src/spu_gen/` (~19 MB), the prebuilt `ps3recomp` runtime and the lawfully obtained original game files. FranklinCG's public ZIP also excludes its full private port runtime. Neither ZIP alone can produce an executable, let alone a running game. The original repositories' READMEs describe the required local analysis and build process.

**GitHub Pages cannot run a native Windows .exe or D3D12.** Keep the Pages URL for project status, documentation and downloads of *permissibly distributable tools*, not for launching the native PS3 recomp.

License and provenance: [NOTICES.md](NOTICES.md). **No EBOOT, asset, key, or generated lifted game source should be committed**. No claim of gameplay or increased FPS is made by these tests.
