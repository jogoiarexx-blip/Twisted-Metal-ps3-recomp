#!/usr/bin/env python3
"""Recompile a restricted set of verified PPU leaf functions to host C++."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN

SUPPORTED = {0x994838, 0x9946e0, 0x9946c0}
EXPECTED = '41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d'

def reg(s):
    m = re.fullmatch(r'r(\d+)', s.strip())
    if not m or int(m[1]) > 31:
        raise ValueError(f'register unsupported: {s}')
    return int(m[1])

def imm(s):
    return int(s.strip(), 0)

def compile_ins(ins):
    op, args = ins.mnemonic, [s.strip() for s in ins.op_str.split(',')]
    if op in ('li', 'lis'):
        d = reg(args[0]); v = imm(args[1]); v = v << 16 if op == 'lis' else v
        return f'  cpu.r[{d}] = static_cast<uint64_t>(static_cast<int64_t>({v}));'
    if op in ('addi', 'addic'):
        d, a, val = reg(args[0]), reg(args[1]), imm(args[2]); base = '0' if a == 0 else f'cpu.r[{a}]'
        # addic also sets XER.CA on unsigned carry; preserving it matters if a later instruction reads it.
        if op == 'addic':
            return f'  cpu.ca = (static_cast<unsigned __int128>({base}) + static_cast<unsigned __int128>(static_cast<uint64_t>(static_cast<int64_t>({val})))) >> 64;\n  cpu.r[{d}] = {base} + static_cast<uint64_t>(static_cast<int64_t>({val}));'
        return f'  cpu.r[{d}] = {base} + static_cast<uint64_t>(static_cast<int64_t>({val}));'
    if op in ('lwz', 'stw', 'stb'):
        m = re.fullmatch(r'(-?(?:0x[0-9a-f]+|\d+))\((r\d+)\)', args[1])
        if not m: raise ValueError(f'unsupported memory operand: {ins.op_str}')
        d, off, base = reg(args[0]), imm(m[1]), reg(m[2]); addr = f'(cpu.r[{base}] + static_cast<uint64_t>(static_cast<int64_t>({off})))' if base else f'static_cast<uint64_t>(static_cast<int64_t>({off}))'
        if op == 'lwz': return f'  cpu.r[{d}] = mem.load32({addr});'
        if op == 'stw': return f'  mem.store32({addr}, static_cast<uint32_t>(cpu.r[{d}]));'
        return f'  mem.store8({addr}, static_cast<uint8_t>(cpu.r[{d}]));'
    if op == 'clrldi':
        d, a, n = reg(args[0]), reg(args[1]), imm(args[2])
        if n < 0 or n > 63: raise ValueError('invalid clrldi')
        mask = (1 << (64 - n)) - 1
        return f'  cpu.r[{d}] = cpu.r[{a}] & 0x{mask:x}ULL;'
    if op == 'blr': return '  return;'
    raise ValueError(f'unsupported instruction at 0x{ins.address:x}: {op} {ins.op_str}')

def main():
    p=argparse.ArgumentParser();p.add_argument('elf',type=Path);p.add_argument('-o','--output',type=Path,required=True);args=p.parse_args()
    data=args.elf.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if digest != EXPECTED: raise SystemExit('ELF hash mismatch: requires the uploaded update ELF')
    phoff=struct.unpack_from('>Q',data,32)[0]; ents,n=struct.unpack_from('>HH',data,54)
    segments=[]
    for i in range(n):
        typ,flags,off,va,_,fs,ms,align=struct.unpack_from('>IIQQQQQQ',data,phoff+i*ents)
        if typ==1 and flags&1:segments.append((va,off,fs))
    md=Cs(CS_ARCH_PPC,CS_MODE_64|CS_MODE_BIG_ENDIAN)
    result=['// Generated from SHA-256 '+digest, '#include "runtime.hpp"','namespace tmrecomp {']
    manifest=[]
    for addr in sorted(SUPPORTED):
        va,offset,size=next((v,o,s) for v,o,s in segments if v<=addr<v+s)
        raw=data[offset+addr-va:offset+addr-va+128]
        ins=[]
        for x in md.disasm(raw,addr):
            if x.address != addr+4*len(ins): raise ValueError('disassembly gap')
            ins.append(x)
            if x.mnemonic=='blr': break
        if not ins or ins[-1].mnemonic!='blr': raise ValueError(f'no return for {addr:x}')
        code=[compile_ins(x) for x in ins]
        result.append(f'void fn_{addr:08x}(Cpu &cpu, Memory &mem) {{')
        for x,c in zip(ins,code):
            result.append(f'  // 0x{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}')
            result.append(c)
        result.append('}')
        manifest.append({'address':f'0x{addr:08x}','instructions':len(ins),'bytes':data[offset+addr-va:offset+addr-va+len(ins)*4].hex()})
    result.append('}')
    args.output.write_text('\n'.join(result)+'\n')
    (args.output.parent/'manifest.json').write_text(json.dumps({'elf_sha256':digest,'functions':manifest},indent=2)+'\n')
    print('Generated',len(manifest),'PPU functions ->',args.output)
if __name__=='__main__': main()
