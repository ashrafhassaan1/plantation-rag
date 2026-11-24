import json
import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("/content/drive/MyDrive/plantation-rag/data")
target = int(sys.argv[1]) if len(sys.argv) > 1 else 1200

chunks = json.load(open(DATA_DIR / "chunks" / f"chunks_{target}.json"))
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = chromadb.PersistentClient(path=str(DATA_DIR / "chroma"))

name = f"chunks_{target}"
try:
    client.delete_collection(name)      # rebuild from scratch each time
except Exception:
    pass
col = client.create_collection(name, metadata={"hnsw:space": "cosine"})

B = 128
for i in range(0, len(chunks), B):
    batch = chunks[i:i + B]
    embs = model.encode([c["text"] for c in batch], normalize_embeddings=True,
                        show_progress_bar=False)
    col.add(
        ids=[c["id"] for c in batch],
        embeddings=embs.tolist(),
        documents=[c["text"] for c in batch],
        metadatas=[{"company": c["company"], "page_start": c["page_start"],
                    "page_end": c["page_end"]} for c in batch],
    )
    print(f"indexed {min(i + B, len(chunks))}/{len(chunks)}")
print("done. collection:", name, "| size:", col.count())
