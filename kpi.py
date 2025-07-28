import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order, store_vintage

def generate_report(df, store: str, fy: str):
    net_sales_metric  = find_metric(df, r"net\s*sales")  # Corrected regex
    aggregator_metric = find_metric(df, r"aggregator")
    expense_patterns  = [r"rent", r"labor", r"CAM", r"utility", r"marketing", r"gst"]
    expenses          = [find_metric(df, p) for p in expense_patterns]

    d = df[(df.Store == store) & (df.FY == fy)]
    total_sales    = d[d.Metric == net_sales_metric].Amount.sum()
    total_expenses = d[d.Metric.isin(expenses + [aggregator_metric])].Amount.sum()
    contribution   = total_sales - total_expenses

    opening = infer_opening_date(df[df.Store == store], net_sales_metric)
    opening_str = opening.strftime("%b %Y") if opening else "Unknown"
    exec_summary = (
        f"{store} opened in {opening_str}. "
        f"In {fy}, net sales were ₹{total_sales:.1f} lakhs, "
        f"contribution margin ₹{contribution:.1f} lakhs."
    )

    fy_list = sorted(df.FY.unique())
    if len(fy_list) >= 2:
        base_fy, comp_fy = fy_list[-2], fy_list[-1]
    else:
        base_fy = comp_fy = None
    sssg_pct = None
    if base_fy and comp_fy:
        bs = df[(df.Store==store)&(df.FY==base_fy)&(df.Metric==net_sales_metric)].Amount.sum()
        cs = df[(df.Store==store)&(df.FY==comp_fy)&(df.Metric==net_sales_metric)].Amount.sum()
        if bs:
            sssg_pct = (cs - bs) / bs * 100

    kpi_table = []
    for year in ([base_fy, comp_fy] if base_fy else [fy]):
        row = {"FY": year}
        row["SSSG (%)"] = round(sssg_pct, 2) if year == comp_fy and sssg_pct is not None else None
        d2 = df[(df.Store == store) & (df.FY == year)]
        ns2 = d2[d2.Metric == net_sales_metric].Amount.sum()
        exp2 = d2[d2.Metric.isin(expenses + [aggregator_metric])].Amount.sum()
        row["Contribution Margin (%)"] = round((ns2 - exp2) / ns2 * 100, 2) if ns2 else None
        kpi_table.append(row)

    cost_ratio_table = []
    for m in expenses:
        pct = d[d.Metric == m].Amount.sum() / total_sales * 100 if total_sales else 0
        cost_ratio_table.append({"Metric": m, "Pct of Sales": round(pct, 2)})
    aggr_amt = d[d.Metric == aggregator_metric].Amount.sum()
    cost_ratio_table.append({"Metric": "Aggregator commission", "Pct of Sales": round(aggr_amt / total_sales * 100, 2) if total_sales else 0})

    series = d[d.Metric == net_sales_metric].groupby("Month")["Amount"].sum().reindex(month_order).fillna(0)
    trend = {"months": series.index.tolist(), "values": series.values.tolist()}

    return {
        "executive_summary": exec_summary,
        "kpi_table": kpi_table,
        "cost_ratio_table": cost_ratio_table,
        "sssg": {"base_fy": base_fy, "compare_fy": comp_fy, "sssg_pct": round(sssg_pct, 2) if sssg_pct is not None else None},
        "trend": trend
}

# Other functions remain unchanged...
