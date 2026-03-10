import pytest
from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def client(configure_auth):
    configure_auth()
    app = FastAPI()

    @app.exception_handler(AuthPASETOException)
    def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    @app.get("/protected")
    def protected(Authorize: AuthPASETO = Depends()):
        Authorize.paseto_required()
        return {"hello": "world"}

    client = TestClient(app)
    return client


def test_header_without_paseto(client):
    response = client.get("/protected", headers={"Authorization": "Bearer"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bad Authorization header. Expected value 'Bearer <PASETO>'"
    }

    response = client.get("/protected", headers={"Authorization": "Bearer "})
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bad Authorization header. Expected value 'Bearer <PASETO>'"
    }


def test_header_without_bearer(client):
    response = client.get("/protected", headers={"Authorization": "Test asd"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bad Authorization header. Expected value 'Bearer <PASETO>'"
    }

    response = client.get("/protected", headers={"Authorization": "Test "})
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Bad Authorization header. Expected value 'Bearer <PASETO>'"
    }


def test_header_invalid_paseto(client):
    response = client.get("/protected", headers={"Authorization": "Bearer asd"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid PASETO format"}


def test_header_requires_exact_bearer_scheme(client, Authorize):
    token = Authorize.create_access_token(subject="test")

    invalid_scheme_response = client.get(
        "/protected",
        headers={"Authorization": f"NotBearer {token}"},
    )
    assert invalid_scheme_response.status_code == 422
    assert invalid_scheme_response.json() == {
        "detail": "Bad Authorization header. Expected value 'Bearer <PASETO>'"
    }

    lowercase_scheme_response = client.get(
        "/protected",
        headers={"Authorization": f"bearer {token}"},
    )
    assert lowercase_scheme_response.status_code == 200
    assert lowercase_scheme_response.json() == {"hello": "world"}


def test_valid_header(client, Authorize):
    token = Authorize.create_access_token(subject="test")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}
