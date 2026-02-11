import spacy
import random
from spacy.training.example import Example
from spacy.tokens import DocBin

TRAIN_DATA = "ner/train.spacy"
OUTPUT_DIR = "ner/lexiscan_ner_model"

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

LABELS = ["DATE", "AMOUNT", "PARTY", "JURISDICTION"]
for label in LABELS:
    ner.add_label(label)

doc_bin = DocBin().from_disk(TRAIN_DATA)
docs = list(doc_bin.get_docs(nlp.vocab))

nlp.initialize()

for epoch in range(20):
    random.shuffle(docs)
    losses = {}
    for doc in docs:
        example = Example.from_dict(
            doc,
            {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}
        )
        nlp.update([example], losses=losses)
    print(f"Epoch {epoch+1} | Losses: {losses}")

nlp.to_disk(OUTPUT_DIR)
print("✅ NER model trained and saved.")
