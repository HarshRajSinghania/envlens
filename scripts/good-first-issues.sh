#!/usr/bin/env bash
# good-first-issues.sh — seed the contributor funnel.
# Usage: ./scripts/good-first-issues.sh [owner/repo]
#
# Every ticket names a file, a scope, and an acceptance line. A "good first issue"
# without a file pointer is a trap and gets abandoned.
set -Eeuo pipefail

REPO="${1:-}"
GH=(gh issue create --label "good first issue")
[[ -n "$REPO" ]] && GH+=(--repo "$REPO")

issue() {
  local title="$1" body="$2"
  "${GH[@]}" --title "$title" --body "$body"
}

issue "docs: add a 10-line minimal example to examples/" \
'**What** — `examples/minimal/` with the smallest input that produces output.
**Where** — new dir, linked from README under Examples.
**Done when** — `bash examples/minimal/run.sh` exits 0 and prints real output.
**Scope** — no core changes. Files touched: `examples/minimal/*`, one README line.'

issue "docs: add a troubleshooting section to README" \
'**What** — the 5 errors new users hit, with the fix for each.
**Where** — README, after "Use".
**Done when** — each entry has the exact message, the cause, and the fix.
**Scope** — README only. Pull the errors from closed issues labelled `needs-repro`.'

issue "test: cover the empty-input path" \
'**What** — a test asserting empty input exits non-zero with a specific message.
**Where** — the existing test file for the entry point.
**Done when** — test fails if the empty guard is removed.
**Scope** — one test, no refactor.'

issue "feat: add --version flag" \
'**What** — `--version` prints the package version and exits 0.
**Where** — argument parser.
**Done when** — covered by a test, documented in README Use block.
**Scope** — parser + test + one docs line.'

issue "feat: add --quiet flag" \
'**What** — `--quiet` suppresses progress output, keeps errors on stderr.
**Where** — logger setup.
**Done when** — covered by a test; `--json --quiet` produces only JSON on stdout.
**Scope** — flags + test + docs line.'

issue "ci: add a coverage gate" \
'**What** — CI fails when line coverage drops below the current number.
**Where** — `.github/workflows/ci.yml`.
**Done when** — a PR that deletes tests goes red.
**Scope** — workflow only.'

issue "docs: write a 300-word tutorial for env drift in CI" \
'**What** — `docs/tutorial.md`, problem → install → run → result.
**Where** — new file, linked from README.
**Done when** — a reader with no context can follow it end to end.
**Scope** — docs only.'

issue "chore: add a pre-commit config" \
'**What** — format + lint on staged files.
**Where** — `.pre-commit-config.yaml`.
**Done when** — `pre-commit run --all-files` is clean on `main`.
**Scope** — config only, no source changes.'

echo "seeded 8 good-first-issues${REPO:+ on $REPO}"
