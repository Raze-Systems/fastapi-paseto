HTTP routes can read tokens from JSON request bodies as well as headers. This
is useful when the client already sends a JSON payload and you want the token to
travel inside that document instead of a header.

The HTTP transport settings that control this behavior are:

- `authpaseto_token_location`
- `authpaseto_json_key`
- `authpaseto_json_type`

You can configure JSON transport globally, or opt into it per route with
`paseto_required(location="json")`.

```python hl_lines="17-21 47 54-58"
{!../examples/json_transport.py!}
```

With the example above:

- `POST /json-protected` expects `{"access_token": "<PASETO>"}` in the JSON body
- `POST /json-refresh` expects `{"refresh_token": "<PASETO>"}` in the JSON body

If you set a JSON prefix, the token value must include it exactly:

```json
{"access_token": "Bearer <PASETO>"}
```

When both header and JSON transport are enabled, header lookup runs first and
JSON lookup runs second.
