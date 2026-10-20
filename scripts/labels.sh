#!/usr/bin/env bash
# labels.sh — create the label set the templates reference.
# Usage: ./scripts/labels.sh [owner/repo]     (defaults to the cwd repo)
set -Eeuo pipefail

REPO="${1:-}"

label() {
  local name="$1" color="$2" desc="$3"
  if [[ -n "$REPO" ]]; then
    gh label create "$name" --color "$color" --description "$desc" --repo "$REPO" --force
  else
    gh label create "$name" --color "$color" --description "$desc" --force
  fi
}

label "bug"                "d73a4a"  "Something is broken"
label "enhancement"        "a2eeef"  "New capability"
label "documentation"      "0075ca"  "Docs only"
label "good first issue"   "7057ff"  "Scoped, guided, no prior context needed"
label "help wanted"        "008672"  "Maintainer is not going to get to this soon"
label "needs-triage"       "fbca04"  "Not yet assessed"
label "needs-repro"        "d4c5f9"  "Cannot reproduce as reported"
label "breaking"           "b60205"  "Breaks existing callers"
label "performance"        "c2e0c6"  "Slower than it should be"
label "security"           "ee0701"  "Private until patched"
label "stale"              "ededed"  "No activity"
label "pinned"             "0e8a16"  "Stays open"
label "blocked"            "000000"  "Waiting on something external"
label "contributor"        "f9d0c4"  "Has landed at least one PR"

echo "labels applied${REPO:+ to $REPO}"
