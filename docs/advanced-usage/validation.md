FastAPI PASETO exposes validation controls for issuer, audience, custom token
types, base64-encoded tokens, and token-binding options such as implicit
assertions.

```python hl_lines="18-22 35-45 49 56 63"
{!../examples/validation.py!}
```

Use these options when you need stronger contracts than "any valid access token":

- Set `authpaseto_decode_issuer` to require an `iss` claim with a specific value.
- Pass `audience=` when creating a token and set `authpaseto_decode_audience` to
  enforce the expected audience on decode.
- Use `create_token(type="...")` together with `paseto_required(type="...")`
  for custom token flows such as email verification.
- Use `base64_encode=True` when creating a token and
  `paseto_required(base64_encoded=True)` when validating it.
- Use `implicit_assertion=` on both creation and validation when a token must
  be bound to external request context.

Important issuer detail:

- `authpaseto_encode_issuer` automatically adds `iss` only to
  `create_access_token()`.
- `authpaseto_decode_issuer` applies to every decoded token.
- If you enable issuer validation for refresh or custom tokens, pass
  `issuer=` when creating those tokens.

For footer handling and `get_token_footer()`, see
[Footers and Assertions](footer-assertion.md).
