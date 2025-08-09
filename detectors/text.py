import re

ANTONYM_PAIRS = [
    ("few competitors", "highly competitive"),
    ("fragmented market", "consolidated market"),
    ("monopoly", "many players"),
    ("low risk", "high risk"),
    ("slow growth", "hypergrowth"),
]

def find_textual_contradictions(slides):
    text_map = {s["slide"]: (s["text"] or "").lower() for s in slides}
    issues = []

    for a, b in ANTONYM_PAIRS:
        hits_a = [sl for sl, t in text_map.items() if a in t]
        hits_b = [sl for sl, t in text_map.items() if b in t]
        if hits_a and hits_b:
            issues.append({
                "type":"text","severity":"medium",
                "slides": sorted(set(hits_a + hits_b)),
                "message": f"Potential contradiction: '{a}' vs '{b}'."
            })

    speeds = []
    for sl, t in text_map.items():
        for m in re.finditer(r"\b(\d+)x\s+faster\b", t):
            speeds.append((sl, int(m.group(1))))
    if len({v for _, v in speeds}) > 1:
        issues.append({
            "type":"text","severity":"medium",
            "slides": sorted({sl for sl,_ in speeds}),
            "message": "Conflicting acceleration claims: " +
                       ", ".join([f"slide {sl}: {v}x faster" for sl,v in speeds])
        })
    return issues
