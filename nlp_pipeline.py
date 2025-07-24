import spacy

# Load your fine-tuned spaCy model
nlp = spacy.load("model_output/model-best")

def predict(text: str):
    """
    Uses the trained spaCy pipeline to extract:
      - intent from textcat labels
      - slots from NER entities
    """
    doc = nlp(text)
    # Determine intent: highest-scoring textcat category
    intent = max(doc.cats, key=doc.cats.get)
    # Extract slots
    slots = {ent.label_: ent.text for ent in doc.ents}
    return intent, slots