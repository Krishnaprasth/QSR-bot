import numpy as np
from openai import OpenAI

class IntentManager:
    def __init__(self, openai_client, model="text-embedding-ada-002"):
        self.openai = openai_client
        self.model = model
        self.templates = [
            {"name":"run_aggregation","description":"Aggregate a metric","example":"Total Net Sales by Store"},
            {"name":"run_trend","description":"Time series of a metric","example":"Net Sales trend for HSR FY25"},
            {"name":"run_comparison","description":"Compare two entities","example":"Compare HSR vs KOR net sales FY25"},
            {"name":"run_anomaly_detection","description":"Detect anomalies","example":"Detect labor cost spikes for HSR"},
            {"name":"run_stat_test","description":"Statistical correlation","example":"Correlation between marketing and sales"},
            # ... include other templates ...
        ]
        self.embeddings = self._embed([t["example"] for t in self.templates])

    def _embed(self, texts):
        resp = self.openai.embeddings.create(model=self.model, input=texts)
        return np.array([e.embedding for e in resp.data])

    def get_top_intents(self, query, k=3):
        resp = self.openai.embeddings.create(model=self.model, input=[query])
        q = np.array(resp.data[0].embedding)
        sims = (self.embeddings @ q) / (np.linalg.norm(self.embeddings,axis=1)*np.linalg.norm(q))
        return [self.templates[i] for i in np.argsort(-sims)[:k]]