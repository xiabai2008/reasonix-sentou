#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasonix 扫描结果格式化工具

将各种工具的原始输出统一转换为 JSON 格式，便于报告生成和 AI 分析。

用法:
    python scripts/format-results.py results/                    # 格式化目录下所有结果
    python scripts/format-results.py results/fscan_*.txt         # 格式化指定文件
    python scripts/format-results.py results/fscan.txt --type fscan
    python scripts/format-results.py results/ --list              # 仅列出可格式化的文件

支持的格式:
    fscan    → JSON（存活IP、端口、服务、凭据、POC）
    nuclei   → JSON（已有 -json 输出时直接归一化）
    httpx    → JSON（URL、状态码、标题、技术栈）
    naabu    → JSON（IP、端口、协议）
    ffuf     → JSON（URL、状态码、大小）
    katana   → JSON（URL、来源）
    subfinder → JSON（子域名）
    nmap     → XML/JSON 解析
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# 每种工具的格式化器签名: (raw_text: str) -> list[dict]
# 返回统一结构: [{"target": "...", "type": "...", "detail": {...}}]

def parse_fscan(text: str) -> list[dict]:
    """解析 fscan 输出"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # fscan 常见格式: [+] 192.168.1.1:80 open
        #               [+] 192.168.1.1:3306 mysql root:123456
        #               [+] 192.168.1.1:445 Microsoft Windows Server 2016
        m = re.match(r'\[\+\]\s+(\S+?):(\d+)\s+(.*)', line)
        if m:
            host, port, info = m.groups()
            entry = {
                "target": f"{host}:{port}",
                "host": host,
                "port": int(port),
                "raw_info": info,
            }
            # 尝试分类
            if re.search(r'root:|admin:|password:|\w+:\w+', info) and 'open' not in info.lower():
                entry["type"] = "credential"
                cred_match = re.search(r'(\w+)\s*:\s*(.+)', info)
                if cred_match:
                    entry["username"] = cred_match.group(1)
                    entry["password"] = cred_match.group(2)
            elif 'POC' in info.upper() or 'vuln' in info.lower():
                entry["type"] = "vulnerability"
            else:
                entry["type"] = "service"
                entry["banner"] = info
            results.append(entry)
    return results

def parse_nuclei_json(text: str) -> list[dict]:
    """解析 nuclei JSON 输出"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            results.append({
                "target": obj.get("host", "") + obj.get("path", ""),
                "type": "vulnerability",
                "template": obj.get("template-id", ""),
                "severity": obj.get("info", {}).get("severity", ""),
                "name": obj.get("info", {}).get("name", ""),
                "detail": obj,
            })
        except json.JSONDecodeError:
            continue
    return results

def parse_httpx_json(text: str) -> list[dict]:
    """解析 httpx JSON 输出"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            results.append({
                "target": obj.get("url", ""),
                "type": "web_service",
                "status_code": obj.get("status_code"),
                "title": obj.get("title", ""),
                "tech": obj.get("tech", []),
                "webserver": obj.get("webserver", ""),
                "detail": obj,
            })
        except json.JSONDecodeError:
            continue
    return results

def parse_naabu(text: str) -> list[dict]:
    """解析 naabu 文本输出"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("["):
            continue
        parts = line.split()
        if len(parts) >= 2:
            results.append({
                "target": line,
                "host": parts[0],
                "port": int(parts[1]),
                "type": "open_port",
            })
    return results

def parse_subfinder(text: str) -> list[dict]:
    """解析 subfinder 输出（每行一个子域名）"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("["):
            results.append({
                "target": line,
                "type": "subdomain",
            })
    return results

def parse_katana(text: str) -> list[dict]:
    """解析 katana 输出（每行一个 URL）"""
    results = []
    for line in text.splitlines():
        line = line.strip()
        if line and (line.startswith("http://") or line.startswith("https://")):
            results.append({
                "target": line,
                "type": "url",
            })
    return results

def detect_type(filepath: Path) -> str | None:
    """根据文件名和内容自动检测工具类型"""
    name = filepath.name.lower()

    if "fscan" in name:
        return "fscan"
    if "nuclei" in name:
        return "nuclei"
    if "httpx" in name:
        return "httpx"
    if "naabu" in name:
        return "naabu"
    if "subfinder" in name:
        return "subfinder"
    if "katana" in name:
        return "katana"
    if "ffuf" in name:
        return "ffuf"

    # 尝试从内容判断
    try:
        sample = filepath.read_text(encoding="utf-8", errors="ignore")[:500]
        if '"template-id"' in sample:
            return "nuclei"
        if '"status_code"' in sample:
            return "httpx"
        if re.search(r'\[\+\]\s+\d+\.\d+\.\d+\.\d+:\d+', sample):
            return "fscan"
    except Exception:
        pass

    return None

PARSERS = {
    "fscan": parse_fscan,
    "nuclei": parse_nuclei_json,
    "httpx": parse_httpx_json,
    "naabu": parse_naabu,
    "subfinder": parse_subfinder,
    "katana": parse_katana,
}

def format_file(filepath: Path, forced_type: str | None = None) -> dict:
    """格式化单个文件"""
    tool_type = forced_type or detect_type(filepath)
    if not tool_type or tool_type not in PARSERS:
        return {"file": str(filepath), "error": f"无法识别工具类型", "results": []}

    text = filepath.read_text(encoding="utf-8", errors="ignore")
    parsed = PARSERS[tool_type](text)

    return {
        "file": str(filepath),
        "tool": tool_type,
        "timestamp": datetime.now().isoformat(),
        "total_findings": len(parsed),
        "results": parsed,
    }

def main():
    parser = argparse.ArgumentParser(description="Reasonix 扫描结果格式化工具")
    parser.add_argument("paths", nargs="+", help="文件或目录路径")
    parser.add_argument("--type", "-t", help="强制指定工具类型")
    parser.add_argument("--list", action="store_true", help="仅列出可格式化的文件")
    parser.add_argument("--output", "-o", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    # 收集文件
    files = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            files.extend(f for f in path.iterdir() if f.is_file())
        elif path.exists():
            files.append(path)

    if args.list:
        for f in sorted(files):
            t = detect_type(f)
            status = t if t else "unknown"
            print(f"  {status:12s} {f.name}")
        print(f"\n共 {len(files)} 个文件")
        return

    all_results = []
    for f in sorted(files):
        result = format_file(f, args.type)
        all_results.append(result)

    output_json = {
        "project": "reasonix_sentou",
        "generated": datetime.now().isoformat(),
        "files_processed": len(all_results),
        "total_findings": sum(r.get("total_findings", 0) for r in all_results),
        "results": all_results,
    }

    json_str = json.dumps(output_json, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"已写入 {args.output}")
    else:
        print(json_str)

if __name__ == "__main__":
    main()
