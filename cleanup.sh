#!/usr/bin/env bash
set -euo pipefail

# cleanup.sh — Remove files and directories generated while running the project.
# Safe to run from the repo root; only removes known build/artifact paths.

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Cleaning up generated files..."

# Python cache
rm -rf __pycache__/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name '*.pyc' -delete 2>/dev/null || true

# Test & lint caches
rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ .benchmarks/ .hypothesis/

# Coverage
rm -rf .coverage coverage.xml htmlcov/

# Build artifacts
rm -rf *.egg-info/ dist/ build/ *.egg

# Logs
find . -type f -name '*.log' -delete 2>/dev/null || true

# Docs build
rm -rf site/

echo "Done."
