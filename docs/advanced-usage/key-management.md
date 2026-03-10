# Key Management

This library is commonly used for header-based application authentication, which
means the configured key material becomes part of your application's root of
trust.

For `local` tokens, `authpaseto_secret_key` is the secret that protects both:

- confidentiality, because holders of the key can decrypt token contents
- authenticity, because holders of the key can mint valid tokens

For `public` tokens, the trust model splits:

- `authpaseto_private_key` is the signing secret and must be protected like any
  other production credential
- `authpaseto_public_key` is not secret, but it still must come from an
  authenticated source so validators do not accept a stale or attacker-swapped
  key

FastAPI PASETO currently accepts the `local` symmetric key as an in-memory
string returned by `AuthPASETO.load_config()`. It also supports
`authpaseto_private_key_file` and `authpaseto_public_key_file`, but file loading
should be treated as a fallback for constrained deployments, not the preferred
production design.

## Use `load_config()` as the retrieval boundary

The safest pattern is to fetch or unwrap the key material inside the
configuration callback and only then return it to the library:

```python
@AuthPASETO.load_config
def get_config():
    return {
        "authpaseto_secret_key": fetch_secret_from_secure_store(),
        "authpaseto_private_key": fetch_private_key_from_secure_store(),
        "authpaseto_public_key": fetch_public_key_from_secure_store(),
    }
```

That keeps the sensitive retrieval logic in one place and avoids teaching users
to bake secrets into source code, images, or repo-tracked files.

## Generate strong key material

### Local purpose secret keys

Use a CSPRNG and generate at least 32 random bytes. Avoid human-chosen strings,
shared team passwords, or values copied from examples.

Python:

```python
import base64
import secrets

raw_secret = secrets.token_bytes(32)
encoded_secret = base64.urlsafe_b64encode(raw_secret).decode("ascii")
```

OpenSSL:

```bash
openssl rand -base64 32
```

Store the exact value consistently. If your storage layer expects a text value,
store the encoded value and return the same string from `load_config()`.

### Public purpose key pairs

Generate asymmetric keys with mature tooling and keep the private key out of the
application repository.

Ed25519 PEM example:

```bash
openssl genpkey -algorithm ED25519 -out private_key.pem
openssl pkey -in private_key.pem -pubout -out public_key.pem
```

The private key is secret signing material. The public key can be distributed
more broadly, but validators should still retrieve it from an authenticated and
rotation-aware source.

## Why file loading is a fallback

`authpaseto_private_key_file` and `authpaseto_public_key_file` are useful when a
file mount is the only practical interface your platform provides, but they come
with tradeoffs:

- files are easy to copy into backups, container layers, shell histories, and
  support bundles
- permissions drift is common, especially on shared hosts and ephemeral
  instances
- rotation usually means replacing files on disk and coordinating reload timing
- local files do not provide audit trails, version history, or centralized
  access control by themselves

Use file loading only when it is the only viable integration point for the
environment, or as a short-lived bridge while you move to a stronger secret
distribution model. If you must use files, keep them outside the repository,
limit filesystem permissions, avoid baking them into images, and document the
rotation procedure.

## Storage and retrieval options

### TPM with `tpm2-pytss`

Best fit:

- single-host deployments
- protecting `authpaseto_secret_key` or `authpaseto_private_key`
- environments that can tolerate hardware coupling and operational complexity

Advantages:

- hardware-backed protection against simple filesystem theft
- supports sealing key material to platform state or policy
- keeps the highest-value secret or private key out of ordinary application
  storage

Disadvantages:

- host-bound design complicates autoscaling, migration, and disaster recovery
- PCR-bound policies can break after firmware, kernel, or boot-chain changes
- development, containers, and CI are harder because hardware is not always
  present

Example retrieval:

```python
from pathlib import Path

from tpm2_pytss import ESAPI


def load_sealed_secret() -> str:
    """Unseal a previously stored TPM object and return it as text."""

    sealed_blob = Path("/run/secrets/paseto-local.blob").read_bytes()
    with ESAPI() as esys:
        sealed_handle = esys.load_blob(sealed_blob)
        return bytes(esys.unseal(sealed_handle)).decode("utf-8")
```

The exact handle-loading and authorization steps depend on how the sealed TPM
object was provisioned in your environment.

The same pattern can return a PEM private key instead of a symmetric secret. A
common deployment model is: store the private key or local secret sealed by the
TPM, then publish the public key through a separate authenticated distribution
path.

### Fernet-wrapped local storage

Best fit:

- single-host or low-complexity deployments
- envelope-encrypting a local secret blob or PEM file before it is read by the
  app
- incremental hardening when a real secret manager is not yet available

Advantages:

- straightforward Python integration
- better than storing raw secrets or PEM files in plaintext
- usable for both `authpaseto_secret_key` and `authpaseto_private_key`

Disadvantages:

- the Fernet key becomes another secret that still needs strong protection
- if the Fernet key lives next to the ciphertext, security gains are minimal
- does not provide centralized audit, policy, or rotation by itself

