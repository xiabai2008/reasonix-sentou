#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 pcap 中提取 flag.jpg"""
import subprocess
import binascii
import sys
import os

PCAP = r"C:\Users\HZR\Desktop\capture.pcapng"
TSHARK = r"C:\Program Files\Wireshark\tshark.exe"
OUT = r"C:\Users\HZR\Downloads\flag.jpg"

# 运行 tshark 获取 hex 流
result = subprocess.run(
    [TSHARK, "-r", PCAP, "-z", "follow,tcp,hex,318"],
    capture_output=True, timeout=30
)
data = result.stdout.decode("utf-8", errors="replace")

# 提取 hex 行
hex_parts = []
for line in data.split("\n"):
    line = line.strip()
    if line and line[0] in "0123456789abcdef" and "  " in line:
        parts = line.split()
        for p in parts[1:]:
            if len(p) == 2 and all(c in "0123456789abcdefABCDEF" for c in p):
                hex_parts.append(p)

raw = binascii.unhexlify("".join(hex_parts))
print(f"Extracted {len(raw)} bytes")

# JPEG 头部验证
if raw[:2] == b"\xff\xd8":
    print("Verified: JPEG header OK")
else:
    print(f"First 16 hex: {raw[:16].hex()}")

with open(OUT, "wb") as f:
    f.write(raw)
print(f"Saved to {OUT}")
print(f"File size: {len(raw)} bytes")
