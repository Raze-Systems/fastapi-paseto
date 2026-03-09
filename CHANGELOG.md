# Changes

## 2026-03-09T16:10:00-03:00

- Renamed the published project from `fastapi-paseto-auth` to `fastapi-paseto`.
- Renamed the import package from `fastapi_paseto_auth` to `fastapi_paseto` and updated examples, tests, and docs to match.
- Repointed repository metadata, badges, and issue links to `Raze-Systems/fastapi-paseto`.
- Updated package authorship to `Raze Systems` and `Alexandre Teles`, with `Alexandre Teles <1757773+alexandreteles@users.noreply.github.com>` as the maintainer.
- Removed the old public documentation URL from package metadata and README.
- Preserved the original MIT copyright notice and added fork copyright lines for the current project owners.

## 2026-03-09T15:03:11-03:00

- Upgraded the runtime stack to `fastapi==0.135.1`, `pydantic==2.12.5`, and `pydantic-settings==2.12.0`; kept `pyseto==1.9.1` because it is already current and compatible.
- Reworked config validation onto Pydantic v2 APIs in `src/fastapi_paseto/config.py`, replacing v1 validators and `Config` usage with `field_validator`, `model_validator`, and `model_config`.
- Changed `AuthPASETO.load_config()` to accept a callback returning either a plain mapping or a `pydantic-settings` `BaseSettings` instance; removed the old `list[tuple]`/generic Pydantic-object contract.
- Fixed `AuthPASETO` dependency injection compatibility with modern FastAPI while preserving direct `AuthPASETO()` construction for tests and non-request token creation.
- Removed mutable default arguments from token creation methods and tightened related typing in the auth implementation.
- Updated tests to target the new config contract and modern Starlette `TestClient` behavior.
- Updated examples and API docs so they no longer show returning `pydantic.BaseModel` config objects from `load_config()`.
- Regenerated `uv.lock` and verified that `uv run pytest -q` succeeds with `44 passed`.

## 2026-03-09T14:25:00-03:00

- Added an autouse test fixture in `tests/conftest.py` that resets `AuthPASETO`'s class-level state before and after every test so test outcomes no longer depend on execution order.
- Added a shared `configure_auth()` fixture in `tests/conftest.py` and updated the request-based test modules to declare their own auth configuration instead of inheriting it implicitly from previous tests.
- Reworked `tests/test_decode_token.py` to replace wall-clock `time.sleep()` expiry checks with explicit `exp` claims, removing timing-based flakiness while preserving the expiry and leeway assertions.
- Reworked `tests/test_denylist.py` so the denylist store and revoked-token setup are isolated per test instead of relying on module-global mutation across parametrized cases.
- Updated `tests/test_config.py::test_secret_key_not_exist` to exercise the decode failure path directly, avoiding the old `TestClient` deadlock behavior triggered by that scenario on the current dependency stack.
- Verified that `uv run --python 3.14 pytest -q` succeeds with `44 passed`.
- Verified that `bash scripts/tests.sh` succeeds with `44 passed` and coverage output generation.
- Rechecked the sandbox behavior and confirmed the remaining environment-specific issue is still `uv` cache access under `/home/alexs/.cache/uv`, not a reproducible test failure in the repo itself.

## 2026-03-09T02:46:38-03:00

- Moved the `fastapi_paseto` package into `src/fastapi_paseto` to match `uv_build`'s default packaged-library layout while preserving the public import path.
- Removed the flat-layout override from `pyproject.toml` so the build now follows the default `src/` module discovery behavior.
- Replaced the published `test`, `doc`, and `dev` extras with a single local `dev` dependency group in `pyproject.toml`.
- Updated `docs/contributing.md` to use `uv sync --python 3.14` for the default contributor setup and `uv sync --python 3.14 --no-dev` for a production-like local environment.
- Updated the GitHub Actions test and docs workflows to install dependencies with `uv sync --python 3.14` so CI follows the new dependency-group layout.
- Regenerated `uv.lock` so it records the new `dev` dependency group instead of published extras metadata.
- Verified that `uv lock`, `uv build`, `uv sync --python 3.14`, `uv sync --python 3.14 --no-dev`, and `uv run --python 3.14 mkdocs build --strict` all succeed after the restructure.
- Verified that `uv run --python 3.14 python -c "import fastapi_paseto; print(fastapi_paseto.__file__)"` resolves to the package under `src/`.
- Rechecked the test suite and confirmed the remaining hang still occurs in `tests/test_config.py::test_secret_key_not_exist`, so there is no new packaging-specific regression identified from this restructure.

## 2026-03-09T03:10:00-03:00

- Updated the supported interpreter target from Python 3.10 to Python 3.14 in `pyproject.toml`, `.python-version`, contributor docs, README installation notes, helper scripts, and GitHub Actions workflows.
- Refreshed the direct runtime pins needed for Python 3.14 compatibility:
  - `pydantic==1.10.25`
  - `pyseto==1.9.1`
- Refreshed the test tooling pins needed for Python 3.14 compatibility:
  - `pytest==8.4.1`
  - `pytest-cov==6.2.1`
  - `coveralls==4.0.1`
- Updated `scripts/tests.sh` and `scripts/docs-live.sh` to run explicitly on Python 3.14 through `uv run --python 3.14`.
- Reworked the GitHub Actions workflows to use `uv`-managed Python 3.14 environments instead of the old `flit`-based setup, and changed the docs workflow to build on pull requests while only deploying on pushes to `master`.
- Regenerated `uv.lock` against Python 3.14, which updated the transitive dependency set, including `cryptography`.
- Verified on Python 3.14 that `uv run pytest --cov=tests --cov-report=term-missing --cov-report=html -v`, `uv run mkdocs build --strict`, and `uv build` all succeed.

## 2026-03-09T01:47:02-03:00

- Migrated packaging metadata in `pyproject.toml` from `flit` tables to PEP 621 `[project]` metadata.
- Switched the build backend from `flit_core` to `uv_build`.
- Moved the package version source of truth to `pyproject.toml` and updated `fastapi_paseto.__version__` to read from installed package metadata with a fallback to `0.6.0`.
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
