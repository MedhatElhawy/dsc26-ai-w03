import math

import pandas as pd
import pytest

from tawseel_eda.stats import (bootstrap_ci, compare_groups, failure_table, summarise,
                               wilson_ci, zones_that_fail_more)


def parcels(rows):
    """rows: (zone, courier_type, slot, outcome, count)"""
    out = []
    for zone, ctype, slot, outcome, count in rows:
        out += [{"zone": zone, "courier_type": ctype, "slot": slot, "outcome": outcome}] * count
    return pd.DataFrame(out)


def test_wilson_known_value():
    lo, hi = wilson_ci(20, 100)
    assert lo == pytest.approx(0.13337, abs=1e-5) and hi == pytest.approx(0.28883, abs=1e-5)


def test_wilson_zero_failures_is_not_zero_width():
    lo, hi = wilson_ci(0, 12)
    assert lo == 0 and hi > 0.2


def test_failure_table_ignores_unresolved_parcels():
    df = parcels([("Faisal", "regular", "morning", "failed", 3), ("Faisal", "regular", "morning", "delivered", 7),
                  ("Faisal", "regular", "morning", "in_transit", 5)])
    t = failure_table(df, "zone")
    assert t.loc["Faisal", "n"] == 10 and t.loc["Faisal", "rate"] == pytest.approx(0.3)


def test_simpson_reversal():
    df = parcels([
        ("Z", "pilot", "morning", "failed", 20), ("Z", "pilot", "morning", "delivered", 80),
        ("Z", "regular", "morning", "failed", 6), ("Z", "regular", "morning", "delivered", 19),
        ("Z", "pilot", "evening", "failed", 1), ("Z", "pilot", "evening", "delivered", 24),
        ("Z", "regular", "evening", "failed", 8), ("Z", "regular", "evening", "delivered", 92),
    ])
    r = compare_groups(df, "courier_type", "pilot", "regular", "slot")
    assert r["crude_diff"] > 0 and r["adjusted_diff"] < 0 and r["reversal"] is True


def test_bootstrap_is_repeatable():
    x = pd.Series(range(1, 101), dtype=float)
    assert bootstrap_ci(x, seed=3) == bootstrap_ci(x, seed=3)
    lo, hi = bootstrap_ci(x)
    assert lo < 50.5 < hi


def test_summarise_counts_missing():
    s = summarise(pd.Series([1.0, 2.0, None, 4.0]))
    assert s["n"] == 3 and s["missing"] == 1 and s["median"] == 2.0


def test_zone_report_columns(tmp_path):
    df = parcels([("A", "regular", "morning", "failed", 40), ("A", "regular", "morning", "delivered", 60),
                  ("B", "regular", "morning", "failed", 10), ("B", "regular", "morning", "delivered", 90),
                  ("C", "regular", "morning", "failed", 12), ("C", "regular", "morning", "delivered", 88)])
    t = zones_that_fail_more(df)
    assert list(t.columns) == ["n", "failures", "rate", "rest_rate", "p_value", "p_adjusted", "flagged"]
    assert t.index[0] == "A" and bool(t.loc["A", "flagged"]) and not t.loc["B", "flagged"]
