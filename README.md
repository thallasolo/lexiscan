🗓️ WEEK 1 — OCR Pipeline & Data Preparation
🎯 Goal
Prepare high-quality text data from raw legal PDFs for downstream NLP model training.
🔧 What was done
1️⃣ Project setup

Created a clean folder structure
Set up Python environment
Initialized GitHub repository

data/raw_pdfs/      → input PDF contracts  
data/ocr_text/      → extracted OCR text  
ocr/                → OCR pipeline code  

2️⃣ PDF → Image conversion
Used Poppler with pdf2image
Converted each PDF page into high-resolution images (dpi=300)
images = convert_from_bytes(pdf_bytes, dpi=300)

3️⃣ OCR using Tesseract
Extracted text from images
Handled scanned + image-only contracts
Stored text as .txt files for review

4️⃣ OCR Quality Check (Manual)
Reviewed extracted text to verify:
Dates are readable
Party names are intact
Amounts are visible

📌 Bad OCR → Fix preprocessing before annotation
5️⃣ Output of Week 1
✔ Clean text data
✔ OCR pipeline ready
✔ Ready for annotation

✅ Validation
OCR text manually inspected
Notes documented in annotation_notes.md

🗓️ WEEK 2 — Named Entity Recognition (NER)
🎯 Goal
Train a custom NLP model to understand legal language and extract entities.
🔧 What was done
1️⃣ Annotation creation
Created data/annotated/train_annotations.json
Annotated 30–50 samples
Used BIO-style entity spans

Entities:
PARTY
DATE
AMOUNT
JURISDICTION

Example:
{
  "text": "Agreement dated February 1, 2018 between Zynga Inc. and WPT Enterprises.",
  "entities": [
    [17, 33, "DATE"],
    [42, 51, "PARTY"],
    [56, 71, "PARTY"]
  ]
}

2️⃣ Convert annotations to SpaCy format
python ner/convert_to_spacy.py

Output:
ner/train.spacy
3️⃣ Train custom SpaCy NER model
python ner/train.py

Loss decreased across epochs
Model saved as:
ner/lexiscan_ner_model/

4️⃣ Evaluation
Used F1-score to evaluate performance
Early-stage model showed learning signal

✅ Validation
✔ Model successfully predicts dates and parties
✔ Ready for inference + improvement loop

🗓️ WEEK 3 — Rule-Based Precision Layer
🎯 Goal
Improve precision and handle legal edge cases that ML alone cannot.

🔧 What was done
1️⃣ Post-processing rules added
Handled problems like:
(i), (30), (the “ false positives

Section headers being misclassified as parties
2️⃣ Party cleanup logic
Removed noisy tokens
Ensured realistic company names
Allowed OCR-broken company names
if len(p.split()) >= 3:
    keep

3️⃣ Normalization rules
Dates → ISO-8601 format
Amounts → numeric values

✅ Validation
✔ Garbage entities reduced by ~80–90%
✔ Output became legally meaningful

🗓️ WEEK 4 — API, Docker & End-to-End Pipeline
🎯 Goal
Deploy the entire system as a production-ready service.

🔧 What was done
1️⃣ FastAPI backend
Created /extract endpoint:
Accepts PDF upload
Returns structured JSON

2️⃣ End-to-End flow
PDF → Image → OCR → NER → Rules → JSON

3️⃣ Dockerization
Installed OCR dependencies inside Docker
Ensured OS-independent deployment
docker build -t lexiscan-auto .
docker run -p 8000:8000 lexiscan-auto

4️⃣ Browser support
Used FastAPI Swagger UI
http://localhost:8000/docs
Upload PDF → Click Execute → Get JSON

5️⃣ Automation (Optional)
Folder watcher auto-processes new PDFs
Simulates production ingestion pipeline

✅ Validation
✔ API runs in Docker
✔ Browser & curl both work
✔ Unseen PDFs processed successfully
