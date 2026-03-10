In some cases you may want one endpoint to serve both authenticated and
anonymous callers. In that case, use the `optional=True` argument of
`paseto_required()`.

With `optional=True`, the route continues when no token is present. It also
continues when a token is present but cannot be decoded, so `get_subject()` and
`get_token_payload()` return `None` in those cases. Checks that happen after a
successful decode, such as token type, freshness, or denylist failures, still
raise an error.

```python hl_lines="37"
{!../examples/optional.py!}
```
