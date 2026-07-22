#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasonix 渗透作战工作台健康检查

用于检查 Reasonix 启动环境、工具包装器、技能索引、敏感输出忽略规则和常见迁移问题。
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class HealthReport:
    def __init__(self) -> None:
        self.ok = 0
        self.warn = 0
        self.fail = 0

    def _line(self, status: str, message: str) -> None:
        print(f"[{status}] {message}")

    def pass_(self, message: str) -> None:
        self.ok += 1
        self._line("OK", message)

    def warning(self, message: str) -> None:
        self.warn += 1
        self._line("WARN", message)

    def error(self, message: str) -> None:
        self.fail += 1
        self._line("FAIL", message)

    def summary(self) -> int:
        print()
        print("=" * 60)
        print(f"健康检查完成: OK={self.ok} WARN={self.warn} FAIL={self.fail}")
        print("=" * 60)
        if self.fail:
            return 2
        if self.warn:
            return 1
        return 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def check_project_structure(report: HealthReport) -> None:
    required = ["AGENTS.md", "reasonix.toml", "README.md", "bin", "config", "scripts", "skills"]
    for item in required:
        path = PROJECT_ROOT / item
        if path.exists():
            report.pass_(f"{item} 已存在")
        else:
            report.error(f"{item} 缺失")


def check_reasonix_config(report: HealthReport) -> None:
    cfg = PROJECT_ROOT / "reasonix.toml"
    if not cfg.exists():
        report.error("reasonix.toml 缺失，无法检查 Reasonix 配置")
        return

    content = read_text(cfg)
    if 'system_prompt_file = "AGENTS.md"' in content:
        report.pass_("reasonix.toml 已指向 AGENTS.md")
    else:
        report.error("reasonix.toml 未正确配置 system_prompt_file = \"AGENTS.md\"")

    if 'mode = "ask"' in content:
        report.pass_("permissions.mode 为 ask")
    else:
        report.warning("permissions.mode 不是 ask，请确认是否允许自动执行危险操作")

    if 'auto_plan = "off"' in content:
        report.pass_("auto_plan 为 off")
    else:
        report.warning("auto_plan 不是 off，高风险操作前请人工确认")


def check_gitignore(report: HealthReport) -> None:
    gitignore = PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        report.error(".gitignore 缺失")
        return

    content = read_text(gitignore)
    required = ["results/", "evidence/", "reports/*.html", "*.pcap", "*.pcapng", "*.har", "*.sqlite"]
    for pattern in required:
        if pattern in content:
            report.pass_(f".gitignore 已忽略 {pattern}")
        else:
            report.warning(f".gitignore 未忽略 {pattern}")


def check_python_dependencies(report: HealthReport) -> None:
    for module in ["requests", "ddddocr"]:
        if importlib.util.find_spec(module):
            report.pass_(f"Python 依赖可用: {module}")
        else:
            report.warning(f"Python 依赖缺失: {module}")


def check_key_tools(report: HealthReport) -> None:
    tools = ["fscan.exe", "naabu.exe", "httpx.exe", "nuclei.exe", "ffuf.exe", "jq.exe"]
    tools_dir = PROJECT_ROOT / "tools"
    for tool in tools:
        if (tools_dir / tool).exists():
            report.pass_(f"关键工具存在: tools/{tool}")
        else:
            report.warning(f"关键工具缺失: tools/{tool}")


