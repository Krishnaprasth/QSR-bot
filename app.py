import streamlit as st
import pandas as pd
import numpy as np
import openai
from datetime import datetime

# -------------------- CONFIG --------------------
st.set_page_config(page_title="QSR CEO Performance Bot", layout="wide")
st.title("🍔 QSR CEO Performance Bot")

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("Upload final_cleaned_50_months.csv", type=["csv"])

if not uploaded_file:
    st.warning("Please upload the final_cleaned_50_months.csv to begin.")
    st.stop()

df = pd.read_csv(uploaded_file)
df['Month'] = pd.to_datetime(df['Month'], errors='coerce')

# -------------------- OPENAI API --------------------
try:
    api_key = st.secrets["openai_api_key"]
except KeyError:
    api_key = st.text_input("Enter your OpenAI API key:", type="password")

if not api_key:
    st.stop()
else:
    openai.api_key = api_key

# -------------------- INPUT QUESTION --------------------
question = st.text_input("Ask a question about store performance:")
if not question:
    st.stop()

# -------------------- LOGIC BLOCKS --------------------
def logic_engine(q, df):
    q = q.lower()

    # 1. Store-wise revenue for a month
    if "revenue" in q and "may 25" in q:
        mask = (df['Month'].dt.strftime('%b-%y') == 'May-25') & (df['Metric'].str.lower() == 'net sales')
        result = df[mask].groupby('Store')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)
        return result

    # 2. FY Net Sales for all stores
    elif "net sales" in q and "fy" in q:
        try:
            fy = [s for s in q.split() if s.startswith("fy")][0]
            year = int(fy[-2:])
            start = pd.Timestamp(f"20{year-1}-04-01")
            end = pd.Timestamp(f"20{year}-03-31")
            result = df[(df['Metric'].str.lower() == 'net sales') & (df['Month'] >= start) & (df['Month'] <= end)]
            out = result.groupby("Store")["Amount"].sum().reset_index().sort_values(by="Amount", ascending=False)
            return out
        except:
            return None

    # 3. EBITDA Margin
    elif "ebitda margin" in q:
        try:
            sales = df[df['Metric'].str.lower() == 'net sales']
            ebitda = df[df['Metric'].str.lower().str.contains('ebitda')]
            merged = pd.merge(sales, ebitda, on=["Month", "Store"], suffixes=("_sales", "_ebitda"))
            merged["EBITDA Margin"] = (merged["Amount_ebitda"] / merged["Amount_sales"]) * 100
            return merged[["Month", "Store", "EBITDA Margin"]].sort_values(by=["Month", "Store"])
        except:
            return None

    # 4. SSSG (Same Store Sales Growth)
    elif "sssg" in q or "same store sales" in q:
        try:
            sales = df[df['Metric'].str.lower() == 'net sales'].copy()
            sales['Year'] = sales['Month'].dt.year
            sales['FY'] = sales['Month'].apply(lambda x: f"FY{x.year+1}" if x.month <= 3 else f"FY{x.year+1}")
            cohort_start = sales.groupby('Store')['Month'].min().reset_index()
            cohort_start['Open_FY'] = cohort_start['Month'].apply(lambda x: f"FY{x.year+1}" if x.month <= 3 else f"FY{x.year+1}")
            sales = pd.merge(sales, cohort_start[['Store', 'Open_FY']], on='Store')
            eligible = sales[sales['FY'] > sales['Open_FY']]
            fy_sales = eligible.groupby(['Store', 'FY'])['Amount'].sum().reset_index()
            fy_sales['SSSG'] = fy_sales.groupby('Store')['Amount'].pct_change() * 100
            return fy_sales.dropna()
        except:
            return None

    return None

# -------------------- EXECUTE LOGIC --------------------
result = logic_engine(question, df)

if isinstance(result, pd.DataFrame) and not result.empty:
    st.success("✅ Answer generated from logic blocks")
    st.dataframe(result)
else:
    # -------------------- FALLBACK TO GPT --------------------
    try:
        schema = "Data has columns: Month, Store, Metric, Amount"
        sample_data = df.head(20).to_csv(index=False)
        prompt = f"""\nYou are a QSR performance analyst.
The user will ask questions based on store performance data.
Data schema: {schema}
Sample data:\n{sample_data}
Question: {question}
Give a concise and clear answer based only on the table and schema."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        st.markdown("🤖 GPT Answer:")
        st.info(response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"GPT Fallback Error: {e}")
