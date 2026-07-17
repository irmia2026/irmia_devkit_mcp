# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **外部工具自动检测**: 启动时自动扫描项目 `vendor/` 目录或系统 PATH 中的 `es`/`rg`/`fd` 路径，写入 `~/.irmia/mcp_config.json`，扫描不到时打印安装指引。
- **跨平台 auto_config**: Linux / macOS 下 `es_path` 自动回退 `locate`/`fd`，不产生误报警。
- **内置二进制支持**: `vendor/` 目录可放置 `rg.exe` / `es.exe` / `fd.exe`（Windows）及 `rg` / `fd`（Linux / macOS），启动时优先使用。

### Removed
- **Git & GitHub 工具集**: 移除 `git_status`、`git_diff`、`git_log`、`git_commit`、`git_branch`、`git_remote`、`git_push`、`git_changelog` 以及 `gh_pr`、`gh_issue`、`gh_release`、`gh_repo` 共 12 个工具。Git 操作更适合由宿主 Agent 或独立 Git 工作流处理。
- **审计工具**: 移除 `tool_stats` 和 `op_log` 及其内存 / SQLite 审计链，简化 `server.py` 架构，移除对 `mcp.tool()` 的 monkey-patch。
- **文本处理工具**: 移除 `csv_parse`、`csv_gen`、`md_strip`、`log_parse`。
- **扩展工具**: 移除 `project_init`、`semver_compare`。
- **命令执行工具**: 移除 `shell_exec`。`test_runner` 继续保留内置的安全命令校验逻辑。
- **相关配置**: 从 `mcp_config.json` 和全局配置中移除 `gh_path` 与 `op_log_db`。

### Changed
- **工具数量**: 65 → **44**。
- **文档重写**: README.md、ARCHITECTURE.md 同步更新，移除已删工具的引用和描述。

### Security
- **本地部署锁定**: `--host` 参数仅接受 `127.0.0.1` / `localhost` / `::1`，远程地址启动时直接拒绝。

## [v2.6.0] — 2026-06-24 — MCP 初始发布

### Added
- 首次 MCP 发布：从 `irmia_devkit_open` v2.6.0 迁移 65 个工具为 MCP Server。
- `server.py`: FastMCP 主机，支持 stdio 和 SSE/HTTP 传输。
- `tools/auto_config.py`: 外部工具自动检测与配置管理。
- 新增 `file_move` 工具（批量移动，同分区 O(1) rename，跨分区 copy+delete）。
- 工具数 64 → **65**。

### Changed
- 工具实现与上游 `irmia_devkit_open` v2.6.0 完全同步。
- `op_log` 参数 `tool` → `tool_name`（避免与框架参数冲突）。
- ARCHITECTURE.md 重写为 MCP 版本上下文。
- 同步全工具深度 review 修复：CRLF/尾随空格容错、next_call 消失修复、context 暴增优化。

### Removed
- 移除 AstrBot 依赖：`_auth.py`（MCP 层自行处理权限）、AstrBot 特定测试。

---

> **以下为上游 `irmia_devkit_open` 的完整版本历史（v1.2.0 → v2.6.0）。**
> MCP 版本继承所有这些功能改进；但当前 `Unreleased` 版本已移除部分工具，详见上方 Removed 节。

## v2.6.0 (upstream) — 增强文件读取 + 全量安全审查修复

- **新工具**: `safe_read` — 增强版安全文件读取，支持编码自动检测、hex 预览、head/tail、代码骨架提取。
- **安全修复**: SSRF IPv4 八进制/十六进制/短写法绕过；`shell_exec` 参数路径校验；`file_remove` symlink 跟随修复；`file_zip` symlink 打包修复。
- **性能修复**: `safe_write` 大文件预览限制、`safe_read` tail 模式优化。
- **Bug 修复**: `safe_read` max_depth、`sys_snapshot` UnboundLocalError。