def check_skill_index(report: HealthReport) -> None:
    skills_root = PROJECT_ROOT / "skills"
    vuln_hunter = skills_root / "vuln-hunter.md"
    if not vuln_hunter.exists():
        report.error("skills/vuln-hunter.md 缺失")
        return

    skill_dirs = {
        str(path.parent.relative_to(skills_root)).replace("\\", "/")
        for path in (skills_root / "pentest_skills").glob("**/SKILL.md")
    }
    content = read_text(vuln_hunter)
    indexed = set()
    planning_section = False
    reference_section = False
    planning = set()
    references = set()

    for line in content.splitlines():
        if line.startswith("### 规划中技能"):
            planning_section = True
            reference_section = False
            continue
        if line.startswith("### 绕过参考文档"):
            reference_section = True
            planning_section = False
            continue
        if planning_section and line.startswith("### "):
            planning_section = False
        if reference_section and line.startswith("### "):
            reference_section = False
        for part in line.split("`"):
            if part.startswith("pentest_skills/"):
                if planning_section:
                    planning.add(part)
                elif reference_section:
                    references.add(part)
                else:
                    indexed.add(part)

    missing = sorted(ref for ref in indexed if ref not in skill_dirs)
    unindexed = sorted(path for path in skill_dirs if path not in indexed)

    if missing:
        report.warning(f"vuln-hunter.md 引用了 {len(missing)} 个不存在技能: {', '.join(missing[:5])}")
    else:
        report.pass_("vuln-hunter.md 未引用不存在的实际技能")

    important = [
        "pentest_skills/ai-assisted-code-audit",
        "pentest_skills/jwt-privilege-escalation",
        "pentest_skills/dalfox-xss-scanner",
        "pentest_skills/sstimap-exploit",
    ]
    for item in important:
        if item in indexed:
            report.pass_(f"关键技能已进入索引: {item}")
        else:
            report.warning(f"关键技能未进入索引: {item}")

    if unindexed:
        report.warning(f"存在 {len(unindexed)} 个未索引技能: {', '.join(unindexed[:8])}")
    else:
        report.pass_("所有 SKILL.md 目录均已进入 vuln-hunter.md 索引")

    if references:
        report.pass_(f"参考文档已单独标记: {len(references)} 个")

    if planning:
        report.pass_(f"规划中技能已单独标记: {len(planning)} 个")


def check_old_paths(report: HealthReport) -> None:
    patterns = [
        "reasonix渗透助手",
        r"C:\Users\HZR\reasonix_sentou",
        r"D:\tools\Python 3.12.9",
    ]
    globs = ["*.md", "*.py", "*.ps1", "*.cmd", "bin/*", "skills/**/*.md", "scripts/*", "config/*.py"]
    hits: list[tuple[str, str]] = []

    files: set[Path] = set()
    for pattern in globs:
        files.update(PROJECT_ROOT.glob(pattern))

    for path in sorted(files):
        if not path.is_file():
            continue
        if path == Path(__file__).resolve():
            continue
        if path.name == "setup-new-pc.ps1":
            # 迁移脚本会保留旧目录名的正则，用于把历史路径替换成新路径。
            continue
        if "tools" in path.parts or "config/dictionaries" in str(path):
            continue
        text = read_text(path)
        for pat in patterns:
            if pat in text and path.name != "AGENTS.md":
                hits.append((str(path.relative_to(PROJECT_ROOT)), pat))

    if hits:
        sample = "; ".join(f"{path} -> {pat}" for path, pat in hits[:6])
        report.warning(f"发现旧路径或硬编码路径残留: {sample}")
    else:
        report.pass_("未发现需要修复的旧路径残留")


def check_wrappers(report: HealthReport) -> None:
    bin_dir = PROJECT_ROOT / "bin"
    if not bin_dir.exists():
        report.error("bin/ 缺失，无法检查包装器")
        return

    missing_targets: list[str] = []
    checked = 0
    for path in bin_dir.iterdir():
        if not path.is_file() or path.suffix.lower() == ".cmd":
            continue
        text = read_text(path)[:600]
        match = re.search(r'exec "([^"]+)"', text)
        if not match:
            continue
        target = match.group(1)
        if "$" in target:
            continue
        checked += 1
        normalized = target.replace("/c/Tools/reasonix_sentou", str(PROJECT_ROOT)).replace("/", os.sep)
        if not Path(normalized).exists():
            missing_targets.append(f"{path.name} -> {target}")

    if missing_targets:
        report.warning(f"包装器目标不存在: {'; '.join(missing_targets[:8])}")
    else:
        report.pass_(f"已检查 {checked} 个静态 exec 包装器，未发现缺失目标")


