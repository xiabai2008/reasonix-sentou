# -*- coding: utf-8 -*-
"""
evidence_harvest — 证据采集模块

对标 VulnClaw 的核心反幻觉机制: 将"证据必须逐字符出现在真实工具输出"落地为代码强制。

功能:
    1. 从 stdin 读取工具原始输出
    2. 对调用方声明的每条结论 (--claim) 分配 EVID 编号
    3. 逐字符归属校验: 结论必须作为原始输出的子串出现, 否则标记 [UNVERIFIED]
    4. 产出 evidence/manifest_<tag>.json

用法:
    echo "output" | python scripts/evidence_pack/cli.py harvest --tag T01 --target localhost --claim "admin/admin123"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = PROJECT_ROOT / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

# 高信号证据类型 (与 memory_archive 共享)
HIGH_SIGNAL_TYPES = {"flag", "credential", "vuln_alert", "chain", "critical_config"}


def normalize(text: str) -> str:
    """去除空白后归一化, 用于逐字符匹配"""
    return re.sub(r"\s+", "", text)


def normalize_claim_text(text: str) -> str:
    """去掉方括号状态标记, 提取纯结论文本用于匹配"""
    # 形如 "admin/admin123" 或 "[VERIFIED] admin/admin123"
    return re.sub(r"^\[(VERIFIED|UNVERIFIED)\]\s*", "", text).strip()


def verify_claim(claim: str, raw_output: str) -> bool:
    """逐字符归属校验: 结论去空白后必须是原始输出去空白后的子串"""
    return normalize(claim) in normalize(raw_output)


def assign_evidence(tag: str, index: int) -> str:
    """生成 EVID 编号: EVID-<tag>-<NNN>"""
    return f"EVID-{tag}-{index:03d}"


def parse_claims(arg_claims, claim_file) -> list:
    """收集所有声明的结论"""
    claims = list(arg_claims or [])
    if claim_file:
        p = Path(claim_file)
        if not p.exists():
            raise FileNotFoundError(f"断言文件不存在: {claim_file}")
        with open(p, encoding="utf-8") as f:
            claims.extend([line.strip() for line in f if line.strip()])
    return claims


def harvest(raw_output: str, tag: str, claims: list, target: str = "",
            source_cmd: str = "", verify: bool = True,
            allow_unverified: bool = False) -> dict:
    """核心采集逻辑, 返回 manifest dict"""
    created_at = datetime.now().isoformat(timespec="seconds")
    evidence_list = []
    verified_n = 0
    unverified_n = 0

    for i, raw_claim in enumerate(claims, start=1):
        claim_text = normalize_claim_text(raw_claim)
        evid_id = assign_evidence(tag, i)

        # 判断类型: 简单启发式
        lower = claim_text.lower()
        if "flag{" in lower or claim_text.startswith("flag{") or "flag{" in claim_text:
            etype = "flag"
        elif any(k in lower for k in ("pass", "password", "token", "cred", "user:", "口令", "凭证", "pwd", "account")):
            etype = "credential"
        elif "/" in claim_text and claim_text.count("/") == 1:  # 账号/密码 对格式
            etype = "credential"
        elif "://" not in claim_text and re.search(r":[^:]+:[^:]+", claim_text):  # 服务:账号:密码
            etype = "credential"
        elif any(k in lower for k in ("注入", "sqli", "xss", "rce", "vuln", "漏洞", "exec", "bypass")):
            etype = "vuln_alert"
        else:
            etype = "evidence"

        # 校验
        if verify:
            ok = verify_claim(claim_text, raw_output)
        else:
            ok = True  # --no-verify 调试模式跳过校验

        status = "VERIFIED" if ok else "UNVERIFIED"
        if ok:
            verified_n += 1
        else:
            unverified_n += 1

        # 原始片段: 在 raw_output 中定位并截取
        snippet = ""
        if ok:
            idx = raw_output.find(claim_text)
            if idx >= 0:
                snippet = raw_output[max(0, idx - 40): idx + len(claim_text) + 40]

        evidence_list.append({
            "id": evid_id,
            "type": etype,
            "source_cmd": source_cmd,
            "claim": claim_text,
            "status": status,
            "raw_snippet": snippet,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })

    manifest = {
        "task_id": tag,
        "created_at": created_at,
        "target": target,
        "source_cmd": source_cmd,
        "verify_enabled": verify,
        "allow_unverified": allow_unverified,
        "evidence": evidence_list,
    }

    # 汇总统计
    print(f"[*] 校验结果: {verified_n} verified / {unverified_n} unverified")

    # 若存在 unverified 且未放行, 记录警告 (不阻断, 由 report 层决定是否显示)
    if unverified_n > 0 and not allow_unverified:
        print(f"[!] 存在 {unverified_n} 条 UNVERIFIED 证据, 默认不进报告 (可用 --allow-unverified 放行)")

    return manifest


def write_manifest(tag: str, manifest: dict) -> Path:
    out = EVIDENCE_DIR / f"manifest_{tag}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[+] 证据清单已写入: {out}")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="证据采集: 分配 EVID 编号 + 逐字符归属校验")
    parser.add_argument("--tag", required=True, help="任务标识 (用于证据号前缀)")
    parser.add_argument("--target", default="", help="目标")
    parser.add_argument("--claim", action="append", default=[], help="结论 (可多次传入)")
    parser.add_argument("--claim-file", default=None, help="结论文件 (每行一个)")
    parser.add_argument("--source-cmd", default="", help="来源命令")
    parser.add_argument("--no-verify", action="store_true", help="跳过校验 (仅调试)")
    parser.add_argument("--allow-unverified", action="store_true", help="放行 UNVERIFIED 证据")
    args = parser.parse_args(argv)

    # 从 stdin 读取原始输出
    raw_output = sys.stdin.read()

    claims = parse_claims(args.claim, args.claim_file)
    if not claims:
        print("[!] 未提供任何结论 (--claim 或 --claim-file)", file=sys.stderr)
        return 1
    if not raw_output.strip():
        print("[!] stdin 无原始输出", file=sys.stderr)
        return 1

    manifest = harvest(
        raw_output=raw_output,
        tag=args.tag,
        claims=claims,
        target=args.target,
        source_cmd=args.source_cmd,
        verify=not args.no_verify,
        allow_unverified=args.allow_unverified,
    )
    write_manifest(args.tag, manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())