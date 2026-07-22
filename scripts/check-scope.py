#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasonix 授权范围校验工具

用法:
    python scripts/check-scope.py 192.168.1.1
    python scripts/check-scope.py http://example.com
    python scripts/check-scope.py example.com
    python scripts/check-scope.py --file targets.txt

退出码:
    0 = 目标在授权范围内
    1 = 目标不在授权范围内
    2 = 配置错误或参数错误
"""

import argparse
import fnmatch
import ipaddress
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCOPE_FILE = PROJECT_ROOT / "config" / "scope.yaml"


def parse_scope_simple(path: Path) -> dict:
    """不依赖 PyYAML 的简易 YAML 解析（仅支持本文件的简单格式）

    支持的格式:
    - 顶层键值对: key: value  (字符串)
    - 列表项:   - "item"  或  - item
    - 注释:     # 开头
    - 多行字符串: key: | 后跟缩进内容
    - 布尔值:   true / false
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    result = {
        "enforce": False,
        "blocked": [],
        "allowed_cidr": [],
        "allowed_domains": [],
        "allowed_ips": [],
        "allowed_url_prefixes": [],
    }

    # 已知的列表类型键
    list_keys = {"blocked", "allowed_cidr", "allowed_domains", "allowed_ips", "allowed_url_prefixes"}
    current_list_key = None
    in_multiline = False
    multiline_key = None
    multiline_lines = []

    for raw_line in lines:
        # 多行字符串处理（| 块）
        if in_multiline:
            # YAML 多行块: 空行或非缩进行结束块
            if raw_line.strip() == "":
                if multiline_lines:
                    multiline_lines.append("")
                continue
            if not raw_line.startswith(" " * 2) and not raw_line.startswith("\t") and raw_line.strip() != "":
                # 多行块结束，保存结果
                result[multiline_key] = "\n".join(multiline_lines).strip()
                in_multiline = False
                multiline_key = None
                multiline_lines = []
                # 继续处理当前行（不 return，fall through 到下面的逻辑）
            else:
                multiline_lines.append(raw_line.strip())
                continue

        # 去除行尾注释（不在引号内的 #）
        stripped = raw_line.strip()

        # 空行
        if not stripped:
            continue

        # 纯注释行
        if stripped.startswith("#"):
            continue

        # 列表项: 以 "  - " 开头（两个空格缩进的破折号）
        list_match = re.match(r'^\s+-\s+(.+)$', raw_line)
        if list_match and current_list_key:
            value = list_match.group(1).strip()
            # 去除行内注释（不在引号内的 #）
            comment_pos = _find_comment(value)
            if comment_pos >= 0:
                value = value[:comment_pos].strip()
            # 去除引号
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # 跳过纯注释项（如 "  # - comment"）
            if value.startswith("#") or not value:
                continue
            if current_list_key in result and isinstance(result[current_list_key], list):
                result[current_list_key].append(value)
            continue

        # 顶层键值对: key: value
        kv_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$', raw_line)
        if kv_match:
            key = kv_match.group(1)
            raw_value = kv_match.group(2).strip()

            # 如果值是 | ，进入多行模式
            if raw_value == "|":
                in_multiline = True
                multiline_key = key
                multiline_lines = []
                continue

            # 去除行内注释
            comment_pos = _find_comment(raw_value)
            if comment_pos >= 0:
                raw_value = raw_value[:comment_pos].strip()

            # 去除引号
            if (raw_value.startswith('"') and raw_value.endswith('"')) or \
               (raw_value.startswith("'") and raw_value.endswith("'")):
                raw_value = raw_value[1:-1]

            # 布尔值
            if raw_value.lower() == "true":
                raw_value = True
            elif raw_value.lower() == "false":
                raw_value = False
            # 数字
            elif re.match(r'^\d+$', raw_value):
                raw_value = int(raw_value)

            # 判断是否是列表键（值为空，后续行是列表项）
            if raw_value == "" or raw_value is None:
                if key in list_keys:
                    result[key] = []
                    current_list_key = key
                else:
                    current_list_key = None
                    result[key] = raw_value
            else:
                current_list_key = None
                result[key] = raw_value
            continue

        # 未匹配的行，重置当前列表上下文
        if not raw_line.startswith(" "):
            current_list_key = None

    # 处理文件末尾仍在多行模式的情况
    if in_multiline and multiline_key:
        result[multiline_key] = "\n".join(multiline_lines).strip()

    return result


def _find_comment(value: str) -> int:
    """找到不在引号内的 # 注释位置，找不到返回 -1"""
    in_double = False
    in_single = False
    for i, ch in enumerate(value):
        if ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '#' and not in_double and not in_single:
            return i
    return -1


