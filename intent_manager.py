import numpy as np
from openai import OpenAI

class IntentManager:
    def __init__(self, openai_client, model="text-embedding-ada-002"):
        self.openai = openai_client
        self.model = model
        self.templates = [
            {"name":"generate_report","description":"Full report for a store and FY","example":"Generate report for HSR in FY 2024-25"},
            {"name":"generate_vintage_report","description":"Vintage KPI comparison","example":"Vintage report for FY 2024-25"},
            {"name":"split_online_offline","description":"Split online vs offline","example":"Split sales channel"},
            {"name":"get_top_sales_by_month","description":"Top net sales store for a given month/FY","example":"Which store had highest sales in Dec 2024?"},
            {"name":"get_revenue_breakup_by_cohort_by_fy","description":"Revenue by FY for specified cohorts","example":"Revenue breakup by FY for New and Mature stores"}
        ]
        self.embeddings = self._embed([t["example"] for t in self.templates])

    def _embed(self, texts):
        resp = self.openai.embeddings.create(model=self.model, input=texts)
        return np.array([e.embedding for e in resp.data])

    def get_top_intents(self, query, k=3):
        resp = self.openai.embeddings.create(model=self.model, input=[query])
        q = np.array(resp.data[0].embedding)
        sims = (self.embeddings @ q) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q))
        return [self.templates[i] for i in np.argsort(-sims)[:k]]