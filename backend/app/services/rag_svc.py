from app.services.vector_store import search


def retrieve_similar_fighters(scores: dict, background: str = "") -> str:
    """
    スコアから検索クエリを生成し、類似選手の文書を返す
    """
    parts = []

    # リーチで判断
    if scores.get("reach_ratio", 0) > 0.5:
        parts.append("リーチが長くアウトサイドスタイルに適した")
    else:
        parts.append("コンパクトなビルドでインファイターに向いた")

    # スタンス幅で判断
    if scores.get("stance_ratio", 0) > 0.2:
        parts.append("安定したスタンスの")
    else:
        parts.append("機動力重視の")

    # バックボーンで判断
    if background:
        if any(w in background for w in ["柔道", "レスリング", "柔術"]):
            parts.append("グラップリングベースの")
        elif any(w in background for w in ["ボクシング", "キック", "空手", "テコンドー"]):
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