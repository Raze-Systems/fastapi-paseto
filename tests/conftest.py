from copy import deepcopy
from datetime import timedelta

import pytest

from fastapi_paseto import AuthPASETO


_AUTHPASETO_DEFAULTS: dict[str, object] = {
    "_token": None,
    "_token_parts": [],
    "_token_location": ("headers",),
    "_current_user": None,
    "_decoded_token": None,
    "_secret_key": None,
    "_public_key": None,
    "_private_key": None,
    "_purpose": "local",
    "_version": 4,
    "_decode_leeway": 0,
    "_encode_issuer": None,
    "_decode_issuer": None,
    "_decode_audience": "",
    "_denylist_enabled": False,
    "_denylist_token_checks": ("access", "refresh"),
    "_header_name": "Authorization",
    "_header_type": "Bearer",
    "_token_in_denylist_callback": None,
    "_json_key": "access_token",
    "_json_type": None,
    "_access_token_expires": timedelta(minutes=15),
    "_refresh_token_expires": timedelta(days=30),
    "_other_token_expires": timedelta(days=30),
}


def _reset_authpaseto_state() -> None:
    """Restore ``AuthPASETO`` class attributes to their defaults."""

    for attr_name, value in _AUTHPASETO_DEFAULTS.items():
        setattr(AuthPASETO, attr_name, deepcopy(value))


@pytest.fixture(autouse=True)
def reset_authpaseto_state():
    """Isolate tests from shared ``AuthPASETO`` class-level state."""

    _reset_authpaseto_state()
    yield
    _reset_authpaseto_state()


@pytest.fixture(scope="function")
def Authorize():
    """Provide a fresh ``AuthPASETO`` instance for each test."""

    return AuthPASETO()


@pytest.fixture(scope="function")
def configure_auth():
    """Load a deterministic test configuration onto ``AuthPASETO``."""

    def _configure(**overrides: object) -> None:
        settings: dict[str, object] = {
            "authpaseto_token_location": ["headers"],
            "authpaseto_secret_key": "testing",
            "authpaseto_header_name": "Authorization",
            "authpaseto_header_type": "Bearer",
            "authpaseto_json_key": "access_token",
            "authpaseto_json_type": None,
        }
        settings.update(overrides)

        @AuthPASETO.load_config
        def get_settings() -> dict[str, object]:
            """Return explicit config values for the test harness."""

            return settings

    return _configure
