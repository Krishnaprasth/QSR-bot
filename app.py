# QSR CEO BOT with Logic Blocks and Reasoning Layer (Final Version)
import streamlit as st
import pandas as pd
import numpy as np
import openai

st.set_page_config(page_title="QSR CEO Performance Bot", layout="wide")
st.title("🍔 QSR CEO Performance Bot")

# Load CSV from GitHub repo (not upload)
@st.cache_data
def load_data():
    return pd.read_csv("final_cleaned_50_months.csv")

df = load_data()
df['Month'] = pd.to_datetime(df['Month'], format='%b-%y', errors='coerce')

# Get OpenAI API key from secrets
api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key not found in Streamlit secrets.")
    st.stop()
openai.api_key = api_key

# Ask question
question = st.text_input("Ask a question about store performance:")
if not question:
    st.stop()

# Logic Engine
def run_logic_blocks(question, df):
    q = question.lower()

    if "net sales" in q and "fy" in q:
        try:
            fy = [s for s in q.split() if s.upper().startswith("FY")][0]
            fy_year = int(fy[-2:])
            start = pd.Timestamp(f"20{fy_year - 1}-04-01")
            end = pd.Timestamp(f"20{fy_year}-03-31")
            result = df[(df['Metric'].str.lower() == 'net sales') & (df['Month'] >= start) & (df['Month'] <= end)]
            out = result.groupby("Store")["Amount"].sum().reset_index().sort_values(by="Amount", ascending=False)
            return out
        except:
            return None

    elif "ebitda margin" in q:
        try:
            sales = df[df['Metric'].str.lower() == 'net sales']
            ebitda = df[df['Metric'].str.lower().str.contains('ebitda')]
            merged = pd.merge(sales, ebitda, on=["Month", "Store"], suffixes=("_sales", "_ebitda"))
            merged["EBITDA Margin"] = (merged["Amount_ebitda"] / merged["Amount_sales"]) * 100
            return merged[["Month", "Store", "EBITDA Margin"]].sort_values(by=["Month", "Store"])
        except:
            return None

    elif "sssg" in q or "same store sales growth" in q:
        try:
            sales = df[df['Metric'].str.lower() == 'net sales'].copy()
            sales['Year'] = sales['Month'].dt.year
            sales['FY'] = sales['Month'].apply(lambda x: f"FY{x.year+1}" if x.month <= 3 else f"FY{x.year+1}")
            sales['Quarter'] = sales['Month'].dt.quarter

            cohort_start = sales.groupby('Store')['Month'].min().reset_index()
            cohort_start['Open_FY'] = cohort_start['Month'].apply(lambda x: f"FY{x.year+1}" if x.month <= 3 else f"FY{x.year+1}")
            sales = pd.merge(sales, cohort_start[['Store', 'Open_FY']], on='Store')
            eligible = sales[sales['FY'] > sales['Open_FY']]

            # FY-wise SSSG
            fy_sales = eligible.groupby(['Store', 'FY'])['Amount'].sum().reset_index()
            fy_sales.sort_values(by=['Store', 'FY'], inplace=True)
            fy_sales['SSSG'] = fy_sales.groupby('Store')['Amount'].pct_change() * 100

            # Company SSSG
            company_fy_sales = eligible.groupby(['FY'])['Amount'].sum().reset_index()
            company_fy_sales['Company SSSG'] = company_fy_sales['Amount'].pct_change() * 100

            # Quarterly SSSG
            q_sales = eligible.copy()
            q_sales['FQ'] = q_sales['Month'].apply(lambda x: f"FY{x.year+1} Q{x.quarter}")
            store_q_sales = q_sales.groupby(['Store', 'FQ'])['Amount'].sum().reset_index()
            store_q_sales['SSSG'] = store_q_sales.groupby('Store')['Amount'].pct_change() * 100

            # Top and Bottom 5 Stores by SSSG
            top_bottom = fy_sales.dropna().copy()
            last_year = top_bottom['FY'].max()
            last_year_data = top_bottom[top_bottom['FY'] == last_year]
            top_5 = last_year_data.sort_values(by='SSSG', ascending=False).head(5)
            bottom_5 = last_year_data.sort_values(by='SSSG').head(5)

            return fy_sales.dropna(subset=['SSSG']), company_fy_sales.dropna(), store_q_sales.dropna(), top_5, bottom_5
        except:
            return None

    return None

# Run logic engine
logic_output = run_logic_blocks(question, df)

# Show logic result
if isinstance(logic_output, tuple):
    st.success("📈 Answer from Logic Engine (SSSG)")
    store_df, company_df, store_q_df, top5, bottom5 = logic_output
    st.subheader("📊 Store-level SSSG (FY-wise)")
    st.dataframe(store_df)
    st.subheader("🏢 Company-level SSSG (FY-wise)")
    st.dataframe(company_df)
    st.subheader("📈 Store-level SSSG (Quarterly)")
    st.dataframe(store_q_df)
    st.subheader("🔥 Top 5 Stores by SSSG in last FY")
    st.dataframe(top5)
    st.subheader("❄️ Bottom 5 Stores by SSSG in last FY")
    st.dataframe(bottom5)

elif isinstance(logic_output, pd.DataFrame) and not logic_output.empty:
    st.success("📊 Answer from Logic Engine")
    st.dataframe(logic_output)

else:
    # GPT fallback
    sample = df.head(15).to_csv(index=False)
    prompt = f"""You are a financial analyst for a QSR chain.
The dataset has: Month, Store, Metric, Amount.
Sample data:
{sample}

Now answer this question using reasoning and financial knowledge:
Question: {question}
Answer:"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        st.markdown("🤖 GPT Answer:\n\n" + response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ GPT Error: {e}")
