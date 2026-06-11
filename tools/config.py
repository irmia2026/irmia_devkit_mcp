"""
config — MCP-level 全局配置单例。
从 irmia_devkit_open 剥离，移除 AstrBot 依赖。
"""

from __future__ import annotations
from pathlib import Path
import os

_config: dict = {}
_plugin_dir: str = ""


def set_config(cfg: dict, plugin_dir: str = "") -> None:
    global _config, _plugin_dir
    _config = cfg
    if plugin_dir:
        _plugin_dir = plugin_dir
    # 保证默认值
    _config.setdefault("backup_dir", str(Path.home() / ".irmia" / "backups"))
    _config.setdefault("gh_path", "")
    _config.setdefault("es_path", "")
    _config.setdefault("state_dir", "")
    _config.setdefault("lock_dirs", [])
    _config.setdefault("op_log_db", "")


def get_config() -> dict:
    return _config


def get_plugin_dir() -> str:
    if _plugin_dir:
        return _plugin_dir
    return os.getcwd()
