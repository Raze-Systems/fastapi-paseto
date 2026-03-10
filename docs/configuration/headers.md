These settings control how HTTP requests carry tokens.

`authpaseto_token_location`
:   Token sources checked for HTTP requests. Valid values are `headers` and
    `json`. Defaults to `("headers",)`.

    If both sources are enabled, header lookup runs first and JSON lookup runs
    second.

`authpaseto_header_name`
:   Header name used when `headers` transport is enabled. Defaults to
    `Authorization`.

`authpaseto_header_type`
:   Optional prefix required in the header value, such as `Bearer`. Set this to
    `None` to accept a bare token value like `Authorization: <PASETO>`. Defaults
    to `Bearer`.

`authpaseto_json_key`
:   JSON field name used when `json` transport is enabled. Defaults to
    `access_token`.

`authpaseto_json_type`
:   Optional prefix required in the JSON field value. Set this to `None` to
    accept a bare token value like `{"access_token": "<PASETO>"}`. Defaults to
    `None`.

Per-route overrides on `paseto_required()` can temporarily replace the active
location, key, and prefix for a single endpoint.
