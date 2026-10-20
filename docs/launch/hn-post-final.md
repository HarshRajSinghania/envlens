# HN post — final copy, paste-ready

Post Tuesday–Thursday, 06:00–08:00 US Eastern. Title first, body second, both below.

## Title

```
Show HN: Envlens – find the missing env var before your deploy does
```

## Body

```
Hi HN,

Every project I have worked on eventually deploys with an env var missing, and the
failure always shows up as a stack trace three layers away from the cause. So I wrote
the smallest thing that catches it: one Python file, no dependencies, no account.

    $ envlens check --example .env.example --actual .env
    envlens examples/.env.example vs examples/.env
      WARN  optional     API_TOKEN       not set (optional in example)
      WARN  undocumented DEBUG_TOKEN     set here, not in example

    0 error(s), 2 warning(s)

It reports three classes of drift:

- a required key from .env.example that is absent
- a key that is present but empty — the one that passes every "does the key exist" check
- a key that is set but undocumented, which is usually the one that breaks staging

Exit codes are 0 clean / 1 drift / 2 parse error, so `envlens check --strict` in CI is
the whole integration. Also ships `diff` between two env files with credential-looking
values masked, `mask` for pasting an env file into an issue, and `docs` which emits the
variable table for a README.

The parsing was the part I got wrong twice. Inline comments are only comments when
preceded by a space, so `A=x#y` keeps `#y`; double quotes unescape and can span lines
(people put PEM blocks in .env files more often than you would think); single quotes
are literal; `${VAR}` expands from keys earlier in the same file with a depth cap so a
cycle does not hang the process. Duplicate keys keep dotenv's last-wins behaviour but
report both line numbers.

What it deliberately does not do: types, YAML/TOML/JSON, secret scanning of git history
(gitleaks does that better), any network call.

28 tests, stdlib unittest, Python 3.9+.

Repo: https://github.com/your-handle/envlens

Things I am unsure about and would rather hear now:
- Should a key that is empty in .env.example be treated as optional or required? I
  picked optional, and `--strict` flips it. Not convinced.
- Is the undocumented-key warning useful, or is it the kind of thing people disable
  on day two?
```

## First comment, posted immediately by you

```
Author here. Two implementation notes that did not fit above:

1. The exit-code contract is the actual product. `2` is parse failure, not drift, so a
   broken .env file cannot be mistaken for a clean one in a pipeline.

2. Masking is key-name based plus a length/entropy heuristic on the value, so
   `DATABASE_URL` stays readable while `DEBUG_TOKEN` gets redacted. If you think the
   heuristic misses a class of value, that is a good issue.
```

## Reply templates

| Comment | Reply |
| --- | --- |
| "dotenv libraries already do this" | "They load. This compares two files and exits non-zero. Different verb." |
| "Use a schema / pydantic-settings" | "Agreed for typed config. This has to run before the schema exists — it catches the var that is not there yet." |
| "Why not just `diff`?" | "`diff` shows every line that changed. This classifies: missing, empty, undocumented, and masks credentials." |
| "Python startup is slow" | "~40ms on 3.12, measured, `time` output in the issue if you want it." |
| "Does it read .env from the environment too?" | "Only files, on purpose. Reading the process env makes CI results depend on the runner." |

## What to have ready before posting

- `envlens` on PyPI under a real version, `pipx install envlens` works from a clean box
- Repo description, 10 topics, social preview image
- 8 good-first-issues seeded
- Branch protection on `main`
- One person on standby for the first 3 hours to answer in parallel
