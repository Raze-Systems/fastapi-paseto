import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException


@pytest.fixture(scope="function")
def client(configure_auth, key_material):
    """Return an app client with routes covering footer and assertion features."""

    configure_auth(
        authpaseto_secret_key="secret-key",
        authpaseto_private_key=key_material["private"],
        authpaseto_public_key=key_material["public"],
    )
    app = FastAPI()

    @app.exception_handler(AuthPASETOException)
    def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.get("/protected")
    def protected(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {"subject": Authorize.get_subject()}

    @app.get("/refresh")
    def refresh(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(refresh_token=True)
        return {"subject": Authorize.get_subject()}

    @app.get("/refresh-footer")
    def refresh_footer(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(refresh_token=True)
        return {
            "footer": Authorize.get_token_footer(),
            "payload": Authorize.get_token_payload(),
        }

    @app.get("/custom")
    def custom(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(type="email-verify")
        return {"subject": Authorize.get_subject()}

    @app.get("/footer")
    def footer(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {
            "footer": Authorize.get_token_footer(),
            "payload": Authorize.get_token_payload(),
        }

    @app.get("/implicit")
    def implicit(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(implicit_assertion="channel-binding")
        return {"subject": Authorize.get_subject()}

    return TestClient(app)


def test_local_footer_round_trip(client: TestClient, Authorize: AuthPASETO) -> None:
    token = Authorize.create_access_token(
        subject="footer-user",
        footer={"kid": "k4.lid.example"},
    )

    response = client.get("/footer", headers={"Authorization": f"Bearer {token}"})
    body = response.json()

    assert response.status_code == 200
    assert body == {
        "footer": {"kid": "k4.lid.example"},
        "payload": {
            "sub": "footer-user",
            "type": "access",
            "fresh": False,
            "jti": body["payload"]["jti"],
            "nbf": body["payload"]["nbf"],
            "exp": body["payload"]["exp"],
            "iat": body["payload"]["iat"],
        },
    }


def test_public_token_round_trip(client: TestClient, Authorize: AuthPASETO) -> None:
    token = Authorize.create_access_token(subject="public-user", purpose="public")

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"subject": "public-user"}


def test_public_refresh_token_with_footer(client: TestClient, Authorize: AuthPASETO) -> None:
    token = Authorize.create_refresh_token(
        subject="refresh-user",
        purpose="public",
        footer={"kid": "k4.pid.example"},
    )

    refresh_response = client.get(
        "/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    footer_response = client.get(
        "/refresh-footer",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert refresh_response.status_code == 200
    assert refresh_response.json() == {"subject": "refresh-user"}
    assert footer_response.status_code == 200
    assert footer_response.json()["footer"] == {"kid": "k4.pid.example"}
    assert footer_response.json()["payload"]["sub"] == "refresh-user"
    assert footer_response.json()["payload"]["type"] == "refresh"


def test_implicit_assertion_round_trip(client: TestClient, Authorize: AuthPASETO) -> None:
    token = Authorize.create_access_token(
        subject="asserted-user",
        implicit_assertion="channel-binding",
    )

    valid_response = client.get(
        "/implicit",
        headers={"Authorization": f"Bearer {token}"},
    )
    invalid_response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert valid_response.status_code == 200
    assert valid_response.json() == {"subject": "asserted-user"}
    assert invalid_response.status_code == 422
    assert invalid_response.json() == {"detail": "Failed to decrypt."}


def test_refresh_and_custom_tokens_accept_explicit_issuer(
    client: TestClient,
    Authorize: AuthPASETO,
) -> None:
    AuthPASETO._decode_issuer = "urn:example"

    refresh_token = Authorize.create_refresh_token(
        subject="refresh-user",
        issuer="urn:example",
    )
    custom_token = Authorize.create_token(
        subject="custom-user",
        type="email-verify",
        issuer="urn:example",
    )

    refresh_response = client.get(
        "/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    custom_response = client.get(
        "/custom",
        headers={"Authorization": f"Bearer {custom_token}"},
    )

    assert refresh_response.status_code == 200
    assert refresh_response.json() == {"subject": "refresh-user"}
    assert custom_response.status_code == 200
    assert custom_response.json() == {"subject": "custom-user"}


@pytest.mark.parametrize("reserved_claim", ["sub", "type", "jti", "exp", "iss"])
def test_reserved_claims_are_rejected(
    Authorize: AuthPASETO,
    reserved_claim: str,
    configure_auth,
) -> None:
    configure_auth(authpaseto_secret_key="secret-key")

    with pytest.raises(
        ValueError,
        match=r"user_claims cannot include reserved claims",
    ):
        Authorize.create_access_token(
            subject="test",
            user_claims={reserved_claim: "override"},
        )


@pytest.mark.parametrize(
    ("method_name", "value", "message"),
    [
        ("create_access_token", 1, "footer must be bytes, str, or dict"),
        ("create_access_token", [], "footer must be bytes, str, or dict"),
    ],
)
def test_invalid_footer_type_is_rejected(
    Authorize: AuthPASETO,
    method_name: str,
    value: object,
    message: str,
    configure_auth,
) -> None:
    configure_auth(authpaseto_secret_key="secret-key")
    create_method = getattr(Authorize, method_name)

    with pytest.raises(TypeError, match=message):
        create_method(subject="test", footer=value)


@pytest.mark.parametrize(
    ("create_method_name", "call_kwargs"),
    [
        ("create_access_token", {"subject": "test", "implicit_assertion": 1}),
        ("create_refresh_token", {"subject": "test", "implicit_assertion": []}),
        (
            "create_token",
            {
                "subject": "test",
                "type": "email-verify",
                "implicit_assertion": object(),
            },
        ),
    ],
)
def test_invalid_implicit_assertion_type_is_rejected(
    Authorize: AuthPASETO,
    create_method_name: str,
    call_kwargs: dict[str, object],
    configure_auth,
) -> None:
    configure_auth(authpaseto_secret_key="secret-key")
    create_method = getattr(Authorize, create_method_name)

    with pytest.raises(TypeError, match="implicit_assertion must be bytes or str"):
        create_method(**call_kwargs)
