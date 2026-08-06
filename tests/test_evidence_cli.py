# ============================================================
# DawnForge 证据包 — cli 统一入口测试
# harvest → archive → report 全链路路由
# ============================================================
import sys
import io
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from evidence_pack import cli, evidence_harvest as eh, memory_archive as ma, report_pack as rp


class TestCliDispatch:
    """测试子命令路由"""

    def test_no_args_returns_1(self, capsys):
        assert cli.main([]) == 1
        assert "usage" in capsys.readouterr().out

    def test_version(self, capsys):
        assert cli.main(["--version"]) == 0
        assert "evidence_pack" in capsys.readouterr().out

    def test_version_short(self, capsys):
        assert cli.main(["-v"]) == 0

    def test_help(self, capsys):
        assert cli.main(["--help"]) == 0
        assert "harvest" in capsys.readouterr().out

    def test_unknown_subcommand(self, capsys):
        assert cli.main(["explode"]) == 1
        assert "未知子命令" in capsys.readouterr().err


class TestCliHarvest:
    """测试 harvest 子命令端到端"""

    def test_full_harvest_flow(self, tmp_path, monkeypatch, capsys):
        # stdin 模拟工具输出
        monkeypatch.setattr("sys.stdin", io.StringIO("found: secret123"))
        monkeypatch.setattr(eh, "EVIDENCE_DIR", tmp_path / "evidence")

        rc = cli.main(["harvest", "--tag", "T01", "--target", "x",
                       "--claim", "secret123", "--source-cmd", "cat flag"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "1 verified / 0 unverified" in out
        manifest = json.loads((tmp_path / "evidence" / "manifest_T01.json").read_text(encoding="utf-8"))
        assert manifest["evidence"][0]["status"] == "VERIFIED"

    def test_no_claims_returns_1(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", io.StringIO("output"))
        assert cli.main(["harvest", "--tag", "T01"]) == 1
        assert "未提供任何结论" in capsys.readouterr().err

    def test_empty_stdin_returns_1(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        assert cli.main(["harvest", "--tag", "T01", "--claim", "x"]) == 1
        assert "stdin 无原始输出" in capsys.readouterr().err


class TestCliArchiveReport:
    """测试 archive / report 子命令路由到对应模块"""

    def test_archive_routes_and_handles_missing_file(self, capsys):
        # manifest 不存在 → main 捕获 FileNotFoundError 返回 1
        assert cli.main(["archive", "no/such/manifest.json"]) == 1
        assert "manifest 不存在" in capsys.readouterr().err

    def test_report_routes_and_handles_missing_file(self, capsys):
        assert cli.main(["report", "no/such/manifest.json"]) == 1
        assert "manifest 不存在" in capsys.readouterr().err

    def test_archive_routes_to_memory_archive(self, tmp_path, monkeypatch, capsys):
        manifest = {"task_id": "T01", "created_at": "t", "target": "x",
                    "evidence": [{"id": "EVID-T01-001", "type": "flag", "status": "VERIFIED",
                                  "claim": "flag{a}", "source_cmd": "cat"}]}
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps(manifest), encoding="utf-8")
        monkeypatch.setattr(ma, "MEMORY_DIR", tmp_path / "memory")
        monkeypatch.setattr(ma, "ATTACK_CHAINS_FILE", tmp_path / "memory" / "attack-chains.yaml")

        assert cli.main(["archive", str(p)]) == 0
        assert (tmp_path / "memory" / "pentest-experience-001.md").exists()

    def test_report_routes_to_report_pack(self, tmp_path, monkeypatch, capsys):
        manifest = {"task_id": "T01", "created_at": "t", "target": "x",
                    "evidence": [{"id": "EVID-T01-001", "type": "flag", "status": "VERIFIED",
                                  "claim": "flag{a}", "source_cmd": "", "raw_snippet": "flag{a}"}]}
        p = tmp_path / "manifest.json"
        p.write_text(json.dumps(manifest), encoding="utf-8")
        monkeypatch.setattr(rp, "REPORTS_DIR", tmp_path / "reports")

        assert cli.main(["report", str(p), "--format", "md"]) == 0
        assert any((tmp_path / "reports").glob("report_T01_*.md"))