def check_tool_versions(report: HealthReport) -> None:
    """检查关键工具版本信息"""
    tools_dir = PROJECT_ROOT / "tools"
    version_cmds = [
        ("fscan.exe", [], b"fscan", None),  # fscan 没有标准 --version，从二进制头部提取
        ("nuclei.exe", ["-version"], b"nuclei", None),
        ("httpx.exe", ["-version"], b"httpx", None),
        ("naabu.exe", ["-version"], b"naabu", None),
        ("subfinder.exe", ["-version"], b"subfinder", None),
        ("ffuf.exe", ["-V"], b"ffuf", None),
        ("jq.exe", ["--version"], b"jq-", None),
    ]

    for bin_name, args, keyword, _ in version_cmds:
        tool_path = tools_dir / bin_name
        if not tool_path.exists():
            continue
        try:
            result = subprocess.run(
                [str(tool_path)] + args,
                capture_output=True,
                timeout=10,
            )
            version_line = ""
            # 尝试从 stdout 或 stderr 获取版本
            for line in (result.stdout + result.stderr).split(b"\n"):
                if keyword in line:
                    version_line = line.decode("utf-8", errors="ignore").strip()
                    break
            if version_line:
                # 截取合理长度
                if len(version_line) > 80:
                    version_line = version_line[:77] + "..."
                report.pass_(f"{bin_name}: {version_line}")
            else:
                report.warning(f"{bin_name}: 无法提取版本信息")
        except (subprocess.TimeoutExpired, OSError) as e:
            report.warning(f"{bin_name}: 版本检测失败 ({e})")


def check_wrapper_consistency(report: HealthReport) -> None:
    """检查 bin/ 下 wrapper 脚本的一致性"""
    bin_dir = PROJECT_ROOT / "bin"
    if not bin_dir.exists():
        report.error("bin/ 缺失，无法检查 wrapper 一致性")
        return

    bash_exec = []    # #!/usr/bin/env bash 或 #!/bin/bash，用 exec 调用
    cmd_wrappers = []  # @echo off，用 wsl 调用
    other_special = []  # 其他/特殊 wrapper（帮助信息、非标准调用）

    for path in bin_dir.iterdir():
        if not path.is_file():
            continue

        text = read_text(path)
        is_cmd = path.suffix.lower() == ".cmd"

        if is_cmd:
            if text.strip().upper().startswith("@ECHO OFF"):
                has_rem = bool(re.search(r'^REM\b', text, re.MULTILINE))
                cmd_wrappers.append((path.name, has_rem))
            else:
                other_special.append((path.name, "非标准 .cmd"))
        else:
            # bash wrapper
            first_line = text.splitlines()[0].strip() if text.splitlines() else ""
            if first_line in ("#!/usr/bin/env bash", "#!/bin/bash"):
                if re.search(r'\bexec\b', text):
                    bash_exec.append((path.name, text))
                else:
                    other_special.append((path.name, "bash 但无 exec（特殊 wrapper）"))
            else:
                other_special.append((path.name, f"非标准 shebang: {first_line[:50]}"))

    # 输出统计
    report.pass_(f"wrapper 总数: {len(bash_exec) + len(cmd_wrappers) + len(other_special)}")
    report.pass_(f"  bash exec wrapper: {len(bash_exec)} 个")
    report.pass_(f"  .cmd wrapper: {len(cmd_wrappers)} 个")
    report.pass_(f"  其他/特殊 wrapper: {len(other_special)} 个")

    # 检查 .cmd 是否有 REM 注释
    cmd_no_rem = [name for name, has_rem in cmd_wrappers if not has_rem]
    if cmd_no_rem:
        report.warning(f"{len(cmd_no_rem)} 个 .cmd wrapper 缺少 REM 注释: {', '.join(cmd_no_rem[:5])}")
    else:
        report.pass_("所有 .cmd wrapper 均有 REM 注释说明")

    # 检查 bash wrapper 的硬编码路径
    hardcoded = []
    for name, text in bash_exec:
        if "/c/Tools/reasonix_sentou" in text:
            hardcoded.append(name)

    if hardcoded:
        report.warning(
            f"{len(hardcoded)} 个 bash wrapper 使用硬编码路径 /c/Tools/reasonix_sentou"
            f"（当前正常工作，迁移时需更新）: {', '.join(hardcoded[:5])}"
        )
    else:
        report.pass_("bash wrapper 未发现硬编码项目路径")

    # 列出特殊 wrapper
    if other_special:
        report.pass_(f"特殊 wrapper: {', '.join(name for name, _ in other_special[:8])}")


def main() -> int:
    print("Reasonix 渗透作战工作台健康检查")
    print(f"项目路径: {PROJECT_ROOT}")
    print("=" * 60)

    report = HealthReport()
    check_project_structure(report)
    check_reasonix_config(report)
    check_gitignore(report)
    check_python_dependencies(report)
    check_key_tools(report)
    check_skill_index(report)
    check_old_paths(report)
    check_wrappers(report)
    check_tool_versions(report)
    check_wrapper_consistency(report)
    return report.summary()


if __name__ == "__main__":
    sys.exit(main())
