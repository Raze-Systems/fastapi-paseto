"""Configuration validation for the ``fastapi_paseto`` package."""

from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator, model_validator

_ALLOWED_SEQUENCE_VALUES: dict[str, set[str]] = {
    "authpaseto_denylist_token_checks": {"access", "refresh"},
    "authpaseto_token_location": {"headers", "json"},
    "authpaseto_websocket_token_location": {"headers", "query"},
}

_SEQUENCE_ERROR_MESSAGES: dict[str, str] = {
    "authpaseto_denylist_token_checks": (
        "The 'authpaseto_denylist_token_checks' must be between 'access' or 'refresh'"
    ),
    "authpaseto_token_location": (
        "The 'authpaseto_token_location' must be between 'headers' or 'json'"
    ),
    "authpaseto_websocket_token_location": (
        "The 'authpaseto_websocket_token_location' must be between 'headers' or 'query'"
    ),
}


def _validate_expiry(name: str, value: bool | int | timedelta) -> bool | int | timedelta:
    """Reject unsupported boolean expiry values."""

    if value is True:
        raise ValueError(f"The '{name}' only accept value False (bool)")
    return value


class LoadConfig(BaseModel):
    """Validate and normalize library configuration."""

    model_config = ConfigDict(strict=True, str_min_length=1, str_strip_whitespace=True)

    authpaseto_token_location: list[str] | tuple[str, ...] = ("headers",)
    authpaseto_websocket_token_location: list[str] | tuple[str, ...] = ("headers",)
    authpaseto_secret_key: str | None = None
    authpaseto_public_key: str | None = None
    authpaseto_public_key_file: str | None = None
    authpaseto_private_key: str | None = None
    authpaseto_private_key_file: str | None = None
    authpaseto_purpose: str = "local"
    authpaseto_version: int = 4
    authpaseto_decode_leeway: int | timedelta = 0
    authpaseto_encode_issuer: str | None = None
    authpaseto_decode_issuer: str | None = None
    authpaseto_decode_audience: str | list[str] | tuple[str, ...] = ""
    authpaseto_denylist_enabled: bool = False
    authpaseto_denylist_token_checks: list[str] | tuple[str, ...] = (
        "access",
        "refresh",
    )
    authpaseto_header_name: str = "Authorization"
    authpaseto_json_key: str = "access_token"
    authpaseto_websocket_query_key: str = "token"
    authpaseto_header_type: str | None = "Bearer"
    authpaseto_json_type: str | None = None
    authpaseto_websocket_query_type: str | None = None
    authpaseto_access_token_expires: bool | int | timedelta = timedelta(minutes=15)
    authpaseto_refresh_token_expires: bool | int | timedelta = timedelta(days=30)
    authpaseto_other_token_expires: bool | int | timedelta = timedelta(days=30)

    @field_validator(
        "authpaseto_denylist_token_checks",
        "authpaseto_token_location",
        "authpaseto_websocket_token_location",
        mode="after",
    )
    @classmethod
    def validate_sequence_values(
        cls,
        values: list[str] | tuple[str, ...],
        info: ValidationInfo,
    ) -> list[str] | tuple[str, ...]:
        """Validate constrained string collections."""

        field_name = info.field_name
        allowed = _ALLOWED_SEQUENCE_VALUES[field_name]
        if invalid_value := next((value for value in values if value not in allowed), None):
            raise ValueError(_SEQUENCE_ERROR_MESSAGES[field_name])
        return values

    @field_validator(
        "authpaseto_access_token_expires",
        "authpaseto_refresh_token_expires",
        "authpaseto_other_token_expires",
        mode="after",
    )
    @classmethod
    def validate_expiry_fields(
        cls,
        value: bool | int | timedelta,
        info: ValidationInfo,
    ) -> bool | int | timedelta:
        """Ensure expiry fields only allow ``False`` as a boolean value."""

        return _validate_expiry(info.field_name, value)

    @model_validator(mode="after")
    def load_key_files(self) -> "LoadConfig":
        """Populate inline key fields from file paths when needed."""

        if (
            self.authpaseto_private_key is None
            and self.authpaseto_private_key_file is not None
        ):
            self.authpaseto_private_key = Path(self.authpaseto_private_key_file).read_text()

        if self.authpaseto_public_key is None and self.authpaseto_public_key_file is not None:
            self.authpaseto_public_key = Path(self.authpaseto_public_key_file).read_text()

        return self
