#!/usr/bin/env python3
"""Check the exact bytes and entry descriptor before using the v1.06 memory init lift."""
import hashlib
import struct
import sys
from pathlib import Path
EXPECTED = '41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'
WORDS = '''f821ff91 7c0802a6 f8010080 3c60017e 39600160 3063fc48 78630020 44000002
3c60017e 3960015c 30a3fc40 3c6000f0 78a50020 38800400 44000002 2c030000
4182000c 48473129 48000000 3c60017e 3c8000f0 8063fc40 4849ff99 3c80017e
9064fc44 480008bd e8010080 7c0803a6 38210070 4e800020'''.split()

def main(path):
    elf=Path(path).read_bytes()
    if hashlib.sha256(elf).hexdigest()!=EXPECTED:
        raise ValueError('wrong ELF SHA-256; this lift is only for BCUS98106 1.06')
    # This ELF's executable PT_LOAD has p_offset=0, p_vaddr=0x10000.
    at=0x4ec8d0-0x10000
    if elf[at:at+len(WORDS)*4] != bytes.fromhex(''.join(WORDS)):
        raise ValueError('0x4ec8d0 instruction sequence differs')
    # The 1.06 map verified a real OPD entry at 0xf17610 (code, TOC).
    opd_at=0xf17610-0x10000
    code,toc=struct.unpack_from('>II',elf,opd_at)
    if (code,toc)!=(0x4ec8d0,0xf31ac0):raise ValueError('function descriptor differs')
    print('PASS: v1.06 0x4ec8d0..0x4ec944, 30 instructions, OPD 0xf17610, TOC 0xf31ac0')

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python verify_startup4.py EBOOT.elf')
    try:main(sys.argv[1])
    except (ValueError,OSError) as e:raise SystemExit(f'FAIL: {e}')
