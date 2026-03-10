import pytest
from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

@pytest.fixture(scope="function")
def denylist() -> set[str]:
    """Store revoked token identifiers for the current test only."""

    return set()


def build_client(
    configure_auth,
    denylist: set[str],
    *,
    token_checks: list[str] | tuple[str, ...] = ("access", "refresh"),
) -> TestClient:
    """Build a client with configurable denylist token-type checks."""

    configure_auth(
        authpaseto_denylist_enabled=True,
        authpaseto_denylist_token_checks=token_checks,
    )

    @AuthPASETO.token_in_denylist_loader
    def check_if_token_in_denylist(decrypted_token):
        jti = decrypted_token["jti"]
        return jti in denylist

    app = FastAPI()

    @app.exception_handler(AuthPASETOException)
    def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.get("/paseto-required")
    def paseto_required(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {"hello": "world"}

    @app.get("/paseto-optional")
    def paseto_optional(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {"hello": "world"}

    @app.get("/paseto-refresh-required")
    def paseto_refresh_required(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(refresh_token=True)
        return {"hello": "world"}

    @app.get("/fresh-paseto-required")
    def fresh_paseto_required(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(fresh=True)
        return {"hello": "world"}

    @app.get("/get-jti")
    def get_access_jti(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {"jti": Authorize.get_jti()}

    @app.get("/get-refresh-jti")
    def get_refresh_jti(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required(refresh_token=True)
        return {"jti": Authorize.get_jti()}

    return TestClient(app)


@pytest.fixture(scope="function")
def client(configure_auth, denylist):
    return build_client(configure_auth, denylist)


@pytest.fixture(scope="function")
def access_token(Authorize, configure_auth):
    configure_auth(
        authpaseto_denylist_enabled=True,
        authpaseto_denylist_token_checks=["access", "refresh"],
    )
    return Authorize.create_access_token(subject="test", fresh=True)


@pytest.fixture(scope="function")
def refresh_token(Authorize, configure_auth):
    configure_auth(
        authpaseto_denylist_enabled=True,
        authpaseto_denylist_token_checks=["access", "refresh"],
    )
    return Authorize.create_refresh_token(subject="test")


@pytest.fixture(scope="function")
def denylisted_access_token(client, access_token, denylist):
    """Return an access token after revoking its identifier."""

    response = client.get("/get-jti", headers={"Authorization": f"Bearer {access_token}"})
    denylist.add(response.json()["jti"])
    return access_token


@pytest.fixture(scope="function")
def denylisted_refresh_token(client, refresh_token, denylist):
    """Return a refresh token after revoking its identifier."""

    response = client.get(
        "/get-refresh-jti", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    denylist.add(response.json()["jti"])
    return refresh_token


@pytest.mark.parametrize(
    "url", ["/paseto-required", "/paseto-optional", "/fresh-paseto-required"]
)
def test_non_denylisted_access_token(client, url, access_token, Authorize: AuthPASETO):
    response = client.get(url, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}


def test_non_denylisted_refresh_token(client, refresh_token, Authorize: AuthPASETO):
    url = "/paseto-refresh-required"
    response = client.get(url, headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}


@pytest.mark.parametrize(
    "url", ["/paseto-required", "/paseto-optional", "/fresh-paseto-required"]
)
def test_denylisted_access_token(client, url, denylisted_access_token):
    response = client.get(
        url, headers={"Authorization": f"Bearer {denylisted_access_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has been revoked"}


def test_denylisted_refresh_token(client, denylisted_refresh_token):
    url = "/paseto-refresh-required"
    response = client.get(
        url, headers={"Authorization": f"Bearer {denylisted_refresh_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has been revoked"}


def test_refresh_only_denylist_checks_skip_access_tokens(
    configure_auth,
    denylist: set[str],
    Authorize: AuthPASETO,
):
    client = build_client(configure_auth, denylist, token_checks=["refresh"])
    token = Authorize.create_access_token(subject="test", fresh=True)

    response = client.get("/get-jti", headers={"Authorization": f"Bearer {token}"})
    denylist.add(response.json()["jti"])

    protected_response = client.get(
        "/paseto-required",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_response.status_code == 200
    assert protected_response.json() == {"hello": "world"}


def test_refresh_only_denylist_checks_still_revoke_refresh_tokens(
    configure_auth,
    denylist: set[str],
    Authorize: AuthPASETO,
):
    client = build_client(configure_auth, denylist, token_checks=["refresh"])
    token = Authorize.create_refresh_token(subject="test")

    response = client.get(
        "/get-refresh-jti",
        headers={"Authorization": f"Bearer {token}"},
    )
    denylist.add(response.json()["jti"])

    revoked_response = client.get(
        "/paseto-refresh-required",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert revoked_response.status_code == 401
    assert revoked_response.json() == {"detail": "Token has been revoked"}