Example retrieval:

```python
from pathlib import Path

from cryptography.fernet import Fernet


def decrypt_secret_blob() -> str:
    """Decrypt a local secret or PEM blob before passing it to the library."""

    fernet_key = Path("/run/secrets/paseto-fernet.key").read_bytes()
    encrypted_blob = Path("/run/secrets/paseto.enc").read_bytes()
    return Fernet(fernet_key).decrypt(encrypted_blob).decode("utf-8")
```

Use this only if the Fernet key itself comes from a stronger root of trust such
as a TPM, OS secret store, or centralized secret manager.

### OS secret stores or protected mounted secrets

Best fit:

- single-host deployments
- Kubernetes or platform secret injection
- moderate-complexity environments where a central secret service is not
  available

Advantages:

- usually simpler to operate than TPM or Vault
- works for `authpaseto_secret_key`, PEM private keys, and public-key
  distribution
- often integrates well with existing deployment tooling

Disadvantages:

- still vulnerable to host compromise or accidental process-level disclosure
- permissions and mount configuration matter a lot
- audit and rotation support depend on the underlying platform

Use this when the platform injects secrets at runtime, not when the values are
hardcoded into `.env` files committed to the repo.

### HashiCorp Vault

Best fit:

- multi-instance production deployments
- teams that need centralized access control, versioning, auditing, and planned
  rotation
- managing both local symmetric secrets and public/private key material

Advantages:

- strong centralized policy and audit model
- secret versioning and controlled rotation workflows
- clean separation between application code and long-lived key material

Disadvantages:

- another critical service to run, secure, and keep highly available
- application bootstrap and auth to Vault must be designed carefully
- operationally heavier than local-only approaches

Example retrieval:

```python
import os

import hvac


def read_from_vault() -> dict[str, str]:
    """Fetch the PASETO key material from Vault KV storage."""

    client = hvac.Client(url="https://vault.internal:8200")
    client.auth.approle.login(
        role_id=os.environ["VAULT_ROLE_ID"],
        secret_id=os.environ["VAULT_SECRET_ID"],
    )
    payload = client.secrets.kv.v2.read_secret_version(path="apps/fastapi-paseto")
    return payload["data"]["data"]
```

```python
@AuthPASETO.load_config
def get_config():
    keys = read_from_vault()
    return {
        "authpaseto_secret_key": keys["local_secret_key"],
        "authpaseto_private_key": keys["private_key_pem"],
        "authpaseto_public_key": keys["public_key_pem"],
    }
```

Vault is usually the best documented centralized choice in this space when you
need multiple services or instances to share and rotate keys.

### Keycloak

Best fit:

- deployments that already standardize heavily on Keycloak for identity flows
- cases where Keycloak participates in broader key-distribution decisions

Advantages:

- can align key management with an existing identity control plane
- may reduce the number of separate platforms a team must learn

Disadvantages:

- not a dedicated general-purpose secret manager
- less natural fit than Vault for arbitrary application secret storage and
  operational rotation workflows
- can encourage coupling application secrets to an identity platform that was
  not chosen for this job

Keycloak can be part of the architecture, especially for public-key
distribution, but it should usually not be the first recommendation for storing
the `local` secret or private signing key. Prefer Vault, TPM, or an established
platform secret store first.

### Environment variables

Best fit:

- local development
- production only when injected by a real secret-management layer

Advantages:

- easy to wire into `load_config()`
- no extra client library needed for the application

Disadvantages:

- values can leak through process inspection, crash dumps, debug tooling, and
  deployment misconfiguration
- rotation typically requires process restarts
- weak choice if the variables are manually copied into shell startup files or
  `.env` files

Use environment variables as a delivery mechanism, not as the root secret store.

## Recommended patterns by key type

### `authpaseto_secret_key`

- Prefer Vault, TPM, or a platform secret store.
- Use Fernet only as envelope encryption around a blob protected elsewhere.
- Avoid hand-written strings and repo-tracked `.env` files.

### `authpaseto_private_key`

- Treat it like any other signing private key.
- Prefer TPM, Vault, or a hardened platform secret store.
- Use `authpaseto_private_key_file` only when mounted files are the only viable
  integration point.

### `authpaseto_public_key`

- It does not require secrecy, but it still requires authenticated retrieval.
- Prefer Vault, service configuration, or another trusted distribution path when
  you need controlled rotation across many validators.
- `authpaseto_public_key_file` is acceptable more often than private-key file
  loading, but still weaker than a centralized authenticated distribution model.

## Example application

The following example shows a production-shaped `load_config()` callback with a
safe default path and optional retrieval backends:

```python
{!../examples/key_management.py!}
```

## Practical defaults

- For small local deployments: use a platform secret store or carefully injected
  environment variables, not hardcoded strings.
- For single-host hardened deployments: TPM for the local secret or private key
  is often the strongest option.
- For multi-instance production: Vault or an equivalent centralized secret store
  is usually the most practical recommendation.
- Use file loading only when the environment cannot provide a stronger retrieval
  interface.
