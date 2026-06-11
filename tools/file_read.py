"""
file_read — 文件读取工具。
编辑前置流程的第一步：读取 → 理解 → 构造 safe_edit 的 old 参数。
"""

from __future__ import annotations
from pathlib import Path
from ._file_utils import SAFE_EDIT_MAX_SIZE, human_size
from ._helpers import proposal_reply

# 二进制文件检测的魔数和空字节阈值
_BINARY_CHECK_BYTES = 1024
_NULL_BYTE_RATIO = 0.10  # 前 1KB 中 >10% 是 \x00 或 \x01-\x08 则判定为二进制
_BINARY_CONTROL_CODES = frozenset(range(1, 9))  # 不含 \t \n \r

# 长文本截断阈值（行数），超过此值在 content 尾部追加提示
_LONG_LINE_THRESHOLD = 500


def _is_binary(raw: bytes) -> bool:
    """检测任意编码读取失败后的二进制特征。传入原始字节串。
    
    两阶段：① 空字节检测 ② 低值控制码比例检测。
    """
    if not raw:
        return False
    chunk = raw[:_BINARY_CHECK_BYTES]
    null_count = chunk.count(0)
    if null_count > 0:
        return True
    control_count = sum(1 for b in chunk if b in _BINARY_CONTROL_CODES)
    return (control_count / len(chunk)) > _NULL_BYTE_RATIO


def _detect_line_ending(raw_text: str) -> str:
    """检测换行符风格。"""
    if "\r\n" in raw_text:
        return "CRLF" if raw_text.count("\r\n") > raw_text.count("\n") / 2 else "mixed"
    return "LF"


