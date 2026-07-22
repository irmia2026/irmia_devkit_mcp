#!/usr/bin/env bash
set -e

# ── 找 Python（校验 >= 3.10） ─────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        if "$cmd" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
            PYTHON="$cmd"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Error: Python >= 3.10 not found. Install: https://python.org" >&2
    exit 1
fi

# ── 本地 venv 隔离依赖（不污染全局 site-packages） ────
DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/../.venv"
VENV_PY="$VENV/bin/python"

if [ ! -x "$VENV_PY" ]; then
    echo "[irmia-devkit] Creating local venv: $VENV" >&2
    if ! "$PYTHON" -m venv "$VENV" >&2; then
        echo "[irmia-devkit] Error: failed to create venv." >&2
        exit 1
    fi
fi

# ── 安装锁定依赖（pip 输出走 stderr，保持 stdout 纯净） ──
REQ="$DIR/../requirements.txt"
if ! "$VENV_PY" -c "import mcp, bs4, lxml, yaml, psutil; from importlib.metadata import version; expected={'mcp':'1.27.0','beautifulsoup4':'4.15.0','lxml':'6.1.1','PyYAML':'6.0.3','psutil':'7.2.2'}; raise SystemExit(0 if all(version(k)==v for k,v in expected.items()) else 1)" 2>/dev/null; then
    echo "[irmia-devkit] Installing dependencies into local venv..." >&2
    if ! "$VENV_PY" -m pip install --requirement "$REQ" -q >&2; then
        echo "[irmia-devkit] Error: dependency install failed. Check network/pip." >&2
        exit 1
    fi
fi

# ── 检查可选依赖（不自动安装，只报告，全部走 stderr） ──
check_bin() {
    local name="$1" hint="$2"
    if command -v "$name" >/dev/null 2>&1; then
        return 0
    else
        echo "[irmia-devkit] Optional: $name not found — $hint" >&2
        return 1
    fi
}
check_pip() {
    local pkg="$1" hint="$2"
    if "$VENV_PY" -c "import $pkg" 2>/dev/null; then
        return 0
    else
        echo "[irmia-devkit] Optional: $pkg not found — $hint" >&2
        return 1
    fi
}

check_bin  rg       "rg_search will use Python fallback. Install: brew install ripgrep / apt install ripgrep" || true
check_bin  gh       "gh_pr/gh_issue need it. Install: https://cli.github.com" || true
check_bin  ruff     "lint_runner prefers ruff. Install: pip install ruff" || true
check_pip tree_sitter "code_index non-Python langs need it. Install: pip install tree-sitter" || true

# ── 启动 ───────────────────────────────────────────────
exec "$VENV_PY" "$DIR/../server.py" "$@"
