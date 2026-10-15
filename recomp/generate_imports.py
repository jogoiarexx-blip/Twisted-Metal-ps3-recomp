#!/usr/bin/env python3
"""Extract active PPU import addresses from a Twisted Metal RPCS3.log."""
import argparse,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('-o','--output',type=Path,default=Path(__file__).with_name('imports.json'));args=p.parse_args()
s=args.log.read_text(encoding='utf-8',errors='replace')
pattern=re.compile(r'\*\*\*\*\s+(\w+) import: \[([^\]]+)\] \(0x([0-9a-fA-F]+)\) -> 0x([0-9a-fA-F]+)')
entries={}
for module,name,nid,addr in pattern.findall(s):
    key=int(addr,16);entry={'address':f'0x{key:08x}','nid':f'0x{int(nid,16):08x}','module':module,'name':name}
    if key in entries and entries[key]!=entry:raise ValueError(f'conflicting imports at 0x{key:x}')
    entries[key]=entry
if entries.get(0xc8d094,{}).get('name')!='sys_initialize_tls':raise ValueError('Not the expected Twisted Metal import layout')
ordered=[entries[k] for k in sorted(entries)]
args.output.write_text(json.dumps({'source':'RPCS3.log for BCUS98106 01.06','count':len(ordered),'modules':len({x['module'] for x in ordered}),'imports':ordered},indent=2)+'\n')
header=args.output.with_name('import_table.hpp')
lines=['// Generated import metadata from RPCS3.log; no game binaries included.','#pragma once','#include <cstdint>','namespace tmrecomp {', 'struct Import { uint32_t address,nid; const char* module; const char* name; };','inline constexpr Import imports[] = {']
for e in ordered:lines.append(f'  {{{e["address"]},{e["nid"]},"{e["module"]}","{e["name"]}"}},')
lines.extend(['};','inline const Import* find_import(uint64_t pc) {','  for(const auto &entry: imports) if(entry.address==pc) return &entry;','  return nullptr;','}','}'])
header.write_text('\n'.join(lines)+'\n')
print(len(ordered),'imports across',len({x['module'] for x in ordered}),'modules')
