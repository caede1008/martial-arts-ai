from transformers import pipeline

CATEGORIES = [
    "トレーニング方法",
    "分析結果の説明",
    "ロールモデルとの比較",
    "試合戦略",
    "その他",
]

_classifier = None


def _load_classifier():
    """モデルを起動時に1回だけ読み込む"""
    global _classifier
    if _classifier is not None:
        return _classifier

    print("🤖 Transformerモデル読み込み中...")
    _classifier = pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-deberta-v3-small",
    )
    print("✅ Transformerモデル読み込み完了")
    return _classifier


def classify_question(question: str) -> dict:
    """質問をカテゴリに分類する"""
    classifier = _load_classifier()

    result = classifier(
        question,
        candidate_labels=CATEGORIES,
    )

    top_category = result["labels"][0]
    top_score    = result["scores"][0]

    # スコアが低い場合は「その他」に強制分類
    if top_score < 0.3:
        top_category = "その他"

    return {
        "category": top_category,
        "score":    round(top_score, 3),
        "all":      dict(zip(result["labels"], [round(s, 3) for s in result["scores"]])),
    }