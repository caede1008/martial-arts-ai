import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# 日本語対応・軽量モデル
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
DATA_PATH = Path(__file__).parent.parent.parent.parent / "ml/fighter_profiles/fighters.json"

_client = chromadb.Client()
_embedder = SentenceTransformer(MODEL_NAME)
_collection = None


def _build_document(fighter: dict) -> str:
    """選手データを検索用テキストに変換"""
    return (
        f"{fighter['name']}は{fighter['style']}スタイルの格闘家。"
        f"体型は{fighter['build']}でリーチ{fighter['reach_cm']}cm、"
        f"身長{fighter['height_cm']}cm。"
        f"強み: {', '.join(fighter['strengths'])}。"
        f"{fighter['description']}"
    )


def init():
    """アプリ起動時に1回だけ呼ぶ"""
    global _collection
    fighters = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    _collection = _client.get_or_create_collection("fighters")

    if _collection.count() > 0:
        return

    docs = [_build_document(f) for f in fighters]
    ids = [f["id"] for f in fighters]
    metadatas = [{"name": f["name"], "style": f["style"],
                  "reach_cm": f["reach_cm"]} for f in fighters]

    _collection.add(
        documents=docs,
        embeddings=_embedder.encode(docs).tolist(),
        ids=ids,
        metadatas=metadatas,
    )
    print(f"✅ ベクトルDB初期化完了: {len(fighters)}名の選手を登録")


def search(query_text: str, n_results: int = 3) -> list[dict]:
    """クエリに最も近い選手をTop-N返す"""
    query_vec = _embedder.encode([query_text]).tolist()
    results = _collection.query(query_embeddings=query_vec, n_results=n_results)

    return [
        {"document": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]