## v2.5.7 — 配置页重构 + Release 安装包补齐

- 群配置页卡片化布局，支持真实 QQ 群列表、群级工具组开关。
- GitHub PR review 修复：`--body-file` 传递避免 shell 截断。
- Release 附加可安装 ZIP 包。

## v2.5.6 — codegraph 性能修复 + review 安全加固

- codegraph 索引从 O(N×M) SQL 优化到 O(1) 哈希查表（500+ 文件项目从 >120s → 3.8s）。
- codegraph P0 Bug: 修复 `project_dir` 路径不一致导致的"索引为空"误报。
- 安全加固: `safe_write` 路径穿越、`symbol_rename` 提案协议。

## v2.5.5 — MCP 改动同步 + 安全修复 + 文档对齐

- 工具合并: `base64_`+`hex_`+`url_` → `encode_decode`; `time_now`+`time_convert`+`time_diff` → `time`。
- 删除非核心工具: `file_watch`、`svg_render`、`json_schema_val`、`regex_test`。
- `shell_exec` ReDoS 防护、`rg_search` Python fallback ReDoS 防护、`op_log` 扩展敏感词。

## v2.5.0 — 测试/执行/审计/重命名能力补完

- 新工具: `test_runner`、`multi_edit`、`shell_exec`、`op_log`、`symbol_rename`。
- `shell_exec` 七层防御沙箱。`op_log` SQLite 审计日志（sensitive 参数脱敏）。
- `protect_tool` 接入 `op_log` 审计。

## v2.4.5 — 语义索引 5 工具 + gh_cli 自动定位

- `code_index`、`code_explore`、`code_diff_impact`、`code_pack`、`code_status` 上线。
- Python AST 零依赖解析 + 可选 tree-sitter 多语言。
- `gh_cli` 移除本地路径硬编码，全盘自动搜索。

## v2.4.0 — 代码语义索引 + L2 原生工具摘除

- `code_index` / `code_explore`: Python AST + SQLite FTS5，三级搜索（LIKE → FTS5 → hint）。
- L2 原生工具摘除恢复（当 devkit 替代品可用时）。

## v2.3.7 — 工具管理权收回 + 防御上线

- handler_module_path 修正，工具管理权从 AstrBot 收回。

## v2.3.6 — 群级 WebUI + handler_module_path 修正

- 群级权限配置 Web 管理面板。

## v2.3.5 — 双层权限防线 + 代码审查修复

- protect_tool 权限守卫、_auth_guard LLM 请求级过滤。
- 三轮代码审查修复 18 项问题。

## v2.3.0 — 基础层补完 (60→61)

- `rg_search` 上线；safe_edit/file_patch whitespace-tolerant 匹配。
- linter ruff↔pylint 互 fallback。架构重构 `_run_cmd()`。

## v2.2.0 — 统一交互协议

- proposal_reply() 提案协议：17 个工具的失败返回统一为四字段结构化提案。
- 51 个 pytest 测试用例。

## v2.0.0 — 生态扩展 (60→63)

- tool_stats、db_query、dep_scan 上线。

## v1.8 — 质量层 (59→60)

- lint_runner 上线。

## v1.7 — 决策层 (57→59)

- project_init、git_changelog 上线。

## v1.6 — 架构收口 + 安全加固 (54→57)

- GhCliTool 拆为 4 独立工具；注册表外移。

## v1.5 — 新工具 (49→54)

- log_parse、file_watch、config_diff、svg_render、json_schema_val。

## v1.4 — 质量打磨 (41→49)

- encode_utils 拆为 6 工具；time_utils 拆为 4 工具。

## v1.3 — 跨平台 (41)

- Linux proc_list/disk_info/sys_snapshot 回退。

## v1.2.1 — Bugfix (41)

- file_patch 编码保留修复。

## v1.2.0 — 初始发布 (42→41)

- 配置系统上线；5 处硬编码路径脱敏。
