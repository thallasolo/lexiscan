import re

def normalize_amount(text):
    """
    Extract numeric value and currency
    """
    pattern = r"(INR|USD|Rs\.?|₹|\$)\s?([\d,]+)"
    match = re.search(pattern, text)

    if not match:
        return None

    currency = match.group(1)
    value = match.group(2).replace(",", "")

    return {
        "currency": currency,
        "amount": float(value)
    }
