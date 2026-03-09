<h1 align="left" style="margin-bottom: 20px; font-weight: 500; font-size: 50px; color: black;">
  FastAPI PASETO
</h1>

---

**Source Code**: <a href="https://github.com/Raze-Systems/fastapi-paseto" target="_blank">https://github.com/Raze-Systems/fastapi-paseto</a>

**Maintained by**: Raze Systems and Alexandre Teles

---

FastAPI extension that provides PASETO (**P**lastform-**A**gnostic **SE**curity **TO**kens) Auth support\
PASETO are a simpler, yet more secure alternative to JWTs.

If you were familiar with flask-jwt-extended or fastapi-jwt-auth this extension suitable for you, as this is forked from fastapi-jwt-auth which in turn used flask-jwt-extended as motivation

## Features
- Access tokens and refresh tokens
- Freshness Tokens
- Revoking Tokens
- Support for adding custom claims to Tokens
- Built-in Base64 Encoding of Tokens
- Custom token types

## Installation
The easiest way to start working with this extension with pip

This project currently targets Python 3.14+.

```bash
pip install fastapi-paseto
```

`AuthPASETO.load_config()` now expects a callback that returns either a plain
mapping or a `pydantic-settings` `BaseSettings` instance. A minimal setup looks
like this:

```python
@AuthPASETO.load_config
def get_config():
    return {"authpaseto_secret_key": "secret"}
```

## Roadmap
- Support for WebSocket authorization

## FAQ
- **Where's support for tokens in cookies?**\
This project focuses on header-based PASETO authentication and only includes the features required for that workflow.\
Cookie storage is intentionally out of scope for now because it adds a large amount of behavior that does not fit the current design.\
If there is strong demand and a solid implementation, contributions adding cookie support can still be considered.

## License
This project is licensed under the terms of the MIT license.
