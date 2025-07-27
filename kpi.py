import datetime
import numpy as np
import pandas as pd
from utils import infer_opening_date, months_between, store_vintage, month_order, expenses_list, net_sales_metric, aggregator_metric, df

def generate_report(store: str, fy: str):
    # Implementation omitted for brevity; see repository for full code
    pass

def generate_vintage_report(fy: str):
    today = datetime.date.today()
    rows = []
    for segment in ["New","Emerging","Established"]:
        stores = [s for s,v in store_vintage.items() if v==segment]
        # Compute KPIs...
        rows.append({"Segment": segment, "Stores": len(stores)})
    return rows

def split_online_offline(net_sales: float, gst_amount: float):
    offline_ex = gst_amount / 1.05
    return {
        "offline_sales": round(offline_ex,2),
        "online_sales":  round(net_sales - offline_ex,2),
        "gst_amount":    round(gst_amount,2)
    }
