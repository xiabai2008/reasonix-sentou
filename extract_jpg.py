#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 flag.jpg 从 FTP data stream 324"""
import subprocess
import binascii
import os

pcap = r"C:\Users\HZR\Desktop\capture.pcapng"
tshark = r"C:\Program Files\Wireshark\tshark.exe"
out = r"C:\Users\HZR\Downloads\flag.jpg"

# 方法1: 直接提取 ftp-data 数据
r = subprocess.run(
    [tshark, "-r", pcap,
     "-Y", "tcp.stream eq 324 and ftp-data",
     "-T", "fields", "-e", "data.data"],
    capture_output=True, timeout=30
)
lines = r.stdout.decode("utf-8", errors="replace").strip().split("\n")
hex_data = "".join(l.strip() for l in lines if l.strip())

if hex_data:
    raw = binascii.unhexlify(hex_data)
    print(f"Method 1: Extracted {len(raw)} bytes, starts with: {raw[:16].hex()}")
    with open(out, "wb") as f:
        f.write(raw)
    
    # 检查是否是 JPEG
    if raw[:2] == b"\xff\xd8":
        print("Verified: JPEG file!")
else:
    # 方法2: 尝试从 data 字段直接提取
    print("Method 1 failed, trying method 2...")
    # 直接提取大块 TCP 数据
    r2 = subprocess.run(
        [tshark, "-r", pcap,
         "-Y", "tcp.stream eq 324 and tcp.len>0",
         "-T", "fields", "-e", "tcp.payload"],
        capture_output=True, timeout=30
    )
    lines2 = r2.stdout.decode("utf-8", errors="replace").strip().split("\n")
    hex_data2 = "".join(l.strip() for l in lines2 if l.strip())
    if hex_data2:
        raw2 = binascii.unhexlify(hex_data2)
        print(f"Method 2: Extracted {len(raw2)} bytes")
        print(f"First 64 hex: {raw2[:32].hex()}")
        print(f"First 32 ascii: {raw2[:32]}")
    else:
        print("Both methods failed to extract data")
