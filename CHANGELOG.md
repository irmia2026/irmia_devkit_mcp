# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.7.0] — 2026-07-17 — Tool consolidation + bundled binaries

### Added

- **Bundled binaries (`vendor/`)**: `rg.exe` / `fd.exe` / `es.exe` (Windows) and `rg` / `fd` (Linux/macOS, musl builds) can be placed in `vendor/`; the server resolves them before PATH. Resolution is platform-aware: Windows prefers `.exe`, POSIX prefers the extensionless binary and skips non-executable candidates.
- **`fd_path` configuration**: `fd` is now a first-class entry in `~/.irmia/mcp_config.json`, alongside `es_path` and `rg_path`, with environment override via `IRMIA_FD_PATH`.

### Removed

- **Git & GitHub tool set** (12 tools): `git_status`, `git_diff`, `git_log`, `git_commit`, `git_branch`, `git_remote`, `git_push`, `git_changelog`, `gh_pr`, `gh_issue`, `gh_release`, `gh_repo`. Git operations are better served by the host agent or a dedicated Git workflow.
- **Audit tools**: `tool_stats` and `op_log`, including the in-memory counter, the SQLite audit log, and the `mcp.tool()` monkey-patch that injected auditing into every registration.
- **Text processing tools**: `csv_parse`, `csv_gen`, `md_strip`, `log_parse`.
- **Misc tools**: `project_init`, `semver_compare`.
- **Command execution**: `shell_exec`. `test_runner` retains its own inlined command allowlist (`split_command` / `validate_command`) and needs no external execution tool.
- **Related configuration**: `gh_path` and `op_log_db` removed from `mcp_config.json` and the global config singleton.

### Changed

- Tool count: 65 → **44**.
- `pyproject.toml` now declares a setuptools `build-system` and package data (`vendor/`, `bin/`), so `pip wheel` produces a complete artifact.
- README / ARCHITECTURE / CONTRIBUTING rewritten end-to-end for accuracy and consistency.

### Security

- **SSRF coverage fix**: `http_get` / `http_download` now block `0.0.0.0/8`, CGNAT (`100.64.0.0/10`), multicast (`224.0.0.0/4`) and reserved (`240.0.0.0/4`) ranges, and use `ipaddress` semantic checks (`is_private`, `is_loopback`, `is_link_local`, `is_multicast`, `is_reserved`, `is_unspecified`) in place of a hand-maintained network list. DNS-resolution results are checked with the same rules.

## [2.6.0] — 2026-06-24 — Initial MCP release

### Added

- First MCP release: 65 tools migrated from `irmia_devkit_open` v2.6.0 into a standalone FastMCP server.
- `server.py`: FastMCP host with stdio and SSE/HTTP transports, localhost-only binding enforced at startup.
- `tools/auto_config.py`: external tool auto-detection (`es` / `rg` / `gh`) with `~/.irmia/mcp_config.json` persistence and per-platform install guidance.
- `file_move`: batch move with O(1) same-partition rename and robocopy/rsync cross-partition fallback.
- Auditing via monkey-patched `mcp.tool()`: every tool invocation recorded to `tool_stats` (in-memory) and `op_log` (SQLite) with sensitive-parameter redaction.

### Changed

- Tool implementations fully synced from upstream `irmia_devkit_open` v2.6.0.
- `op_log` parameter `tool` → `tool_name` to avoid collision with the framework namespace.
- Cross-tool review fixes: CRLF/trailing-whitespace-tolerant matching, `next_call` propagation, context-size safeguards.

### Removed

- AstrBot dependency: `_auth.py` (permissions handled at the MCP layer) and AstrBot-specific tests.

---

> The following is the complete version history of upstream `irmia_devkit_open` (v1.2.0 → v2.6.0).
> The MCP edition inherited these improvements; tools removed in v2.7.0 are listed above and remain in upstream history below for reference.

## v2.6.0 (upstream) — Enhanced file reading + full security review fixes

