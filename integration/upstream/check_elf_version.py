#!/usr/bin/env python3
"""Reject mismatched local EBOOT.elf files before version-specific patching."""
import argparse
import hashlib
import json
from pathlib import Path

KNOWN = {
    "disc-1.00": {
        "sha256": "269642a56f3c70be74df41049876887d07aedd4171ce18a481a05067b1b8564e",
        "entry_code": "0x00348DE0",
        "toc": "0x00F21930",
    },
    "update-1.06-candidate": {
        "sha256": "41a8aae28f111aab6b2ab4fff661920ae191720ea473e3c340266050d7a4b99d",
        "entry_code": "0x00354C80",
        "toc": "0x00F31AC0",
    },
}

def classify_hash(digest):
    return next((name for name, item in KNOWN.items()
                 if item["sha256"] == digest.lower()), "unknown")

def classify_file(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            sha.update(chunk)
    digest = sha.hexdigest()
    version = classify_hash(digest)
    return {"file": str(path), "sha256": digest, "version": version,
            "matched": version != "unknown"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path, help="local decrypted ELF; never uploaded")
    parser.add_argument("--require", choices=sorted(KNOWN), required=True)
    args = parser.parse_args()
    try:
        result = classify_file(args.elf)
    except OSError as exc:
        parser.error(str(exc))
    result["required"] = args.require
    result["accepted"] = result["version"] == args.require
    print(json.dumps(result, indent=2))
    return 0 if result["accepted"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
