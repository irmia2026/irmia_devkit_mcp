# Irmia DevKit MCP

为 Vibe Coding 工具提供 57 个安全开发工具。

## 接入

与 Playwright MCP 相同的模式——npx 自动下载安装：

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "command": "npx",
      "args": ["irmia-devkit-mcp", "--http", "--port", "8000"]
    }
  }
}
```

或直接启动服务端，客户端用 name + URL 接入：

```bash
npx irmia-devkit-mcp --http --port 8000
```

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "name": "irmia-devkit",
      "url": "http://127.0.0.1:8000/sse"
    }
  }
}
```

远程部署带 Token：

```json
{
  "mcpServers": {
    "irmia-devkit": {
      "name": "irmia-devkit",
      "url": "https://your-server.com/sse",
      "headers": {
        "Authorization": "Bearer ${IRMIA_TOKEN}"
      }
    }
  }
}
```

## 安装

| 方式 | 命令 |
|------|------|
| **uv** | `uvx --from git+https://github.com/irmia2026/irmia_devkit_mcp.git irmia-devkit --http --port 8000` |
| **pip** | `pip install git+https://github.com/irmia2026/irmia_devkit_mcp.git && irmia-devkit --http --port 8000` |
| **npx** | `npx github:irmia2026/irmia_devkit_mcp --http --port 8000` |

启动脚本会自动 `pip install mcp`，并报告可选外部程序的安装状态。

## 支持的客户端

| 客户端 | 接入方式 |
|--------|---------|
| **Cursor** | Settings → MCP → Add Server: name + url |
| **Claude Desktop** | `claude_desktop_config.json` |
| **VS Code** | `settings.json` `mcpServers` |
| **Windsurf** | `mcp_config.json` |
| **Cline** | `cline.mcpServers` |
| **AstrBot** | `mcp_servers.json` |
| **Reasonix** | `reasonix.toml` `mcp_servers` |

全部填 `name: irmia-devkit, url: http://host:port/sse`。

## 依赖

核心依赖仅 `mcp>=1.0.0`（启动脚本自动安装）。

49 个工具为 Python 标准库，无需任何外部程序。8 个工具在检测到外部程序时自动启用加速，未检测到时降级运行或给出安装指引：

| 工具 | 外部程序 | 检测到 | 未检测到 |
|------|---------|--------|----------|
| `rg_search` | ripgrep | 毫秒级搜索 | Python os.walk 扫描 |
| `es_search` | Everything/locate/fd | 毫秒级文件名搜索 | Python os.walk 扫描 |
| `gh_pr/issue/release/repo` | GitHub CLI | 完整 GitHub 操作 | 返回安装指引 |
| `lint_runner` | ruff/pylint/eslint | 代码质量检查 | 返回安装指引 |
| `syntax_check` | go/nim/node | 多语言语法检查 | Python 可用，其他 skipped |
| `test_runner` | go/cargo/node | 多框架测试 | 回退 pytest |
| `code_index` | tree-sitter-* | 多语言符号索引 | Python ast 可用 |
| `html_extract` | beautifulsoup4 | HTML 解析 | 返回安装指引 |

## 工具总览 (57)

| # | 分组 | 工具 |
|:--:|------|------|
| 10 | 安全编辑链 | `safe_edit` `safe_write` `safe_backups` `safe_rollback` `file_patch` `file_read` `multi_edit` `syntax_check` `lint_runner` `test_runner` |
| 12 | Git & GitHub | `git_status` `git_diff` `git_log` `git_commit` `git_branch` `git_remote` `git_push` `git_changelog` `gh_pr` `gh_issue` `gh_release` `gh_repo` |
| 9 | 文件 & 搜索 | `es_search` `rg_search` `dir_tree` `dir_list` `file_diff` `file_hash` `file_remove` `file_zip` `config_diff` |
| 3 | 网络 | `http_get` `http_post` `http_download` |
| 1 | 执行 | `shell_exec` |
| 6 | 代码智能 | `code_index` `code_explore` `code_pack` `code_diff_impact` `code_status` `symbol_rename` |
| 8 | 文本处理 | `html_extract` `json_query` `text_filter` `diff_strings` `csv_parse` `csv_gen` `md_strip` `log_parse` |
| 8 | 编码/时间/扩展 | `encode_decode` `time` `db_query` `dep_scan` `project_init` `uuid_gen` `semver_compare` `port_check` |

## 安全

- **命令注入防护**: shell 控制字符黑名单 + 命令白名单 + 高风险操作确认链
- **SSRF 防护**: URL → IP 检查 → DNS 解析 → HTTP 重定向 四层检测
- **路径穿越防护**: `..` 拦截 + `resolve()` 验证 + 系统目录黑名单 + ZIP slip 检测
- **SQL 注入防护**: SELECT/PRAGMA 白名单 + 数据库级只读 + 参数化查询

## 文档

| 文档 | 内容 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 项目结构、启动流程、安全架构、代码智能引擎 |
| [CHANGELOG.md](CHANGELOG.md) | 版本历史 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 新增工具教程、返回值规范、安全检查清单 |

## 许可

MIT
