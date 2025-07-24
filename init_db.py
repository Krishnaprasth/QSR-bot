import pandas as pd
import sqlite3

# 1. Read the CSV
df = pd.read_csv("sales_data.csv")

# 2. Create SQLite database
conn = sqlite3.connect("sales_data.db")
df.to_sql("sales", conn, if_exists="replace", index=False)
conn.close()

print("sales_data.db created.")