#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 GitHub SecLists 下载精选字典
来源: https://github.com/danielmiessler/SecLists
"""
import os
import sys
import urllib.request
import ssl

BASE = "https://raw.githubusercontent.com/danielmiessler/SecLists/master"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionaries")
os.makedirs(OUT, exist_ok=True)

# 忽略 SSL 证书（Windows 环境问题）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

FILES = [
    # === 中文密码（最优先）===
    ("Passwords/Common-Credentials/Language-Specific/Chinese-common-password-list-top-1000.txt",
     "zh_cn_top1000.txt",
     "中文常用密码 Top 1000"),
    ("Passwords/Common-Credentials/Language-Specific/Chinese-common-password-list-top-10000.txt",
     "zh_cn_top10000.txt",
     "中文常用密码 Top 10000"),

    # === 综合 Top 列表 ===
    ("Passwords/Common-Credentials/Pwdb_top-1000.txt",
     "pwdb_top1000.txt",
     "PasswordDB Top 1000 (多数据源合并)"),
    ("Passwords/Common-Credentials/Pwdb_top-10000.txt",
     "pwdb_top10000.txt",
     "PasswordDB Top 10000"),
    ("Passwords/Common-Credentials/xato-net-10-million-passwords-1000.txt",
     "xato_top1000.txt",
     "xato.net Top 1000 (10M数据源)"),
    ("Passwords/Common-Credentials/xato-net-10-million-passwords-10000.txt",
     "xato_top10000.txt",
     "xato.net Top 10000"),
    ("Passwords/Common-Credentials/probable-v2_top-1575.txt",
     "probable_top1575.txt",
     "Probable-Wordlists v2 Top 1575"),

    # === 特定列表 ===
    ("Passwords/Common-Credentials/500-worst-passwords.txt",
     "500-worst-passwords.txt",
     "500个最差密码"),
    ("Passwords/Common-Credentials/2025-199_most_used_passwords.txt",
     "2025_top199.txt",
     "2025年度 Top 199 密码"),
    ("Passwords/Common-Credentials/2024-197_most_used_passwords.txt",
     "2024_top197.txt",
     "2024年度 Top 197 密码"),
    ("Passwords/Common-Credentials/10k-most-common.txt",
     "10k-most-common.txt",
     "10k最常用密码 (NCSC)"),
    ("Passwords/Common-Credentials/common-passwords-win.txt",
     "win-passwords.txt",
     "Windows 常见密码"),

    # === 用户名字典 ===
    ("Usernames/top-usernames-shortlist.txt",
     "top-usernames.txt",
     "Top用户名简表"),
    ("Usernames/cirt-default-usernames.txt",
     "default-usernames.txt",
     "CIRT 默认用户名列表"),
    ("Usernames/CommonAdminBase64.txt",
     "common-admin-base64.txt",
     "通用管理账号 (Base64编码)"),

    # === Web 渗透专项 ===
    ("Discovery/Web-Content/burp-parameter-names.txt",
     "web-params.txt",
     "Web参数名 (Burp)"),
]


def download(url, filename, desc):
    path = os.path.join(OUT, filename)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        size = os.path.getsize(path)
        print(f"  [SKIP] {filename:30s} 已存在 ({size:,} bytes)")
        return
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read()
        with open(path, "wb") as f:
            f.write(data)
        lines = len(data.decode("utf-8", errors="ignore").splitlines())
        print(f"  [OK]   {filename:30s} {lines:>6} 行 ({desc})")
    except Exception as e:
        print(f"  [ERR]  {filename:30s} {e}")


if __name__ == "__main__":
    print("=" * 65)
    print("  从 SecLists 下载精选字典")
    print(f"  来源: {BASE}")
    print(f"  保存: {OUT}")
    print("=" * 65)

    for path, filename, desc in FILES:
        url = f"{BASE}/{path}"
        download(url, filename, desc)

    print("=" * 65)
    print("  下载完成！")
    print(f"  字典目录: {OUT}")
    print("=" * 65)
