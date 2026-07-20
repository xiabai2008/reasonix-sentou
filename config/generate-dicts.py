#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典生成工具 — 生成 CTF/中文/Admin 专用弱口令字典
"""

import os
import sys

# Windows GBK 终端兼容
if sys.stdout.encoding and sys.stdout.encoding.upper() in ("GBK", "GB2312", "CP936"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = print


# ========== 1. CTF 环境专用字典 ==========
ctf_passwords = [
    # admin系列（最常见）
    "admin", "admin123", "admin123456", "admin12345678", "admin888",
    "admin@123", "admin!@#", "admin!@#123", "admin@2024", "admin@2025",
    "admin#123", "admin2024", "admin2025", "admin2023",
    "admin1", "admin12", "admin1234", "admin12345",
    "admin!", "admin@", "admin#",
    "adm!n", "adm1n", "adm1n123",
    # root系列
    "root", "root123", "root123456", "root!@#", "root@123", "toor",
    # 纯数字最常用
    "123456", "12345678", "123456789", "1234567890", "1234", "12345",
    "111111", "222222", "333333", "444444", "555555",
    "666666", "777777", "888888", "999999", "000000",
    "112233", "123123", "123321", "5201314",
    # 键盘序列
    "qwerty", "qwerty123", "qwerty123456", "qwertyuiop",
    "1q2w3e", "1q2w3e4r", "1qaz2wsx", "qazwsx", "qazwsx123",
    "asdfgh", "zxcvbn", "zxcvbnm",
    "!@#$%^", "!@#123", "!@#$%^&*",
    # 常见英文密码
    "password", "pass123", "pass@123", "passw0rd",
    "Passw0rd", "Pass@123", "P@ssw0rd", "P@ss123",
    "letmein", "welcome", "welcome123", "Welcome123",
    "iloveyou", "sunshine", "monkey", "dragon", "master", "shadow",
    "football", "baseball", "batman", "superman",
    "princess", "michael", "jennifer", "thomas", "andrew",
    "sexy", "love",
    # 系统/服务默认
    "test", "test123", "test123456", "test!@#",
    "guest", "guest123",
    "user", "user123", "user123456",
    "system", "system123", "manager", "manager123",
    "default", "default123", "temp123",
    "server", "server123",
    "demo", "demo123",
    "info", "info123",
    "web", "web123", "webadmin",
    "tomcat", "jetty", "nginx", "apache", "mysql",
    # 安全审计常见
    "123qwe", "123qweasd",
    "aaa123", "aaa111",
    "abc123", "abc123456", "abcd1234", "abcd123",
    "password123", "password123456",
    "password1", "password!",
    # 英文单词
    "hello", "hello123", "world", "world123",
    "china", "china123",
    "beijing", "beijing123",
    "shanghai", "guangzhou",
    "school", "college", "university",
    "hacker", "hack123", "hackme",
    "security", "secure123",
    "flag", "flag123",
    "ctf", "ctf123",
    # 日期相关
    "2024", "2025", "2023", "2022", "2021", "2020",
    "2008", "20080808", "20081212",
    # 简单组合
    "a123456", "a12345678",
    "aa123456", "aa12345678",
    "wang123", "li123",
]

# ========== 2. 中文环境常用弱口令 ==========
cn_passwords = [
    # admin中文环境
    "admin", "admin123", "admin123456", "admin888", "admin@123",
    "admin!@#", "admin2024", "admin2025", "admin!@#123",
    "adm1n", "adm1n123",
    # 纯数字
    "123456", "12345678", "123456789", "1234567890",
    "111111", "222222", "333333", "444444", "555555",
    "666666", "777777", "888888", "999999", "000000",
    "123123", "123321", "123456a", "123456b",
    "5201314", "1314520", "7758258",
    "521", "1314", "520", "520520",
    "88888888", "66666666",
    "10086", "10010", "10000",
    # 拼音弱口令（中国特色）
    "zhangsan", "lisi", "wangwu", "zhaoliu",
    "xiaoming", "xiaohong",
    "guanliyuan", "guanli",
    "mima", "mima123", "shebei", "shebei123",
    "nicheng", "yonghu",
    "ceshi", "ceshi123", "ceshiyonghu",
    "denglu", "denglu123",
    "xitong", "xitong123",
    "kaoshi", "kaoshi123", "exam123",
    # 拼音地名
    "beijing", "shanghai", "guangzhou", "shenzhen",
    "hangzhou", "chengdu", "wuhan", "nanjing",
    "tianjin", "chongqing", "xiamen",
    "zhongguo", "zhonghua", "renmin",
    # 中文服务默认
    "root", "root123",
    "test", "test123", "test123456",
    "admin000",
    "guest", "guest123",
    "user123", "useradmin",
    "system123", "system!@#",
    # 互联网常用
    "taobao", "alipay", "weixin", "qq123456",
    "qq", "qq123", "qq123456",
    "baidu", "google", "sina", "163", "126",
    "sohu",
    # 安全弱项
    "1234", "12345", "1234567",
    "123456789a", "123456789b",
    "abcdef", "abcdefg",
    "a1b2c3", "a1b2c3d4",
    "password1", "password12",
    "passw0rd", "P@ssw0rd",
    # 中文系统常见
    "123@#", "qwe123", "qwe123456",
    "1q2w3e", "1q2w3e4r",
    "abc123", "ABC123",
    "iloveyou",
    # 更多中文特色
    "niuniu", "kaixin",
    "tiantian", "meinv",
    "laowang", "laoli",
    "ftp123", "mysql", "oracle",
    "weblogic", "jboss", "jboss123",
]

# ========== 3. Admin 专用 Top 500 ==========
admin_passwords = set()
a = "admin"

# admin + 数字后缀（大范围）
for suffix in ["", "123", "1234", "12345", "123456", "12345678", "123456789",
               "888", "000", "666", "111", "999", "520", "521",
               "555", "333", "222", "777", "444",
               "001", "002",
               "2024", "2025", "2023", "2020", "2022", "2021",
               "2019", "2018", "2017", "2016", "2015"]:
    admin_passwords.add(f"{a}{suffix}")

# admin + 符号后缀
for suffix in ["@123", "!@#", "#123", "!23",
               "@2024", "!2024", "@2025", "!2025",
               "!", "@", "#", "!@#", "@@", "##",
               ".", ";", ",", ":", "~", "?",
               "!@#$", "!@#$%",
               "@1234", "#1234",
               "2024!", "2024@"]:
    admin_passwords.add(f"{a}{suffix}")

# admin + 字母后缀
for suffix in ["a", "b", "c", "d", "e", "f", "g", "h",
               "aa", "bb", "cc", "dd", "ab", "cd",
               "abc", "xyz", "test", "demo"]:
    admin_passwords.add(f"{a}{suffix}")

# admin + cms/php/panel 等
for ext in ["cms", "php", "asp", "aspx", "net", "web", "site", "login",
            "panel", "root", "user", "pass", "pwd", "system",
            "manager", "admin", "master"]:
    admin_passwords.add(f"{a}{ext}")
    admin_passwords.add(f"{a}_{ext}")

# 前缀组合
for prefix in ["root", "test", "guest", "super", "web", "sys", "local",
               "master", "main", "primary", "cloud", "vip",
               "bk", "backup", "new", "old"]:
    admin_passwords.add(f"{prefix}{a}")
    admin_passwords.add(f"{prefix}{a}123")
    admin_passwords.add(f"{prefix}{a}!@#")
    admin_passwords.add(f"{a}_{prefix}")

# admin + 连续两位数字
for i in range(10):
    for j in range(10):
        admin_passwords.add(f"{a}{i}{j}")

# admin + 年份范围
for year in range(2010, 2026):
    admin_passwords.add(f"{a}{year}")

# 大小写
for case in [a.capitalize(), a.upper(), a.lower()]:
    admin_passwords.add(case)
    admin_passwords.add(f"{case}123")
    admin_passwords.add(f"{case}!@#")

# leet / 变体
for leet in ["adm1n", "adm1n123", "adm1n@123", "@dm1n", "@dmin",
             "4dm1n", "4dmin", "4dm1n123",
             "admin!!", "admin!!!"]:
    admin_passwords.add(leet)

# 双写
for suffix in ["", "123", "!@#", "2024"]:
    admin_passwords.add(f"{a}{a}{suffix}")

# admin123+ 扩展
for extra in ["1234", "12345", "123456", "!@#$", "20242025"]:
    admin_passwords.add(f"{a}123{extra}")

# 特殊格式
for fmt in ["()", "[]", "{}", "-123", "_123", "()123"]:
    admin_passwords.add(f"{a}{fmt}")

# root 变体
for r in ["root"]:
    for suffix in ["", "123", "1234", "123456", "12345678", "123456789",
                   "!@#", "@123", "#123",
                   "toor", "r00t", "R00t", "r007",
                   "2024", "2025", "2023", "2020"]:
        admin_passwords.add(f"{r}{suffix}")

# 纯数字（常见）
for n in ["123456", "12345678", "123456789", "111111", "222222", "333333",
          "444444", "555555", "666666", "777777", "888888", "999999", "000000",
          "123123", "123321", "112233", "5201314", "1314520"]:
    admin_passwords.add(n)

# 常见弱口令
common = ["password", "pass123", "passw0rd", "P@ssw0rd", "Pass@123",
          "123qwe", "1q2w3e", "1q2w3e4r", "1qaz2wsx", "qazwsx",
          "qwerty", "qwerty123", "asdfgh", "zxcvbn",
          "welcome", "welcome123", "letmein",
          "test", "test123", "test123456",
          "abc123", "abc123456", "abcd1234",
          "iloveyou", "monkey", "dragon", "master",
          "football", "baseball", "sunshine",
          "hello", "hello123", "world123",
          "china", "china123",
          "beijing", "shanghai",
          "server", "server123",
          "system", "system123",
          "manager", "manager123",
          "default", "default123",
          "hacker", "hack123",
          "!@#$%", "!@#123", "!@#$%^&*",
          "123456a", "123456b", "123456c",
          "ceshi", "ceshi123",
          "mima", "mima123",
          "a123456", "a12345678",
          "guest", "guest123",
          "user", "user123"]
for c in common:
    admin_passwords.add(c)

# 排序：admin(0) > root(1) > test(2) > 纯数字(3) > 其他(4)
admin_sorted = sorted(admin_passwords, key=lambda x: (
    0 if x.startswith("admin") else
    1 if x.startswith("root") else
    2 if x.startswith("test") else
    3 if x.isdigit() and len(x) >= 6 else
    4
))
admin_sorted = admin_sorted[:500]


def ensure_unique_and_save(passwords, filename, header=""):
    """去重并保留顺序写入文件"""
    seen = set()
    unique = []
    for p in passwords:
        p_stripped = p.strip()
        if p_stripped and p_stripped not in seen:
            seen.add(p_stripped)
            unique.append(p_stripped)
    filepath = os.path.join(BASE, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        if header:
            f.write(header + "\n")
        for p in unique:
            f.write(p + "\n")
    OUT(f"[OK] {filename} -> {len(unique)} tiao")
    return set(unique)


def merge_dedupe(*sets):
    """合并多个集合"""
    merged = set()
    for s in sets:
        merged |= s
    return merged


if __name__ == "__main__":
    OUT("=" * 50)
    OUT("  [PASSWORD-DICT] 字典生成工具")
    OUT("=" * 50)

    # 1. CTF 专用字典
    ctf_set = ensure_unique_and_save(ctf_passwords, "ctf-passwords.txt",
                                      "# CTF/考试环境专用弱口令字典")
    # 2. 中文环境字典
    cn_set = ensure_unique_and_save(cn_passwords, "cn-passwords.txt",
                                     "# 中文环境常用弱口令字典")
    # 3. Admin 专用
    admin_set = ensure_unique_and_save(admin_sorted, "admin-top500.txt",
                                        "# Admin 专用弱口令 Top 500")
    # 4. 合并全量（含已有 10k-passwords.txt）
    all_set = merge_dedupe(ctf_set, cn_set, admin_set)
    old_10k = os.path.join(BASE, "10k-passwords.txt")
    if os.path.exists(old_10k):
        with open(old_10k, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    all_set.add(line)
        OUT(f"[MERGE] 已合并 10k-passwords.txt")

    ensure_unique_and_save(sorted(all_set), "all-passwords-merged.txt",
                            "# 全量字典合并(去重)")

    OUT("")
    OUT("=" * 50)
    OUT(f"  [DONE] 总计去重后: {len(all_set)} 条口令")
    OUT("=" * 50)
    OUT("")
    OUT("[FILES] 字典文件列表:")
    for fname in ["ctf-passwords.txt", "cn-passwords.txt",
                   "admin-top500.txt", "all-passwords-merged.txt"]:
        fpath = os.path.join(BASE, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            with open(fpath, "r", encoding="utf-8") as fh:
                count = sum(1 for line in fh if line.strip()
                            and not line.startswith("#"))
            OUT(f"   config/{fname:30s} {count:5d} tiao  ({size:,} bytes)")
