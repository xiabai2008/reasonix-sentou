# ============================================================
# Reasonix 渗透助手 — check-scope.py 单元测试
# ============================================================
"""
运行方式:
    pip install pytest
    pytest tests/test_check_scope.py -v
"""
import sys
import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# 将 scripts/ 加入 path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

# 直接导入模块
spec = importlib.util.spec_from_file_location(
    "check_scope",
    Path(__file__).parent.parent / "scripts" / "check-scope.py"
)
check_scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_scope)


class TestNormalizeTarget:
    """测试目标类型识别"""

    def test_ipv4(self):
        result = check_scope.normalize_target("192.168.1.1")
        assert result["type"] == "ip"
        assert result["host"] == "192.168.1.1"

    def test_cidr(self):
        result = check_scope.normalize_target("10.0.0.0/8")
        assert result["type"] == "cidr"

    def test_domain(self):
        result = check_scope.normalize_target("example.com")
        assert result["type"] == "domain"
        assert result["host"] == "example.com"

    def test_url_http(self):
        result = check_scope.normalize_target("http://example.com/path")
        assert result["type"] == "url"
        assert result["host"] == "example.com"

    def test_url_https(self):
        result = check_scope.normalize_target("https://sub.example.com:8443/api")
        assert result["type"] == "url"
        assert result["host"] == "sub.example.com"

    def test_ip_with_cidr(self):
        result = check_scope.normalize_target("10.0.0.0/24")
        assert result["type"] == "cidr"


class TestCheckBlocked:
    """测试封禁列表匹配"""

    def test_exact_ip_blocked(self):
        blocked = ["192.168.1.100"]
        assert check_scope.check_blocked("192.168.1.100", blocked) is True

    def test_exact_ip_not_blocked(self):
        blocked = ["192.168.1.100"]
        assert check_scope.check_blocked("192.168.1.200", blocked) is False

    def test_cidr_blocked(self):
        blocked = ["10.0.0.0/8"]
        assert check_scope.check_blocked("10.1.2.3", blocked) is True

    def test_cidr_not_blocked(self):
        blocked = ["10.0.0.0/8"]
        assert check_scope.check_blocked("192.168.1.1", blocked) is False

    def test_wildcard_domain_blocked(self):
        blocked = ["*.example.com"]
        assert check_scope.check_blocked("evil.example.com", blocked) is True

    def test_wildcard_domain_not_blocked(self):
        blocked = ["*.example.com"]
        assert check_scope.check_blocked("other.com", blocked) is False

    def test_empty_blocked_list(self):
        assert check_scope.check_blocked("1.2.3.4", []) is False

    def test_empty_string_in_blocked(self):
        """空字符串应被忽略"""
        blocked = [""]
        assert check_scope.check_blocked("1.2.3.4", blocked) is False


class TestCheckAllowed:
    """测试授权范围匹配"""

    def test_ip_allowed(self):
        scope = {"allowed_ips": ["192.168.1.1"]}
        info = {"host": "192.168.1.1", "type": "ip"}
        assert check_scope.check_allowed(info, scope) is True

    def test_ip_not_allowed(self):
        scope = {"allowed_ips": ["192.168.1.1"]}
        info = {"host": "192.168.1.2", "type": "ip"}
        assert check_scope.check_allowed(info, scope) is False

    def test_cidr_allowed(self):
        scope = {"allowed_cidr": ["10.0.0.0/8"]}
        info = {"host": "10.1.1.1", "type": "ip"}
        assert check_scope.check_allowed(info, scope) is True

    def test_domain_wildcard_allowed(self):
        scope = {"allowed_domains": ["*.example.com"]}
        info = {"host": "api.example.com", "type": "domain"}
        assert check_scope.check_allowed(info, scope) is True

    def test_url_prefix_allowed(self):
        scope = {"allowed_url_prefixes": ["http://example.com/api/"]}
        info = {"host": "example.com", "type": "url", "value": "http://example.com/api/v1/users"}
        assert check_scope.check_allowed(info, scope) is True

    def test_url_prefix_not_allowed(self):
        scope = {"allowed_url_prefixes": ["http://example.com/api/"]}
        info = {"host": "example.com", "type": "url", "value": "http://example.com/admin/"}
        assert check_scope.check_allowed(info, scope) is False

    def test_blocked_but_explicitly_allowed(self):
        """封禁列表中但显式授权 → 应放行"""
        scope = {
            "blocked": ["192.168.1.100"],
            "allowed_ips": ["192.168.1.100"]
        }
        info = {"host": "192.168.1.100", "type": "ip"}
        assert check_scope.check_allowed(info, scope) is True

    def test_none_allowed_ips(self):
        """allowed_ips 为 None 时不崩溃"""
        scope = {"allowed_ips": None, "allowed_cidr": None}
        info = {"host": "192.168.1.1", "type": "ip"}
        assert check_scope.check_allowed(info, scope) is False


