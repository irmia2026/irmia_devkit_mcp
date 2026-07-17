<p align="center">
  <img src="https://raw.githubusercontent.com/irmia2026/irmia_devkit_open/main/logo.png" width="120" alt="Irmia DevKit" />
</p>

<h1 align="center">Irmia DevKit MCP</h1>

<p align="center">
  <strong>为 AI 编码 Agent 提供 44 个安全开发工具 — 纯本地 · 零配置 · 开箱即用</strong><br />
  <sub>安全编辑 · 语义索引 · 文件搜索 · 测试运行 · 系统信息</sub>
</p>

<p align="center">
  <a href="https://github.com/irmia2026/irmia_devkit_mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.0%2B-green.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> | 简体中文
</p>

---

`irmia_devkit_mcp` 把 [`irmia_devkit_open`](https://github.com/irmia2026/irmia_devkit_open) 中久经考验的 44 个开发工具打包成一个独立的 [Model Context Protocol](https://modelcontextprotocol.io/) 服务器。任何兼容 MCP 的 Agent——Claude Code、Cursor、Codex、Windsurf——都可以把 `safe_edit`、`code_explore`、`rg_search` 等当作一等工具直接调用，并默认获得加固后的安全配置。

## 为什么选择它

| 特性 | 说明 |
|------|------|
| 🔒 **本地专用** | 拒绝绑定 `127.0.0.1` / `localhost` / `::1` 以外的地址，文件不出本机 |
| ⚡ **零配置** | 内置 `vendor/` 二进制（`rg` / `fd` / `es`）自动优先使用；其次 PATH，最后回退纯 Python 实现 |
| 🛡️ **纵深防御** | SSRF 四层过滤、编辑自动备份回滚、所有文件操作统一路径穿越检查 |
| 🧠 **语义索引** | Python AST + SQLite FTS5，毫秒级符号搜索、调用链和影响分析 |
| 📦 **44 工具** | 覆盖编辑 / 搜索 / 测试 / 代码智能 / 网络 / 文件 / 编码 / 时间 / 文本处理 / 系统信息 |
| 🌍 **跨平台** | Windows / Linux / macOS，按平台自动选择 `.exe` 或无后缀原生二进制 |

## 快速开始

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
pip install mcp
python server.py
```

首次启动时，服务器会扫描 `vendor/` 和 PATH 中的 `rg` / `fd` / `es` 并生成 `~/.irmia/mcp_config.json`。然后把以下配置加到你的 MCP 客户端：

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

### HTTP 模式（本地浏览器客户端）

```bash
python server.py --http --port 8000
# → http://127.0.0.1:8000/mcp
```

> ⚠️ `--host` 仅接受 `127.0.0.1` / `localhost` / `::1`，远程地址会在启动时直接拒绝。这是安全设计，不是 bug。

## 工具总览

| # | 分组 | 工具 |
|---|------|------|
| 10 | 🔒 安全编辑链 | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_preview` `syntax_check` `lint_runner` `test_runner` `multi_edit` |
| 13 | 📂 文件系统 | `safe_read` `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_zip` `file_unzip` `file_move` `file_remove` `disk_info` `config_diff` |
| 6 | 🧠 代码智能 | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 3 | 📊 系统信息 | `port_check` `proc_list` `sys_snapshot` |
| 4 | 📝 文本处理 | `html_extract` `json_query` `text_filter` `diff_strings` |
| 5 | 🔧 编码 / 时间 / 扩展 | `encode_decode` `time` `db_query` `dep_scan` `uuid_gen` |
| 3 | 🌐 网络 | `http_get` `http_post` `http_download` |

## 外部工具解析

搜索顺序：**项目 `vendor/` → PATH → 常见安装路径**。Linux/macOS 上的二进制必须具备执行权限；Windows 优先 `.exe`，其他平台自动跳过。

```json
// ~/.irmia/mcp_config.json（自动生成，可手动编辑）
{
  "es_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\es.exe",
  "rg_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\rg.exe",
  "fd_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\fd.exe",
  "backup_dir": "C:\\Users\\...\\.irmia\\backups"
}
```

| 工具 | Windows | Linux / macOS | 无外部依赖时 |
|------|---------|---------------|--------------|
| `es_search` | Everything CLI（需要 Everything 服务运行） | `locate` → `fd` → Python 回退 | Python `os.walk` |
| `rg_search` | ripgrep | ripgrep | 纯 Python 扫描 |

优先级：环境变量（`IRMIA_ES_PATH`、`IRMIA_RG_PATH`、`IRMIA_FD_PATH`、`IRMIA_BACKUP_DIR`）→ 手动修改 `mcp_config.json` → 自动扫描 → 内置默认值。

## 安全模型

| 层级 | 机制 |
|------|------|
| 编辑 | 备份 → 替换 → 语法检查 → 失败自动回滚 |
| 网络 | SSRF 纵深防御：协议白名单、IP 段黑名单（含 `0.0.0.0/8`、组播、保留段）、DNS 解析复查、每次重定向复查 |
| SQL | `db_query` 只读、仅允许 SELECT/PRAGMA、参数化查询 |
| 路径 | `..` 穿越拒绝 + `resolve()` 前缀校验 + 系统目录黑名单 |
| 部署 | 启动时拒绝非 localhost 绑定 |

## 文档

| 文档 | 内容 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 项目结构、数据流、设计决策 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史（Keep a Changelog） |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 新增工具、返回值规范、安全清单 |
| [LICENSE](LICENSE) | AGPL-3.0 |

## FAQ

**和 `irmia_devkit_open` 是什么关系？**
`irmia_devkit_mcp` 是 MCP 打包版本。工具实现与上游同步，但作为独立 MCP Server 运行，不依赖 AstrBot。

**需要安装什么依赖？**
Python ≥ 3.10 和 `mcp>=1.0.0`。40+ 工具纯标准库实现；外部二进制只用于加速搜索，绝非必需。

**能部署到服务器上多人共享吗？**
不能，也不应该。本服务器只绑定 localhost，所有文件系统工具操作的是运行它的机器。共享部署会泄露主机路径和文件内容。

## License

AGPL-3.0 © irmia2026
