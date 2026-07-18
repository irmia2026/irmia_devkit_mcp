"""
Irmia DevKit MCP Server — 为 Vibe Coding 工具提供安全代码开发工具集。
启动: python server.py  或  mcp run server.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

from tools import config as _cfg
from tools.auto_config import load_config, check_and_warn, print_startup_banner

_mcp_config = load_config()
check_and_warn(_mcp_config)

_cfg.set_config(
    {
        "backup_dir": os.environ.get("IRMIA_BACKUP_DIR", _mcp_config.get("backup_dir", str(Path.home() / ".irmia" / "backups"))),
        "es_path": os.environ.get("IRMIA_ES_PATH", _mcp_config.get("es_path", "")),
        "rg_path": os.environ.get("IRMIA_RG_PATH", _mcp_config.get("rg_path", "")),
        "fd_path": os.environ.get("IRMIA_FD_PATH", _mcp_config.get("fd_path", "")),
        "state_dir": "",
        "lock_dirs": [],
    },
    plugin_dir=str(Path(__file__).resolve().parent),
)

# ── 导入工具函数 ──────────────────────────────────────
from tools.safe_edit import edit as _safe_edit, list_backups as _safe_backups, rollback as _safe_rollback
from tools.safe_write import write as _safe_write
from tools.file_patch import patch as _file_patch, preview as _file_preview
from tools.multi_edit import run as _multi_edit
from tools.syntax_check import check as _syntax_check
from tools.lint_runner import run as _lint_runner
from tools.test_runner import run as _test_runner
from tools.http_get import get as _http_get, post as _http_post
from tools.http_download import download as _http_download
from tools.rg_search import search as _rg_search
from tools.codegraph import CodeGraph
from tools.symbol_rename import run as _symbol_rename
from tools.dep_scan import scan as _dep_scan
from tools.db_query import query as _db_query
from tools.file_remove import remove as _file_remove, move as _file_move
from tools.file_diff import compare as _file_diff
from tools.safe_read import read as _safe_read
from tools.es_search import search as _es_search
from tools.file_hash import compute as _file_hash
from tools.file_zip import compress as _file_zip, extract as _file_unzip
from tools.dir_tree import tree as _dir_tree
from tools.dir_list import list_dir as _dir_list
from tools.html_extract import extract as _html_extract
from tools.json_query import query as _json_query
from tools.text_filter import filter_lines as _text_filter
from tools.diff_strings import diff as _diff_strings
from tools.encode_utils import (
    b64_encode as _b64_encode, b64_decode as _b64_decode,
    url_encode as _url_encode, url_decode as _url_decode,
    hex_encode as _hex_encode, hex_decode as _hex_decode,
)  # used by encode_decode tool
from tools.time_utils import now as _time_now, ts_to_iso as _ts_to_iso, iso_to_ts as _iso_to_ts, time_diff as _time_diff  # used by time tool
from tools.port_check import check as _port_check, scan as _port_scan
from tools.uuid_gen import gen as _uuid_gen
from tools.config_diff import diff as _config_diff
from tools.proc_list import list_processes as _proc_list
from tools.sys_snapshot import snapshot as _sys_snapshot
from tools.disk_info import info as _disk_info

mcp = FastMCP(
    "irmia-devkit",
    instructions="弥亚开发工具箱 MCP — 安全代码编辑、搜索、测试、代码智能、网络、文件、编码、时间、文本处理、系统信息。为仅有 shell 的 bare agent 提供全面且安全的开发工具集。",
)


def _json(result: dict) -> str:
    return json.dumps(result, ensure_ascii=False)




# ═══════════════════════════════════════════════════════
# 🔒 安全编辑链 (10)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def safe_edit(filepath: str, old: str, new: str, replace_all: bool = False, occurrence: int = 0) -> str:
    """安全编辑文件：自动备份→替换→语法检查→通过保留/失败回滚。
    修改任何代码文件必须使用此工具，内置 whitespace 容错对齐。多处匹配时返回所有位置供消歧。

    Args:
        filepath: 文件路径
        old: 旧文本（精确匹配，允许缩进容错）
        new: 新文本
        replace_all: 是否替换所有匹配
        occurrence: 替换第 N 次出现（多匹配消歧用，0=首次）
    """
    result = _safe_edit(filepath, old, new, replace_all=replace_all, occurrence=occurrence)
    if result.get("ok") and result.get("syntax_ok") is not False and filepath.endswith((".py", ".go", ".rs", ".js", ".ts")):
        _auto_index(filepath)
    return _json(result)


@mcp.tool()
def safe_backups(filepath: str = "") -> str:
    """列出某个文件的所有备份。不传 filepath 列出全部备份。

    Args:
        filepath: 文件路径，空字符串=列出全部备份
    """
    return _json(_safe_backups(filepath or None))


@mcp.tool()
def safe_rollback(filepath: str, backup_name: str = "") -> str:
    """回滚文件到指定备份。不传 backup_name 回滚到最近一次备份。

    Args:
        filepath: 文件路径
        backup_name: 备份文件名，空字符串=最近一次
    """
    return _json(_safe_rollback(filepath, backup_name or None))


@mcp.tool()
def safe_write(filepath: str, content: str, overwrite: bool = False) -> str:
    """新建文件或整体覆盖（safe_edit 的姊妹工具）。新建首选，自动创建父目录。

    新建文件：写入后语法检查，失败不阻塞——新文件无旧版本可回滚，文件保留+修正建议。
    已存在且 overwrite=false（默认）：不写入，返回 proposal 引导用 safe_edit 或 overwrite=true。
    overwrite=true：先备份，语法检查失败自动回滚到覆盖前内容。

    Args:
        filepath: 目标文件路径。父目录不存在自动创建。
        content: 完整文件内容（文本，UTF-8）。
        overwrite: 已存在时是否覆盖。默认 false——返回 proposal 而不写入。
    """
    return _json(_safe_write(filepath, content, overwrite=overwrite))


@mcp.tool()
def file_patch(filepath: str, old: str, new: str, replace_all: bool = False) -> str:
    """精确文本替换（非代码文件用）。自带 whitespace 对齐容错。

    Args:
        filepath: 文件路径
        old: 旧文本
        new: 新文本
        replace_all: 是否替换所有匹配
    """
    return _json(_file_patch(filepath, old, new, replace_all=replace_all))


@mcp.tool()
def file_preview(filepath: str, old: str, new: str, replace_all: bool = False) -> str:
    """预览 file_patch 的替换效果（dry-run diff），不实际修改文件。

    Args:
        filepath: 文件路径
        old: 旧文本
        new: 新文本
        replace_all: 是否替换所有匹配
    """
    return _json(_file_preview(filepath, old, new, replace_all=replace_all))


@mcp.tool()
def multi_edit(edits: list, syntax_check: bool = True) -> str:
    """跨文件原子编辑：所有编辑在内存中完成，全成功才一次写入磁盘。任一文件写入失败 → 全量回滚所有文件。

    Args:
        edits: 编辑列表，每项 {"file": "...", "old": "...", "new": "...", "replace_all": false, "occurrence": 0}
        syntax_check: 是否对代码文件执行语法检查
    """
    return _json(_multi_edit(edits, syntax_check=syntax_check))


@mcp.tool()
def syntax_check(filepath: str) -> str:
    """检查文件语法。支持 Python / Go / Nim / JavaScript / TypeScript。

    Args:
        filepath: 文件路径
    """
    return _json(_syntax_check(filepath))


@mcp.tool()
def lint_runner(filepath: str, linter: str = "auto") -> str:
    """运行代码质量检查。自动 fallback: ruff → pylint → eslint。

    Args:
        filepath: 文件路径
        linter: linter 名称，auto=自动选择
    """
    return _json(_lint_runner(filepath, linter=linter))


@mcp.tool()
def test_runner(project_dir: str = ".", test_cmd: str = "", timeout: int = 120, filepath: str = "") -> str:
    """统一测试运行器。自动检测框架并运行。

    支持: pytest (Python), go test (Go), cargo test (Rust), jest/npm test (JS/TS)

    Args:
        project_dir: 项目目录
        test_cmd: 自定义测试命令，空=自动检测
        timeout: 超时秒数
        filepath: 限定测试文件，空=全部
    """
    return _json(_test_runner(filepath=filepath or "", project_dir=project_dir, test_cmd=test_cmd, timeout=timeout))


# ═══════════════════════════════════════════════════════
# 🌐 网络 (3)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def http_get(url: str, headers: dict = None, timeout: int = 10) -> str:
    """HTTP GET 请求 (SSRF 四层防护).

    Args:
        url: 请求 URL
        headers: 请求头字典
        timeout: 超时秒数
    """
    result = _http_get(url, headers=headers, timeout=timeout)
    if not result.get("ok") and isinstance(result.get("status"), int) and result["status"] > 0:
        result.setdefault("proposal", f"HTTP {result['status']}: request failed, check URL or retry")
        result.setdefault("options", ["check URL", "try http_post as alternative", "check network"])
    elif not result.get("ok") and "proposal" not in result:
        result.setdefault("proposal", "request failed; check URL validity and network connection")
    return _json(result)


@mcp.tool()
def http_post(url: str, data: str = "", headers: dict = None, timeout: int = 10) -> str:
    """HTTP POST 请求 (SSRF 防护). 多数 MCP 客户端只能 GET.

    Args:
        url: 请求 URL
        data: 请求体 JSON 字符串
        headers: 请求头字典
        timeout: 超时秒数
    """
    parsed = None
    if data:
        try:
            parsed = json.loads(data)
        except Exception:
            parsed = data
    result = _http_post(url, data=parsed, headers=headers, timeout=timeout)
    if not result.get("ok") and isinstance(result.get("status"), int) and result["status"] > 0:
        result.setdefault("proposal", f"HTTP {result['status']}: POST failed")
        result.setdefault("options", ["check URL and data format", "try http_get to verify endpoint", "check headers"])
    elif not result.get("ok") and "proposal" not in result:
        result.setdefault("proposal", "POST request failed; check URL and network")
    return _json(result)


@mcp.tool()
def http_download(url: str, path: str, overwrite: bool = False, timeout: int = 60) -> str:
    """下载文件到指定路径 (SSRF + 路径沙箱 + 500MB上限).

    Args:
        url: 下载 URL
        path: 保存路径
        overwrite: 是否覆盖已存在文件
        timeout: 超时秒数
    """
    result = _http_download(url, path, overwrite=overwrite, timeout=timeout)
    if not result.get("ok") and result.get("error") == "file_exists":
        result.setdefault("proposal", "文件已存在，如需覆盖请设置 overwrite=true")
        result.setdefault("options", ["overwrite=true", "更换 path", "取消"])
    elif not result.get("ok"):
        result.setdefault("proposal", "下载失败，检查 URL 和网络")
    return _json(result)


# ═══════════════════════════════════════════════════════
# 📁 文件系统 (13)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def safe_read(
    path: str,
    start_line: int = 0,
    end_line: int = 0,
    max_lines: int = 0,
    offset: int = 0,
    limit_bytes: int = 0,
    encoding: str = "auto",
    mode: str = "auto",
    head: int = 0,
    tail: int = 0,
    include_metadata: bool = True,
) -> str:
    """增强版安全文件读取：编码自动检测、二进制/hex、head/tail、行号范围、代码骨架。
    替代旧版 file_read，编辑前必调。

    Args:
        path: 文件路径
        start_line: 起始行号（1-based，0=从头）
        end_line: 结束行号（1-based，0=到尾）
        max_lines: 最大返回行数（0=使用工具内部默认值）
        offset: 字节偏移（hex 模式）
        limit_bytes: 字节限制（hex 模式）
        encoding: 编码：auto / utf-8 / gbk / latin-1
        mode: 模式：auto / text / binary / hex / skeleton
        head: 读取前 N 行（优先级高于 start_line/end_line）
        tail: 读取后 N 行（优先级高于 start_line/end_line）
        include_metadata: 是否包含文件元信息
    """
    kwargs = {"path": path, "start_line": start_line, "end_line": end_line, "encoding": encoding,
              "mode": mode, "head": head, "tail": tail, "include_metadata": include_metadata}
    if max_lines > 0:
        kwargs["max_lines"] = max_lines
    if offset > 0:
        kwargs["offset"] = offset
    if limit_bytes > 0:
        kwargs["limit_bytes"] = limit_bytes
    return _json(_safe_read(**kwargs))


@mcp.tool()
def es_search(query: str, path: str = "", max_results: int = 100, regex: bool = False, case_sensitive: bool = False, whole_word: bool = False, file_type: str = "all", sort_by: str = "", ext: str = "") -> str:
    """毫秒级文件名搜索。Everything (Win) → locate → fd → Python os.walk 四层 fallback，零依赖也能工作。

    Args:
        query: 搜索关键词，支持 * ? 通配符
        path: 限定搜索路径，空=全盘/全项目
        max_results: 最大结果数
        regex: 使用正则表达式
        case_sensitive: 区分大小写
        whole_word: 全词匹配
        file_type: file | folder | all
        sort_by: name | path | size | ext | date_modified
        ext: 扩展名过滤，如 "py" "js"
    """
    return _json(_es_search(query=query, path=path or None, max_results=max_results, regex=regex, case_sensitive=case_sensitive, whole_word=whole_word, file_type=file_type, sort_by=sort_by or None, ext=ext or None))


@mcp.tool()
def rg_search(pattern: str, path: str = ".", file_exts: str = "", case_sensitive: bool = False, whole_word: bool = False, list_files: bool = False, context_lines: int = 0, max_results: int = 40) -> str:
    """文件内容搜索（ripgrep 优先，自动 Python fallback）。

    Args:
        pattern: 搜索模式（正则或纯文本）
        path: 搜索路径
        file_exts: 逗号分隔扩展名，如 "py,js,go"（不要带点）
        case_sensitive: 区分大小写，默认忽略
        whole_word: 全词匹配
        list_files: 仅返回文件名
        context_lines: 上下文行数
        max_results: 最大结果数
    """
    return _json(_rg_search(pattern=pattern, path=path, file_exts=file_exts, case_sensitive=case_sensitive, whole_word=whole_word, list_files=list_files, context_lines=context_lines, max_results=max_results))


@mcp.tool()
def dir_tree(path: str = ".", max_depth: int = 3, show_hidden: bool = False, pattern: str = "", max_items: int = 100) -> str:
    """可视化目录树。bare agent 的 ls/find 替代。

    Args:
        path: 目录路径
        max_depth: 最大深度
        show_hidden: 是否显示隐藏文件
        pattern: glob 过滤
        max_items: 最大条目数
    """
    return _json(_dir_tree(path=path, max_depth=max_depth, show_hidden=show_hidden, pattern=pattern, max_items=max_items))


@mcp.tool()
def dir_list(path: str = ".", pattern: str = "*", max_depth: int = 1, show_hidden: bool = False) -> str:
    """结构化目录列表，返回 {name, type, size, modified}。

    Args:
        path: 目录路径
        pattern: glob 过滤
        max_depth: 最大深度
        show_hidden: 是否显示隐藏文件
    """
    return _json(_dir_list(path=path, pattern=pattern, max_depth=max_depth, show_hidden=show_hidden))


@mcp.tool()
def file_diff(file1: str, file2: str) -> str:
    """两个文件的 unified diff 比较。

    Args:
        file1: 第一个文件路径
        file2: 第二个文件路径
    """
    result = _file_diff(file1, file2)
    if not result.get("ok"):
        result.setdefault("proposal", "diff 失败：检查文件是否存在且可读")
    return _json(result)


@mcp.tool()
def file_hash(filepath: str, algo: str = "sha256") -> str:
    """计算文件哈希 (MD5/SHA1/SHA256). 无终端的 agent 无法用命令行。

    Args:
        filepath: 文件路径
        algo: md5 | sha1 | sha256
    """
    return _json(_file_hash(filepath, algo=algo))


@mcp.tool()
def file_zip(source: str, output: str = "") -> str:
    """ZIP 压缩。压缩目录或文件到 output zip。

    Args:
        source: 要压缩的文件或目录路径
        output: 输出 zip 路径，空则使用 source + ".zip"
    """
    if not output:
        output = f"{source}.zip"
    return _json(_file_zip(files_or_dir=[source], output=output))


@mcp.tool()
def file_unzip(zip_file: str, output_dir: str = "") -> str:
    """ZIP 解压（Zip-slip 防护）。output_dir 空则解压到 zip 文件所在目录。

    Args:
        zip_file: zip 文件路径
        output_dir: 解压目标目录
    """
    if not output_dir:
        output_dir = str(Path(zip_file).parent)
    return _json(_file_unzip(zip_file=zip_file, output_dir=output_dir))


@mcp.tool()
def file_remove(path: str, confirm: bool = False, max_items: int = 50) -> str:
    """安全删除文件或目录（路径穿越防护 + 系统目录黑名单）。

    Args:
        path: 要删除的路径
        confirm: 必须显式设为 True 才执行
        max_items: 最大删除文件数
    """
    return _json(_file_remove(path, confirm=confirm, max_items=max_items))


@mcp.tool()
def file_move(sources: list, dest: str, overwrite: bool = False) -> str:
    """批量移动文件/目录到目标目录。
    同分区内原子 rename（O(1)），跨分区自动退化为 copy+delete。

    Args:
        sources: 源文件/目录路径列表
        dest: 目标目录路径（会自动创建）
        overwrite: 是否覆盖目标已存在的文件
    """
    return _json(_file_move(sources, dest, overwrite=overwrite))


@mcp.tool()
def disk_info() -> str:
    """获取磁盘分区使用情况。"""
    return _json(_disk_info())


@mcp.tool()
def config_diff(file1: str, file2: str) -> str:
    """配置文件 key 级差异比较 (JSON/YAML)。

    Args:
        file1: 第一个配置文件
        file2: 第二个配置文件
    """
    return _json(_config_diff(file_a=file1, file_b=file2))


# ═══════════════════════════════════════════════════════
# 🤖 代码智能 (6)
# ═══════════════════════════════════════════════════════

_codegraph_instances: dict = {}

_CODEGRAPH_TTL = 300  # 5 分钟连接缓存

def _get_codegraph(project_dir: str = ".") -> CodeGraph:
    cwd = str(Path(project_dir).resolve())
    entry = _codegraph_instances.get(cwd)
    now = __import__("time").monotonic()
    if entry and (now - entry["ts"] < _CODEGRAPH_TTL):
        return entry["cg"]
    db_path = os.path.join(cwd, ".codegraph", "codegraph.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    cg = CodeGraph(db_path)
    _codegraph_instances[cwd] = {"cg": cg, "ts": now}
    return cg


def _auto_index(filepath: str) -> None:
    """safe_edit 成功后自动增量索引，维持实时性。best-effort，失败静默。"""
    try:
        parent = str(Path(filepath).resolve().parent)
        cg = _get_codegraph(parent)
        cg.index(project_dir=parent, incremental=True)
    except Exception:
        pass  # 索引失败不影响编辑流程


@mcp.tool()
def code_index(project_dir: str = ".", incremental: bool = False) -> str:
    """建立项目语义索引。首次进项目调用，后续增量更新。
    支持: Python (ast, 零依赖) / Go/Rust/JS/TS/C/C++/Java (tree-sitter, 可选)

    Args:
        project_dir: 项目目录
        incremental: True=增量索引（仅扫描变更文件）
    """
    return _json(_get_codegraph(project_dir).index(project_dir=project_dir, incremental=incremental))


@mcp.tool()
def code_explore(query: str, project_dir: str = ".") -> str:
    """探索代码库：查符号定义、调用链、路径追踪。
    查询语法: "X 在哪定义" → 符号搜索, "谁调用了 X" → 调用链, "X → Y" → BFS路径

    Args:
        query: 自然语言或符号查询
        project_dir: 项目目录
    """
    return _json(_get_codegraph(project_dir).explore(query, project_dir=project_dir))


@mcp.tool()
def code_pack(target: str, depth: int = 2, mode: str = "both", project_dir: str = ".") -> str:
    """精准上下文打包：收集符号及其调用链的完整源码。

    Args:
        target: 目标符号名
        depth: 调用链深度（1=仅自身，2=含直接调用者，3=两层调用者）
        mode: callers=仅调用者 | callees=仅被调用者 | both=双向
        project_dir: 项目目录
    """
    return _json(_get_codegraph(project_dir).code_pack(target, depth=depth, mode=mode))


@mcp.tool()
def code_diff_impact(filepaths: list, max_depth: int = 3, project_dir: str = ".") -> str:
    """变更影响分析：分析修改文件会波及哪些调用者。

    Args:
        filepaths: 变更的文件路径列表
        max_depth: 最大追溯深度
        project_dir: 项目目录
    """
    return _json(_get_codegraph(project_dir).code_diff_impact(filepaths, max_depth=max_depth))


@mcp.tool()
def code_status(project_dir: str = ".") -> str:
    """索引健康检查：覆盖范围、符号数、边数、最后索引时间。explore 查不到时先查这个。

    Args:
        project_dir: 项目目录
    """
    return _json(_get_codegraph(project_dir).code_status())


@mcp.tool()
def symbol_rename(old_name: str, new_name: str, project_dir: str = ".", dry_run: bool = True, confirm_multi_file: bool = False) -> str:
    """Python 符号重命名（tokenize 级别，跳过注释和字符串中的同名标识符）。

    Args:
        old_name: 旧符号名
        new_name: 新符号名（必须是合法 Python 标识符）
        project_dir: 项目目录
        dry_run: True=仅预览 diff 不实际执行
        confirm_multi_file: 跨文件重命名需显式设为 True
    """
    return _json(_symbol_rename(old=old_name, new=new_name, project_dir=project_dir, dry_run=dry_run, confirm_multi_file=confirm_multi_file))


# ═══════════════════════════════════════════════════════
# 📊 系统信息 (3)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def port_check(action: str = "check", host: str = "127.0.0.1", port: int = 7860, ports: list = None) -> str:
    """端口检测/扫描。

    Args:
        action: check (单端口) | scan (批量)
        host: 目标主机
        port: 单端口号（check 用）
        ports: 端口列表（scan 用）
    """
    if action == "scan" and ports:
        return _json(_port_scan(ports=ports, host=host))
    return _json(_port_check(host=host, port=port))


@mcp.tool()
def proc_list(filter_name: str = "") -> str:
    """列出系统进程。可通过 filter_name 按名称模糊过滤。

    Args:
        filter_name: 进程名过滤子串，空=全部
    """
    return _json(_proc_list(filter_name=filter_name or None))


@mcp.tool()
def sys_snapshot() -> str:
    """获取系统快照：CPU/内存/进程/开机时间等。"""
    return _json(_sys_snapshot())


# ═══════════════════════════════════════════════════════
# 📝 文本处理 (4)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def html_extract(html: str, what: str = "text", selector: str = "") -> str:
    """HTML → 纯文本/链接/表格。配合 http_get 做 web scraping。

    Args:
        html: HTML 内容
        what: text | links | tables
        selector: CSS 选择器，空=全文
    """
    return _json(_html_extract(html=html, what=what, selector=selector))


@mcp.tool()
def json_query(data: str, path: str) -> str:
    """jq 风格 JSON 路径查询。bare agent 没有 jq。

    Args:
        data: JSON 字符串
        path: 查询路径，如 "users[0].name" 或 "items[*].id"
    """
    return _json(_json_query(data=data, path=path))


@mcp.tool()
def text_filter(text: str, action: str = "grep", pattern: str = "", n: int = 10, case_sensitive: bool = False, regex: bool = False) -> str:
    """行过滤：grep/head/tail/count。bare agent 的 grep/head/tail 替代。

    Args:
        text: 输入文本
        action: grep | head | tail | count | invert
        pattern: 过滤模式（grep/invert 用）
        n: 行数（head/tail 用）
        case_sensitive: 区分大小写
        regex: pattern 是否正则
    """
    return _json(_text_filter(text=text, action=action, pattern=pattern, n=n, case_sensitive=case_sensitive, regex=regex))


@mcp.tool()
def diff_strings(a: str, b: str, context_lines: int = 3) -> str:
    """两个字符串的 unified diff。

    Args:
        a: 字符串 A
        b: 字符串 B
        context_lines: 上下文行数
    """
    return _json(_diff_strings(a=a, b=b, context_lines=context_lines))


# ═══════════════════════════════════════════════════════
# 🔤 编码
# ═══════════════════════════════════════════════════════

@mcp.tool()
def encode_decode(action: str, format: str = "base64", data: str = "", as_uri: bool = False) -> str:
    """编解码：支持 base64 / url / hex。bare agent 没有这些命令。

    Args:
        action: encode | decode
        format: base64 | url | hex
        data: 输入字符串
        as_uri: (仅 base64) encode 时使用 URI safe 模式
    """
    fmt = format.lower()
    if fmt == "base64":
        if action == "encode": return _json(_b64_encode(data=data, as_uri=as_uri))
        elif action == "decode": return _json(_b64_decode(data=data, strip_uri=as_uri))
    elif fmt == "url":
        if action == "encode": return _json(_url_encode(data=data))
        elif action == "decode": return _json(_url_decode(data=data))
    elif fmt == "hex":
        if action == "encode": return _json(_hex_encode(data=data))
        elif action == "decode": return _json(_hex_decode(data=data))
    else:
        return _json({"ok": False, "error": f"unknown format: {format}, use base64/url/hex"})
    return _json({"ok": False, "error": f"unknown action: {action}, use encode/decode"})


# ═══════════════════════════════════════════════════════
# ⏱ 时间
# ═══════════════════════════════════════════════════════

@mcp.tool()
def time(action: str = "now", value: str = "", ts: int = 0, ms: bool = False, iso1: str = "", iso2: str = "") -> str:
    """时间工具。bare agent 不知道现在几点。

    Args:
        action: now (当前时间) | convert (时间戳↔ISO互转) | diff (两ISO时间差)
        value: ISO 时间字符串 (action=convert, →时间戳)
        ts: Unix 时间戳 (action=convert, →ISO)
        ms: 是否为毫秒时间戳
        iso1: 第一个 ISO 时间 (action=diff)
        iso2: 第二个 ISO 时间 (action=diff)
    """
    if action == "now":
        return _json(_time_now())
    elif action == "convert":
        if value: return _json(_iso_to_ts(iso=value))
        return _json(_ts_to_iso(ts=ts, ms=ms))
    elif action == "diff":
        return _json(_time_diff(iso1=iso1, iso2=iso2))
    return _json({"ok": False, "error": f"unknown action: {action}, use now/convert/diff"})


# ═══════════════════════════════════════════════════════
# 🧩 扩展 (3)
# ═══════════════════════════════════════════════════════

@mcp.tool()
def db_query(db_path: str, sql: str, params: list = None) -> str:
    """只读 SQLite 查询（仅允许 SELECT/PRAGMA，参数化查询防注入）。

    Args:
        db_path: SQLite 数据库路径
        sql: SQL 查询语句（仅 SELECT 或 PRAGMA）
        params: 查询参数列表
    """
    return _json(_db_query(db_path, sql, params=params or []))


@mcp.tool()
def dep_scan(project_dir: str = ".", timeout: int = 10) -> str:
    """Python 依赖扫描：构建依赖图并检测循环依赖。

    Args:
        project_dir: 项目目录
        timeout: 超时秒数
    """
    return _json(_dep_scan(project_dir=project_dir, timeout=timeout))


@mcp.tool()
def uuid_gen(kind: str = "uuid4", length: int = 16) -> str:
    """生成 UUID4 / 随机 hex / 随机 token。

    Args:
        kind: uuid4 | hex | token
        length: hex/token 的长度
    """
    return _json(_uuid_gen(kind=kind, length=length))


# ═══════════════════════════════════════════════════════
# 启动入口
# ═══════════════════════════════════════════════════════

def main():
    """MCP 入口。默认 stdio；传 --http 则启动 HTTP 服务。"""
    import argparse

    ap = argparse.ArgumentParser(description="Irmia DevKit MCP Server")
    ap.add_argument("--http", action="store_true", help="以 HTTP streamable 模式启动 (默认 stdio)")
    ap.add_argument("--port", type=int, default=8000, help="HTTP 端口 (默认 8000)")
    ap.add_argument("--host", default="127.0.0.1", help="监听地址 (默认 127.0.0.1)")
    args = ap.parse_args()

    if args.http:
        print_startup_banner(_mcp_config, quiet=False)
        if args.host not in ("127.0.0.1", "localhost", "::1"):
            print(
                f"❌ irmia-devkit-mcp 仅支持本地部署。"
                f"不允许 --host={args.host}（仅允许 127.0.0.1 / localhost / ::1）。",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Irmia DevKit MCP HTTP -> http://{args.host}:{args.port}/mcp  (本地专用)", file=sys.stderr)
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        # stdio 模式：stdout 只传 JSON-RPC，横幅静默（诊断信息一律走 stderr）
        print_startup_banner(_mcp_config, quiet=True)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
