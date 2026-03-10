Revoking tokens lets you block a specific token even if it has not expired yet.

Choose which token types should be checked with
`authpaseto_denylist_token_checks`, then register a callback with
`token_in_denylist_loader()`. That callback receives the decoded token payload
and should return `True` when the token has been revoked.

Only the configured token types are checked. For example, if you set
`authpaseto_denylist_token_checks=["refresh"]`, access tokens skip denylist
lookups while refresh tokens still enforce them.

This can be utilized to invalidate token in multiple cases, e.g.:
- A user logs out and their currently active tokens need to be invalidated
- You detect a replay attack and the leaked tokens need to be blocked

Each generated token includes a UUID in the `jti` claim, which is typically the
identifier you store in your denylist backend.

Here is a basic example use tokens revoking:

```python hl_lines="17-18 34 40-43 70 79"
{!../examples/denylist.py!}
```

In production, you will usually want a database or in-memory store such as
Redis for revoked-token state. A TTL-based store works well because the denylist
entry can expire when the token would have expired anyway.

Make sure Redis is running locally before trying the Redis example. One option
is:

```bash
docker run -d -p 6379:6379 redis
```

Here is an example that uses Redis for revoking tokens:

```python hl_lines="7 17-20 38 44-48 78 87"
{!../examples/denylist_redis.py!}
```
