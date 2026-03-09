"""Pure helpers used by the public ``AuthPASETO`` implementation."""

import base64
import binascii
import uuid
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from fastapi_paseto.exceptions import (
    AccessTokenRequired,
    InvalidPASETOArgumentError,
    InvalidPASETOPurposeError,
    InvalidPASETOVersionError,
    InvalidTokenTypeError,
    PASETODecodeError,
    RefreshTokenRequired,
)

TokenAudience = str | Sequence[str]
ExpiryValue = timedelta | datetime | int | bool | None
PurposeProcess = str


def generate_token_identifier() -> str:
    """Return a new random token identifier."""

    return str(uuid.uuid4())


def build_reserved_claims(subject: str | int) -> dict[str, object]:
    """Build the reserved claims added to every generated token."""

    return {
        "sub": subject,
        "nbf": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        "jti": generate_token_identifier(),
    }


def build_custom_claims(
    type_token: str,
    fresh: bool | None,
    issuer: str | None,
    audience: TokenAudience,
) -> dict[str, object]:
    """Build the non-reserved claims added to generated tokens."""

    custom_claims: dict[str, object] = {"type": type_token}
    if type_token == "access":
        custom_claims["fresh"] = fresh
    if issuer:
        custom_claims["iss"] = issuer
    if audience:
        custom_claims["aud"] = audience
    return custom_claims


def validate_token_creation_arguments(
    subject: str | int,
    fresh: bool | None,
    audience: TokenAudience,
    purpose: str | None,
    version: int | None,
    user_claims: dict[str, object] | None,
) -> None:
    """Validate user-supplied inputs before generating a token."""

    if not isinstance(subject, (str, int)):
        raise TypeError("Subject must be a string or int")
    if fresh is not None and not isinstance(fresh, bool):
        raise TypeError("Fresh must be a boolean")
    if audience and not isinstance(audience, (str, list, tuple, set, frozenset)):
        raise TypeError("audience must be a string or sequence")
    if purpose and not isinstance(purpose, str):
        raise TypeError("purpose must be a string")
    if version and not isinstance(version, int):
        raise TypeError("version must be an integer")
    if user_claims and not isinstance(user_claims, dict):
        raise TypeError("User claims must be a dictionary")


def validate_required_token_flags(fresh: bool, refresh_token: bool) -> None:
    """Reject incompatible validation flags."""

    if fresh and refresh_token:
        raise InvalidPASETOArgumentError(
            status_code=422,
            message="fresh and refresh_token cannot be True at the same time",
        )


def resolve_default_expiry(
    type_token: str,
    access_expires: timedelta | int | bool,
    refresh_expires: timedelta | int | bool,
    other_expires: timedelta | int | bool,
) -> timedelta | int | bool:
    """Return the configured default expiry for the requested token type."""

    match type_token:
        case "access":
            return access_expires
        case "refresh":
            return refresh_expires
        case _:
            return other_expires


def resolve_expiry_seconds(
    type_token: str,
    expires_time: ExpiryValue,
    access_expires: timedelta | int | bool,
    refresh_expires: timedelta | int | bool,
    other_expires: timedelta | int | bool,
) -> int:
    """Normalize an expiry value into whole seconds."""

    if expires_time and not isinstance(expires_time, (timedelta, datetime, int, bool)):
        raise TypeError("expires_time must be a timedelta, datetime, int or bool")

    if expires_time is False:
        return 0

    resolved_expiry = expires_time or resolve_default_expiry(
        type_token,
        access_expires=access_expires,
        refresh_expires=refresh_expires,
        other_expires=other_expires,
    )
    if isinstance(resolved_expiry, bool):
        resolved_expiry = resolve_default_expiry(
            type_token,
            access_expires=access_expires,
            refresh_expires=refresh_expires,
            other_expires=other_expires,
        )

    match resolved_expiry:
        case timedelta():
            return int(resolved_expiry.total_seconds())
        case datetime():
            current_time = datetime.utcnow()
            valid_time = resolved_expiry - current_time
            return int(valid_time.total_seconds())
        case _:
            return resolved_expiry


def resolve_secret_key(
    purpose: str,
    process: PurposeProcess,
    secret_key: str | None,
    private_key: str | None,
    public_key: str | None,
) -> str | None:
    """Return the configured key required for the requested purpose and process."""

    match purpose:
        case "local":
            if not secret_key:
                raise RuntimeError(
                    f"authpaseto_secret_key must be set when using {purpose} purpose"
                )
            return secret_key
        case "public":
            match process:
                case "encode":
                    if not private_key:
                        raise RuntimeError(
                            "authpaseto_private_key must be set when using "
                            f"{purpose} purpose"
                        )
                    return private_key
                case "decode":
                    if not public_key:
                        raise RuntimeError(
                            "authpaseto_public_key must be set when using "
                            f"{purpose} purpose"
                        )
                    return public_key
                case _:
                    return None
        case _:
            raise ValueError("Algorithm must be local or public.")


def parse_token_version(version_name: str) -> int:
    """Parse the version prefix from a token."""

    match version_name:
        case "v4":
            return 4
        case "v3":
            return 3
        case "v2":
            return 2
        case "v1":
            return 1
        case _:
            raise InvalidPASETOVersionError(
                status_code=422,
                message=f"Invalid PASETO version {version_name}",
            )


def parse_token_purpose(purpose_name: str) -> str:
    """Parse the purpose segment from a token."""

    match purpose_name:
        case "local" | "public":
            return purpose_name
        case _:
            raise InvalidPASETOPurposeError(
                status_code=422,
                message=f"Invalid PASETO purpose {purpose_name}",
            )


def split_token_parts(token: str) -> list[str]:
    """Split a token into its dot-separated parts."""

    parts = token.split(".")
    if len(parts) != 3:
        raise PASETODecodeError(status_code=422, message="Invalid PASETO format")
    return parts


def decode_base64_token(token: str) -> str:
    """Decode a base64-encoded token string."""

    try:
        return base64.b64decode(token.encode("utf-8")).decode("utf-8")
    except (UnicodeDecodeError, binascii.Error) as err:
        raise PASETODecodeError(
            status_code=422,
            message="Invalid base64 encoding",
        ) from err


def validate_token_type(
    payload_type: str,
    refresh_token: bool,
    token_type: str | None,
) -> None:
    """Ensure the decoded token type matches the required endpoint contract."""

    match (refresh_token, token_type):
        case (False, None) if payload_type != "access":
            raise AccessTokenRequired(
                status_code=422,
                message=f"Access token required but {payload_type} provided",
            )
        case (True, _) if payload_type != "refresh":
            raise RefreshTokenRequired(
                status_code=422,
                message=f"Refresh token required but {payload_type} provided",
            )
        case (False, expected_type) if (
            expected_type is not None and payload_type != expected_type
        ):
            raise InvalidTokenTypeError(
                status_code=422,
                message=f"{expected_type} token required but {payload_type or 'None'} provided",
            )
