"""Analytics helpers kept independent from the UI for testability."""

from __future__ import annotations

import pandas as pd

ACTIVE_STATUSES = {"Applied", "Screening", "Interview", "Offer"}
RESPONSE_STATUSES = {"Screening", "Interview", "Offer", "Rejected"}


def summary_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    if df.empty:
        return {
            "total": 0, "active": 0, "interviews": 0, "offers": 0,
            "avg_match": 0.0, "response_rate": 0.0
        }

    statuses = df["status"].fillna("")
    applied_pool = statuses.isin(ACTIVE_STATUSES | {"Rejected", "Withdrawn"}).sum()
    responses = statuses.isin(RESPONSE_STATUSES).sum()
    match = pd.to_numeric(df.get("match_score"), errors="coerce")

    return {
        "total": int(len(df)),
        "active": int(statuses.isin(ACTIVE_STATUSES).sum()),
        "interviews": int((statuses == "Interview").sum()),
        "offers": int((statuses == "Offer").sum()),
        "avg_match": float(round(match.mean(), 1)) if match.notna().any() else 0.0,
        "response_rate": float(round((responses / applied_pool * 100), 1)) if applied_pool else 0.0,
    }


def status_counts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["status", "count"])
    return (
        df["status"].fillna("Unknown")
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )


def applications_over_time(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "applied_date" not in df:
        return pd.DataFrame(columns=["date", "applications"])
    dates = pd.to_datetime(df["applied_date"], errors="coerce")
    valid = dates.dropna()
    if valid.empty:
        return pd.DataFrame(columns=["date", "applications"])
    return (
        valid.dt.to_period("W").dt.start_time
        .value_counts()
        .sort_index()
        .rename_axis("date")
        .reset_index(name="applications")
    )


def source_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["source", "applications", "responses", "response_rate"])
    work = df.copy()
    work["source"] = work["source"].replace("", "Unknown").fillna("Unknown")
    work["responded"] = work["status"].isin(RESPONSE_STATUSES)
    grouped = work.groupby("source", as_index=False).agg(
        applications=("id", "count"), responses=("responded", "sum")
    )
    grouped["response_rate"] = (grouped["responses"] / grouped["applications"] * 100).round(1)
    return grouped.sort_values(["response_rate", "applications"], ascending=False)
