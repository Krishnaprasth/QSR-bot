import random
import spacy
from spacy.tokens import DocBin

# 1. Load the full training DocBin
docbin = DocBin().from_disk("train_qsr.spacy")

# 2. Unpickle docs
nlp = spacy.blank("en")
docs = list(docbin.get_docs(nlp.vocab))

# 3. Shuffle & split (80% train / 20% dev)
random.shuffle(docs)
split = int(len(docs) * 0.8)
train_docs, dev_docs = docs[:split], docs[split:]

# 4. Save out train.spacy and dev.spacy
DocBin(docs=train_docs, store_user_data=True).to_disk("train.spacy")
DocBin(docs=dev_docs,   store_user_data=True).to_disk("dev.spacy")

print(f"Saved {len(train_docs)} training and {len(dev_docs)} dev examples.")