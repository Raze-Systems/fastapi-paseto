# Changes

## 2026-03-09T01:47:02-03:00

- Migrated packaging metadata in `pyproject.toml` from `flit` tables to PEP 621 `[project]` metadata.
- Switched the build backend from `flit_core` to `uv_build`.
- Moved the package version source of truth to `pyproject.toml` and updated `fastapi_paseto_auth.__version__` to read from installed package metadata with a fallback to `0.6.0`.
- Removed the legacy `Pipfile` and `Pipfile.lock`.
- Added `.python-version` with `3.10` so local `uv` workflows resolve the intended interpreter by default.
- Generated and added `uv.lock` for the `uv`-managed development environment.
- Updated declared runtime dependencies to match the previous `Pipfile.lock` versions:
  - `fastapi==0.85.0`
  - `pyseto==1.6.10`
  - `pydantic==1.10.2`
- Updated declared test dependencies to track the previous lockfile behavior:
  - `anyio==3.6.1`
  - `sniffio==1.3.0`
  - `pytest==7.1.3`
  - `pytest-cov==3.0.0`
  - `coveralls==3.3.1`
  - `requests==2.28.1`
  - `urllib3==1.26.12`
- Kept doc and dev extras in `pyproject.toml` and preserved the existing MkDocs and `uvicorn` setup.
- Updated `scripts/tests.sh` to run tests through `uv run`.
- Updated `scripts/docs-live.sh` to run the docs server through `uv run`.
- Updated `docs/contributing.md` to replace `Pipenv`/`flit` setup instructions with `uv sync --extra test --extra doc --extra dev`.
- Updated `.gitignore` to ignore `.venv/` and `site/`.
- Verified that `uv build` succeeds and that `uv run mkdocs build --strict` succeeds after the migration.
- Investigated the hanging `TestClient` behavior and confirmed it is caused by the current sandbox environment blocking thread-to-event-loop wakeups used by `asyncio`, `anyio`, and Starlette's `TestClient`, not by the packaging migration itself.
