#!/usr/bin/env python3
"""
经验索引追加工具 — 破晓打完靶场后自动调用

用法:
    python scripts/exp-add.py memory/pentest-experience-013.md
    python scripts/exp-add.py --id EXP-013 --target "DVWA" --category xss --cvss 6.1 --tools curl,sed --skills xss-cross-site-scripting --tags dvwa,xss --impact "XSS反射执行" --lesson "无过滤直接注入"

数据来源:
    - 从 .md 文件名推断 ID
    - 其他字段通过命令行参数传入
    - 自动追加到 memory/experiences-index.yaml
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
INDEX_FILE = PROJECT_ROOT / "memory" / "experiences-index.yaml"


def parse_md_id(filepath: str) -> str | None:
    """从文件名提取 ID, 如 pentest-experience-013.md → EXP-013"""
    match = re.search(r'pentest-experience-(\d+)', str(filepath))
    if match:
        return f"EXP-{match.group(1)}"
    return None


def add_experience(entry: dict):
    """追加一条经验到索引文件"""
    index = INDEX_FILE.read_text(encoding="utf-8")

    # 构建 YAML 条目
    yaml_entry = f"""  - id: {entry['id']}
    date: "{entry['date']}"
    target: "{entry['target']}"
    target_type: {entry.get('target_type', 'url')}
    target_tech: [{', '.join(entry.get('target_tech', []))}]
    vuln_category: {entry.get('vuln_category', 'unknown')}
    vuln_name: "{entry.get('vuln_name', '')}"
    cvss: {entry.get('cvss', 0)}
    tools_used: [{', '.join(entry.get('tools_used', []))}]
    skills_used: [{', '.join(entry.get('skills_used', []))}]
    waf_present: {str(entry.get('waf_present', False)).lower()}
    waf_bypassed: {str(entry.get('waf_bypassed', False)).lower()}
    attack_chain:
{chr(10).join(f'      - "{step}"' for step in entry.get('attack_chain', []))}
    final_impact: "{entry.get('final_impact', '')}"
    lessons: "{entry.get('lessons', '')}"
    failed_attempts:
{chr(10).join(f'      - "{fa}"' for fa in entry.get('failed_attempts', []))}
    cost_tokens: {entry.get('cost_tokens', 0)}
    cost_time_min: {entry.get('cost_time_min', 0)}
    rating: {entry.get('rating', 3)}
    tags: [{', '.join(entry.get('tags', []))}]
"""

    # 追加到索引文件末尾
    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(yaml_entry)

    print(f"[+] {entry['id']} 已追加到 memory/experiences-index.yaml")


def main():
    parser = argparse.ArgumentParser(
        description="经验索引追加 — 破晓专用",
        epilog="示例: python scripts/exp-add.py --id EXP-013 --target DVWA --category xss --cvss 6.1 --tools curl --skills xss-cross-site-scripting --tags dvwa,xss --impact 'XSS执行' --lesson '无过滤'"
    )
    parser.add_argument("md_file", nargs="?", help="经验 .md 文件路径 (自动提取 ID)")
    parser.add_argument("--id", help="经验 ID (如 EXP-013)")
    parser.add_argument("--target", default="unknown", help="目标名称")
    parser.add_argument("--target-type", default="url", help="目标类型")
    parser.add_argument("--tech", default="", help="技术栈,逗号分隔")
    parser.add_argument("--category", default="unknown", help="漏洞类型")
    parser.add_argument("--name", default="", help="漏洞名称")
    parser.add_argument("--cvss", type=float, default=5.0, help="CVSS 评分")
    parser.add_argument("--tools", default="", help="使用的工具,逗号分隔")
    parser.add_argument("--skills", default="", help="使用的技能,逗号分隔")
    parser.add_argument("--waf", action="store_true", help="是否遇到 WAF")
    parser.add_argument("--waf-bypass", action="store_true", help="是否绕过 WAF")
    parser.add_argument("--chain", default="", help="攻击链步骤,分号分隔")
    parser.add_argument("--impact", default="", help="最终影响")
    parser.add_argument("--lesson", default="", help="经验教训")
    parser.add_argument("--failed", default="", help="失败尝试,分号分隔")
    parser.add_argument("--tokens", type=int, default=0, help="消耗 Token 数")
    parser.add_argument("--time", type=int, default=0, help="耗时(分钟)")
    parser.add_argument("--rating", type=int, default=3, help="评分 1-5")
    parser.add_argument("--tags", default="", help="标签,逗号分隔")

    args = parser.parse_args()

    # 确定 ID
    exp_id = args.id
    if not exp_id and args.md_file:
        exp_id = parse_md_id(args.md_file)
    if not exp_id:
        print("[!] 需要 --id 参数或提供 .md 文件路径", file=sys.stderr)
        sys.exit(1)

    # 构建条目
    entry = {
        "id": exp_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "target": args.target,
        "target_type": args.target_type,
        "target_tech": [t.strip() for t in args.tech.split(",") if t.strip()],
        "vuln_category": args.category,
        "vuln_name": args.name,
        "cvss": args.cvss,
        "tools_used": [t.strip() for t in args.tools.split(",") if t.strip()],
        "skills_used": [s.strip() for s in args.skills.split(",") if s.strip()],
        "waf_present": args.waf,
        "waf_bypassed": args.waf_bypass,
        "attack_chain": [c.strip() for c in args.chain.split(";") if c.strip()],
        "final_impact": args.impact,
        "lessons": args.lesson,
        "failed_attempts": [f.strip() for f in args.failed.split(";") if f.strip()],
        "cost_tokens": args.tokens,
        "cost_time_min": args.time,
        "rating": args.rating,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    }

    add_experience(entry)


if __name__ == "__main__":
    main()
