#!/usr/bin/env python
"""Locate and repair corrupted regions in a downloaded file against its HTTP source.

Probes every 32MB block with a 4KB range request, compares with the local copy,
re-downloads mismatching blocks, patches them in place, then verifies total sha256.
Only used for the hostile-CDN situation on this host; normal hosts: use hf CLI.
"""
import hashlib
import sys
import urllib.request

URL = sys.argv[1]
PATH = sys.argv[2]
EXPECT_SHA = sys.argv[3]
SIZE = int(sys.argv[4])
BLOCK = 32 * 1024 * 1024
PROBE = 4096


def fetch(start, length):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{start + length - 1}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


bad = []
suspects = []
with open(PATH, "rb") as f:
    for off in range(0, SIZE, BLOCK):
        n = min(BLOCK, SIZE - off)
        hits = 0
        for k in range(16):  # 16 coarse points per 32MB block
            p = off + (n - PROBE) * k // 15
            f.seek(p)
            if f.read(PROBE) != fetch(p, PROBE):
                hits += 1
        if hits:
            suspects.append((off, n, hits))
        print(f"\rcoarse {off // BLOCK + 1}/{(SIZE + BLOCK - 1) // BLOCK} suspect_blocks={len(suspects)}", end="", flush=True)
print()
print(f"suspects: {[hex(o) for o, _, _ in suspects]}")

FINE = 64 * 1024
bad = []
with open(PATH, "r+b") as f:
    for off, n, hits in suspects:
        for p in range(off, off + n, FINE):
            m = min(PROBE, off + n - p)
            if m <= 0:
                break
            f.seek(p)
            if f.read(m) != fetch(p, m):
                bad.append(p)
        print(f"fine-scanned block {hex(off)} (coarse hits={hits}) -> {sum(1 for b in bad if off <= b < off + n)} bad spots")
print(f"bad spots: {[hex(b) for b in bad]}")

if bad:
    print(f"repairing {len(bad)} x {FINE // 1024}KB segments")
    with open(PATH, "r+b") as f:
        for p in bad:
            seg = p - (p % FINE)
            m = min(FINE, SIZE - seg)
            f.seek(seg)
            f.write(fetch(seg, m))
            print(f"patched {hex(seg)}..{hex(seg + m)}")

got = sha256_file(PATH)
print("final sha:", got)
print("SHA_OK" if got == EXPECT_SHA else "SHA_MISMATCH")
sys.exit(0 if got == EXPECT_SHA else 1)
