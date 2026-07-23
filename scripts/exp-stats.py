#!/usr/bin/env python3
"""
Reasonix 渗透经验统计分析

用法:
    python scripts/exp-stats.py                    # 全量统计
    python scripts/exp-stats.py --tag jwt          # 按标签筛选
    python scripts/exp-stats.py --category sqli    # 按漏洞类型筛选
    python scripts/exp-stats.py --top              # 显示 Top-N
    python scripts/exp-stats.py --json             # JSON 输出

数据来源: memory/experiences-index.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

PROJECT_ROOT = Path(__file__).parent.parent
INDEX_FILE = PROJECT_ROOT / "memory" / "experiences-index.yaml"


def load_yaml(path: Path) -> dict:
    """加载 YAML，兼容 PyYAML 和简易解析"""
    if yaml:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    # PyYAML 不可用: 尝试用 json 兼容模式
    print("[WARN] PyYAML 未安装，统计功能受限。pip install PyYAML", file=sys.stderr)
    return {"experiences": []}


def analyze(experiences: list[dict]) -> dict:
    """统计分析"""
    if not experiences:
        return {"error": "无经验数据"}

    stats = {
        "total": len(experiences),
        "date_range": {
            "first": experiences[0]["date"],
            "last": experiences[-1]["date"],
        },
        "vuln_distribution": Counter(),
        "target_type_distribution": Counter(),
        "tools_most_used": Counter(),
        "skills_most_used": Counter(),
        "tags_distribution": Counter(),
        "waf_encounters": 0,
        "waf_bypasses": 0,
        "avg_cvss": 0.0,
        "avg_tokens": 0,
        "avg_time_min": 0,
        "total_tokens": 0,
        "total_time_min": 0,
        "rating_distribution": Counter(),
        "top_lessons": [],
        "attack_chains": [],
    }

    for exp in experiences:
        # 漏洞类型分布
        stats["vuln_distribution"][exp.get("vuln_category", "unknown")] += 1
        stats["target_type_distribution"][exp.get("target_type", "unknown")] += 1

        # 工具使用频率
        for tool in exp.get("tools_used", []):
            stats["tools_most_used"][tool] += 1
        for skill in exp.get("skills_used", []):
            stats["skills_most_used"][skill] += 1
        for tag in exp.get("tags", []):
            stats["tags_distribution"][tag] += 1

        # WAF 统计
        if exp.get("waf_present"):
            stats["waf_encounters"] += 1
            if exp.get("waf_bypassed"):
                stats["waf_bypasses"] += 1

        # 成本统计
        cvss = exp.get("cvss", 0)
        tokens = exp.get("cost_tokens", 0)
        time_min = exp.get("cost_time_min", 0)
        stats["avg_cvss"] += cvss
        stats["total_tokens"] += tokens
        stats["total_time_min"] += time_min

        # 评分分布
        stats["rating_distribution"][str(exp.get("rating", 0))] += 1

        # 关键教训
        if exp.get("rating", 0) >= 4:
            stats["top_lessons"].append({
                "id": exp["id"],
                "lesson": exp.get("lessons", ""),
                "rating": exp["rating"],
            })

        # 攻击链
        chain = exp.get("attack_chain", [])
        if chain:
            stats["attack_chains"].append({
                "id": exp["id"],
                "vuln": exp.get("vuln_name", ""),
                "chain": " → ".join(chain),
                "impact": exp.get("final_impact", ""),
            })

    n = len(experiences)
    stats["avg_cvss"] = round(stats["avg_cvss"] / n, 1)
    stats["avg_tokens"] = round(stats["total_tokens"] / n)
    stats["avg_time_min"] = round(stats["total_time_min"] / n)

    return stats


def filter_experiences(experiences: list, tag=None, category=None, tool=None) -> list:
    """按条件筛选"""
    result = experiences
    if tag:
        result = [e for e in result if tag in e.get("tags", [])]
    if category:
        result = [e for e in result if e.get("vuln_category") == category]
    if tool:
        result = [e for e in result if tool in e.get("tools_used", [])]
    return result


def print_stats(stats: dict):
    """格式化输出"""
    print("=" * 60)
    print("  Reasonix 渗透经验统计分析")
    print("=" * 60)
    print(f"  总经验数: {stats['total']}")
    print(f"  日期范围: {stats['date_range']['first']} ~ {stats['date_range']['last']}")
    print()

    print("--- 漏洞类型分布 ---")
    for vuln, count in stats["vuln_distribution"].most_common():
        bar = "█" * min(count, 20)
        print(f"  {vuln:12s} {bar} {count}")

    print("\n--- 常用工具 TOP5 ---")
    for tool, count in stats["tools_most_used"].most_common(5):
        print(f"  {tool:15s} {count} 次")

    print("\n--- 常用技能 TOP5 ---")
    for skill, count in stats["skills_most_used"].most_common(5):
        short = skill.replace("pentest_skills/", "").replace("skills/", "")
        print(f"  {short:30s} {count} 次")

    if stats.get("tags_distribution"):
        print("\n--- 标签分布 ---")
        for tag, count in stats["tags_distribution"].most_common(10):
            print(f"  #{tag:20s} {count}")

    print("\n--- 成本统计 ---")
    print(f"  平均 CVSS: {stats['avg_cvss']}")
    print(f"  平均 Token: {stats['avg_tokens']:,}")
    print(f"  平均耗时: {stats['avg_time_min']} 分钟")
    print(f"  累计 Token: {stats['total_tokens']:,}")
    print(f"  累计耗时: {stats['total_time_min']} 分钟 ({stats['total_time_min']//60:.0f} 小时)")

    print("\n--- WAF 对抗 ---")
    waf_rate = stats["waf_bypasses"] / max(stats["waf_encounters"], 1) * 100
    print(f"  遇到 WAF: {stats['waf_encounters']} 次")
    print(f"  成功绕过: {stats['waf_bypasses']} 次")
    print(f"  绕过率: {waf_rate:.0f}%")

    print("\n--- 评分分布 ---")
    for rating, count in sorted(stats["rating_distribution"].items()):
        stars = "★" * int(rating)
        print(f"  {stars:10s} {count} 条")

    if stats.get("top_lessons"):
        print("\n--- 高价值教训 (≥4★) ---")
        for item in stats["top_lessons"][:5]:
            print(f"  [{item['id']}] ★{item['rating']} {item['lesson']}")

    if stats.get("attack_chains"):
        print("\n--- 攻击链记录 ---")
        for item in stats["attack_chains"]:
            print(f"  [{item['id']}] {item['chain']}")
            print(f"       → 最终影响: {item['impact']}")


def main():
    parser = argparse.ArgumentParser(description="Reasonix 渗透经验统计分析")
    parser.add_argument("--tag", help="按标签筛选")
    parser.add_argument("--category", help="按漏洞类型筛选")
    parser.add_argument("--tool", help="按使用的工具筛选")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    data = load_yaml(INDEX_FILE)
    experiences = data.get("experiences", [])

    filtered = filter_experiences(experiences, args.tag, args.category, args.tool)
    stats = analyze(filtered)

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    else:
        print_stats(stats)

    return 0


if __name__ == "__main__":
    sys.exit(main())
