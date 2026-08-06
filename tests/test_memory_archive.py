# ============================================================
# DawnForge 证据包 — memory_archive 单元测试
# 冷热记忆治理: 高信号证据去重沉淀到经验/攻击链
# ============================================================
import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evidence_pack import memory_archive as ma
from evidence_pack.evidence_harvest import HIGH_SIGNAL_TYPES


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """将 MEMORY_DIR / ATTACK_CHAINS_FILE 指向临时目录, 避免污染真实 memory/"""
    monkeypatch.setattr(ma, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(ma, "ATTACK_CHAINS_FILE", tmp_path / "attack-chains.yaml")
    return tmp_path


def make_manifest(task_id="T01", target="192.168.1.10", evidence=None):
    return {
        "task_id": task_id,
        "created_at": "2026-08-06T10:00:00",
        "target": target,
        "evidence": evidence or [],
    }


def make_evidence(eid="EVID-T01-001", etype="flag", status="VERIFIED", claim="flag{x}", src="cmd"):
    return {"id": eid, "type": etype, "status": status, "claim": claim, "source_cmd": src}


class TestLoadManifest:
    """测试 manifest 读取"""

    def test_load_existing(self, tmp_path):
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps({"task_id": "T01"}), encoding="utf-8")
        assert ma.load_manifest(str(p))["task_id"] == "T01"

    def test_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ma.load_manifest(str(tmp_path / "nope.json"))


class TestNextExperienceNumber:
    """测试经验文件序号推进"""

    def test_empty_dir_starts_at_1(self, isolated):
        assert ma.next_experience_number() == 1

    def test_highest_existing_plus_one(self, isolated):
        (isolated / "pentest-experience-005.md").write_text("x", encoding="utf-8")
        (isolated / "pentest-experience-002.md").write_text("x", encoding="utf-8")
        assert ma.next_experience_number() == 6

    def test_ignores_other_files(self, isolated):
        (isolated / "attack-chains.yaml").write_text("x", encoding="utf-8")
        (isolated / "README.md").write_text("x", encoding="utf-8")
        assert ma.next_experience_number() == 1


class TestCollectExistingEvidIds:
    """测试已归档 EVID 编号收集"""

    def test_finds_evids_in_markdown(self, isolated):
        (isolated / "pentest-experience-001.md").write_text(
            "EVID-T01-001 and EVID-T02-007\nnot-an-evid", encoding="utf-8"
        )
        ids = ma.collect_existing_evid_ids()
        assert ids == {"EVID-T01-001", "EVID-T02-007"}

    def test_empty_when_no_files(self, isolated):
        assert ma.collect_existing_evid_ids() == set()

    def test_skips_unreadable_files(self, isolated):
        # 二进制/异常编码文件不应让整个流程崩溃
        (isolated / "pentest-experience-001.md").write_bytes(b"\xff\xfe\x00\x80")
        assert ma.collect_existing_evid_ids() == set()


class TestFilterHighSignal:
    """测试高信号筛选"""

    def test_only_high_signal_verified(self):
        m = make_manifest(evidence=[
            make_evidence("EVID-T01-001", "flag", "VERIFIED"),       # 保留
            make_evidence("EVID-T01-002", "credential", "VERIFIED"),  # 保留
            make_evidence("EVID-T01-003", "evidence", "VERIFIED"),    # 噪音, 排除
            make_evidence("EVID-T01-004", "flag", "UNVERIFIED"),      # 未验证, 排除
        ])
        result = ma.filter_high_signal(m)
        assert [e["id"] for e in result] == ["EVID-T01-001", "EVID-T01-002"]

    def test_high_signal_types_defined(self):
        assert {"flag", "credential", "vuln_alert", "chain", "critical_config"} == HIGH_SIGNAL_TYPES


