#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-tool-table.py — 从 config/tools-manifest.json 自动生成 README 工具清单表格

用法:
    python scripts/gen-tool-table.py              # 生成并回写 README.md / README.zh-CN.md
    python scripts/gen-tool-table.py --dry-run    # 只打印不写文件

机制:
    在 README 中查找两个标记之间的工具清单表格并整体替换，保证与 manifest 一致。
        起始标记: <!-- TOOL-TABLE:BEGIN -->
        结束标记: <!-- TOOL-TABLE:END -->
    若 README 中尚不存在标记，则不会改动（首次需手动插入标记）。

说明:
    manifest 只含 来源仓库/资产匹配/目标路径，不含用途文案，
    因此本脚本内置 ROLE_MAP 维护"工具 -> 用途"的中英双语描述。
    新增工具需同时: 1) 在 manifest 登记; 2) 在 ROLE_MAP 补充用途。
"""

import argparse
import json
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(PROJECT_DIR, "config", "tools-manifest.json")
README_EN = os.path.join(PROJECT_DIR, "README.md")
README_ZH = os.path.join(PROJECT_DIR, "README.zh-CN.md")

BEGIN_MARK = "<!-- TOOL-TABLE:BEGIN -->"
END_MARK = "<!-- TOOL-TABLE:END -->"

# 工具 -> (英文用途, 中文用途)
ROLE_MAP = {
    "fscan": ("Intranet port scan + brute-force + POC / 内网扫描", "内网扫描（端口+爆破+POC）"),
    "naabu": ("Fast port scan / 快速端口扫描", "快速端口扫描"),
    "nuclei": ("Vulnerability scan (125k+ templates) / 漏洞扫描", "漏洞扫描（12.5w+ 模板）"),
    "httpx": ("HTTP probing / tech-stack fingerprint / Web 探活", "Web 探活 / 技术栈指纹"),
    "subfinder": ("Passive subdomain enumeration / 子域名被动枚举", "子域名被动枚举"),
    "katana": ("Crawler / 爬虫", "爬虫"),
    "dnsx": ("DNS toolkit / DNS 工具包", "DNS 工具包"),
    "tlsx": ("TLS certificate fetch / TLS 证书", "TLS 证书信息"),
    "ffuf": ("Web fuzzer / 目录与参数模糊测试", "目录与参数模糊测试"),
    "gau": ("URL collection / URL 收集", "URL 收集"),
    "dalfox": ("XSS scanner / XSS 专项扫描", "XSS 专项扫描"),
    "jq": ("JSON processing / JSON 处理", "JSON 处理"),
    # 克隆类工具
    "PEASS-ng": ("Priv-esc assist / 提权辅助", "提权辅助"),
    "SSTImap": ("SSTI detect & exploit / SSTI 检测利用", "SSTI 检测利用"),
    "SpiderX": ("Frontend JS anti-encryption bypass / 前端加密绕过", "前端 JS 加密绕过"),
    "MemShellParty": ("Java memory-shell injection / Java 内存马注入", "Java 内存马注入"),
    "JYso": ("JNDI + deserialization / JNDI 反序列化", "JNDI 注入 + 反序列化"),
}


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    tools = data.get("tools", {})
    cloned = data.get("cloned_tools", {})
    return tools, cloned


def collect_tools(tools, cloned):
    """返回有序列表: (name, repo, role_en)"""
    items = []
    for name in tools:
        t = tools[name]
        role = ROLE_MAP.get(name, ("", ""))
        items.append((name, t.get("repo", ""), role[0]))
    for name in cloned:
        t = cloned[name]
        role = ROLE_MAP.get(name, ("", ""))
        items.append((name, t.get("repo", ""), role[0]))
    return items


def build_table_en(items):
    lines = [
        "| Tool / 工具 | Role / 用途 | Source / 来源 |",
        "|:---|:---|:---|",
    ]
    for name, repo, role in items:
        source = f"https://github.com/{repo}" if repo else ""
        link = f"[{repo}]({source})" if source else "—"
        lines.append(f"| {name} | {role} | {link} |")
    return "\n".join(lines)


def build_table_zh(items):
    lines = [
        "| 工具 | 用途 | 来源 |",
        "|:---|:---|:---|",
    ]
    for name, repo, _ in items:
        role = ROLE_MAP.get(name, ("", ""))[1]
        source = f"https://github.com/{repo}" if repo else ""
        link = f"[{repo}]({source})" if source else "—"
        lines.append(f"| {name} | {role} | {link} |")
    return "\n".join(lines)


def replace_block(content, block):
    if BEGIN_MARK not in content or END_MARK not in content:
        return None
    head = content.split(BEGIN_MARK)[0]
    tail = content.split(END_MARK)[1]
    return f"{head}{BEGIN_MARK}\n{block}\n{END_MARK}{tail}"


def main():
    parser = argparse.ArgumentParser(description="从 manifest 生成 README 工具清单表格")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    args = parser.parse_args()

    tools, cloned = load_manifest()
    items = collect_tools(tools, cloned)
    if not items:
        print("ERROR: manifest 中未找到任何工具。")
        sys.exit(1)

    table_en = build_table_en(items)
    table_zh = build_table_zh(items)

    changes = []
    for path, block in ((README_EN, table_en), (README_ZH, table_zh)):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        new = replace_block(content, block)
        if new is None:
            print(f"[WARN] {os.path.basename(path)} 缺少标记 {BEGIN_MARK}/{END_MARK}，跳过。")
            print("       请先在工具清单表格处插入这对注释标记。")
            continue
        if new == content:
            print(f"[OK] {os.path.basename(path)} 已是最新（无改动）")
            continue
        if args.dry_run:
            print(f"[DRY-RUN] {os.path.basename(path)} 将更新")
            changes.append(path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"[UPDATED] {os.path.basename(path)}")
            changes.append(path)

    print(f"\n共 {len(items)} 个工具。")
    print("完成。" if not args.dry_run and changes else "（dry-run 或未变更）")


if __name__ == "__main__":
    main()