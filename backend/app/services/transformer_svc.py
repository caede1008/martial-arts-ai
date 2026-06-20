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

    return {
        "category": top_category,
        "score":    round(top_score, 3),
        "all":      dict(zip(result["labels"], [round(s, 3) for s in result["scores"]])),
    }


def build_context(category: str, analysis_data: dict) -> str:
    """カテゴリに応じて参照するデータを選ぶ"""

    scores     = analysis_data.get("scores", {})
    cnn_result = analysis_data.get("cnn_result", {})
    analysis   = analysis_data.get("analysis", "")

    if category == "トレーニング方法":
        return f"""
【骨格スコア】
- リーチ比率: {scores.get('reach_ratio')}
- スタンス幅: {scores.get('stance_ratio')}
- 重心の高さ: {scores.get('center_y')}

【分析レポートより】
{analysis[:500]}
"""

    elif category == "分析結果の説明":
        cnn_scores = cnn_result.get("scores", {})
        return f"""
【CNN競技適性スコア】
- BJJ（柔術）:  {cnn_scores.get('bjj', 0):.1%}
- ボクシング:   {cnn_scores.get('boxing', 0):.1%}
- ムエタイ:     {cnn_scores.get('muaythai', 0):.1%}
- レスリング:   {cnn_scores.get('wrestling', 0):.1%}
- 最高適性:     {cnn_result.get('top_class')}

【骨格スコア】
- リーチ比率: {scores.get('reach_ratio')}
- スタンス幅: {scores.get('stance_ratio')}
- 重心の高さ: {scores.get('center_y')}
"""

    elif category == "ロールモデルとの比較":
        return f"""
【分析レポートより（ロールモデル情報含む）】
{analysis}
"""

    elif category == "試合戦略":
        cnn_scores = cnn_result.get("scores", {})
        return f"""
【競技適性スコア】
- BJJ（柔術）:  {cnn_scores.get('bjj', 0):.1%}
- ボクシング:   {cnn_scores.get('boxing', 0):.1%}
- ムエタイ:     {cnn_scores.get('muaythai', 0):.1%}
- レスリング:   {cnn_scores.get('wrestling', 0):.1%}

【骨格スコア】
- リーチ比率: {scores.get('reach_ratio')}
- スタンス幅: {scores.get('stance_ratio')}
- 重心の高さ: {scores.get('center_y')}

【分析レポートより】
{analysis[:500]}
"""

    else:
        # その他・分類外 → 全データを渡す
        cnn_scores = cnn_result.get("scores", {})
        return f"""
【骨格スコア】
- リーチ比率: {scores.get('reach_ratio')}
- スタンス幅: {scores.get('stance_ratio')}
- 重心の高さ: {scores.get('center_y')}

【CNN競技適性スコア】
- BJJ（柔術）:  {cnn_scores.get('bjj', 0):.1%}
- ボクシング:   {cnn_scores.get('boxing', 0):.1%}
- ムエタイ:     {cnn_scores.get('muaythai', 0):.1%}
- レスリング:   {cnn_scores.get('wrestling', 0):.1%}

【分析レポートより】
{analysis[:800]}
"""