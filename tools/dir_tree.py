"""
dir_tree — 目录树可视化。
用 os.scandir 递归扫描目录，生成缩进树结构。
"""

import fnmatch
import os

from ._file_utils import human_size


def tree(
    path: str,
    max_depth: int = 3,
    show_hidden: bool = False,
    pattern: str = "",
    max_items: int = 100,
) -> dict:
    """生成目录树。

    Args:
        path: 目录路径
        max_depth: 最大递归深度（默认 3）
        show_hidden: 是否显示隐藏文件/目录
        pattern: 文件名过滤，如 "*.py"
        max_items: 每层最大条目数

    Returns:
        {"ok": True, "tree": "...", "stats": {...}} 或 {"ok": False, "error": ...}
    """
    if not os.path.isdir(path):
        return {"ok": False, "error": f"不是目录: {path}"}

    root_name = os.path.basename(os.path.abspath(path)) or path
    lines = [root_name]
    stats = {"dirs": 0, "files": 0}
    # H9: symlink 循环检测
    visited_inodes: set[int] = set()

    def _walk(current: str, prefix: str, depth: int):
        if depth >= max_depth:
            return
        # H9: 检测并跳过循环
        try:
            st = os.stat(current)
            inode_key = (st.st_dev, st.st_ino)
            if inode_key in visited_inodes:
                lines.append(f"{prefix}└── [循环链接]")
                return
            visited_inodes.add(inode_key)
        except OSError:
            pass
        try:
            entries = sorted(
                os.scandir(current), key=lambda e: (not e.is_dir(), e.name.lower())
            )
        except PermissionError:
            lines.append(f"{prefix}└── [权限不足]")
            return

        # 过滤隐藏
        if not show_hidden:
            entries = [e for e in entries if not e.name.startswith(".")]

        # 模式过滤
        if pattern:
            entries = [
                e for e in entries if e.is_dir() or fnmatch.fnmatch(e.name, pattern)
            ]

        count = min(len(entries), max_items)
        for i, entry in enumerate(entries[:count]):
            is_last = i == count - 1
            connector = "└── " if is_last else "├── "
            if entry.is_dir():
                stats["dirs"] += 1
                lines.append(f"{prefix}{connector}{entry.name}/")
                _walk(entry.path, prefix + ("    " if is_last else "│   "), depth + 1)
            else:
                stats["files"] += 1
                try:
                    size = entry.stat().st_size
                    lines.append(
                        f"{prefix}{connector}{entry.name} ({human_size(size)})"
                    )
                except OSError:
                    lines.append(f"{prefix}{connector}{entry.name}")

        if len(entries) > max_items:
            lines.append(f"{prefix}└── ... 还有 {len(entries) - max_items} 项")

    _walk(os.path.abspath(path), "", 0)

    return {
        "ok": True,
        "tree": "\n".join(lines),
        "stats": stats,
    }
