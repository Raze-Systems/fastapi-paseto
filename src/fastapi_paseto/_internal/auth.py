"""Internal ``AuthPASETO`` implementation."""

import base64
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta

from fastapi import Depends, Request, Response, WebSocket
from pyseto import Key, Paseto, Token
from pyseto.exceptions import DecryptError, SignError, VerifyError

from fastapi_paseto.auth_config import AuthConfig
from fastapi_paseto.exceptions import (
    AuthPASETOException,
    FreshTokenRequired,
    MissingTokenError,
    PASETODecodeError,
    RevokedTokenError,
)

from .request import (
    extract_token_from_header,
    extract_token_from_json,
    get_request_json,
)
from .transport import (
    extract_token_from_query,
    normalize_token_locations,
    raise_websocket_auth_error,
    validate_connection_token_locations,
)
from .token_helpers import (
    build_custom_claims,
    build_reserved_claims,
    decode_base64_token,
    generate_token_identifier,
    parse_token_purpose,
    parse_token_version,
    resolve_expiry_seconds,
    resolve_secret_key,
    split_token_parts,
    validate_implicit_assertion,
    validate_required_token_flags,
    validate_token_creation_arguments,
    validate_token_type,
)


class AuthPASETO(AuthConfig):
    """FastAPI dependency that creates and validates PASETO tokens."""

    def __init__(
        self,
        request: Request = None,
        response: Response = None,
        websocket: WebSocket = None,
        request_json: dict[str, object] = Depends(get_request_json),
    ) -> None:
        """Capture request-scoped objects used by token extraction helpers."""

        self._token: str | None = None
        self._token_parts: list[str] = []
        self._current_user: str | int | None = None
        self._decoded_token: Token | None = None
        self._request_json = request_json
        self._response = response
        self._request = request
        self._websocket = websocket

    def _reset_runtime_state(self) -> None:
        """Clear request-scoped authentication state."""

        self._token = None
        self._token_parts = []
        self._current_user = None
        self._decoded_token = None

    def _get_paseto_from_json(
        self,
        json_key: str | None = None,
        json_type: str | None = None,
    ) -> str | None:
        """Extract a token from the request JSON body."""

        return extract_token_from_json(
            request_json=self._request_json,
            json_key=json_key or self._json_key,
            json_type=json_type or self._json_type,
        )

    def _get_paseto_from_header(
        self,
        header_name: str | None = None,
        header_type: str | None = None,
    ) -> str | None:
        """Extract a token from the configured request header."""

        return extract_token_from_header(
            header_value=self._get_connection_headers().get(header_name or self._header_name),
            header_name=header_name or self._header_name,
            header_type=header_type or self._header_type,
        )

    def _get_paseto_from_query(
        self,
        query_key: str | None = None,
        query_type: str | None = None,
    ) -> str | None:
        """Extract a token from the configured websocket query parameter."""

        return extract_token_from_query(
            query_params=self._get_connection_query_params(),
            query_key=query_key or self._websocket_query_key,
            query_type=query_type or self._websocket_query_type,
        )

    def _get_connection(self) -> Request | WebSocket:
        """Return the current request or websocket connection."""

        if self._websocket is not None:
            return self._websocket
        if self._request is None:  # pragma: no cover
            raise RuntimeError("Request or websocket connection is required")
        return self._request

    def _get_connection_headers(self) -> Mapping[str, str]:
        """Return the headers mapping for the current connection."""

        return self._get_connection().headers

    def _get_connection_query_params(self) -> Mapping[str, str]:
        """Return the query params mapping for the current connection."""

        return self._get_connection().query_params

    def _is_websocket_connection(self) -> bool:
        """Return whether the current dependency context is a websocket."""

        return self._websocket is not None

    def _get_paseto_identifier(self) -> str:
        """Return a new unique token identifier."""

        return generate_token_identifier()

    def _get_secret_key(self, purpose: str, process: str) -> str:
        """Return the configured key for the requested cryptographic operation."""

        return resolve_secret_key(
            purpose=purpose,
            process=process,
            secret_key=self._secret_key,
            private_key=self._private_key,
            public_key=self._public_key,
        )

    def _get_int_from_datetime(self, value: datetime) -> int:
        """Convert a datetime to whole seconds since the Unix epoch."""

        if not isinstance(value, datetime):  # pragma: no cover
            raise TypeError("a datetime is required")
        return int(value.timestamp())

    def _create_token(
        self,
        subject: str | int,
        type_token: str,
        exp_seconds: int,
        fresh: bool | None = None,
        issuer: str | None = None,
        purpose: str | None = None,
        audience: str | Sequence[str] = "",
        user_claims: dict[str, object] | None = None,
        version: int | None = None,
        footer: bytes | str | dict[str, object] | None = None,
        implicit_assertion: bytes | str = b"",
        base64_encode: bool = False,
    ) -> str:
        """Create and return an encoded PASETO string."""

        validate_token_creation_arguments(
            subject=subject,
            fresh=fresh,
            audience=audience,
            issuer=issuer,
            purpose=purpose,
            version=version,
            user_claims=user_claims,
            footer=footer,
            implicit_assertion=implicit_assertion,
        )
        user_claims = user_claims or {}
        issuer = issuer or self._encode_issuer
        purpose = purpose or self._purpose
        version = version or self._version

        if purpose not in ("local", "public"):
            raise ValueError("Purpose must be local or public.")

        claims = {
            **build_reserved_claims(subject),
            **build_custom_claims(type_token, fresh, issuer, audience),
            **user_claims,
        }
        secret_key = self._get_secret_key(purpose, "encode")
        paseto = Paseto.new(exp=exp_seconds, include_iat=True)
        encoding_key = Key.new(version=version, purpose=purpose, key=secret_key)
        token = paseto.encode(
            encoding_key,
            claims,
            footer=footer or b"",
            implicit_assertion=implicit_assertion,
            serializer=json,
        )
        if base64_encode:
            token = base64.b64encode(token)
        return token.decode("utf-8")

    def _has_token_in_denylist_callback(self) -> bool:
        """Return whether a denylist callback has been configured."""

        return self._token_in_denylist_callback is not None

    def _check_token_is_revoked(self, payload: dict[str, object]) -> None:
        """Raise if the decoded token has been revoked via the configured callback."""

        if not self._denylist_enabled:
            return
        payload_type = payload.get("type")
        if payload_type not in self._denylist_token_checks:
            return
        if not self._has_token_in_denylist_callback():
            raise RuntimeError(
                "A token_in_denylist_callback must be provided via "
                "the '@AuthPASETO.token_in_denylist_loader' if "
                "authpaseto_denylist_enabled is 'True'"
            )
        if self._token_in_denylist_callback.__func__(payload):
            raise RevokedTokenError(status_code=401, message="Token has been revoked")

    def _get_expiry_seconds(
        self,
        type_token: str,
        expires_time: timedelta | datetime | int | bool | None = None,
    ) -> int:
        """Resolve an expiry configuration into the seconds expected by ``pyseto``."""

        return resolve_expiry_seconds(
            type_token=type_token,
            expires_time=expires_time,
            access_expires=self._access_token_expires,
            refresh_expires=self._refresh_token_expires,
            other_expires=self._other_token_expires,
        )

    def create_access_token(
        self,
        subject: str | int,
        fresh: bool = False,
        purpose: str | None = None,
        expires_time: timedelta | datetime | int | bool | None = None,
        audience: str | Sequence[str] | None = None,
        issuer: str | None = None,
        user_claims: dict[str, object] | None = None,
        footer: bytes | str | dict[str, object] | None = None,
        implicit_assertion: bytes | str = b"",
        base64_encode: bool = False,
    ) -> str:
        """Create a new access token."""

        return self._create_token(
            subject=subject,
            type_token="access",
            exp_seconds=self._get_expiry_seconds("access", expires_time),
            fresh=fresh,
            purpose=purpose,
            audience=audience,
            user_claims=user_claims,
            issuer=issuer or self._encode_issuer,
            footer=footer,
            implicit_assertion=implicit_assertion,
            base64_encode=base64_encode,
        )

    def create_refresh_token(
        self,
        subject: str | int,
        purpose: str | None = None,
        expires_time: timedelta | datetime | int | bool | None = None,
        audience: str | Sequence[str] | None = None,
        issuer: str | None = None,
        user_claims: dict[str, object] | None = None,
        footer: bytes | str | dict[str, object] | None = None,
        implicit_assertion: bytes | str = b"",
        base64_encode: bool = False,
    ) -> str:
        """Create a new refresh token."""

        return self._create_token(
            subject=subject,
            type_token="refresh",
            exp_seconds=self._get_expiry_seconds("refresh", expires_time),
            purpose=purpose,
            audience=audience,
            issuer=issuer,
            user_claims=user_claims,
            footer=footer,
            implicit_assertion=implicit_assertion,
            base64_encode=base64_encode,
        )

    def create_token(
        self,
        subject: str | int,
        type: str,
        purpose: str | None = None,
        expires_time: timedelta | datetime | int | bool | None = None,
        audience: str | Sequence[str] | None = None,
        issuer: str | None = None,
        user_claims: dict[str, object] | None = None,
        footer: bytes | str | dict[str, object] | None = None,
        implicit_assertion: bytes | str = b"",
        base64_encode: bool = False,
    ) -> str:
        """Create a token with a caller-provided custom type."""

        return self._create_token(
            subject=subject,
            type_token=type,
            exp_seconds=self._get_expiry_seconds(type, expires_time),
            purpose=purpose,
            audience=audience,
            issuer=issuer,
            user_claims=user_claims,
            footer=footer,
            implicit_assertion=implicit_assertion,
            base64_encode=base64_encode,
        )

    def _get_token_version(self) -> int:
        """Return the parsed version of the current token."""

        return parse_token_version(self._get_raw_token_parts()[0])

    def _get_token_purpose(self) -> str:
        """Return the parsed purpose of the current token."""

        return parse_token_purpose(self._get_raw_token_parts()[1])

    def _get_raw_token_parts(self) -> list[str]:
        """Return and cache the dot-separated parts of the current token."""

        if self._token_parts:
            return self._token_parts
        self._token_parts = split_token_parts(self._token)
        return self._token_parts

    def _decode_token(
        self,
        base64_encoded: bool = False,
        implicit_assertion: bytes | str = b"",
    ) -> Token:
        """Decode and validate the current token."""

        if base64_encoded:
            self._token = decode_base64_token(self._token)

        validate_implicit_assertion(implicit_assertion)
        purpose = self._get_token_purpose()
        version = self._get_token_version()
        secret_key = self._get_secret_key(purpose=purpose, process="decode")
        decoding_key = Key.new(version=version, purpose=purpose, key=secret_key)

        try:
            paseto = Paseto.new(leeway=self._decode_leeway)
            token = paseto.decode(
                keys=decoding_key,
                token=self._token,
                implicit_assertion=implicit_assertion,
                deserializer=json,
                aud=self._decode_audience,
            )
        except (DecryptError, SignError, VerifyError) as err:
            raise PASETODecodeError(status_code=422, message=str(err))

        if self._decode_issuer:
            if "iss" not in token.payload:
                raise PASETODecodeError(
                    status_code=422,
                    message="Token is missing the 'iss' claim",
                )
            if token.payload["iss"] != self._decode_issuer:
                raise PASETODecodeError(
                    status_code=422,
                    message="Token issuer is not valid",
                )

        self._check_token_is_revoked(token.payload)
        self._decoded_token = token
        if "sub" in token.payload:
            self._current_user = token.payload["sub"]
        return token

    def get_token_payload(self) -> dict[str, object] | None:
        """Return the decoded token payload for the current request."""

        if self._decoded_token:
            return self._decoded_token.payload
        return None

    def get_token_footer(self) -> bytes | str | dict[str, object] | None:
        """Return the decoded token footer for the current request if present."""

        if self._decoded_token is None:
            return None

        footer = self._decoded_token.footer
        if footer in (b"", ""):
            return None
        return footer

    def get_jti(self) -> str | None:
        """Return the current token identifier if present."""

        payload = self.get_token_payload()
        if payload and "jti" in payload:
            return payload["jti"]
        return None

    def get_paseto_subject(self) -> str | int | None:
        """Return the current decoded token subject if present."""

        payload = self.get_token_payload()
        if payload and "sub" in payload:
            return payload["sub"]
        return None

    def get_subject(self) -> str | int | None:
        """Return the cached subject captured during token validation."""

        return self._current_user

    def paseto_required(
        self,
        optional: bool = False,
        fresh: bool = False,
        refresh_token: bool = False,
        type: str | None = None,
        base64_encoded: bool = False,
        location: str | Sequence[str] | None = None,
        token_key: str | None = None,
        token_prefix: str | None = None,
        token: str | bool | None = None,
        implicit_assertion: bytes | str = b"",
    ) -> None:
        """Validate the current request token against the endpoint requirements."""

        self._reset_runtime_state()
        try:
            validate_required_token_flags(fresh=fresh, refresh_token=refresh_token)
            if token:
                self._token = token
            else:
                self._token = self._resolve_paseto_token(
                    location=location,
                    token_key=token_key,
                    token_prefix=token_prefix,
                )

            if not self._token:
                if optional:
                    return None
                raise MissingTokenError(
                    status_code=401,
                    message="PASETO Authorization Token required",
                )

            try:
                self._decode_token(
                    base64_encoded=base64_encoded,
                    implicit_assertion=implicit_assertion,
                )
            except PASETODecodeError as err:
                if optional:
                    return None
                raise err

            payload = self.get_token_payload()
            validate_token_type(
                payload_type=payload["type"],
                refresh_token=refresh_token,
                token_type=type,
            )
            if fresh and not payload["fresh"]:
                raise FreshTokenRequired(
                    status_code=401,
                    message="PASETO access token is not fresh",
                )
        except AuthPASETOException as err:
            if self._is_websocket_connection():
                raise_websocket_auth_error(err)
            raise err

    def _resolve_paseto_token(
        self,
        location: str | Sequence[str] | None,
        token_key: str | None,
        token_prefix: str | None,
    ) -> str | None:
        """Return the first token found for the current connection context."""

        resolved_locations = normalize_token_locations(
            location
            or (
                self._websocket_token_location
                if self._is_websocket_connection()
                else self._token_location
            )
        )
        validate_connection_token_locations(
            locations=resolved_locations,
            is_websocket=self._is_websocket_connection(),
        )

        if "headers" in resolved_locations:
            if token_from_header := self._get_paseto_from_header(
                header_name=token_key or self._header_name,
                header_type=token_prefix or self._header_type,
            ):
                return token_from_header

        if "json" in resolved_locations:
            if token_from_json := self._get_paseto_from_json(
                json_key=token_key or self._json_key,
                json_type=token_prefix or self._json_type,
            ):
                return token_from_json

        if "query" in resolved_locations:
            if token_from_query := self._get_paseto_from_query(
                query_key=token_key or self._websocket_query_key,
                query_type=token_prefix or self._websocket_query_type,
            ):
                return token_from_query

        return None
