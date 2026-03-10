"""Helpers for extracting PASETO tokens from incoming requests."""

from json import JSONDecodeError

from fastapi import Request, WebSocket

from fastapi_paseto.exceptions import InvalidHeaderError


def _build_token_error_message(token_key: str, token_type: str | None) -> str:
    """Return the error message for a malformed token-bearing field."""

    if token_type:
        return f"Bad {token_key} header. Expected value '{token_type} <PASETO>'"
    return f"Bad {token_key} header. Expected value '<PASETO>'"


async def get_request_json(
    request: Request = None,
    websocket: WebSocket = None,
) -> dict[str, object]:
    """Return HTTP request JSON bodies and an empty mapping for websockets."""

    if websocket is not None:
        return {}

    try:
        if request is None:  # pragma: no cover
            return {}
        return await request.json()
    except JSONDecodeError:
        return {}


def extract_token_from_json(
    request_json: dict[str, object],
    json_key: str,
    json_type: str | None,
) -> str | None:
    """Extract a token from a JSON body using the configured key and prefix."""

    if json_key not in request_json:
        return None

    token = request_json[json_key]
    if not isinstance(token, str):
        raise InvalidHeaderError(
            status_code=422,
            message=_build_token_error_message(json_key, json_type),
        )

    if not json_type:
        if not token:
            raise InvalidHeaderError(
                status_code=422,
                message=_build_token_error_message(json_key, json_type),
            )
        return token

    parts = token.split()
    if len(parts) != 2 or parts[0] != json_type or not parts[1]:
        raise InvalidHeaderError(
            status_code=422,
            message=_build_token_error_message(json_key, json_type),
        )
    return parts[1]


def extract_token_from_header(
    header_value: str | None,
    header_name: str,
    header_type: str | None,
) -> str | None:
    """Extract a token from a header value using the configured prefix rules."""

    if not header_value:
        return None

    parts = header_value.split()
    if not header_type:
        if len(parts) != 1:
            raise InvalidHeaderError(
                status_code=422,
                message=f"Bad {header_name} header. Expected value '<PASETO>'",
            )
        return parts[0]

    if len(parts) != 2 or parts[0].lower() != header_type.lower() or not parts[1]:
        raise InvalidHeaderError(
            status_code=422,
            message=f"Bad {header_name} header. Expected value '{header_type} <PASETO>'",
        )

    return parts[1]
