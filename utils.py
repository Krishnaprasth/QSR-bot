import pandas as pd
import datetime
import re

def load_data(path="data/sales_data.csv"):
    df = pd.read_csv(path)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df.dropna(subset=["Amount"])

df = load_data()
def find_metric(pattern):
    vals = df["Metric"].unique().tolist()
    for m in vals:
        if re.search(pattern, m, re.IGNORECASE):
            return m
    raise ValueError(f"No metric matching {pattern}")

net_sales_metric = find_metric(r"net\s*sales")
aggregator_metric = find_metric(r"aggregator")
expenses_list = [find_metric(pat) for pat in [r"rent", r"labor", r"CAM", r"utility", r"marketing", r"gst"]]

month_order = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"]
month_map = {m:i+1 for i,m in enumerate(month_order)}

def infer_opening_date(store_df):
    dates = []
    for fy, grp in store_df.groupby("FY"):
        years = [int(x) for x in re.findall(r"\d{4}", fy)]
        if len(years)==2:
            sy, ey = years
        else:
            continue
        for month, amt in grp[grp.Metric==net_sales_metric][["Month","Amount"]].values:
            mon = month_map.get(month)
            if amt > 0 and mon:
                year = sy if mon >= 4 else ey
                dates.append(datetime.date(year, mon, 1))
    return min(dates) if dates else None

def months_between(d1, d2):
    return (d2.year - d1.year)*12 + (d2.month - d1.month)

store_vintage = {}
today = datetime.date.today()
for store, grp in df.groupby("Store"):
    opening = infer_opening_date(grp)
    if opening:
        age = months_between(opening, today)
        if age <= 12:
            store_vintage[store] = "New"
        elif age <= 24:
            store_vintage[store] = "Emerging"
        else:
            store_vintage[store] = "Established"
    else:
        store_vintage[store] = "Unknown"
