#!/usr/bin/env python3
"""Translate the second entry basic block with exact opcode validation.

This deliberately stops at the next call. No fallback to interpretation.
"""
import hashlib
import sys
from pathlib import Path
EXPECTED_SHA='41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'
START=0x354d88
WORDS=[
 0xf821ff61,0x7c0802a6,0xfb410070,0xfb810080,0xfbc10090,0xfbe10098,
 0xfb610078,0xfba10088,0xf80100b0,0x7c7f1b78,0x7c9c2378,0x7cba2b78,
 0x7cde3378,0x7d9d6378,0x81628004,0x79040020,0x79460020,0x7ce33b78,
 0x79250020,0x7f9be378,0x93ab0000,0x489382b9,
]
elf=Path(sys.argv[1]).read_bytes()
if hashlib.sha256(elf).hexdigest()!=EXPECTED_SHA:raise SystemExit('ELF 1.06 hash mismatch')
actual=[int.from_bytes(elf[START-0x10000+i*4:START-0x10000+i*4+4],'big') for i in range(len(WORDS))]
if actual!=WORDS:raise SystemExit('Startup opcodes differ from verified ELF')
lines=['// Generated from ELF '+EXPECTED_SHA,'#include "runtime.hpp"','namespace tmrecomp {','uint64_t startup_00354d88(Cpu &cpu, Memory &mem) {']
for i,w in enumerate(WORDS):
    addr=START+i*4; opcode=w>>26; rd=(w>>21)&31; ra=(w>>16)&31
    if w==0x7c0802a6: action='cpu.r[0] = cpu.lr;' # mflr r0
    elif w==0x489382b9:
        # The target is 0xc8d094; the LR is return after this call.
        action='cpu.lr = 0x354de0; return 0xc8d094;'
    elif opcode==62: # std/stdu, DS form; low 2 bits encode update
        signed=((w>>2)&0x3fff);signed=signed-0x4000 if signed&0x2000 else signed
        offset=signed*4
        if (w&3)==1: # stdu r1,-0xa0(r1)
            if rd!=1 or ra!=1 or offset!=-0xa0:raise SystemExit('Unexpected stdu')
            action='uint64_t old_sp=cpu.r[1]; cpu.r[1]-=0xa0; mem.store64(cpu.r[1],old_sp);'
        elif (w&3)==0: action=f'mem.store64(cpu.r[{ra}] + static_cast<uint64_t>(static_cast<int64_t>({offset})), cpu.r[{rd}]);'
        else:raise SystemExit('Unsupported DS opcode')
    elif opcode==31 and (w&0x7ff)==0x378: # or rA,rS,rB, same source = mr alias
        rs=(w>>21)&31; dest=(w>>16)&31; rb=(w>>11)&31
        if rs!=rb:raise SystemExit('Unexpected OR register operands')
        action=f'cpu.r[{dest}] = cpu.r[{rs}];'
    elif opcode==32: # lwz rD,D(rA)
        delta=w&0xffff;delta=delta-0x10000 if delta&0x8000 else delta
        action=f'cpu.r[{rd}] = mem.load32(cpu.r[{ra}] + static_cast<uint64_t>(static_cast<int64_t>({delta})));'
    elif opcode==36: # stw rS,D(rA)
        delta=w&0xffff;delta=delta-0x10000 if delta&0x8000 else delta
        action=f'mem.store32(cpu.r[{ra}] + static_cast<uint64_t>(static_cast<int64_t>({delta})), static_cast<uint32_t>(cpu.r[{rd}]));'
    elif w in (0x79040020,0x79460020,0x79250020): # rldicl aliases: clrldi dest,src,32
        rs=(w>>21)&31;dest=(w>>16)&31
        action=f'cpu.r[{dest}] = cpu.r[{rs}] & 0xffffffffULL;'
    else:raise SystemExit(f'Unimplemented opcode 0x{w:08x} at 0x{addr:x}')
    lines.extend([f'  // 0x{addr:08x}: {w:08x}',f'  {action}'])
lines.extend(['}','}'])
Path(__file__).with_name('startup2.cpp').write_text('\n'.join(lines)+'\n')
print(f'{len(WORDS)} instructions translated, next call 0xc8d094')
