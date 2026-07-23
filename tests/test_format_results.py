# ============================================================
# Reasonix 渗透助手 — format-results.py 单元测试
# ============================================================
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "format_results",
    Path(__file__).parent.parent / "scripts" / "format-results.py"
)
format_results = importlib.util.module_from_spec(spec)
spec.loader.exec_module(format_results)


class TestParseFscan:
    """测试 fscan 输出解析"""

    def test_open_port(self):
        text = "[+] 192.168.1.1:80 open"
        results = format_results.parse_fscan(text)
        assert len(results) == 1
        assert results[0]["type"] == "service"
        assert results[0]["host"] == "192.168.1.1"
        assert results[0]["port"] == 80
        assert "open" in results[0]["banner"]

    def test_mysql_service(self):
        text = "[+] 192.168.1.1:3306 mysql 5.7.32"
        results = format_results.parse_fscan(text)
        assert len(results) == 1
        assert results[0]["type"] == "service"
        assert "mysql" in results[0]["banner"]

    def test_empty_input(self):
        results = format_results.parse_fscan("")
        assert len(results) == 0

    def test_multiple_entries(self):
        text = """[+] 192.168.1.1:80 open
[+] 192.168.1.1:22 ssh
[+] 192.168.1.2:3306 mysql 8.0"""
        results = format_results.parse_fscan(text)
        assert len(results) == 3

    def test_credential_detection(self):
        text = "[+] 192.168.1.1:3306 mysql root:admin123"
        results = format_results.parse_fscan(text)
        assert results[0]["type"] == "credential"
        assert results[0]["username"] == "root"
        assert results[0]["password"] == "admin123"


class TestParseNuclei:
    """测试 nuclei JSON 输出解析"""

    def test_valid_json_line(self):
        text = json.dumps({
            "host": "http://example.com",
            "path": "/admin",
            "template-id": "exposed-panel",
            "info": {"severity": "medium", "name": "Admin Panel Exposed"}
        })
        results = format_results.parse_nuclei_json(text)
        assert len(results) == 1
        assert results[0]["type"] == "vulnerability"
        assert results[0]["severity"] == "medium"

    def test_invalid_json_skipped(self):
        text = "not a json line\n" + json.dumps({"host": "x", "template-id": "y", "info": {}})
        results = format_results.parse_nuclei_json(text)
        assert len(results) == 1  # only the valid line


class TestParseHttpx:
    """测试 httpx JSON 输出解析"""

    def test_valid_httpx_output(self):
        text = json.dumps({
            "url": "http://example.com",
            "status_code": 200,
            "title": "Example",
            "tech": ["nginx", "php"],
            "webserver": "nginx/1.18"
        })
        results = format_results.parse_httpx_json(text)
        assert len(results) == 1
        assert results[0]["status_code"] == 200
        assert "nginx" in results[0]["tech"]


class TestParseSubfinder:
    """测试 subfinder 输出解析"""

    def test_subdomains(self):
        text = "mail.example.com\napi.example.com\nwww.example.com"
        results = format_results.parse_subfinder(text)
        assert len(results) == 3
        assert all(r["type"] == "subdomain" for r in results)

    def test_skip_system_lines(self):
        text = "[INF] Starting subfinder\napi.example.com\n[INF] Finished"
        results = format_results.parse_subfinder(text)
        assert len(results) == 1
        assert results[0]["target"] == "api.example.com"


class TestDetectType:
    """测试工具类型自动检测"""

    def test_fscan_by_filename(self):
        assert format_results.detect_type(Path("fscan_scan.txt")) == "fscan"

    def test_nuclei_by_filename(self):
        assert format_results.detect_type(Path("nuclei_results.json")) == "nuclei"

    def test_httpx_by_filename(self):
        assert format_results.detect_type(Path("httpx_output.txt")) == "httpx"

    def test_naabu_by_filename(self):
        assert format_results.detect_type(Path("naabu_scan.txt")) == "naabu"

    def test_unknown_file(self):
        assert format_results.detect_type(Path("unknown_output.txt")) is None
