#!/usr/bin/env python3
"""envlens — env-file drift detector. stdlib only, no daemon, no account.

Detects the three failures that break a deploy at 2am:
  1. a key the app needs that the environment does not set
  2. a key that exists but is empty
  3. a key the environment sets that nobody documented

Exit codes: 0 clean, 1 drift found, 2 usage or parse error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

__version__ = "0.1.0"

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2

# one place for every offset the parser and the reporter agree on
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")
REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_.\-]*)\}|\$([A-Za-z_][A-Za-z0-9_.\-]*)")
SECRET_KEY_RE = re.compile(
    r"(SECRET|TOKEN|PASSWD|PASSWORD|PASS|PWD|PRIVATE|CREDENTIAL|APIKEY|API_KEY|"
    r"SALT|SIGNING|CERT|AUTH|DSN|CONN|SESSION|COOKIE|WEBHOOK|ACCESS_KEY)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(r"^[A-Za-z0-9+/=_\-]{32,}$")


class ParseError(Exception):
    """Raised with file and line so the caller can report the offset."""

    def __init__(self, path: Path, line: int, message: str) -> None:
        super().__init__(f"{path}:{line}: {message}")
        self.path = path
        self.line = line
        self.message = message


@dataclass
class Entry:
    key: str
    value: str
    line: int
    duplicate_of: int | None = None


@dataclass
class EnvFile:
    path: Path
    entries: dict[str, Entry] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def keys(self) -> list[str]:
        return list(self.entries)

    def get(self, key: str, default: str = "") -> str:
        entry = self.entries.get(key)
        return entry.value if entry else default


# ---------------------------------------------------------------- parsing


def _read_value(lines: Sequence[str], idx: int, first: str, path: Path) -> tuple[str, int]:
    """Return (value, consumed_lines). Handles quotes spanning lines."""
    if not first or first[0] not in "\"'":
        # unquoted: an inline comment starts at " #" only
        cut = first.find(" #")
        if cut != -1:
            first = first[:cut]
        return first.rstrip(), 1

    quote = first[0]
    body = first[1:]
    consumed = 1
    while True:
        end = _find_close(body, quote)
        if end != -1:
            tail = body[end + 1 :].strip()
            if tail and not tail.startswith("#"):
                raise ParseError(path, idx + consumed, f"trailing content after closing quote: {tail!r}")
            return _unescape(body[:end], quote), consumed
        if idx + consumed >= len(lines):
            raise ParseError(path, idx + 1, "unterminated quoted value")
        body += "\n" + lines[idx + consumed]
        consumed += 1


def _find_close(body: str, quote: str) -> int:
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and quote == '"':
            i += 2
            continue
        if ch == quote:
            return i
        i += 1
    return -1


def _unescape(body: str, quote: str) -> str:
    if quote == "'":
        return body
    out: list[str] = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            out.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}.get(nxt, "\\" + nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _expand(value: str, entries: dict[str, Entry], depth: int = 0) -> str:
    if depth > 10 or "$" not in value:
        return value

    def sub(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(2)
        entry = entries.get(name)
        if entry is None:
            return match.group(0)
        return _expand(entry.value, entries, depth + 1)

    return REF_RE.sub(sub, value)


def parse_dotenv(path: Path) -> EnvFile:
    env = EnvFile(path=path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ParseError(path, 0, f"cannot read: {exc.strerror}") from exc

    lines = raw.splitlines()
    idx = 0
    while idx < len(lines):
        lineno = idx + 1
        line = lines[idx].strip()
        idx += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            env.errors.append(f"{path}:{lineno}: not a KEY=VALUE line: {line!r}")
            continue
        key, _, rest = line.partition("=")
        key = key.strip()
        if not KEY_RE.match(key):
            env.errors.append(f"{path}:{lineno}: invalid key {key!r}")
            continue
        try:
            value, consumed = _read_value(lines, idx - 1, rest.strip(), path)
        except ParseError as exc:
            env.errors.append(str(exc))
            continue
        idx += consumed - 1
        if key in env.entries:
            env.entries[key] = Entry(key, value, env.entries[key].line, duplicate_of=lineno)
            env.errors.append(f"{path}:{lineno}: duplicate key {key!r} (first at line {env.entries[key].line})")
            continue
        env.entries[key] = Entry(key, value, lineno)

    for entry in env.entries.values():
        entry.value = _expand(entry.value, env.entries)
    return env


# ---------------------------------------------------------------- reporting


def is_secret_key(key: str) -> bool:
    return bool(SECRET_KEY_RE.search(key))


def looks_secret(value: str) -> bool:
    return bool(SECRET_VALUE_RE.match(value)) and not value.startswith("http")


def mask_value(key: str, value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    keep = 4 if len(value) > 16 else 2
    return f"{value[:keep]}{'*' * min(len(value) - keep - 2, 24)}{value[-2:]}"


def mask_if_secret(key: str, value: str) -> str:
    """Only redact what is actually a credential — non-secret values stay readable."""
    if value and (is_secret_key(key) or looks_secret(value)):
        return mask_value(key, value)
    return value


@dataclass
class Finding:
    kind: str  # missing | empty | undocumented | duplicate | parse
    key: str
    detail: str
    severity: str  # error | warning

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "key": self.key, "detail": self.detail, "severity": self.severity}


def check(example: EnvFile, actual: EnvFile, strict: bool, allow_extra: bool) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for err in [*actual.errors, *example.errors]:
        if err in seen:
            continue
        seen.add(err)
        findings.append(Finding("parse", "-", err, "error"))

    for key, entry in example.entries.items():
        optional = entry.value == ""
        target = actual.entries.get(key)
        if target is None:
            if optional:
                findings.append(
                    Finding("optional", key, "not set (optional in example)", "warning" if not strict else "error")
                )
            else:
                findings.append(Finding("missing", key, "required by example, absent here", "error"))
        elif not target.value and not optional:
            findings.append(Finding("empty", key, "present but empty", "error"))

    if not allow_extra:
        for key in actual.entries:
            if key not in example.entries:
                findings.append(
                    Finding(
                        "undocumented",
                        key,
                        "set here, not in example",
                        "error" if strict else "warning",
                    )
                )
    return findings


def diff_env(a: EnvFile, b: EnvFile) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key in a.entries:
        if key not in b.entries:
            rows.append({"key": key, "state": "removed", "a": a.get(key), "b": ""})
        elif a.get(key) != b.get(key):
            rows.append({"key": key, "state": "changed", "a": a.get(key), "b": b.get(key)})
    for key in b.entries:
        if key not in a.entries:
            rows.append({"key": key, "state": "added", "a": "", "b": b.get(key)})
    return rows


# ---------------------------------------------------------------- renderers


def render_text(findings: Iterable[Finding]) -> str:
    out: list[str] = []
    for f in findings:
        tag = "ERROR" if f.severity == "error" else "WARN "
        out.append(f"  {tag} {f.kind:<12} {f.key:<28} {f.detail}")
    return "\n".join(out)


def render_md(findings: Iterable[Finding]) -> str:
    rows = ["| severity | kind | key | detail |", "| --- | --- | --- | --- |"]
    for f in findings:
        rows.append(f"| {f.severity} | {f.kind} | `{f.key}` | {f.detail} |")
    return "\n".join(rows)


def render_diff_text(rows: Sequence[dict[str, str]], reveal: bool) -> str:
    out: list[str] = []
    for row in rows:
        state = row["state"]
        if state == "changed":
            a = row["a"] if reveal else mask_if_secret(row["key"], row["a"])
            b = row["b"] if reveal else mask_if_secret(row["key"], row["b"])
            out.append(f"  ~ {row['key']:<28} {a or '(empty)'} -> {b or '(empty)'}")
        elif state == "added":
            b = row["b"] if reveal else mask_if_secret(row["key"], row["b"])
            out.append(f"  + {row['key']:<28} {b or '(empty)'}")
        else:
            a = row["a"] if reveal else mask_if_secret(row["key"], row["a"])
            out.append(f"  - {row['key']:<28} {a or '(empty)'}")
    return "\n".join(out)
    return "\n".join(out)


def render_env(env: EnvFile, reveal: bool) -> str:
    lines: list[str] = []
    for key, entry in env.entries.items():
        if not reveal and (is_secret_key(key) or looks_secret(entry.value)):
            lines.append(f"{key}={mask_value(key, entry.value)}")
        else:
            lines.append(f"{key}={entry.value}")
    return "\n".join(lines)


def render_docs(env: EnvFile) -> str:
    rows = ["| Variable | Required | Default | Notes |", "| --- | --- | --- | --- |"]
    for key, entry in env.entries.items():
        required = "no" if entry.value == "" else "yes"
        default = "—" if entry.value == "" else (mask_value(key, entry.value) if is_secret_key(key) else f"`{entry.value}`")
        rows.append(f"| `{key}` | {required} | {default} | |")
    return "\n".join(rows)


# ---------------------------------------------------------------- commands


def _load(path_str: str) -> EnvFile:
    path = Path(path_str)
    if not path.exists():
        raise ParseError(path, 0, "file not found")
    return parse_dotenv(path)


def cmd_check(args: argparse.Namespace) -> int:
    try:
        example = _load(args.example)
        actual = _load(args.actual)
    except ParseError as exc:
        print(f"envlens: {exc}", file=sys.stderr)
        return EXIT_USAGE

    findings = check(example, actual, strict=args.strict, allow_extra=args.allow_extra)
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    parse_failed = any(f.kind == "parse" for f in findings)

    if args.format == "json":
        payload = {
            "command": "check",
            "example": str(example.path),
            "actual": str(actual.path),
            "ok": errors == 0,
            "errors": errors,
            "warnings": warnings,
            "findings": [f.as_dict() for f in findings],
        }
        print(json.dumps(payload, indent=2))
    elif args.format == "md":
        print(render_md(findings) if findings else "| severity | kind | key | detail |\n| --- | --- | --- | --- |\n| ok | — | — | no drift |")
    else:
        print(f"envlens {example.path} vs {actual.path}")
        print(render_text(findings) if findings else "  ok           no drift")
        print(f"\n{errors} error(s), {warnings} warning(s)")

    # parse failure is not drift: a broken file must never read as a clean pass
    if parse_failed:
        return EXIT_USAGE
    return EXIT_DRIFT if errors else EXIT_OK


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        a = _load(args.a)
        b = _load(args.b)
    except ParseError as exc:
        print(f"envlens: {exc}", file=sys.stderr)
        return EXIT_USAGE

    rows = diff_env(a, b)
    if args.format == "json":
        payload = {
            "command": "diff",
            "a": str(a.path),
            "b": str(b.path),
            "changed": len(rows),
            "rows": [
                {
                    "key": r["key"],
                    "state": r["state"],
                    "a": r["a"] if args.show_values else mask_if_secret(r["key"], r["a"]),
                    "b": r["b"] if args.show_values else mask_if_secret(r["key"], r["b"]),
                }
                for r in rows
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"envlens diff {a.path} -> {b.path}")
        print(render_diff_text(rows, args.show_values) if rows else "  ok           identical")

    return EXIT_DRIFT if rows else EXIT_OK


def cmd_mask(args: argparse.Namespace) -> int:
    try:
        env = _load(args.file)
    except ParseError as exc:
        print(f"envlens: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(render_env(env, reveal=False))
    return EXIT_OK


def cmd_docs(args: argparse.Namespace) -> int:
    try:
        env = _load(args.example)
    except ParseError as exc:
        print(f"envlens: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(render_docs(env))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envlens",
        description="Detect env-file drift before it breaks a deploy.",
    )
    parser.add_argument("--version", action="version", version=f"envlens {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="compare an environment against the documented example")
    p_check.add_argument("--example", default=".env.example")
    p_check.add_argument("--actual", default=".env")
    p_check.add_argument("--strict", action="store_true", help="treat warnings as errors")
    p_check.add_argument("--allow-extra", action="store_true", help="ignore undocumented keys")
    p_check.add_argument("--format", choices=["text", "json", "md"], default="text")
    p_check.set_defaults(func=cmd_check)

    p_diff = sub.add_parser("diff", help="compare two env files, values masked by default")
    p_diff.add_argument("a")
    p_diff.add_argument("b")
    p_diff.add_argument("--show-values", action="store_true", help="print real values — do not pipe to a log")
    p_diff.add_argument("--format", choices=["text", "json"], default="text")
    p_diff.set_defaults(func=cmd_diff)

    p_mask = sub.add_parser("mask", help="print an env file with secrets redacted")
    p_mask.add_argument("file")
    p_mask.set_defaults(func=cmd_mask)

    p_docs = sub.add_parser("docs", help="emit a markdown variable table from an example file")
    p_docs.add_argument("--example", default=".env.example")
    p_docs.set_defaults(func=cmd_docs)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
