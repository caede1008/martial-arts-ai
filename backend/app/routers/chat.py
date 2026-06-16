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


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):

    # Transformerで質問を分類
    classification = transformer_svc.classify_question(req.question)
    category       = classification["category"]
    category_score = classification["score"]

    print(f"📝 質問: {req.question}")
    print(f"🏷️  カテゴリ: {category}（{category_score:.1%}）")

    # カテゴリに応じて参照データを選ぶ
    context = transformer_svc.build_context(category, req.analysis_data)

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