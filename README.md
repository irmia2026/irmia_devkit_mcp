# Irmia DevKit MCP

为 Vibe Coding 工具提供 **65** 个安全开发工具 — MCP 协议实现。

继承自 [`irmia_devkit_open`](https://github.com/irmia2026/irmia_devkit_open) v2.6.0，包装为 MCP Server。

## 安装

### 方式 1：mcp run（推荐）

```bash
# clone 仓库
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp

# 安装依赖
pip install mcp

# 直接运行
mcp run server.py
```

### 方式 2：Github + uv（无需 clone）

在 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "command": "uvx",
      "args": ["mcp", "run", "https://raw.githubusercontent.com/irmia2026/irmia_devkit_mcp/main/server.py"]
    }
  }
}
```

### 方式 3：npm install（需要 Node.js）

```bash
npm install irmia-devkit-mcp
npx irmia-devkit
```

### 方式 4：HTTP 模式

```bash
python server.py --http --port 8000
# 或
mcp run server.py --transport sse --port 8000
```

## MCP 客户端配置

### Cursor

`~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "irmia-devkit": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "mcp", "run", "/path/to/irmia_devkit_mcp/server.py"]
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

### 更多客户端

| 客户端 | 配置方式 |
|--------|----------|
| Windsurf | File → Settings → MCP Servers |
| Continue | `~/.continue/config.json` |
| Cline | VSCode 扩展设置 → MCP Server → Add |
| Aider | `aider --mcp-servers irmia-devkit` |

## 前置依赖

| 工具 | 依赖 | 未安装时 |
|------|------|----------|
| `es_search` | Everything + es.exe (Win) / locate / fd | 错误提示或 Python os.walk 扫描 |
| `gh_pr` / `gh_issue` / `gh_release` / `gh_repo` | GitHub CLI (`gh`) | 返回错误提示 |
| `html_extract` | `beautifulsoup4`，lxml 可选 | 缺 bs4 报错，缺 lxml 回退 |
| `syntax_check` (Nim/Go/JS/TS) | 对应编译器 | 跳过 |
| `lint_runner` | ruff / pylint / eslint | 安装提示 |
| `rg_search` | ripgrep（可选） | 降级纯标库扫描 |
| `code_index` (多语言) | tree-sitter（可选） | Python 零依赖；其他跳过 |

其余 50+ 工具为 Python 标准库实现，无外部依赖。

## 工具总览 (65)

| # | 分组 | 工具 |
|:--:|------|------|
| 10 | 安全编辑链 | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_preview` `syntax_check` `lint_runner` `test_runner` `multi_edit` |
| 11 | Git & GitHub | `git_status` `git_diff` `git_log` `git_commit` `git_branch` `git_remote` `git_push` `git_changelog` `gh_pr` `gh_issue` `gh_release` `gh_repo` |
| 13 | 文件系统 | `safe_read` `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_zip` `file_unzip` `file_move` `file_remove` `disk_info` `config_diff` |
| 4 | 系统信息 | `port_check` `proc_list` `sys_snapshot` `tool_stats` |
| 3 | 网络 | `http_get` `http_post` `http_download` |
| 1 | 执行 | `shell_exec` |
| 6 | 代码智能 | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 8 | 文本处理 | `html_extract` `json_query` `text_filter` `diff_strings` `csv_parse` `csv_gen` `md_strip` `log_parse` |
| 8 | 编码/时间/扩展 | `encode_decode` `time` `db_query` `dep_scan` `project_init` `uuid_gen` `semver_compare` `op_log` |

## 设计说明

### safe_edit 流程
备份 → 精确替换 → whitespace-tolerant 模糊匹配 → 语法检查 → 失败自动回滚。
多处匹配时返回所有位置并用 `occurrence=N` 消歧。

### 安全设计
- **SSRF 四层**：IP 黑名单、内网网段拦截、SSRF 库防护、路径沙箱
- **safe_edit 防御链**：自动备份 + 语法检查 + 原子写入 + 失败回滚
- **shell_exec 沙箱**：命令白名单 + 路径参数沙箱 + 高风险命令分级
- **路径穿越防护**：check_path_allowed 统一拦截

### 提案协议
部分工具在失败或歧义时返回 `{proposal, evidence, options, next_call}` 结构化信息，引导 LLM 下一步操作。

## License

MIT
