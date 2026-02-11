import spacy

# Load your trained NER model
MODEL_PATH = "ner/lexiscan_ner_model"
nlp = spacy.load(MODEL_PATH)

# Test sentences (you can modify these)
test_sentences = [
    "This agreement was signed on April 6, 2007 between Chase Bank USA and ABC Media.",
    "The total payment under this contract is INR 5,000.",
    "This Agreement shall be governed by the laws of the State of New York.",
    "The termination date of this agreement is December 31, 2025."
]

# Run NER on each sentence
for text in test_sentences:
    print("\nTEXT:", text)
    doc = nlp(text)

    if not doc.ents:
        print("  No entities detected.")
    else:
        for ent in doc.ents:
            print(f"  Entity: {ent.text} | Label: {ent.label_}")
