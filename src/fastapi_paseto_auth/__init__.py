"""FastAPI extension that provides PASETO Auth support"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fastapi-paseto-auth")
except PackageNotFoundError:
    __version__ = "0.6.0"

from .auth_paseto import AuthPASETO
