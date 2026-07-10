#!/usr/bin/env bash
set -euo pipefail

CACHE_VERSION="${1:-$(git rev-parse --short HEAD)}"

while IFS= read -r -d '' file; do
  sed -i "s/__CACHE_VERSION__/${CACHE_VERSION}/g" "$file"
  echo "Applied cache busting to ${file}"
done < <(find site -type f \( -name '*.html' -o -name '*.css' -o -name '*.js' \) -print0)

echo "Cache busting version: ${CACHE_VERSION}"
