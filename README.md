# envlens

[![CI](https://github.com/n5za/envlens/actions/workflows/ci.yml/badge.svg)](https://github.com/n5za/envlens/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/github/license/n5za/envlens)](LICENSE)

**Find the env var that is missing before your deploy does.**

`envlens` compares your real environment against `.env.example` and reports three things:
a key the app needs that is not set, a key that is set to empty, and a key that is set but
nobody documented. One file, stdlib only, exit code you can wire into CI.

## Install

```bash
pipx install envlens
# or
pip install envlens
# or, no install at all
curl -O https://raw.githubusercontent.com/n5za/envlens/main/envlens.py
python envlens.py --help
```

## Use

```bash
envlens check --example .env.example --actual .env
# or multiple actuals:
envlens check --example .env.example --actual .env --actual .env.local
```

Real output, against the files in [`examples/`](examples):

```console
$ envlens check --example examples/.env.example --actual examples/.env
envlens examples/.env.example vs examples/.env
  WARN  optional     API_TOKEN                    not set (optional in example)
  WARN  undocumented DEBUG_TOKEN                  set here, not in example

0 error(s), 2 warning(s)
```

`--strict` turns every warning into a failure. `--format json` for machines:

```console
$ envlens check --example .env.example --actual .env --format json
{
  "command": "check",
  "ok": false,
  "errors": 1,
  "warnings": 1,
  "findings": [
    { "kind": "missing", "key": "DATABASE_URL", "detail": "required by example, absent here", "severity": "error" }
  ]
}
```

### diff — what changed between two environments

```console
$ envlens diff examples/.env.example examples/.env
envlens diff examples/.env.example -> examples/.env
  - API_TOKEN                    (empty)
  ~ LOG_LEVEL                    info -> debug
  + DEBUG_TOKEN                  loca****************ip
```

Values are masked when the key looks like a credential or the value looks like one.
`--show-values` reveals them — never pipe that into a build log.

### mask — before you paste an env file into an issue

```console
$ envlens mask .env
DATABASE_URL=postgres://localhost:5432/app
LOG_LEVEL=debug
DEBUG_TOKEN=loca****************ip
```

### docs — generate the variable table for your README

```console
$ envlens docs --example .env.example
| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `DATABASE_URL` | yes | `postgres://localhost:5432/app` | |
| `API_TOKEN` | no | — | |
| `LOG_LEVEL` | yes | `info` | |
| `PORT` | yes | `8080` | |
```

## In CI

```yaml
- name: env drift gate
  run: envlens check --example .env.example --actual .env --strict
```

Fails the job on a missing key, an empty required key, or an undocumented key.
Exit codes: `0` clean, `1` drift, `2` usage or parse error.

## What it handles

- `KEY=value`, `export KEY=value`, `#` comments, blank lines
- single quotes (literal), double quotes (`\n`, `\t`, `\"`), values spanning lines
- inline comments only when preceded by a space — `A=x#y` keeps `#y`
- `${VAR}` and `$VAR` interpolation from keys earlier in the same file, depth-capped
- duplicate keys reported with both line numbers, last one wins (dotenv convention)
- invalid key names and unterminated quotes reported with the file and line

## What it deliberately does not do

- No remote fetch. No account, no telemetry, no update check.
- No schema types. A `.env` is strings; types belong in your config loader.
- No secret scanning of committed history. Use `gitleaks` for that.
- No YAML, TOML, or JSON config parsing. Different problem.

## Development

```bash
git clone https://github.com/n5za/envlens
cd envlens
make check     # compileall + ruff + unittest
make demo      # runs against examples/
```

28 tests, no test dependency.

## Contributing

Start with a [`good first issue`](https://github.com/n5za/envlens/labels/good%20first%20issue).
[CONTRIBUTING.md](CONTRIBUTING.md) is short.

## Security

[SECURITY.md](SECURITY.md). Never paste a real `.env` into a public issue — `envlens mask` first.

## License

MIT.
