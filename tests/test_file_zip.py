"""Tests for file_zip.extract — Zip-slip protection."""

import zipfile
import os
import tempfile
from pathlib import Path
import pytest
from tools.file_zip import extract


@pytest.fixture
def temp_zip_dir():
    d = tempfile.mkdtemp()
    yield d
    import shutil

    shutil.rmtree(d, ignore_errors=True)


class TestFileZipExtract:
    def test_normal_extract(self, temp_zip_dir):
        zip_path = os.path.join(temp_zip_dir, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("hello.txt", "hello world")

        result = extract(zip_path, os.path.join(temp_zip_dir, "out"))
        assert result["ok"] is True
        assert result["files_extracted"] == 1
        assert os.path.exists(os.path.join(temp_zip_dir, "out", "hello.txt"))

    def test_zip_slip_blocked(self, temp_zip_dir):
        zip_path = os.path.join(temp_zip_dir, "evil.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../escape.txt", "escaped!")

        result = extract(zip_path, os.path.join(temp_zip_dir, "out"))
        assert result["ok"] is False
        assert "安全拦截" in result["error"] or "逃逸" in result["error"]

    def test_not_a_zip(self, temp_zip_dir):
        fake = os.path.join(temp_zip_dir, "fake.zip")
        Path(fake).write_text("not a zip file")
        result = extract(fake, os.path.join(temp_zip_dir, "out"))
        assert result["ok"] is False
        assert "不是有效的 ZIP" in result["error"] or "BadZip" in result.get(
            "error", ""
        )
