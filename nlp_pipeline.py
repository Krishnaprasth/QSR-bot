# nlp_pipeline.py

import re
import spacy
from spacy.pipeline import EntityRuler

def create_nlp():
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")

    # 1) Metric patterns
    patterns = [
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
    ]

    # 2) Store code: 3–4 uppercase letters
    patterns.append({
        "label":"STORE",
        "pattern":[{"TEXT":{"REGEX":"^[A-Z]{3,4}$"}}]
    })

    # 3) Periods (e.g. "Nov 2024", "2024-11")
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        patterns.append({
            "label":"PERIOD",
            "pattern":[{"TEXT":m}, {"TEXT":{"REGEX":"^[0-9]{4}$"}}]
        })
    # Also ISO style
    patterns.append({
        "label":"PERIOD",
        "pattern":[{"TEXT":{"REGEX":"^[0-9]{4}-[0-9]{2}$"}}]
    })

    ruler.add_patterns(patterns)
    return nlp

nlp = create_nlp()

def determine_intent(text: str) -> str:
    t = text.lower()
    if re.search(r"\bcompare\b", t):
        return "COMPARE"
    if re.search(r"\btrend\b", t):
        return "TREND"
    # catch both “max” and synonyms
    if re.search(r"\b(max|highest|largest|min|smallest|lowest)\b", t):
        return "MAX_METRIC"
    return "UNKNOWN"

def predict(text: str):
    """
    Returns (intent, slots) where slots is a dict
    mapping ENTITY_LABEL → extracted text.
    """
    doc = nlp(text)
    intent = determine_intent(text)
    slots = {ent.label_: ent.text for ent in doc.ents}
    return intent, slots
