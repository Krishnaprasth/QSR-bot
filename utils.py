# utils.py
import os, re, datetime, pandas as pd

def load_data():
    for p in ("data/sales_data.csv", "sales_data.csv"):
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
    else:
        raise FileNotFoundError("sales_data.csv not found; add to data/ or root")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df.dropna(subset=["Amount"])

def find_metric(df, pattern):
    for m in df["Metric"].unique():
        if re.search(pattern, m, re.IGNORECASE):
            return m
    raise ValueError(f"No metric matches {pattern}")

month_order = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar"]

def infer_opening_date(store_df, net_sales_metric):
    dates = []
    for fy, grp in store_df.groupby("FY"):
        years = [int(x) for x in re.findall(r"\\d{4}", fy)]
        if len(years) != 2: continue
        sy, ey = years
        for month, amt in grp[grp.Metric==net_sales_metric][["Month","Amount"]].values:
            if month in month_order:
                mon = month_order.index(month) + 1
                if amt>0:
                    year = sy if mon>=4 else ey
                    dates.append(datetime.date(year, mon, 1))
    return min(dates) if dates else None

def months_between(d1, d2):
    return (d2.year - d1.year)*12 + (d2.month - d1.month)

# Precompute store_vintage
df = load_data()
store_vintage = {}
today = datetime.date.today()
net_metric = find_metric(df, r"net\\s*sales")
for store, grp in df.groupby("Store"):
    opening = infer_opening_date(grp, net_metric)
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
