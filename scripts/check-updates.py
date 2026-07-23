#!/usr/bin/env python3
"""
Reasonix 工具链版本检查

读取 config/tools-manifest.json，对比本地工具版本与 GitHub Release 最新版本。

用法:
    python scripts/check-updates.py            # 检查所有工具
    python scripts/check-updates.py --json     # JSON 输出
    python scripts/check-updates.py --tool nuclei  # 检查单个工具
    python scripts/check-updates.py --gh-token xxx  # 使用 GitHub Token (提高 API 限流)

依赖: requests
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("[ERROR] 需要 requests 库: pip install requests", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
MANIFEST_FILE = PROJECT_ROOT / "config" / "tools-manifest.json"
CACHE_FILE = PROJECT_ROOT / "tmp" / "tool-versions-cache.json"

GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "reasonix-tool-checker",
}


def load_manifest() -> dict:
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_local_version(tool_name: str, bin_name: str) -> str | None:
    """尝试获取本地工具版本"""
    tool_path = TOOLS_DIR / bin_name
    if not tool_path.exists():
        return None

    version_cmds = {
        "nuclei": ["-version"],
        "naabu": ["-version"],
        "httpx": ["-version"],
        "subfinder": ["-version"],
        "ffuf": ["-V"],
        "jq": ["--version"],
        "katana": ["-version"],
        "dnsx": ["-version"],
        "tlsx": ["-version"],
        "gau": ["-version"],
    }

    args = version_cmds.get(tool_name, ["--version"])
    try:
        result = subprocess.run(
            [str(tool_path)] + args,
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout + result.stderr
        # 提取版本号 (常见格式: v1.2.3 或 1.2.3)
        match = re.search(r'v?(\d+\.\d+\.\d+)', output)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def get_github_latest(repo: str, token: str | None = None) -> dict | None:
    """从 GitHub API 获取最新 Release"""
    url = f"{GITHUB_API}/repos/{repo}/releases/latest"
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            tag = data.get("tag_name", "")
            # 去除 v 前缀
            version = tag.lstrip("v") if tag else "unknown"
            return {
                "version": version,
                "tag": tag,
                "published": data.get("published_at", ""),
                "url": data.get("html_url", ""),
            }
        elif resp.status_code == 403:
            return {"version": "rate-limited", "error": "GitHub API 限流 (60次/小时)，使用 --gh-token 提高限制"}
        elif resp.status_code == 404:
            return {"version": "no-release", "error": "仓库无 Release"}
    except requests.RequestException as e:
        return {"version": "error", "error": str(e)}
    return None


def load_cache() -> dict:
    """加载本地缓存 (减少 API 调用)"""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(data: dict):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def check_tool(name: str, info: dict, token: str | None, cache: dict) -> dict:
    """检查单个工具"""
    bin_name = info.get("bin", "")
    repo = info.get("repo", "")
    category = info.get("category", "")

    result = {
        "tool": name,
        "category": category,
        "local_version": None,
        "latest_version": None,
        "status": "unknown",
        "message": "",
    }

    # 本地版本
    local = get_local_version(name, bin_name)
    result["local_version"] = local
    if not local:
        result["status"] = "not-found"
        result["message"] = f"本地未找到 {bin_name}"
        return result

    # 检查缓存 (24 小时内有效)
    cached = cache.get(name, {})
    cache_time = cached.get("checked_at", 0)
    if cache_time and (time.time() - cache_time) < 86400:
        result["latest_version"] = cached.get("latest_version", "")
        result["cached"] = True
    else:
        # GitHub API
        latest = get_github_latest(repo, token)
        if latest:
            result["latest_version"] = latest.get("version", "")
            result["published"] = latest.get("published", "")
            result["release_url"] = latest.get("url", "")
            cache[name] = {
                "latest_version": result["latest_version"],
                "checked_at": time.time(),
            }
        else:
            result["status"] = "api-error"
            result["message"] = "无法获取最新版本"
            return result

    # 版本对比
    local_v = result["local_version"]
    latest_v = result["latest_version"]

    if local_v and latest_v and latest_v not in ("rate-limited", "no-release", "error", "unknown"):
        if local_v == latest_v:
            result["status"] = "up-to-date"
            result["message"] = f"已是最新版本 ({local_v})"
        else:
            result["status"] = "outdated"
            result["message"] = f"可更新: {local_v} → {latest_v}"
    elif latest_v == "rate-limited":
        result["status"] = "rate-limited"
        result["message"] = "GitHub API 限流 — 1小时后重试或使用 --gh-token"
    else:
        result["status"] = "ok"
        result["message"] = f"当前版本: {local_v}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Reasonix 工具链版本检查")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--tool", help="仅检查指定工具")
    parser.add_argument("--gh-token", help="GitHub Personal Access Token (提高 API 限流)")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    args = parser.parse_args()

    manifest = load_manifest()
    cache = {} if args.no_cache else load_cache()

    tools_to_check = {}

    # tools 部分
    for name, info in manifest.get("tools", {}).items():
        if args.tool and args.tool != name:
            continue
        tools_to_check[name] = info

    # cloned_tools 部分 (-clone 后缀标记)
    for name, info in manifest.get("cloned_tools", {}).items():
        if args.tool and args.tool != name.lower():
            continue
        info["bin"] = ""  # cloned tools 无本地二进制
        tools_to_check[name.lower()] = info

    if not tools_to_check:
        print(f"[!] 未找到工具: {args.tool}", file=sys.stderr)
        sys.exit(1)

    results = []
    for name, info in tools_to_check.items():
        result = check_tool(name, info, args.gh_token, cache)
        results.append(result)

    save_cache(cache)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 65)
        print("  Reasonix 工具链版本检查")
        print(f"  检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)

        up_to_date = 0
        outdated = 0
        not_found = 0

        for r in results:
            status_icon = {
                "up-to-date": "✅",
                "outdated": "🔶",
                "not-found": "❌",
                "rate-limited": "⏳",
                "ok": "✅",
                "api-error": "⚠️",
            }.get(r["status"], "❓")

            local = r.get("local_version") or "—"
            latest = r.get("latest_version") or "—"
            print(f"  {status_icon} {r['tool']:12s} {local:10s} → {latest:10s} {r.get('message', '')}")

            if r["status"] == "up-to-date" or r["status"] == "ok":
                up_to_date += 1
            elif r["status"] == "outdated":
                outdated += 1
            elif r["status"] == "not-found":
                not_found += 1

        print("-" * 65)
        print(f"  已是最新: {up_to_date} | 可更新: {outdated} | 未安装: {not_found}")
        print()

        if outdated > 0:
            print("  [!] 有工具可更新。下载最新版:")
            for r in results:
                if r["status"] == "outdated":
                    print(f"      {r['tool']}: {r.get('release_url', '')}")
            print()


if __name__ == "__main__":
    main()
