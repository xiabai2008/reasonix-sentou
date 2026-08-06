# -*- coding: utf-8 -*-
"""
report_pack — 报告打包模块

落地 evidence/ results/ reports/ 三目录分工, 生成带 [EVID-0NN] 链接的可复核报告。

功能:
    1. 读 manifest.json + 可选 AI 结论文件
    2. 生成可复核报告 (MD / HTML), 每个结论带证据号 + 可复现命令
    3. UNVERIFIED 条目醒目标红 (HTML) / ⚠️ (MD)

用法:
    python scripts/evidence_pack/cli.py report evidence/manifest_<tag>.json --format md
"""

import argparse
import html as html_lib
import json
import sys
from datetime import datetime
from pathlib import Path

from .evidence_harvest import HIGH_SIGNAL_TYPES

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def load_manifest(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"manifest 不存在: {path}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_ai_analysis(path) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"AI 分析文件不存在: {path}")
    return p.read_text(encoding="utf-8")


def render_markdown(manifest: dict, ai_analysis: str) -> str:
    target = manifest.get("target", "")
    task_id = manifest.get("task_id", "TASK")
    ts = manifest.get("created_at", "")
    lines = [
        f"# 渗透测试可复核报告",
        "",
        f"- 目标: {target}",
        f"- 任务标识: {task_id}",
        f"- 时间: {ts}",
        f"- 证据总数: {len(manifest.get('evidence', []))}",
        "",
        "## 发现摘要 (带证据号)",
        "",
    ]
    for ev in manifest.get("evidence", []):
        status = ev.get("status", "UNVERIFIED")
        if status == "VERIFIED":
            lines.append(f"- **{ev['id']}** [{ev.get('type','')}] `{ev['claim']}`")
        else:
            lines.append(f"- > ⚠️ **{ev['id']}** [{ev.get('type','')}] `{ev['claim']}` (UNVERIFIED)")
    lines.append("")
    lines.append("## 验证命令")
    lines.append("")
    for ev in manifest.get("evidence", []):
        if ev.get("source_cmd"):
            lines.append(f"```bash")
            lines.append(f"# {ev['id']}")
            lines.append(ev["source_cmd"])
            lines.append("```")
    lines.append("")
    lines.append("## 证据清单")
    lines.append("")
    lines.append("| EVID | 类型 | 状态 | 结论 | 原始片段 |")
    lines.append("|:-----|:-----|:-----|:-----|:-----|")
    for ev in manifest.get("evidence", []):
        snippet = ev.get("raw_snippet", "")[:80]
        lines.append(
            f"| {ev['id']} | {ev.get('type','')} | {ev.get('status','')} | "
            f"{ev.get('claim','')} | `{snippet}` |"
        )
    lines.append("")
    if ai_analysis:
        lines.append("## AI 分析")
        lines.append("")
        lines.append(ai_analysis)
        lines.append("")
    return "\n".join(lines)


def render_html(manifest: dict, ai_analysis: str) -> str:
    h = html_lib.escape
    target = h(manifest.get("target", ""))
    task_id = h(manifest.get("task_id", "TASK"))
    ts = h(manifest.get("created_at", ""))

    rows = []
    for ev in manifest.get("evidence", []):
        status = ev.get("status", "UNVERIFIED")
        status_html = (
            f'<span class="verified">VERIFIED</span>'
            if status == "VERIFIED"
            else f'<span class="unverified">UNVERIFIED</span>'
        )
        snippet = h(ev.get("raw_snippet", "")[:80])
        rows.append(
            f"<tr><td>{h(ev['id'])}</td><td>{h(ev.get('type',''))}</td>"
            f"<td>{status_html}</td><td><code>{h(ev.get('claim',''))}</code></td>"
            f"<td><code>{snippet}</code></td></tr>"
        )

    ai_html = ""
    if ai_analysis:
        ai_html = f"<h2>AI 分析</h2><pre>{h(ai_analysis)}</pre>"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>渗透测试可复核报告 - {task_id}</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
         max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #1f2937; }}
  h1 {{ border-bottom: 2px solid #d1d5db; padding-bottom: .5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #d1d5db; padding: .5rem; text-align: left; font-size: .9rem; }}
  th {{ background: #f3f4f6; }}
  code {{ background: #f3f4f6; padding: .1rem .3rem; border-radius: 3px; }}
  pre {{ background: #111827; color: #e5e7eb; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
  .verified {{ color: #047857; font-weight: 600; }}
  .unverified {{ color: #b91c1c; font-weight: 700; }}
</style>
</head>
<body>
<h1>渗透测试可复核报告</h1>
<p><strong>目标:</strong> {target} &nbsp;|&nbsp; <strong>任务:</strong> {task_id} &nbsp;|&nbsp; {ts}</p>
<h2>发现摘要</h2>
<table><thead><tr><th>EVID</th><th>类型</th><th>状态</th><th>结论</th><th>原始片段</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
{ai_html}
</body>
</html>"""


def output_report(manifest: dict, fmt: str, ai_analysis: str) -> Path:
    task_id = manifest.get("task_id", "TASK")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if fmt == "html":
        content = render_html(manifest, ai_analysis)
        out = REPORTS_DIR / f"report_{task_id}_{ts}.html"
    else:
        content = render_markdown(manifest, ai_analysis)
        out = REPORTS_DIR / f"report_{task_id}_{ts}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"[+] 报告已生成: {out}")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="报告打包: 生成带 EVID 链接的可复核报告")
    parser.add_argument("manifest", help="manifest.json 路径")
    parser.add_argument("--ai", default=None, help="AI 分析结论文件")
    parser.add_argument("--format", choices=["html", "md"], default="md", help="报告格式 (默认 md)")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        ai_analysis = load_ai_analysis(args.ai)
        output_report(manifest, args.format, ai_analysis)
        return 0
    except FileNotFoundError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())