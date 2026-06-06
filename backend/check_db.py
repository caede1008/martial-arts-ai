import chromadb
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path

client = chromadb.Client()
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
fighters = json.loads(Path("../ml/fighter_profiles/fighters.json").read_text(encoding="utf-8"))
collection = client.get_or_create_collection("fighters")
docs = [f["name"] + "は" + f["style"] for f in fighters]
collection.add(documents=docs, embeddings=embedder.encode(docs).tolist(), ids=[f["id"] for f in fighters])

print("登録件数:", collection.count())
for item in collection.get()["documents"]:
    print("-", item)