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

## Example

Fixtures in `fixtures/` hold one baseline and two candidate runs over the same
20 hand-written cases (fixture data, not a real model's results):

```text
$ python3 -m evalgate fixtures/baseline.jsonl fixtures/candidate_regressed.jsonl --must-pass fixtures/must_pass.txt
cases:      20
pass rate:  0.850 -> 0.500
score delta: -0.350 (95% CI -0.550 to -0.150)
McNemar p:  0.0156
regressed:  case-02, case-05, case-07, case-10, case-12, case-16, case-18
fixed:      -
gate: FAIL - must-pass cases regressed: case-02
gate: FAIL - significant regression: 7 regressed vs 0 fixed (McNemar p=0.0156 < 0.05)
```

`candidate_stable.jsonl` swaps one case each way and passes (p=1.0).

## Design notes

- Runs must cover exactly the same case ids; a dropped case is an error, not
  a silent improvement.
- The gate only fails on a *significant* drop (default alpha 0.05, `--alpha`
  to change). The bootstrap interval is reported for context but does not
  decide the verdict, so the two signals cannot disagree in CI.
- The bootstrap is seeded (`--seed`) so a rerun gives the same answer.

## Tests

```bash
python3 -m unittest
```
