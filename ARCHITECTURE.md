# Architecture — Irmia DevKit MCP

## Project Structure

```
irmia_devkit_mcp/
├── server.py                     # MCP entry: 65 tool registrations, FastMCP setup
├── __main__.py                   # Python entry point (`python -m irmia-devkit-mcp`)
├── pyproject.toml                # Package metadata (name: irmia-devkit-mcp, deps: mcp>=1.0.0)
├── package.json                  # npm publish config
├── bin/                          # Shell launchers (irmia-devkit.cmd / .sh)
├── tools/                        # Tool implementations (shared with upstream)
│   ├── safe_edit.py              # Backup → replace → syntax check → rollback
│   ├── safe_read.py              # Enhanced file read (encoding/hex/skeleton/head/tail)
│   ├── codegraph.py              # Semantic index + explore + call chain
│   ├── shell_exec.py             # Sandboxed command execution
│   ├── ... (60+ tool modules)
│   ├── _file_utils.py            # Shared file utilities
│   └── _helpers.py               # Shared helpers (proposal_reply, run_in_thread)
├── tests/                        # 49 pytest test files
│   ├── conftest.py               # Test fixtures
│   ├── test_safe_read.py
│   ├── test_safe_edit.py
│   └── ...
├── README.md                     # MCP-specific user guide
├── CHANGELOG.md                  # Version history (MCP + upstream sync)
└── ARCHITECTURE.md               # This file
```

## Data Flow

```
MCP Client (Cursor/Claude Desktop/...) 
    │  JSON-RPC over stdio or SSE
    ▼
server.py (FastMCP host)
    │  @mcp.tool() decorator routes to function
    ▼
tools/*.py (implementation)
    │  Returns dict → _json() → string → MCP response
    ▼
MCP Client
```

## Tool Registration Pattern

Every tool in `server.py` follows this pattern:

```python
from tools.safe_edit import edit as _safe_edit

@mcp.tool()
def safe_edit(filepath: str, old: str, new: str, ...) -> str:
    \"\"\"Docstring becomes tool description in MCP.\"\"\"
    return _json(_safe_edit(filepath, old, new, ...))
```

- All parameters are typed (MCP uses JSON Schema from type hints)
- Return is `dict` → JSON string (the MCP layer serializes it)
- Proposal protocol: on failure/ambiguity, tools return `{proposal, evidence, options, next_call}`

## Key Design Decisions

1. **Tools are thin wrappers** — `server.py` only registers and delegates. All logic lives in `tools/*.py`, shared with the upstream `irmia_devkit_open` plugin.
2. **No AstrBot dependency** — This is a standalone MCP server. The tool implementations are adapted to work without the AstrBot plugin framework.
3. **`safe_read` replaces `file_read`** — Enhanced file reading with hex/skeleton/head/tail modes, no line-number-polluted content.
4. **`proposal_reply`** — Structured error protocol guides LLM to next action instead of crashing.
5. **Local-only by design** — The MCP server refuses to bind to non-localhost addresses. `es_search`/`rg_search`/`safe_edit` etc. all operate on the local filesystem; sharing this server remotely would expose the host's file paths and operation logs. Use `stdio` mode for single-machine Vibe Coding, or `--http` (localhost-only) for local browser-based MCP clients.

## Deployment

| Mode | Command | Scope |
|------|---------|-------|
| stdio | `python server.py` | Single-machine, CLI agent |
| HTTP (local) | `python server.py --http` | `http://127.0.0.1:8000/mcp`, browser clients |
| ❌ Remote | `--host 0.0.0.0` | **Rejected** — prints error and exits |

The `--host` parameter only accepts `127.0.0.1`, `localhost`, or `::1`. This is enforced at startup. All file-system tools (`safe_edit`, `es_search`, `rg_search`, `safe_read`, etc.) operate on the machine running the server — sharing it remotely would leak host file paths and audit data.

## Dependencies

| Required | Optional |
|----------|----------|
| Python ≥ 3.10 | chardet (better encoding detection) |
| `mcp>=1.0.0` (Python SDK) | psutil (process list) |
| | tree-sitter (multi-language code index) |
| | ripgrep (fast content search) |
| | beautifulsoup4 (HTML extraction) |

## Sync Strategy with Upstream

The MCP repo periodically syncs `tools/` and `tests/` from `irmia_devkit_open`. Files specific to MCP (`server.py`, `__main__.py`, `package.json`, `bin/`) are preserved. The sync copies:
- All `tools/*.py` (implementation)
- Selected `tests/*.py` (excluding AstrBot-specific tests)
