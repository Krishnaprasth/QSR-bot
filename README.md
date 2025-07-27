# QSR CEO Bot

A GPT-4o-powered Streamlit app for on-demand financial and operational reporting of your QSR chain.

## Setup

1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd qsr-ceo-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your data CSV to `data/sales_data.csv`.
4. Set your OpenAI API key:
   - Locally: `export OPENAI_API_KEY="sk-..."`
   - Streamlit Cloud: in **Settings → Secrets**.

## Usage

- **Generate a full report**: “Generate report for HSR in FY 2024-25”
- **Vintage report**: “Generate vintage report for FY 2024-25”
- **Channel split**: “Show online vs offline split”

GPT will call underlying functions and render tables, charts, or PDFs.

## CI/CD

GitHub Actions runs lint and smoke tests on each push.
