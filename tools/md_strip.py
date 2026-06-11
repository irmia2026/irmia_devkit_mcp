"""
md_strip — Markdown 格式剥离。
纯 re 标准库，去除常见 Markdown 标记。
"""

import re


def strip(text: str) -> dict:
    """
    剥离 Markdown 标记，返回纯文本。

    处理: 标题(#) 粗体(**) 斜体(*) 代码块(```) 行内代码(`)
          链接 [text](url) 图片 ![alt](url) 列表(-/*) 引用(>)
          删除线(~~) 水平线(---)
    """
    original_len = len(text)

    # 代码块（多行）
    text = re.sub(r"```[\s\S]*?```", "", text)
    # 行内代码
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 图片
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # 链接
    text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # 标题
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # 粗体/斜体
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # 删除线
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    # 引用
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    # 无序列表
    text = re.sub(r"^[\-\*\+]\s+", "", text, flags=re.MULTILINE)
    # 水平线
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # 清理多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return {
        "ok": True,
        "result": text.strip(),
        "original_length": original_len,
        "stripped_length": len(text.strip()),
    }
