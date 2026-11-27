#!/usr/bin/env python3
"""Opt-in instrumentation for TM_THREADMAP: rename the generated definitions of the RTApp frame
step (func_0010EF58) and its direct callees to *_lifted so src/hle_extra.cpp can wrap and count them.

  python tools/patch_frame_counters.py recomp/src_recomp_100        # apply (backs up chunks to *.orig)
  python tools/patch_frame_counters.py recomp/src_recomp_100 --revert

Then add `#define TM_FRAME_COUNTERS 1` to a local, untracked src/tm_local.h and rebuild. The recomp chunks
are git-ignored; without this patch and macro the wrappers are not compiled and the build is unchanged."""
import os, shutil, sys
FUNCS = {'000': ['0010EF58', '0015F3B8', '0010ED40'],
         '001': ['003C31D0', '003621DC', '0036181C', '002A0AF8', '0024D3FC'],
         '002': ['005AF200', '005ABA58', '00610028', '005B0E0C', '005B0DD0', '005AF0D8', '005ABB70', '005511A4', '00535120', '004DE120'],
         '003': ['00692918']}
def main():
    d = sys.argv[1]; revert = '--revert' in sys.argv
    for c, names in FUNCS.items():
        p = os.path.join(d, f'ppu_recomp_{c}.cpp')
        if revert:
            if os.path.exists(p + '.orig'): shutil.move(p + '.orig', p); print('reverted', p)
            continue
        s = open(p, encoding='utf-8', errors='surrogateescape', newline='').read()
        if not os.path.exists(p + '.orig'): shutil.copy2(p, p + '.orig')
        for n in names:
            old = f'\nvoid func_{n}(ppu_context* ctx) {{'
            if s.count(old) != 1: print('skip (already patched or missing)', n); continue
            s = s.replace(old, f'\nvoid func_{n}_lifted(ppu_context* ctx) {{')
        open(p, 'w', encoding='utf-8', errors='surrogateescape', newline='').write(s); print('patched', p)
main()
