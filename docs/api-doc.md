This page documents the public `AuthPASETO` API and its related helpers.

## Configuration Decorators

### `load_config(callback)`

Registers the callback that loads class-level configuration for `AuthPASETO`.

- The callback must return either a plain mapping or a `pydantic-settings`
  `BaseSettings` instance.
- Keys are normalized to lowercase before validation.
- The callback runs when the decorator is applied, not lazily per request.

### `token_in_denylist_loader(callback)`

Registers the callback used to decide whether a decoded token has been revoked.

- The callback receives the decoded token payload as `dict[str, object]`.
- Return `True` to reject the token, or `False` to allow it.
- This callback is only consulted when `authpaseto_denylist_enabled=True`.

## Request Validation

### `paseto_required(optional=False, fresh=False, refresh_token=False, type=None, base64_encoded=False, location=None, token_key=None, token_prefix=None, token=None, implicit_assertion=b"")`

Validates the current request or websocket connection against the supplied token
requirements.

Parameters:

- `optional`: allow the route to continue when no token is present or when the
  token cannot be decoded.
- `fresh`: require a fresh access token.
- `refresh_token`: require a refresh token instead of an access token.
- `type`: require a custom token type produced by `create_token()`.
- `base64_encoded`: decode the token from base64 before PASETO validation.
- `location`: override the configured token source. HTTP supports `headers` and
  `json`; websocket handlers support `headers` and `query`.
- `token_key`: override the configured header name, JSON key, or websocket query
  key for this check.
- `token_prefix`: override the configured token prefix with another non-empty
  string for this check.
- `token`: provide a raw token directly and bypass request or websocket lookup.
- `implicit_assertion`: require the same implicit assertion that was used when
  the token was created.

Notes:

- `fresh=True` and `refresh_token=True` cannot be used together.
- `optional=True` does not suppress type mismatches, freshness failures, or
  denylist failures after a token decodes successfully.
- On websocket handlers, call `paseto_required()` before `accept()`. Auth
  failures are converted to websocket close code `1008`.

## Token Creation

### `create_access_token(subject, fresh=False, purpose=None, expires_time=None, audience=None, issuer=None, user_claims=None, footer=None, implicit_assertion=b"", base64_encode=False)`

Creates a new access token.

- `subject`: string or integer identifier stored in the `sub` claim.
- `fresh`: whether the token should be marked as fresh.
- `purpose`: override the configured `local` or `public` purpose.
- `expires_time`: override the configured expiration with integer seconds,
  `datetime`, `timedelta`, or `False`.
- `audience`: string or sequence of audience values added to `aud`.
- `issuer`: override the `iss` claim for this token. If omitted, access tokens
  fall back to `authpaseto_encode_issuer`.
- `user_claims`: additional non-reserved claims merged into the payload.
- `footer`: optional PASETO footer as bytes, string, or dictionary.
- `implicit_assertion`: optional implicit assertion bound to the token.
- `base64_encode`: base64-encode the generated token string before returning it.

Returns a token string.

### `create_refresh_token(subject, purpose=None, expires_time=None, audience=None, issuer=None, user_claims=None, footer=None, implicit_assertion=b"", base64_encode=False)`

Creates a new refresh token.

Parameters are the same as `create_access_token()`, except refresh tokens do not
accept a `fresh` flag and do not inherit `authpaseto_encode_issuer`.

Returns a token string.

### `create_token(subject, type, purpose=None, expires_time=None, audience=None, issuer=None, user_claims=None, footer=None, implicit_assertion=b"", base64_encode=False)`

Creates a custom token with the caller-provided `type` claim.

- `type`: custom token type string that can later be required with
  `paseto_required(type="...")`.

Returns a token string.

## Request-Scoped Helpers

### `get_token_payload()`

Returns the decoded token payload for the current request or websocket
connection, or `None` if no token has been validated successfully.

### `get_token_footer()`

Returns the decoded footer for the current request or websocket connection, or
`None` if no token has been validated successfully or the token has no footer.

### `get_jti()`

Returns the current token identifier from the `jti` claim, or `None` if no
token has been validated successfully.

### `get_paseto_subject()`

Returns the current token subject by reading the decoded payload directly, or
`None` if no token has been validated successfully.

### `get_subject()`

Returns the cached subject captured during the last successful
`paseto_required()` call, or `None` otherwise.

In normal request handling, `get_subject()` and `get_paseto_subject()` return
the same value after successful validation.

## Helper Dependency

### `get_request_json()`

The `fastapi_paseto.auth_paseto` module also exposes `get_request_json()` as a
dependency helper.

- For HTTP requests it returns the parsed JSON body, or `{}` when the body is
  empty or invalid JSON.
- For websocket connections it always returns `{}`.
