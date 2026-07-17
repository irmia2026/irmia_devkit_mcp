# Architecture

This document describes the internal design of `irmia_devkit_mcp`: project layout, data flow, and the decisions that shape the codebase. For usage instructions see [README.md](README.md); for contribution guidelines see [CONTRIBUTING.md](CONTRIBUTING.md).

## Project layout

```
irmia_devkit_mcp/
├── server.py                # MCP entry point: 44 tool registrations, FastMCP startup
├── __main__.py              # `python -m irmia_devkit_mcp`
├── pyproject.toml           # Python package metadata (setuptools)
├── package.json             # npm-side metadata for MCP client registries
├── bin/                     # Launcher scripts (irmia-devkit.cmd / irmia-devkit.sh)
├── tools/                   # Tool implementations (synced from irmia_devkit_open)
│   ├── safe_edit.py         # backup → replace → syntax check → rollback
│   ├── safe_read.py         # enhanced file reading (encoding / hex / skeleton)
│   ├── codegraph.py         # semantic index, symbol search, call chains
│   ├── auto_config.py       # external-tool detection + config file management
│   ├── config.py            # global configuration singleton
│   ├── _helpers.py          # proposal_reply, _run_cmd and shared helpers
│   ├── _http_utils.py       # SSRF validation shared by http_get / http_download
│   ├── _file_utils.py       # shared file utilities
│   └── ... (49 modules)
├── vendor/                  # Optional bundled binaries (rg / fd / es, per-platform)
├── tests/                   # 38 pytest files, one per tool module
├── README.md                # User documentation
├── CHANGELOG.md             # Version history (Keep a Changelog)
├── CONTRIBUTING.md          # Contributor guide
└── ARCHITECTURE.md          # This document
```

## Data flow

```
MCP client (Claude Code / Cursor / Windsurf / ...)
    │  JSON-RPC over stdio │ SSE on localhost
    ▼
server.py ── FastMCP host
    │  @mcp.tool() registration
    ▼
tools/*.py ── pure-function implementations
    │  dict result → _json() → JSON string → MCP response
    ▼
MCP client ── LLM consumes structured result
```

Tool implementations are pure functions returning plain dicts. `server.py` is a thin registration layer: it imports the functions, wraps them with `@mcp.tool()`, and serializes results. No business logic lives in the server layer.

## Design decisions

### ADR-1 — Pure functions plus a thin registration layer

**Decision.** All behavior lives in `tools/*.py` as importable functions; `server.py` only registers them with FastMCP and serializes results.

**Rationale.** Tool implementations are shared verbatim with `irmia_devkit_open`. Keeping the MCP layer a pure wrapper means upstream syncs never touch `server.py`.

### ADR-2 — Localhost-only binding

**Decision.** At startup, `--host` is validated against `{127.0.0.1, localhost, ::1}`; anything else exits with code 1.

**Rationale.** Every filesystem tool operates on the machine running the server. Binding to a routable address would expose arbitrary host paths and file contents to the network. This is enforced in code, not configuration, so it cannot be disabled by mistake.

### ADR-3 — Vendor-first binary resolution

**Decision.** External executables (`rg`, `fd`, `es`) are resolved in this order: project `vendor/` → PATH → well-known install locations. On Windows `.exe` is preferred; on POSIX systems the extensionless binary is preferred and non-executable candidates are skipped.

**Rationale.** Shipping known-good binaries in `vendor/` makes the server work offline and produces reproducible behavior across machines. PATH fallback keeps the server usable in a stock environment; the pure-Python fallbacks in `rg_search` / `es_search` keep it functional with no external tools at all.

### ADR-4 — Proposal protocol for recoverable failures

**Decision.** When a tool cannot proceed but the situation is resolvable (ambiguity, missing confirmation, oversized batch), it returns a structured proposal `{proposal, evidence, options, next_call}` instead of a bare error.

**Rationale.** The caller is an LLM. A bare `{"ok": false, "error": "..."}` gives it nothing to plan with; a structured proposal tells it exactly what to ask the user or which tool to call next. See [CONTRIBUTING.md](CONTRIBUTING.md#return-value-conventions) for the full contract.

### ADR-5 — Configuration as a layered singleton

**Decision.** `tools/config.py` holds a process-wide dict populated at startup by `tools/auto_config.py`. Precedence: environment variables → `~/.irmia/mcp_config.json` → auto-scan → defaults.

**Rationale.** Tool modules must not re-scan the filesystem on every call; a single config load at startup keeps per-call latency at zero while remaining user-overridable.

```
Startup sequence:
  1. load_config()       → read ~/.irmia/mcp_config.json
  2. scan_tools()        → detect vendor/ → PATH → well-known paths (rg / fd / es)
  3. fill empty paths    → write back to mcp_config.json when new tools are found
  4. set_config()        → inject into the global config singleton
  5. check_and_warn()    → print install guidance for missing tools
  6. print_startup_banner() → display resolved tool status
```

## Deployment modes

| Mode | Command | Transport | Scope |
|------|---------|-----------|-------|
| stdio | `python server.py` | stdin/stdout | Single agent (default for MCP clients) |
| HTTP (local) | `python server.py --http` | SSE on 127.0.0.1 | Local browser-based clients |
| Remote | `--host 0.0.0.0` | **rejected** | Blocked at startup (ADR-2) |

## Tool registration pattern

```python
@mcp.tool()
def safe_edit(filepath: str, old: str, new: str, ...) -> str:
    """Docstring → surfaced to the MCP client as the tool description.

    Args:
        ... (Args section becomes the parameter schema documentation)
    """
    result = _safe_edit(filepath, old, new, ...)
    if result.get("ok") and ...:
        _auto_index(filepath)   # best-effort semantic index refresh
    return _json(result)
```

Rules every registration follows:

- Return `str` (JSON via `_json()`), never raise.
- The implementing function lives in `tools/` and returns a plain dict.
- Side effects beyond the primary purpose (e.g. index refresh) are best-effort and must not affect the result.

## Dependencies

| Required | Optional |
|----------|----------|
| Python ≥ 3.10 | chardet — better encoding detection in `safe_read` |
| `mcp>=1.0.0` | psutil — process listing in `proc_list` |
| | tree-sitter — multi-language indexing in `code_index` |
| | ripgrep / fd / Everything CLI — accelerated search |
| | beautifulsoup4 — HTML table extraction in `html_extract` |

40+ tools run on the standard library alone. Optional dependencies degrade gracefully; nothing fails hard when they are missing.

## Testing

- 38 pytest files, one per tool module, in `tests/`.
- Shared fixtures in `tests/conftest.py`: config reset, temp directories/files, mock system calls.
- External processes (ripgrep, Everything) are exercised when present and skipped when absent; the test suite is green in both environments.

## Upstream sync strategy

`tools/` and `tests/` are synced from `irmia_devkit_open`. MCP-specific files — `server.py`, `tools/auto_config.py`, `tools/config.py` customizations, `__main__.py`, `package.json`, `bin/`, `vendor/` — are maintained in this repository only. Upstream releases that remove or rename tools require a corresponding registration change in `server.py`; everything else is a drop-in copy.
