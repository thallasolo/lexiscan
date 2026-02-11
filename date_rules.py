from datetime import datetime

def normalize_date(date_text):
    """
    Converts date into ISO 8601 format (YYYY-MM-DD)
    """
    possible_formats = [
        "%B %d, %Y",    # April 6, 2007
        "%d %B %Y",     # 6 April 2007
        "%m/%d/%Y",     # 04/06/2007
        "%d-%m-%Y"      # 06-04-2007
    ]

    for fmt in possible_formats:
        try:
            parsed = datetime.strptime(date_text, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None  # unrecognized format
