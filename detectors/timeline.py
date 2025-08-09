import re
from dateutil.parser import parse as dtparse

def extract_dates(text):
    dates = []
    for m in re.finditer(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|20\d{2})\b", text, re.I):
        raw = m.group(0)
        try:
            dt = dtparse(raw, fuzzy=True)
            dates.append(dt.date().isoformat())
        except Exception:
            pass
    return dates

def find_timeline_conflicts(slides):
    return []
