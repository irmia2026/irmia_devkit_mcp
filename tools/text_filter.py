"""
text_filter — 行文本过滤。
head/tail/grep-like，处理已加载的文本，不依赖 shell。
"""

from ._helpers import proposal_reply


def filter_lines(
    text: str,
    action: str = "grep",
    pattern: str = "",
    n: int = 10,
    case_sensitive: bool = False,
    regex: bool = False,
) -> dict:
    """
    对文本执行行过滤操作。

    Args:
        text: 输入文本
        action: grep(匹配) / invert(反向匹配) / head(前N行) / tail(后N行) / count(统计行数)
        pattern: 匹配模式。regex=False 时用 fnmatch 通配(*?)，regex=True 时用正则
        n: head/tail 时的行数
        case_sensitive: 是否区分大小写
        regex: 是否将 pattern 视为正则表达式
    """
    lines = text.split("\n")

    if action == "head":
        result_lines = lines[:n]
        return {
            "ok": True,
            "action": "head",
            "n": n,
            "matched": len(result_lines),
            "total": len(lines),
            "result": "\n".join(result_lines),
        }

    if action == "tail":
        result_lines = lines[-n:] if n < len(lines) else lines
        return {
            "ok": True,
            "action": "tail",
            "n": n,
            "matched": len(result_lines),
            "total": len(lines),
            "result": "\n".join(result_lines),
        }

    if action == "count":
        return {
            "ok": True,
            "action": "count",
            "total": len(lines),
            "non_empty": sum(1 for l in lines if l.strip()),
        }

    if action in ("grep", "invert"):
        if regex:
            import re

            flag = 0 if case_sensitive else re.IGNORECASE
            try:
                compiled = re.compile(pattern, flag)
            except re.error as e:
                return proposal_reply(
                    False,
                    f"正则语法错误 (pos {e.pos}): {e.msg}",
                    error=f"正则语法错误: {e.msg}",
                    evidence={"pattern": pattern, "pos": e.pos},
                    options=[
                        "修正正则语法，检查未闭合的括号/方括号",
                        "切换到 regex=False 用 fnmatch 通配",
                    ],
                )
            matched = [line for line in lines if compiled.search(line)]
        else:
            import fnmatch

            matched = []
            for line in lines:
                target = line if case_sensitive else line.lower()
                pat = pattern if case_sensitive else pattern.lower()
                is_match = fnmatch.fnmatch(target, f"*{pat}*")
                if is_match:
                    matched.append(line)
        if action == "invert":
            matched_set = set(matched)
            matched = [l for l in lines if l not in matched_set]

        proposal = ""
        resp_options = None
        if len(matched) == 0 and len(lines) > 0:
            proposal = f"'{pattern}' 未匹配任何行——共 {len(lines)} 行文本"
            resp_options = [
                "尝试 regex=True",
                "放宽 pattern 为通配",
                "设 case_sensitive=false",
                "检查输入文本前几行",
            ]
        elif len(matched) > 200:
            proposal = f"结果截断 ({len(matched)}行→200行)"

        r = {
            "ok": True,
            "action": action,
            "pattern": pattern,
            "regex": regex,
            "matched": len(matched),
            "total": len(lines),
            "result": "\n".join(matched[:200]) if matched else "",
            "truncated": len(matched) > 200,
        }
        if proposal:
            r["proposal"] = proposal
        if resp_options:
            r["options"] = resp_options
        return r

    return {
        "ok": False,
        "error": f"未知 action: {action}，可选: grep/invert/head/tail/count",
    }
