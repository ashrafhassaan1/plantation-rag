import json
from pathlib import Path
import fitz  # PyMuPDF

DATA_DIR = Path("/content/drive/MyDrive/plantation-rag/data")
RAW = DATA_DIR / "raw"
OUT = DATA_DIR / "parsed"
OUT.mkdir(parents=True, exist_ok=True)


def parse_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append({
            "company": pdf_path.stem,
            "page": page_number,
            "text": text,
        })
    return pages


for pdf in sorted(RAW.glob("*.pdf")):
    pages = parse_pdf(pdf)
    out_file = OUT / f"{pdf.stem}.json"
    out_file.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
    nearly_empty = sum(1 for p in pages if len(p["text"].strip()) < 50)
    print(f"{pdf.name}: {len(pages)} pages, {nearly_empty} nearly empty")
