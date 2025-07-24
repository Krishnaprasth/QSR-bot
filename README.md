# QSR CEO Data‑Chat Bot

A Streamlit app that loads sales data from a SQLite database and lets you chat with GPT over the data.

## Files

- `sales_data.csv`: Source CSV (for reference).
- `sales_data.db`: SQLite database table `sales` generated from the CSV.
- `init_db.py`: Script to create/update `sales_data.db` from the CSV.
- `app.py`: Streamlit application using LangChain to chat with the data.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files to exclude from Git.

## Setup

```bash
git clone <repo_url>
cd streamlit_sql_app
pip install -r requirements.txt
python init_db.py
streamlit run app.py
```

Ensure `OPENAI_API_KEY` is set in your environment.