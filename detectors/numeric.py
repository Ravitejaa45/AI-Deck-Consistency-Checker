import re

def find_conflicting_metrics(slides):
    issues = []
    times_by_slide = {}
    for s in slides:
        tvals = []
        for m in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(?:mins?|min)\b", s["text"], re.I):
            tvals.append(float(m.group(1)))
        if tvals:
            times_by_slide[s["slide"]] = sorted(set(tvals))
    if len(times_by_slide) >= 2:
        uniq = set()
        for arr in times_by_slide.values():
            uniq |= set(arr)
        if len(uniq) > 1:
            issues.append({
                "type":"numeric","severity":"medium","slides": sorted(times_by_slide.keys()),
                "message": f"Conflicting 'minutes saved per slide' values found: {sorted(uniq)}."
            })

    money = []
    for s in slides:
        for tok in re.findall(r"\$\s*\d+(?:\.\d+)?\s*[kKmMbB]?\b", s["text"]):
            money.append((s["slide"], tok.strip()))
    if len({v.lower() for _, v in money}) > 1:
        issues.append({
            "type":"numeric","severity":"high",
            "slides": sorted({sl for sl,_ in money}),
            "message": "Conflicting impact/savings amounts across slides: " +
                       ", ".join([f"slide {sl}: {v}" for sl,v in money])
        })

    for s in slides:
        text = s["text"]
        slide_no = s["slide"]
        head = re.search(r"\b(\d+(?:\.\d+)?)\s*hours?\b", text, re.I)
        parts = [float(x) for x in re.findall(r"\b(\d+(?:\.\d+)?)\s*hours?\b", text, re.I)]
        if head and parts:
            total = float(head.group(1))
            if len(parts) > 1:
                parts_sum = sum(parts[1:])
                if parts_sum < total - 0.5:
                    issues.append({
                        "type":"numeric","severity":"high","slides":[slide_no],
                        "message": f"Headline claims {total} hours, but components sum to {parts_sum:.0f} hours."
                    })

    for s in slides:
        percents = [float(p) for p in re.findall(r"\b(\d+(?:\.\d+)?)\s*%\b", s["text"])]
        if len(percents) >= 2:
            tot = sum(percents)
            if tot > 100.5:
                issues.append({
                    "type":"numeric","severity":"medium","slides":[s["slide"]],
                    "message": f"Percent components sum to {tot:.1f}%, exceeding 100%."
                })

    for s in slides:
        t = s["text"]
        tl = t.lower()
        if "copilot" in tl and "gamma" in tl:
            def sum_near(keyword):
                total = 0.0
                patt = rf"{keyword}.{{0,120}}?(\d+(?:\.\d+)?)\s*hours?"
                for m in re.finditer(patt, tl, re.I | re.S):
                    total += float(m.group(1))
                return total
            c_sum = sum_near("copilot")
            g_sum = sum_near("gamma")
            if c_sum and g_sum and c_sum > g_sum + 0.49:
                issues.append({
                    "type":"text","severity":"low","slides":[s["slide"]],
                    "message": f"On this slide, Copilot hours (~{c_sum:g}) exceed Gamma (~{g_sum:g}); verify claim of Gamma being 'superior'."
                })

    return issues
