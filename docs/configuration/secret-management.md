# Secret Key Management

`authpaseto_secret_key` is the root of trust for all `local` tokens. If an attacker
reads this key, they can mint valid tokens and impersonate any subject in your
system until the key is rotated and previously issued tokens are invalidated.

This guide explains how to:

1. Generate a cryptographically strong key.
2. Store it in a secure system instead of source code.
3. Retrieve it safely at runtime.
4. Rotate it with minimal downtime.

## Why this matters

For `local` PASETO, your secret key is used for authenticated encryption.
Compromise impact is high:

- **Token forgery:** attackers can create valid access or refresh tokens.
- **Privilege escalation:** forged tokens can carry arbitrary claims.
- **Persistence:** compromise may remain active until keys rotate.

Treat this key like a database credential with admin scope, or better.

## Key generation requirements

Use at least **32 random bytes** from a cryptographically secure RNG. For
storage and transport, encode bytes as URL-safe base64.

```python
import base64
import secrets


def generate_paseto_secret_key() -> str:
    """Return a new URL-safe base64 key for `authpaseto_secret_key`."""
    raw_key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(raw_key).decode("utf-8")
```

Avoid:

- Hardcoded strings such as `"secret"`.
- Password-like values typed by humans.
- Reusing keys across environments.

Generate unique keys per environment (`dev`, `staging`, `prod`) and per tenant
when you need strict cryptographic isolation.

## Storage and retrieval options

### 1) Environment variable (baseline)

Store only the generated random key value in an environment variable such as
`AUTHPASETO_SECRET_KEY`.

**Advantages**

- Easy to adopt.
- Works with containers and most deployment systems.

**Disadvantages**

- Exposed to process-level introspection.
- Rotation usually needs restarts.
- Weak controls if your deployment platform lacks secret management.

### 2) Encrypted file + Fernet envelope encryption

Store an encrypted key blob on disk and decrypt it at startup with a separate
master key (for example from your orchestrator secret store).

**Advantages**

- At-rest encryption for file-based deployments.
- Easy local/offline operation.

**Disadvantages**

- You must still protect and rotate the Fernet master key.
- Adds envelope-encryption operational complexity.

### 3) TPM-backed unsealing (`tpm2-pytss`)

Seal the PASETO key to TPM state (PCR policy), then unseal only on trusted
hosts and expected boot conditions.

**Advantages**

- Hardware-backed protection.
- Strong resistance to key extraction from disk images.
- Can bind decryption to platform integrity.

**Disadvantages**

- Platform-specific provisioning and recovery workflows.
- Hardware lifecycle and replacement complexity.
- More operational overhead than software-only options.

### 4) HashiCorp Vault (transit/kv)

Keep key material in Vault and retrieve short-lived secrets at startup (or on a
refresh schedule). Prefer AppRole, Kubernetes auth, or cloud IAM auth.

**Advantages**

- Centralized access control and auditing.
- Strong policy model and dynamic credentials.
- Good rotation workflows.

**Disadvantages**

- Requires high-availability Vault operations.
- New dependency in your auth critical path.
- Misconfigured policies can still leak secrets.

### 5) Cloud secret managers (AWS/GCP/Azure)

Use managed secrets services (for example AWS Secrets Manager, GCP Secret
Manager, or Azure Key Vault) with workload identity.

**Advantages**

- Managed durability/HA and IAM integration.
- Native rotation tooling and audit logs.

**Disadvantages**

- Cloud lock-in.
- Latency/network dependency if fetched at request time.

### 6) Keycloak (identity provider integration)

Keycloak is useful for externalizing identity and token issuance, but it is not
a full secret-management system for generic application keys.

**Advantages**

- Centralized identity and access model.
- Useful when you already delegate authn/authz to Keycloak.

**Disadvantages**

- Not designed as a general-purpose secret vault.
- Limited secret lifecycle controls compared to Vault/KMS products.
- Usually better paired with a dedicated secret manager.

## Recommended loading pattern

- Retrieve the secret once during startup.
- Keep it in memory only (avoid writing plaintext to logs/files).
- Fail fast if retrieval fails.
- Cache with explicit refresh policy only if your backend supports safe rotation.

```python
import os

from fastapi_paseto import AuthPASETO


def load_secret_from_env() -> str:
    """Read a required PASETO secret from environment variables."""
    secret = os.getenv("AUTHPASETO_SECRET_KEY")
    if not secret:
        msg = "AUTHPASETO_SECRET_KEY is not set"
        raise RuntimeError(msg)
    return secret


@AuthPASETO.load_config
def get_config() -> dict[str, str]:
    """Provide secure runtime configuration to FastAPI PASETO."""
    return {"authpaseto_secret_key": load_secret_from_env()}
```

## Rotation strategy

Use staged rotation with overlap:

1. Generate a new key in your secret manager.
2. Deploy services that can validate old tokens while issuing with the new key
   (or use short token TTLs and coordinated cutover).
3. Wait for old access/refresh windows to expire.
4. Revoke and remove the previous key.

For high-security environments, automate periodic key rotation and include
incident-driven emergency rotation playbooks.
