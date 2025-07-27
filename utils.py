import os
import re
import datetime
import pandas as pd
import streamlit as st

def load_data(path="data/sales_data.csv"):
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        uploaded = st.file_uploader("Upload cleaned QSR dataset (CSV)", type=["csv"])
        if not uploaded:
            st.info(f"Please commit your CSV to `{path}` or upload it here.")
            st.stop()
        df = pd.read_csv(uploaded)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df.dropna(subset=["Amount"])

def find_metric(df, pattern):
    for m in df["Metric"].unique():
        if re.search(pattern, m, re.IGNORECASE):
            return m
    raise ValueError(f"No metric matches /{pattern}/")

month_order = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"]
month_map   = {m: i+1 for i,m in enumerate(month_order)}

def infer_opening_date(store_df, net_sales_metric):
    dates = []
    for fy, grp in store_df.groupby("FY"):
        years = [int(x) for x in re.findall(r"\d{4}", fy)]
        if len(years) != 2:
            continue
        sy, ey = years
        for month, amt in grp[grp.Metric == net_sales_metric][["Month","Amount"]].values:
            mon = month_map.get(month)
            if amt > 0 and mon:
                year = sy if mon >= 4 else ey
                dates.append(datetime.date(year, mon, 1))
    return min(dates) if dates else None

def months_between(d1, d2):
    return (d2.year - d1.year)*12 + (d2.month - d1.month)
