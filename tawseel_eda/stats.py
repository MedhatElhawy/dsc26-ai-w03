"""W3: a small statistics module for Tawseel's failure analysis. Implement every function below.

Read README.md for the definitions (resolved parcels, failure rate). Do not change names or signatures:
the hidden tests import them.
"""
import pandas as pd


def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval. (nan, nan) if n == 0. ValueError if successes < 0, successes > n,
    or confidence not strictly between 0 and 1. The lower bound is exactly 0.0 when successes == 0
    and the upper bound exactly 1.0 when successes == n."""
    raise NotImplementedError


def summarise(values: pd.Series) -> dict:
    """Keys n (non-missing count), missing, mean, median, p10, p90, iqr (p75 - p25).
    Quantiles use pandas' default (linear) interpolation. With no non-missing values, n is 0
    and the five statistics are nan."""
    raise NotImplementedError


def failure_table(df: pd.DataFrame, by: str | list[str], confidence: float = 0.95) -> pd.DataFrame:
    """Resolved parcels only. Index: the group key(s), sorted. Columns: n, failures (int64), rate,
    ci_low, ci_high (Wilson). Groups with no resolved parcels do not appear."""
    raise NotImplementedError


def bootstrap_ci(values, statistic: str = "median", n_resamples: int = 2000,
                 confidence: float = 0.95, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap of 'median' or 'mean'. Missing values dropped first; fewer than two values
    gives (nan, nan). Same inputs and seed, same answer, every time."""
    raise NotImplementedError


def compare_groups(df: pd.DataFrame, group_col: str, a: str, b: str, stratum_col: str) -> dict:
    """Resolved parcels of groups a and b only. Returns
    crude_a, crude_b: failure rates; crude_diff = crude_a - crude_b;
    adjusted_diff: sum over strata of w_s * (rate_a_s - rate_b_s) / sum of w_s, where w_s is the number of
        resolved parcels (both groups) in stratum s, using only strata in which both groups have parcels;
    strata_used: those strata, sorted;
    reversal: True when crude_diff and adjusted_diff are both non-zero and have opposite signs."""
    raise NotImplementedError


def zones_that_fail_more(df: pd.DataFrame, alpha: float = 0.05, min_n: int = 30) -> pd.DataFrame:
    """One row per zone with at least min_n resolved parcels, index 'zone'.
    For each, a one-sided Fisher exact test (alternative='greater') of the 2x2 table
    [[zone failures, zone deliveries], [rest failures, rest deliveries]], where 'rest' is every other
    zone's resolved parcels, including zones below min_n. Benjamini-Hochberg across the tested zones.
    Columns, in order: n, failures, rate, rest_rate, p_value, p_adjusted, flagged.
    flagged = p_adjusted < alpha and rate > rest_rate. Sorted by p_value, then zone name."""
    raise NotImplementedError
