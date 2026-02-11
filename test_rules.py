from date_rules import normalize_date
from money_rules import normalize_amount
from validator import validate_contract

def test_date():
    assert normalize_date("April 6, 2007") == "2007-04-06"

def test_amount():
    result = normalize_amount("INR 5,000")
    assert result["amount"] == 5000.0

def test_validation():
    valid, msg = validate_contract({
        "effective_date": "2007-04-06",
        "termination_date": "2008-01-01"
    })
    assert valid is True

print("All rule-based tests passed")
