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

DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$PYTHON" "$DIR/irmia-devkit.py" "$@"
