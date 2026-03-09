#!/usr/bin/env bash
set -euo pipefail

uv run pytest --cov=tests --cov-report=term-missing --cov-report=html -v
