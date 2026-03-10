"""Example secret loading patterns for `authpaseto_secret_key`.

This module demonstrates secure key generation and retrieval options that can be
adapted to environment variables, Fernet-encrypted local files, and TPM-backed
unsealing.
"""

import base64
import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet

from fastapi_paseto import AuthPASETO


def generate_paseto_secret_key() -> str:
    """Generate a URL-safe base64 key for `authpaseto_secret_key`.

    Returns:
        Newly generated key encoded as UTF-8 text.
    """
    raw_key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(raw_key).decode("utf-8")


def load_secret_from_env() -> str:
    """Load `AUTHPASETO_SECRET_KEY` and fail fast if it is unset.

    Raises:
        RuntimeError: If the environment variable is missing.

    Returns:
        Secret key string suitable for `authpaseto_secret_key`.
    """
    secret = os.getenv("AUTHPASETO_SECRET_KEY")
    if secret:
        return secret
    msg = "AUTHPASETO_SECRET_KEY is not set"
    raise RuntimeError(msg)


def decrypt_secret_with_fernet(encrypted_path: Path, fernet_key: str) -> str:
    """Decrypt an encrypted secret blob with Fernet.

    Args:
        encrypted_path: Path to encrypted key bytes.
        fernet_key: Base64-encoded Fernet key from a secure source.

    Returns:
        Decrypted secret key text for `authpaseto_secret_key`.
    """
    encrypted_bytes = encrypted_path.read_bytes()
    decrypted_bytes = Fernet(fernet_key.encode("utf-8")).decrypt(encrypted_bytes)
    return decrypted_bytes.decode("utf-8")


def load_secret_from_tpm() -> str:
    """Placeholder showing where TPM unseal integration should happen.

    Replace this function with your `tpm2-pytss` policy session and unseal flow.

    Returns:
        Secret key text loaded from TPM-sealed storage.
    """
    msg = "Implement TPM unseal using tpm2-pytss for your platform"
    raise NotImplementedError(msg)


@AuthPASETO.load_config
def get_config() -> dict[str, str]:
    """Return runtime configuration for FastAPI PASETO.

    This example defaults to an environment variable for simplicity.
    """
    return {"authpaseto_secret_key": load_secret_from_env()}
