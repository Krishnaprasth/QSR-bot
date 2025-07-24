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
    ]
    # Store-code pattern: 3-4 uppercase letters
    patterns.append({"label":"STORE","pattern":[{"TEXT":{"REGEX":"^[A-Z]{3,4}$"}}]})
    # Period patterns (e.g. "Nov 2024", "2024-11")
    import re
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    for m in months:
        patterns.append({
            "label":"PERIOD",
            "pattern":[{"TEXT":m}, {"TEXT":{"REGEX":"^[0-9]{4}$"}}]
        })
    ruler.add_patterns(patterns)
    textcat = nlp.add_pipe("textcat")
    for intent in ["MAX_METRIC","TREND","COMPARE"]:
        textcat.add_label(intent)
    return nlp

nlp = create_nlp()

def predict(text):
    doc = nlp(text)
    intent = max(doc.cats, key=doc.cats.get) if hasattr(doc, "cats") else None
    slots = {ent.label_: ent.text for ent in doc.ents}
    return intent, slots

if __name__ == "__main__":
    tests = [
        "Which store had max Net Sales in Nov 2024?",
        "Show trend of Outlet EBITDA for HSR",
        "Compare Rent for KOR vs HSR in FY25"
    ]
    for t in tests:
        print(t, "->", predict(t))
