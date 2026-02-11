from datetime import datetime

def validate_contract(dates):
    """
    dates = {
        "effective_date": "2007-04-06",
        "termination_date": "2006-12-31"
    }
    """

    eff = datetime.fromisoformat(dates["effective_date"])
    term = datetime.fromisoformat(dates["termination_date"])

    if term < eff:
        return False, "Termination date cannot precede effective date"

    return True, "Dates are valid"
