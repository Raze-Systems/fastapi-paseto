Create a file `websocket.py`:

```python hl_lines="31 42-46 50-58"
{!../examples/websocket.py!}
```

Websocket endpoints use the same dependency injection pattern as HTTP endpoints:

```python
@app.websocket("/ws/header")
async def websocket_header(
    websocket: WebSocket,
    Authorize: AuthPASETO = Depends(),
) -> None:
    Authorize.paseto_required()
    await websocket.accept()
```

The important rule is to call **paseto_required()** before `accept()`. If auth fails,
the handshake is rejected with websocket close code `1008` and the auth error message
is used as the close reason.

## Header Authorization

By default, websocket authorization reads the token from the configured auth header,
reusing `authpaseto_header_name` and `authpaseto_header_type`.

```
Authorization: Bearer <access_token>
```

## Query Authorization

Browsers often cannot attach custom auth headers during the websocket handshake. For
those clients, you can either enable websocket query transport globally:

```python
@AuthPASETO.load_config
def get_config():
    return {
        "authpaseto_secret_key": "secret",
        "authpaseto_websocket_token_location": ["query"],
    }
```

or opt into query transport for a single route:

```python
Authorize.paseto_required(location="query")
```

The default query parameter is `token`, and you can customize it with
`authpaseto_websocket_query_key` or per-route with `token_key`.

## Parity and Limits

- `optional=True`, `fresh=True`, `refresh_token=True`, custom `type`, denylist checks,
  issuer validation, audience validation, base64 decoding, and `token=` overrides all
  work the same way for websocket handlers.
- JSON body token transport is not supported for websocket handshakes, because there is
  no request body available before the connection is accepted.
