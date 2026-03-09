"""Shared mutable configuration state for ``AuthPASETO``."""

from collections.abc import Callable, Mapping
from datetime import timedelta

from pydantic import ValidationError
from pydantic_settings import BaseSettings
from pyseto import Token

from fastapi_paseto.config import LoadConfig

_CONFIG_ATTRIBUTE_MAP: tuple[tuple[str, str], ...] = (
    ("_token_location", "authpaseto_token_location"),
    ("_websocket_token_location", "authpaseto_websocket_token_location"),
    ("_secret_key", "authpaseto_secret_key"),
    ("_public_key", "authpaseto_public_key"),
    ("_private_key", "authpaseto_private_key"),
    ("_purpose", "authpaseto_purpose"),
    ("_version", "authpaseto_version"),
    ("_decode_leeway", "authpaseto_decode_leeway"),
    ("_encode_issuer", "authpaseto_encode_issuer"),
    ("_decode_issuer", "authpaseto_decode_issuer"),
    ("_decode_audience", "authpaseto_decode_audience"),
    ("_denylist_enabled", "authpaseto_denylist_enabled"),
    ("_denylist_token_checks", "authpaseto_denylist_token_checks"),
    ("_header_name", "authpaseto_header_name"),
    ("_header_type", "authpaseto_header_type"),
    ("_json_key", "authpaseto_json_key"),
    ("_json_type", "authpaseto_json_type"),
    ("_websocket_query_key", "authpaseto_websocket_query_key"),
    ("_websocket_query_type", "authpaseto_websocket_query_type"),
    ("_access_token_expires", "authpaseto_access_token_expires"),
    ("_refresh_token_expires", "authpaseto_refresh_token_expires"),
    ("_other_token_expires", "authpaseto_other_token_expires"),
)


class AuthConfig:
    """Hold class-level configuration shared by all ``AuthPASETO`` instances."""

    _token: str | None = None
    _token_parts: list[str] = []
    _token_location: list[str] | tuple[str, ...] = ("headers",)
    _websocket_token_location: list[str] | tuple[str, ...] = ("headers",)
    _current_user: str | int | None = None
    _decoded_token: Token | None = None

    _secret_key: str | None = None
    _public_key: str | None = None
    _private_key: str | None = None
    _purpose: str = "local"
    _version: int = 4
    _decode_leeway: int | timedelta = 0
    _encode_issuer: str | None = None
    _decode_issuer: str | None = None
    _decode_audience: str | list[str] | tuple[str, ...] = ""
    _denylist_enabled = False
    _denylist_token_checks: list[str] | tuple[str, ...] = ("access", "refresh")
    _header_name: str = "Authorization"
    _header_type: str | None = "Bearer"
    _json_key: str = "access_token"
    _json_type: str | None = None
    _websocket_query_key: str = "token"
    _websocket_query_type: str | None = None
    _token_in_denylist_callback: Callable[..., bool] | None = None
    _access_token_expires = timedelta(minutes=15)
    _refresh_token_expires = timedelta(days=30)
    _other_token_expires = timedelta(days=30)

    @property
    def paseto_in_headers(self) -> bool:
        """Return whether headers are configured as a token source."""

        return "headers" in self._token_location

    @property
    def paseto_in_json(self) -> bool:
        """Return whether JSON bodies are configured as a token source."""

        return "json" in self._token_location

    @staticmethod
    def _normalize_settings(
        settings: Mapping[str, object] | BaseSettings,
    ) -> dict[str, object]:
        """Normalize supported config inputs into lowercase keys."""

        if isinstance(settings, BaseSettings):
            return {key.lower(): value for key, value in settings.model_dump().items()}

        if isinstance(settings, Mapping):
            return {str(key).lower(): value for key, value in settings.items()}

        raise TypeError(
            "Config must be a mapping or pydantic-settings 'BaseSettings'"
        )

    @classmethod
    def load_config(
        cls, settings: Callable[[], Mapping[str, object] | BaseSettings]
    ) -> "AuthConfig":
        """Load configuration values from a callback into class-level state."""

        try:
            raw_settings = settings()
            config = LoadConfig(**cls._normalize_settings(raw_settings))
            for attribute_name, config_name in _CONFIG_ATTRIBUTE_MAP:
                setattr(cls, attribute_name, getattr(config, config_name))
        except ValidationError:
            raise
        except TypeError:
            raise
        except Exception as err:
            raise TypeError(
                "Config must be a mapping or pydantic-settings 'BaseSettings'"
            ) from err

        return cls

    @classmethod
    def token_in_denylist_loader(cls, callback: Callable[..., bool]) -> "AuthConfig":
        """Register the callback used to decide whether a token is revoked."""

        cls._token_in_denylist_callback = callback
        return cls