class TestCheckTarget:
    """测试完整校验流程"""

    def test_blank_scope_warns(self):
        """未配置任何授权规则时 → 警告但放行"""
        scope = {
            "enforce": False,
            "blocked": [],
            "allowed_cidr": [],
            "allowed_domains": [],
            "allowed_ips": [],
            "allowed_url_prefixes": [],
        }
        allowed, msg = check_scope.check_target("example.com", scope)
        assert allowed is True
        assert "WARN" in msg

    def test_enforce_true_denies_unknown(self):
        """enforce=true 时未授权目标被拒绝"""
        scope = {
            "enforce": True,
            "blocked": [],
            "allowed_cidr": [], "allowed_domains": [],
            "allowed_ips": ["1.2.3.4"],
            "allowed_url_prefixes": [],
        }
        allowed, msg = check_scope.check_target("5.6.7.8", scope)
        assert allowed is False
        assert "DENY" in msg

    def test_blocked_target_denied(self):
        """封禁目标被拒绝"""
        scope = {
            "enforce": False,
            "blocked": ["evil.com"],
            "allowed_cidr": [], "allowed_domains": [],
            "allowed_ips": [], "allowed_url_prefixes": [],
        }
        allowed, msg = check_scope.check_target("evil.com", scope)
        assert allowed is False
        assert "BLOCKED" in msg

    def test_blocked_but_allowed_passes(self):
        """封禁列表但显式授权 → 放行"""
        scope = {
            "enforce": False,
            "blocked": ["10.0.0.0/8"],
            "allowed_cidr": [],
            "allowed_domains": [],
            "allowed_ips": ["10.1.1.1"],
            "allowed_url_prefixes": [],
        }
        allowed, msg = check_scope.check_target("10.1.1.1", scope)
        assert allowed is True


class TestLoadScopeSecurity:
    """P0 修复验证: 解析失败时拒绝所有目标"""

    def test_parse_failure_rejects_all(self):
        """YAML 解析失败时 enforce=true，拒绝所有"""
        # 模拟 parse_scope_simple 抛出异常
        with patch.object(check_scope, "parse_scope_simple", side_effect=Exception("parse error")):
            scope = check_scope.load_scope()
            assert scope["enforce"] is True

    def test_normal_load_reads_scope_config(self):
        """正常加载 scope.yaml 后 enforce 值应由配置文件决定"""
        scope = check_scope.load_scope()
        assert isinstance(scope["enforce"], bool)
        assert "allowed_ips" in scope
        assert "blocked" in scope


class TestParseScopeSimple:
    """测试内置 YAML 解析器"""

    def test_basic_keys(self):
        yaml_content = """enforce: true
allowed_ips:
  - "192.168.1.1"
  - "10.0.0.1"
"""
        with patch("pathlib.Path.read_text", return_value=yaml_content):
            result = check_scope.parse_scope_simple(Path("dummy.yaml"))
            assert result["enforce"] is True
            assert "192.168.1.1" in result["allowed_ips"]
            assert "10.0.0.1" in result["allowed_ips"]
        pass

    def test_list_parsing(self):
        yaml_content = """allowed_domains:
  - "example.com"
  - "*.test.com"
"""
        with patch("pathlib.Path.read_text", return_value=yaml_content):
            result = check_scope.parse_scope_simple(Path("dummy.yaml"))
            assert len(result["allowed_domains"]) == 2
            assert "*.test.com" in result["allowed_domains"]


class TestFindComment:
    """测试引号内注释识别"""

    def test_no_comment(self):
        assert check_scope._find_comment("hello world") == -1

    def test_simple_comment(self):
        assert check_scope._find_comment('value # comment') == 6

    def test_comment_in_double_quotes(self):
        """双引号内的 # 不算注释"""
        assert check_scope._find_comment('"hello # world"') == -1

    def test_comment_in_single_quotes(self):
        """单引号内的 # 不算注释"""
        assert check_scope._find_comment("'hello # world'") == -1

    def test_comment_after_quotes(self):
        """引号外的 # 是注释"""
        # '"hello" # real comment' — # 在第8个位置（0-indexed）
        assert check_scope._find_comment('"hello" # real comment') == 8
