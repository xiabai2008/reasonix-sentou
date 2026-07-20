#!/usr/bin/env python3
"""
Download specific SecLists subdirectories via GitHub API + raw.githubusercontent.com
Usage: python scripts/download-seclists.py
Target: config/dictionaries/SecLists/<subdir>/
"""

import os, requests, json, sys

BASE_API = "https://api.github.com/repos/danielmiessler/SecLists/contents"
RAW_BASE = "https://raw.githubusercontent.com/danielmiessler/SecLists/master"
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "dictionaries", "SecLists")

# Key directories to download (most useful for pentesting)
TARGET_DIRS = [
    "Passwords/Common-Credentials",
    "Passwords/Software",
    "Passwords/darkweb2017",
    "Usernames",
    "Discovery/Web-Content",
    "Discovery/DNS",
]

def download_file(url, dest):
    """Download a single file from raw url to dest path"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        print(f"  ⏭️ 跳过已有: {os.path.relpath(dest, OUT_DIR)} ({size//1024}KB)")
        return
    try:
        r = requests.get(url, timeout=(10, 60))
        r.raise_for_status()
        with open(dest, 'wb') as f:
            f.write(r.content)
        print(f"  ✅ {os.path.relpath(dest, OUT_DIR)} ({len(r.content)//1024}KB)")
    except Exception as e:
        print(f"  ❌ {url}: {e}")

def list_dir(api_url, prefix=""):
    """List directory contents recursively via GitHub API"""
    try:
        r = requests.get(api_url, timeout=15)
        r.raise_for_status()
        items = r.json()
        if isinstance(items, dict):
            items = [items]
        for item in items:
            name = item["name"]
            path = item["path"]
            if item["type"] == "file":
                # Skip large binary files
                size = item.get("size", 0)
                if size > 50 * 1024 * 1024:  # > 50MB skip
                    print(f"  ⏭️ 过大文件跳过: {path} ({size//1024//1024}MB)")
                    continue
                raw_url = f"{RAW_BASE}/{path}"
                dest_path = os.path.join(OUT_DIR, path)
                yield raw_url, dest_path
            elif item["type"] == "dir":
                yield from list_dir(item["url"], prefix)
    except Exception as e:
        print(f"  ❌ 列表获取失败 {api_url}: {e}")

def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    
    total = 0
    # First, download specific useful dirs
    for target_dir in TARGET_DIRS:
        api_url = f"{BASE_API}/{target_dir}"
        print(f"\n📁 下载目录: {target_dir}")
        count = 0
        for raw_url, dest_path in list_dir(api_url):
            download_file(raw_url, dest_path)
            count += 1
            total += 1
        print(f"   完成: {count} 个文件")
    
    print(f"\n🎉 总计下载 {total} 个文件到 {OUT_DIR}")

if __name__ == "__main__":
    main()
