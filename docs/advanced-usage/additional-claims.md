You can store additional information in access, refresh, or custom tokens and
read it later from protected endpoints.

Pass a dictionary through the `user_claims` parameter of
`create_access_token()`, `create_refresh_token()`, or `create_token()`, then
read it back with `get_token_payload()`.

Storing data in tokens can reduce repeated database lookups, but you still need
to choose those claims carefully.

When using the `public` purpose, the token payload is signed but not encrypted.
Anyone with the token can read its contents, so do not store sensitive
information there. Whether `local` tokens are appropriate for sensitive data is
still your own security decision.


```python hl_lines="34-35 44"
{!../examples/additional_claims.py!}
```
