from fastapi import APIRouter
from pydantic import BaseModel
from app.services import transformer_svc
import anthropic
import os

router = APIRouter()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ChatRequest(BaseModel):
    question: str
    analysis_data: dict


class ChatResponse(BaseModel):
    answer: str
    category: str
    category_score: float


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


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):

    # Transformerで質問を分類
    classification = transformer_svc.classify_question(req.question)
    category       = classification["category"]
    category_score = classification["score"]

    print(f"📝 質問: {req.question}")
    print(f"🏷️  カテゴリ: {category}（{category_score:.1%}）")

    # カテゴリに応じて参照データを選ぶ
    context = build_context(category, req.analysis_data)

    # Claude APIで回答生成
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""あなたは格闘技の専門コーチです。
以下のユーザーデータをもとに質問に答えてください。

{context}

【質問】
{req.question}

日本語で具体的に答えてください。"""
            }
        ]
    )

    answer = message.content[0].text

    return ChatResponse(
        answer=answer,
        category=category,
        category_score=category_score,
    )