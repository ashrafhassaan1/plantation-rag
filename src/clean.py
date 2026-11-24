import json
from collections import Counter
from pathlib import Path
import pymupdf

DATA_DIR = Path("/content/drive/MyDrive/plantation-rag/data")
RAW = DATA_DIR / "raw"
OUT = DATA_DIR / "parsed_clean"
OUT.mkdir(parents=True, exist_ok=True)

# printed-page ranges worth keeping, taken from each report's contents page
KEEP = {
    "ioi_2025": [(8, 15), (18, 27), (30, 65), (66, 86), (88, 144), (148, 273)],
    "klk_2025": [(2, 108), (111, 134), (136, 241), (247, 254)],
    "sdguthrie_2025": [(2, 14), (18, 61), (64, 66), (69, 102), (103, 222), (226, 230)],
}

# the navigation menu that IOI repeats on its financial pages (exact line sequence)
IOI_NAV = ["Group", "Overview", "Key", "Messages", "Strategic Value", "Creation",
           "Strategic", "Progress", "Performance", "Review", "Additional",
           "Information", "Governance", "Financial", "Report", "Annual Report",
           "2025", "IOI CORPORATION", "BERHAD"]


def remove_block(lines, block):
    n, out, i = len(block), [], 0
    while i < len(lines):
        if [l.strip() for l in lines[i:i + n]] == block:
            i += n
        else:
            out.append(lines[i])
            i += 1
    return out


def clean_text(text):
    lines = remove_block(text.split("\n"), IOI_NAV)
    out = []
    for line in lines:
        s = line.strip()
        # drop immediately repeated long lines (the triple "Our Key Stakeholder Groups")
        if out and s == out[-1].strip() and len(s) > 15:
            continue
        out.append(line)
    return "\n".join(out).strip()


def build_units(doc):
    """One unit per printed page: a spread gives two units, a normal page gives one."""
    units, k = [], 0
    for pno, page in enumerate(doc, start=1):
        r = page.rect
        if r.width > r.height * 1.2:
            mid = r.x0 + r.width / 2
            halves = [("left", pymupdf.Rect(r.x0, r.y0, mid, r.y1)),
                      ("right", pymupdf.Rect(mid, r.y0, r.x1, r.y1))]
        else:
            halves = [("single", r)]
        for side, rect in halves:
            units.append({"pdf_page": pno, "side": side, "rect": rect, "k": k})
            k += 1
    return units


def edge_numbers(page, rect):
    """All 1-3 digit numbers in the top or bottom 10% of this page area."""
    band = 0.10 * rect.height
    nums = set()
    for x0, y0, x1, y1, word, *_ in page.get_text("words", clip=rect):
        if word.isdigit() and len(word) <= 3:
            if y0 < rect.y0 + band or y0 > rect.y1 - band:
                nums.add(int(word))
    return nums


def decide(company, printed, text):
    if printed is None:
        return False, "front matter"
    if len(text) < 200:
        return False, "almost no text"
    ranges = KEEP.get(company, [(1, 10**6)])
    if not any(a <= printed <= b for a, b in ranges):
        return False, "outside kept ranges"
    return True, ""


for pdf in sorted(RAW.glob("*.pdf")):
    company = pdf.stem
    doc = pymupdf.open(pdf)
    units = build_units(doc)

    # every page votes: (number seen at the edge) - (running page index)
    votes = Counter()
    for u in units:
        u["nums"] = edge_numbers(doc[u["pdf_page"] - 1], u["rect"])
        for v in u["nums"]:
            votes[v - u["k"]] += 1
    offset, _ = votes.most_common(1)[0]

    records, unverified = [], []
    for u in units:
        printed = u["k"] + offset
        printed = printed if printed >= 1 else None
        verified = printed in u["nums"]
        text = clean_text(doc[u["pdf_page"] - 1].get_text("text", clip=u["rect"]))
        keep, reason = decide(company, printed, text)
        if not verified:
            unverified.append((u["pdf_page"], u["side"], printed))
        records.append({
            "company": company, "pdf_page": u["pdf_page"], "side": u["side"],
            "printed_page": printed, "number_verified": verified,
            "keep": keep, "skip_reason": reason, "text": text,
        })

    (OUT / f"{company}.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
    kept = sum(r["keep"] for r in records)
    print(f"{company}: {len(doc)} PDF pages -> {len(units)} printed pages | "
          f"offset {offset:+d} | number verified on {len(units) - len(unverified)}/{len(units)} | kept {kept}")
    print("   first unverified (pdf_page, side, guessed printed):", unverified[:8])
