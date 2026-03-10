Refresh tokens are long-lived tokens that can be exchanged for new access
tokens after an access token expires.

Refresh tokens cannot access an endpoint protected with `paseto_required()`, and
access tokens cannot access an endpoint protected with
`paseto_required(refresh_token=True)`.

Access tokens are marked as fresh when they were created from an explicit
credential check instead of from a refresh flow. This gives you a way to reserve
high-risk operations for recently authenticated users.

When calling a refresh endpoint, send the refresh token instead of the access
token:

```text
Authorization: Bearer <refresh_token>
```

Here is an example of using access and refresh tokens:

```python hl_lines="35 46"
{!../examples/refresh.py!}
```
