Create a file `basic.py`:

```python hl_lines="16 19-21 25-30 36 41 47-48 50"
{!../examples/basic.py!}
```

The inline `"secret"` in this demo is only a placeholder for the smallest
possible example. In production, generate a high-entropy key and retrieve it
from secure storage inside `load_config()`. See [Key Management](../advanced-usage/key-management.md).

Run the server with:

```bash
$ uvicorn basic:app --host 0.0.0.0

INFO:     Started server process [9859]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

By default, `paseto_required()` reads access tokens from the `Authorization`
header using the `Bearer` prefix:

```text
Authorization: Bearer <access_token>
```

You can see the flow with `curl`:

```bash
$ curl http://localhost:8000/user

{"detail":"PASETO Authorization Token required"}

$ curl -H "Content-Type: application/json" -X POST \
  -d '{"username":"test","password":"test"}' http://localhost:8000/login

{"access_token":"v4.local...."}

$ curl -H "Authorization: Bearer <access_token>" http://localhost:8000/user

{"user":"test"}
```

After `paseto_required()` succeeds, `get_subject()` returns the decoded `sub`
claim cached for the current request.
