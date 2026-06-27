"""Tests for symbol_rename token-based Python renaming."""

import os
import sqlite3
from pathlib import Path

from tools import config as _tool_config
from tools.codegraph import CodeGraph
from tools.symbol_rename import _rename_content, run


class TestSymbolRename:
    def test_rename_content_skips_strings_and_comments(self):
        content = (
            "def old_name():\n"
            "    text = 'old_name'\n"
            "    # old_name in comment\n"
            "    return old_name()\n"
        )

        renamed, refs = _rename_content(content, "old_name", "new_name")

        assert "def new_name()" in renamed
        assert "return new_name()" in renamed
        assert "'old_name'" in renamed
        assert "# old_name in comment" in renamed
        assert len(refs) == 2

    def test_requires_index(self, tmp_dir):
        result = run("old_name", "new_name", project_dir=tmp_dir)

        assert result["ok"] is False
        assert "codegraph index" in result["error"]

    def test_dry_run_preview(self, tmp_dir):
        root = Path(tmp_dir)
        (root / "mod.py").write_text(
            "def old_name():\n"
            "    return 1\n\n"
            "def caller():\n"
            "    return old_name()\n",
            encoding="utf-8",
        )
        cg = CodeGraph(str(root / ".codegraph" / "codegraph.db"))
        try:
            cg.index(str(root))
        finally:
            cg.close()

        result = run("old_name", "new_name", project_dir=tmp_dir, dry_run=True)

        assert result["ok"] is True
        assert result["dry_run"] is True
        assert result["total_refs"] == 2
        assert "new_name" in result["diffs"][0]["diff"]
        assert "old_name" in (root / "mod.py").read_text(encoding="utf-8")

    def test_apply_uses_multi_edit(self, tmp_dir):
        _tool_config.set_config({"backup_dir": f"{tmp_dir}/backups"}, plugin_dir=tmp_dir)
        root = Path(tmp_dir)
        (root / "mod.py").write_text(
            "def old_name():\n"
            "    return 1\n\n"
            "def caller():\n"
            "    return old_name()\n",
            encoding="utf-8",
        )
        cg = CodeGraph(str(root / ".codegraph" / "codegraph.db"))
        try:
            cg.index(str(root))
        finally:
            cg.close()

        result = run("old_name", "new_name", project_dir=tmp_dir, dry_run=False)

        assert result["ok"] is True
        assert result["renamed"] == 2
        content = (root / "mod.py").read_text(encoding="utf-8")
        assert "def new_name()" in content
        assert "return new_name()" in content

    def test_conflict_blocks_rename(self, tmp_dir):
        root = Path(tmp_dir)
        (root / "mod.py").write_text(
            "def old_name():\n"
            "    return 1\n\n"
            "def new_name():\n"
            "    return 2\n",
            encoding="utf-8",
        )
        cg = CodeGraph(str(root / ".codegraph" / "codegraph.db"))
        try:
            cg.index(str(root))
        finally:
            cg.close()

        result = run("old_name", "new_name", project_dir=tmp_dir)

        assert result["ok"] is False
        assert "conflict" in result["error"]
