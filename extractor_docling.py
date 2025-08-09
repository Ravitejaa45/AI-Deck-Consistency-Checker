from pathlib import Path
from collections import defaultdict
from docling.document_converter import DocumentConverter

def extract_with_docling(pptx_path: str):
    converter = DocumentConverter()
    result = converter.convert(Path(pptx_path))
    doc = result.document

    texts_by_page = defaultdict(list)
    images_by_page = defaultdict(list)

    for t in getattr(doc, "texts", []) or []:
        prov = getattr(t, "prov", []) or []
        page_nos = sorted({getattr(p, "page_no", None) for p in prov if getattr(p, "page_no", None)})
        for pn in page_nos:
            txt = (getattr(t, "text", "") or "").strip()
            if txt:
                texts_by_page[pn].append(txt)

    thumbs = Path("out/thumbs")
    thumbs.mkdir(parents=True, exist_ok=True)
    for pic in getattr(doc, "pictures", []) or []:
        prov = getattr(pic, "prov", []) or []
        page_nos = sorted({getattr(p, "page_no", None) for p in prov if getattr(p, "page_no", None)})
        img = getattr(pic, "image", None)
        data = getattr(img, "data", None) if img else None
        for pn in page_nos:
            if data:
                outp = thumbs / f"slide{pn}_{len(images_by_page[pn])+1}.png"
                outp.write_bytes(data)
                images_by_page[pn].append(str(outp))

    num_pages = getattr(doc, "num_pages", None)
    if callable(num_pages):
        num_pages = num_pages()
    if not num_pages:
        pages_obj = getattr(doc, "pages", None)
        if pages_obj is not None:
            try:
                num_pages = len(pages_obj)
            except Exception:
                num_pages = None
    if not num_pages:
        all_pns = set(texts_by_page.keys()) | set(images_by_page.keys())
        num_pages = max(all_pns) if all_pns else 1

    slides = []
    for pn in range(1, int(num_pages) + 1):
        txt = "\n".join(texts_by_page.get(pn, []))
        imgs = images_by_page.get(pn, [])
        slides.append({"slide": pn, "text": txt, "images": imgs})

    return slides
