These options control the cryptographic keys, claim validation rules, token
defaults, and websocket transport settings used by `AuthPASETO`.

## Keys and Token Format

`authpaseto_secret_key`
:   Secret key used for `local` tokens. Required when `authpaseto_purpose` is
    `local`. Defaults to `None`.

`authpaseto_public_key`
:   Public key used to decode `public` tokens. PEM text is expected. Defaults to
    `None`.

`authpaseto_public_key_file`
:   Path to a PEM file containing the public key. When `authpaseto_public_key`
    is unset, this file is read during config loading and its contents are used
    instead. Defaults to `None`.

`authpaseto_private_key`
:   Private key used to encode `public` tokens. PEM text is expected. Defaults
    to `None`.

`authpaseto_private_key_file`
:   Path to a PEM file containing the private key. When
    `authpaseto_private_key` is unset, this file is read during config loading
    and its contents are used instead. Defaults to `None`.

`authpaseto_purpose`
:   Default token purpose for newly created tokens. Valid values are `local` and
    `public`. Defaults to `local`.

`authpaseto_version`
:   PASETO version used when creating new tokens. Defaults to `4`.

## Claim Validation

`authpaseto_decode_leeway`
:   Leeway applied when decoding an expired token. Accepts an integer number of
    seconds or a `datetime.timedelta`. Defaults to `0`.

`authpaseto_encode_issuer`
:   Default issuer value automatically added by `create_access_token()`.
    Refresh and custom tokens can set `iss` explicitly with `issuer=`.
    Defaults to `None`.

`authpaseto_decode_issuer`
:   Expected `iss` claim value when decoding a token. If this is set, every
    decoded token must contain the matching issuer. Defaults to `None`.

`authpaseto_decode_audience`
:   Expected audience when decoding a token. Accepts a string or sequence of
    strings. The empty string disables audience validation. Defaults to `""`.

## Token Lifetimes

`authpaseto_access_token_expires`
:   Default lifetime for access tokens. Accepts integer seconds,
    `datetime.timedelta`, or `False` to disable expiration. Defaults to
    **15 minutes**.

`authpaseto_refresh_token_expires`
:   Default lifetime for refresh tokens. Accepts integer seconds,
    `datetime.timedelta`, or `False` to disable expiration. Defaults to
    **30 days**.

`authpaseto_other_token_expires`
:   Default lifetime for custom tokens created with `create_token()`. Accepts
    integer seconds, `datetime.timedelta`, or `False` to disable expiration.
    Defaults to **30 days**.

## WebSocket Transport

`authpaseto_websocket_token_location`
:   Where websocket handlers look for tokens during the handshake. Valid values
    are `headers` and `query`. Defaults to `("headers",)`.

`authpaseto_websocket_query_key`
:   Query-string key used when websocket query transport is enabled. Defaults to
    `token`.

`authpaseto_websocket_query_type`
:   Optional query-string prefix required before the token value, similar to a
    `Bearer` header prefix. Defaults to `None`.
