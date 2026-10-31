"""W3: a small statistics module for Tawseel's failure analysis. Implement every function below.

Read README.md for the definitions (resolved parcels, failure rate). Do not change names or signatures:
the hidden tests import them.
"""
import pandas as pd
import numpy as np
import scipy.stats
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.multitest import multipletests


def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval. (nan, nan) if n == 0. ValueError if successes < 0, successes > n,
    or confidence not strictly between 0 and 1. The lower bound is exactly 0.0 when successes == 0
    and the upper bound exactly 1.0 when successes == n."""
    if not (0 < confidence < 1):
        raise ValueError("Confidence must be strictly between 0 and 1.")
    if n == 0:
        return (float('nan'), float('nan'))
    if successes < 0 or successes > n:
        raise ValueError("successes must be between 0 and n.")
    
    alpha = 1.0 - confidence
    low, high = proportion_confint(successes, n, alpha=alpha, method="wilson")
    
    if successes == 0:
        low = 0.0
    if successes == n:
        high = 1.0
        
    return (float(low), float(high))


def summarise(values: pd.Series) -> dict:
    """Keys n (non-missing count), missing, mean, median, p10, p90, iqr (p75 - p25).
    Quantiles use pandas' default (linear) interpolation. With no non-missing values, n is 0
    and the five statistics are nan."""
    s = pd.Series(values)
    missing = int(s.isna().sum())
    non_missing = s.dropna()
    n = int(len(non_missing))
    
    if n == 0:
        return {
            "n": 0,
            "missing": missing,
            "mean": float('nan'),
            "median": float('nan'),
            "p10": float('nan'),
            "p90": float('nan'),
            "iqr": float('nan'),
        }
    
    mean_val = float(non_missing.mean())
    median_val = float(non_missing.median())
    p10_val = float(non_missing.quantile(0.10, interpolation='linear'))
    p90_val = float(non_missing.quantile(0.90, interpolation='linear'))
    q75 = non_missing.quantile(0.75, interpolation='linear')
    q25 = non_missing.quantile(0.25, interpolation='linear')
    iqr_val = float(q75 - q25)
    
    return {
        "n": n,
        "missing": missing,
        "mean": mean_val,
        "median": median_val,
        "p10": p10_val,
        "p90": p90_val,
        "iqr": iqr_val,
    }


def failure_table(df: pd.DataFrame, by: str | list[str], confidence: float = 0.95) -> pd.DataFrame:
    """Resolved parcels only. Index: the group key(s), sorted. Columns: n, failures (int64), rate,
    ci_low, ci_high (Wilson). Groups with no resolved parcels do not appear."""
    resolved = df[df["outcome"].isin(["delivered", "failed"])].copy()
    resolved["is_failed"] = (resolved["outcome"] == "failed").astype(int)
    
    # Pass 'by' directly to groupby so string 'by' results in a standard Index
    grouped = resolved.groupby(by)
    
    records = []
    keys = []
    for name, group in grouped:
        n = len(group)
        if n == 0:
            continue
        failures = int(group["is_failed"].sum())
        rate = float(failures / n)
        ci_low, ci_high = wilson_ci(failures, n, confidence=confidence)
        records.append({
            "n": n,
            "failures": np.int64(failures),
            "rate": rate,
            "ci_low": ci_low,
            "ci_high": ci_high
        })
        keys.append(name)
        
    cols = ["n", "failures", "rate", "ci_low", "ci_high"]
    if not records:
        if isinstance(by, str):
            idx = pd.Index([], name=by)
        else:
            idx = pd.MultiIndex.from_tuples([], names=by)
        res_df = pd.DataFrame(columns=cols, index=idx)
        res_df["failures"] = res_df["failures"].astype("int64")
        return res_df
        
    res_df = pd.DataFrame(records, index=keys)
    res_df["failures"] = res_df["failures"].astype("int64")
    res_df = res_df.sort_index()
    return res_df[cols]


def bootstrap_ci(values, statistic: str = "median", n_resamples: int = 2000,
                 confidence: float = 0.95, seed: int = 0) -> tuple[float, float]:
    """Percentile bootstrap of 'median' or 'mean'. Missing values dropped first; fewer than two values
    gives (nan, nan). Same inputs and seed, same answer, every time."""
    s = pd.Series(values).dropna().values
    if len(s) < 2:
        return (float('nan'), float('nan'))
        
    if statistic == "median":
        stat_func = np.median
    elif statistic == "mean":
        stat_func = np.mean
    else:
        raise ValueError("statistic must be 'median' or 'mean'")
        
    res = scipy.stats.bootstrap(
        (s,),
        stat_func,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method='percentile',
        random_state=seed
    )
    return (float(res.confidence_interval.low), float(res.confidence_interval.high))


def compare_groups(df: pd.DataFrame, group_col: str, a: str, b: str, stratum_col: str) -> dict:
    """Resolved parcels of groups a and b only. Returns
    crude_a, crude_b: failure rates; crude_diff = crude_a - crude_b;
    adjusted_diff: sum over strata of w_s * (rate_a_s - rate_b_s) / sum of w_s, where w_s is the number of
        resolved parcels (both groups) in stratum s, using only strata in which both groups have parcels;
    strata_used: those strata, sorted;
    reversal: True when crude_diff and adjusted_diff are both non-zero and have opposite signs."""
    resolved = df[df["outcome"].isin(["delivered", "failed"])].copy()
    resolved["is_failed"] = (resolved["outcome"] == "failed").astype(int)
    
    sub = resolved[resolved[group_col].isin([a, b])]
    
    group_a_parcels = sub[sub[group_col] == a]
    group_b_parcels = sub[sub[group_col] == b]
    
    crude_a = float(group_a_parcels["is_failed"].mean()) if len(group_a_parcels) > 0 else 0.0
    crude_b = float(group_b_parcels["is_failed"].mean()) if len(group_b_parcels) > 0 else 0.0
    crude_diff = float(crude_a - crude_b)
    
    strata_all = sub[stratum_col].unique()
    valid_strata = []
    
    numerator = 0.0
    denominator = 0.0
    
    for s in sorted(list(strata_all)):
        stratum_data = sub[sub[stratum_col] == s]
        a_in_s = stratum_data[stratum_data[group_col] == a]
        b_in_s = stratum_data[stratum_data[group_col] == b]
        
        if len(a_in_s) > 0 and len(b_in_s) > 0:
            valid_strata.append(s)
            w_s = len(stratum_data)
            rate_a_s = a_in_s["is_failed"].mean()
            rate_b_s = b_in_s["is_failed"].mean()
            numerator += w_s * (rate_a_s - rate_b_s)
            denominator += w_s
            
    if denominator > 0:
        adjusted_diff = float(numerator / denominator)
    else:
        adjusted_diff = 0.0
        
    reversal = bool((crude_diff * adjusted_diff < 0) and (crude_diff != 0.0) and (adjusted_diff != 0.0))
    
    return {
        "crude_a": float(crude_a),
        "crude_b": float(crude_b),
        "crude_diff": float(crude_diff),
        "adjusted_diff": float(adjusted_diff),
        "strata_used": list(valid_strata),
        "reversal": reversal
    }


def zones_that_fail_more(df: pd.DataFrame, alpha: float = 0.05, min_n: int = 30) -> pd.DataFrame:
    """One row per zone with at least min_n resolved parcels, index 'zone'.
    For each, a one-sided Fisher exact test (alternative='greater') of the 2x2 table
    [[zone failures, zone deliveries], [rest failures, rest deliveries]], where 'rest' is every other
    zone's resolved parcels, including zones below min_n. Benjamini-Hochberg across the tested zones.
    Columns, in order: n, failures, rate, rest_rate, p_value, p_adjusted, flagged.
    flagged = p_adjusted < alpha and rate > rest_rate. Sorted by p_value, then zone name."""
    resolved = df[df["outcome"].isin(["delivered", "failed"])].copy()
    resolved["is_failed"] = (resolved["outcome"] == "failed").astype(int)
    resolved["is_delivered"] = (resolved["outcome"] == "delivered").astype(int)
    
    zone_grouped = resolved.groupby("zone").agg(
        n=("is_failed", "count"),
        failures=("is_failed", "sum"),
        deliveries=("is_delivered", "sum")
    )
    
    total_failures = int(resolved["is_failed"].sum())
    total_deliveries = int(resolved["is_delivered"].sum())
    
    tested_zones = zone_grouped[zone_grouped["n"] >= min_n].index.tolist()
    
    results = []
    for zone in tested_zones:
        z_row = zone_grouped.loc[zone]
        z_n = int(z_row["n"])
        z_fail = int(z_row["failures"])
        z_del = int(z_row["deliveries"])
        z_rate = float(z_fail / z_n)
        
        rest_fail = total_failures - z_fail
        rest_del = total_deliveries - z_del
        rest_n = rest_fail + rest_del
        rest_rate = float(rest_fail / rest_n) if rest_n > 0 else 0.0
        
        _, p_val = scipy.stats.fisher_exact(
            [[z_fail, z_del], [rest_fail, rest_del]],
            alternative='greater'
        )
        
        results.append({
            "zone": zone,
            "n": z_n,
            "failures": np.int64(z_fail),
            "rate": z_rate,
            "rest_rate": rest_rate,
            "p_value": float(p_val),
            "zone_name_for_sort": str(zone)
        })
        
    cols = ["n", "failures", "rate", "rest_rate", "p_value", "p_adjusted", "flagged"]
    if not results:
        idx = pd.Index([], name="zone")
        res_df = pd.DataFrame(columns=cols, index=idx)
        res_df["failures"] = res_df["failures"].astype("int64")
        res_df["flagged"] = res_df["flagged"].astype(bool)
        return res_df
        
    res_df = pd.DataFrame(results)
    
    p_values = res_df["p_value"].values
    if len(p_values) > 0:
        _, p_adjusted, _, _ = multipletests(p_values, alpha=alpha, method='fdr_bh')
        res_df["p_adjusted"] = p_adjusted.astype(float)
    else:
        res_df["p_adjusted"] = []
        
    res_df["flagged"] = (res_df["p_adjusted"] < alpha) & (res_df["rate"] > res_df["rest_rate"])
    res_df["flagged"] = res_df["flagged"].astype(bool)
    res_df["failures"] = res_df["failures"].astype("int64")
    
    res_df = res_df.sort_values(by=["p_value", "zone_name_for_sort"])
    res_df = res_df.set_index("zone")
    res_df.index.name = "zone"
    
    return res_df[cols]