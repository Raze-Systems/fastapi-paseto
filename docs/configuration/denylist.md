`authpaseto_denylist_enabled`
:   Enables token revocation checks. Defaults to `False`.

`authpaseto_denylist_token_checks`
:   Token types that should be checked against the denylist callback. Valid
    values are `access` and `refresh`. Pass a sequence to check both. Defaults
    to `("access", "refresh")`.

When denylist support is enabled, register a callback with
`@AuthPASETO.token_in_denylist_loader`. That callback receives the decoded token
payload and should return `True` when the token has been revoked.
