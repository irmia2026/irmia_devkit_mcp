<p align="center">
  <img src="https://raw.githubusercontent.com/irmia2026/irmia_devkit_open/main/logo.png" width="120" alt="Irmia DevKit" />
</p>

<h1 align="center">Irmia DevKit MCP</h1>

<p align="center">
  <strong>44 permission-annotated development tools for AI coding agents — localhost transport, zero-config setup.</strong><br />
  <sub>Safe editing · Semantic code index · File search · Test runner · System info</sub>
</p>

<p align="center">
  <a href="https://github.com/irmia2026/irmia_devkit_mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.0%2B-green.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">简体中文</a>
</p>

---

`irmia_devkit_mcp` packages 44 battle-tested development tools from [`irmia_devkit_open`](https://github.com/irmia2026/irmia_devkit_open) as a standalone [Model Context Protocol](https://modelcontextprotocol.io/) server. It also declares the companion `dev-workflow` Skill through `reasonix-plugin.json`, so plugin-aware hosts can install the tools and their safe coding workflow together. Any MCP-compatible agent — Claude Code, Cursor, Codex, Windsurf — can call `safe_edit`, `code_explore`, `rg_search` and friends as first-class tools, with hardened security defaults out of the box.

## Why this server

| Feature | What it means |
|---------|---------------|
| 🔒 **Local transport** | Refuses non-loopback HTTP binds. MCP clients may still send tool inputs and outputs to their configured model provider. |
| ⚡ **Zero config** | Includes verified x86-64 search binaries for Windows/Linux, then falls back to PATH or pure Python on other platforms. |
| 🛡️ **Defense in depth** | Four-layer SSRF filtering, automatic edit backups with rollback, unified path-traversal checks on every file operation. |
| 🧠 **Semantic index** | Python AST + SQLite FTS5 — symbol search, call chains, and impact analysis in milliseconds. |
| 📦 **44 tools** | Editing, search, testing, code intelligence, networking, files, encoding, time, text processing, system info. |
| 🌍 **Cross-platform** | Windows, Linux, macOS, with platform-native launchers and executable resolution. |

## Quick start

**Requirements:** Python ≥ 3.10 (on Windows, either check *Add python.exe to PATH* during installation or install the `py` launcher). The launchers call one standard-library Python bootstrap, which creates a project-local `.venv` on first launch and installs dependencies into it — nothing touches your global site-packages. npm commands use the included Node launcher to locate Python correctly on each platform. This first launch writes under the plugin directory and requires network access to PyPI unless the pinned dependencies are already installed in that venv.

Reasonix users can preview the combined Skill + MCP plugin before installation:

```bash
reasonix plugin install https://github.com/irmia2026/irmia_devkit_mcp --dry-run
reasonix plugin install https://github.com/irmia2026/irmia_devkit_mcp --yes
```

The native Reasonix manifest works on Linux/macOS. Reasonix v1.17.18 does not yet wrap plugin-local `.cmd` MCP commands with `cmd.exe` on Windows; Windows users should use the npm launcher or configure `python server.py` directly until the host adds batch-command wrapping.

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
bin/irmia-devkit.sh        # Linux/macOS
bin\irmia-devkit.cmd       # Windows — or: npx irmia-devkit-mcp
```

On first launch the server scans `vendor/` and PATH for `rg` / `fd` / `es` and writes `~/.irmia/mcp_config.json`. Point your MCP client at the launcher script (or `server.py`):

### Cursor — `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "command": "python",
      "args": ["D:\\path\\to\\irmia_devkit_mcp\\server.py"]
    }
  }
}
```

### Claude Desktop — `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "command": "python",
      "args": ["/path/to/irmia_devkit_mcp/server.py"]
    }
  }
}
```

### HTTP mode (local browser clients)

```bash
python server.py --http --port 8000
# → http://127.0.0.1:8000/mcp
```

> ⚠️ `--host` only accepts `127.0.0.1` / `localhost` / `::1`. Remote binding is rejected at startup — this is by design, not a bug.

## Tool overview

| # | Group | Tools |
|---|-------|-------|
| 10 | 🔒 Safe editing | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_preview` `syntax_check` `lint_runner` `test_runner` `multi_edit` |
| 13 | 📂 Filesystem | `safe_read` `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_zip` `file_unzip` `file_move` `file_remove` `disk_info` `config_diff` |
| 6 | 🧠 Code intelligence | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 3 | 📊 System info | `port_check` `proc_list` `sys_snapshot` |
| 4 | 📝 Text processing | `html_extract` `json_query` `text_filter` `diff_strings` |
| 5 | 🔧 Encoding / time / misc | `encode_decode` `time` `db_query` `dep_scan` `uuid_gen` |
| 3 | 🌐 Networking | `http_get` `http_post` `http_download` |

