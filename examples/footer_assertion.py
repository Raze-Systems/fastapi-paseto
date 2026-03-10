from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException

app = FastAPI()

IMPLICIT_ASSERTION = "tenant-alpha"


class User(BaseModel):
    username: str
    password: str


@AuthPASETO.load_config
def get_config():
    return {"authpaseto_secret_key": "secret"}


@app.exception_handler(AuthPASETOException)
def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
def login(user: User, Authorize: AuthPASETO = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(
        subject=user.username,
        footer={"kid": "k4.lid.demo"},
    )
    bound_token = Authorize.create_access_token(
        subject=user.username,
        implicit_assertion=IMPLICIT_ASSERTION,
    )
    return {"access_token": access_token, "bound_token": bound_token}


@app.get("/footer")
def footer(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required()
    return {
        "footer": Authorize.get_token_footer(),
        "payload": Authorize.get_token_payload(),
    }


@app.get("/bound")
def bound(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required(implicit_assertion=IMPLICIT_ASSERTION)
    return {"user": Authorize.get_subject()}
