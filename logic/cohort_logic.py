
import pandas as pd

def tag_cohorts(df):
    first_months = df[df['Metric'] == "Net Sales"].groupby("Store")["Month"].min().reset_index()
    first_months.rename(columns={"Month": "Cohort"}, inplace=True)
    return df.merge(first_months, on="Store", how="left")
