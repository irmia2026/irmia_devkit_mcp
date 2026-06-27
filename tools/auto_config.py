"""
auto_config — 外部工具自动检测 + 配置文件管理。

启动时自动扫描外部工具，将路径写入 ~/.irmia/mcp_config.json。
用户可手动编辑该文件。扫不到的给出安装指引。

跨平台:
  Windows:  Everything (es.exe) + ripgrep (rg) + GitHub CLI (gh)
  Linux:    locate/fd (内置 fallback, 无需 es) + ripgrep + GitHub CLI
  macOS:    locate/fd (内置 fallback, 无需 es) + ripgrep + GitHub CLI
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

CONFIG_DIR = Path.home() / ".irmia"
CONFIG_PATH = CONFIG_DIR / "mcp_config.json"

# -- 默认配置 --------------------------------------------------
DEFAULT_CONFIG: dict[str, Any] = {
    "es_path": "",
    "rg_path": "",
    "gh_path": "",
    "backup_dir": str(Path.home() / ".irmia" / "backups"),
}

# -- 安装指引（跨平台） -----------------------------------------
_INSTALL_GUIDE_BASE: dict[str, dict[str, str]] = {
    "es": {
        "windows": (
            "Everything (Windows 文件名搜索, 毫秒级):\n"
            "  下载: https://www.voidtools.com/downloads/\n"
            "  安装后请确保 es.exe 在 PATH 中, 或手动填写 es_path。"
        ),
        "linux": (
            "Linux 下 es_search 自动使用 locate / fd / os.walk 三层回退,\n"
            "无需安装 Everything。建议安装 'fd-find' 获得更快速度:\n"
            "  sudo apt install fd-find  或  sudo dnf install fd-find\n"
            "  (可选) 运行 sudo updatedb 更新 locate 索引。"
        ),
        "darwin": (
            "macOS 下 es_search 自动使用 locate / fd / os.walk 三层回退,\n"
            "无需安装 Everything。建议安装 'fd' 获得更快速度:\n"
            "  brew install fd"
        ),
    },
    "rg": {
        "windows": (
            "ripgrep (跨平台内容搜索, 毫秒级):\n"
            "  scoop install ripgrep  或  choco install ripgrep"
        ),
        "linux": (
            "ripgrep (跨平台内容搜索, 毫秒级):\n"
            "  sudo apt install ripgrep  或  sudo dnf install ripgrep"
        ),
        "darwin": (
            "ripgrep (跨平台内容搜索, 毫秒级):\n"
            "  brew install ripgrep"
        ),
    },
    "gh": {
        "windows": (
            "GitHub CLI (GitHub 操作):\n"
            "  下载: https://cli.github.com/\n"
            "  安装后运行: gh auth login"
        ),
        "linux": (
            "GitHub CLI (GitHub 操作):\n"
            "  sudo apt install gh  或  sudo dnf install gh\n"
            "  安装后运行: gh auth login"
        ),
        "darwin": (
            "GitHub CLI (GitHub 操作):\n"
            "  brew install gh\n"
            "  安装后运行: gh auth login"
        ),
    },
}

# 根据当前平台生成安装指引
INSTALL_GUIDE: dict[str, str] = {}
for _tool, _platforms in _INSTALL_GUIDE_BASE.items():
    if IS_WINDOWS:
        INSTALL_GUIDE[_tool] = _platforms["windows"]
    elif IS_MACOS:
        INSTALL_GUIDE[_tool] = _platforms.get("darwin", _platforms.get("linux", ""))
    else:
        INSTALL_GUIDE[_tool] = _platforms.get("linux", list(_platforms.values())[0])


def _get_platform_key() -> str:
    """返回当前平台标识: windows / linux / darwin。"""
    return platform.system().lower()


def _find_exe(names: list[str], extra_paths: list[str] | None = None) -> str:
    """搜索可执行文件：PATH -> 常见路径 -> 返回空字符串。"""
    for name in names:
        found = shutil.which(name)
        if found:
            return found

    if extra_paths:
        for name in names:
            for base in extra_paths:
                candidate = os.path.join(base, name)
                if os.path.isfile(candidate):
                    return candidate

    return ""


def scan_tools() -> dict[str, Any]:
    """扫描本地外部工具，返回检测结果。跨平台感知。"""
    result: dict[str, Any] = {}

    # -- es (仅 Windows 需要 Everything；Linux/macOS 用 locate/fd) --
    if IS_WINDOWS:
        result["es_path"] = _find_exe(["es", "es.exe"])
    else:
        # Linux/macOS: es_search 自动用 locate/fd，不需要 es_path
        result["es_path"] = ""  # 空 = 使用内置 fallback（不会触发警告）

    # -- rg (跨平台) --
    result["rg_path"] = _find_exe(["rg", "rg.exe"])

    # -- gh (跨平台) --
    extra_gh = None
    if IS_WINDOWS:
        extra_gh = [
            r"C:\Program Files\GitHub CLI",
            r"C:\Program Files (x86)\GitHub CLI",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\GitHub CLI"),
        ]
    result["gh_path"] = _find_exe(["gh", "gh.exe"], extra_paths=extra_gh)

    result["_platform"] = _get_platform_key()
    result["_missing"] = [
        k.replace("_path", "") for k, v in result.items()
        if not v and k.endswith("_path") and not k.startswith("_")
    ]

    return result


def load_config() -> dict[str, Any]:
    """加载配置：读 mcp_config.json -> 合并扫描结果 -> 写回。"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 读已有配置
    if CONFIG_PATH.exists():
        try:
            existing = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    else:
        existing = {}

    # 2) 合并默认值
    config = dict(DEFAULT_CONFIG)
    for key in config:
        if key in existing and existing[key]:
            config[key] = existing[key]

    # 3) 自动扫描并填充空值
    scanned = scan_tools()
    updated = False
    for key in config:
        if key.endswith("_path") and not config.get(key):
            found = scanned.get(key, "")
            if found:
                config[key] = found
                updated = True

    # 4) 写回（如有新发现）
    if updated:
        _save_config(config)

    return config


