"""
Baseline Entity Extraction using Regex and TF-IDF
This is NOT the production model.
Used for comparison with NER-based approach.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer


def extract_dates(text: str):
    """
    Extract dates using regex patterns
    """
    date_pattern = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b"
    return re.findall(date_pattern, text)


def extract_amounts(text: str):
    """
    Extract monetary values using regex
    """
    amount_pattern = r"(?:INR|Rs\.?|\$)\s?\d+(?:,\d+)*(?:\.\d+)?"
    return re.findall(amount_pattern, text)


def tfidf_keywords(text: str, top_k=5):
    """
    Extract top keywords using TF-IDF
    (Demonstration purpose only)
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([text])
    scores = tfidf.toarray()[0]

    keywords = sorted(
        zip(vectorizer.get_feature_names_out(), scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [word for word, score in keywords[:top_k]]


if __name__ == "__main__":
    sample_text = """
    This Affiliate Agreement is entered into on April 6, 2007.
    The Company agrees to pay INR 5,000 to the Affiliate.
    """

    print("DATES:", extract_dates(sample_text))
    print("AMOUNTS:", extract_amounts(sample_text))
    print("TF-IDF KEYWORDS:", tfidf_keywords(sample_text))
