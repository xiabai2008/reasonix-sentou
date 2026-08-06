# -*- coding: utf-8 -*-
"""
memory_archive — 记忆归档模块

解决"冷热记忆治理": 区分高信号证据与普通噪音, 将高信号证据去重沉淀到经验/攻击链。

功能:
    1. 读 manifest.json, 识别高信号证据 (type ∈ HIGH_SIGNAL_TYPES)
    2. 与 memory/ 下已有经验文件去重 (按 EVID 编号)
    3. 新高信号证据沉淀到 memory/pentest-experience-0XX.md
    4. chain 类型并入 memory/attack-chains.yaml
    5. 普通噪音不落记忆

用法:
    python scripts/evidence_pack/cli.py archive evidence/manifest_<tag>.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from .evidence_harvest import HIGH_SIGNAL_TYPES  # 复用高信号类型定义

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
MEMORY_DIR.mkdir(exist_ok=True)
ATTACK_CHAINS_FILE = MEMORY_DIR / "attack-chains.yaml"


def load_manifest(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"manifest 不存在: {path}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def list_experience_files() -> list:
    """返回已存在的经验文件 (按序号排序)"""
    files = sorted(MEMORY_DIR.glob("pentest-experience-*.md"))
    return files


def next_experience_number() -> int:
    """返回下一个经验文件序号"""
    nums = []
    for f in list_experience_files():
        m = re.search(r"pentest-experience-(\d+)\.md", f.name)
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def collect_existing_evid_ids() -> set:
    """收集 memory/ 下所有已出现的 EVID 编号, 用于去重"""
    ids = set()
    pattern = re.compile(r"EVID-[\w-]+-\d{3}")
    for f in MEMORY_DIR.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        ids.update(pattern.findall(text))
    return ids


def filter_high_signal(manifest: dict) -> list:
    """筛选高信号且 VERIFIED 的证据"""
    result = []
    for ev in manifest.get("evidence", []):
        if ev.get("type") in HIGH_SIGNAL_TYPES and ev.get("status") == "VERIFIED":
            result.append(ev)
    return result


def write_experience_file(manifest: dict, new_evidence: list) -> Path:
    """写入新的经验文件 pentest-experience-0XX.md"""
    num = next_experience_number()
    path = MEMORY_DIR / f"pentest-experience-{num:03d}.md"

    target = manifest.get("target", "")
    task_id = manifest.get("task_id", "TASK")
    ts = manifest.get("created_at", datetime.now().isoformat(timespec="seconds"))

    lines = [
        f"# pentest-experience-{num:03d}",
        "",
        "## 目标概况",
        "",
        f"- 目标: {target}",
        f"- 任务标识: {task_id}",
        f"- 归档时间: {ts}",
        f"- 来源: evidence_pack (evidence_harvest 自动沉淀)",
        "",
        "## 高信号证据 (VERIFIED)",
        "",
        "| EVID | 类型 | 结论 | 来源命令 |",
        "|:-----|:-----|:-----|:-----|",
    ]
    for ev in new_evidence:
        lines.append(
            f"| {ev['id']} | {ev['type']} | {ev['claim']} | {ev.get('source_cmd','')} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] 经验沉淀: {path.name} ({len(new_evidence)} 条高信号证据)")
    return path


def append_attack_chains(manifest: dict) -> None:
    """将 chain 类型且 VERIFIED 的证据并入 attack-chains.yaml"""
    chain_evs = [
        e for e in manifest.get("evidence", [])
        if e.get("type") == "chain" and e.get("status") == "VERIFIED"
    ]
    if not chain_evs:
        return

    # 读取现有内容
    existing = ""
    if ATTACK_CHAINS_FILE.exists():
        existing = ATTACK_CHAINS_FILE.read_text(encoding="utf-8")

    ATTACK_CHAINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ATTACK_CHAINS_FILE, "a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        for ev in chain_evs:
            f.write(f"  - id: CHAIN-{manifest.get('task_id','TASK')}\n")
            f.write(f"    summary: \"{ev['claim']}\"\n")
            f.write(f"    evidence: \"{ev['id']}\"\n")
            f.write(f"    target: \"{manifest.get('target','')}\"\n")
    print(f"[+] 攻击链条目并入: {ATTACK_CHAINS_FILE.name} ({len(chain_evs)} 条)")


def archive(manifest_path: str, no_dedup: bool = False) -> int:
    manifest = load_manifest(manifest_path)
    new_evidence = filter_high_signal(manifest)

    if not new_evidence:
        print("[*] 无高信号 VERIFIED 证据, 不沉淀 (避免噪音污染记忆)")
        return 0

    # 去重
    if no_dedup:
        final_evidence = new_evidence
    else:
        existing_ids = collect_existing_evid_ids()
        final_evidence = [e for e in new_evidence if e["id"] not in existing_ids]
        if len(final_evidence) < len(new_evidence):
            print(f"[*] 去重: 跳过 {len(new_evidence) - len(final_evidence)} 条已存在证据")

    if not final_evidence:
        print("[*] 全部证据已存在, 无新增")
        return 0

    write_experience_file(manifest, final_evidence)
    append_attack_chains(manifest)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="记忆归档: 高信号证据去重沉淀到经验/攻击链")
    parser.add_argument("manifest", help="manifest.json 路径")
    parser.add_argument("--no-dedup", action="store_true", help="跳过去重")
    args = parser.parse_args(argv)
    try:
        return archive(args.manifest, no_dedup=args.no_dedup)
    except FileNotFoundError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())