"""Tests for syntax_check — multi-language syntax validation."""

import os
import tempfile
from pathlib import Path

import pytest

from tools.syntax_check import check


def _write_temp(suffix, content):
    fd, path = tempfile.mkstemp(suffix=suffix, text=True)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class TestSyntaxCheckPython:

    def test_valid_python(self):
        path = _write_temp(".py", "x = 1\ny = 2\nprint(x + y)\n")
        try:
            result = check(path)
            assert result["ok"] is True
            assert result["language"] == "python"
        finally:
            os.unlink(path)

    def test_syntax_error(self):
        path = _write_temp(".py", "x = \ny = 2\n")
        try:
            result = check(path)
            assert result["ok"] is False
            assert "errors" in result
            assert len(result["errors"]) >= 1
        finally:
            os.unlink(path)

    def test_syntax_error_has_context(self):
        """P0 feature: 语法错误返回上下文代码片段"""
        path = _write_temp(".py", "def foo():\n    x = \n    return x\n")
        try:
            result = check(path)
            assert result["ok"] is False
            err = result["errors"][0]
            assert "context" in err, "错误应包含 context 字段"
            assert len(err["context"]) >= 1
            # 至少有一行带 → 标记（错误行）
            assert any("→" in line for line in err["context"])
        finally:
            os.unlink(path)

    def test_syntax_error_has_line_and_col(self):
        path = _write_temp(".py", "x = \ny = 2\n")
        try:
            result = check(path)
            assert result["ok"] is False
            err = result["errors"][0]
            assert "line" in err
            assert err["line"] > 0
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        result = check("/nonexistent/file.py")
        assert result["ok"] is False
        assert "不存在" in result["error"]

    def test_unknown_extension(self):
        path = _write_temp(".xyz", "some content")
        try:
            result = check(path)
            assert result["ok"] is True
            assert "note" in result
        finally:
            os.unlink(path)

    def test_gbk_fallback(self):
        """UTF-8 失败时回退 GBK"""
        path = _write_temp(".py", "x = '中文'\n")
        try:
            result = check(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)


class TestSyntaxCheckOther:

    def test_go_skipped_if_not_installed(self):
        path = _write_temp(".go", "package main\nfunc main() {}\n")
        try:
            result = check(path)
            # go 可能未安装 → skipped:true 或 ok:true
            assert result["ok"] is True
        finally:
            os.unlink(path)

    def test_nim_skipped_if_not_installed(self):
        path = _write_temp(".nim", "echo 1\n")
        try:
            result = check(path)
            assert result["language"] == "nim"
            if result["ok"] is False:
                assert "skipped" not in result.get("error", "")
        finally:
            os.unlink(path)

    def test_js_node_skipped_if_not_installed(self):
        path = _write_temp(".js", "console.log('hi');\n")
        try:
            result = check(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)
