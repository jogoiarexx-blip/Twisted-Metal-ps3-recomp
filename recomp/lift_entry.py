#!/usr/bin/env python3
"""Lift the verified entry basic block until its first call."""
import hashlib,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_PPC,CS_MODE_BIG_ENDIAN,CS_MODE_64
ELF_SHA='41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'
ENTRY=0x354c80
elf=Path(sys.argv[1]).read_bytes()
if hashlib.sha256(elf).hexdigest()!=ELF_SHA:raise SystemExit('wrong ELF hash')
md=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
ins=list(md.disasm(elf[ENTRY-0x10000:ENTRY-0x10000+32],ENTRY))[:8]
expected=['li','oris','ori','lwz','stdu','li','std','bl']
if [x.mnemonic for x in ins]!=expected or ins[-1].op_str!='0x354d88':raise SystemExit('entry block changed or unsupported')
lines=['// Generated from verified ELF SHA-256 '+ELF_SHA,'#include "runtime.hpp"','namespace tmrecomp {','uint64_t entry_00354c80(Cpu &cpu, Memory &mem) {']
body=[
 '  cpu.r[2] = 0;',
 '  cpu.r[2] |= uint64_t(0xf1) << 16;',
 '  cpu.r[2] |= 0x3170;',
 '  cpu.r[2] = mem.load32(cpu.r[2] + 4);',
 '  { uint64_t old_sp=cpu.r[1]; cpu.r[1]-=0x70; mem.store64(cpu.r[1],old_sp); }',
 '  cpu.r[14] = 0;',
 '  mem.store64(cpu.r[1],cpu.r[14]);',
 '  cpu.lr = 0x354ca0; return 0x354d88;',
]
for x,b in zip(ins,body):
 lines.extend([f'  // 0x{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}',b])
lines.extend(['}','}'])
Path(__file__).with_name('entry.cpp').write_text('\n'.join(lines)+'\n')
print('Recompiled entry block:',len(ins),'instructions -> first call 0x354d88')
