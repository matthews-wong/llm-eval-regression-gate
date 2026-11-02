import unittest

from evalgate.flaky import find_flaky
from evalgate.results import CaseResult, ResultsError


def run(**passed: bool) -> dict[str, CaseResult]:
    return {k: CaseResult(k, v, 1.0 if v else 0.0) for k, v in passed.items()}


class FindFlakyTest(unittest.TestCase):
    def test_flipping_case_is_flaky(self):
        got = find_flaky([run(a=True, b=True), run(a=True, b=False), run(a=True, b=True)])
        self.assertEqual(got, ("b",))

    def test_consistent_failure_is_not_flaky(self):
        self.assertEqual(find_flaky([run(a=False), run(a=False)]), ())

    def test_single_run_rejected(self):
        with self.assertRaisesRegex(ResultsError, "at least 2 runs, got 1"):
            find_flaky([run(a=True)])

    def test_mismatched_cases_name_the_run_and_ids(self):
        with self.assertRaisesRegex(ResultsError, "run 2 .* b, c"):
            find_flaky([run(a=True, b=True), run(a=True, c=True)])


if __name__ == "__main__":
    unittest.main()
