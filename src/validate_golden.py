import csv
import json
import re
from pathlib import Path

DATA_DIR = Path("/content/drive/MyDrive/plantation-rag/data")


def norm(s):
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


pages = {}
for f in (DATA_DIR / "parsed_clean").glob("*.json"):
    for r in json.load(open(f)):
        if r["printed_page"]:
            pages[(r["company"], r["printed_page"])] = norm(r["text"])

rows = list(csv.DictReader(open("eval/golden_set.csv", encoding="utf-8")))
bad = 0
for row in rows:
    ok = True
    for p in str(row["pages"]).split(";"):
        text = pages.get((row["company"], int(p)))
        if text is None or norm(row["evidence"]) not in text:
            ok = False
    print("OK     " if ok else "PROBLEM", row["id"], row["company"], "p.", row["pages"], "|", row["question"][:60])
    bad += not ok
print(f"\n{len(rows) - bad}/{len(rows)} rows verified")
