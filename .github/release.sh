#!/usr/bin/env bash
# Create a GitHub Release from conventional commits on develop.
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
}

last_tag() {
  git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || true
}

tag_exists() {
  git rev-parse "$1" >/dev/null 2>&1
}

is_releasable() {
  [[ "$1" =~ ^feat(\(.+\))?!: ]] && return 0
  [[ "$1" =~ ^feat(\(.+\))?: ]] && return 0
  [[ "$1" =~ ^fix(\(.+\))?!: ]] && return 0
  [[ "$1" =~ ^fix(\(.+\))?: ]] && return 0
  [[ "$1" =~ ^perf(\(.+\))?: ]] && return 0
  [[ "$1" =~ ^revert(\(.+\))?: ]] && return 0
  return 1
}

has_releasable_commits() {
  local range="$1"
  local log_cmd=(git log --pretty=format:%s)
  if [[ -n "$range" ]]; then
    log_cmd+=("$range")
  fi
  while IFS= read -r msg; do
    is_releasable "$msg" && return 0
  done < <("${log_cmd[@]}")
  return 1
}

commit_bump_type() {
  local range="$1"
  local breaking=false feat=false fix=false
  while IFS= read -r msg; do
    [[ "$msg" =~ ^feat(\(.+\))?!: ]] && breaking=true
    [[ "$msg" =~ ^fix(\(.+\))?!: ]] && breaking=true
    [[ "$msg" =~ ^feat(\(.+\))?: ]] && feat=true
    [[ "$msg" =~ ^fix(\(.+\))?: ]] && fix=true
    [[ "$msg" =~ ^perf(\(.+\))?: ]] && fix=true
    [[ "$msg" =~ ^revert(\(.+\))?: ]] && fix=true
  done < <(git log --pretty=format:%s "$range")
  if $breaking; then echo major
  elif $feat; then echo minor
  elif $fix; then echo patch
  else echo none
  fi
}

next_version() {
  local cur="$1" kind="$2"
  if [[ "$cur" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)-rc\.([0-9]+)$ ]]; then
    local major="${BASH_REMATCH[1]}" minor="${BASH_REMATCH[2]}" patch="${BASH_REMATCH[3]}" rc="${BASH_REMATCH[4]}"
    case "$kind" in
      major) echo "${major}.$((minor + 1)).0-rc.0" ;;
      minor) echo "${major}.$((minor + 1)).0-rc.0" ;;
      patch) echo "${major}.${minor}.${patch}-rc.$((rc + 1))" ;;
      *) echo "$cur" ;;
    esac
  elif [[ "$cur" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    local major="${BASH_REMATCH[1]}" minor="${BASH_REMATCH[2]}" patch="${BASH_REMATCH[3]}"
    case "$kind" in
      major) echo "$((major + 1)).0.0" ;;
      minor) echo "${major}.$((minor + 1)).0" ;;
      patch) echo "${major}.${minor}.$((patch + 1))" ;;
      *) echo "$cur" ;;
    esac
  else
    echo "Unsupported version format: $cur" >&2
    exit 1
  fi
}

prepend_changelog() {
  local ver="$1" prev_tag="$2" today="$3"
  local compare=""
  if [[ -n "$prev_tag" ]]; then
    compare="https://github.com/${GITHUB_REPOSITORY}/compare/${prev_tag}...v${ver}"
  fi

  local section_file tmp
  section_file="$(mktemp)"
  tmp="$(mktemp)"

  {
    if [[ -n "$compare" ]]; then
      echo "## [${ver}](${compare}) (${today})"
    else
      echo "## [${ver}] (${today})"
    fi
    echo
    local log_range=""
    if [[ -n "$prev_tag" ]]; then
      log_range="${prev_tag}..HEAD"
    fi
    local wrote=false
    while IFS='|' read -r msg sha; do
      if is_releasable "$msg"; then
        echo "* ${msg} (${sha})"
        wrote=true
      fi
    done < <(git log ${log_range:+$log_range} --pretty=format:'%s|%h')
    if ! $wrote; then
      echo "* Release ${ver}"
    fi
    echo
  } > "$section_file"

  head -n 3 CHANGELOG.md > "$tmp"
  echo >> "$tmp"
  cat "$section_file" >> "$tmp"
  tail -n +4 CHANGELOG.md >> "$tmp"
  mv "$tmp" CHANGELOG.md
  rm -f "$section_file"
}

sync_master() {
  git fetch origin master develop
  git push origin "HEAD:refs/heads/master"
  echo "master synced to $(git rev-parse --short HEAD)"
}

publish_release() {
  local ver="$1" tag="v${ver}"
  local prerelease_flag=()
  if [[ "$ver" == *"-rc"* ]]; then
    prerelease_flag=(--prerelease)
  fi

  if tag_exists "$tag"; then
    echo "Tag ${tag} already exists."
  else
    git tag -a "$tag" -m "Release ${ver}"
    git push origin "$tag"
    local notes_file
    notes_file="$(mktemp)"
    awk -v ver="$ver" '
      $0 ~ "^## \\[" ver "\\]" { found=1; print; next }
      found && /^## \[/ { exit }
      found { print }
    ' CHANGELOG.md > "$notes_file" || echo "Release ${ver}" > "$notes_file"
    gh release create "$tag" --title "$ver" "${prerelease_flag[@]}" --notes-file "$notes_file"
    rm -f "$notes_file"
    echo "Published GitHub Release ${ver}"
  fi
  sync_master
}

PREV_TAG="$(last_tag)"
CURRENT="$(read_version)"
TODAY="$(date -u +%Y-%m-%d)"

echo "Previous tag: ${PREV_TAG:-<none>}"
echo "Current pyproject version: ${CURRENT}"

if tag_exists "v${CURRENT}" && [[ "$(git rev-parse "v${CURRENT}")" == "$(git rev-parse HEAD)" ]]; then
  echo "HEAD already tagged v${CURRENT}."
  sync_master
  exit 0
fi

RANGE="${PREV_TAG:+$PREV_TAG..}HEAD"

if ! tag_exists "v${CURRENT}"; then
  if has_releasable_commits "$RANGE" || [[ "$(git log -1 --pretty=format:%s)" =~ ^chore\(develop\):|^chore\(release\): ]]; then
    echo "Publishing version ${CURRENT} at HEAD"
    if ! grep -qF "## [${CURRENT}]" CHANGELOG.md; then
      prepend_changelog "$CURRENT" "$PREV_TAG" "$TODAY"
      git add CHANGELOG.md
      git diff --staged --quiet || git commit -m "chore(release): changelog for ${CURRENT}"
      git push origin HEAD
    fi
    publish_release "$CURRENT"
    exit 0
  fi
fi

if ! has_releasable_commits "$RANGE"; then
  echo "No releasable commits since ${PREV_TAG:-start}."
  exit 0
fi

BUMP="$(commit_bump_type "$RANGE")"
[[ "$BUMP" == "none" ]] && { echo "No semver bump."; exit 0; }

BASE_VER="${PREV_TAG#v}"
[[ -z "$PREV_TAG" ]] && BASE_VER="$CURRENT"

NEW_VER="$(next_version "$BASE_VER" "$BUMP")"
echo "Bumping ${BASE_VER} → ${NEW_VER} (${BUMP})"

set_version "$NEW_VER"
prepend_changelog "$NEW_VER" "$PREV_TAG" "$TODAY"
git add pyproject.toml frontend/package.json CHANGELOG.md
git commit -m "chore(release): adn-monitor ${NEW_VER}"
git push origin HEAD

publish_release "$NEW_VER"
