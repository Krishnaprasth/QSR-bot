import os
import re
import datetime
import pandas as pd

def load_data():
    for p in ("data/sales_data.csv", "sales_data.csv"):
        if os.path.exists(p):
            df = pd.read_csv(p)
            break
    else:
        raise FileNotFoundError("sales_data.csv not found; please run sample_data_generator.py to create sample data or add your data file.")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df.dropna(subset=["Amount"])

# existing helper functions...
