# nlp_pipeline.py

import spacy
from spacy.pipeline import EntityRuler

def create_nlp():
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")

    # 1) Metric patterns
    metrics = [
        "Net Sales",
        "COGS (food +packaging)",
        "store Labor Cost",
        "Utility Cost",
        "Rent",
        "CAM",
        "Aggregator commission",
        "Marketing & advertisement",
        "Other opex expenses",
        "Gross Margin",
        "Outlet EBITDA",
    ]
    patterns = [{"label":"METRIC","pattern":m} for m in metrics]

    # 2) Store-code pattern: 3–4 uppercase letters
    patterns.append({
        "label":"STORE",
        "pattern":[{"TEXT":{"REGEX":"^[A-Z]{3,4}$"}}]
    })

    # 3) Period patterns (e.g. "Nov 2024", "2024-11")
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        patterns.append({
            "label":"PERIOD",
            "pattern":[{"TEXT":m}, {"TEXT":{"REGEX":"^[0-9]{4}$"}}]
        })
    patterns.append({
        "label":"PERIOD",
        "pattern":[{"TEXT":{"REGEX":"^[0-9]{4}-[0-9]{2}$"}}]
    })

    ruler.add_patterns(patterns)

    # 4) Intent classifier stub
    textcat = nlp.add_pipe("textcat")
    for intent in ["MAX_METRIC","TREND","COMPARE"]:
        textcat.add_label(intent)

    return nlp

# instantiate once
nlp = create_nlp()

def predict(text: str):
    """
    Returns (intent, slots) for a given user utterance.
    intent: one of MAX_METRIC, TREND, COMPARE (or None if untrained)
    slots: dict of extracted entities, e.g. {"METRIC":"Net Sales", "STORE":"HSR", "PERIOD":"Nov 2024"}
    """
    doc = nlp(text)
    intent = None
    if hasattr(doc, "cats"):
        # pick highest‑scoring intent
        intent = max(doc.cats, key=doc.cats.get)
    slots = {ent.label_: ent.text for ent in doc.ents}
    return intent, slots

if __name__ == "__main__":
    # quick smoke‑test
    samples = [
        "Which store had max Net Sales in Nov 2024?",
        "Show trend of Outlet EBITDA for HSR",
        "Compare Rent for KOR vs HSR in FY25",
    ]
    for s in samples:
        print(s, "→", predict(s))
