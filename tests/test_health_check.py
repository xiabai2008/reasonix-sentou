# ============================================================
# Reasonix 渗透助手 — health-check.py 单元测试
# ============================================================
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "health_check",
    Path(__file__).parent.parent / "scripts" / "health-check.py"
)
health_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_check)


class TestHealthReport:
    """测试健康报告类"""

    def test_initial_state(self):
        report = health_check.HealthReport()
        assert report.ok == 0
        assert report.warn == 0
        assert report.fail == 0

    def test_pass_increments(self):
        report = health_check.HealthReport()
        report.pass_("test")
        assert report.ok == 1
        assert report.warn == 0
        assert report.fail == 0

    def test_warning_increments(self):
        report = health_check.HealthReport()
        report.warning("test")
        assert report.ok == 0
        assert report.warn == 1
        assert report.fail == 0

    def test_error_increments(self):
        report = health_check.HealthReport()
        report.error("test")
        assert report.ok == 0
        assert report.warn == 0
        assert report.fail == 1

    def test_mixed_counts(self):
        report = health_check.HealthReport()
        report.pass_("a")
        report.pass_("b")
        report.warning("c")
        report.error("d")
        report.error("e")
        assert report.ok == 2
        assert report.warn == 1
        assert report.fail == 2

    def test_summary_with_failures(self):
        """有失败时返回退出码 2"""
        report = health_check.HealthReport()
        report.fail = 1
        assert report.summary() == 2

    def test_summary_with_warnings(self):
        """有警告无失败时返回退出码 1"""
        report = health_check.HealthReport()
        report.warn = 1
        assert report.summary() == 1

    def test_summary_all_ok(self):
        """全部通过时返回退出码 0"""
        report = health_check.HealthReport()
        report.ok = 10
        assert report.summary() == 0


class TestReadText:
    """测试 read_text 辅助函数"""

    def test_read_utf8(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")
        assert health_check.read_text(f) == "hello"

    def test_read_with_errors(self, tmp_path):
        """带编码错误时不抛异常"""
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\xff\xfe\x00\x01")
        result = health_check.read_text(f)
        assert isinstance(result, str)
