#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-manifest.py — 校验 config/tools-manifest.json 的资产匹配规则

逐条核对 manifest 中每个二进制工具的 asset_pattern 是否能在对应仓库的
最新 release 里真实匹配到资产。防止出现"asset_pattern 写错 → 用户下载失败"
这类问题（历史上 dalfox / fscan 都踩过）。

用法:
    python scripts/validate-manifest.py            # 联网校验 assets
    python scripts/validate-manifest.py --offline  # 仅校验结构/正则合法性，不联网

退出码: 0 = 全部通过, 1 = 存在失败
"""
import argparse
import json
import os
import re
import sys
import urllib.request

MANIFEST = os.path.join(os.path.dirname(__file__), "..", "config", "tools-manifest.json")


def load_manifest():
    with open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def fetch_latest_assets(repo, token=None):
    """返回 repo 最新 release 的资产名列表。"""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest")
    req.add_header("User-Agent", "DawnForge-manifest-validator")
    if token:
        req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return [a.get("name", "") for a in data.get("assets", [])]


def main():
    ap = argparse.ArgumentParser(description="Validate tools-manifest.json asset patterns")
    ap.add_argument("--offline", action="store_true", help="skip network checks, only validate structure/regex")
    args = ap.parse_args()

    manifest = load_manifest()
    errors = []
    checked = 0
    token = os.environ.get("GITHUB_TOKEN")

    tools = manifest.get("tools", {})
    for name, conf in tools.items():
        pattern = conf.get("asset_pattern")
        if not pattern:
            errors.append(f"  {name}: 缺少 asset_pattern")
            continue
        # 结构/正则合法性校验（离线和联网都做）
        try:
            re.compile(pattern)
        except re.error as exc:
            errors.append(f"  {name}: asset_pattern 正则非法 ({exc})")
            continue

        if args.offline:
            continue

        repo = conf.get("repo")
        if not repo:
            errors.append(f"  {name}: 缺少 repo")
            continue
        try:
            assets = fetch_latest_assets(repo, token)
        except Exception as exc:
            errors.append(f"  {name} ({repo}): 无法获取 release — {exc}")
            continue

        checked += 1
        if not assets:
            errors.append(f"  {name} ({repo}): 最新 release 无任何资产")
            continue
        matched = [a for a in assets if re.search(pattern, a)]
        if not matched:
            errors.append(
                f"  {name} ({repo}): asset_pattern '{pattern}' 未匹配到任何资产。"
                f"实际资产: {', '.join(assets[:6])}"
            )

    if errors:
        print("FAIL: tools-manifest.json 存在需要修复的问题:")
        for e in errors:
            print(e)
        print(f"\n已联网校验 {checked} 个工具，{len(errors)} 个问题。")
        return 1

    if args.offline:
        print(f"OK: 结构校验通过（{len(tools)} 个工具，offline 模式未联网）。")
    else:
        print(f"OK: {len(tools)} 个工具的 asset_pattern 均能在最新 release 中匹配（联网校验 {checked} 个）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())