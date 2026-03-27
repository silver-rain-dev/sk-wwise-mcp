#!/usr/bin/env bash
set -e

echo ""
echo "SK Wwise MCP — Setup"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check for uv
if command -v uv &> /dev/null; then
    echo "Found uv, using it for setup..."
    uv run setup.py
    exit 0
fi

# Check for python3
if command -v python3 &> /dev/null; then
    echo "Found python3, using it for setup..."
    python3 setup.py
    exit 0
fi

# Check for python
if command -v python &> /dev/null; then
    echo "Found python, using it for setup..."
    python setup.py
    exit 0
fi

echo "ERROR: Neither uv nor python found. Please install one of:"
echo "  - uv: https://docs.astral.sh/uv/getting-started/installation/"
echo "  - Python 3.12+: https://www.python.org/downloads/"
exit 1
