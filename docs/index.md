# FastAPI PASETO

FastAPI PASETO adds PASETO-based authentication helpers to FastAPI applications.
It supports access tokens, refresh tokens, custom token types, denylist checks,
HTTP and websocket authentication flows, and per-route transport overrides.

PASETO tokens are a simpler and safer alternative to JWTs for many use cases.
If you have used `flask-jwt-extended` or `fastapi-jwt-auth`, the dependency and
token-creation flow should feel familiar.

## Features

- Access tokens and refresh tokens
- Fresh access token checks
- Revoking tokens with a denylist callback
- WebSocket authorization via headers or query parameters
- JSON body token transport for HTTP routes
- Custom claims and custom token types
- Base64-encoded token support

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

If you need a fully reproducible installation, pin a commit hash instead of a
tag and verify the release artifacts described in the Supply Chain Security
section.

## Minimal Configuration

`AuthPASETO.load_config()` expects a callback that returns either a plain
mapping or a `pydantic-settings` `BaseSettings` instance.

```python
@AuthPASETO.load_config
def get_config():
    return {"authpaseto_secret_key": "secret"}
```

## Next Steps

- Start with [Basic Usage](usage/basic.md)
- See [JSON Body Tokens](usage/json.md) for HTTP body transport
- See [WebSocket Usage](usage/websocket.md) for header and query auth
- See [Examples](examples.md) for the full example catalog
- See [API Documentation](api-doc.md) for the full callable reference
