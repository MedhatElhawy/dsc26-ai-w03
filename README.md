# W3 · Tawseel: which zones really fail more?

DSC Summer Internship 2026 · Data Science & Analytics track · Task after session W3 (EDA and statistical rigour)

**Repository name:** `dsc26-dsa-w03` (exactly this, public, in your own GitHub account)
**Language:** Python 3.12 · pandas 2.3.3 · SciPy 1.18.1 · statsmodels 0.15.0 · pytest 9.1.1 (pinned in `requirements.txt`)
**Expected time:** 2.5–3.5 hours

## Scenario

Sherif has a slide that says three zones "fail significantly more" and a pilot that "made failures worse". He wants the data pod to check both before Thursday's operations meeting. You build a small, reusable statistics module the squad will keep using: Wilson intervals, an honest failure table, a seeded bootstrap, a Simpson-aware comparison and a zone screen with a false-discovery correction. The hidden tests run it on other fortnights of synthetic Tawseel data.

## Set up

```bash
uv venv --python 3.12
source .venv/bin/activate            # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt   # the pinned versions; do not add packages
pytest -q                            # public tests: they fail until you build the task
```

## Files

```
tawseel_eda/
  io.py       load_parcels(path): string columns, dispatched_at as UTC. Provided by DSC. Do not change (the grader overwrites it).
  stats.py    YOU WRITE: wilson_ci, summarise, failure_table, bootstrap_ci, compare_groups, zones_that_fail_more
data/parcels_sample.csv   9,447 synthetic parcels over two weeks in 24 zones
tests/test_public.py      public tests
AI_USAGE.md               fill in before you submit
```

`data/parcels_sample.csv` has the columns `parcel_id, zone, courier_id, courier_type, slot, dispatched_at, cod_amount_egp, outcome, minutes_to_outcome`. It is generated from a seed and contains a Simpson reversal and some genuinely worse zones. Hidden fixtures come from other seeds. You may add helper modules inside `tawseel_eda/` and your own tests under `tests/`.

## Definitions your code must use

- A parcel is **resolved** if its `outcome` is `delivered` or `failed`. Only resolved parcels count, in every function. `in_transit` and `cancelled_before_dispatch` are excluded.
- **Failure rate** = failed / resolved.

The functions that take a `df` need only the columns they use (`outcome` plus the grouping columns). The hidden tests often pass small frames built by hand with just `zone, courier_type, slot, outcome`, with plain `object` columns, as the public tests do.

## What to build (`tawseel_eda/stats.py`)

```python
import pandas as pd

def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval. (nan, nan) if n == 0. ValueError if successes < 0, successes > n,
    or confidence not strictly between 0 and 1. The lower bound is exactly 0.0 when successes == 0
    and the upper bound exactly 1.0 when successes == n."""

def summarise(values: pd.Series) -> dict:
    """Keys n (non-missing count), missing, mean, median, p10, p90, iqr (p75 - p25).
    Quantiles use pandas' default (linear) interpolation. With no non-missing values, n is 0
    and the five statistics are nan."""

def failure_table(df: pd.DataFrame, by: str | list[str], confidence: float = 0.95) -> pd.DataFrame:
    """Resolved parcels only. Index: the group key(s), sorted. Columns: n, failures (int64), rate,
    ci_low, ci_high (Wilson). Groups with no resolved parcels do not appear."""

def bootstrap_ci(values, statistic: str = "median", n_resamples: int = 2000,
                 confidence: float = 0.95, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap of 'median' or 'mean'. Missing values dropped first; fewer than two values
    gives (nan, nan). Same inputs and seed, same answer, every time."""

def compare_groups(df: pd.DataFrame, group_col: str, a: str, b: str, stratum_col: str) -> dict:
    """Resolved parcels of groups a and b only. Returns
    crude_a, crude_b: failure rates; crude_diff = crude_a - crude_b;
    adjusted_diff: sum over strata of w_s * (rate_a_s - rate_b_s) / sum of w_s, where w_s is the number of
        resolved parcels (both groups) in stratum s, using only strata in which both groups have parcels;
    strata_used: those strata, sorted;
    reversal: True when crude_diff and adjusted_diff are both non-zero and have opposite signs."""

def zones_that_fail_more(df: pd.DataFrame, alpha: float = 0.05, min_n: int = 30) -> pd.DataFrame:
    """One row per zone with at least min_n resolved parcels, index 'zone'.
    For each, a one-sided Fisher exact test (alternative='greater') of the 2x2 table
    [[zone failures, zone deliveries], [rest failures, rest deliveries]], where 'rest' is every other
    zone's resolved parcels, including zones below min_n. Benjamini-Hochberg across the tested zones.
    Columns, in order: n, failures, rate, rest_rate, p_value, p_adjusted, flagged.
    flagged = p_adjusted < alpha and rate > rest_rate. Sorted by p_value, then zone name."""
```

You may use `scipy.stats` and `statsmodels` freely. You may also write any of these by hand; the tests check results, not imports.

