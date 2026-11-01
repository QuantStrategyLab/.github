#!/usr/bin/env bash
# Download a fixed release and verify against a checksum committed with this code.
set -euo pipefail
install_dir="${1:?Usage: install-gitleaks.sh INSTALL_DIR}"
version=8.30.1
case "$(uname -s)/$(uname -m)" in
  Linux/x86_64)
    platform=linux_x64
    checksum=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb ;;
  Darwin/x86_64)
    platform=darwin_x64
    checksum=dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709 ;;
  Darwin/arm64)
    platform=darwin_arm64
    checksum=b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5 ;;
  *) echo 'Unsupported runner; use Linux x64 or macOS x64/arm64' >&2; exit 2 ;;
esac
mkdir -p "$install_dir"
archive=$(mktemp "${TMPDIR:-/tmp}/publication-gitleaks.XXXXXX")
trap 'rm -f "$archive"' EXIT
curl --fail --silent --show-error --location --retry 2 \
  "https://github.com/gitleaks/gitleaks/releases/download/v$version/gitleaks_${version}_${platform}.tar.gz" \
  --output "$archive"
python3 - "$archive" "$checksum" <<'VERIFY'
import hashlib
import sys
from pathlib import Path

if hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest() != sys.argv[2]:
    sys.exit("Gitleaks archive checksum mismatch")
VERIFY
tar -xzf "$archive" -C "$install_dir" gitleaks
"$install_dir/gitleaks" version
