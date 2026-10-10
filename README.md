# llm-eval-regression-gate

Compare two eval runs (a baseline and a candidate) and fail CI when the
candidate is meaningfully worse. Pure standard-library Python, no model calls.

A single pass-rate number hides what changed. This tool looks at the same
cases in both runs and reports:

- which cases regressed (pass -> fail) and which were fixed (fail -> pass)
- an exact McNemar test on the discordant pairs, so a 2-case swing on a
  20-case set is not reported as a real change
- a seeded paired-bootstrap confidence interval on the mean score delta
- a hard fail if any case you marked as must-pass regressed

## Input format

One JSON object per line:

```json
{"id": "refund-policy-01", "passed": true, "score": 1.0}
```

`score` is optional and defaults to `1.0` / `0.0` from `passed`.

## Usage

```bash
python3 -m evalgate baseline.jsonl candidate.jsonl --must-pass must_pass.txt
```

Exit code is `0` when the gate passes, `1` on a regression, `2` on bad input.

## Tests

```bash
python3 -m unittest
```
