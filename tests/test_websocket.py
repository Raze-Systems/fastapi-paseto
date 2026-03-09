from collections.abc import Callable

import pytest
from fastapi import Depends, FastAPI, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from fastapi_paseto import AuthPASETO


@pytest.fixture(scope="function")
def denylist() -> set[str]:
    """Store revoked token identifiers for the current test."""

    return set()


@pytest.fixture(scope="function")
def make_client(
    configure_auth: Callable[..., None],
    denylist: set[str],
) -> Callable[..., TestClient]:
    """Build a websocket-enabled test client with configurable auth settings."""

    def _make_client(**config_overrides: object) -> TestClient:
        configure_auth(**config_overrides)

        @AuthPASETO.token_in_denylist_loader
        def check_if_token_in_denylist(payload: dict[str, object]) -> bool:
            """Return whether the token identifier has been revoked."""

            return payload["jti"] in denylist

        app = FastAPI()

        @app.websocket("/required")
        async def required(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required()
            await websocket.accept()
            await websocket.send_json(
                {
                    "jti": Authorize.get_jti(),
                    "payload": Authorize.get_token_payload(),
                    "subject": Authorize.get_subject(),
                    "paseto_subject": Authorize.get_paseto_subject(),
                }
            )
            await websocket.close()

        @app.websocket("/optional")
        async def optional(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(optional=True)
            await websocket.accept()
            await websocket.send_json(
                {
                    "payload": Authorize.get_token_payload(),
                    "subject": Authorize.get_subject(),
                }
            )
            await websocket.close()

        @app.websocket("/refresh")
        async def refresh(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(refresh_token=True)
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/fresh")
        async def fresh(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(fresh=True)
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/other")
        async def other(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(type="other")
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/base64")
        async def base64_route(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(base64_encoded=True)
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/query")
        async def query_route(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required()
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/query-override")
        async def query_override(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(
                location="query",
                token_key="paseto",
                token_prefix="Bearer",
            )
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/override")
        async def override(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            token = Authorize.create_access_token(subject="override-user")
            Authorize.paseto_required(token=token)
            await websocket.accept()
            await websocket.send_json({"subject": Authorize.get_subject()})
            await websocket.close()

        @app.websocket("/json-location")
        async def json_location(
            websocket: WebSocket,
            Authorize: AuthPASETO = Depends(),
        ) -> None:
            Authorize.paseto_required(location="json")
            await websocket.accept()
            await websocket.close()

        return TestClient(app)

    return _make_client


def expect_disconnect(
    client: TestClient,
    path: str,
    *,
    headers: dict[str, str] | None = None,
) -> WebSocketDisconnect:
    """Assert that the websocket connection is rejected and return the exception."""

    with pytest.raises(WebSocketDisconnect) as exc_info:
        connect_kwargs = {"headers": headers} if headers is not None else {}
        with client.websocket_connect(path, **connect_kwargs):
            pass
    return exc_info.value


def test_websocket_required_valid_header(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client()
    token = Authorize.create_access_token(subject="test")

    with client.websocket_connect("/required", headers={"Authorization": f"Bearer {token}"}) as websocket:
        message = websocket.receive_json()

    assert message["subject"] == "test"
    assert message["paseto_subject"] == "test"
    assert message["payload"]["sub"] == "test"
    assert message["payload"]["type"] == "access"
    assert message["jti"] == message["payload"]["jti"]


def test_websocket_required_missing_token(make_client: Callable[..., TestClient]) -> None:
    client = make_client()

    exc = expect_disconnect(client, "/required")
    assert exc.code == 1008
    assert exc.reason == "PASETO Authorization Token required"


def test_websocket_optional_without_token(make_client: Callable[..., TestClient]) -> None:
    client = make_client()

    with client.websocket_connect("/optional") as websocket:
        message = websocket.receive_json()

    assert message == {"payload": None, "subject": None}


def test_websocket_refresh_required(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client()
    access_token = Authorize.create_access_token(subject="test")
    refresh_token = Authorize.create_refresh_token(subject="test")

    exc = expect_disconnect(
        client,
        "/refresh",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert exc.code == 1008
    assert exc.reason == "Refresh token required but access provided"

    with client.websocket_connect(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "test"}


def test_websocket_fresh_required(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client()
    stale_token = Authorize.create_access_token(subject="test")
    fresh_token = Authorize.create_access_token(subject="test", fresh=True)

    exc = expect_disconnect(
        client,
        "/fresh",
        headers={"Authorization": f"Bearer {stale_token}"},
    )
    assert exc.code == 1008
    assert exc.reason == "PASETO access token is not fresh"

    with client.websocket_connect(
        "/fresh",
        headers={"Authorization": f"Bearer {fresh_token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "test"}


def test_websocket_custom_type(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client()
    invalid_token = Authorize.create_access_token(subject="test")
    valid_token = Authorize.create_token(subject="test", type="other")

    exc = expect_disconnect(
        client,
        "/other",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert exc.code == 1008
    assert exc.reason == "other token required but access provided"

    with client.websocket_connect(
        "/other",
        headers={"Authorization": f"Bearer {valid_token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "test"}


def test_websocket_base64(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client()
    encoded_token = Authorize.create_access_token(subject="test", base64_encode=True)

    with client.websocket_connect(
        "/base64",
        headers={"Authorization": f"Bearer {encoded_token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "test"}

    invalid_token = Authorize.create_access_token(subject="test")
    exc = expect_disconnect(
        client,
        "/base64",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert exc.code == 1008
    assert exc.reason == "Invalid base64 encoding"


def test_websocket_query_transport_default_and_override(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    default_client = make_client()
    query_token = Authorize.create_access_token(subject="query-user")

    missing_exc = expect_disconnect(default_client, f"/query?token={query_token}")
    assert missing_exc.code == 1008
    assert missing_exc.reason == "PASETO Authorization Token required"

    query_client = make_client(authpaseto_websocket_token_location=["query"])
    with query_client.websocket_connect(f"/query?token={query_token}") as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "query-user"}

    prefixed_token = Authorize.create_access_token(subject="override-user")
    with default_client.websocket_connect(
        f"/query-override?paseto=Bearer%20{prefixed_token}"
    ) as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "override-user"}


def test_websocket_token_override(
    make_client: Callable[..., TestClient],
) -> None:
    client = make_client()

    with client.websocket_connect("/override") as websocket:
        message = websocket.receive_json()

    assert message == {"subject": "override-user"}


def test_websocket_json_location_is_not_supported(
    make_client: Callable[..., TestClient],
) -> None:
    client = make_client()

    exc = expect_disconnect(client, "/json-location")
    assert exc.code == 1008
    assert exc.reason == "json token location is not supported for WebSocket connections"


def test_websocket_issuer_and_audience_validation(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
) -> None:
    client = make_client(
        authpaseto_decode_issuer="urn:expected",
        authpaseto_decode_audience=["urn:expected"],
    )
    valid_token = Authorize.create_access_token(
        subject="test",
        audience=["urn:expected"],
        user_claims={"iss": "urn:expected"},
    )
    invalid_audience = Authorize.create_access_token(
        subject="test",
        audience=["urn:other"],
        user_claims={"iss": "urn:expected"},
    )

    with client.websocket_connect(
        "/required",
        headers={"Authorization": f"Bearer {valid_token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message["subject"] == "test"

    exc = expect_disconnect(
        client,
        "/required",
        headers={"Authorization": f"Bearer {invalid_audience}"},
    )
    assert exc.code == 1008
    assert exc.reason == "aud verification failed."


def test_websocket_denylisted_token(
    make_client: Callable[..., TestClient],
    Authorize: AuthPASETO,
    denylist: set[str],
) -> None:
    client = make_client(authpaseto_denylist_enabled=True)
    token = Authorize.create_access_token(subject="test", fresh=True)

    with client.websocket_connect(
        "/required",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        message = websocket.receive_json()

    denylist.add(message["jti"])

    exc = expect_disconnect(
        client,
        "/required",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert exc.code == 1008
    assert exc.reason == "Token has been revoked"
