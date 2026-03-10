from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


class AccessTokenPayload(BaseModel):
    access_token: str


class RefreshTokenPayload(BaseModel):
    refresh_token: str


@AuthPASETO.load_config
def get_config():
    return {
        "authpaseto_secret_key": "secret",
        "authpaseto_token_location": ["headers", "json"],
        "authpaseto_json_key": "access_token",
        "authpaseto_json_type": None,
    }


@app.exception_handler(AuthPASETOException)
def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
def login(user: User, Authorize: AuthPASETO = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/json-protected")
def json_protected(
    payload: AccessTokenPayload,
    Authorize: AuthPASETO = Depends(),
):
    Authorize.paseto_required(location="json")
    return {"user": Authorize.get_subject(), "token_length": len(payload.access_token)}


@app.post("/json-refresh")
def json_refresh(
    payload: RefreshTokenPayload,
    Authorize: AuthPASETO = Depends(),
):
    Authorize.paseto_required(
        location="json",
        token_key="refresh_token",
        refresh_token=True,
    )
    new_access_token = Authorize.create_access_token(subject=Authorize.get_subject())
    return {"access_token": new_access_token, "refresh_token_length": len(payload.refresh_token)}