def _save_config(config: dict[str, Any]) -> None:
    """保存配置到磁盘（仅保存用户可编辑的键）。"""
    to_save = {k: v for k, v in config.items() if not k.startswith("_")}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(to_save, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def check_and_warn(config: dict[str, Any], *, silent: bool = False) -> list[str]:
    """检查缺失的外部工具，打印警告 + 返回缺失列表。
    跨平台：Linux/macOS 下 es_path 为空不警告（自动用 locate/fd）。
    """
    missing: list[str] = []
    for key, guide in INSTALL_GUIDE.items():
        path_key = f"{key}_path"

        # es_path 在非 Windows 平台上空值是正常的（使用 locate/fd）
        if key == "es" and not IS_WINDOWS:
            continue

        if not config.get(path_key):
            missing.append(key)
            if not silent:
                print(f"\n[!] 未检测到 {key} -- {path_key} 为空")
                print(f"    对应的外部工具: {guide.split(chr(10))[0]}")
                print(f"    详细安装指引见: ~/.irmia/mcp_config.json")
                print(f"    {guide}")
    return missing


def print_startup_banner(config: dict[str, Any]) -> None:
    """启动横幅：工具状态一览。"""
    tools_status = []
    for key in ("es_path", "rg_path", "gh_path"):
        name = key.replace("_path", "")
        path = config.get(key, "")

        # 非 Windows 下 es 显示内置回退
        if key == "es_path" and not IS_WINDOWS:
            if path:
                tools_status.append(f"  [+] {name:>4s} -> {path}")
            else:
                tools_status.append(f"  [~] {name:>4s} -> locate/fd (内置回退)")
        elif path:
            tools_status.append(f"  [+] {name:>4s} -> {path}")
        else:
            tools_status.append(f"  [-] {name:>4s} -> 未安装 (功能降级可用)")

    print(f"""
+======================================================================+
|           Irmia DevKit MCP -- 外部工具状态  ({_get_platform_key():>7s})         |
+======================================================================+
{chr(10).join(tools_status)}
+======================================================================+
|  配置文件: {str(CONFIG_PATH):<55s} |
+======================================================================+
""")
