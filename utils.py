import os
import re
import datetime
import pandas as pd

def load_data():
    """
    Looks for sales_data.csv in data/ or root, loads it,
    coerces Amount to numeric, drops NaNs.
    """
    for p in ("data/sales_data.csv", "sales_data.csv"):
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
    else:
        raise FileNotFoundError(
            "sales_data.csv not found; please add it to data/ or repo root"
        )
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df.dropna(subset=["Amount"])

def find_metric(df: pd.DataFrame, pattern: str) -> str:
    """
    Finds a Metric name matching the regex pattern (case‑insensitive).
    Falls back to substring match if no regex hits.
    """
    # try regex
    for m in df["Metric"].unique():
        if re.search(pattern, m, re.IGNORECASE):
            return m
    # fallback substring
    pat = pattern.replace("\\s*", "").lower()
    for m in df["Metric"].unique():
        if pat in m.lower():
            return m
    raise ValueError(
        f"No metric matches pattern '{pattern}'. Available: {sorted(df['Metric'].unique())}"
    )

month_order = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"]

def infer_opening_date(store_df: pd.DataFrame, net_sales_metric: str) -> datetime.date:
    """
    Given a store's slice of df, returns the first month (as date)
    where net_sales_metric > 0, inferring the opening.
    """
    dates = []
    for fy, grp in store_df.groupby("FY"):
        # parse FY string like "FY 2023-24"
        years = [int(x) for x in re.findall(r"\d{4}", fy)]
        if len(years) != 2:
            continue
        start_year, end_year = years
        for month, amt in grp[grp.Metric == net_sales_metric][["Month","Amount"]].values:
            if month in month_order and amt > 0:
                mon = month_order.index(month) + 1
                year = start_year if mon >= 4 else end_year
                dates.append(datetime.date(year, mon, 1))
    return min(dates) if dates else None

def months_between(d1: datetime.date, d2: datetime.date) -> int:
    """Full months between two dates."""
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)
