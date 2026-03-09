#!/usr/bin/env bash
set -euo pipefail

uv run --python 3.14 pytest --cov=tests --cov-report=term-missing --cov-report=html -v
