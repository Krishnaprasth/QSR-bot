import re
import spacy
from spacy.pipeline import EntityRuler

def create_nlp():
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
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
        {"label":"STORE","pattern":[{"TEXT":{"REGEX":"^[A-Z]{3,4}$"}}]},
    ]
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
    return nlp

nlp = create_nlp()

def determine_intent(text: str) -> str:
    t = text.lower()
    if re.search(r"\bcompare\b", t):
        return "COMPARE"
    if re.search(r"\btrend\b", t):
        return "TREND"
    if re.search(r"\b(max|highest|min|lowest)\b", t):
        return "MAX_METRIC"
    return "UNKNOWN"

def predict(text: str):
    doc = nlp(text)
    intent = determine_intent(text)
    slots = {ent.label_: ent.text for ent in doc.ents}
    return intent, slots