## Bundled search tools and resolution

Runtime search order is: **environment/manual configuration → verified project `vendor/` → PATH → pure-Python fallback**. The repository bundles upstream x86-64 releases of ripgrep and fd for Windows/Linux plus Everything CLI for Windows. Archive URLs, archive hashes, extraction members, licenses, and extracted-file SHA-256 hashes are recorded in [`vendor/README.txt`](vendor/README.txt), [`vendor/SHA256SUMS`](vendor/SHA256SUMS), and [`vendor/THIRD_PARTY_LICENSES.txt`](vendor/THIRD_PARTY_LICENSES.txt); packaging tests pin every extracted hash. macOS, ARM, and other unsupported targets automatically use PATH or the Python fallback.

```json
// ~/.irmia/mcp_config.json (auto-generated, user-editable)
{
  "es_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\es.exe",
  "rg_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\rg.exe",
  "fd_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\fd.exe",
  "backup_dir": "C:\\Users\\...\\.irmia\\backups"
}
```

| Tool | Windows | Linux / macOS | No external dependency |
|------|---------|---------------|------------------------|
| `es_search` | Everything CLI (requires the Everything service) | `locate` → `fd` → Python fallback | Python `os.walk` |
| `rg_search` | ripgrep | ripgrep | Pure-Python scanner |

Precedence: environment variable (`IRMIA_ES_PATH`, `IRMIA_RG_PATH`, `IRMIA_FD_PATH`, `IRMIA_BACKUP_DIR`) → manual `mcp_config.json` values → auto-scan → built-in defaults.

## Security model

| Layer | Mechanism |
|-------|-----------|
| Editing | Backup → replace → syntax check → rollback on failure |
| Network | SSRF defense in depth: scheme allowlist, IP-range blocklist, DNS answer pinning, proxy bypass, and per-redirect re-validation |
| SQL | `db_query` read-only, SELECT/PRAGMA allowlist, parameterized queries |
| Paths | `..` traversal rejection + canonical prefix validation + filesystem-root, user-home, and system-directory blocklist |
| Deployment | Non-localhost binding refused at startup |
| Startup | The source/plugin launcher may create `.venv`, install pinned direct dependencies from PyPI, and write detected-tool configuration under `~/.irmia/` |

### Required capabilities and data flow

This server is intentionally powerful. Depending on the selected tool, it can read, create, overwrite, move, archive, or delete local files; execute test and lint subprocesses; inspect process, port, disk, and system metadata; and make outbound HTTP requests or downloads. The MCP schema marks read-only, mutating, destructive, and open-world tools explicitly so compatible hosts can apply the appropriate approval policy. Tool results are returned to the MCP client and may be transmitted to the model provider configured by that client.

## Documentation

| Document | Contents |
|----------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Project layout, data flow, design decisions |
| [CHANGELOG.md](CHANGELOG.md) | Version history (Keep a Changelog) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Adding tools, return-value conventions, security checklist |
| [LICENSE](LICENSE) | AGPL-3.0 |
| [vendor/THIRD_PARTY_LICENSES.txt](vendor/THIRD_PARTY_LICENSES.txt) | Licenses for bundled search binaries |

## FAQ

**How does this relate to `irmia_devkit_open`?**
`irmia_devkit_mcp` is the MCP-packaged edition. Tool implementations are synced from upstream; the server runs standalone without AstrBot.

**What do I need to install?**
Python ≥ 3.10. The launchers install the exact versions in `requirements.txt` into a project-local virtual environment. Bundled search binaries accelerate supported x86-64 systems but are never required.

**Can I deploy this on a shared server?**
No — by design. The server only binds to localhost, and every filesystem tool operates on the machine it runs on. Shared deployment would leak host paths and file contents.

## License

AGPL-3.0 © irmia2026
