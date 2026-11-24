import json
import sys
from pathlib import Path

DATA_DIR = Path("/content/drive/MyDrive/plantation-rag/data")
CLEAN = DATA_DIR / "parsed_clean"
CHUNKS = DATA_DIR / "chunks"
CHUNKS.mkdir(parents=True, exist_ok=True)


def chunk_company(records, target=1200, overlap=150):
    company = records[0]["company"]
    chunks, buf, fresh, prev_page = [], [], 0, None

    def size():
        return sum(len(line) + 1 for _, line in buf)

    def flush():
        text = "\n".join(line for _, line in buf).strip()
        if fresh and len(text) >= 50:
            pages = [p for p, _ in buf]
            chunks.append({"company": company, "page_start": min(pages),
                           "page_end": max(pages), "text": text})

    for r in records:
        if not r["keep"]:
            continue
        # a gap in kept pages (a skipped section) ends the current chunk
        if prev_page is not None and r["printed_page"] - prev_page > 1:
            flush()
            buf, fresh = [], 0
        prev_page = r["printed_page"]
        for line in r["text"].split("\n"):
            line = line.strip()
            if not line:
                continue
            buf.append((r["printed_page"], line))
            fresh += 1
            if size() >= target:
                flush()
                tail, s = [], 0
                for item in reversed(buf):       # keep the last ~overlap characters
                    tail.insert(0, item)
                    s += len(item[1]) + 1
                    if s >= overlap:
                        break
                buf, fresh = tail, 0
    flush()
    for n, c in enumerate(chunks):
        c["id"] = f"{company}_{n:05d}"
    return chunks


if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    all_chunks = []
    for f in sorted(CLEAN.glob("*.json")):
        records = json.load(open(f))
        cs = chunk_company(records, target=target)
        avg = sum(len(c["text"]) for c in cs) // max(len(cs), 1)
        print(f"{f.stem}: {len(cs)} chunks, average {avg} characters")
        all_chunks += cs
    out = CHUNKS / f"chunks_{target}.json"
    out.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", out, "| total chunks:", len(all_chunks))
