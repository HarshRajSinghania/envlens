# Contributing to envlens

## The 60-second version

1. Open an issue before non-trivial work. A PR that lands without one may be closed.
2. Fork, branch from `main`, keep the diff scoped to one thing.
3. `make check` must pass locally — format, lint, types, tests.
4. Conventional Commits only. `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
5. One maintainer approval merges. Squash merge, title becomes the changelog line.

## Setup

```bash
git clone https://github.com/your-handle/envlens.git
cd envlens
make install
make check
```

## Branches

```
main          protected, releases are tagged here
feat/<slug>   feature
fix/<slug>    bugfix
docs/<slug>   docs only
```

Rebase on `main` before asking for review. Merge commits in the branch are fine, we squash on the way in.

## Commits

```
<type>(<scope>): <imperative summary, lowercase, no period>

<why this change exists — not what the diff does>

Refs: #123
```

The body explains motivation. The diff already shows the mechanics.

## Tests

- Bugfix PRs include a test that fails on `main` and passes on the branch.
- New behaviour gets a test at the public boundary, not the private helper.
- Do not lower coverage. CI fails if the line gate drops.

## Code style

- Formatter and linter are authoritative. Do not hand-format around them.
- No new dependency without a sentence in the PR explaining why stdlib does not cover it.
- Public API changes need a `BREAKING CHANGE:` footer and a docs update in the same PR.

## Review

- Reviewers respond within 72h. If nobody has, ping `@your-handle` once — not three times.
- Address comments with a new commit, not a force-push mid-review. Squash at the end.
- A red CI is the author's problem until it is green.

## Issues

Good issues contain: what you ran, what you expected, what happened, version. Paste the command block, not a screenshot of it.

## Recognition

Every release note names its contributors. If your first PR merges, you get a `contributor` label and a line in [CHANGELOG.md](CHANGELOG.md).
