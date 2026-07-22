"""Contract tests for the public MCP tool surface."""


def test_server_version_matches_package_version():
    import json
    from pathlib import Path

    import server

    package = json.loads((Path(__file__).resolve().parents[1] / "package.json").read_text(encoding="utf-8"))
    assert server.mcp._mcp_server.version == package["version"]

def test_all_tools_publish_explicit_safety_annotations():
    import server

    tools = {tool.name: tool for tool in server.mcp._tool_manager.list_tools()}
    assert len(tools) == 44

    read_only = {
        "safe_backups", "file_preview", "syntax_check",
        "http_get", "safe_read", "es_search", "rg_search", "dir_tree",
        "dir_list", "file_diff", "file_hash", "disk_info", "config_diff",
        "port_check", "proc_list", "sys_snapshot", "html_extract",
        "json_query", "text_filter", "diff_strings", "encode_decode", "time",
        "db_query", "dep_scan", "uuid_gen",
    }
    destructive = {
        "safe_edit", "safe_rollback", "safe_write", "file_patch", "multi_edit",
        "test_runner", "http_post", "http_download", "file_zip", "file_unzip",
        "file_remove", "file_move", "symbol_rename",
    }
    open_world = {"http_get", "http_post", "http_download", "port_check"}

    assert {name for name, tool in tools.items() if tool.annotations.readOnlyHint} == read_only
    assert tools["lint_runner"].annotations.readOnlyHint is False
    assert {name for name, tool in tools.items() if tool.annotations.destructiveHint} == destructive
    assert {name for name, tool in tools.items() if tool.annotations.openWorldHint} == open_world

    non_destructive_writers = {
        "code_index", "code_explore", "code_pack", "code_diff_impact", "code_status", "lint_runner",
    }
    assert {
        name for name, tool in tools.items()
        if tool.annotations.readOnlyHint is False and tool.annotations.destructiveHint is False
    } == non_destructive_writers

    for tool in tools.values():
        annotations = tool.annotations
        assert annotations.readOnlyHint is not None
        assert annotations.destructiveHint is not None
        assert annotations.idempotentHint is not None
        assert annotations.openWorldHint is not None
