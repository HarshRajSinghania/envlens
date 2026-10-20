"""Tests for envlens. stdlib unittest only — `python -m unittest discover -s tests`."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import envlens  # noqa: E402


class ParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name: str, body: str) -> Path:
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_plain_and_export_and_comments(self) -> None:
        p = self.write("a.env", "# top\nA=1\nexport B=2\n\nC = 3  # trailing\n")
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("A"), "1")
        self.assertEqual(env.get("B"), "2")
        self.assertEqual(env.get("C"), "3")
        self.assertEqual(env.errors, [])

    def test_quoted_values_keep_hash(self) -> None:
        p = self.write("a.env", 'A="x # not a comment"\nB=\'y # also not\'\n')
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("A"), "x # not a comment")
        self.assertEqual(env.get("B"), "y # also not")

    def test_multiline_double_quoted(self) -> None:
        p = self.write("a.env", 'PEM="-----BEGIN-----\nabc\ndef\n-----END-----"\nNEXT=1\n')
        env = envlens.parse_dotenv(p)
        self.assertIn("abc\ndef", env.get("PEM"))
        self.assertEqual(env.get("NEXT"), "1")

    def test_single_quoted_is_literal(self) -> None:
        p = self.write("a.env", "A='a\\nb'\n")
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("A"), "a\\nb")

    def test_duplicate_key_reported_and_last_wins(self) -> None:
        p = self.write("a.env", "A=1\nA=2\n")
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("A"), "2")
        self.assertTrue(any("duplicate key" in e for e in env.errors))

    def test_interpolation(self) -> None:
        p = self.write("a.env", "HOST=db\nURL=postgres://${HOST}:5432/x\nBARE=$HOST\n")
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("URL"), "postgres://db:5432/x")
        self.assertEqual(env.get("BARE"), "db")

    def test_invalid_key_is_reported_not_raised(self) -> None:
        p = self.write("a.env", "1BAD=x\nGOOD=y\n")
        env = envlens.parse_dotenv(p)
        self.assertIn("GOOD", env.entries)
        self.assertTrue(any("invalid key" in e for e in env.errors))

    def test_unterminated_quote_reported(self) -> None:
        p = self.write("a.env", 'A="never closed\n')
        env = envlens.parse_dotenv(p)
        self.assertTrue(any("unterminated" in e for e in env.errors))

    def test_trailing_garbage_after_quote(self) -> None:
        p = self.write("a.env", 'A="x" junk\n')
        env = envlens.parse_dotenv(p)
        self.assertTrue(any("trailing content" in e for e in env.errors))

    def test_empty_value_is_kept(self) -> None:
        p = self.write("a.env", "EMPTY=\n")
        env = envlens.parse_dotenv(p)
        self.assertEqual(env.get("EMPTY"), "")


class CheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.ex = envlens.parse_dotenv(self.write("example", "A=1\nB=2\nOPT=\n"))
        self.act = envlens.parse_dotenv(self.write("actual", "A=1\nB=2\n"))

    def write(self, name: str, body: str) -> Path:
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        return p

    def kinds(self, findings):
        return [f.kind for f in findings]

    def test_clean_when_optional_absent(self) -> None:
        findings = envlens.check(self.ex, self.act, strict=False, allow_extra=False)
        self.assertEqual([f for f in findings if f.severity == "error"], [])

    def test_missing_required_is_error(self) -> None:
        act = envlens.parse_dotenv(self.write("a2", "A=1\n"))
        findings = envlens.check(self.ex, act, strict=False, allow_extra=False)
        errors = [f for f in findings if f.severity == "error"]
        self.assertEqual([f.key for f in errors], ["B"])

    def test_empty_required_is_error(self) -> None:
        act = envlens.parse_dotenv(self.write("a3", "A=1\nB=\n"))
        findings = envlens.check(self.ex, act, strict=False, allow_extra=False)
        self.assertIn("empty", self.kinds(findings))

    def test_undocumented_is_warning_until_strict(self) -> None:
        act = envlens.parse_dotenv(self.write("a4", "A=1\nB=2\nEXTRA=9\n"))
        soft = envlens.check(self.ex, act, strict=False, allow_extra=False)
        hard = envlens.check(self.ex, act, strict=True, allow_extra=False)
        self.assertIn("undocumented", self.kinds(soft))
        self.assertTrue(all(f.severity == "warning" for f in soft if f.kind == "undocumented"))
        self.assertTrue(any(f.kind == "undocumented" and f.severity == "error" for f in hard))

    def test_allow_extra_suppresses(self) -> None:
        act = envlens.parse_dotenv(self.write("a5", "A=1\nB=2\nEXTRA=9\n"))
        findings = envlens.check(self.ex, act, strict=False, allow_extra=True)
        self.assertNotIn("undocumented", self.kinds(findings))

    def test_optional_missing_is_warning_until_strict(self) -> None:
        findings = envlens.check(self.ex, self.act, strict=True, allow_extra=False)
        self.assertTrue(any(f.key == "OPT" and f.kind == "optional" and f.severity == "error" for f in findings))


class MaskTests(unittest.TestCase):
    def test_secret_key_masked(self) -> None:
        self.assertTrue(envlens.is_secret_key("DATABASE_PASSWORD"))
        self.assertTrue(envlens.is_secret_key("api_key"))
        self.assertFalse(envlens.is_secret_key("LOG_LEVEL"))

    def test_mask_keeps_shape_not_value(self) -> None:
        masked = envlens.mask_value("API_TOKEN", "supersecretvalue12345")
        self.assertNotIn("supersecret", masked)
        self.assertTrue(masked.startswith("supe"))
        self.assertTrue(masked.endswith("45"))

    def test_short_value_fully_masked(self) -> None:
        self.assertEqual(envlens.mask_value("X", "abc"), "***")


class DiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self.a = envlens.parse_dotenv(self._w(d, "a", "A=1\nB=2\nC=3\n"))
        self.b = envlens.parse_dotenv(self._w(d, "b", "A=1\nB=9\nD=4\n"))

    def _w(self, d: Path, n: str, body: str) -> Path:
        p = d / n
        p.write_text(body, encoding="utf-8")
        return p

    def test_states(self) -> None:
        rows = {r["key"]: r["state"] for r in envlens.diff_env(self.a, self.b)}
        self.assertEqual(rows, {"B": "changed", "C": "removed", "D": "added"})

    def test_masked_render_hides_secret(self) -> None:
        rendered = envlens.render_diff_text(envlens.diff_env(self.a, self.b), reveal=False)
        self.assertNotIn("B=9", rendered)
        self.assertIn("->", rendered)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.example = self.write("example.env", "HOST=x\nPORT=5432\nSECRET_KEY=abc\n")
        self.actual = self.write("actual.env", "HOST=x\nPORT=5432\nSECRET_KEY=abc\n")

    def write(self, name: str, body: str) -> Path:
        p = self.dir / name
        p.write_text(body, encoding="utf-8")
        return p

    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        import contextlib
        import io

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = envlens.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_check_clean_exit_0(self) -> None:
        code, out, _ = self.run_cli(["check", "--example", str(self.example), "--actual", str(self.actual)])
        self.assertEqual(code, 0)
        self.assertIn("no drift", out)

    def test_check_drift_exit_1(self) -> None:
        self.actual.write_text("HOST=x\n", encoding="utf-8")
        code, out, _ = self.run_cli(["check", "--example", str(self.example), "--actual", str(self.actual)])
        self.assertEqual(code, 1)
        self.assertIn("missing", out)

    def test_check_json_is_parseable(self) -> None:
        code, out, _ = self.run_cli(
            ["check", "--example", str(self.example), "--actual", str(self.actual), "--format", "json"]
        )
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["findings"], [])

    def test_missing_file_exit_2(self) -> None:
        code, _, err = self.run_cli(["check", "--example", str(self.example), "--actual", "/nope/.env"])
        self.assertEqual(code, 2)
        self.assertIn("file not found", err)

    def test_mask_hides_secret(self) -> None:
        code, out, _ = self.run_cli(["mask", str(self.actual)])
        self.assertEqual(code, 0)
        self.assertNotIn("SECRET_KEY=abc", out)
        self.assertIn("HOST=x", out)

    def test_docs_marks_required(self) -> None:
        code, out, _ = self.run_cli(["docs", "--example", str(self.example)])
        self.assertEqual(code, 0)
        self.assertIn("| `HOST` | yes |", out)

    def test_version(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            envlens.main(["--version"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
