# Architecture

## 项目结构

```
irmia_devkit_mcp/
├── server.py              # FastMCP 入口，57 个工具注册
├── __main__.py            # python -m 入口
├── pyproject.toml         # 项目元数据
├── package.json           # npx 入口
├── requirements.txt       # 唯一依赖：mcp>=1.0.0
├── bin/
│   ├── irmia-devkit.cmd   # Windows 启动脚本
│   └── irmia-devkit.sh    # Unix 启动脚本
├── tools/                 # 44 个工具模块（零 AstrBot 依赖）
│   ├── _helpers.py        # 基础设施：proposal_reply / unwrap / _run_cmd
│   ├── _file_utils.py     # 文件读写：编码检测 / whitespace 对齐 / SymlinkGuard
│   ├── _http_utils.py     # SSRF 防护：四层检测
│   ├── config.py          # 全局配置单例
│   ├── safe_edit.py       # 安全编辑链核心
│   ├── safe_write.py      # 新建文件 / 整体覆盖写入
│   ├── multi_edit.py      # 跨文件原子编辑
│   ├── file_read.py       # 文件读取（带行号）
│   ├── codegraph.py       # 语义索引引擎 (AST + FTS5 + BFS)
│   ├── shell_exec.py      # 白名单命令执行
│   ├── gh_cli.py          # GitHub CLI 封装 (13 操作)
│   ├── git_smart.py       # 结构化 Git 操作
│   ├── ... (38 more)
│   └── symbol_rename.py   # Token 级重命名
├── tests/                 # 测试目录
└── docs/                  # 文档
```

## 启动流程

```
python server.py --http --port 8000
  │
  ├─ 解析命令行参数 (argparse)
  ├─ tools/config.set_config() 初始化配置
  ├─ 导入全部 44 个工具模块
  ├─ FastMCP 实例化 ("irmia-devkit")
  ├─ @mcp.tool() 装饰器注册 57 个工具
  │    ├─ 每个工具 = 薄包装层（参数适配 + json.dumps 序列化）
  │    └─ 底层调用 tools/ 中的原生 Python 函数
  ├─ HTTP 模式 → mcp.run(transport="sse")
  └─ stdio 模式 → mcp.run(transport="stdio")
```

## 工具执行流程

```
MCP Client → SSE/stdio → FastMCP → @mcp.tool() wrapper
  │
  ├─ 参数从 MCP schema 反序列化
  ├─ 传递给 tools/xxx.py 的原生函数
  ├─ 原生函数返回 dict
  │    ├─ {"ok": True, "data": {...}}       → 纯成功
  │    ├─ {"ok": False, "error": "..."}      → 纯错误
  │    └─ {"ok": ..., "proposal": "...",      → 提案协议
  │        "evidence": {...}, "options": [...]}
  └─ json.dumps() 序列化为字符串返回
```

## 响应协议

所有工具返回 JSON 字符串，遵循三形态协议：

### 形态 A: 纯成功
```json
{"ok": true, "file": "/path/to/file.py", "replaced": 1, "syntax_ok": true}
```

### 形态 B: 纯错误
```json
{"ok": false, "error": "文件不存在: /path/to/file.py"}
```

### 形态 C: 提案协议
```json
{
  "ok": false,
  "proposal": "多匹配：发现 3 处匹配",
  "evidence": {"matches": [{"line": 1, "col": 3}, {"line": 5, "col": 3}]},
  "options": ["occurrence=1", "occurrence=2", "cancel"]
}
```

## 安全架构

### 命令注入防护 (shell_exec.py)
```
DANGEROUS_RAW 黑名单: | ; & || > < $( ` \n \r %
  ├─ 命令拆分前整串检查
  └─ 每个参数逐个检查
白名单模式: npm/npx/cargo/go/pip/make/pytest/python
高风险命令两段式: pip install → allow_high_risk=true 确认
```

### SSRF 防护 (_http_utils.py)
```
Layer 1: URL 解析 → IP 检查私有网段 (6 个 IPv4 + IPv6 loopback + ULA)
Layer 2: IPv4-mapped-IPv6 提取
Layer 3: DNS 解析 → 对解析结果再次 IP 检查
Layer 4: SafeRedirectHandler → 每次 HTTP 重定向重新校验
```

### 路径穿越防护
| 工具 | 防护方式 |
|------|---------|
| file_remove | `..` 检测 + `resolve()` + 系统目录黑名单 |
| file_zip | Zip-slip: `(target_dir / entry_name).resolve()` 前缀验证 |
| http_download | `_resolve_path` 取纯文件名，写入 `~/.irmia/downloads` |
| safe_edit | 文件存在校验 + 备份到 `~/.irmia/backups` |

### SQL 注入防护 (db_query.py)
```
1. SQL 白名单: 仅 SELECT / PRAGMA
2. 数据库级只读: sqlite3.connect("file.db?mode=ro")
3. 参数化查询: params 参数
4. Row factory: sqlite3.Row 字典访问
```

## 代码智能引擎 (codegraph.py)

```
code_index(project_dir, incremental=False)
  ├─ Python: ast 模块解析（零依赖）
  ├─ 多语言: tree-sitter 解析（可选依赖）
  ├─ SQLite WAL 模式 + FTS5 全文索引
  └─ 增量模式: mtime 跟踪，仅扫描变更文件

code_explore(query) → 自然语言路由
  ├─ "X 在哪定义" / "where is X"     → FTS5 符号搜索
  ├─ "谁调用了 X" / "who calls X"    → BFS 开放调用链
  └─ "从 X 到 Y" / "X → Y"          → BFS 路径追踪

code_pack(target, depth=2, mode="both")
  └─ BFS 依赖收集 → 智能截断 (15行头+5行尾) → 2000行上限

code_diff_impact(filepaths, max_depth=3)
  └─ 从修改文件反推符号 → BFS 上游追溯调用者

code_status()
  └─ 索引健康检查: 覆盖范围 / 符号数 / 边数 / 最后索引时间
```


## 与 irmia_devkit_open 的关系

irmia_devkit_mcp 从 [irmia_devkit_open](https://github.com/irmia2026/irmia_devkit_open) (AstrBot 插件 v2.5.0) 剥离：

- 移除 AstrBot 框架依赖（_registry.py / _auth.py / main.py）
- 移除运维/非核心工具（系统信息、编码独立工具、op_log 等）
- 合并编码 3→1、时间 3→1
- 添加 MCP 协议适配层（FastMCP）
- 添加 HTTP SSE 传输
- 添加 npx / uv / pip 三种安装方式
