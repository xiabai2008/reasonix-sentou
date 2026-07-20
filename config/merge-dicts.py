#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典管理工具 — 下载 + 合并 + 更新
用法:
  python merge-dicts.py        # 合并所有字典
  python merge-dicts.py --download  # 从 GitHub 重新下载
"""
import os
import sys
import argparse

BASE = os.path.dirname(os.path.abspath(__file__))
DICT_DIR = os.path.join(BASE, "dictionaries")
CONFIG_DIR = BASE
PROJECT = os.path.dirname(BASE)

OUT = print


def load_words(path):
    """加载字典，去空行注释"""
    words = set()
    if not os.path.exists(path):
        return words
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                words.add(line)
    return words


def save_words(words, path, header=""):
    """保存字典"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if header:
            f.write(f"# {header}\n")
        for w in sorted(words):
            f.write(w + "\n")
    return len(words)


def merge():
    """合并所有字典源"""
    OUT("=" * 60)
    OUT("  [MERGE] 合并字典...")
    OUT("=" * 60)

    # === 精选 Top 合集（各 Top 1000 合并）===
    elite = set()
    sources_elite = [
        ("zh_cn_top1000.txt", "中文 Top 1000"),
        ("pwdb_top1000.txt", "PasswordDB Top 1000"),
        ("xato_top1000.txt", "xato.net Top 1000"),
        ("probable_top1575.txt", "Probable v2 Top 1575"),
        ("../ctf-passwords.txt", "CTF 自建"),
        ("../cn-passwords.txt", "中文自建"),
        ("../admin-top500.txt", "Admin 自建"),
        ("../top100-passwords.txt", "Top100 自建"),
    ]
    for fname, desc in sources_elite:
        path = os.path.join(DICT_DIR, fname)
        # 处理相对路径
        if fname.startswith(".."):
            path = os.path.normpath(os.path.join(DICT_DIR, fname))
        words = load_words(path)
        before = len(elite)
        elite |= words
        added = len(elite) - before
        OUT(f"  [IN]  {desc:25s} {len(words):>5} -> +{added:>4} = {len(elite):>5}")

    save_words(elite, os.path.join(CONFIG_DIR, "elite-passwords.txt"),
               f"精华字典合集 ({len(sources_elite)}源, {len(elite)}条去重)")
    OUT(f"\n  [OK]  elite-passwords.txt -> {len(elite)} 条")

    # === 全量超级字典（所有 10k 级别合并）===
    mega = set()
    sources_mega = [
        ("zh_cn_top10000.txt", "中文 Top 10000"),
        ("pwdb_top10000.txt", "PasswordDB Top 10000"),
        ("xato_top10000.txt", "xato.net Top 10000"),
        ("10k-most-common.txt", "NCSC 10k"),
        ("../10k-passwords.txt", "自有 10k"),
        ("../all-passwords-merged.txt", "自建全量"),
    ]
    for fname, desc in sources_mega:
        path = os.path.join(DICT_DIR, fname)
        if fname.startswith(".."):
            path = os.path.normpath(os.path.join(CONFIG_DIR, fname))
        words = load_words(path)
        before = len(mega)
        mega |= words
        added = len(mega) - before
        OUT(f"  [IN]  {desc:25s} {len(words):>6} -> +{added:>5} = {len(mega):>6}")

    # 也加入精英集合
    mega |= elite

    save_words(mega, os.path.join(CONFIG_DIR, "mega-passwords.txt"),
               f"全量超级字典 ({len(sources_mega)}源 + 精英, {len(mega)}条去重)")
    OUT(f"\n  [OK]  mega-passwords.txt -> {len(mega)} 条")

    # === 用户名合并 ===
    users = set()
    user_sources = [
        ("top-usernames.txt", "SecLists Top"),
        ("default-usernames.txt", "CIRT 默认"),
        ("common-admin-base64.txt", "Admin Base64"),
        ("../top100-passwords.txt", "",  # 补常用的用户名如 admin/root/test
         ),
    ]
    # 加常用管理用户名
    admin_users = ["admin", "root", "test", "guest", "user", "manager",
                   "system", "administrator", "operator", "demo",
                   "sa", "oracle", "mysql", "postgres",
                   "tomcat", "jboss", "weblogic", "webadmin",
                   "admin888", "admin123",
                   "zhangsan", "lisi", "wangwu"]
    users.update(admin_users)

    for fname, desc in user_sources:
        if fname.startswith(".."):
            path = os.path.normpath(os.path.join(CONFIG_DIR, fname))
        else:
            path = os.path.join(DICT_DIR, fname)
        if os.path.exists(path):
            words = load_words(path)
            users |= words

    save_words(users, os.path.join(CONFIG_DIR, "users-common.txt"),
               f"常用用户名合集 ({len(users)}条)")
    OUT(f"  [OK]  users-common.txt -> {len(users)} 条")

    # === 文件名对比 ===
    OUT("\n" + "=" * 60)
    OUT("  [DONE] 字典文件一览")
    OUT("=" * 60)
    all_txt = []
    # config/
    for f in sorted(os.listdir(CONFIG_DIR)):
        if f.endswith(".txt") and "pass" in f.lower():
            path = os.path.join(CONFIG_DIR, f)
            cnt = len(load_words(path))
            all_txt.append(("config/" + f, cnt))
    # dictionaries/
    for f in sorted(os.listdir(DICT_DIR)):
        if f.endswith(".txt"):
            path = os.path.join(DICT_DIR, f)
            cnt = len(load_words(path))
            all_txt.append(("dictionaries/" + f, cnt))

    for name, cnt in sorted(all_txt, key=lambda x: -x[1]):
        OUT(f"  {name:45s} {cnt:>7,} 条")
    OUT(f"  {'总计':45s} {sum(c for _,c in all_txt):>7,} 条 (含重复)")


def download():
    """调用下载脚本"""
    download_script = os.path.join(BASE, "download-dicts.py")
    if os.path.exists(download_script):
        OUT("\n  [DL] 执行 download-dicts.py...")
        os.system(f'"{sys.executable}" "{download_script}"')
    else:
        OUT("  [ERR] download-dicts.py 不存在")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="字典管理工具")
    parser.add_argument("--download", action="store_true", help="重新从 GitHub 下载")
    parser.add_argument("--merge-only", action="store_true", help="仅合并不下载")
    args = parser.parse_args()

    if args.download:
        download()
    merge()
