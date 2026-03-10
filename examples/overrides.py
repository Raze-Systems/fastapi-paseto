from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


class JsonTokenPayload(BaseModel):
    paseto: str


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

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@app.get("/custom-header")
def custom_header(Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required(token_key="X-PASETO", token_prefix="Token")
    return {"user": Authorize.get_subject()}


@app.post("/json-override")
def json_override(payload: JsonTokenPayload, Authorize: AuthPASETO = Depends()):
    Authorize.paseto_required(
        location="json",
        token_key="paseto",
        token_prefix="Token",
    )
    return {"user": Authorize.get_subject(), "token_length": len(payload.paseto)}


@app.get("/server-side-override")
def server_side_override(Authorize: AuthPASETO = Depends()):
    token = Authorize.create_access_token(subject="service-user")
    Authorize.paseto_required(token=token)
    return {"user": Authorize.get_subject()}
