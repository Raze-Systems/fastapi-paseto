# Supply Chain Security

FastAPI PASETO release artifacts are built in GitHub Actions and published as
GitHub Release assets. Each release includes:

- the wheel
- the source distribution
- `SHA256SUMS`
- one SPDX JSON SBOM for the wheel
- one SPDX JSON SBOM for the source distribution
- GitHub artifact attestations for build provenance
- GitHub artifact attestations for the SPDX SBOM predicates

The release job writes the same verification details into the workflow summary
and the GitHub Release description so consumers can verify what they downloaded
without reading the workflow source first.

## Verifying a release

Install the <a href="https://cli.github.com/" target="_blank">GitHub CLI</a>,
download the release asset you want to inspect, and run:

```bash
gh release verify vX.Y.Z --repo Raze-Systems/fastapi-paseto
gh release verify-asset vX.Y.Z ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto
gh attestation verify ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto --signer-workflow .github/workflows/release.yml
gh attestation verify ./fastapi_paseto-X.Y.Z-py3-none-any.whl --repo Raze-Systems/fastapi-paseto --signer-workflow .github/workflows/release.yml --predicate-type https://spdx.dev/Document/v2.3
```

Swap the wheel path for the source distribution if you prefer to verify the
sdist instead.

## Installing from the repository

Most supply-chain guarantees depend on immutable inputs. For Git installs, that
means you should install from a tag or a commit hash:

```bash
pip install "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@vX.Y.Z"
pip install "fastapi-paseto @ git+https://github.com/Raze-Systems/fastapi-paseto.git@<commit-sha>"
```

Avoid installs from `master`. A mutable branch reference can change after you
install it, which makes later verification weak even if the branch tip was
signed at the time.

Python installers record VCS origin metadata in `direct_url.json` as described
by PEP 610. That metadata helps downstream auditing tools understand where the
package came from, but it does not replace artifact verification. The strongest
path is:

1. Pin a tag or commit hash.
2. Verify that ref in GitHub.
3. Verify the matching release asset, provenance attestation, and SPDX SBOM.

## Trust model

This repository uses GitHub's keyless OIDC signing flow for attestations. The
trust decision is therefore based on:

- the repository identity
- the release workflow identity
- the artifact digest you downloaded

No long-lived signing key is required for release assets, which reduces manual
key management overhead for maintainers.
