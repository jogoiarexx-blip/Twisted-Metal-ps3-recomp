#!/usr/bin/env python3
"""Compare generated native code against Unicorn executing bytes from the uploaded ELF."""
import json, subprocess, sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_PPC,UC_MODE_PPC32,UC_MODE_BIG_ENDIAN
from unicorn.ppc_const import UC_PPC_REG_3,UC_PPC_REG_4,UC_PPC_REG_LR
root=Path(__file__).resolve().parent
elf=Path(sys.argv[1]).read_bytes();manifest=json.loads((root/'manifest.json').read_text())
# Executable segment vaddr 0x10000 corresponds to file offset zero in this ELF.
for address,r3,word in [(0x994838,0x100040,0xabcdef01),(0x994838,0x100080,0),
                         (0x9946e0,0x100040,0xfffffff8),(0x9946e0,0x100040,0x100090),
                         (0x9946c0,0x100040,0xfedcba98)]:
    block=next(x for x in manifest['functions'] if int(x['address'],16)==address)
    code=bytes.fromhex(block['bytes'])
    assert code==elf[address-0x10000:address-0x10000+len(code)]
    uc=Uc(UC_ARCH_PPC,UC_MODE_PPC32|UC_MODE_BIG_ENDIAN)
    uc.mem_map(0x990000,0x10000);uc.mem_map(0x100000,0x1000);uc.mem_map(0x200000,0x1000)
    uc.mem_write(address,code)
    uc.mem_write(0x100048,word.to_bytes(4,'big'))
    uc.mem_write(0x1001ac,word.to_bytes(4,'big'))
    uc.reg_write(UC_PPC_REG_3,r3);uc.reg_write(UC_PPC_REG_4,0x12345678);uc.reg_write(UC_PPC_REG_LR,0x200000)
    uc.emu_start(address,0x200000,count=20)
    actual=[uc.reg_read(UC_PPC_REG_3),uc.reg_read(UC_PPC_REG_4)]+[int.from_bytes(uc.mem_read(0x100040+i*4,4),'big') for i in range(4)]+[int.from_bytes(uc.mem_read(addr,4),'big') for addr in (0x10015c,0x1001ac)]
    native=subprocess.check_output([str(root/'check'),hex(address),hex(r3),hex(word)],text=True)
    expected=[int(x,16) for x in native.split()]
    if actual!=expected:
        raise AssertionError(f'{address:x} expected native {expected!r}, PPC {actual!r}')
    print(f'PASS {address:#x} r3={r3:#x} word={word:#x}')
