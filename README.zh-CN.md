<p align="center">
  <img src="https://raw.githubusercontent.com/irmia2026/irmia_devkit_open/main/logo.png" width="120" alt="Irmia DevKit" />
</p>

<h1 align="center">Irmia DevKit MCP</h1>

<p align="center">
  <strong>为 AI 编码 Agent 提供 44 个安全开发工具 — 纯本地 · 零配置 · 开箱即用</strong><br />
  <sub>安全编辑 · 语义索引 · 文件搜索 · 测试运行 · 系统信息</sub>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.0%2B-green.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" /></a>
</p>

---

`irmia_devkit_mcp` 将 [`irmia_devkit_open`](https://github.com/irmia2026/irmia_devkit_open) 中经过实战检验的 44 个开发工具，打包成一个标准 [MCP](https://modelcontextprotocol.io/) Server。Claude Code、Cursor、Codex、Windsurf 等 MCP 客户端可以像调用原生工具一样调用 `safe_edit`、`code_explore`、`rg_search` 等能力，开箱即享安全加固。

## 为什么用它

| 特性 | 说明 |
|------|------|
| 🔒 **纯本地** | 仅绑定 `127.0.0.1` / `localhost` / `::1`，数据不出本机 |
| ⚡ **零配置** | 项目内置 `vendor/` 目录放入 `rg` / `fd` / `es` 即可自动识别，也支持系统 PATH 和纯 Python 降级 |
| 🛡️ **多层防御** | 四层 SSRF 过滤、编辑自动备份回滚、全文件操作统一路径穿越检查 |
| 🧠 **语义索引** | Python AST + SQLite FTS5，毫秒级符号搜索、调用链追踪、变更影响分析 |
| 📦 **44 工具** | 安全编辑、文件系统、搜索、代码智能、网络、文本处理、系统信息、测试运行 |
| 🌍 **跨平台** | Windows / Linux / macOS，自动选择对应平台二进制 |

## 快速开始

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
pip install mcp
python server.py
```

首次启动会自动扫描 `vendor/` 和 PATH，生成 `~/.irmia/mcp_config.json`。然后在你的 MCP 客户端中配置：

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

> ⚠️ `--host` 仅接受 `127.0.0.1` / `localhost` / `::1`，远程地址拒绝启动——这是安全设计，不是 bug。

## 工具总览

| 数量 | 分组 | 工具 |
|------|------|------|
| 10 | 🔒 安全编辑 | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_preview` `syntax_check` `lint_runner` `test_runner` `multi_edit` |
| 13 | 📂 文件系统 | `safe_read` `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_zip` `file_unzip` `file_move` `file_remove` `disk_info` `config_diff` |
| 6 | 🧠 代码智能 | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 3 | 📊 系统信息 | `port_check` `proc_list` `sys_snapshot` |
| 4 | 📝 文本处理 | `html_extract` `json_query` `text_filter` `diff_strings` |
| 5 | 🔧 编码/时间/扩展 | `encode_decode` `time` `db_query` `dep_scan` `uuid_gen` |
| 3 | 🌐 网络 | `http_get` `http_post` `http_download` |

## 外部工具与 vendor 目录

搜索顺序：**项目 `vendor/` → 系统 PATH → 常见安装路径**。各平台自动选择对应格式的二进制（Windows 用 `.exe`，POSIX 用无后缀 ELF），找不到时使用纯 Python 降级。

```json
// ~/.irmia/mcp_config.json（自动生成，可手动编辑）
{
  "es_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\es.exe",
  "rg_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\rg.exe",
  "fd_path": "D:\\path\\to\\irmia_devkit_mcp\\vendor\\fd.exe",
  "backup_dir": "C:\\Users\\...\\.irmia\\backups"
}
```

配置优先级：环境变量（`IRMIA_ES_PATH` / `IRMIA_RG_PATH` / `IRMIA_FD_PATH` / `IRMIA_BACKUP_DIR`）> 手动编辑的 `mcp_config.json` > 自动扫描 > 默认值。

## 安全

| 层级 | 机制 |
|------|------|
| 编辑 | 自动备份 → 替换 → 语法检查 → 失败回滚 |
| 网络 | SSRF 深度防御：协议白名单、内网 IP 黑名单（含 `0.0.0.0/8`、组播等）、DNS 解析后二次校验、重定向逐跳校验 |
| SQL | 仅允许 SELECT/PRAGMA，参数化查询防注入 |
| 路径 | `..` 穿越拒绝 + `resolve()` 前缀验证 + 系统目录黑名单 |
| 部署 | 拒绝非本地绑定 |

## 文档

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | English version |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计、数据流、设计决策 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [LICENSE](LICENSE) | AGPL-3.0 |

## FAQ

**和 `irmia_devkit_open` 什么关系？**
工具实现从 `irmia_devkit_open` 同步，MCP Server 独立运行，不依赖 AstrBot。

**需要装什么依赖？**
Python ≥ 3.10 和 `mcp>=1.0.0`。40+ 工具纯标准库实现，可选二进制仅加速无需强制。

**能部署到服务器上多人共享吗？**
不能，本 Server 锁定本地部署，所有文件操作作用于运行机器的文件系统。

## License

AGPL-3.0 © irmia2026
