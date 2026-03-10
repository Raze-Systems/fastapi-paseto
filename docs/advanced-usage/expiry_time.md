You can override the default token lifetime with the `expires_time` parameter on
`create_access_token()`, `create_refresh_token()`, or `create_token()`.

`expires_time` accepts a `datetime.timedelta`, `datetime.datetime`, integer
seconds, or `False`. That override takes precedence over the configured
`authpaseto_access_token_expires`, `authpaseto_refresh_token_expires`, or
`authpaseto_other_token_expires` defaults.

```python
@app.post('/create-dynamic-token')
def create_dynamic_token(Authorize: AuthPASETO = Depends()):
    expires = datetime.timedelta(days=1)
    token = Authorize.create_access_token(subject="test",expires_time=expires)
    return {"token": token}
```

You can disable expiration by setting `expires_time=False`:

```python
@app.post('/create-token-disable')
def create_dynamic_token(Authorize: AuthPASETO = Depends()):
    token = Authorize.create_access_token(subject="test",expires_time=False)
    return {"token": token}
```
