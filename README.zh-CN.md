<p align="center">
  <img src="https://raw.githubusercontent.com/irmia2026/irmia_devkit_open/main/logo.png" width="120" alt="Irmia DevKit" />
</p>

<h1 align="center">Irmia DevKit MCP</h1>

<p align="center">
  <strong>为 AI 编码 Agent 提供 44 个带权限注解的开发工具 — 本地传输 · 零配置</strong><br />
  <sub>安全编辑 · 语义索引 · 文件搜索 · 测试运行 · 系统信息</sub>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.0%2B-green.svg" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" /></a>
</p>

---

`irmia_devkit_mcp` 将 [`irmia_devkit_open`](https://github.com/irmia2026/irmia_devkit_open) 中经过实战检验的 44 个开发工具，打包成一个标准 [MCP](https://modelcontextprotocol.io/) Server；同时通过 `reasonix-plugin.json` 声明配套的 `dev-workflow` Skill，使支持插件的宿主一次安装工具和安全开发工作流。Claude Code、Cursor、Codex、Windsurf 等 MCP 客户端可以像调用原生工具一样调用 `safe_edit`、`code_explore`、`rg_search` 等能力，开箱即享安全加固。

## 为什么用它

| 特性 | 说明 |
|------|------|
| 🔒 **本地传输** | HTTP 仅允许绑定 `127.0.0.1` / `localhost` / `::1`；MCP 客户端仍可能把工具输入与结果发送给其配置的模型服务商 |
| ⚡ **零配置** | 内置已校验的 Windows/Linux x86-64 搜索程序，其他平台自动回退到 PATH 或纯 Python 实现 |
| 🛡️ **多层防御** | 四层 SSRF 过滤、编辑自动备份回滚、全文件操作统一路径穿越检查 |
| 🧠 **语义索引** | Python AST + SQLite FTS5，毫秒级符号搜索、调用链追踪、变更影响分析 |
| 📦 **44 工具** | 安全编辑、文件系统、搜索、代码智能、网络、文本处理、系统信息、测试运行 |
| 🌍 **跨平台** | Windows / Linux / macOS，使用平台启动脚本并自动解析可执行文件 |

## 快速开始

**要求：** Python ≥ 3.10（Windows 安装时建议勾选 *Add python.exe to PATH*，或确保安装了 `py` 启动器）。各平台入口统一调用仅依赖标准库的 Python bootstrap，首次运行会自动创建项目本地 `.venv` 并安装依赖，不会污染全局 site-packages；npm 入口通过随包 Node launcher 查找本机 Python。首次启动会写入插件目录；若该 venv 尚无锁定依赖，还需要访问 PyPI。

Reasonix 用户可先预览同时包含 Skill 与 MCP 的插件，再确认安装：

```bash
reasonix plugin install https://github.com/irmia2026/irmia_devkit_mcp --dry-run
reasonix plugin install https://github.com/irmia2026/irmia_devkit_mcp --yes
```

Reasonix 原生清单在 Linux/macOS 可直接启动。Reasonix v1.17.18 在 Windows 尚未用 `cmd.exe` 包装插件内的 `.cmd` MCP 命令；宿主补齐该能力前，Windows 用户应使用 npm 入口，或在 MCP 配置中直接指定 `python server.py`。

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
bin/irmia-devkit.sh        # Linux/macOS
bin\irmia-devkit.cmd       # Windows —— 或运行: npx irmia-devkit-mcp
```

首次启动会自动扫描 `vendor/` 和 PATH，生成 `~/.irmia/mcp_config.json`。然后在你的 MCP 客户端中配置（指向启动脚本或 `server.py`）：

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

## 内置搜索工具与解析顺序

运行时解析顺序：**环境变量/手动配置 → 已校验的项目 `vendor/` → 系统 PATH → 纯 Python 降级**。仓库内置 ripgrep、fd 的 Windows/Linux x86-64 官方版本，以及 Windows Everything CLI；归档下载地址、归档哈希、解压成员、许可证和文件 SHA-256 记录在 [`vendor/README.txt`](vendor/README.txt)、[`vendor/SHA256SUMS`](vendor/SHA256SUMS) 与 [`vendor/THIRD_PARTY_LICENSES.txt`](vendor/THIRD_PARTY_LICENSES.txt)，打包测试会固定并逐项校验。macOS、ARM 等未内置的平台会自动使用 PATH 或 Python 降级。

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
| 网络 | SSRF 深度防御：协议白名单、内网 IP 黑名单、DNS 结果固定、禁用代理、重定向逐跳校验 |
| SQL | 仅允许 SELECT/PRAGMA，参数化查询防注入 |
| 路径 | `..` 穿越拒绝 + 规范化前缀验证 + 文件系统根目录、用户主目录与系统目录黑名单 |
| 部署 | 拒绝非本地绑定 |
| 启动 | 源码/插件启动器可能创建 `.venv`、从 PyPI 安装锁定的直接依赖，并在 `~/.irmia/` 写入工具探测配置 |

### 所需权限与数据流

本 Server 按所选工具可读取、新建、覆盖、移动、压缩或删除本机文件，执行测试和 lint 子进程，读取进程、端口、磁盘与系统元数据，以及发起对外 HTTP 请求或下载。MCP schema 已明确标注只读、写入、破坏性和外部交互工具，供兼容客户端执行相应审批。工具结果会返回 MCP 客户端，并可能被该客户端发送给其配置的模型服务商。

## 文档

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | English version |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计、数据流、设计决策 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [LICENSE](LICENSE) | AGPL-3.0 |
| [vendor/THIRD_PARTY_LICENSES.txt](vendor/THIRD_PARTY_LICENSES.txt) | 内置搜索程序的第三方许可证 |

## FAQ

**和 `irmia_devkit_open` 什么关系？**
工具实现从 `irmia_devkit_open` 同步，MCP Server 独立运行，不依赖 AstrBot。

**需要装什么依赖？**
Python ≥ 3.10（Windows 推荐勾选 Add to PATH 或安装 `py` 启动器）。首次经启动脚本运行会自动创建本地 `.venv`，并按 `requirements.txt` 的精确版本安装依赖；内置搜索程序只用于加速受支持的 x86-64 平台，并非必需。

**能部署到服务器上多人共享吗？**
不能，本 Server 锁定本地传输，所有文件操作作用于运行机器的文件系统；这不等于模型侧离线，请同时检查 MCP 客户端所配置模型服务商的数据策略。

## License

AGPL-3.0 © irmia2026