def read(
    filepath: str,
    start_line: int = 0,
    end_line: int = 0,
    encoding: str = "",
) -> dict:
    """读取文件内容，返回带行号的 content 和无行号的 text。
    
    编辑前必调——LLM 需要看到文件才能构造 safe_edit 的 old 参数。
    text 字段可以直接复制为 safe_edit 的 old 值，无需手动去除行号。

    Args:
        filepath: 文件路径
        start_line: 起始行号（1-based，0=从头开始）
        end_line: 结束行号（1-based 含，0=到末尾）。只设 end_line 时等价于读前 N 行
        encoding: 强制编码，空=自动检测（UTF-8 → GBK → Latin-1）
    """
    # ── 守卫：路径合法性 ──────────────────────────────
    try:
        p = Path(filepath).resolve(strict=False)
    except (OSError, RuntimeError) as e:
        return proposal_reply(
            False,
            f"路径无效: {filepath}",
            error=str(e),
            evidence={"filepath": filepath},
            options=["检查路径是否存在", "用 es_search 搜索文件名", "用 dir_list 浏览目录"],
        )

    if not p.exists():
        return proposal_reply(
            False,
            f"文件不存在: {filepath}",
            error="file_not_found",
            evidence={"filepath": filepath, "resolved": str(p)},
            options=["用 es_search 搜索文件名", "用 dir_list 浏览父目录", "检查拼写"],
            next_call={"tool": "es_search", "params": {"query": p.name, "max_results": 10}},
        )

    if not p.is_file():
        return proposal_reply(
            False,
            f"不是文件: {filepath}（可能是目录）",
            error="not_a_file",
            evidence={"filepath": filepath, "resolved": str(p), "is_dir": p.is_dir()},
            options=["用 dir_list 列出目录内容"] if p.is_dir() else ["检查路径"],
        )

    # ── 守卫：文件大小 ──────────────────────────────────
    try:
        st = p.stat()
        size = st.st_size
    except OSError as e:
        return {"ok": False, "error": f"无法读取文件状态: {e}"}

    if size > SAFE_EDIT_MAX_SIZE:
        return proposal_reply(
            False,
            f"文件过大 ({human_size(size)} > {human_size(SAFE_EDIT_MAX_SIZE)})，建议分段读取",
            error="file_too_large",
            evidence={"filepath": filepath, "size": size, "size_human": human_size(size),
                      "limit": SAFE_EDIT_MAX_SIZE, "limit_human": human_size(SAFE_EDIT_MAX_SIZE)},
            options=["用 start_line/end_line 分段读取", "用 rg_search 搜索关键内容"],
            next_call={"tool": "rg_search", "params": {"pattern": "keyword", "path": str(p), "max_results": 20}},
        )

    # ── 空文件快速路径 ──────────────────────────────────
    if size == 0:
        return {
            "ok": True,
            "path": str(p),
            "total_lines": 0,
            "returned_lines": 0,
            "encoding": "utf-8",
            "size": 0,
            "size_human": "0B",
            "line_ending": "N/A",
            "content": "",
            "text": "",
            "note": "文件为空 (0 字节)",
        }

    # ── 读取 + 编码检测 ─────────────────────────────────
    raw_bytes = None
    detected_encoding = ""
    raw_text = ""

    if encoding:
        try:
            raw_text = p.read_text(encoding=encoding)
            detected_encoding = encoding
        except (UnicodeDecodeError, LookupError) as e:
            return proposal_reply(
                False,
                f"编码 {encoding} 无法解码此文件",
                error=str(e),
                evidence={"filepath": filepath, "encoding": encoding},
                options=["使用 encoding=\"\" 自动检测", "尝试 encoding=\"gbk\"", "尝试 encoding=\"latin-1\""],
            )
    else:
        # 先读原始字节做二进制检测
        try:
            raw_bytes = p.read_bytes()
        except OSError as e:
            return {"ok": False, "error": f"读取文件失败: {e}"}

        # 二进制检测
        if _is_binary(raw_bytes):
            return proposal_reply(
                False,
                f"文件似乎是二进制格式（{human_size(size)}），无法以文本方式读取",
                error="binary_file",
                evidence={"filepath": filepath, "size": size, "size_human": human_size(size)},
                options=[
                    "用 shell_exec file 命令确认文件类型",
                    "如果确实需要读取二进制内容，用 encode_decode base64",
                    "用 file_hash 计算校验值",
                ],
                next_call={"tool": "shell_exec", "params": {"cmd": f"file {filepath}", "timeout": 5}},
            )

        # 编码检测链：UTF-8 → GBK → Latin-1 (兜底)
        for enc in ("utf-8", "gbk", "latin-1"):
            try:
                raw_text = raw_bytes.decode(enc)
                detected_encoding = enc
                break
            except UnicodeDecodeError:
                continue

        if not detected_encoding:
            return {"ok": False, "error": "无法以任何已知编码解码此文件"}

    # ── 行号范围处理 ────────────────────────────────────
    all_lines = raw_text.split("\n")
    total_lines = len(all_lines)

    if start_line == 0 and end_line == 0:
        selected = all_lines
        first = 1
        last = total_lines
    elif start_line == 0 and end_line > 0:
        last = min(end_line, total_lines)
        selected = all_lines[:last]
        first = 1
    elif start_line > 0 and end_line == 0:
        first = max(1, start_line)
        selected = all_lines[first - 1:]
        last = total_lines
    else:
        first = max(1, start_line)
        last = min(end_line, total_lines)
        if first > last:
            first, last = last, first
        selected = all_lines[first - 1:last]

    returned_lines = len(selected)
    is_partial = (first != 1 or last != total_lines)

    # ── 构建带行号的 content ────────────────────────────
    # 格式对齐 Aider/Claude Code: 右对齐 6 位行号 + "|" + 行内容
    numbered: list[str] = []
    for i, line in enumerate(selected):
        numbered.append(f"{first + i:6d}|{line}")

    content_str = "\n".join(numbered)
    text_str = "\n".join(selected)
    line_ending = _detect_line_ending(raw_text)

    # ── 长文本尾部提示 ──────────────────────────────────
    note = ""
    if returned_lines > _LONG_LINE_THRESHOLD:
        note = f"返回了 {returned_lines} 行（文件共 {total_lines} 行）。建议用 start_line/end_line 分段精确读取。"
        content_str += f"\n[... 共 {returned_lines} 行，文件共 {total_lines} 行。用 start_line/end_line 分段读取 ...]"

    result: dict = {
        "ok": True,
        "path": str(p),
        "total_lines": total_lines,
        "returned_lines": returned_lines,
        "start_line": first,
        "end_line": last,
        "encoding": detected_encoding,
        "size": size,
        "size_human": human_size(size),
        "line_ending": line_ending,
        "content": content_str,
        "text": text_str,
    }
    if note:
        result["note"] = note
    if is_partial:
        result["partial"] = True

    return result
