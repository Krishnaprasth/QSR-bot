
import re
from logic_templates import *

def extract_store(query):
    return next((w for w in query.split() if w.isupper() and 3 <= len(w) <= 4), None)

def extract_fy(query):
    match = re.search(r"fy\d{2,4}", query.lower())
    return match.group().upper() if match else None

def extract_metric(query, df):
    q = query.lower()
    for m in df["Metric"].str.lower().unique():
        if m in q:
            return m
    return None

def route_query(query, df):
    q = query.lower()
    store = extract_store(q)
    fy = extract_fy(q)
    metric = extract_metric(q, df)

    if not metric:
        return None

    if "total" in q and store and fy:
        return total_metric_by_store_and_fy(df, metric, store, fy)
    if "average" in q and store:
        return average_metric_by_store(df, metric, store)
    if "ssg" in q or "same store sales" in q:
        if store and fy:
            fy_int = int(fy[-2:])
            fy_prev = f"FY{fy_int - 1}"
            return ssg_between_fys(df, metric, store, fy, fy_prev)
    if "trend" in q and store:
        return trend_by_month(df, metric, store)
    if "top" in q and "stores" in q and fy:
        return top_stores_by_metric_fy(df, metric, fy)
    if "lowest" in q and "store" in q and fy:
        return lowest_store_by_metric_fy(df, metric, fy)
    if "rent" in q and "%" in q and store and fy:
        return rent_as_percent_of_sales(df, store, fy)
    return None
