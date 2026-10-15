#!/usr/bin/env python3
"""Pin the exact PPC code regions lifted for the Twisted Metal BCUS98106 1.06 heap init."""
import hashlib
import sys
from pathlib import Path

EXPECTED_ELF = '41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'
# 0x10000 maps to file offset 0; matches the EBOOT's executable PT_LOAD.
REGIONS = (
    (0x98c8c0, 0x98c954, 'd0eff769e237e0ab4936226ba7a75ab6655195cc9d6cac35dd7f728f7aa3ca98'),
    (0x988b78, 0x988be8, 'ef9fa0567ab2b10124194a11d6428be21879f9fb064a934e97e85592ff859b49'),
)
def verify(path):
    content = Path(path).read_bytes()
    if hashlib.sha256(content).hexdigest() != EXPECTED_ELF:
        raise ValueError('incorrect ELF (SHA-256); expected BCUS98106 update 1.06')
    if content[:6] != b'\x7fELF\x02\x02':
        raise ValueError('ELF64 big-endian header missing')
    for first, end, digest in REGIONS:
        data = content[first-0x10000:end-0x10000]
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f'bytes at 0x{first:x}..0x{end:x} do not match')
    print('PASS: matching 1.06 EBOOT, heap 0x98C8C0 and helper 0x988B78')
if __name__ == '__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: python verify_heap_init.py EBOOT.elf')
    try:
        verify(sys.argv[1])
    except (OSError, ValueError) as err:
        raise SystemExit(f'FAIL: {err}')
