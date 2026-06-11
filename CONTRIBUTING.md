# Contributing

## 环境

```bash
git clone https://github.com/irmia2026/irmia_devkit_mcp.git
cd irmia_devkit_mcp
pip install -e . && pip install pytest
```

## 新增工具

### 1. 创建模块

```python
# tools/my_tool.py
from __future__ import annotations
from ._helpers import proposal_reply

def do_something(param: str) -> dict:
    if not param:
        return {"ok": False, "error": "param must not be empty"}

    if need_choice:
        return proposal_reply(
            False,
            "多个选项，选择一个",
            evidence={"count": 3},
            options=["选项 A", "选项 B"],
        )

    return {"ok": True, "result": f"processed: {param}"}
```

### 2. 注册到 server.py

```python
from tools.my_tool import do_something as _do_something

@mcp.tool()
def my_action(param: str) -> str:
    """何时调用此工具的一句话描述。

    Args:
        param: 参数说明
    """
    result = _do_something(param)
    return json.dumps(result, ensure_ascii=False)
```

### 3. 运行测试

```bash
pytest tests/ -v
```

## 返回值规范

三形态，靠 bottom 函数返回的 dict 中是否存在特定 key 分流：

| 形态 | 条件 | 示例 |
|------|------|------|
| 纯成功 | ok=True，无特殊 key | {"ok": True, "result": "..."} |
| 纯错误 | ok=False，无特殊 key | {"ok": False, "error": "无法读取"} |
| 提案协议 | 含 proposal / options / evidence / next_call / stdout / stderr 任一 | {"ok": False, "proposal": "...", "options": [...]} |

**关键规则：**

- 永远 return dict，不 raise。工具函数和工具内调用的子函数都一样。
- proposal + options 成对出现。evidence 有数据时必带。
- next_call 格式：{"tool": "tool_name", "params": {...}}。
- 破坏性操作（删除、高风险命令）用 proposal (ok=False) + boolean 确认参数做两段式。LLM 必须修改参数重试。

## 安全

| 关注点 | 文件 | 方式 |
|--------|------|------|
| 命令注入 | shell_exec.py | DANGEROUS_RAW 黑名单 (| ; & || > < $( ` 
 
 %) + 白名单命令 |
| SSRF | _http_utils.py | URL->IP->DNS->重定向 四层检测 |
| 路径穿越 | file_remove.py | .. 检测 + resolve() + 系统目录黑名单 |
| ZIP slip | file_zip.py | target_dir/entry_name resolve 前缀验证 |
| SQL 注入 | db_query.py | SELECT/PRAGMA 白名单 + mode=ro + 参数化 |

## 依赖管理

纯 Python 标准库工具 49 个。8 个工具需要外部程序——未安装时优雅降级，不阻塞：

| 工具 | 需外部程序 | 降级行为 | 自动安装 |
|------|-----------|---------|:--:|
| rg_search | ripgrep | Python os.walk 扫描 | — |
| es_search | Everything/locate/fd | Python os.walk 扫描 | — |
| gh_* (4个) | GitHub CLI | 返回安装指引 | — |
| lint_runner | ruff/pylint/eslint | 自动 fallback | — |
| syntax_check | go/nim/node | skipped=true | — |
| test_runner | go/cargo/node | 回退 pytest | — |
| code_index | tree-sitter-* | 跳过非 Python | — |
| html_extract | beautifulsoup4 | 返回安装指引 | pip install bs4 |

启动脚本 (bin/) 会自动 pip install mcp。其余外部程序由用户按需安装。

## 发布检查清单

- [ ] python server.py — 正常启动 stdio
- [ ] python server.py --http — 正常启动 HTTP SSE
- [ ] 57 工具全部注册
- [ ] 安全门禁通过 (& % | ; 被 reject)
