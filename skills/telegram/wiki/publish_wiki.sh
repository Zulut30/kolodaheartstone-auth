#!/usr/bin/env bash
# Publish wiki/ directory to GitHub Wiki repo.
# Prerequisite: the wiki must be initialized via the web UI once (create any page).
#
# Usage: bash wiki/publish_wiki.sh

set -euo pipefail

REPO_OWNER="${BOTFORGE_REPO_OWNER:-Zulut30}"
REPO_NAME="${BOTFORGE_REPO_NAME:-telegram-skills}"
WIKI_URL="${BOTFORGE_WIKI_URL:-https://github.com/${REPO_OWNER}/${REPO_NAME}.wiki.git}"

color() { printf "\033[%sm%s\033[0m" "$1" "$2"; }
say()   { printf "$(color 36 '[wiki]') %s\n" "$*"; }
die()   { printf "$(color 31 '[wiki] error:') %s\n" "$*" >&2; exit 1; }

ROOT_DIR="$(git rev-parse --show-toplevel)"
SRC_DIR="${ROOT_DIR}/wiki"
[[ -d "$SRC_DIR" ]] || die "wiki source dir not found: $SRC_DIR"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

say "cloning $WIKI_URL"
if ! git clone "$WIKI_URL" "$TMPDIR/wiki" 2>/dev/null; then
  cat <<EOF
Wiki repo doesn't exist yet. Initialize it first:

  1. Open https://github.com/${REPO_OWNER}/${REPO_NAME}/wiki
  2. Click "Create the first page"
  3. Save (any content)
  4. Re-run this script

EOF
  exit 1
fi

say "copying pages"
find "$TMPDIR/wiki" -maxdepth 1 -name '*.md' -delete
# copy every wiki page except maintenance files
for f in "$SRC_DIR"/*.md; do
  name="$(basename "$f")"
  [[ "$name" == "README.md" ]] && continue
  cp "$f" "$TMPDIR/wiki/"
done

cd "$TMPDIR/wiki"

if git diff --quiet && git diff --cached --quiet; then
  say "no changes to publish"
  exit 0
fi

git add -A
git commit -m "Sync wiki from main repo $(date +%Y-%m-%d)"
git push origin master 2>/dev/null || git push origin main

say "wiki published"
