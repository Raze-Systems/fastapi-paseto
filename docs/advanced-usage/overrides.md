`paseto_required()` can override the configured token transport on a single
route. This is useful when most of your application follows one convention, but
one endpoint needs a different header name, body key, prefix, or a token that
was already extracted by another dependency.

The route-level override arguments are:

- `location`
- `token_key`
- `token_prefix`
- `token`

```python hl_lines="37 44-48 55-60"
{!../examples/overrides.py!}
```

Notes:

- `location="json"` is only valid for HTTP requests.
- `location="query"` is only valid for websocket handlers.
- `token=` bypasses header, JSON, and query lookup entirely.
- `token_prefix` can override the configured prefix with another non-empty
  string. If you need to disable the prefix completely, set the transport type
  to `None` in configuration.
