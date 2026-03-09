"""Helpers for extracting PASETO tokens from incoming requests."""

from json import JSONDecodeError

from fastapi import Request, WebSocket

from fastapi_paseto.exceptions import InvalidHeaderError


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
    if not json_type:
        if not token:
            raise InvalidHeaderError(
                status_code=422,
                message=f"Bad {json_key} header. Excepted value 'Bearer <PASETO>'",
            )
        return token

    token_prefix, token = token.split()
    if not token or token_prefix != json_type:
        raise InvalidHeaderError(
            status_code=422,
            message=f"Bad {json_key} header. Expected value '{json_type} <PASETO>'",
        )
    return token


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
                message=f"Bad {header_name} header. Excepted value '<PASETO>'",
            )
        return parts[0]

    if not parts[0].__contains__(header_type) or len(parts) != 2:
        raise InvalidHeaderError(
            status_code=422,
            message=f"Bad {header_name} header. Expected value '{header_type} <PASETO>'",
        )

    return parts[1]
