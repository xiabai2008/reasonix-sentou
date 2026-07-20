#!/usr/bin/env python3
"""
[已升级] brute-flask.py 已整合到 brute.py，功能更强。

用法:
  python config/brute.py <url> -u admin -d config/admin-top500.txt

本文件保留只为兼容旧命令，请使用 brute.py。
"""
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
new_script = os.path.join(BASE, "brute.py")

if not os.path.exists(new_script):
    print("错误: 请使用 python config/brute.py")
    sys.exit(1)

# 将参数透传给 brute.py
os.execvp(sys.executable, [sys.executable, new_script] + sys.argv[1:])