Details the hidden tests rely on:

- `wilson_ci` is compared with statsmodels' `proportion_confint(k, n, alpha=1 - confidence, method="wilson")` to within 1e-9, at 90%, 95% and 99%. A confidence of `0`, `1` or `95` (a percentage) raises `ValueError`.
- `failure_table` columns are exactly `n, failures, rate, ci_low, ci_high`, in that order. With a list `by`, the index is a sorted `MultiIndex`.
- `bootstrap_ci` accepts a pandas Series, a NumPy array or a list. It is compared with `scipy.stats.bootstrap(..., method="percentile")` to within a fraction of a standard error, so any correct, seeded percentile bootstrap passes; it must honour `n_resamples` and `confidence`, and a different `seed` must give a different interval.
- `compare_groups` returns plain Python values: `reversal` is the Python `bool` `True` or `False` (the tests use `is True` / `is False`, so a NumPy `bool_` fails), and `strata_used` is a list sorted ascending.
- `zones_that_fail_more` has the index named `zone`; `flagged` is boolean.

## Public tests

`tests/test_public.py` has seven tests. Run them with `pytest -q` from the repository root. They fail on the starter and pass on a correct solution. Passing them is necessary, not sufficient.

## How grading works

1. Push to `dsc26-dsa-w03`, then press **Submit for grading** on DSC Hex. The grader pins your latest commit and clones it.
2. If `AI_USAGE.md` is missing or lacks any of its three headings, the grader stops and reports **0**.
3. DSC's copy of `tawseel_eda/io.py` replaces yours. Any `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg` or `[tool.pytest]` settings at the repository root are removed.
4. The hidden tests run with `pytest` on Python 3.12 with the pinned packages, network off, 60 s per test and 3 minutes for the whole run. They generate new fortnights of data from seeds that are not in the starter, and use Hypothesis for hundreds of random inputs.
5. You get a score from 0 to 100 and, per hidden test, its public name, pass or fail, and a short hint. A test ID passes only if every case under it passes. You never see the hidden test code.
6. You get 5 grader runs per day. Run the public tests locally first.

| ID | Public name | What it checks | Weight |
|---|---|---|---|
| H01 | wilson: matches the reference everywhere | 300 random (k, n) with n up to 5,000 at 90/95/99%, against statsmodels' Wilson to 1e-9; exact 0 and 1 at the ends | 10 |
| H02 | wilson: empty groups, bad input, wider at higher confidence | `n = 0` gives NaNs; `k < 0`, `k > n` and a confidence outside (0, 1) raise; the 99% interval contains the 90% one | 6 |
| H03 | summarise: quantiles, missing values, empty input | Known answers for p10, p90 and IQR with two missing values; an all-missing series | 6 |
| H04 | failure table: the denominator rule | Cancelled and in-transit parcels excluded, a group with only in-transit parcels absent, sorted index, a two-column `by` | 10 |
| H05 | failure table: intervals per row | Every row's interval equals Wilson on its own counts, at 90% | 6 |
| H06 | bootstrap: seeded, NaN-safe, defined on tiny input | Same seed same answer, different seed different answer, NaNs dropped, one value gives NaNs | 8 |
| H07 | bootstrap: close to a reference and narrower with more data | Within a tolerance of SciPy's percentile bootstrap for the median and the mean; eight times the data gives a narrower interval | 8 |
| H08 | simpson: the arithmetic, by hand | Known crude rates and adjusted difference; a stratum with only one group is left out; in-transit parcels ignored; no reversal when there is none | 10 |
| H09 | simpson: finds the reversal in new data | Two seeded fortnights; swapping a and b flips the sign of the adjusted difference | 8 |
| H10 | zones: the right test, the right rest-of-city, min_n | p-values equal the one-sided Fisher test on your own counts, with small zones inside "rest"; zones under `min_n` absent; sorted by p-value | 10 |
| H11 | zones: Benjamini-Hochberg and the flag rule | Adjusted p-values equal `fdr_bh`; `flagged` follows the rule at `alpha=0.10` | 8 |
| H12 | zones: flags the truly worse zones and nothing else | Three seeded fortnights in which an uncorrected 5% test flags an extra zone; exactly the planted zones must be flagged | 10 |
| | | **Total** | **100** |

Late policy: ×1.0 within 72 hours of the session starting, ×0.6 for the following 7 days, ×0.5 after that until Thu 3 Dec 23:59. W5 reopens W3 at ×1.0. Your best attempt counts.

## AI_USAGE.md

AI tools are allowed. Keep the three headings `## Tools`, `## What AI got wrong` and `## In my own words`. The grader does not score the content, but it reports 0 if the file or a heading is missing. Under `## In my own words`, answer in one or two sentences each, without AI:

1. In the sample, the pilot couriers have a higher overall failure rate but a lower one in each slot. Which number would you show Sherif, and what would you tell him about the pilot?
2. Why might a zone that really is worse not be flagged by your screen?
