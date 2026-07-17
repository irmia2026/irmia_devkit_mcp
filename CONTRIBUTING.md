# Contributing

This guide covers everything needed to add a tool, fix a bug, or prepare a release. For architecture context see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development setup

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
pip install -e .
pip install pytest
```

Run the suite:

```bash
pytest tests/ -v
```

The suite is green with and without the optional external binaries (ripgrep, fd, Everything CLI). Tests that need them skip automatically.

## Adding a tool

### 1. Create the implementation module

Every tool is a pure function in `tools/` that returns a dict and never raises:

```python
# tools/my_tool.py
from __future__ import annotations
from ._helpers import proposal_reply

def do_something(param: str) -> dict:
    if not param:
        return {"ok": False, "error": "param must not be empty"}

    if ambiguous:
        return proposal_reply(
            False,
            "Multiple candidates found — pick one",
            evidence={"candidates": 3},
            options=["candidate A", "candidate B"],
        )

    return {"ok": True, "result": f"processed: {param}"}
```

### 2. Register it in `server.py`

```python
from tools.my_tool import do_something as _do_something

@mcp.tool()
def my_action(param: str) -> str:
    """One sentence telling the agent when to call this tool.

    Args:
        param: What this parameter controls
    """
    return _json(_do_something(param))
```

The docstring is the tool's public contract: the first paragraph becomes the description shown to the agent, and the `Args:` section documents the schema. Keep it accurate — the LLM reads it verbatim.

### 3. Add tests

Create `tests/test_my_tool.py` following the existing per-module pattern. Use the fixtures from `tests/conftest.py` (`tmp_dir`, `tmp_py_file`, `project_dir`, …) rather than writing ad-hoc temp files.

### 4. Update documentation

- Add the tool to the overview table in [README.md](README.md).
- Note the addition in [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]`.

## Return-value conventions

Every tool result is a dict matching one of three shapes:

| Shape | Condition | Example |
|-------|-----------|---------|
| Success | `ok=True`, no special keys | `{"ok": True, "result": "..."}` |
| Error | `ok=False`, no special keys | `{"ok": False, "error": "cannot read file"}` |
| Proposal | contains any of `proposal`, `options`, `evidence`, `next_call` | `{"ok": False, "proposal": "...", "options": [...]}` |

Rules:

- **Never raise.** Return the error as a dict, from the tool function and from every helper it calls.
- `proposal` and `options` always appear together; include `evidence` whenever there is concrete data to show.
- `next_call` has the form `{"tool": "tool_name", "params": {...}}` when the fix is a different tool invocation.
- Destructive operations (deletion, overwrite, anything irreversible) use a two-phase pattern: first call returns `ok=False` with a proposal, the agent must re-call with an explicit confirmation parameter (`confirm=true`, `overwrite=true`, …).

## Security checklist

| Concern | Where | Mechanism |
|---------|-------|-----------|
| SSRF | `tools/_http_utils.py` | scheme allowlist → IP-range blocklist (`ipaddress.is_private` et al.) → DNS-resolution re-check → per-redirect re-check |
| Path traversal | `tools/file_remove.py`, `tools/safe_edit.py`, … | `..` segment rejection + `resolve()` prefix validation + system-directory blocklist |
| ZIP slip | `tools/file_zip.py` | per-entry `resolve()` prefix check against the target directory |
| SQL injection | `tools/db_query.py` | SELECT/PRAGMA allowlist, read-only mode, parameterized queries |
| Command injection | `tools/test_runner.py` | allowlisted executables/subcommands, shell-control-character rejection, `shell=False` |
| Binary hijacking | `tools/auto_config.py` | `vendor/` path derived from `__file__`, never from the working directory |

When you touch any of these files, extend the corresponding tests rather than weakening a check to make a test pass.

## Dependency policy

The standard library is the default. Before adding a third-party dependency:

1. Check whether the dependency is optional and degrades gracefully (like `psutil` or `beautifulsoup4`).
2. If it is required, discuss first — `mcp` is currently the only required dependency.
3. External executables must be resolvable through `tools/auto_config.py` and must have a pure-Python fallback path.

## Release checklist

- [ ] `pytest tests/ -q` — fully green
- [ ] `python server.py` — starts on stdio, banner shows resolved tools
- [ ] `python server.py --http` — starts SSE on 127.0.0.1
- [ ] Tool count in README table matches `@mcp.tool()` registrations in `server.py`
- [ ] Version bumped consistently in `pyproject.toml` and `package.json`
- [ ] `CHANGELOG.md` — `[Unreleased]` section renamed to the new version, fresh `[Unreleased]` added
- [ ] `python -m pip wheel --no-deps -w dist .` — wheel builds cleanly
- [ ] Tag: `git tag -a vX.Y.Z -m "vX.Y.Z"` and push with `--tags`
