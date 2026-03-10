The fresh-token pattern is built into this extension. You can mark some access
tokens as fresh, mark others as non-fresh, and protect a route with
`paseto_required(fresh=True)` so that only fresh access tokens may use it.

This is useful for higher-risk actions such as changing account information.
Combining fresh-token checks with refresh tokens lets you reduce frequent
password prompts while still requiring a recent login for sensitive operations.

Here is an example of how you could utilize refresh tokens with the fresh token pattern:

```python hl_lines="39 82"
{!../examples/freshness.py!}
```
