#!/usr/bin/env bash
set -euo pipefail

uv run --python 3.14 mkdocs serve -a 0.0.0.0:5000
