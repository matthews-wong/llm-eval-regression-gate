import contextlib
import io
import unittest
from pathlib import Path

from evalgate.__main__ import EXIT_BAD_INPUT, EXIT_OK, EXIT_REGRESSION, main

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
BASELINE = str(FIXTURES / "baseline.jsonl")
MUST_PASS = str(FIXTURES / "must_pass.txt")


def run(*args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_stable_candidate_passes(self):
        code, out, _ = run(BASELINE, str(FIXTURES / "candidate_stable.jsonl"), "--must-pass", MUST_PASS)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("gate: PASS", out)

    def test_regressed_candidate_fails_with_both_reasons(self):
        code, out, _ = run(BASELINE, str(FIXTURES / "candidate_regressed.jsonl"), "--must-pass", MUST_PASS)
        self.assertEqual(code, EXIT_REGRESSION)
        self.assertIn("must-pass cases regressed: case-02", out)
        self.assertIn("significant regression", out)

    def test_missing_file_is_bad_input(self):
        code, _, err = run(BASELINE, str(FIXTURES / "absent.jsonl"))
        self.assertEqual(code, EXIT_BAD_INPUT)
        self.assertIn("absent.jsonl", err)

    def test_unknown_must_pass_id_is_bad_input(self):
        path = FIXTURES / "unknown_must_pass.tmp"
        path.write_text("case-99\n", encoding="utf-8")
        self.addCleanup(path.unlink)
        code, _, err = run(BASELINE, BASELINE, "--must-pass", str(path))
        self.assertEqual(code, EXIT_BAD_INPUT)
        self.assertIn("case-99", err)

    def test_same_run_passes(self):
        self.assertEqual(run(BASELINE, BASELINE)[0], EXIT_OK)


if __name__ == "__main__":
    unittest.main()
