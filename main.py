import argparse
import os
import re
from rapidfuzz import fuzz

from utils.io import write_reports, ensure_outdir, to_abs
from detectors.numeric import find_conflicting_metrics
from detectors.text import find_textual_contradictions
from detectors.timeline import find_timeline_conflicts
from utils.text_norm import normalize_numbers
from llm_client import check_contradictions_with_llm


def load_slides(args):
    if args.parser == "docling":
        from extractor_docling import extract_with_docling as extract_from_pptx
    elif args.parser == "pptx":
        from extractor_pptx import extract_from_pptx
    else:
        raise SystemExit("--parser must be 'docling' or 'pptx'")

    slides = []
    if args.pptx:
        slides = extract_from_pptx(args.pptx)

    if args.images_dir:
        import glob
        imgs = []
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            imgs.extend(glob.glob(os.path.join(args.images_dir, ext)))
        base = len(slides)
        for i, p in enumerate(sorted(imgs), start=1):
            slides.append({
                "slide": base + i,
                "text": "",
                "images": [to_abs(p)]
            })
    return slides


def _sig(item):
    return (item.get("type"), tuple(sorted(item.get("slides", []))))


def _normalize_msg(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9%\s\.\$x]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("contradiction", "conflict")
    s = s.replace("inconsistency", "conflict")
    s = s.replace(" mins", "min").replace(" minutes", "min").replace(" hours", "h")
    s = s.replace("$ ", "$")
    return s


def _merge_issues(issues):
    sev_rank = {"low": 0, "medium": 1, "high": 2}
    merged = []

    for cand in issues:
        cand["message_norm"] = _normalize_msg(cand.get("message", ""))
        did_merge = False

        for kept in merged:
            if _sig(cand) != _sig(kept):
                continue

            sim = fuzz.token_set_ratio(cand["message_norm"], kept["message_norm"])

            if kept.get("type") == "numeric" and cand.get("type") == "numeric":
                nums_k = re.findall(r"\$?\d+(?:\.\d+)?\s*[mkb%]?", kept["message_norm"])
                nums_c = re.findall(r"\$?\d+(?:\.\d+)?\s*[mkb%]?", cand["message_norm"])
                if set(nums_k) == set(nums_c) and set(nums_k):
                    sim = 100

            if sim >= 80:
                if sev_rank.get(cand.get("severity", "low"), 0) > sev_rank.get(kept.get("severity", "low"), 0):
                    kept["severity"] = cand.get("severity", "low")
                if kept.get("origin") == "rules" and cand.get("origin") == "llm":
                    kept["message"] = cand.get("message", "")
                    kept["message_norm"] = cand["message_norm"]
                    kept["origin"] = "llm"

                did_merge = True
                break

        if not did_merge:
            merged.append(cand)

    for it in merged:
        it.pop("message_norm", None)
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", type=str, help="Path to .pptx")
    ap.add_argument("--images_dir", type=str, help="Folder with slide images")
    ap.add_argument("--parser", type=str, default="docling",
                    choices=["docling", "pptx"], help="Extractor to use")
    ap.add_argument("--no_llm", action="store_true", help="Disable Gemini pass")
    args = ap.parse_args()

    ensure_outdir()

    slides = load_slides(args)
    if not slides:
        raise SystemExit("No input: provide --pptx and/or --images_dir.")

    issues = []
    issues += find_conflicting_metrics(slides)
    issues += find_textual_contradictions(slides)
    issues += find_timeline_conflicts(slides)

    for it in issues:
        it.setdefault("origin", "rules")

    if not args.no_llm:
        smini = []
        for s in slides:
            smini.append({
                "slide": s["slide"],
                "text": (s["text"][:1600] if s["text"] else ""),
                "numbers": normalize_numbers(s["text"]) if s["text"] else [],
                "image_paths": s.get("images", []),
            })
        try:
            llm_issues = check_contradictions_with_llm(smini)
            for it in llm_issues:
                it.setdefault("origin", "llm")
            issues.extend(llm_issues)
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "slides": [],
                "message": f"LLM cross-check failed: {e}",
                "origin": "system"
            })

    issues = _merge_issues(issues)

    write_reports(
        issues,
        [{"slide": s["slide"],
          "text_len": len(s["text"] or ""),
          "images": len(s.get("images", []))}
         for s in slides]
    )

    print(f"Found {len(issues)} issues. See out/report.json and out/report.md")


if __name__ == "__main__":
    main()
