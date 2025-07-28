import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order

def generate_report(df: pd.DataFrame, store: str, fy: str):
    net = find_metric(df, r"net\s*sales")
    aggr = find_metric(df, r"aggregator")
    exps = [find_metric(df, p) for p in [r"rent",r"labor",r"CAM",r"utility",r"marketing",r"gst"]]

    d = df[(df.Store==store)&(df.FY==fy)]
    sales = d[d.Metric==net].Amount.sum()
    total_exp = d[d.Metric.isin(exps+[aggr])].Amount.sum()
    contrib = sales - total_exp

    opening = infer_opening_date(df[df.Store==store], net)
    opening_str = opening.strftime("%b %Y") if opening else "Unknown"
    summary = (
        f"{store} opened in {opening_str}. "
        f"In {fy}, net sales ₹{sales:.1f} L, contribution ₹{contrib:.1f} L."
    )

    fy_list = sorted(df.FY.unique())
    base_fy = comp_fy = None
    if len(fy_list) >= 2:
        base_fy, comp_fy = fy_list[-2], fy_list[-1]

    sssg = None
    if base_fy and comp_fy:
        bs = df[(df.Store==store)&(df.FY==base_fy)&(df.Metric==net)].Amount.sum()
        cs = df[(df.Store==store)&(df.FY==comp_fy)&(df.Metric==net)].Amount.sum()
        if bs:
            sssg = (cs - bs) / bs * 100

    kpi = []
    years = [base_fy, comp_fy] if base_fy else [fy]
    for yr in years:
        row = {"FY": yr}
        row["SSSG (%)"] = round(sssg,2) if yr==comp_fy and sssg is not None else None
        d2 = df[(df.Store==store)&(df.FY==yr)]
        ns2 = d2[d2.Metric==net].Amount.sum()
        exp2= d2[d2.Metric.isin(exps+[aggr])].Amount.sum()
        row["CM (%)"] = round((ns2-exp2)/ns2*100,2) if ns2 else None
        kpi.append(row)

    cost_ratios = []
    for m in exps:
        pct = d[d.Metric==m].Amount.sum()/sales*100 if sales else 0
        cost_ratios.append({"Metric": m, "Pct": round(pct,2)})
    ag_amt = d[d.Metric==aggr].Amount.sum()
    cost_ratios.append({"Metric":"Aggregator commission","Pct":round(ag_amt/sales*100,2) if sales else 0})

    series = (
        d[d.Metric==net]
        .groupby("Month")["Amount"].sum()
        .reindex(month_order)
        .fillna(0)
    )
    trend = {"months": series.index.tolist(), "values": series.values.tolist()}

    return {
        "executive_summary": summary,
        "kpi_table": kpi,
        "cost_ratio_table": cost_ratios,
        "sssg": {"base_fy": base_fy, "compare_fy": comp_fy, "sssg_pct": round(sssg,2) if sssg is not None else None},
        "trend": trend
    }

def generate_vintage_report(df: pd.DataFrame, fy: str):
    today = datetime.date.today()
    net = find_metric(df, r"net\s*sales")

    # bucket stores locally
    vintage = {}
    for s, grp in df.groupby("Store"):
        op = infer_opening_date(grp, net)
        if not op:
            vintage[s] = "Unknown"
        else:
            age = months_between(op, today)
            vintage[s] = "New" if age<=12 else "Emerging" if age<=24 else "Established"

    out = []
    for seg in ["New","Emerging","Established"]:
        stores = [s for s,v in vintage.items() if v==seg]
        dseg = df[(df.Store.isin(stores)) & (df.FY==fy)]
        sales_sum = dseg[dseg.Metric==net].Amount.sum()
        cm_vals = []
        exp_metrics = [find_metric(df, p) for p in [r"rent",r"labor",r"CAM",r"utility",r"marketing",r"gst"]]
        for s in stores:
            d2 = dseg[dseg.Store==s]
            s_sales = d2[d2.Metric==net].Amount.sum()
            s_exp   = d2[d2.Metric.isin(exp_metrics + [find_metric(df, r"aggregator")])].Amount.sum()
            cm_vals.append(s_sales - s_exp)
        # compute SSSG medians
        sssg_vals = []
        fy_list = sorted(df.FY.unique())
        if len(fy_list)>=2:
            prev, curr = fy_list[-2], fy_list[-1]
            for s in stores:
                bs = df[(df.Store==s)&(df.FY==prev)&(df.Metric==net)].Amount.sum()
                cs = df[(df.Store==s)&(df.FY==curr)&(df.Metric==net)].Amount.sum()
                if bs: sssg_vals.append((cs-bs)/bs*100)
        out.append({
            "Segment":seg,
            "Stores":len(stores),
            "Total Sales":round(sales_sum,2),
            "Avg Rev/Store/mo":round(sales_sum/(len(stores)*12),2) if stores else 0,
            "Avg CM/Store":round(np.mean(cm_vals),2) if cm_vals else 0,
            "Median SSSG (%)":round(np.median(sssg_vals),2) if sssg_vals else None
        })
    return out

def split_online_offline(net_sales: float, gst_amount: float):
    off = gst_amount/1.05
    return {"offline":round(off,2),"online":round(net_sales-off,2),"gst":round(gst_amount,2)}

def get_top_sales_by_month(df: pd.DataFrame, month: str, fy: str):
    net = find_metric(df, r"net\s*sales")
    filt = df[(df.Month==month)&(df.FY==fy)&(df.Metric==net)]
    grp = filt.groupby("Store")["Amount"].sum()
    return {"store": grp.idxmax() if not grp.empty else None,
            "amount": grp.max() if not grp.empty else None}

def get_revenue_breakup_by_cohort_by_fy(df: pd.DataFrame, cohorts: list):
    net = find_metric(df, r"net\s*sales")
    today = datetime.date.today()
    vintage = {}
    for s, grp in df.groupby("Store"):
        op = infer_opening_date(grp, net)
        vintage[s] = (
            "Unknown" if not op else
            "New" if months_between(op,today)<=12 else
            "Emerging" if months_between(op,today)<=24 else
            "Established"
        )
    fy_list = sorted(df.FY.unique())
    rows = []
    for fy in fy_list:
        row = {"FY": fy}
        for c in cohorts:
            stores = [s for s,v in vintage.items() if v==c]
            total = df[(df.FY==fy)&(df.Store.isin(stores))&(df.Metric==net)]["Amount"].sum()
            row[c] = round(total,2)
        rows.append(row)
    return rows

def get_overall_ssg_by_fy(df: pd.DataFrame, fy: str):
    net = find_metric(df, r"net\s*sales")
    fy_list = sorted(df.FY.unique())
    if fy not in fy_list or len(fy_list)<2:
        return {"sssg_pct": None}
    prev = fy_list[fy_list.index(fy)-1]
    base = df[(df.FY==prev)&(df.Metric==net)].groupby("Store")["Amount"].sum()
    curr = df[(df.FY==fy)&(df.Metric==net)].groupby("Store")["Amount"].sum()
    common = base.index.intersection(curr.index)
    if base.loc[common].sum()==0:
        return {"sssg_pct": None}
    pct = (curr.loc[common].sum() - base.loc[common].sum()) / base.loc[common].sum() * 100
    return {"sssg_pct": round(pct,2)}

# Generic primitives (run_aggregation, run_trend, etc.) can be added below...
