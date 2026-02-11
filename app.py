from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
from pdf2image import convert_from_bytes
import spacy
import re
import traceback
import os
import io
from PyPDF2 import PdfReader
from rapidfuzz import fuzz

from rules.date_rules import normalize_date
from rules.money_rules import normalize_amount


# --------------------------------------------------
# Initialize FastAPI
# --------------------------------------------------
app = FastAPI(title="LexiScan Auto API - Advanced")


@app.get("/")
def home():
    return {"message": "LexiScan Advanced API Running 🚀"}


# --------------------------------------------------
# Load spaCy model
# --------------------------------------------------
nlp = spacy.load("ner/lexiscan_ner_model")

if "parser" not in nlp.pipe_names and "senter" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")


# --------------------------------------------------
# Windows Tesseract path
# --------------------------------------------------
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


# --------------------------------------------------
# Helper: Date Context
# --------------------------------------------------
def classify_date_context(sentence_text):
    text = sentence_text.lower()

    if "effective" in text or "entered into" in text:
        return "Agreement effective date"
    elif "termination" in text or "expire" in text:
        return "Termination date"
    elif "advance payment" in text:
        return "Advance payment due"
    elif "final payment" in text:
        return "Final payment due"
    elif "payment" in text:
        return "Payment due"
    elif "remain in effect until" in text:
        return "Contract validity end date"

    return "Important contract date"


# --------------------------------------------------
# Helper: Party Role
# --------------------------------------------------
def classify_party_role(name, full_text):
    window_pattern = rf"{re.escape(name)}(.{{0,100}})"
    matches = re.findall(window_pattern, full_text, flags=re.IGNORECASE)
    context = " ".join(matches).lower()

    if "service provider" in context or "vendor" in context:
        return "Service Provider"
    elif "client" in context or "customer" in context:
        return "Client"
    elif "supplier" in context:
        return "Supplier"
    elif "contractor" in context:
        return "Contractor"
    elif "first party" in context:
        return "First Party"
    elif "second party" in context:
        return "Second Party"

    return "Contracting Party"


# --------------------------------------------------
# Helper: Normalize Company Name
# --------------------------------------------------
def normalize_company_name(name):
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)

    suffixes = [
        "inc", "incorporated", "corp", "corporation",
        "llc", "ltd", "limited", "company"
    ]

    words = [w for w in name.split() if w not in suffixes]
    return " ".join(words).strip()


# --------------------------------------------------
# Helper: Merge Similar Companies
# --------------------------------------------------
def merge_similar_companies(parties):
    merged = []
    used = set()

    for i, p1 in enumerate(parties):
        if i in used:
            continue

        group = [p1]
        norm1 = normalize_company_name(p1["name"])

        for j, p2 in enumerate(parties):
            if j <= i or j in used:
                continue

            norm2 = normalize_company_name(p2["name"])
            similarity = fuzz.ratio(norm1, norm2)

            if similarity > 85:
                group.append(p2)
                used.add(j)

        best_name = max(group, key=lambda x: len(x["name"]))["name"]
        best_conf = max(g["confidence"] for g in group)

        merged.append({
            "name": best_name,
            "role": group[0]["role"],
            "confidence": best_conf
        })

    return merged


# --------------------------------------------------
# Extract Endpoint
# --------------------------------------------------
@app.post("/extract")
async def extract_entities(pdf: UploadFile = File(...)):
    try:
        pdf_bytes = await pdf.read()

        # Hybrid Text Extraction
        full_text = ""

        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        if not full_text.strip():
            images = convert_from_bytes(pdf_bytes, dpi=200)
            for img in images:
                full_text += pytesseract.image_to_string(
                    img, config="--oem 3 --psm 6"
                ) + "\n"

        if not full_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text")

        doc = nlp(full_text)

        response = {
            "dates": [],
            "contract_value": None,
            "advance_payment": [],
            "other_amounts": [],
            "parties": []
        }

        # Date Extraction
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b'
        ]

        for sent in doc.sents:
            for pattern in date_patterns:
                for d in re.findall(pattern, sent.text):
                    iso = normalize_date(d)
                    if iso:
                        response["dates"].append({
                            "date": iso,
                            "context": classify_date_context(sent.text)
                        })

        # Amount Extraction
        amount_pattern = r'(\$?\d[\d,]+(?:\.\d{2})?)'

        for sent in doc.sents:
            matches = re.findall(amount_pattern, sent.text)

            for amt in matches:
                normalized = normalize_amount(amt)
                if not normalized:
                    continue

                lower = sent.text.lower()

                if "total contract value" in lower:
                    response["contract_value"] = normalized
                elif "advance payment" in lower:
                    response["advance_payment"].append(normalized)
                else:
                    response["other_amounts"].append(normalized)

        # Party Extraction
        party_candidates = []

        for ent in doc.ents:
            if ent.label_ in ["ORG", "PARTY"]:
                party_candidates.append(ent.text)

        between_matches = re.findall(
            r'between\s+(.*?)\s+and\s+(.*?)[\.,\n]',
            full_text,
            flags=re.IGNORECASE
        )

        for match in between_matches:
            party_candidates.extend(match)

        company_pattern = r'\b[A-Z][A-Za-z&,\.\s]+(?:Inc|Corp|LLC|Ltd|Limited|Company|Corporation)\b'
        party_candidates.extend(re.findall(company_pattern, full_text))

        cleaned = []
        seen = set()

        for p in party_candidates:
            p = re.sub(r'\s+', ' ', p).strip()
            p = re.sub(r'^[^A-Za-z]+', '', p)
            p = re.sub(r'[^A-Za-z\.,& ]+$', '', p)

            if len(p) < 4:
                continue

            if p not in seen:
                seen.add(p)
                cleaned.append(p)

        advanced_parties = []

        for name in cleaned:
            role = classify_party_role(name, full_text)
            confidence = 0.92 if role != "Contracting Party" else 0.85

            advanced_parties.append({
                "name": name,
                "role": role,
                "confidence": confidence
            })

        response["parties"] = merge_similar_companies(advanced_parties)

        return response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)

