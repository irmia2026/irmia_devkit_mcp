"""
auto_config — 外部工具自动检测 + 配置文件管理。

启动时自动扫描外部工具，将路径写入 ~/.irmia/mcp_config.json。
用户可手动编辑该文件。扫不到的给出安装指引。

跨平台:
  Windows:  Everything (es.exe) + ripgrep (rg.exe/rg) + fd (fd.exe/fd)
  Linux:    locate/fd (内置 fallback, 无需 es) + ripgrep (rg) + fd
  macOS:    locate/fd (内置 fallback, 无需 es) + ripgrep (rg) + fd
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

# -- 用户可选二进制目录（发布包不内置；可放置已验证的 rg / es / fd） --------
VENDOR_DIR = Path(__file__).resolve().parent.parent / "vendor"

# -- 默认配置 --------------------------------------------------
DEFAULT_CONFIG: dict[str, Any] = {
    "es_path": "",
    "rg_path": "",
    "fd_path": "",
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
    """搜索可执行文件：用户提供的 vendor 目录 → PATH → 常见路径 → 返回空字符串。
    跨平台：Linux/macOS 优先无后缀原生二进制，忽略 .exe；Windows 优先 .exe。"""
    # 根据平台决定候选顺序：Linux/macOS 优先无后缀，Windows 优先 .exe
    if IS_WINDOWS:
        ordered = sorted(names, key=lambda n: (not n.endswith(".exe"), n))
    else:
        ordered = sorted(names, key=lambda n: (n.endswith(".exe"), n))

    # 1. 优先搜索项目内置目录
    for name in ordered:
        candidate = str(VENDOR_DIR / name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
        # Windows 上 .exe 可能没有显式 X 权限，但仍可执行
        if IS_WINDOWS and os.path.isfile(candidate):
            return candidate

    # 2. 系统 PATH
    for name in ordered:
        found = shutil.which(name)
        if found:
            return found

    # 3. 额外指定路径
    if extra_paths:
        for name in ordered:
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

    # -- fd (跨平台，es_search 的 fallback 引擎) --
    result["fd_path"] = _find_exe(["fd", "fd.exe"])

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
                print(f"\n[!] 未检测到 {key} -- {path_key} 为空", file=sys.stderr)
                print(f"    对应的外部工具: {guide.split(chr(10))[0]}", file=sys.stderr)
                print(f"    详细安装指引见: ~/.irmia/mcp_config.json", file=sys.stderr)
                print(f"    {guide}", file=sys.stderr)
    return missing


def print_startup_banner(config: dict[str, Any], *, quiet: bool = False) -> None:
    """启动横幅：工具状态一览。quiet=True 时静默（stdio 模式必须保持 stdout 纯净）。"""
    if quiet:
        return
    tools_status = []
    for key in ("es_path", "rg_path", "fd_path"):
        name = key.replace("_path", "")
        path = config.get(key, "")

        # 非 Windows 下 es 显示内置回退；fd 是 es_search 的 fallback 引擎
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
""", file=sys.stderr)
