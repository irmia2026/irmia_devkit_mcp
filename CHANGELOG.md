# Changelog


## 1.0.1 (2026-06-11)

### 新增

- **safe_write 工具** — 新建文件 / 整体覆盖写入（safe_edit 的姊妹工具）。新建自动创建父目录，语法检查失败不阻塞（无旧版本可回滚）。overwrite=true 时先备份再覆盖，语法检查失败自动回滚。

## 1.0.0 (2026-06-11)

Initial release — 从 [irmia_devkit_open](https://github.com/irmia2026/irmia_devkit_open) v2.5.0 剥离并重构为独立 MCP 服务。

### 新增

- **MCP 协议适配** — FastMCP 框架，56 个工具，HTTP SSE + stdio 双传输模式
- **三种安装方式** — npx / uv / pip 全部支持
- **file_read 工具** — 带行号、编码检测、二进制检测、CRLF 检测的极致文件读取
- **CodeGraph TTL 缓存** — 5 分钟连接缓存，避免每次 code_explore 重建 SQLite 连接
- **safe_edit 自动增量索引** — 编辑 .py/.go/.rs/.js/.ts 成功后自动更新语义索引
- **HTTP SSE 传输** — 远程部署模式，一行 URL 接入
- **结构化 proposal 扩展** — http_get/post/download/file_diff 全面追加 proposal 引导

### 变更（相对 irmia_devkit_open）

- **移除** AstrBot 框架依赖（_registry.py / _auth.py / main.py）
- **合并** 编码工具：base64 + url_enc + hex_enc → `encode_decode` (action + format)
- **合并** 时间工具：time_now + time_convert + time_diff → `time` (action)
- **移除** 非核心工具：system info(4)、op_log / tool_stats、svg_render / json_schema_val、file_watch
- **移除** es_search 的 Windows Everything 强依赖，保留 locate/fd/Python 三层 fallback
- **Safety fix**: shell_exec DANGEROUS_RAW 添加 `&` 和 `%` 字符
- **Protocol fix**: symbol_rename 跨文件拦截改用 proposal_reply 三件套
- **Protocol fix**: http_get 错误路径添加 status 键
- **Protocol fix**: file_remove 系统目录拦截添加 options
- **Annotation fix**: gh_cli.py / http_get.py 添加 `from __future__ import annotations`
- **Semantics fix**: syntax_check 编译器缺失返回 ok=False（原为 ok=True）

### 工具清单

| 分组 | 原项目 | MCP |
|------|:---:|:---:|
| 安全编辑链 | 9 | 10 (+file_read, +safe_write) |
| Git & GitHub | 11 | 12 (+git_remote, +gh_release/repo) |
| 文件 & 搜索 | 12 | 9 |
| 网络 | 3 | 3 |
| 执行 | 2 | 1 |
| 代码智能 | 6 | 6 (+code_status) |
| 文本处理 | 10 | 8 |
| 编码 | 3 | 1 (合并) |
| 时间 | 3 | 1 (合并) |
| 扩展/数据 | 8 | 6 |
| **合计** | **71** | **57** |
