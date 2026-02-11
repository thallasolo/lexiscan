import json
import spacy
import matplotlib.pyplot as plt
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score

# --------------------------------------------------
# Load trained model
# --------------------------------------------------
nlp = spacy.load("ner/lexiscan_ner_model")

ANNOTATIONS_FILE = "data/annotated/train_annotation.json"

true_labels = []
pred_labels = []

# --------------------------------------------------
# Load annotations
# --------------------------------------------------
with open(ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    text = item["text"]
    entities = item["entities"]

    # Create doc with model tokenizer
    doc = nlp.make_doc(text)

    true_seq = ["O"] * len(doc)

    # --------------------------------------------------
    # Build TRUE labels
    # --------------------------------------------------
    for start, end, label in entities:
        span = doc.char_span(start, end, alignment_mode="contract")

        if span is None:
            continue

        true_seq[span.start] = f"B-{label}"
        for i in range(span.start + 1, span.end):
            true_seq[i] = f"I-{label}"

    # --------------------------------------------------
    # Build PREDICTED labels
    # --------------------------------------------------
    doc_pred = nlp(text)
    pred_seq = ["O"] * len(doc_pred)

    for ent in doc_pred.ents:
        pred_seq[ent.start] = f"B-{ent.label_}"
        for i in range(ent.start + 1, ent.end):
            pred_seq[i] = f"I-{ent.label_}"

    # Ensure equal length
    if len(true_seq) == len(pred_seq):
        true_labels.append(true_seq)
        pred_labels.append(pred_seq)

# --------------------------------------------------
# Compute Metrics
# --------------------------------------------------
precision = precision_score(true_labels, pred_labels)
recall = recall_score(true_labels, pred_labels)
f1 = f1_score(true_labels, pred_labels)

print("\n==============================")
print("📊 MODEL PERFORMANCE METRICS")
print("==============================")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\n📄 Detailed Classification Report:\n")
print(classification_report(true_labels, pred_labels))

# --------------------------------------------------
# Save report to file
# --------------------------------------------------
with open("ner_model_report.txt", "w", encoding="utf-8") as report_file:
    report_file.write("MODEL PERFORMANCE\n")
    report_file.write(f"Precision: {precision:.4f}\n")
    report_file.write(f"Recall   : {recall:.4f}\n")
    report_file.write(f"F1 Score : {f1:.4f}\n\n")
    report_file.write(classification_report(true_labels, pred_labels))

# --------------------------------------------------
# Generate Performance Chart
# --------------------------------------------------
metrics = {
    "Precision": precision * 100,
    "Recall": recall * 100,
    "F1 Score": f1 * 100
}

plt.figure()
plt.bar(metrics.keys(), metrics.values())
plt.title("LexiScan NER Model Performance")
plt.ylabel("Score (%)")
plt.ylim(0, 100)
plt.savefig("ner_model_performance.png")
plt.show()

print("\n✅ Performance chart saved as ner_model_performance.png")
print("✅ Detailed report saved as ner_model_report.txt")
