#!/usr/bin/env bash
# check.sh — pre-launch readiness gate. Read-only. Exits non-zero if anything is missing.
# Usage: ./scripts/check.sh [owner/repo]
set -Eeuo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)}"
[[ -n "$REPO" ]] || { echo "usage: check.sh owner/repo" >&2; exit 1; }

fail=0
pass() { printf '  ok    %s\n' "$1"; }
bad()  { printf '  MISS  %s\n' "$1"; fail=$((fail + 1)); }

echo "repo: $REPO"
data="$(gh api "repos/$REPO")"

jq_get() { printf '%s' "$data" | jq -r "$1"; }

[[ "$(jq_get '.description // ""')" != "" ]] && pass "description set" || bad "description empty"
[[ "$(jq_get '.license.spdx_id // ""')" != "NOASSERTION" && "$(jq_get '.license.spdx_id // ""')" != "null" ]] \
  && pass "license: $(jq_get '.license.spdx_id')" || bad "no license"
[[ "$(jq_get '.topics | length')" -ge 5 ]] && pass "topics: $(jq_get '.topics | length')" || bad "fewer than 5 topics"
[[ "$(jq_get '.has_issues')" == "true" ]] && pass "issues on" || bad "issues disabled"
[[ "$(jq_get '.has_discussions')" == "true" ]] && pass "discussions on" || bad "discussions disabled"
[[ "$(jq_get '.security_and_analysis.secret_scanning.status // "disabled"')" != "disabled" ]] \
  && pass "secret scanning" || bad "secret scanning off"

releases="$(gh api "repos/$REPO/releases" --jq 'length')"
[[ "$releases" -ge 1 ]] && pass "releases: $releases" || bad "no release tagged"

workflows="$(gh api "repos/$REPO/actions/workflows" --jq '[.workflows[].state] | map(select(.=="active")) | length')"
[[ "$workflows" -ge 1 ]] && pass "active workflows: $workflows" || bad "no active workflow"

runs="$(gh api "repos/$REPO/actions/runs?per_page=1" --jq '.workflow_runs[0].conclusion // "none"')"
[[ "$runs" == "success" ]] && pass "last run green" || bad "last run: $runs"

gfi="$(gh api "repos/$REPO/issues?labels=good%20first%20issue&state=open" --jq 'length')"
[[ "$gfi" -ge 3 ]] && pass "good first issues: $gfi" || bad "good first issues: $gfi (want 3+)"

contrib="$(gh api "repos/$REPO/contributors" --jq 'length')"
pass "contributors: $contrib"

# README heuristics, local only
if [[ -f README.md ]]; then
  head -40 README.md | grep -qE '^\s*(```|npm i|pip install|cargo install|go install|docker run)' \
    && pass "install path in first 40 lines" || bad "no install block near the top"
  grep -q '{{' README.md && bad "unresolved {{tokens}} in README" || pass "no unresolved tokens"
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "ready to launch"
else
  echo "$fail blocking item(s) — fix before posting anywhere"
  exit 1
fi
