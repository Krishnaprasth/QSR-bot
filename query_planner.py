# query_planner.py

import pandas as pd

def load_data(input_data):
    """
    Accepts either:
      - a pandas.DataFrame (already read), or
      - a file‐like buffer / file‑path for CSV.
    Returns the pivoted DataFrame with derived KPIs.
    """
    if isinstance(input_data, pd.DataFrame):
        df_raw = input_data.copy()
    else:
        df_raw = pd.read_csv(input_data)

    # pivot metrics into columns
    df = (
        df_raw
        .pivot_table(index=["Month","Store"], columns="Metric", values="Amount")
        .reset_index()
    )

    # compute derived KPIs
    df["Gross Margin"] = df["Net Sales"] - df["COGS (food +packaging)"]
    df["Outlet EBITDA"] = (
        df["Gross Margin"]
        - df["store Labor Cost"]
        - df["Utility Cost"]
        - df["Rent"]
        - df["CAM"]
        - df["Aggregator commission"]
        - df["Marketing & advertisement"]
        - df["Other opex expenses"]
    )

    return df

def max_metric_for_month(df, metric, period):
    sub = df[df["Month"] == period]
    row = sub.loc[sub[metric].idxmax()]
    return row["Store"], row[metric]

def trend_for_store_metric(df, store, metric):
    ts = df[df["Store"] == store].sort_values("Month")[["Month", metric]]
    return ts

def compare_metric(df, metric, store1, store2, period):
    sub = df[df["Month"] == period]
    v1 = sub.loc[sub["Store"] == store1, metric].squeeze()
    v2 = sub.loc[sub["Store"] == store2, metric].squeeze()
    return {store1: v1, store2: v2}

def handle_query(intent, slots, df):
    if intent == "MAX_METRIC":
        store, val = max_metric_for_month(df, slots.get("METRIC"), slots.get("PERIOD"))
        return f"🏆 {store} had the highest {slots.get('METRIC')} in {slots.get('PERIOD')}: {val:.2f} lakhs"
    if intent == "TREND":
        ts = trend_for_store_metric(df, slots.get("STORE"), slots.get("METRIC"))
        return ts.to_string(index=False)
    if intent == "COMPARE":
        stores = [s.strip() for s in slots.get("STORE","").split("vs")]
        res = compare_metric(df, slots.get("METRIC"), stores[0], stores[1], slots.get("PERIOD"))
        return res
    return "Sorry, I couldn't understand or handle that query."
