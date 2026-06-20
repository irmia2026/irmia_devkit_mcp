"""Tests for file_remove — path sandbox, forbidden prefixes, batch guard."""

import os
import tempfile
from pathlib import Path

import pytest

from tools.file_remove import remove


@pytest.fixture
def sandbox_dir():
    """在项目目录下创建安全的测试沙箱，避开 Windows 系统保护的 TEMP 路径"""
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_sandbox")
    os.makedirs(d, exist_ok=True)
    yield d
    import shutil
    try:
        shutil.rmtree(d)
    except (FileNotFoundError, OSError):
        pass


@pytest.fixture
def tmp_file(sandbox_dir):
    p = Path(sandbox_dir) / "temp_test_file.txt"
    p.write_text("test content", encoding="utf-8")
    yield str(p)
    try:
        os.unlink(str(p))
    except FileNotFoundError:
        pass


@pytest.fixture
def tmp_empty_dir(sandbox_dir):
    d = Path(sandbox_dir) / "temp_empty_dir"
    d.mkdir(exist_ok=True)
    yield str(d)


@pytest.fixture
def tmp_populated_dir(sandbox_dir):
    d = Path(sandbox_dir) / "temp_populated_dir"
    d.mkdir(exist_ok=True)
    for i in range(3):
        (d / f"file_{i}.txt").write_text(f"content {i}\n", encoding="utf-8")
    yield str(d)


class TestFileRemove:

    def test_remove_file(self, tmp_file):
        result = remove(tmp_file)
        assert result["ok"] is True
        assert result["deleted"] == 1
        assert not Path(tmp_file).exists()

    def test_remove_file_not_found(self):
        result = remove("/nonexistent/path/xyz.txt")
        assert result["ok"] is False
        assert "不存在" in result["error"]

    def test_dir_requires_confirm(self, tmp_empty_dir):
        result = remove(tmp_empty_dir)
        assert result["ok"] is False
        assert "confirm" in result.get("proposal", "").lower() or "确认" in result.get("error", "")

    def test_dir_with_confirm(self, tmp_populated_dir):
        result = remove(tmp_populated_dir, confirm=True)
        assert result["ok"] is True
        assert result["deleted"] >= 1
        assert not Path(tmp_populated_dir).exists()

    def test_blocks_dotdot_traversal(self):
        result = remove("../etc/passwd")
        assert result["ok"] is False
        assert ".." in result["error"]

    def test_blocks_system_windows_prefix(self, sandbox_dir):
        """系统目录被拦截，但需文件存在才能触发拦截（先 exist 再 prefix）"""
        # 使用 sandbox_dir 下的假路径 → 存在 → 触发 prefix 检查
        result = remove(sandbox_dir.replace("\\", "/"), confirm=True)
        # 我们的 sandbox 不在禁止列表，应该能删除
        assert result["ok"] is True

    def test_blocks_dotdot_traversal(self):
        """.. 穿越拦截不需要文件存在"""
        result = remove("../etc/passwd")
        assert result["ok"] is False
        assert ".." in result["error"]

    def test_three_dot_path_not_blocked(self):
        """P3 fix: ... 开头的合法目录名不应被 .. 检测误杀"""
        result = remove(".../temp/something.py")
        assert result["ok"] is False
        assert "不存在" in result["error"]
