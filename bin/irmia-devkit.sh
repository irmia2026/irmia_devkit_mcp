#!/usr/bin/env bash
set -e

# ── 找 Python ──────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Error: Python >= 3.10 not found. Install: https://python.org" >&2
    exit 1
fi

# ── 自动安装 mcp ───────────────────────────────────────
if ! $PYTHON -c "import mcp" 2>/dev/null; then
    echo "[irmia-devkit] Installing mcp..." >&2
    $PYTHON -m pip install 'mcp>=1.0.0' -q
fi

# ── 检查可选依赖（不自动安装，只报告） ────────────────
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
    if $PYTHON -c "import $pkg" 2>/dev/null; then
        return 0
    else
        echo "[irmia-devkit] Optional: $pkg not found — $hint" >&2
        return 1
    fi
}

check_bin  rg       "rg_search will use Python fallback. Install: brew install ripgrep / apt install ripgrep"
check_bin  gh       "gh_pr/gh_issue need it. Install: https://cli.github.com"
check_bin  ruff     "lint_runner prefers ruff. Install: pip install ruff"
check_pip bs4       "html_extract needs it. Install: pip install beautifulsoup4"
check_pip tree_sitter "code_index non-Python langs need it. Install: pip install tree-sitter"

# ── 启动 ───────────────────────────────────────────────
DIR="$(cd "$(dirname "$0")" && pwd)"
exec $PYTHON "$DIR/../server.py" "$@"
