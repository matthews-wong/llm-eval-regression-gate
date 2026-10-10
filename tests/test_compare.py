import unittest

from evalgate.compare import compare
from evalgate.results import CaseResult, ResultsError


def run(**passed: bool) -> dict[str, CaseResult]:
    return {k: CaseResult(k, v, 1.0 if v else 0.0) for k, v in passed.items()}


class CompareTest(unittest.TestCase):
    def test_classifies_regressions_and_fixes(self):
        got = compare(run(a=True, b=False, c=True), run(a=False, b=True, c=True))
        self.assertEqual(got.regressed, ("a",))
        self.assertEqual(got.fixed, ("b",))

    def test_pass_rates(self):
        got = compare(run(a=True, b=True, c=False, d=False), run(a=True, b=False, c=False, d=False))
        self.assertEqual((got.baseline_pass_rate, got.candidate_pass_rate), (0.5, 0.25))
        self.assertAlmostEqual(got.delta_mean, -0.25)

    def test_identical_runs(self):
        got = compare(run(a=True, b=False), run(a=True, b=False))
        self.assertEqual((got.regressed, got.fixed, got.mcnemar_p), ((), (), 1.0))

    def test_mismatched_cases_name_the_ids(self):
        with self.assertRaisesRegex(ResultsError, "b, c"):
            compare(run(a=True, b=True), run(a=True, c=True))

    def test_empty_rejected(self):
        with self.assertRaisesRegex(ResultsError, "empty"):
            compare({}, {})


if __name__ == "__main__":
    unittest.main()
