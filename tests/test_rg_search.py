"""Tests for rg_search — ripgrep + Python fallback content search."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.rg_search import search, _parse_rg_output, _find_rg


class TestRgOutputParser:
    """测试 _parse_rg_output 的跨平台路径解析"""

    def test_standard_unix_path(self):
        lines = _parse_rg_output("file.py:10:    print(x)\n")
        assert len(lines) == 1
        assert lines[0]["file"] == "file.py"
        assert lines[0]["line"] == 10
        assert lines[0]["content"] == "    print(x)"

    def test_relative_path(self):
        lines = _parse_rg_output("tools/safe_edit.py:68:    result = await _run_sync\n")
        assert len(lines) == 1
        assert lines[0]["file"] == "tools/safe_edit.py"
        assert lines[0]["line"] == 68

    def test_windows_absolute_path(self):
        """Windows 盘符含冒号，regex 正确解析"""
        lines = _parse_rg_output(r"C:\Users\dev\proj\main.py:42:    x = 1")
        assert len(lines) == 1
        assert lines[0]["file"] == r"C:\Users\dev\proj\main.py"
        assert lines[0]["line"] == 42
        assert lines[0]["content"] == "    x = 1"

    def test_content_contains_colons(self):
        """内容含冒号时 rsplit 取最后两个作为 line:content"""
        lines = _parse_rg_output("config.py:5:    url: str = ''\n")
        assert len(lines) == 1
        assert lines[0]["file"] == "config.py"
        assert lines[0]["line"] == 5
        assert lines[0]["content"] == "    url: str = ''"

    def test_multiple_matches(self):
        stdout = "a.py:1:import os\na.py:3:import sys\nb.py:7:from pathlib import Path\n"
        lines = _parse_rg_output(stdout)
        assert len(lines) == 3
        assert lines[0]["file"] == "a.py"
        assert lines[2]["file"] == "b.py"
        assert lines[2]["line"] == 7

    def test_empty_input(self):
        assert _parse_rg_output("") == []

    def test_malformed_lines_skipped(self):
        """格式不对的行静默跳过"""
        lines = _parse_rg_output("broken_line\nok.py:3:content\n")
        assert len(lines) == 1


class TestRgSearchBasic:
    def test_finds_pattern_in_files(self, project_dir):
        result = search("def helper", path=project_dir)
        assert result["ok"] is True
        assert result["count"] >= 1
        match_files = [m["file"] for m in result["matches"]]
        assert any("utils.py" in f for f in match_files)

    def test_no_match_returns_empty(self, project_dir):
        result = search("nonexistent_xyz_123", path=project_dir)
        assert result["ok"] is True
        assert result["count"] == 0

    def test_file_exts_filter(self, project_dir):
        """指定扩展名过滤"""
        result = search("helper", path=project_dir, file_exts="txt")
        assert result["count"] == 0

    def test_list_files_mode(self, project_dir):
        """list_files=True 只返回文件名无行号"""
        result = search("def", path=project_dir, list_files=True)
        assert result["ok"] is True
        for m in result["matches"]:
            assert "file" in m
            assert "line" not in m

    def test_whole_word(self, project_dir):
        """全词匹配"""
        result = search("hel", path=project_dir, whole_word=True)
        assert result["count"] == 0  # "hel" 不是独立词
        result2 = search("helper", path=project_dir, whole_word=True)
        assert result2["count"] >= 1  # "helper" 是独立词

    def test_case_sensitive(self, project_dir):
        result = search("HELPER", path=project_dir, case_sensitive=True)
        assert result["count"] == 0
        result2 = search("HELPER", path=project_dir, case_sensitive=False)
        assert result2["count"] >= 1

    def test_max_results(self, project_dir):
        result = search(".", path=project_dir, max_results=1)
        assert result["count"] <= 1
        assert result["truncated"] is True or result["count"] == 1

    def test_non_existent_dir(self):
        result = search("test", path="/nonexistent/path/xyz")
        assert result["ok"] is False
        assert "不存在" in result["error"]

    def test_invalid_regex(self, project_dir):
        result = search("[unclosed", path=project_dir)
        assert result["ok"] is False

    def test_python_fallback_redos_long_pattern(self, project_dir, monkeypatch):
        """Python fallback 应拒绝超长 pattern。"""
        monkeypatch.setattr("tools.rg_search._find_rg", lambda: None)
        result = search("x" * 2000, path=project_dir)
        assert result.get("ok") is False
        assert "pattern_too_long" in str(result)

    def test_python_fallback_redos_nested_quantifiers(self, project_dir, monkeypatch):
        """Python fallback 应拒绝嵌套量词。"""
        monkeypatch.setattr("tools.rg_search._find_rg", lambda: None)
        result = search("(a+)+b", path=project_dir)
        assert result.get("ok") is False
        assert "nested_quantifiers" in str(result)

    def test_returns_engine_field(self, project_dir):
        result = search("class", path=project_dir)
        assert "engine" in result
        assert result["engine"] in ("rg", "python")

    def test_find_rg(self):
        """_find_rg 返回 True/None"""
        rg = _find_rg()
        # 不能假设 rg 已安装，只验证返回类型
        assert rg is None or isinstance(rg, str)
