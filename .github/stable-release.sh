#!/usr/bin/env bash
# Publish stable release on master from the current RC in pyproject.toml.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

read_version() {
  grep -E '^version\s*=' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/'
}

set_version() {
  local ver="$1"
  sed -i "s/^version = \".*\"/version = \"${ver}\"/" pyproject.toml
  sed -i "s/\"version\": \".*\"/\"version\": \"${ver}\"/" frontend/package.json
  sed -i "s/^\*\*Version [^*]*\*\*/**Version ${ver}**/" README.md
  sed -i "s/^\*\*Versión [^*]*\*\*/**Versión ${ver}**/" README_es.md
}

CURRENT="$(read_version)"
if [[ "$CURRENT" =~ ^([0-9]+\.[0-9]+\.[0-9]+)-rc\.[0-9]+$ ]]; then
  STABLE="${BASH_REMATCH[1]}"
elif [[ "$CURRENT" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Already stable version ${CURRENT}; nothing to do."
  exit 0
else
  echo "Unsupported version format: ${CURRENT}" >&2
  exit 1
fi

TAG="v${STABLE}"
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag ${TAG} already exists."
  exit 0
fi

echo "Promoting ${CURRENT} → ${STABLE}"
set_version "$STABLE"
git add pyproject.toml frontend/package.json README.md README_es.md
git commit -m "chore(release): ${STABLE}"
git push origin HEAD
git tag -a "$TAG" -m "Release ${STABLE}"
git push origin "$TAG"

NOTES_FILE="$(mktemp)"
{
  echo "## ${STABLE}"
  echo
  echo "Stable release paired with **adn-server ${STABLE}**."
  echo
  echo "See [CHANGELOG.md](CHANGELOG.md) for RC history through \`${CURRENT}\`."
} > "$NOTES_FILE"
gh release create "$TAG" --title "${STABLE}" --notes-file "$NOTES_FILE"
rm -f "$NOTES_FILE"

echo "Published ${STABLE}: https://github.com/${GITHUB_REPOSITORY}/releases/tag/${TAG}"
