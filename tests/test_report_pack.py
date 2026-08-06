# ============================================================
# DawnForge 证据包 — report_pack 单元测试
# 可复核报告: 带 EVID 链接, UNVERIFIED 醒目标记
# ============================================================
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evidence_pack import report_pack as rp


def make_manifest(task_id="T01", target="192.168.1.10", evidence=None, ai=""):
    return {
        "task_id": task_id,
        "created_at": "2026-08-06T10:00:00",
        "target": target,
        "evidence": evidence or [],
    }


def make_evidence(eid="EVID-T01-001", etype="flag", status="VERIFIED", claim="flag{x}",
                  source_cmd="nmap -p22", snippet="...flag{x}..."):
    return {"id": eid, "type": etype, "status": status, "claim": claim,
            "source_cmd": source_cmd, "raw_snippet": snippet}


class TestLoadManifest:
    """测试 manifest 读取"""

    def test_load_existing(self, tmp_path):
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps({"task_id": "T01"}), encoding="utf-8")
        assert rp.load_manifest(str(p))["task_id"] == "T01"

    def test_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rp.load_manifest(str(tmp_path / "nope.json"))


class TestLoadAiAnalysis:
    """测试 AI 分析文件读取"""

    def test_none_returns_empty(self):
        assert rp.load_ai_analysis(None) == ""

    def test_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rp.load_ai_analysis(str(tmp_path / "nope.txt"))

    def test_load_content(self, tmp_path):
        p = tmp_path / "ai.txt"
        p.write_text("结论: 存在 SQLi", encoding="utf-8")
        assert rp.load_ai_analysis(str(p)) == "结论: 存在 SQLi"


class TestRenderMarkdown:
    """测试 MD 报告渲染"""

    def test_verified_line_format(self):
        m = make_manifest(evidence=[make_evidence()])
        md = rp.render_markdown(m, "")
        assert "- **EVID-T01-001** [flag] `flag{x}`" in md

    def test_unverified_line_marked(self):
        m = make_manifest(evidence=[make_evidence(status="UNVERIFIED", claim="fake")])
        md = rp.render_markdown(m, "")
        assert "⚠️" in md
        assert "(UNVERIFIED)" in md

    def test_verification_command_blocks(self):
        m = make_manifest(evidence=[make_evidence(source_cmd="nmap -p22 1.2.3.4")])
        md = rp.render_markdown(m, "")
        assert "# EVID-T01-001" in md
        assert "nmap -p22 1.2.3.4" in md

    def test_evidence_table_truncates_snippet(self):
        m = make_manifest(evidence=[make_evidence(snippet="x" * 200)])
        md = rp.render_markdown(m, "")
        assert "x" * 80 in md
        assert "x" * 90 not in md

    def test_ai_analysis_section_only_when_present(self):
        m = make_manifest()
        assert "AI 分析" not in rp.render_markdown(m, "")
        assert "AI 分析" in rp.render_markdown(m, "deep analysis text")

    def test_empty_evidence_still_valid(self):
        md = rp.render_markdown(make_manifest(), "")
        assert "# 渗透测试可复核报告" in md
        assert "证据总数: 0" in md


class TestRenderHtml:
    """测试 HTML 报告渲染"""

    def test_status_classes(self):
        m = make_manifest(evidence=[
            make_evidence(eid="EVID-T01-001", status="VERIFIED"),
            make_evidence(eid="EVID-T01-002", status="UNVERIFIED"),
        ])
        html = rp.render_html(m, "")
        assert '<span class="verified">VERIFIED</span>' in html
        assert '<span class="unverified">UNVERIFIED</span>' in html

    def test_escapes_claim_html(self):
        # 结论中的 HTML 必须转义, 防注入
        m = make_manifest(evidence=[make_evidence(claim='<script>alert(1)</script>')])
        html = rp.render_html(m, "")
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_ai_analysis_escaped(self):
        html = rp.render_html(make_manifest(), "<b>bold</b>")
        assert "<b>bold</b>" not in html
        assert "&lt;b&gt;bold&lt;/b&gt;" in html

    def test_doctype_and_meta(self):
        html = rp.render_html(make_manifest(), "")
        assert "<!DOCTYPE html>" in html
        assert 'charset="utf-8"' in html


class TestOutputReport:
    """测试报告落盘"""

    def test_markdown_output(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rp, "REPORTS_DIR", tmp_path)
        out = rp.output_report(make_manifest(task_id="T01"), "md", "")
        assert out.suffix == ".md"
        assert out.name.startswith("report_T01_")
        assert "可复核报告" in out.read_text(encoding="utf-8")

    def test_html_output(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rp, "REPORTS_DIR", tmp_path)
        out = rp.output_report(make_manifest(task_id="T02"), "html", "")
        assert out.suffix == ".html"
        assert "<!DOCTYPE html>" in out.read_text(encoding="utf-8")

    def test_default_fmt_is_markdown(self, tmp_path, monkeypatch):
        monkeypatch.setattr(rp, "REPORTS_DIR", tmp_path)
        out = rp.output_report(make_manifest(task_id="T03"), "md", "")
        assert out.suffix == ".md"
