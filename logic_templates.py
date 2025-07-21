import pandas as pd

def get_metric_by_store_and_fy(df, metric, store, fy):
    data = df[(df["Metric"] == metric) & (df["Store"] == store) & (df["FY"] == fy)]
    total = data["Amount (in lakhs)"].sum()
    return pd.DataFrame([{"Store": store, "FY": fy, metric: round(total, 2)}])

def compute_ssg_for_store(df, store, metric, from_fy, to_fy):
    df_filtered = df[(df["Store"] == store) & (df["Metric"] == metric)]
    sales_from = df_filtered[df_filtered["FY"] == from_fy]["Amount (in lakhs)"].sum()
    sales_to = df_filtered[df_filtered["FY"] == to_fy]["Amount (in lakhs)"].sum()
    if sales_from == 0:
        return pd.DataFrame([{"Store": store, "SSG %": "N/A"}])
    ssg = round(((sales_to - sales_from) / sales_from) * 100, 2)
    return pd.DataFrame([{"Store": store, "SSG %": ssg}])

def top_ssg_stores(df, from_fy, to_fy, top_n=10):
    stores = df["Store"].unique()
    ssg_list = []
    for store in stores:
        ssg_data = compute_ssg_for_store(df, store, "Net Sales", from_fy, to_fy)
        if ssg_data["SSG %"].iloc[0] != "N/A":
            ssg_list.append(ssg_data.iloc[0])
    result_df = pd.DataFrame(ssg_list).sort_values("SSG %", ascending=False).head(top_n)
    return result_df