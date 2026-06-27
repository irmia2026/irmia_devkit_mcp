<p align="center">
  <img src="https://raw.githubusercontent.com/irmia2026/irmia_devkit_open/main/logo.png" width="120" alt="Irmia DevKit" />
</p>

<h1 align="center">Irmia DevKit MCP</h1>

<p align="center">
  <strong>为 AI 编码 Agent 提供 65 个安全开发工具 — 纯本地 · 零配置 · 开箱即用</strong><br />
  <sub>安全编辑 · 语义索引 · Git/GitHub · 文件搜索 · 测试运行 · 系统信息</sub>
</p>

<p align="center">
  <a href="https://github.com/irmia2026/irmia_devkit_mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.0+-green.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" /></a>
</p>

---

> **这是什么？** 把 irmia_devkit_open 的 65 个开发工具，打包成一个 MCP Server。你的 AI Agent（Claude Code / Cursor / Codex / Windsurf 等）可以通过 MCP 协议直接调用 safe_edit、git_commit、code_explore 等工具——就像给 Agent 配了一把瑞士军刀。

## ✨ 为什么选它

| 特性 | 说明 |
|------|------|
| 🔒 **本地专用** | 拒绝非 localhost 绑定，数据不出本机 |
| ⚡ **零配置** | 自动扫描 es / rg / gh 路径，生成配置文件 |
| 🛡️ **安全第一** | SSRF 四层防护 · 编辑自动备份回滚 · 命令白名单沙箱 |
| 🧠 **语义索引** | Python AST 解析 + SQLite FTS5，秒级代码搜索 |
| 📦 **65 工具** | 覆盖编辑/搜索/Git/测试/代码智能/网络/文本处理 |
| 🌍 **跨平台** | Windows / Linux / macOS 均可用 |

## 🚀 30 秒快速开始

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
pip install mcp
python server.py
```

启动后自动扫描本地工具并生成 `~/.irmia/mcp_config.json`。然后将以下配置添加到你的 MCP 客户端：

### Cursor
`~/.cursor/mcp.json`:
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

### Claude Desktop
`~/.claude/settings.json`:
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

> ⚠️ `--host` 仅接受 `127.0.0.1` / `localhost` / `::1`，远程部署会被拒绝启动。这是安全设计，不是 bug。

## 📋 工具总览

| # | 分组 | 核心工具 |
|:--:|------|----------|
| 10 | 🔒 安全编辑链 | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_preview` `syntax_check` `lint_runner` `test_runner` `multi_edit` |
| 12 | 🔀 Git & GitHub | `git_status` `git_diff` `git_log` `git_commit` `git_branch` `git_remote` `git_push` `git_changelog` `gh_pr` `gh_issue` `gh_release` `gh_repo` |
| 13 | 📂 文件系统 | `safe_read` `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_zip` `file_unzip` `file_move` `file_remove` `disk_info` `config_diff` |
| 6 | 🧠 代码智能 | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 4 | 📊 系统信息 | `port_check` `proc_list` `sys_snapshot` `tool_stats` |
| 8 | 📝 文本处理 | `html_extract` `json_query` `text_filter` `diff_strings` `csv_parse` `csv_gen` `md_strip` `log_parse` |
| 8 | 🔧 编码/时间/扩展 | `encode_decode` `time` `db_query` `dep_scan` `project_init` `uuid_gen` `semver_compare` `op_log` |
| 3 | 🌐 网络 | `http_get` `http_post` `http_download` |
| 1 | ⚡ 执行 | `shell_exec` |

## ⚙️ 外部工具自动检测

首次启动后生成 `~/.irmia/mcp_config.json`：

```json
{
  "es_path": "D:\\Program Files\\Everything\\es.exe",
  "rg_path": "/usr/bin/rg",
  "gh_path": "",
  "backup_dir": "C:\\Users\\...\\.irmia\\backups"
}
```

| 机制 | 说明 |
|------|------|
| 🔍 自动扫描 | PATH → 常见安装路径 → 自动写入 config |
| ✏️ 手动填写 | 编辑 `mcp_config.json`，立即生效 |
| ⚠️ 安装指引 | 扫不到时打印下载链接和安装命令 |
| 🌍 跨平台 | Linux/macOS 下 `es_path` 自动回退 `locate`/`fd`，不报警 |

| 工具 | Windows | Linux/macOS | 无依赖时 |
|------|---------|-------------|----------|
| `es_search` | Everything CLI | `locate` → `fd` → Python 回退 | Python os.walk |
| `rg_search` | ripgrep | ripgrep | Python 纯标准库 |
| `gh_*` | GitHub CLI | GitHub CLI | 返回错误提示 |

## 🛡️ 安全设计

| 层级 | 机制 |
|------|------|
| **编辑** | 自动备份 → 替换 → 语法检查 → 失败自动回滚 |
| **网络** | SSRF 四层防护：IP 黑名单 + 内网拦截 + DNS 解析校验 + 重定向重新校验 |
| **执行** | `shell_exec` 七层沙箱：白名单 → 子命令 → 危险字符 → shell=False → cwd 限制 → 高风险确认 |
| **SQL** | `db_query` 只读 + 参数化查询，防注入 |
| **路径** | 所有文件操作统一路径穿越检查 |
| **部署** | 拒绝非 localhost 绑定，防止远程访问 |

## 📖 更多文档

| 文档 | 内容 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 项目结构、数据流、关键设计决策 |
| [CHANGELOG.md](CHANGELOG.md) | 完整版本历史（Keep a Changelog 格式） |
| [LICENSE](LICENSE) | MIT |

## ❓ FAQ

**Q: 和 `irmia_devkit_open` 什么关系？**
A: `irmia_devkit_mcp` 是 MCP 协议版本，工具实现完全同步自 `irmia_devkit_open`，但作为独立 MCP Server 运行，不依赖 AstrBot。

**Q: 需要装什么依赖？**
A: Python ≥ 3.10 + `mcp>=1.0.0`。50+ 工具纯标准库实现，可选依赖见上方表格。

**Q: 能部署到服务器上多人共享吗？**
A: 不能，也不应该。本 MCP Server 锁定本地部署（拒绝非 localhost 绑定），所有工具操作的是运行服务器的机器文件系统。共享部署会暴露主机文件路径和操作日志。

**Q: 为什么 tool_stats 显示全 0？**
A: v2.6.2 已修复。旧版因 MCP 迁移时审计链断裂导致，现已通过 monkey-patch `mcp.tool()` 自动修复。

## 📄 License

MIT © irmia2026
