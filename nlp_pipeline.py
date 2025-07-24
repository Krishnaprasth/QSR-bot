# nlp_pipeline.py

import os
import re
import spacy

MODEL_PATH = "model_output/model-best"

if os.path.isdir(MODEL_PATH):
    # --- ML-BASED PIPELINE ---
    nlp = spacy.load(MODEL_PATH)

    def predict(text: str):
        """
        Uses the trained spaCy model to return (intent, slots).
        intent comes from the textcat labels, slots from doc.ents.
        """
        doc = nlp(text)
        # Pick the highest-scoring intent
        intent = max(doc.cats, key=doc.cats.get) if doc.cats else "UNKNOWN"
        # Extract all entities
        slots = {ent.label_: ent.text for ent in doc.ents}
        return intent, slots

else:
    # --- RULE-BASED FALLBACK PIPELINE ---
    from spacy.pipeline import EntityRuler

    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")

    # 1) Slot patterns for key metrics, stores, and periods
    patterns = [
        # Metrics
        {"label":"METRIC","pattern":"Net Sales"},
        {"label":"METRIC","pattern":"COGS (food +packaging)"},
        {"label":"METRIC","pattern":"store Labor Cost"},
        {"label":"METRIC","pattern":"Utility Cost"},
        {"label":"METRIC","pattern":"Rent"},
        {"label":"METRIC","pattern":"CAM"},
        {"label":"METRIC","pattern":"Aggregator commission"},
        {"label":"METRIC","pattern":"Marketing & advertisement"},
        {"label":"METRIC","pattern":"Other opex expenses"},
        {"label":"METRIC","pattern":"Gross Margin"},
        {"label":"METRIC","pattern":"Outlet EBITDA"},
        # Store codes
        {"label":"STORE","pattern":[{"TEXT":{"REGEX":"^[A-Z]{3,4}$"}}]}
    ]

    # Periods: “Nov 2024”, ISO “2024-11”, hyphen “2021-Apr”, or fiscal “FY25”
    months = "|".join(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    patterns += [
        {"label":"PERIOD","pattern":[{"TEXT":{"REGEX":f"^({months})$"}},{"TEXT":{"REGEX":"^[0-9]{4}$"}}]},
        {"label":"PERIOD","pattern":[{"TEXT":{"REGEX":"^[0-9]{4}-[0-9]{2}$"}}]},
        {"label":"PERIOD","pattern":[{"TEXT":{"REGEX":f"^[0-9]{{4}}-({months})$"}}]},
        {"label":"PERIOD","pattern":[{"TEXT":{"REGEX":"^FY[0-9]{2}$"}}]}
    ]

    ruler.add_patterns(patterns)

    def determine_intent(text: str) -> str:
        t = text.lower()
        if "ssg" in t or "same-store sales growth" in t:
            return "SSG"
        if re.search(r"\bcompare\b", t):
            return "COMPARE"
        if re.search(r"\btrend\b", t):
            return "TREND"
        if re.search(r"\b(descend|ascending|descending)\b", t):
            return "RANK"
        if re.search(r"\b(max|highest|min|lowest)\b", t):
            return "MAX_METRIC"
        return "UNKNOWN"

    def predict(text: str):
        """
        Rule‑based fallback: returns (intent, slots) by regex & EntityRuler.
        """
        doc = nlp(text)
        intent = determine_intent(text)
        slots = {ent.label_: ent.text for ent in doc.ents}
        return intent, slots

# End of nlp_pipeline.py
