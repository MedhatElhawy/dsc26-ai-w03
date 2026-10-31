"""Provided by DSC. Do not change: the grader overwrites this file."""
from pathlib import Path

import pandas as pd

OUTCOMES = ["delivered", "failed", "in_transit", "cancelled_before_dispatch"]
RESOLVED = ["delivered", "failed"]


def load_parcels(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"parcel_id": "string", "zone": "string", "courier_id": "string",
                                  "courier_type": "string", "slot": "string", "outcome": "string"})
    df["dispatched_at"] = pd.to_datetime(df["dispatched_at"], utc=True, format="ISO8601")
    return df
