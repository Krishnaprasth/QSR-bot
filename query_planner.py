import pandas as pd
import re

def load_data(input_data):
    # 1) Read raw
    if isinstance(input_data, pd.DataFrame):
        df_raw = input_data.copy()
    else:
        df_raw = pd.read_csv(input_data)

    # 2) Parse hyphenated months like "2021-Apr" into datetime,
    #    then stringify back to the exact same format for consistency
    df_raw["Month"] = pd.to_datetime(
        df_raw["Month"], format="%Y-%b", errors="coerce"
    ).dt.strftime("%Y-%b")

    # 3) Pivot & derive KPIs
    df = (
        df_raw
        .pivot_table(index=["Month","Store"], columns="Metric", values="Amount")
        .reset_index()
    )
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
    v1 = sub[sub["Store"] == store1][metric].squeeze()
    v2 = sub[sub["Store"] == store2][metric].squeeze()
    return {store1: v1, store2: v2}

def rank_metric_for_period(df, metric, period, ascending=False):
    sub = df[df["Month"] == period]
    return sub.sort_values(metric, ascending=ascending)[["Store", metric]]

def handle_query(intent, slots, df):
    raw = slots.get("RAW_TEXT", "")
    # MAX
    if intent == "MAX_METRIC":
        store, val = max_metric_for_month(df, slots["METRIC"], slots["PERIOD"])
        return f"🏆 {store} had the highest {slots['METRIC']} in {slots['PERIOD']}: {val:.2f} lakhs"
    # TREND
    if intent == "TREND":
        ts = trend_for_store_metric(df, slots["STORE"], slots["METRIC"])
        return ts.to_string(index=False)
    # COMPARE
    if intent == "COMPARE":
        s1, s2 = [s.strip() for s in slots["STORE"].split(",")]
        res = compare_metric(df, slots["METRIC"], s1, s2, slots["PERIOD"])
        return res
    # RANK
    if intent == "RANK":
        asc = bool(re.search(r"\b(ascend|lowest)\b", raw.lower()))
        ranked = rank_metric_for_period(df, slots["METRIC"], slots["PERIOD"], ascending=asc)
        return ranked.to_markdown(index=False)
    # FALLBACK
    return "Sorry, I couldn't handle that query."
