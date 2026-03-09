from collections.abc import Callable, Mapping
from datetime import timedelta

from pydantic import ValidationError
from pydantic_settings import BaseSettings
from pyseto import Token

from fastapi_paseto_auth.config import LoadConfig


class AuthConfig:
    _token = None
    _token_parts = []
    _token_location = ("headers",)
    _current_user = None
    _decoded_token: Token | None = None

    _secret_key = None
    _public_key = None
    _private_key = None
    _purpose = "local"
    _version = 4
    _decode_leeway = 0
    _encode_issuer = None
    _decode_issuer = None
    _decode_audience = ""
    _denylist_enabled = False
    _denylist_token_checks = ("access", "refresh")
    _header_name = "Authorization"
    _header_type = "Bearer"
    _json_key = "access_token"
    _json_type = None
    _token_in_denylist_callback = None
    _access_token_expires = timedelta(minutes=15)
    _refresh_token_expires = timedelta(days=30)
    _other_token_expires = timedelta(days=30)

    @property
    def paseto_in_headers(self) -> bool:
        return "headers" in self._token_location

    @property
    def paseto_in_json(self) -> bool:
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
        try:
            raw_settings = settings()
            config = LoadConfig(**cls._normalize_settings(raw_settings))

            cls._token_location = config.authpaseto_token_location
            cls._secret_key = config.authpaseto_secret_key
            cls._public_key = config.authpaseto_public_key
            cls._private_key = config.authpaseto_private_key
            cls._purpose = config.authpaseto_purpose
            cls._version = config.authpaseto_version
            cls._decode_leeway = config.authpaseto_decode_leeway
            cls._encode_issuer = config.authpaseto_encode_issuer
            cls._decode_issuer = config.authpaseto_decode_issuer
            cls._decode_audience = config.authpaseto_decode_audience
            cls._denylist_enabled = config.authpaseto_denylist_enabled
            cls._denylist_token_checks = config.authpaseto_denylist_token_checks
            cls._header_name = config.authpaseto_header_name
            cls._header_type = config.authpaseto_header_type
            cls._json_key = config.authpaseto_json_key
            cls._json_type = config.authpaseto_json_type
            cls._access_token_expires = config.authpaseto_access_token_expires
            cls._refresh_token_expires = config.authpaseto_refresh_token_expires
            cls._other_token_expires = config.authpaseto_other_token_expires
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
        """
        This decorator sets the callback function that will be called when
        a protected endpoint is accessed and will check if the PASETO has been
        been revoked. By default, this callback is not used.

        *HINT*: The callback must be a function that takes decrypted_token argument,
        args for object AuthPASETO and this is not used, decrypted_token is decode
        PASETO (python dictionary) and returns *`True`* if the token has been deny,
        or *`False`* otherwise.
        """
        cls._token_in_denylist_callback = callback
        return cls
