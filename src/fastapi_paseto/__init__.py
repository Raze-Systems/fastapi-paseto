"""FastAPI extension that provides PASETO Auth support"""

from importlib.metadata import PackageNotFoundError, version

from ._version import __version__ as _source_version

try:
    __version__ = version("fastapi-paseto")
except PackageNotFoundError:
    __version__ = _source_version

from .auth_paseto import AuthPASETO
