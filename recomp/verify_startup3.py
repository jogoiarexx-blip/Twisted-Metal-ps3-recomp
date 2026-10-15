#!/usr/bin/env python3
"""Fail closed if the exact BCUS98106 v1.06 startup block changes."""
import hashlib, sys
from pathlib import Path
SHA = '41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'
WORDS = '''60000000 395c0004 39000000 79490020 7b8b0020 39080001 394a0008 7fbf4040
80090000 3b9c0004 900b0000 409cffe0 81228000 7f5dd378 7f45d378 7ffcfb78
395a0004 39000000 93e90000 93690004 79490020 78ab0020 39080001 394a0008
7fbe4040 80090000 38a50004 900b0000 409cffe0 48197a7d'''.split()
if len(sys.argv)!=2: raise SystemExit('usage: python verify_startup3.py /path/to/EBOOT.elf')
elf=Path(sys.argv[1]).read_bytes()
if hashlib.sha256(elf).hexdigest()!=SHA:raise SystemExit('FAIL: input ELF hash does not match expected v1.06')
# All instructions in this verified PT_LOAD segment have ELF offset = VA - 0x10000.
start=0x354de0-0x10000
actual=elf[start:start+4*len(WORDS)]
if actual!=bytes.fromhex(''.join(WORDS)):raise SystemExit('FAIL: opcode mismatch at 0x354de0')
print(f'PASS: SHA256 and {len(WORDS)} instructions match 0x354de0..0x354e54')
