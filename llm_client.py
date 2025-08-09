import os, json, re, math
from dotenv import load_dotenv
import google.generativeai as genai

MODEL_NAME = "gemini-2.5-flash"

def _configure():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set (in .env or environment)")
    genai.configure(api_key=key)

def _upload_images(paths):
    files = []
    for p in paths:
        try:
            f = genai.upload_file(p)
            files.append(f)
        except Exception:
            pass
    return files

def check_contradictions_with_llm(slide_snippets):
    _configure()
    model = genai.GenerativeModel(MODEL_NAME)

    all_imgs = []
    for s in slide_snippets:
        all_imgs.extend([(s["slide"], ip) for ip in s.get("image_paths", [])])
    all_imgs = all_imgs[:12]
    uploaded = _upload_images([ip for _, ip in all_imgs])

    header = (
        "You are a consistency checker for slide decks.\n"
        "Identify contradictions in numbers (money, time, %, totals), text claims"
        "(e.g., 'few competitors' vs 'highly competitive'), and timeline conflicts.\n"
        "Cite slide numbers and quote conflicting values/phrases.\n"
        "Return ONLY a JSON array with items of shape:\n"
        "{type:'numeric'|'text'|'timeline', severity:'high'|'medium'|'low', slides:[int], message:str}\n"
    )

    parts = [header]
    for s in slide_snippets:
        desc = {
            "slide": s["slide"],
            "text": s.get("text",""),
            "numbers": s.get("numbers", []),
        }
        parts.append(json.dumps(desc)[:4000])

    parts.extend(uploaded)

    resp = model.generate_content(parts)
    text = getattr(resp, "text", "[]")
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except Exception:
        return []
