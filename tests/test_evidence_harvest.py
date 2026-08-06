# ============================================================
# DawnForge 证据包 — evidence_harvest 单元测试
# 反幻觉核心: 逐字符归属校验 (normalize + 子串匹配)
# ============================================================
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evidence_pack import evidence_harvest as eh


class TestNormalize:
    """测试空白归一化"""

    def test_removes_all_whitespace(self):
        assert eh.normalize("admin / admin123") == "admin/admin123"

    def test_removes_newlines_and_tabs(self):
        assert eh.normalize("flag{\n\tsecret\n}") == "flag{secret}"


class TestNormalizeClaimText:
    """测试状态前缀剥离"""

    def test_plain_claim(self):
        assert eh.normalize_claim_text("admin/admin123") == "admin/admin123"

    def test_strips_verified_prefix(self):
        assert eh.normalize_claim_text("[VERIFIED] admin/admin123") == "admin/admin123"

    def test_strips_unverified_prefix(self):
        assert eh.normalize_claim_text("[UNVERIFIED] SQLi") == "SQLi"


class TestVerifyClaim:
    """测试逐字符归属校验"""

    def test_exact_substring_verified(self):
        assert eh.verify_claim("admin/admin123", "Nmap 输出 ... admin/admin123 ...")

    def test_whitespace_folded_match(self):
        # 结论跨行出现也能匹配 (归一化后为子串)
        raw = "[+] mysql root:admin123\n[+] mysql root:admin123\n"
        assert eh.verify_claim("root:\nadmin123", raw)

    def test_missing_claim_unverified(self):
        assert not eh.verify_claim("flag{secret}", "no flag here")

    def test_partial_match_fails(self):
        # 只匹配一半不算证据
        assert not eh.verify_claim("admin/admin123", "admin/admin12")


class TestAssignEvidence:
    """测试 EVID 编号生成"""

    def test_format(self):
        assert eh.assign_evidence("T01", 1) == "EVID-T01-001"

    def test_zero_padding(self):
        assert eh.assign_evidence("T01", 12) == "EVID-T01-012"

    def test_hundreds(self):
        assert eh.assign_evidence("T99", 123) == "EVID-T99-123"


class TestParseClaims:
    """测试结论收集 (命令行 + 文件)"""

    def test_from_args_list(self, tmp_path):
        assert eh.parse_claims(["a", "b"], None) == ["a", "b"]

    def test_from_file(self, tmp_path):
        f = tmp_path / "claims.txt"
        f.write_text("claim one\n\nclaim two\n", encoding="utf-8")
        assert eh.parse_claims([], str(f)) == ["claim one", "claim two"]

    def test_merge_args_and_file(self, tmp_path):
        f = tmp_path / "claims.txt"
        f.write_text("from-file\n", encoding="utf-8")
        assert eh.parse_claims(["from-arg"], str(f)) == ["from-arg", "from-file"]

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            eh.parse_claims([], str(tmp_path / "nope.txt"))


class TestHarvest:
    """测试核心采集逻辑"""

    RAW = "nmap scan: 192.168.1.10:22 ssh open\nvuln: SQLi found at /api/login\ncred: admin/admin123"

    def test_verified_and_unverified_status(self):
        m = eh.harvest(self.RAW, "T01", ["SQLi found at /api/login", "fake finding"])
        assert m["evidence"][0]["status"] == "VERIFIED"
        assert m["evidence"][1]["status"] == "UNVERIFIED"

    def test_evid_ids_sequential(self):
        m = eh.harvest(self.RAW, "T01", ["a", "b", "c"])
        ids = [e["id"] for e in m["evidence"]]
        assert ids == ["EVID-T01-001", "EVID-T01-002", "EVID-T01-003"]

    def test_type_heuristics(self):
        m = eh.harvest(
            self.RAW,
            "T01",
            [
                "flag{ctf_secret}",          # flag
                "user: admin pass: secret",  # credential
                "admin/admin123",            # credential (账号/密码对)
                "127.0.0.1:3306:root:123456",  # credential (服务:账号:密码)
                "SQLi found",                # vuln_alert
                "plain note",                # evidence 默认
            ],
        )
        types = [e["type"] for e in m["evidence"]]
        assert types == ["flag", "credential", "credential", "credential", "vuln_alert", "evidence"]

    def test_credential_keyword_detection(self):
        # 中文关键词也要识别
        m = eh.harvest(self.RAW, "T01", ["发现口令: secret123"])
        assert m["evidence"][0]["type"] == "credential"

    def test_strip_status_prefix_before_match(self):
        # 带 [VERIFIED] 前缀的结论, 匹配时应剥掉前缀
        m = eh.harvest(self.RAW, "T01", ["[VERIFIED] SQLi found at /api/login"])
        assert m["evidence"][0]["status"] == "VERIFIED"
        assert m["evidence"][0]["claim"] == "SQLi found at /api/login"

    def test_no_verify_skips_checking(self):
        m = eh.harvest("nothing here", "T01", ["anything"], verify=False)
        assert m["evidence"][0]["status"] == "VERIFIED"

    def test_manifest_structure(self):
        m = eh.harvest(self.RAW, "T01", ["SQLi found at /api/login"],
                       target="192.168.1.10", source_cmd="nuclei -u http://x")
        assert m["task_id"] == "T01"
        assert m["target"] == "192.168.1.10"
        assert m["source_cmd"] == "nuclei -u http://x"
        assert m["verify_enabled"] is True
        assert m["allow_unverified"] is False
        assert m["created_at"]  # 非空时间戳

    def test_raw_snippet_has_context(self):
        m = eh.harvest(self.RAW, "T01", ["SQLi found at /api/login"])
        snippet = m["evidence"][0]["raw_snippet"]
        assert "SQLi found at /api/login" in snippet
        assert len(snippet) > len("SQLi found at /api/login")  # 带上下文

    def test_allow_unverified_does_not_change_status(self):
        m = eh.harvest(self.RAW, "T01", ["fake"], allow_unverified=True)
        assert m["evidence"][0]["status"] == "UNVERIFIED"


class TestWriteManifest:
    """测试 manifest 落盘"""

    def test_writes_json(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(eh, "EVIDENCE_DIR", tmp_path)
        m = eh.harvest("out: secret", "T99", ["secret"], target="x")
        out = eh.write_manifest("T99", m)
        assert out == tmp_path / "manifest_T99.json"
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["task_id"] == "T99"
        assert data["evidence"][0]["id"] == "EVID-T99-001"
        assert "证据清单已写入" in capsys.readouterr().out