def load_scope() -> dict:
    """加载 scope.yaml"""
    default = {
        "enforce": False,
        "blocked": [],
        "allowed_cidr": [],
        "allowed_domains": [],
        "allowed_ips": [],
        "allowed_url_prefixes": [],
    }

    if not SCOPE_FILE.exists():
        return default

    try:
        if yaml:
            data = yaml.safe_load(SCOPE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # 用默认值填充缺失的键
                for k, v in default.items():
                    data.setdefault(k, v)
                return data
    except Exception:
        pass

    # PyYAML 不可用或解析失败，使用简易解析
    try:
        data = parse_scope_simple(SCOPE_FILE)
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default


def normalize_target(target: str) -> dict:
    """解析目标，返回 {"type": "ip"|"cidr"|"domain"|"url", "value": "...", "host": "..."}"""
    target = target.strip()

    # URL
    if target.startswith("http://") or target.startswith("https://"):
        from urllib.parse import urlparse
        parsed = urlparse(target)
        host = parsed.hostname or parsed.netloc.split(":")[0]
        return {"type": "url", "value": target, "host": host, "scheme": parsed.scheme}

    # CIDR
    if "/" in target:
        try:
            ipaddress.ip_network(target, strict=False)
            return {"type": "cidr", "value": target, "host": target}
        except ValueError:
            pass

    # IP
    try:
        ipaddress.ip_address(target)
        return {"type": "ip", "value": target, "host": target}
    except ValueError:
        pass

    # Domain
    return {"type": "domain", "value": target, "host": target}


def check_blocked(host: str, blocked: list) -> bool:
    """检查是否在封禁列表中"""
    for b in blocked:
        if not b:
            continue
        # 检查 IP/CIDR 封禁
        if "/" in b and not b.startswith("*"):
            try:
                network = ipaddress.ip_network(b, strict=False)
                try:
                    if ipaddress.ip_address(host) in network:
                        return True
                except ValueError:
                    pass
            except ValueError:
                pass
        # 检查域名通配符封禁
        elif "*" in b or b.startswith("."):
            if fnmatch.fnmatch(host, b) or fnmatch.fnmatch("." + host, b):
                return True
        # 精确匹配
        elif host == b:
            return True
    return False


def check_allowed(info: dict, scope: dict) -> bool:
    """检查目标是否在授权范围内"""
    host = info["host"]

    # CIDR 授权
    for cidr in scope.get("allowed_cidr", []) or []:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            try:
                if ipaddress.ip_address(host) in network:
                    return True
            except ValueError:
                pass
        except ValueError:
            pass

    # 精确 IP 授权
    if host in (scope.get("allowed_ips") or []):
        return True

    # 域名授权（通配符匹配）
    for pattern in (scope.get("allowed_domains") or []):
        if fnmatch.fnmatch(host, pattern) or host == pattern.lstrip("*."):
            return True
        if host.endswith("." + pattern.lstrip("*.")):
            return True

    # URL 前缀授权
    if info["type"] == "url":
        for prefix in (scope.get("allowed_url_prefixes") or []):
            if info["value"].startswith(prefix):
                return True

    return False


def check_target(target: str, scope: dict) -> tuple:
    """校验单个目标，返回 (is_allowed, message)"""
    info = normalize_target(target)

    # 检查封禁
    if check_blocked(info["host"], scope.get("blocked", [])):
        # 如果同时在 allowed 中，则放行
        if check_allowed(info, scope):
            return True, f"[ALLOW] {target} 在封禁列表中但已显式授权"
        return False, f"[BLOCKED] {target} 命中封禁规则，拒绝操作"

    # 检查授权
    if check_allowed(info, scope):
        return True, f"[ALLOW] {target} 在授权范围内"

    # 未配置任何授权规则 = 空白授权模式（仅警告）
    has_any_rule = (
        scope.get("allowed_cidr") or scope.get("allowed_domains") or
        scope.get("allowed_ips") or scope.get("allowed_url_prefixes")
    )
    if not has_any_rule:
        return True, f"[WARN] {target} 未配置授权规则（空白授权模式），请尽快配置 scope.yaml"

    enforce = scope.get("enforce", False)
    if enforce:
        return False, f"[DENY] {target} 不在授权范围内（enforce=true）"
    else:
        return True, f"[WARN] {target} 不在授权范围内（enforce=false，仅警告）"


def main():
    parser = argparse.ArgumentParser(
        description="Reasonix 授权范围校验",
        epilog="示例:\n"
               "  python scripts/check-scope.py 192.168.1.1\n"
               "  python scripts/check-scope.py http://example.com\n"
               "  python scripts/check-scope.py --file targets.txt --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", nargs="?", help="目标 (IP/URL/域名/CIDR)")
    parser.add_argument("--file", "-f", help="从文件读取目标列表（每行一个，# 开头为注释）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出结果")
    args = parser.parse_args()

    scope = load_scope()
    targets = []

    if args.file:
        f = Path(args.file)
        if not f.exists():
            print(f"[ERROR] 文件不存在: {f}", file=sys.stderr)
            sys.exit(2)
        targets = f.read_text(encoding="utf-8").strip().splitlines()
    elif args.target:
        targets = [args.target]
    else:
        parser.print_help()
        sys.exit(2)

    all_allowed = True
    results = []

    for target in targets:
        target = target.strip()
        if not target or target.startswith("#"):
            continue
        allowed, msg = check_target(target, scope)
        results.append({"target": target, "allowed": allowed, "message": msg})
        if not allowed:
            all_allowed = False

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(r["message"])
        if not all_allowed:
            print("\n[!] 存在未授权目标。请编辑 config/scope.yaml 添加授权，或将 enforce 设为 false。")

    sys.exit(0 if all_allowed else 1)


if __name__ == "__main__":
    main()