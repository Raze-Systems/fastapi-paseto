from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


ISSUER = "https://auth.example.com"
AUDIENCE = ["urn:customers"]


@AuthPASETO.load_config
def get_config():
    return {
        "authpaseto_secret_key": "secret",
        "authpaseto_encode_issuer": ISSUER,
        "authpaseto_decode_issuer": ISSUER,
        "authpaseto_decode_audience": AUDIENCE,
    }


@app.exception_handler(AuthPASETOException)
def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
def login(user: User, Authorize: AuthPASETO = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(
        subject=user.username,
        audience=AUDIENCE,
    )
    base64_token = Authorize.create_access_token(
        subject=user.username,
        audience=AUDIENCE,
        base64_encode=True,
    )
    email_verify_token = Authorize.create_token(
        subject=user.username,
        type="email-verify",
        audience=AUDIENCE,
        user_claims={"iss": ISSUER},
    )
    return {
        "access_token": access_token,
        "base64_token": base64_token,
        "email_verify_token": email_verify_token,
    }


@app.get("/audience-protected")
def audience_protected(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required()
    return {"user": Authorize.get_subject()}


@app.get("/base64-protected")
def base64_protected(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required(base64_encoded=True)
    return {"user": Authorize.get_subject()}


@app.get("/email-verify")
def email_verify(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required(type="email-verify")
    return {"user": Authorize.get_subject()}
