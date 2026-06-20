"""pytest fixtures for irmia_devkit tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import config as _tool_config


@pytest.fixture(autouse=True)
def _reset_config():
    """每个测试前重置全局配置，防止测试间互扰。"""
    _tool_config.set_config({}, plugin_dir="")


@pytest.fixture
def tmp_dir():
    """临时目录，测试后自动清理。"""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def tmp_py_file(tmp_dir):
    """临时 Python 文件，写入简短示例代码。"""
    p = Path(tmp_dir) / "test.py"
    p.write_text("x = 1\ny = 2\nprint(x + y)\n", encoding="utf-8")
    return str(p)


@pytest.fixture
def tmp_txt_file(tmp_dir):
    """临时文本文件。"""
    p = Path(tmp_dir) / "test.txt"
    p.write_text("hello world\nfoo bar\n", encoding="utf-8")
    return str(p)


@pytest.fixture
def tmp_json_file(tmp_dir):
    """临时 JSON 配置文件。"""
    p = Path(tmp_dir) / "config.json"
    p.write_text('{"name": "test", "version": "1.0"}', encoding="utf-8")
    return str(p)


@pytest.fixture
def project_dir(tmp_dir):
    """迷你项目目录：含多个 .py 文件和 __pycache__。"""
    root = Path(tmp_dir) / "project"
    root.mkdir()
    (root / "main.py").write_text("from .utils import helper\ndef main(): pass\n", encoding="utf-8")
    (root / "utils.py").write_text("def helper(): return 42\n", encoding="utf-8")
    (root / "models.py").write_text("class User:\n    pass\n", encoding="utf-8")
    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "main.cpython-312.pyc").write_text("", encoding="utf-8")
    return str(root)
