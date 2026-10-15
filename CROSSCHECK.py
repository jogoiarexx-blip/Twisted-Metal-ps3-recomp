#!/usr/bin/env python3
"""Non-mutating cross-check of the supplied PPU ELF and recompilation metadata."""
import argparse, hashlib, json, struct, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('elf', type=Path)
    ap.add_argument('--rpcs3-source', type=Path, help='Optional RPCS3 source ZIP for source-presence check')
    args=ap.parse_args()
    elf=args.elf.read_bytes()
    digest=hashlib.sha256(elf).hexdigest()
    manifest=json.loads((ROOT/'recomp/manifest.json').read_text())
    image=json.loads((ROOT/'elf-map-update-1.06.json').read_text())
    imports=json.loads((ROOT/'recomp/imports.json').read_text())
    results=[]
    def check(cond, text):
        results.append(bool(cond))
        print(('PASS' if cond else 'FAIL') + '  ' + text)
    check(digest==manifest['elf_sha256'], 'ELF hash corresponds to recomp v0.7')
    check(digest==image['input_sha256'], 'ELF hash corresponds to update map')
    check(elf[:6]==b'\x7fELF\x02\x02' and elf[18:20]==b'\x00\x15', 'ELF64 PPC big-endian')
    if len(elf)>=64:
        entry=struct.unpack_from('>Q',elf,24)[0]
        check(entry==0xf13170, 'PPU entry descriptor address matches v0.7')
    else:
        check(False, 'ELF header complete')
    if len(elf)>=64:
        off=struct.unpack_from('>Q',elf,32)[0]
        phsize=struct.unpack_from('>H',elf,54)[0]
        phnum=struct.unpack_from('>H',elf,56)[0]
        mapping=[]
        if phsize>=56 and off+phsize*phnum<=len(elf):
            for i in range(phnum):
                p=off+i*phsize
                kind,flags=struct.unpack_from('>II',elf,p)
                if kind==1:
                    fileoff,vaddr,_,fs,ms,align=struct.unpack_from('>QQQQQQ',elf,p+8)
                    if fileoff+fs<=len(elf) and ms>=fs:
                        mapping.append((vaddr,vaddr+fs,fileoff))
        else: check(False, 'ELF program header bounds')
        for block in manifest['functions']:
            addr=int(block['address'],16)
            source=bytes.fromhex(block['bytes'])
            matches=[elf[fileoff+addr-start:fileoff+addr-start+len(source)]==source
                     for start,end,fileoff in mapping if start<=addr and addr+len(source)<=end]
            check(any(matches),f'Original bytes verified at {block["address"]}')
    imp=imports['imports']
    addresses=[int(x['address'],16) for x in imp]
    check(len(imp)==imports['count']==583, '583 imports match declared count')
    check(len(set(addresses))==len(addresses), 'No duplicate import address')
    check(len(set(x['module'] for x in imp))==imports['modules']==35, '35 imported modules')
    check(any(x['address'].lower()=='0x00c8d094' and 'sys_initialize_tls' in x['name'] for x in imp), 'TLS import correctly identified')
    if args.rpcs3_source:
        with zipfile.ZipFile(args.rpcs3_source) as z:
            names=z.namelist()
            check(any(n.endswith('SPUThread.cpp') for n in names), 'RPCS3 SPU implementation source included')
            check(any('VKGSRender' in n for n in names), 'RPCS3 Vulkan renderer source included')
    print(f'\n{sum(results)}/{len(results)} checks passed. This is NOT gameplay or FPS validation.')
    return 0 if all(results) else 1
if __name__=='__main__':
    raise SystemExit(main())
