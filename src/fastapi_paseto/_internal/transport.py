"""Helpers for resolving token transport across HTTP and websocket contexts."""

from collections.abc import Mapping, Sequence

from fastapi import WebSocketException, status

from fastapi_paseto.exceptions import (
    AuthPASETOException,
    InvalidHeaderError,
    InvalidPASETOArgumentError,
)


def normalize_token_locations(location: str | Sequence[str] | None) -> tuple[str, ...]:
    """Return token locations as a normalized tuple."""

    if location is None:
        return ()
    if isinstance(location, str):
        return (location,)
    return tuple(location)


def validate_connection_token_locations(
    *,
    locations: tuple[str, ...],
    is_websocket: bool,
) -> None:
    """Reject token locations that are not supported by the current connection type."""

    invalid_location = next(
        (
            location
            for location in locations
            if location not in {"headers", "json", "query"}
        ),
        None,
    )
    if invalid_location is not None:
        raise InvalidPASETOArgumentError(
            status_code=422,
            message=f"Unsupported token location '{invalid_location}'",
        )

    if is_websocket and "json" in locations:
        raise InvalidPASETOArgumentError(
            status_code=422,
            message="json token location is not supported for WebSocket connections",
        )

    if not is_websocket and "query" in locations:
        raise InvalidPASETOArgumentError(
            status_code=422,
            message="query token location is only supported for WebSocket connections",
        )


def extract_token_from_query(
    query_params: Mapping[str, str],
    query_key: str,
    query_type: str | None,
) -> str | None:
    """Extract a token from query params using the configured key and prefix."""

    token = query_params.get(query_key)
    if token is None:
        return None

    if not query_type:
        if not token:
            raise InvalidHeaderError(
                status_code=422,
                message=f"Bad {query_key} query param. Expected value '<PASETO>'",
            )
        return token

    parts = token.split()
    if len(parts) != 2 or parts[0] != query_type or not parts[1]:
        raise InvalidHeaderError(
            status_code=422,
            message=(
                f"Bad {query_key} query param. Expected value "
                f"'{query_type} <PASETO>'"
            ),
        )

    return parts[1]


def raise_websocket_auth_error(error: AuthPASETOException) -> None:
    """Convert an auth-domain error into a websocket policy violation."""

    raise WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason=error.message,
    ) from error
