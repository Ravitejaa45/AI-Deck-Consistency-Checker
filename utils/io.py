import os, json

def ensure_outdir():
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/thumbs", exist_ok=True)

def write_reports(issues, slides_meta):
    ensure_outdir()
    with open("out/report.json","w") as f:
        json.dump({"issues": issues, "slides": slides_meta}, f, indent=2)

    lines = ["# Consistency Report", ""]
    if not issues:
        lines += ["No issues found by heuristics/LLM."]
    else:
        for i, iss in enumerate(issues, 1):
            lines += [
                f"## Issue {i}",
                f"- **Type:** {iss.get('type')}",
                f"- **Severity:** {iss.get('severity')}",
                f"- **Slides:** {', '.join(map(str, iss.get('slides', [])))}",
                f"- **Details:** {iss.get('message','')}",
                ""
            ]
    with open("out/report.md","w") as f:
        f.write("\n".join(lines))

def to_abs(p):
    return os.path.abspath(p)
