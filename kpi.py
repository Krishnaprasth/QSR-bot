import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order

def generate_report(df, store: str, fy: str):
    net = find_metric(df, r"net\s*sales")
    aggr = find_metric(df, r"aggregator")
    exps = [find_metric(df, p) for p in [r"rent",r"labor",r"CAM",r"utility",r"marketing",r"gst"]]
    d = df[(df.Store==store)&(df.FY==fy)]
    sales = d[d.Metric==net].Amount.sum()
    total_exp = d[d.Metric.isin(exps+[aggr])].Amount.sum()
    contrib = sales - total_exp
    opening = infer_opening_date(df[df.Store==store], net)
    exec_summary = f"{store} opened in {opening.strftime('%b %Y') if opening else 'Unknown'}. In {fy}, net sales ₹{sales:.1f}L, contribution ₹{contrib:.1f}L."
    fy_list = sorted(df.FY.unique())
    bs, cs = None, None
    if len(fy_list)>=2:
        bs = df[(df.Store==store)&(df.FY==fy_list[-2])&(df.Metric==net)].Amount.sum()
        cs = df[(df.Store==store)&(df.FY==fy_list[-1])&(df.Metric==net)].Amount.sum()
    sssg = (cs-bs)/bs*100 if bs else None
    kpi = [{"FY":fy_list[-2],"SSSG (%)":round(sssg,2) if sssg else None},
           {"FY":fy_list[-1],"Contribution (%)":round((sales-total_exp)/sales*100,2) if sales else None}]
    cost_ratios = [{"Metric":m,"Pct":round(d[d.Metric==m].Amount.sum()/sales*100,2)} for m in exps+[aggr]]
    trend = d[d.Metric==net].groupby("Month")["Amount"].sum().reindex(month_order).fillna(0)
    return {"executive_summary":exec_summary,"kpi_table":kpi,"cost_ratio_table":cost_ratios,
            "sssg":{"value":round(sssg,2) if sssg else None},"trend":{"months":trend.index.tolist(),"values":trend.values.tolist()}}

def generate_vintage_report(df, fy: str):
    today = datetime.date.today()
    rows = []
    net = find_metric(df, r"net\s*sales")
    for seg, (lo,hi) in [("New",(0,12)),("Emerging",(13,24)),("Established",(25,999))]:
        stores = [s for s,grp in df.groupby("Store") if (lambda d=grp: (age:=(months_between(infer_opening_date(d,net),today)) and lo<=age<=hi)())]
        dseg = df[(df.Store.isin(stores))&(df.FY==fy)]
        sales = dseg[dseg.Metric==net].Amount.sum()
        rows.append({"Segment":seg,"Stores":len(stores),"Total Sales":round(sales,2)})
    return rows

def split_online_offline(net_sales: float, gst_amount: float):
    offline = gst_amount/1.05
    return {"offline_sales":round(offline,2),"online_sales":round(net_sales-offline,2)}