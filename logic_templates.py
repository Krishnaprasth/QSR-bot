
import pandas as pd

def total_metric_by_store_and_fy(df, metric, store, fy):
    result = df[(df["Metric"].str.lower() == metric.lower()) & 
                (df["Store"] == store) & 
                (df["FY"] == fy)]
    total = result["Amount (in lakhs)"].sum()
    return pd.DataFrame({"Metric": [metric], "Store": [store], "FY": [fy], "Total": [round(total, 2)]})

def average_metric_by_store(df, metric, store):
    result = df[(df["Metric"].str.lower() == metric.lower()) & (df["Store"] == store)]
    avg = result["Amount (in lakhs)"].mean()
    return pd.DataFrame({"Store": [store], f"Average {metric}": [round(avg, 2)]})

def ssg_between_fys(df, metric, store, fy1, fy2):
    sales1 = df[(df["Metric"].str.lower() == metric.lower()) & (df["Store"] == store) & (df["FY"] == fy1)]["Amount (in lakhs)"].sum()
    sales2 = df[(df["Metric"].str.lower() == metric.lower()) & (df["Store"] == store) & (df["FY"] == fy2)]["Amount (in lakhs)"].sum()
    growth = ((sales1 - sales2) / sales2 * 100) if sales2 else None
    return pd.DataFrame({"Store": [store], "SSG %": [round(growth, 2) if growth is not None else "NA"]})

def trend_by_month(df, metric, store):
    result = df[(df["Metric"].str.lower() == metric.lower()) & (df["Store"] == store)]
    return result[["Month-Year", "Amount (in lakhs)"]].sort_values("Month-Year")

def top_stores_by_metric_fy(df, metric, fy, top_n=5):
    result = df[(df["Metric"].str.lower() == metric.lower()) & (df["FY"] == fy)]
    agg = result.groupby("Store")["Amount (in lakhs)"].sum().reset_index()
    return agg.sort_values("Amount (in lakhs)", ascending=False).head(top_n).reset_index(drop=True)

def lowest_store_by_metric_fy(df, metric, fy):
    result = df[(df["Metric"].str.lower() == metric.lower()) & (df["FY"] == fy)]
    agg = result.groupby("Store")["Amount (in lakhs)"].sum().reset_index()
    return agg.sort_values("Amount (in lakhs)", ascending=True).head(1).reset_index(drop=True)

def rent_as_percent_of_sales(df, store, fy):
    rent = df[(df["Metric"].str.lower().str.contains("rent")) & (df["Store"] == store) & (df["FY"] == fy)]["Amount (in lakhs)"].sum()
    sales = df[(df["Metric"].str.lower() == "net sales") & (df["Store"] == store) & (df["FY"] == fy)]["Amount (in lakhs)"].sum()
    percent = (rent / sales * 100) if sales else None
    return pd.DataFrame({"Store": [store], "FY": [fy], "Rent % of Sales": [round(percent, 2) if percent is not None else "NA"]})
