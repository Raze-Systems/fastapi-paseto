"""Key-management example for FastAPI PASETO."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, FastAPI

from fastapi_paseto import AuthPASETO

app = FastAPI()


def _read_required_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.environ.get(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def _read_text_file(path_env_name: str) -> str:
    """Return UTF-8 text from a path provided by an environment variable."""

    return Path(_read_required_env(path_env_name)).read_text(encoding="utf-8").strip()


def load_local_secret() -> str:
    """Return the local-purpose secret using a secure retrieval strategy."""

    backend = os.environ.get("PASETO_SECRET_BACKEND", "env")
    match backend:
        case "env":
            return _read_required_env("PASETO_LOCAL_SECRET")
        case "file":
            # Fallback only. Prefer a secret manager or platform-injected secret.
            return _read_text_file("PASETO_LOCAL_SECRET_FILE")
        case "fernet":
            raise RuntimeError(
                "Install 'cryptography' and decrypt the wrapped secret before "
                "returning it from this helper."
            )
        case "vault":
            raise RuntimeError(
                "Fetch the secret from Vault here and return it as plain text."
            )
        case "tpm":
            raise RuntimeError(
                "Unseal the secret with tpm2-pytss here and return it as plain text."
            )
        case _:
            raise RuntimeError(f"Unsupported PASETO_SECRET_BACKEND: {backend}")


def load_public_keys() -> tuple[str, str]:
    """Return the private/public key pair for public-purpose tokens."""

    backend = os.environ.get("PASETO_PUBLIC_KEY_BACKEND", "env")
    match backend:
        case "env":
            return (
                _read_required_env("PASETO_PRIVATE_KEY_PEM"),
                _read_required_env("PASETO_PUBLIC_KEY_PEM"),
            )
        case "file":
            # Fallback only. Use when mounted files are the only viable interface.
            return (
                _read_text_file("PASETO_PRIVATE_KEY_FILE"),
                _read_text_file("PASETO_PUBLIC_KEY_FILE"),
            )
        case "vault":
            raise RuntimeError(
                "Fetch the private and public key PEM values from Vault here."
            )
        case "tpm":
            raise RuntimeError(
                "Unseal the private key with tpm2-pytss and retrieve the public key "
                "from a trusted distribution channel here."
            )
        case _:
            raise RuntimeError(f"Unsupported PASETO_PUBLIC_KEY_BACKEND: {backend}")


@AuthPASETO.load_config
def get_config() -> dict[str, str]:
    """Return FastAPI PASETO configuration using secure retrieval helpers."""

    purpose = os.environ.get("PASETO_PURPOSE", "local")
    match purpose:
        case "local":
            return {
                "authpaseto_secret_key": load_local_secret(),
                "authpaseto_purpose": "local",
            }
        case "public":
            private_key, public_key = load_public_keys()
            return {
                "authpaseto_private_key": private_key,
                "authpaseto_public_key": public_key,
                "authpaseto_purpose": "public",
            }
        case _:
            raise RuntimeError(f"Unsupported PASETO_PURPOSE: {purpose}")


@app.get("/token")
def issue_token(Authorize: AuthPASETO = Depends()) -> dict[str, str]:
    """Issue a sample access token using the configured key material."""

    return {"access_token": Authorize.create_access_token(subject="alice")}
