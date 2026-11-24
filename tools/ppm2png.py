import sys, os, struct, zlib

def write_png(w, h, rgb_bytes, dst):
    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png += struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT
    # Add filter byte (0) to each scanline
    scanlines = []
    line_len = w * 3
    for y in range(h):
        line = rgb_bytes[y * line_len : (y + 1) * line_len]
        scanlines.append(b'\x00' + line)
    raw_data = b''.join(scanlines)
    compressed = zlib.compress(raw_data, 9)
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND
    iend_crc = zlib.crc32(b'IEND')
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    with open(dst, 'wb') as f:
        f.write(png)
    print(f"Saved PNG {w}x{h} -> {dst}")

def convert_ppm(src, dst):
    if not os.path.exists(src):
        print("Not found:", src)
        return
    with open(src, 'rb') as f:
        data = f.read()
    # parse header
    # P6 <w> <h> 255\n
    header_end = 0
    lines = []
    curr = []
    for i in range(min(len(data), 200)):
        b = data[i:i+1]
        if b in (b' ', b'\t', b'\r', b'\n'):
            if curr:
                lines.append(bytes(curr).decode('ascii', errors='ignore'))
                curr = []
                if len(lines) >= 4:
                    header_end = i + 1
                    break
        else:
            curr.append(b[0])
    if len(lines) < 4 or lines[0] != 'P6':
        print("Invalid PPM format in", src)
        return
    w = int(lines[1])
    h = int(lines[2])
    rgb_data = data[header_end : header_end + w * h * 3]
    write_png(w, h, rgb_data, dst)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: ppm2png.py <src.ppm> <dst.png>")
        sys.exit(1)
    convert_ppm(sys.argv[1], sys.argv[2])
