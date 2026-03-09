"""Public compatibility module for the ``AuthPASETO`` implementation."""

from ._internal.auth import AuthPASETO
from ._internal.request import get_request_json

__all__ = ["AuthPASETO", "get_request_json"]