- **New tool**: `safe_read` — enhanced safe file reading with encoding auto-detection, hex preview, head/tail, code skeleton extraction.
- **Security fixes**: SSRF IPv4 octal/hex/short-form bypass; `shell_exec` argument path validation; `file_remove` symlink-follow fix; `file_zip` symlink packing fix.
- **Performance fixes**: `safe_write` large-file preview cap; `safe_read` tail-mode optimization.
- **Bug fixes**: `safe_read` max_depth; `sys_snapshot` UnboundLocalError.

## v2.5.7 — Config page rework + release packaging

- Group config page card layout with real QQ group lists and per-group tool switches.
- GitHub PR review fix: `--body-file` to avoid shell truncation.
- Installable ZIP attached to release.

## v2.5.6 — codegraph performance fix + review hardening

- codegraph indexing from O(N×M) SQL to O(1) hash lookup (500+ file projects: >120s → 3.8s).
- codegraph P0 fix: false "empty index" from inconsistent `project_dir` paths.
- Hardening: `safe_write` path traversal, `symbol_rename` proposal protocol.

## v2.5.5 — MCP sync + security fixes + doc alignment

- Tool merges: `base64_`+`hex_`+`url_` → `encode_decode`; `time_now`+`time_convert`+`time_diff` → `time`.
- Non-core tools removed: `file_watch`, `svg_render`, `json_schema_val`, `regex_test`.
- `shell_exec` ReDoS protection, `rg_search` Python-fallback ReDoS protection, `op_log` expanded sensitive-word list.

## v2.5.0 — Testing / execution / audit / rename capabilities

- New tools: `test_runner`, `multi_edit`, `shell_exec`, `op_log`, `symbol_rename`.
- `shell_exec` seven-layer sandbox; `op_log` SQLite audit log with sensitive-parameter redaction.
- `protect_tool` wired into `op_log` auditing.

## v2.4.5 — Semantic index (5 tools) + gh_cli auto-location

- `code_index`, `code_explore`, `code_diff_impact`, `code_pack`, `code_status` released.
- Zero-dependency Python AST parsing + optional tree-sitter for other languages.
- `gh_cli` local-path hardcoding removed, full-drive auto-search.

## v2.4.0 — Code semantic index + L2 native tool removal

- `code_index` / `code_explore`: Python AST + SQLite FTS5, three-tier search (LIKE → FTS5 → hint).
- L2 native tool removal restored when devkit replacements are available.

## v2.3.7 — Tool management reclaimed + defenses

- `handler_module_path` corrected; tool management reclaimed from AstrBot.

## v2.3.6 — Group-level WebUI + handler_module_path fix

- Group-level permission configuration web panel.

## v2.3.5 — Two-layer permission defense + code review fixes

- `protect_tool` permission guard, `_auth_guard` LLM request-level filtering.
- Three review rounds fixing 18 issues.

## v2.3.0 — Foundation completion (60→61)

- `rg_search` released; whitespace-tolerant matching in `safe_edit` / `file_patch`.
- ruff ↔ pylint mutual fallback for linters; `_run_cmd()` architecture refactor.

## v2.2.0 — Unified interaction protocol

- `proposal_reply()` protocol: failure returns from 17 tools unified into the four-field structured proposal.
- 51 pytest cases.

## v2.0.0 — Ecosystem expansion (60→63)

- `tool_stats`, `db_query`, `dep_scan` released.

## v1.8 — Quality layer (59→60)

- `lint_runner` released.

## v1.7 — Decision layer (57→59)

- `project_init`, `git_changelog` released.

## v1.6 — Architecture consolidation + hardening (54→57)

- `GhCliTool` split into 4 standalone tools; registry externalized.

## v1.5 — New tools (49→54)

- `log_parse`, `file_watch`, `config_diff`, `svg_render`, `json_schema_val`.

## v1.4 — Quality polish (41→49)

- `encode_utils` split into 6 tools; `time_utils` split into 4 tools.

## v1.3 — Cross-platform (41)

- Linux fallbacks for `proc_list` / `disk_info` / `sys_snapshot`.

## v1.2.1 — Bugfix (41)

- `file_patch` encoding preservation fix.

## v1.2.0 — Initial release (42→41)

- Configuration system; 5 hardcoded paths sanitized.
