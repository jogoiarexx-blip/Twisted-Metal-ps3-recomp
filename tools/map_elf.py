#!/usr/bin/env python3
"""Map a PS3 PPU ELF without modifying it or bundling game data."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def parse_elf(path):
    data = path.read_bytes()
    if data[:6] != b"\x7fELF\x02\x02":
        raise ValueError("Expected a 64-bit big-endian ELF")
    if struct.unpack_from(">H", data, 18)[0] != 21:
        raise ValueError("Expected PowerPC64 (e_machine=21)")
    entry = struct.unpack_from(">Q", data, 24)[0]
    phoff = struct.unpack_from(">Q", data, 32)[0]
    phentsize, phnum = struct.unpack_from(">HH", data, 54)
    if phentsize < 56 or phoff + phentsize * phnum > len(data):
        raise ValueError("Invalid program headers")
    segments = []
    for i in range(phnum):
        typ, flags, off, va, _, fs, ms, align = struct.unpack_from(">IIQQQQQQ", data, phoff + i * phentsize)
        if typ == 1:
            if off + fs > len(data):
                raise ValueError("Segment exceeds the input file")
            segments.append(dict(offset=off, vaddr=va, filesz=fs, memsz=ms, flags=flags, align=align))

    def offset(addr, length=1):
        for seg in segments:
            if seg['vaddr'] <= addr and addr + length <= seg['vaddr'] + seg['filesz']:
                return seg['offset'] + addr - seg['vaddr']
        raise ValueError(f"Address 0x{addr:x} is not file-backed")

    # This PS3 PPU binary has 32-bit code/TOC addresses in an 8-byte OPD entry.
    code, toc = struct.unpack_from(">II", data, offset(entry, 8))
    exec_segments = [s for s in segments if s['flags'] & 1]
    if not any(s['vaddr'] <= code < s['vaddr'] + s['filesz'] for s in exec_segments):
        raise ValueError("Entry descriptor does not point into executable code")
    if not any(s['vaddr'] <= toc < s['vaddr'] + s['memsz'] for s in segments):
        raise ValueError("Entry descriptor TOC is not mapped")
    descriptors = []
    for seg in segments:
        if not (seg['flags'] & 2):
            continue
        for off in range(seg['offset'], seg['offset'] + seg['filesz'] - 7, 4):
            target, candidate_toc = struct.unpack_from(">II", data, off)
            if candidate_toc != toc or target % 4:
                continue
            if any(s['vaddr'] <= target < s['vaddr'] + s['filesz'] for s in exec_segments):
                descriptors.append({'descriptor': f"0x{seg['vaddr'] + off - seg['offset']:08x}", 'code': f"0x{target:08x}"})
    return {
        'input_sha256': hashlib.sha256(data).hexdigest(),
        'input_size': len(data), 'machine': 'PowerPC64 big-endian',
        'entry_descriptor': f"0x{entry:08x}", 'entry_code': f"0x{code:08x}",
        'entry_toc': f"0x{toc:08x}",
        'segments': [{k: (f"0x{v:x}" if k in ('offset', 'vaddr', 'flags') else v) for k, v in s.items()} for s in segments],
        'descriptor_count': len(descriptors),
        'descriptors': descriptors,
        'caveat': 'Candidates share the entry TOC and point into executable memory; function bounds and validity need disassembly and runtime checks.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('elf', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    result = parse_elf(args.elf)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"Entry {result['entry_code']}; {result['descriptor_count']} descriptor candidates -> {args.output}")
