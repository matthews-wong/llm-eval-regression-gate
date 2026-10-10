import unittest

from evalgate.stats import mcnemar_exact, paired_bootstrap_ci


class McNemarTest(unittest.TestCase):
    def test_no_discordant_pairs_is_not_significant(self):
        self.assertEqual(mcnemar_exact(0, 0), 1.0)

    def test_balanced_is_not_significant(self):
        self.assertEqual(mcnemar_exact(3, 3), 1.0)

    def test_known_value(self):
        # 0 vs 5: 2 * (1 / 32)
        self.assertAlmostEqual(mcnemar_exact(5, 0), 0.0625)

    def test_symmetric(self):
        self.assertEqual(mcnemar_exact(7, 2), mcnemar_exact(2, 7))

    def test_negative_rejected(self):
        with self.assertRaisesRegex(ValueError, "-1"):
            mcnemar_exact(-1, 2)


class BootstrapTest(unittest.TestCase):
    def test_deterministic_for_seed(self):
        deltas = [0.0, -1.0, 0.0, 1.0, -1.0, 0.0]
        self.assertEqual(paired_bootstrap_ci(deltas, seed=3), paired_bootstrap_ci(deltas, seed=3))

    def test_constant_deltas_collapse_to_a_point(self):
        self.assertEqual(paired_bootstrap_ci([-1.0] * 8), (-1.0, -1.0))

    def test_interval_brackets_the_mean(self):
        deltas = [-1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0]
        low, high = paired_bootstrap_ci(deltas)
        self.assertLessEqual(low, sum(deltas) / len(deltas))
        self.assertGreaterEqual(high, sum(deltas) / len(deltas))

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            paired_bootstrap_ci([])


if __name__ == "__main__":
    unittest.main()
