import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import io

# App title and UI
st.set_page_config(page_title="QSR CEO Performance Bot", layout="wide")
st.markdown("## 📊 QSR CEO Performance Bot")
st.markdown("#### 📁 Upload your cleaned 50-month QSR dataset (optional)")

# Load default dataset
@st.cache_data
def load_default_data():
    return pd.read_csv("final_cleaned_50_months.csv")

# Dataset uploader
uploaded_file = st.file_uploader("Drag and drop file here", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Custom dataset uploaded")
else:
    df = load_default_data()
    st.info("📊 Using default dataset: final_cleaned_50_months.csv")

# Show sample
if st.checkbox("Preview data", False):
    st.dataframe(df.head(10))

# Normalize month field
def normalize_month(df):
    df["Month"] = pd.to_datetime(df["Month"], errors='coerce')
    df["Month"] = df["Month"].dt.strftime('%b %Y')
    return df

df = normalize_month(df)

# Core logic engine
def compute_answer(query, df):
    query = query.lower()

    if "highest sales" in query or "max revenue" in query:
        month_str = ""
        for word in query.split():
            if word[:3].lower() in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]:
                month_str = word[:3].capitalize()
        year = "".join([c for c in query if c.isdigit()])
        target_month = f"{month_str} 20{year[-2:]}" if year else None

        if target_month and "Net Sales" in df.columns:
            filtered = df[df["Month"] == target_month]
            top = filtered.loc[filtered["Net Sales"].idxmax()]
            return f"🏆 Store with highest Net Sales in {target_month} was **{top['Store']}** with ₹{top['Net Sales']:.2f} lakhs."
        else:
            return "❗ Could not understand month/year in query."

    return None  # fallback needed

# GPT fallback
def get_gpt_fallback_answer(user_query):
    try:
        client = OpenAI(api_key=st.secrets["openai_api_key"])

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful QSR analytics assistant for a CEO. Respond based on store performance data."},
                {"role": "user", "content": user_query},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"GPT fallback failed:\n\n{str(e)}"

# User query
st.markdown("### 🤖 Ask a question about store performance:")
user_query = st.text_input("e.g., which store did max revenue in Nov 24")

if user_query:
    answer = compute_answer(user_query, df)
    if answer:
        st.markdown(f"**✅ Answer:** {answer}")
    else:
        st.markdown("**🤖 GPT Answer:**")
        st.markdown(get_gpt_fallback_answer(user_query))
