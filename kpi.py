import datetime
import numpy as np
import pandas as pd
from utils import find_metric, infer_opening_date, months_between, month_order, store_vintage

def run_aggregation(df, metric, aggfunc, by=None):
    by = by or []
    df_metric = df[df.Metric == metric]
    series = getattr(df_metric.groupby(by)["Amount"], aggfunc)()
    return series.reset_index().rename(columns={"Amount": aggfunc}).to_dict(orient="records")

def run_trend(df, metric, group_by=None, window=1):
    gb = group_by or []
    df_metric = df[df.Metric == metric]
    ts = df_metric.groupby(gb + ["Month"])["Amount"].sum().reset_index()
    pivot = ts.pivot(index="Month", columns=gb, values="Amount").reindex(month_order).fillna(0)
    trend = pivot.rolling(window=window, min_periods=1).mean()
    return {"months": trend.index.tolist(), "values": trend.values.tolist()}

def run_comparison(df, entity_type, entity1, entity2, metric):
    key = entity_type
    df_metric = df[df.Metric == metric]
    grp = df_metric.groupby([key, "FY"])["Amount"].sum().reset_index()
    val1 = grp[(grp[key] == entity1)]["Amount"].tolist()
    val2 = grp[(grp[key] == entity2)]["Amount"].tolist()
    return {entity1: val1, entity2: val2}

def run_anomaly_detection(df, metric, group_by=None, method="zscore", threshold=2.5):
    gb = group_by or []
    df_metric = df[df.Metric == metric]
    ts = df_metric.groupby(gb + ["Month"])["Amount"].sum().reset_index()
    stats = ts.groupby(gb)["Amount"].agg(["mean", "std"]).reset_index()
    merged = pd.merge(ts, stats, on=gb)
    if method == "zscore":
        merged["z"] = (merged["Amount"] - merged["mean"]) / merged["std"]
        anomalies = merged[merged["z"].abs() > threshold]
    else:
        q1 = merged.groupby(gb)["Amount"].quantile(0.25)
        q3 = merged.groupby(gb)["Amount"].quantile(0.75)
        iqr = q3 - q1
        merged = merged.merge(q1.rename("q1"), on=gb).merge(q3.rename("q3"), on=gb)
        merged["iqr_flag"] = ((merged["Amount"] < (merged["q1"] - threshold*iqr)) | (merged["Amount"] > (merged["q3"] + threshold*iqr)))
        anomalies = merged[merged["iqr_flag"]]
    return anomalies[gb + ["Month", "Amount"]].to_dict(orient="records")

def run_stat_test(df, metric_x, metric_y, test="pearson"):
    df_x = df[df.Metric == metric_x].groupby("Store")["Amount"].sum()
    df_y = df[df.Metric == metric_y].groupby("Store")["Amount"].sum()
    common = df_x.index.intersection(df_y.index)
    x = df_x.loc[common]
    y = df_y.loc[common]
    if test == "pearson":
        from scipy.stats import pearsonr
        r, p = pearsonr(x, y)
    elif test == "spearman":
        from scipy.stats import spearmanr
        r, p = spearmanr(x, y)
    else:
        from scipy.stats import ttest_ind
        r, p = ttest_ind(x, y)
    return {"r": r, "p_value": p}

# Existing specific functions omitted for brevity...
