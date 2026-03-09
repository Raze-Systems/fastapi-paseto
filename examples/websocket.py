from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_paseto import AuthPASETO
from fastapi_paseto.exceptions import AuthPASETOException

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


@AuthPASETO.load_config
def get_config():
    """Return the application auth configuration."""

    return {"authpaseto_secret_key": "secret"}


@app.exception_handler(AuthPASETOException)
def authpaseto_exception_handler(request: Request, exc: AuthPASETOException):
    """Return auth exceptions as JSON for HTTP endpoints."""

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
def login(user: User, Authorize: AuthPASETO = Depends()):
    """Issue an access token for the demo user."""

    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@app.websocket("/ws/header")
async def websocket_header(
    websocket: WebSocket,
    Authorize: AuthPASETO = Depends(),
) -> None:
    """Authorize the websocket using the configured auth header."""

    Authorize.paseto_required()
    await websocket.accept()
    await websocket.send_json({"user": Authorize.get_subject()})
    await websocket.close()


@app.websocket("/ws/query")
async def websocket_query(
    websocket: WebSocket,
    Authorize: AuthPASETO = Depends(),
) -> None:
    """Authorize the websocket using a query parameter fallback."""

    Authorize.paseto_required(location="query")
    await websocket.accept()
    await websocket.send_json({"user": Authorize.get_subject()})
    await websocket.close()
