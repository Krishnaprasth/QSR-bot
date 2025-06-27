
from logic.metrics_engine import compute_metric
from logic.counterfactuals import simulate_scenario
import pandas as pd
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set in your environment

def route_query(query, df):
    query = query.lower()
    if "net sales" in query and "store" in query:
        return compute_metric(df, "Net Sales")
    elif "cam cap" in query:
        return simulate_scenario(df, "CAM", 200000)
    else:
        return gpt_fallback(query, df)

def gpt_fallback(query, df):
    sample_data = df.head(100).to_dict(orient="records")

    prompt = f"""
You are a financial analyst for a QSR chain.
You have the following data (sample of full data):

{sample_data}

Answer this query using only the above data:
{query}

If you cannot answer exactly, say "Not enough data to answer".
Keep your answer structured and concise.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a QSR financial analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        answer = response.choices[0].message.content
        return pd.DataFrame([{"GPT Response": answer}])
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
