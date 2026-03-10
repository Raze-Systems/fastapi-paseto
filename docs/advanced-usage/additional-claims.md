You can store additional information in access, refresh, or custom tokens and
read it later from protected endpoints.

Pass a dictionary through the `user_claims` parameter of
`create_access_token()`, `create_refresh_token()`, or `create_token()`, then
read it back with `get_token_payload()`.

Storing data in tokens can reduce repeated database lookups, but you still need
to choose those claims carefully.

`user_claims` is only for custom application data. Reserved top-level claims
such as `sub`, `type`, `jti`, `exp`, `nbf`, `iat`, `iss`, `aud`, and `fresh`
cannot be overridden there.

Use the dedicated parameters instead:

- `subject=` for `sub`
- `fresh=` for access-token freshness
- `audience=` for `aud`
- `issuer=` for `iss`
- `expires_time=` for `exp`
- `create_token(type="...")` for custom token types

When using the `public` purpose, the token payload is signed but not encrypted.
Anyone with the token can read its contents, so do not store sensitive
information there. Whether `local` tokens are appropriate for sensitive data is
still your own security decision.


```python hl_lines="34-35 44"
{!../examples/additional_claims.py!}
```
