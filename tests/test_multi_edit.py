"""Tests for atomic multi_edit."""

from pathlib import Path

from tools import config as _tool_config
from tools.multi_edit import run


class TestMultiEdit:
    def _use_tmp_backups(self, tmp_dir):
        _tool_config.set_config({"backup_dir": f"{tmp_dir}/backups"}, plugin_dir=tmp_dir)

    def test_applies_multiple_files(self, tmp_dir):
        self._use_tmp_backups(tmp_dir)
        a = Path(tmp_dir) / "a.py"
        b = Path(tmp_dir) / "b.py"
        a.write_text("x = 1\n", encoding="utf-8")
        b.write_text("y = 2\n", encoding="utf-8")

        result = run([
            {"file": str(a), "old": "x = 1", "new": "x = 10"},
            {"file": str(b), "old": "y = 2", "new": "y = 20"},
        ])

        assert result["ok"] is True
        assert "x = 10" in a.read_text(encoding="utf-8")
        assert "y = 20" in b.read_text(encoding="utf-8")

    def test_rejects_ambiguous_match_before_writing(self, tmp_dir):
        self._use_tmp_backups(tmp_dir)
        a = Path(tmp_dir) / "a.py"
        b = Path(tmp_dir) / "b.py"
        a.write_text("x = 1\nx = 1\n", encoding="utf-8")
        b.write_text("y = 2\n", encoding="utf-8")

        result = run([
            {"file": str(b), "old": "y = 2", "new": "y = 20"},
            {"file": str(a), "old": "x = 1", "new": "x = 10"},
        ])

        assert result["ok"] is False
        assert result["rolled_back_all"] is True
        assert b.read_text(encoding="utf-8") == "y = 2\n"

    def test_same_file_edits_are_sequential(self, tmp_dir):
        self._use_tmp_backups(tmp_dir)
        p = Path(tmp_dir) / "a.py"
        p.write_text("x = 1\ny = x\n", encoding="utf-8")

        result = run([
            {"file": str(p), "old": "x = 1", "new": "x = 2"},
            {"file": str(p), "old": "y = x", "new": "y = x + 1"},
        ])

        assert result["ok"] is True
        assert p.read_text(encoding="utf-8") == "x = 2\ny = x + 1\n"

    def test_syntax_failure_rolls_back_all(self, tmp_dir):
        self._use_tmp_backups(tmp_dir)
        a = Path(tmp_dir) / "a.py"
        b = Path(tmp_dir) / "b.py"
        a.write_text("x = 1\n", encoding="utf-8")
        b.write_text("y = 2\n", encoding="utf-8")

        result = run([
            {"file": str(a), "old": "x = 1", "new": "x ="},
            {"file": str(b), "old": "y = 2", "new": "y = 20"},
        ])

        assert result["ok"] is False
        assert result["rolled_back_all"] is True
        assert a.read_text(encoding="utf-8") == "x = 1\n"
        assert b.read_text(encoding="utf-8") == "y = 2\n"
