#!/usr/bin/env bash
set -euo pipefail

uv run mkdocs serve -a 0.0.0.0:5000
