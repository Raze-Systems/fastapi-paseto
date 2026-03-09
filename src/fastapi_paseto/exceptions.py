"""Exception hierarchy for the ``fastapi_paseto`` package."""

class AuthPASETOException(Exception):
    """Base exception for all ``fastapi_paseto`` errors."""

    def __init__(self, status_code: int, message: str, **kwargs) -> None:
        """Store the HTTP status code and human-readable error message."""

        super().__init__(**kwargs)
        self.status_code = status_code
        self.message = message


class InvalidHeaderError(AuthPASETOException):
    """Raised when a token-bearing header or JSON field is malformed."""


class InvalidTokenTypeError(AuthPASETOException):
    """Raised when a token's ``type`` claim does not match the requirement."""


class PASETODecodeError(AuthPASETOException):
    """Raised when a PASETO cannot be decoded or verified."""


class InvalidPASETOVersionError(AuthPASETOException):
    """Raised when the token version prefix is not supported."""


class InvalidPASETOArgumentError(AuthPASETOException):
    """Raised when a validation call receives incompatible arguments."""


class InvalidPASETOPurposeError(AuthPASETOException):
    """Raised when the token purpose segment is not supported."""


class MissingTokenError(AuthPASETOException):
    """Raised when no token is available for a required endpoint."""


class RevokedTokenError(AuthPASETOException):
    """Raised when a denylisted token is used."""


class AccessTokenRequired(AuthPASETOException):
    """Raised when an access token is required but another token is provided."""


class RefreshTokenRequired(AuthPASETOException):
    """Raised when a refresh token is required but another token is provided."""


class FreshTokenRequired(AuthPASETOException):
    """Raised when a fresh access token is required but a stale one is provided."""
