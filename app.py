import streamlit as st
import pandas as pd
import numpy as np
import openai
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

st.set_page_config(page_title="QSR CEO Bot", layout="wide")

# ========== Load Data ==========
@st.cache_data
def load_default_csv():
    return pd.read_csv("final_cleaned_50_months.csv")

# ========== GPT Fallback ==========
def gpt_fallback(query, context):
    prompt = f"You are a QSR CEO bot. Answer the following based on the data context:\n{context}\n\nQuestion: {query}"
    try:
        openai.api_key = st.secrets["openai_api_key"]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a QSR performance analysis bot."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"GPT fallback failed: {e}"

# ========== Metric Engine ==========
def compute_metric(df, query):
    if "net sales" in query.lower():
        result = df.groupby("Month")["Net Sales"].sum().reset_index()
        return result
    return None

# ========== Cohort Logic ==========
def analyze_store_cohort(df):
    df['Open Month'] = df.groupby('Store')['Month'].transform('min')
    cohort_perf = df.groupby('Open Month')['Net Sales'].mean().reset_index()
    return cohort_perf

# ========== Counterfactual ==========
def simulate_counterfactual(df, store, metric, factor):
    store_df = df[df["Store"] == store].copy()
    store_df[metric] *= factor
    return store_df

# ========== Semantic Match ==========
def find_best_match(query, questions):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([query] + questions)
    sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    best_idx = np.argmax(sims)
    return questions[best_idx] if sims[best_idx] > 0.5 else None

# ========== Streamlit App ==========
st.title("📊 QSR CEO Performance Bot")

uploaded_file = st.file_uploader(
    "📁 Upload your cleaned 50-month QSR dataset (optional)", 
    type=["csv"],
    help="If no file is uploaded, the default dataset (final_cleaned_50_months.csv) will be used."
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Using uploaded file")
else:
    df = load_default_csv()
    st.info("📊 Using default dataset: final_cleaned_50_months.csv")

query = st.text_input("🧠 Ask a question about store performance:")

if query:
    with st.spinner("Analyzing your question..."):
        answer_df = compute_metric(df, query)
        if answer_df is not None:
            st.write("📈 Structured Answer:")
            st.dataframe(answer_df)
        else:
            fallback = gpt_fallback(query, df.head(20).to_string())
            st.write("🤖 GPT Answer:")
            st.markdown(fallback)
