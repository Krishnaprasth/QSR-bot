import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order

def generate_report(df, store: str, fy: str):
    # ... existing implementation ...
    pass

def generate_vintage_report(df, fy: str):
    # ... existing implementation ...
    pass

def split_online_offline(net_sales: float, gst_amount: float):
    offline = gst_amount / 1.05
    return {"offline_sales": round(offline, 2), "online_sales": round(net_sales - offline, 2)}

def get_top_sales_by_month(df, month: str, fy: str):
    net = find_metric(df, r"net\s*sales")
    filt = df[(df.Month == month) & (df.FY == fy) & (df.Metric == net)]
    grp = filt.groupby("Store")["Amount"].sum()
    store = grp.idxmax() if not grp.empty else None
    amount = grp.max() if not grp.empty else None
    return {"store": store, "amount": amount}

def get_revenue_breakup_by_cohort_by_fy(df, cohorts: list):
    net = find_metric(df, r"net\s*sales")
    fy_list = sorted(df.FY.unique())
    # Assume store_vintage available globally in utils
    from utils import store_vintage
    rows = []
    for fy in fy_list:
        row = {"FY": fy}
        for cohort in cohorts:
            stores = [s for s, v in store_vintage.items() if v == cohort]
            total = df[(df.FY == fy) & (df.Store.isin(stores)) & (df.Metric == net)]["Amount"].sum()
            row[cohort] = round(total, 2)
        rows.append(row)
    return rows