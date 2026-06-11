"""
semver — 语义版本号比较。
纯 Python，无依赖。
"""

import re


def compare(v1: str, v2: str) -> dict:
    """
    比较两个语义版本号。

    Args:
        v1, v2: 版本字符串，如 "1.2.3" "2.0.0-beta.1"

    Returns:
        含 result: ">" / "<" / "="，以及解析后的各段
    """
    p1 = _parse(v1)
    p2 = _parse(v2)

    if p1 is None or p2 is None:
        return {"ok": False, "error": "版本号格式无效"}

    if p1 > p2:
        result = ">"
    elif p1 < p2:
        result = "<"
    else:
        result = "="

    return {
        "ok": True,
        "v1": v1,
        "v2": v2,
        "result": result,
        "v1_parsed": _fmt_parsed(p1),
        "v2_parsed": _fmt_parsed(p2),
    }


def _fmt_parsed(p: tuple) -> dict:
    return {
        "major": p[0], "minor": p[1], "patch": p[2],
        "pre": [x for x in p[3] if x != chr(127)] or None,
    }


def _parse(v: str) -> tuple | None:
    """解析 semver 为可比较元组。H7: 数字预发布字段按数值比较。"""
    v = v.strip().lstrip("v")
    # H7: 剥离 build metadata (+xxx)，不影响优先级
    build_split = v.split("+", 1)
    v = build_split[0]

    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$", v)
    if not m:
        # 尝试容忍只有 major.minor
        m = re.match(r"^(\d+)\.(\d+)$", v)
        if not m:
            return None
        return (int(m.group(1)), int(m.group(2)), 0, (chr(127),))

    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    pre_raw = m.group(4) or ""
    # H7: 拆分预发布为点分隔字段，纯数字字段转 int，字母字段保持 str
    if pre_raw:
        pre_parts = []
        for field in pre_raw.split("."):
            if field.isdigit():
                pre_parts.append(int(field))
            else:
                pre_parts.append(field)
        pre = tuple(pre_parts)
    else:
        # 正式版应排在任何预发布之后，用 DEL(127) 哨兵
        pre = (chr(127),)
    return (major, minor, patch, pre)
