import re

def normalize_numbers(text):
    if not text:
        return []
    m = re.findall(r"\$?\d+\.?\d*\s*(?:[kKmMbB%]|hours?|hrs?|mins?|min|m|x)?", text)
    return [t.strip() for t in m if t.strip()]
