#!/usr/bin/env bash
# migrate-to-org.sh — move the repo to an organization and rewrite every owner reference.
#
# Use this instead of a second personal account. GitHub allows one personal account per
# person; a second personal account is a ToS violation, an organization is not.
#
# Usage:
#   ./scripts/migrate-to-org.sh NEW_ORG [OLD_OWNER] [REPO]
#
# Requires: gh authenticated as an owner/admin of NEW_ORG.
set -Eeuo pipefail

ORG="${1:?usage: migrate-to-org.sh <new-org> [old-owner] [repo]}"
OLD_OWNER="${2:-$(gh api user -q .login)}"
REPO="${3:-$(basename "$(git rev-parse --show-toplevel)")}"

command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated" >&2; exit 1; }

echo "moving $OLD_OWNER/$REPO -> $ORG/$REPO"

# 1. the destination must exist and you must be able to admin it
if ! gh api "orgs/$ORG" >/dev/null 2>&1; then
  cat >&2 <<EOF
organization $ORG does not exist.

create it first (web UI, one minute):
  https://github.com/organizations/plan
  name: $ORG  |  owner: $OLD_OWNER  |  plan: Free

then run this script again.
EOF
  exit 1
fi

role="$(gh api "orgs/$ORG/memberships/$OLD_OWNER" -q .role 2>/dev/null || echo none)"
if [[ "$role" != "admin" ]]; then
  echo "you are '$role' in $ORG — need admin to transfer a repo in" >&2
  exit 1
fi

# 2. transfer — this redirects old URLs and keeps stars, issues, releases
gh api -X POST "repos/$OLD_OWNER/$REPO/transfer" -f new_owner="$ORG" >/dev/null
echo "transfer requested; waiting for the API to settle"
for _ in $(seq 1 20); do
  gh repo view "$ORG/$REPO" >/dev/null 2>&1 && break
  sleep 3
done
gh repo view "$ORG/$REPO" >/dev/null 2>&1 || { echo "transfer did not land — check the org's pending invitations" >&2; exit 1; }

# 3. rewrite owner references in tracked files only
files="$(git ls-files | grep -E '\.(md|toml|yml|yaml|json|py|sh|cfg|txt)$' || true)"
if [[ -n "$files" ]]; then
  # shellcheck disable=SC2086
  sed -i.bak "s|$OLD_OWNER/$REPO|$ORG/$REPO|g; s|github.com/$OLD_OWNER|github.com/$ORG|g" $files
  find . -name '*.bak' -delete
fi

# 4. repoint the remote and push the rewrite
git remote set-url origin "https://github.com/$ORG/$REPO.git"
git add -A
git -c user.name="$(git config user.name || echo migrate)" \
    -c user.email="$(git config user.email || echo migrate@localhost)" \
    commit -qm "chore: move to $ORG/$REPO" || echo "nothing to commit"
git push -q origin HEAD:"$(git branch --show-current)"

# 5. project metadata that does not travel with the transfer
gh repo edit "$ORG/$REPO" \
  --description "Find missing, empty, and undocumented env vars before your deploy does" \
  --add-topic envlens,dotenv,environment-variables,cli,devops,ci,configuration,python,devtools,static-analysis
gh api "repos/$ORG/$REPO" -X PATCH -f has_discussions=true >/dev/null
gh api "repos/$ORG/$REPO" -X PATCH -f has_wiki=false >/dev/null

# 6. seed the funnel on the new home
if [[ -x ./scripts/labels.sh ]]; then ./scripts/labels.sh "$ORG/$REPO" >/dev/null; fi

# 7. two settings only the web UI can flip
cat <<EOF

done: https://github.com/$ORG/$REPO

two toggles left, both in Settings → Actions → General:
  [ ] Workflow permissions -> Read and write
  [ ] Allow GitHub Actions to create and approve pull requests   <- release-please needs this

then verify:
  ./scripts/check.sh $ORG/$REPO
EOF
