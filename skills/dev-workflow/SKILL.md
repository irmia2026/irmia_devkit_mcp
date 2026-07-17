---
name: dev-workflow
description: >
  收到编码任务时强制走安全工作流。触发：写代码、改代码、修bug、重构、实现功能、修改文件。
  核心原则：先确认后执行、自动备份回滚、语法门禁。Git 操作由宿主 Agent 负责。
  可用工具：safe_edit、safe_read、safe_write、safe_backups、safe_rollback、multi_edit、
  file_patch、file_remove、file_move、syntax_check、lint_runner、test_runner、
  es_search、rg_search、dir_tree、dir_list、file_diff、file_hash、
  code_index、code_explore、code_pack、code_diff_impact、code_status、symbol_rename、
  dep_scan、db_query、http_get、http_post、http_download、config_diff。
---

# 开发工作流 (MCP 版)

> 本 Skill 适用于 irmia-devkit MCP Server。Git 操作（status/commit/push/PR）由宿主 Agent 负责，不在此工具箱范围内。

## 核心原则

```
一边确认一边推进。
该停的时候停（方案阶段、计划阶段、审查后），
该走的时候走（小修改、已验证的步骤）。
不等用户催，也不用写死的路由表。
```

## 改代码之前

1. `safe_backups` — 看一眼有没有旧备份可用
2. `es_search` / `rg_search` / `dir_tree` / `dir_list` — 需要时先了解项目结构
3. 首次进项目 → `code_index` 建立语义索引
4. 代码理解 → 走「代码智能工具组」决策树（见下方完整章节）

## 节奏感

- **需求模糊** → 先 brainstorming 探索方案，确认后再动
- **需求清晰但复杂** → 先 writing-plans 拆任务，确认后再执行
- **简单修改** → 直接 safe_edit
- **审完** → 问是否修 Critical/High，修完交还给宿主 Agent 做 Git 提交

不需要路由表，不需要流水线引擎。用判断力。

## safe_edit 铁律

- 改代码**必须**用 `safe_edit`，禁止 `file_write` 或裸 `file_patch`
- `safe_edit` 自动跑 `syntax_check`，语法错就分析根因重新改
- 语法失败自动回滚，不要手动恢复
- 回滚后工具返回 `proposal` 和 `options`——直接看提案，选一个选项，重试
- 代码改完后用 `lint_runner` 检查质量（ruff→pylint 自动 fallback）
- 想回到之前版本 → `safe_rollback`
- 跨文件批量改 → `multi_edit`（原子提交，任一失败全体回滚）
- 新建文件 → `safe_write`（自动创建目录，语法失败不阻塞）

## safe_read 铁律

- 读代码文件**必须**用 `safe_read`，不要用任何其他阅读工具
- 大文件分页：`head=100` 或 `tail=100`
- 二进制文件自动切换 hex 模式，不抛异常
- 编码自动检测（utf-8/gbk/latin-1），不用手动指定

## 代码智能工具组

> 图优先，grep 兜底。能用图就不要 rg_search。

### 心智模型

```
code_index（一次性建索引）
  │
  ├─ 查符号定义/调用者 ──→ code_explore
  ├─ 修 bug 要完整上下文 ──→ code_pack
  ├─ 改完了查影响范围 ──→ code_diff_impact
  └─ explore 返回空 ──→ code_status（再 fallback rg_search）
```

### 决策树

| 意图 | 用这个 |
|------|--------|
| 第一次进项目 | `code_index`（后续增量 `incremental=true`） |
| 「X 在哪定义」「谁调了 X」 | `code_explore("X")` |
| 修 X 的 bug，要 X + 依赖链全部源码 | `code_pack("X", depth=2)` |
| 刚改了文件 Y，会影响什么 | `code_diff_impact(["Y"])` |
| explore 查不到，怀疑索引坏了 | `code_status` |
| 索引正常但 explore 查不到 | fallback → `rg_search` |

### 铁律

1. **图优先** — 能 code_explore 就不要 rg_search
2. **建索引一次性** — 进项目 `code_index`，后续增量，不要每查一次重建
3. **失败先查 status** — explore 返回空 → 先 `code_status`，再怀疑查询词
4. **打包替代多次 explore** — 需要 3+ 符号源码才能理解流程 → 直接 `code_pack`
5. **改完必查影响** — 提交前 `code_diff_impact`，确认不炸隐藏调用者
6. **用符号名而非自然语言** — `_auth_guard` 而非「权限守卫怎么工作」
7. **safe_edit 自动增量索引** — 改完代码自动更新索引，不需要手动 `code_index --incremental`

### 反模式

- ❌ 不建索引就调 explore
- ❌ 每查一个符号重新 code_index
- ❌ explore 失败直接 rg_search，不查 code_status
- ❌ 用 code_pack 查单个符号定义（用 explore 更快）
- ❌ 用 explore 查改动影响（用 diff_impact，它从文件反推符号树）
- ❌ 改 5 个文件但 diff_impact 只查 1 个（传列表一次查全）
