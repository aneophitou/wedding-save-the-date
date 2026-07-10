#!/usr/bin/env bash
set -euo pipefail

CACHE_VERSION="${1:-$(git rev-parse --short HEAD)}"
TARGET="site/index.html"

if [[ ! -f "$TARGET" ]]; then
  echo "Missing $TARGET" >&2
  exit 1
fi

sed -i "s/__CACHE_VERSION__/${CACHE_VERSION}/g" "$TARGET"
echo "Applied cache busting version: ${CACHE_VERSION}"
