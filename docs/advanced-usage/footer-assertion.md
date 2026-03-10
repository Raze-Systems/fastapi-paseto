FastAPI PASETO can carry optional PASETO footers and verify implicit
assertions when you need stronger token binding than payload claims alone.

```python hl_lines="10 30-36 42-44 49"
{!../examples/footer_assertion.py!}
```

## What They Are

**Footer**
: Extra authenticated data attached to the token outside the payload.
  A footer travels with the token and is protected by PASETO integrity checks,
  but it is not meant for confidential application data.

**Implicit assertion**
: Extra authenticated data that does **not** travel inside the token at all.
  The same value must be supplied again at verification time or validation
  fails.

In practice:

- Put application claims you want to read later in the payload.
- Put non-secret token metadata you want attached to the token in the footer.
- Put request-bound context that should never be embedded in the token in the
  implicit assertion.

## Footers

PASETO footers are useful for metadata such as:

- `kid` values for key selection
- routing or tenant hints
- integration metadata that should stay outside the payload

- Pass `footer=` to `create_access_token()`, `create_refresh_token()`, or
  `create_token()` to include an optional PASETO footer.
- After `paseto_required()` succeeds, call `get_token_footer()` to read the
  decoded footer.
- Footer data is authenticated by PASETO, but for `public` tokens it remains
  visible to anyone holding the token.

Example:

```python
token = Authorize.create_access_token(
    subject="alice",
    footer={"kid": "k4.lid.primary"},
)

Authorize.paseto_required()
footer = Authorize.get_token_footer()
```

Use a footer when the metadata belongs to the token itself and can safely
travel with it.

## Implicit Assertions

Implicit assertions are useful when the token must be bound to external context
such as:

- a tenant identifier chosen by the server
- a channel or transport binding
- a deployment- or service-specific contract

- Pass `implicit_assertion=` when creating a token.
- Pass the same `implicit_assertion=` value to `paseto_required()` when
  validating it.
- If the assertion is missing or mismatched, token validation fails.

Example:

```python
token = Authorize.create_access_token(
    subject="alice",
    implicit_assertion="tenant-alpha",
)

Authorize.paseto_required(implicit_assertion="tenant-alpha")
```

Use an implicit assertion when the value should influence verification but
should not be readable from the token or transported inside it.

## Choosing Between Them

Choose a **footer** when:

- the verifier needs to read the metadata from the token itself
- the value can safely travel with the token

Choose an **implicit assertion** when:

- the verifier already knows the value from surrounding context
- the value should not be embedded into or exposed by the token

Do not use either one for ordinary application claims such as user roles,
permissions, or profile data. Those belong in the token payload.
