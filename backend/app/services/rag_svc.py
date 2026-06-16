from app.services.vector_store import search
def retrieve_similar_fighters(scores: dict, background: str = "", cnn_result: dict = None) -> str:

    parts = []

    # リーチで判断（従来通り）
    if scores.get("reach_ratio", 0) > 0.5:
        parts.append("リーチが長くアウトサイドスタイルに適した")
    else:
        parts.append("コンパクトなビルドでインファイターに向いた")

    # CNNの結果を追加（新規）
    if cnn_result:
        cnn_scores = cnn_result["scores"]
        top_class  = cnn_result["top_class"]

        # 上位2競技を検索クエリに追加
        sorted_sports = sorted(cnn_scores.items(), key=lambda x: x[1], reverse=True)
        top2 = [s[0] for s in sorted_sports[:2]]

        sport_map = {
            "bjj":       "グラップリング・柔術",
            "boxing":    "ボクシング・打撃",
            "muaythai":  "ムエタイ・立ち技",
            "wrestling": "レスリング・組み技",
        }

        parts.append(f"{sport_map[top2[0]]}と{sport_map[top2[1]]}の適性が高い")

    # バックボーンで判断（従来通り）
    if background:
        if any(w in background for w in ["柔道", "レスリング", "柔術"]):
            parts.append("グラップリングベースの")
        elif any(w in background for w in ["ボクシング", "キック", "空手"]):
            parts.append("打撃ベースの")

    parts.append("格闘家")
    query = "".join(parts)

    results = search(query, n_results=3)

    context_lines = []
    for i, r in enumerate(results, 1):
        context_lines.append(
            f"【参考選手{i}: {r['metadata']['name']}】\n{r['document']}"
        )

    return "\n\n".join(context_lines)