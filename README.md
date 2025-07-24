# QSR CEO Performance Bot

A hybrid NLP + structured query bot for Quick Service Restaurant store metrics.

## Setup

```bash
git clone <repo_url>
cd qsr_ceo_bot
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Files

- `nlp_pipeline.py`: spaCy-based intent & entity extraction.
- `query_planner.py`: Data loading and query-handling functions.
- `app.py`: Streamlit UI for interactive Q&A.
- `requirements.txt`: Python dependencies.
- `README.md`: Project overview and instructions.

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then upload your `sales_data.csv` and start asking performance questions!