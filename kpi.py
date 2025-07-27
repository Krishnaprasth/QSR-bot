import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order

def generate_report(df: pd.DataFrame, store: str, fy: str):
    net_sales_metric  = find_metric(df, r"net\s*sales")
    aggregator_metric = find_metric(df, r"aggregator")
    expense_patterns  = [r"rent", r"labor", r"CAM", r"utility", r"marketing", r"gst"]
    expenses          = [find_metric(df, p) for p in expense_patterns]

    d = df[(df.Store == store) & (df.FY == fy)]
    total_sales    = d[d.Metric == net_sales_metric].Amount.sum()
    total_expenses = d[d.Metric.isin(expenses + [aggregator_metric])].Amount.sum()
    contribution   = total_sales - total_expenses

    opening = infer_opening_date(df[df.Store == store], net_sales_metric)
    opening_str = opening.strftime("%b %Y") if opening else "Unknown"
    exec_summary = (
        f"{store} opened in {opening_str}. "
        f"In {fy}, net sales were ₹{total_sales:.1f} lakhs, "
        f"contribution margin ₹{contribution:.1f} lakhs."
    )

    fy_list = sorted(df.FY.unique())
    base_fy, comp_fy = (fy_list[-2], fy_list[-1]) if len(fy_list) >= 2 else (None, None)
    sssg_pct = None
    if base_fy and comp_fy:
        bs = df[(df.Store == store)&(df.FY == base_fy)&(df.Metric == net_sales_metric)].Amount.sum()
        cs = df[(df.Store == store)&(df.FY == comp_fy)&(df.Metric == net_sales_metric)].Amount.sum()
        if bs: sssg_pct = (cs - bs)/bs*100

    kpi_table = []
    for year in ([base_fy, comp_fy] if base_fy else [fy]):
        row = {"FY": year}
        row["SSSG (%)"] = round(sssg_pct,2) if year==comp_fy and sssg_pct is not None else None
        d2 = df[(df.Store==store)&(df.FY==year)]
        ns2 = d2[d2.Metric==net_sales_metric].Amount.sum()
        exp2= d2[d2.Metric.isin(expenses + [aggregator_metric])].Amount.sum()
        row["Contribution Margin (%)"] = round((ns2 - exp2)/ns2*100,2) if ns2 else None
        kpi_table.append(row)

    cost_ratio_table = []
    for m in expenses:
        pct = d[d.Metric==m].Amount.sum()/total_sales*100 if total_sales else 0
        cost_ratio_table.append({"Metric": m, "Pct of Sales": round(pct,2)})
    aggr_amt = d[d.Metric==aggregator_metric].Amount.sum()
    cost_ratio_table.append({
        "Metric": "Aggregator commission",
        "Pct of Sales": round(aggr_amt/total_sales*100,2) if total_sales else 0
    })

    sssg_detail = {
        "base_fy": base_fy, "compare_fy": comp_fy,
        "sssg_pct": round(sssg_pct,2) if sssg_pct is not None else None
    }

    series = (
        d[d.Metric==net_sales_metric]
        .groupby("Month")["Amount"]
        .sum()
        .reindex(month_order)
        .fillna(0)
    )
    trend = {"months": series.index.tolist(), "values": series.values.tolist()}

    return {
        "executive_summary": exec_summary,
        "kpi_table":         kpi_table,
        "cost_ratio_table":  cost_ratio_table,
        "sssg":              sssg_detail,
        "trend":             trend
    }

def generate_vintage_report(df: pd.DataFrame, fy: str):
    today = datetime.date.today()
    rows = []
    net_sales_metric  = find_metric(df, r"net\s*sales")
    aggregator_metric = find_metric(df, r"aggregator")
    expense_patterns  = [r"rent", r"labor", r"CAM", r"utility", r"marketing", r"gst"]
    expenses          = [find_metric(df, p) for p in expense_patterns]

    fy_list = sorted(df.FY.unique())
    base_fy, comp_fy = (fy_list[-2], fy_list[-1]) if len(fy_list)>=2 else (None, None)
    for segment in ["New","Emerging","Established"]:
        stores = []
        for s, grp in df.groupby("Store"):
            opening = infer_opening_date(grp, net_sales_metric)
            if not opening: continue
            age = months_between(opening, today)
            if (segment=="New" and age<=12) or (segment=="Emerging" and 13<=age<=24) or (segment=="Established" and age>=25):
                stores.append(s)
        d_seg = df[(df.Store.isin(stores)) & (df.FY==fy)]
        per_store = []
        for s in stores:
            d2 = d_seg[d_seg.Store==s]
            ns = d2[d2.Metric==net_sales_metric].Amount.sum()
            exp2 = d2[d2.Metric.isin(expenses + [aggregator_metric])].Amount.sum()
            cm = ns - exp2
            sssg = None
            if base_fy and comp_fy:
                bs = df[(df.Store==s)&(df.FY==base_fy)&(df.Metric==net_sales_metric)].Amount.sum()
                cs = df[(df.Store==s)&(df.FY==comp_fy)&(df.Metric==net_sales_metric)].Amount.sum()
                if bs: sssg = (cs-bs)/bs*100
            per_store.append((ns,cm,sssg))
        sales_arr   = np.array([x[0] for x in per_store])
        contrib_arr = np.array([x[1] for x in per_store])
        sssg_arr    = np.array([x[2] for x in per_store if x[2] is not None])
        total_sales     = sales_arr.sum()
        avg_monthly_rev = total_sales/(len(stores)*12) if stores else 0
        avg_contrib     = contrib_arr.mean() if contrib_arr.size else 0
        median_sssg     = np.median(sssg_arr) if sssg_arr.size else None
        rows.append({
            "Segment": segment,
            "Stores": len(stores),
            "Total Sales (Lakhs)": round(total_sales,2),
            "Avg Monthly Rev/Store (Lakhs)": round(avg_monthly_rev,2),
            "Avg Contribution/Store (Lakhs)": round(avg_contrib,2),
            "Median SSSG (%)": round(median_sssg,2) if median_sssg is not None else None
        })
    return rows

def split_online_offline(net_sales: float, gst_amount: float):
    offline_ex = gst_amount/1.05
    return {"offline_sales":round(offline_ex,2),"online_sales":round(net_sales-offline_ex,2),"gst_amount":round(gst_amount,2)}