class TestWriteExperienceFile:
    """测试经验文件生成"""

    def test_content_structure(self, isolated):
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "flag", "VERIFIED", "flag{x}", "nmap -p22")])
        path = ma.write_experience_file(m, m["evidence"])
        assert path.name == "pentest-experience-001.md"
        text = path.read_text(encoding="utf-8")
        assert "# pentest-experience-001" in text
        assert "- 目标: 192.168.1.10" in text
        assert "- 任务标识: T01" in text
        assert "| EVID-T01-001 | flag | flag{x} | nmap -p22 |" in text

    def test_number_increments_across_writes(self, isolated):
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "flag", "VERIFIED")])
        first = ma.write_experience_file(m, m["evidence"])
        second = ma.write_experience_file(m, m["evidence"])
        assert first.name == "pentest-experience-001.md"
        assert second.name == "pentest-experience-002.md"


class TestAppendAttackChains:
    """测试攻击链并入"""

    def test_appends_chain_evidence(self, isolated):
        m = make_manifest(task_id="T03", evidence=[
            make_evidence("EVID-T03-001", "chain", "VERIFIED", "SSRF -> RCE", "curl"),
            make_evidence("EVID-T03-002", "flag", "VERIFIED", "flag{y}", "cat"),  # 非 chain 不写
        ])
        ma.append_attack_chains(m)
        text = (isolated / "attack-chains.yaml").read_text(encoding="utf-8")
        assert "id: CHAIN-T03" in text
        assert 'summary: "SSRF -> RCE"' in text
        assert "evidence: \"EVID-T03-001\"" in text
        assert "flag{y}" not in text

    def test_no_chain_evidence_does_not_create_file(self, isolated):
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "flag", "VERIFIED")])
        ma.append_attack_chains(m)
        assert not (isolated / "attack-chains.yaml").exists()

    def test_appends_to_existing_without_broken_lines(self, isolated):
        (isolated / "attack-chains.yaml").write_text("chains:", encoding="utf-8")  # 无结尾换行
        m = make_manifest(task_id="T05", evidence=[make_evidence("EVID-T05-001", "chain", "VERIFIED", "a->b")])
        ma.append_attack_chains(m)
        text = (isolated / "attack-chains.yaml").read_text(encoding="utf-8")
        assert "chains:\n  - id: CHAIN-T05" in text


class TestArchive:
    """测试归档主流程 (含去重)"""

    def test_no_high_signal_returns_early(self, isolated, capsys):
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "evidence", "VERIFIED")])
        p = isolated / "m.json"
        p.write_text(json.dumps(m), encoding="utf-8")
        assert ma.archive(str(p)) == 0
        assert "不沉淀" in capsys.readouterr().out
        assert not list(isolated.glob("pentest-experience-*.md"))

    def test_dedup_skips_existing_evid(self, isolated, capsys):
        (isolated / "pentest-experience-001.md").write_text(
            "EVID-T01-001 already archived", encoding="utf-8"
        )
        m = make_manifest(evidence=[
            make_evidence("EVID-T01-001", "flag", "VERIFIED", "old"),
            make_evidence("EVID-T01-002", "flag", "VERIFIED", "new"),
        ])
        p = isolated / "m.json"
        p.write_text(json.dumps(m), encoding="utf-8")
        ma.archive(str(p))
        text = (isolated / "pentest-experience-002.md").read_text(encoding="utf-8")
        assert "EVID-T01-001" not in text  # 已存在, 跳过
        assert "EVID-T01-002" in text
        assert "去重" in capsys.readouterr().out

    def test_all_duplicate_returns_early(self, isolated, capsys):
        (isolated / "pentest-experience-001.md").write_text("EVID-T01-001", encoding="utf-8")
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "flag", "VERIFIED")])
        p = isolated / "m.json"
        p.write_text(json.dumps(m), encoding="utf-8")
        assert ma.archive(str(p)) == 0
        assert "无新增" in capsys.readouterr().out

    def test_no_dedup_forces_write(self, isolated):
        (isolated / "pentest-experience-001.md").write_text("EVID-T01-001", encoding="utf-8")
        m = make_manifest(evidence=[make_evidence("EVID-T01-001", "flag", "VERIFIED")])
        p = isolated / "m.json"
        p.write_text(json.dumps(m), encoding="utf-8")
        ma.archive(str(p), no_dedup=True)
        assert (isolated / "pentest-experience-002.md").exists()
