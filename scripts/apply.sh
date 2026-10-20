#!/usr/bin/env bash
# apply.sh — drop the launch rig into a project and fill its tokens.
#
# Usage:
#   ./scripts/apply.sh /path/to/project OWNER REPO NAME "One line tagline"
#
# Optional env:
#   KEYWORD=records DOMAIN=example.com LANG=python FORCE=1
set -Eeuo pipefail

TARGET="${1:?usage: apply.sh <target-dir> <owner> <repo> <name> <tagline>}"
OWNER="${2:?owner required}"
REPO="${3:?repo required}"
NAME="${4:?name required}"
TAGLINE="${5:?tagline required}"
KEYWORD="${KEYWORD:-the-task}"
DOMAIN="${DOMAIN:-example.com}"
LANG="${LANG:-nodejs}"
FORCE="${FORCE:-0}"

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -d "$TARGET" ]] || { echo "no such directory: $TARGET" >&2; exit 1; }
[[ -d "$TARGET/.git" ]] || echo "warning: $TARGET is not a git repo — files land anyway" >&2

escape() { printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'; }

files=(
  README.md
  CONTRIBUTING.md
  SECURITY.md
  CODE_OF_CONDUCT.md
  LICENSE
  CHANGELOG.md
  .gitignore
  release-please-config.json
  .release-please-manifest.json
  .github/workflows/ci.yml
  .github/workflows/release.yml
  .github/workflows/release-please.yml
  .github/workflows/stale.yml
  .github/workflows/greetings.yml
  .github/ISSUE_TEMPLATE/bug_report.yml
  .github/ISSUE_TEMPLATE/feature_request.yml
  .github/ISSUE_TEMPLATE/config.yml
  .github/PULL_REQUEST_TEMPLATE.md
  .github/dependabot.yml
  .github/FUNDING.yml
)

copied=0
skipped=0

for f in "${files[@]}"; do
  dest="$TARGET/$f"
  if [[ -e "$dest" && "$FORCE" != "1" ]]; then
    echo "skip (exists): $f"
    skipped=$((skipped + 1))
    continue
  fi
  mkdir -p "$(dirname "$dest")"
  sed -e "s/{{OWNER}}/$(escape "$OWNER")/g" \
      -e "s/{{REPO}}/$(escape "$REPO")/g" \
      -e "s/{{NAME}}/$(escape "$NAME")/g" \
      -e "s/{{TAGLINE}}/$(escape "$TAGLINE")/g" \
      -e "s/{{KEYWORD}}/$(escape "$KEYWORD")/g" \
      -e "s/{{DOMAIN}}/$(escape "$DOMAIN")/g" \
      -e "s/{{LANG}}/$(escape "$LANG")/g" \
      "$SRC/$f" > "$dest"
  copied=$((copied + 1))
done

# launch docs get the same substitution so nothing ships with a raw token
for f in "$SRC"/docs/launch/*.md; do
  [[ -e "$f" ]] || continue
  base="$(basename "$f")"
  dest="$TARGET/docs/launch/$base"
  if [[ -e "$dest" && "$FORCE" != "1" ]]; then
    echo "skip (exists): docs/launch/$base"
    continue
  fi
  mkdir -p "$TARGET/docs/launch"
  sed -e "s/{{OWNER}}/$(escape "$OWNER")/g" \
      -e "s/{{REPO}}/$(escape "$REPO")/g" \
      -e "s/{{NAME}}/$(escape "$NAME")/g" \
      -e "s/{{TAGLINE}}/$(escape "$TAGLINE")/g" \
      -e "s/{{KEYWORD}}/$(escape "$KEYWORD")/g" \
      -e "s/{{DOMAIN}}/$(escape "$DOMAIN")/g" \
      -e "s/{{LANG}}/$(escape "$LANG")/g" \
      "$f" > "$dest"
  copied=$((copied + 1))
done

cat <<EOF

installed: $copied   skipped: $skipped   target: $TARGET

next:
  cd $TARGET
  grep -rnE '\\{\\{(OWNER|REPO|NAME|TAGLINE|KEYWORD|DOMAIN|LANG)\\}\\}' . || echo '  no unresolved tokens'
  git add -A && git commit -m 'chore: repo scaffolding'
  git push origin main

then, once pushed:
  gh repo edit --description "$TAGLINE"
  gh repo edit --add-topic ${NAME},cli,opensource
  ./scripts/labels.sh $OWNER/$REPO
EOF
