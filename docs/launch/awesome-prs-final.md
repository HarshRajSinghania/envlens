# Awesome-list PRs — ready to open

Five targets. Open one per day, not five in an hour. Each body is three sentences,
which is what maintainers actually read.

## 1. sindresorhus/awesome-nodejs — skip

Wrong stack. Do not submit Python tools to JS lists; it is the fastest way to get the
account flagged by a maintainer who talks to the others.

## 1. vinta/awesome-python

Section: **DevOps Tools** (alphabetical, `envlens` goes after `doitlive`).

Entry line, matching the list's style:

```markdown
- [envlens](https://github.com/n5za/envlens) - Detect missing, empty, and undocumented environment variables by comparing against `.env.example`.
```

PR title: `Add envlens to DevOps Tools`

PR body:

```
envlens compares a real environment against .env.example and exits non-zero on drift.

Stdlib only, Python 3.9+, MIT licensed, 28 tests, no network calls.

It belongs under DevOps Tools because the failure it catches is a deploy-time failure, not a library concern.
```

## 2. agarrharr/awesome-cli-apps

Section: **Utilities**.

```markdown
- [envlens](https://github.com/n5za/envlens) - Find missing or empty environment variables before a deploy.
```

PR title: `Add envlens to Utilities`

PR body:

```
envlens is a single-file CLI that reports env-file drift: missing keys, empty required keys, undocumented keys.

Zero dependencies, installs with pipx, exit codes designed for CI.

MIT licensed.
```

## 3. awesome-selfhosted/awesome-selfhosted

**Read their contributing rules first.** They require a specific entry format and
reject tools without a demo. `envlens` is a CLI, not a hosted service — it likely does
not belong. Skip unless a maintainer says otherwise.

## 3. k4m4/terminals-are-sexy

Section: **Tools**.

```markdown
- [envlens](https://github.com/n5za/envlens) - Report missing, empty, and undocumented env vars before deploy.
```

PR title: `Add envlens`

PR body:

```
envlens is a terminal tool that diffs `.env` against `.env.example` and fails the shell on drift.

Stdlib Python, no daemon, no account.

MIT licensed, actively maintained.
```

## 4. jaywcjlove/awesome-mac

Section: **Developer Tools** — only if you ship a Homebrew formula. Otherwise skip.

## 4. inputsh/awesome-linux

Section: **Tools**.

```markdown
- [envlens](https://github.com/n5za/envlens) - Detect environment variable drift before deployment.
```

PR title: `Add envlens to Tools`

PR body:

```
envlens compares an environment against its documented example and reports missing, empty, and undocumented keys.

Single file, no dependencies, works anywhere Python 3.9 runs.

MIT licensed.
```

## 5. practical-tutorials/project-based-learning

Not a fit — they want tutorials, not tools. Do not submit.

## 5. A Python newsletter instead

Higher hit rate than a list PR. In order of response quality:

| Target | How | Note |
| --- | --- | --- |
| Python Weekly | pythonweekly.com submit form | 2–3 week lead time |
| PyCoder's Weekly | news@pycoders.com | one-line pitch, link |
| Console.dev | console.dev/submit | dev tools only, they reply |
| TLDR Newsletter | tldr.tech/submit | needs a real launch |
| Bytes Weekly | bytes.dev | JS-focused, skip |

Pitch template:

```
Subject: envlens — env drift detector, one file, no deps

envlens compares a real environment against .env.example and exits non-zero when a
required key is missing, a key is empty, or a key is undocumented. Stdlib Python, MIT,
28 tests, zero network calls.

Repo: https://github.com/n5za/envlens
Demo, 40 seconds: `pipx install envlens && envlens check --example examples/.env.example --actual examples/.env`
```

## Rules that get the account flagged

- Submitting the same repo to 10 lists in one day
- Editing the alphabetical order of surrounding entries
- Description longer than the neighbours'
- No license in the repo
- Arguing after a close. Take the no, move on.
