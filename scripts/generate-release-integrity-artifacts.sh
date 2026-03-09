#!/usr/bin/env bash

set -euo pipefail

dist_dir="${1:-dist}"
metadata_path="${2:-$dist_dir/release-integrity.env}"
syft_cmd="${SYFT:-syft}"
python_cmd="${PYTHON:-python3}"

if [[ ! -d "$dist_dir" ]]; then
  printf 'Distribution directory not found: %s\n' "$dist_dir" >&2
  exit 1
fi

mapfile -t package_info < <("$python_cmd" - <<'PY'
from pathlib import Path
import tomllib

pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
distribution = pyproject["project"]["name"].replace("-", "_")
version = pyproject["project"]["version"]
print(distribution)
print(version)
PY
)

distribution_name="${package_info[0]}"
version="${package_info[1]}"

mapfile -t wheels < <(find "$dist_dir" -maxdepth 1 -type f -name "${distribution_name}-${version}-*.whl" | LC_ALL=C sort)
mapfile -t sdists < <(find "$dist_dir" -maxdepth 1 -type f -name "${distribution_name}-${version}.tar.gz" | LC_ALL=C sort)

if [[ ${#wheels[@]} -ne 1 ]]; then
  printf 'Expected exactly one wheel in %s, found %s\n' "$dist_dir" "${#wheels[@]}" >&2
  exit 1
fi

if [[ ${#sdists[@]} -ne 1 ]]; then
  printf 'Expected exactly one source distribution in %s, found %s\n' "$dist_dir" "${#sdists[@]}" >&2
  exit 1
fi

wheel="${wheels[0]}"
sdist="${sdists[0]}"
checksums_path="$dist_dir/SHA256SUMS"
wheel_sbom="$dist_dir/$(basename "$wheel").spdx.json"
sdist_sbom="$dist_dir/$(basename "$sdist").spdx.json"

(cd "$dist_dir" && sha256sum "$(basename "$wheel")" "$(basename "$sdist")") > "$checksums_path"
"$syft_cmd" "$wheel" -o "spdx-json=$wheel_sbom"
"$syft_cmd" "$sdist" -o "spdx-json=$sdist_sbom"

cat > "$metadata_path" <<EOF
wheel=$wheel
wheel_name=$(basename "$wheel")
wheel_sbom=$wheel_sbom
wheel_sbom_name=$(basename "$wheel_sbom")
sdist=$sdist
sdist_name=$(basename "$sdist")
sdist_sbom=$sdist_sbom
sdist_sbom_name=$(basename "$sdist_sbom")
checksums=$checksums_path
checksums_name=$(basename "$checksums_path")
EOF
