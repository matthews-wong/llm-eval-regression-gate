import tempfile
import unittest
from pathlib import Path

from evalgate.results import ResultsError, load_results


def load(text: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "r.jsonl"
        path.write_text(text, encoding="utf-8")
        return load_results(path)


class LoadResultsTest(unittest.TestCase):
    def test_score_defaults_from_passed(self):
        got = load('{"id":"a","passed":true}\n{"id":"b","passed":false}\n')
        self.assertEqual(got["a"].score, 1.0)
        self.assertEqual(got["b"].score, 0.0)

    def test_blank_lines_ignored(self):
        self.assertEqual(len(load('\n{"id":"a","passed":true}\n\n')), 1)

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ResultsError, "duplicate case id 'a'"):
            load('{"id":"a","passed":true}\n{"id":"a","passed":false}\n')

    def test_bad_json_names_line(self):
        with self.assertRaisesRegex(ResultsError, r":2: invalid JSON"):
            load('{"id":"a","passed":true}\nnot json\n')

    def test_missing_passed_rejected(self):
        with self.assertRaisesRegex(ResultsError, "needs boolean 'passed'"):
            load('{"id":"a"}\n')

    def test_boolean_score_rejected(self):
        with self.assertRaisesRegex(ResultsError, "non-numeric 'score'"):
            load('{"id":"a","passed":true,"score":true}\n')


if __name__ == "__main__":
    unittest.main()
