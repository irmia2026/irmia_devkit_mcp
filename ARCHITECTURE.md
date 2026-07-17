# Architecture — Irmia DevKit MCP

> 本文档描述 `irmia_devkit_mcp` 的架构设计、关键决策和内部机制。
> 面向需要理解项目结构或贡献代码的开发者。用户文档见 [README.md](README.md)。

## Project Structure

```
irmia_devkit_mcp/
├── server.py                     # MCP 入口：44 工具注册，FastMCP 启动
├── __main__.py                   # `python -m irmia_devkit_mcp`
├── pyproject.toml                # Python 包元数据
├── package.json                  # npm 发布配置
├── bin/                          # Shell 启动脚本 (irmia-devkit.cmd / .sh)
├── tools/                        # 工具实现（与 irmia_devkit_open 共享）
│   ├── safe_edit.py              # 备份 → 替换 → 语法检查 → 回滚
│   ├── safe_read.py              # 增强文件读取（编码/hex/skeleton）
│   ├── codegraph.py              # 语义索引 + 符号搜索 + 调用链
│   ├── auto_config.py            # 外部工具自动检测 + 配置文件管理
│   ├── config.py                 # 全局配置单例
│   ├── _helpers.py               # proposal_reply, _run_cmd 等共享助手
│   ├── _file_utils.py            # 文件工具共享函数
│   └── ... (49 工具模块)
├── vendor/                       # 可内置 rg.exe / es.exe / fd.exe
├── tests/                        # 38 个 pytest 测试文件
├── README.md                     # 用户文档
├── CHANGELOG.md                  # 版本历史 (Keep a Changelog)
└── ARCHITECTURE.md               # 本文档
```

## Data Flow

```
MCP Client (Claude Code / Cursor / Windsurf / ...)
    │  JSON-RPC over stdio | SSE (localhost HTTP)
    ▼
server.py ── FastMCP 主机
    │  @mcp.tool()
    ▼
tools/*.py ── 纯函数实现
    │  返回 dict → _json() → JSON 字符串 → MCP 响应
    ▼
MCP Client ── LLM 解析结构化结果
```

## Key Design Decisions (ADR)

### ADR-1: 纯函数 + 薄包装层

**决策**：所有业务逻辑在 `tools/*.py` 中实现为纯函数；`server.py` 仅做 MCP 注册和结果序列化。

**理由**：与上游 `irmia_devkit_open` 共享工具实现，MCP 版本只需维护包装层。同步上游时不需要修改 `server.py`。

### ADR-2: 本地部署锁定

**决策**：启动时检查 `--host` 参数，仅允许 `127.0.0.1` / `localhost` / `::1`。

**理由**：所有文件系统工具操作的是运行服务器的机器。共享部署会导致文件路径泄露和操作日志污染。

### ADR-3: 外部工具自动配置

**决策**：启动时自动扫描项目内置 `vendor/` 目录和系统 PATH 中的 `es` / `rg` / `fd`，写入 `~/.irmia/mcp_config.json`。用户可手动编辑。扫描不到时打印安装指引。

**理由**：零配置开箱即用；内置二进制优先于系统 PATH，便于离线部署。同时给高级用户手动控制权。跨平台：Windows 扫描 Everything，Linux / macOS 自动使用 `locate` / `fd` 回退。

### ADR-4: 提案协议 (Proposal Protocol)

**决策**：工具失败或歧义时返回结构化 JSON `{proposal, evidence, options, next_call}`，引导 LLM 下一步操作，而非简单报错退出。

**理由**：LLM 需要上下文来做下一步决策。裸 `{"ok": false, "error": "xxx"}` 会导致 LLM 盲目重试或放弃。

## Configuration System

```
启动流程:
  1. load_config() → 读 ~/.irmia/mcp_config.json
  2. scan_tools()  → 自动检测 vendor/ → PATH → 常见安装路径中的 es/rg/fd
  3. 填充空路径 → 写回 mcp_config.json
  4. set_config()  → 注入全局 config 单例
  5. check_and_warn() → 缺失工具打印安装指引
  6. print_startup_banner() → 显示工具状态

优先级链:
  环境变量 > mcp_config.json 手动填写 > 自动扫描 > 默认值
```

## Deployment Modes

| Mode | Command | Transport | Scope |
|------|---------|-----------|-------|
| stdio | `python server.py` | stdin/stdout | 单 Agent |
| HTTP (local) | `python server.py --http` | SSE on 127.0.0.1 | 本地浏览器客户端 |
| ❌ Remote | `--host 0.0.0.0` | **Rejected** | 被启动保护拦截 |

## Tool Registration Pattern

```python
# server.py 中的每个工具都遵循此模式：
@mcp.tool()
def safe_edit(filepath: str, old: str, new: str, ...) -> str:
    """Docstring → MCP 工具描述"""
    result = _safe_edit(filepath, old, new, ...)
    if result.get("ok") and ...:
        _auto_index(filepath)   # best-effort 语义索引更新
    return _json(result)
```

## Dependencies

| Required | Optional |
|----------|----------|
| Python ≥ 3.10 | chardet（更好编码检测） |
| `mcp>=1.0.0` | psutil（进程列表） |
| | tree-sitter（多语言代码索引） |
| | ripgrep（快速内容搜索） |
| | beautifulsoup4（HTML 提取） |
| | Everything CLI / fd（快速文件名搜索） |

40+ 工具纯 Python 标准库实现，零外部依赖。

## Sync Strategy with Upstream

MCP 仓库定期从 `irmia_devkit_open` 同步 `tools/` 和 `tests/`。MCP 专属文件（`server.py`, `auto_config.py`, `__main__.py`, `package.json`, `bin/`）保持不变。

同步内容：
- 所有 `tools/*.py`（工具实现）
- 选定的 `tests/*.py`（排除 AstrBot 特定测试）
