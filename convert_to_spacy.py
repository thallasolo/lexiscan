import json
import spacy
from spacy.tokens import DocBin

INPUT_FILE = "data/annotated/train_annotation.json"
OUTPUT_FILE = "ner/train.spacy"

nlp = spacy.blank("en")
db = DocBin()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    text = item["text"]
    doc = nlp.make_doc(text)
    ents = []

    for start, end, label in item["entities"]:
        span = doc.char_span(start, end, label=label)
        if span:
            ents.append(span)

    doc.ents = ents
    db.add(doc)

db.to_disk(OUTPUT_FILE)
print("✅ Converted annotations to SpaCy format:", OUTPUT_FILE)
