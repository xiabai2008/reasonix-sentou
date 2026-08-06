#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup-agent-links — 多 Agent 通用化：把技能/配置链接到各家 Agent 约定目录

让同一份 skills/ 素材服务 Claude Code / Codex / OpenCode / Cline / Trae，
避免复制粘贴导致的分叉。支持软链（默认）与复制两种模式。
Trae 为特例：自动读取根 AGENTS.md 进入角色、技能按需 Read，无需软链。

用法:
    python scripts/setup-agent-links.py            # 预览将创建哪些链接
    python scripts/setup-agent-links.py --apply    # 实际创建链接
    python scripts/setup-agent-links.py --mode copy  # 用复制代替软链
    python scripts/setup-agent-links.py --clean      # 清理已创建的链接
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_SRC = PROJECT_ROOT / "skills" / "pentest_skills"
CONFIG_SRC = PROJECT_ROOT / "templates" / "agent-configs"

# 各家 Agent 的 skills 约定目录（相对项目根）
AGENT_TARGETS = {
    "claude": {
        "skills_dir": Path(".claude/skills"),
        "config": "CLAUDE.md",
        "settings": Path(".claude/settings.example.json"),
    },
    "codex": {
        "skills_dir": Path(".codex/skills"),
        "config": "AGENTS.md",  # Codex 原生读取根 AGENTS.md
        "settings": Path("codex.json.example"),
    },
    "opencode": {
        "skills_dir": Path(".opencode/skill"),
        "config": "AGENTS.md",
        "settings": Path("opencode.json.example"),
    },
    "cline": {
        "skills_dir": Path(".cline/skills"),
        "config": "CLAUDE.md",
    },
    "cursor": {
        "skills_dir": Path(".cursor/skills"),
        "config": "AGENTS.md",
    },
    "trae": {
        # Trae 特例：无需软链技能。Trae 会自动把根目录 AGENTS.md/CLAUDE.md
        # 读取为工作区规则进入渗透专家角色，技能通过 Read 按需加载。
        # skills_dir 仅作为可选约定位置，供需要时参考，不强制创建。
        "skills_dir": Path(".trae/skills"),
        "config": "AGENTS.md",
        "no_link": True,  # 标记：Trae 技能按需读取，跳过实际软链
    },
}


def _link_one(src: Path, dst: Path, mode: str) -> str:
    """创建单个软链或复制，返回状态描述"""
    if dst.exists() or dst.is_symlink():
        return f"skip(exists): {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if mode == "copy":
        if dst.is_dir() or src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return f"copy: {dst}"
    try:
        os.symlink(src, dst, target_is_directory=src.is_dir())
        return f"link: {dst} -> {src}"
    except (OSError, NotImplementedError) as e:
        # Windows 无权限/不支持软链时回退复制
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return f"link-fallback-copy: {dst} ({e})"


def main():
    ap = argparse.ArgumentParser(description="Multi-agent skill linking")
    ap.add_argument("--apply", action="store_true", help="实际创建链接（默认仅预览）")
    ap.add_argument("--mode", choices=["link", "copy"], default="link",
                    help="创建方式：link=软链(默认) copy=复制")
    ap.add_argument("--clean", action="store_true", help="清理已创建的链接/复制品")
    ap.add_argument("--agents", nargs="*", default=list(AGENT_TARGETS),
                    help="指定目标 agent，默认全部")
    args = ap.parse_args()

    if not SKILLS_SRC.exists():
        print(f"[!] 技能源目录不存在: {SKILLS_SRC}")
        sys.exit(1)

    reports = {name: [] for name in args.agents}

    for name in args.agents:
        spec = AGENT_TARGETS.get(name)
        if not spec:
            print(f"[!] 未知 agent: {name}")
            continue
        skills_dst = PROJECT_ROOT / spec["skills_dir"]
        if args.clean:
            if skills_dst.exists():
                shutil.rmtree(skills_dst, ignore_errors=True)
                reports[name].append(f"removed: {skills_dst}")
            continue
        if not args.apply:
            # Trae 特例：无需软链，仅预览提示即可
            if spec.get("no_link"):
                reports[name].append("(no-link) Trae 通过 AGENTS.md 自动进入角色，技能按需 Read，无需软链")
                continue
            reports[name].append(f"would create skills -> {skills_dst}")
            continue
        # Trae 特例：跳过实际创建
        if spec.get("no_link"):
            reports[name].append("(no-link) Trae 无需软链技能，已跳过")
            continue
        # 逐技能链接
        for skill in sorted(SKILLS_SRC.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").exists():
                reports[name].append(_link_one(skill, skills_dst / skill.name, args.mode))
        # 链接配置模板
        if "settings" in spec and spec["settings"] and CONFIG_SRC.exists():
            cfg = CONFIG_SRC / spec["settings"].name
            if cfg.exists():
                reports[name].append(_link_one(cfg, cfg, args.mode))

    # 输出
    for name, lines in reports.items():
        print(f"\n== {name} ==")
        for line in lines:
            print("  " + line)
    if not args.apply and not args.clean:
        print("\n[提示] 以上为预览。加 --apply 实际创建，--mode copy 用复制，--clean 清理。")


if __name__ == "__main__":
    main()