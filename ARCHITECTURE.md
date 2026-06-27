# Architecture — Irmia DevKit MCP

> 本文档描述 `irmia_devkit_mcp` 的架构设计、关键决策和内部机制。
> 面向需要理解项目结构或贡献代码的开发者。用户文档见 [README.md](README.md)。

## Project Structure

```
irmia_devkit_mcp/
├── server.py                     # MCP 入口：65 工具注册，FastMCP 启动
├── __main__.py                   # `python -m irmia_devkit_mcp`
├── pyproject.toml                # Python 包元数据
├── package.json                  # npm 发布配置
├── bin/                          # Shell 启动脚本 (irmia-devkit.cmd / .sh)
├── tools/                        # 工具实现（与 irmia_devkit_open 共享）
│   ├── safe_edit.py              # 备份 → 替换 → 语法检查 → 回滚
│   ├── safe_read.py              # 增强文件读取 (编码/hex/skeleton)
│   ├── codegraph.py              # 语义索引 + 符号搜索 + 调用链
│   ├── shell_exec.py             # 命令白名单沙箱
│   ├── auto_config.py            # 外部工具自动检测 + 配置文件管理
│   ├── config.py                 # 全局配置单例
│   ├── _helpers.py               # proposal_reply, _run_cmd 等共享助手
│   ├── _file_utils.py            # 文件工具共享函数
│   └── ... (60+ 工具模块)
├── tests/                        # 49 个 pytest 测试文件
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
    │  @mcp.tool() → 自动注入审计 (monkey-patch)
    ▼
tools/*.py ── 纯函数实现
    │  返回 dict → _json() → JSON 字符串 → MCP 响应
    ▼
MCP Client ── LLM 解析结构化结果
```

### 审计链（v2.6.2+）

```
@mcp.tool() 装饰器
    │  _audited_tool 包装
    ├─ 1. 调用前：记录开始时间
    ├─ 2. 调用原始工具函数
    ├─ 3. 调用后：tool_stats.record(name) → 内存计数器 +1
    └─ 4. 调用后：op_log.record(name, params, result, duration) → SQLite
```

所有 65 个工具自动享受审计，无需手动添加代码。审计失败静默吞掉，不影响工具调用。

## Key Design Decisions (ADR)

### ADR-1: 纯函数 + 薄包装层

**决策**: 所有业务逻辑在 `tools/*.py` 中实现为纯函数；`server.py` 仅做 MCP 注册和结果序列化。

**理由**: 与上游 `irmia_devkit_open` 共享工具实现，MCP 版本只需维护包装层。同步上游时不需要修改 `server.py`。

### ADR-2: monkey-patch mcp.tool() 实现审计

**决策**: 不修改每个 `@mcp.tool()` 函数，而是替换 `mcp.tool` 本身来注入 `tool_stats.record()` 和 `op_log.record()`。

**理由**: 65 个工具 × 2 行 = 130 个修改点，手动添加容易遗漏。monkey-patch 一次设置，自动覆盖所有现有及未来工具。

### ADR-3: 本地部署锁定

**决策**: 启动时检查 `--host` 参数，仅允许 `127.0.0.1` / `localhost` / `::1`。

**理由**: 所有文件系统工具操作的是运行服务器的机器。共享部署会导致文件路径泄露和操作日志污染。

### ADR-4: 外部工具自动配置

**决策**: 启动时自动扫描 `es` / `rg` / `gh`，写入 `~/.irmia/mcp_config.json`。用户可手动编辑。扫描不到时打印安装指引。

**理由**: 零配置开箱即用；同时给高级用户手动控制权。跨平台：Windows 扫描 Everything，Linux/macOS 自动使用 `locate`/`fd` 回退。

### ADR-5: 提案协议 (Proposal Protocol)

**决策**: 工具失败或歧义时返回结构化 JSON `{proposal, evidence, options, next_call}`，引导 LLM 下一步操作，而非简单报错退出。

**理由**: LLM 需要上下文来做下一步决策。裸 `{"ok": false, "error": "xxx"}` 会导致 LLM 盲目重试或放弃。

## Configuration System

```
启动流程:
  1. load_config() → 读 ~/.irmia/mcp_config.json
  2. scan_tools()  → 自动检测 es/rg/gh
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
@mcp.tool()                   # 自动注入审计 (monkey-patch)
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
| Python ≥ 3.10 | chardet (更好编码检测) |
| `mcp>=1.0.0` | psutil (进程列表) |
| | tree-sitter (多语言代码索引) |
| | ripgrep (快速内容搜索) |
| | beautifulsoup4 (HTML 提取) |
| | Everything CLI / fd (快速文件名搜索) |
| | GitHub CLI (GitHub 操作) |

50+ 工具纯 Python 标准库实现，零外部依赖。

## Sync Strategy with Upstream

MCP 仓库定期从 `irmia_devkit_open` 同步 `tools/` 和 `tests/`。MCP 专属文件（`server.py`, `auto_config.py`, `__main__.py`, `package.json`, `bin/`）保持不变。

同步内容：
- 所有 `tools/*.py`（工具实现）
- 选定的 `tests/*.py`（排除 AstrBot 特定测试）
