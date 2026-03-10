<h1 align="left" style="margin-bottom: 20px; font-weight: 500; font-size: 50px; color: black;">
  FastAPI PASETO
</h1>

---

**Source Code**: <a href="https://github.com/Raze-Systems/fastapi-paseto" target="_blank">https://github.com/Raze-Systems/fastapi-paseto</a>

**Maintained by**: Raze Systems and Alexandre Teles

---

FastAPI extension that provides PASETO (**P**latform-**A**gnostic **SE**curity **TO**kens) Auth support.
PASETO tokens are a simpler, yet more secure alternative to JWTs.

If you are familiar with `flask-jwt-extended` or `fastapi-jwt-auth`, this
extension should feel familiar. It is forked from `fastapi-jwt-auth`, which in
turn was inspired by `flask-jwt-extended`.

## Features
- Access tokens and refresh tokens
- Freshness Tokens
- Revoking Tokens
- WebSocket authorization
- Support for adding custom claims to Tokens
- Built-in Base64 Encoding of Tokens
- Custom token types
- PASETO footers and implicit assertions

## Installation

This project is not published on PyPI. Install it from an immutable Git tag or
commit hash instead.

This project currently targets Python 3.14+.

```bash
uv add "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@vX.Y.Z"
```

```bash
pip install "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@vX.Y.Z"
```

Releases are built from GitHub Actions after a successful semantic release on
`main`. Each release publishes the wheel and source distribution as GitHub
workflow artifacts and as downloadable assets on the corresponding GitHub
Release.

`AuthPASETO.load_config()` now expects a callback that returns either a plain
mapping or a `pydantic-settings` `BaseSettings` instance. A minimal setup looks
like this:

```python
@AuthPASETO.load_config
def get_config():
    return {"authpaseto_secret_key": "secret"}
```

## Release Process
Releases are automated with conventional commits and semantic versioning.
Commits merged into `main` should follow the Conventional Commits format, for
example `feat: add denylist cache metrics` or `fix: reject malformed token
headers`.

The release workflow runs tests, builds the package, builds the docs, creates
the next semantic version, updates the generated changelog, publishes the
distribution as GitHub Release assets and workflow artifacts, and deploys the
latest docs to GitHub Pages.
The first automated release should start from a bootstrap tag that matches the
current project version.

## Supply Chain Security
Each automated release publishes the wheel, source distribution, `SHA256SUMS`,
and SPDX JSON SBOM files as GitHub Release assets and workflow artifacts. The
release workflow also creates keyless GitHub artifact attestations for both
build provenance and SPDX SBOMs.

To verify a release locally with the GitHub CLI:

```bash
gh release verify vX.Y.Z --repo Raze-Systems/fastapi-paseto
gh release verify-asset vX.Y.Z ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto
gh attestation verify ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto --signer-workflow .github/workflows/release.yml
gh attestation verify ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto --signer-workflow .github/workflows/release.yml --predicate-type https://spdx.dev/Document/v2.3
```

If you prefer to install from a commit hash instead of a release tag:

```bash
uv add "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@<commit-sha>"
```

```bash
pip install "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@<commit-sha>"
```

`pip` and `uv` record VCS origin metadata in `direct_url.json`, which helps
with auditing later, but mutable branch installs cannot be strongly verified
after the fact. Use a signed commit or tag plus the matching release assets if
you need a verifiable supply-chain trail.

## License
This project is licensed under the terms of the MIT license.
