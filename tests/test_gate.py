import unittest

from evalgate.compare import Comparison
from evalgate.gate import evaluate


def comparison(regressed=(), fixed=(), p=1.0) -> Comparison:
    return Comparison(10, tuple(regressed), tuple(fixed), 0.8, 0.7, p, -0.1, (-0.3, 0.1))


class EvaluateTest(unittest.TestCase):
    def test_clean_run_passes(self):
        self.assertTrue(evaluate(comparison()).passed)

    def test_insignificant_regression_passes(self):
        self.assertTrue(evaluate(comparison(["a", "b"], ["c"], p=0.6)).passed)

    def test_significant_regression_fails_with_counts(self):
        verdict = evaluate(comparison(["a", "b", "c", "d", "e", "f"], [], p=0.03))
        self.assertFalse(verdict.passed)
        self.assertIn("6 regressed vs 0 fixed", verdict.reasons[0])

    def test_significant_improvement_passes(self):
        self.assertTrue(evaluate(comparison([], ["a", "b", "c", "d", "e", "f"], p=0.03)).passed)

    def test_must_pass_regression_fails_even_when_insignificant(self):
        verdict = evaluate(comparison(["a"], [], p=1.0), must_pass=frozenset({"a"}))
        self.assertFalse(verdict.passed)
        self.assertIn("a", verdict.reasons[0])

    def test_must_pass_that_did_not_regress_is_fine(self):
        self.assertTrue(evaluate(comparison(["b"], [], p=1.0), must_pass=frozenset({"a"})).passed)


if __name__ == "__main__":
    unittest.main()
