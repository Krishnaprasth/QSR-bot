import numpy as np
from openai import OpenAI

class IntentManager:
    def __init__(self, openai_client, model="text-embedding-ada-002"):
        self.openai = openai_client
        self.model = model
        self.templates = [
            {"name":"generate_report","description":"Full performance report","example":"Generate report for HSR FY 24-25"},
            {"name":"generate_vintage_report","description":"Vintage segment KPIs","example":"Vintage report FY 24-25"},
            {"name":"split_online_offline","description":"Split channel sales","example":"Split online vs offline sales"}
        ]
        self.embeddings = self._embed([t["example"] for t in self.templates])

    def _embed(self, texts):
        resp = self.openai.embeddings.create(model=self.model,input=texts)
        return np.array([e.embedding for e in resp.data])

    def get_top_intents(self, query, k=3):
        resp = self.openai.embeddings.create(model=self.model,input=[query])
        q = np.array(resp.data[0].embedding)
        sims = (self.embeddings @ q)/(np.linalg.norm(self.embeddings,axis=1)*np.linalg.norm(q))
        return [self.templates[i] for i in np.argsort(-sims)[:k]]