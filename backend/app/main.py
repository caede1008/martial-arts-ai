from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import anthropic
import os
from dotenv import load_dotenv
from app.services import vector_store
from app.services.rag_svc import retrieve_similar_fighters

load_dotenv()

@asynccontextmanager
async def lifespan(app):
    vector_store.init()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...),
    height: float = Form(0),
    weight: float = Form(0),
    age: int = Form(0),
    background: str = Form(""),
    strong_move: str = Form(""),
):
    # 画像をバイトデータとして読み込む
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # MediaPipeで骨格解析
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(base_options=base_options)

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        results = landmarker.detect(mp_image)

    if not results.pose_landmarks:
        return {"error": "骨格を検出できませんでした。全身が映った画像を使ってください。"}

    lm = results.pose_landmarks[0]

    reach = abs(lm[15].x - lm[16].x)
    stance = abs(lm[27].x - lm[28].x)
    center_y = (lm[11].y + lm[12].y) / 2

    scores = {
        "reach_ratio": round(reach, 3),
        "stance_ratio": round(stance, 3),
        "center_y": round(center_y, 3),
    }

    # RAGで類似選手を取得
    fighter_context = retrieve_similar_fighters(scores, background)

    # Claude APIで分析文を生成
    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""あなたは格闘技の専門コーチです。
以下の情報をもとに格闘技の適性を分析してください。

【基礎データ】
- 身長: {height}cm
- 体重: {weight}kg
- 年齢: {age}歳
- バックボーン: {background if background else "未入力"}
- 得意技: {strong_move if strong_move else "未入力"}

【骨格スコア】
- リーチ比率: {scores['reach_ratio']}（0〜1、高いほどリーチが長い）
- スタンス幅: {scores['stance_ratio']}（0〜1、高いほどスタンスが広い）
- 重心の高さ: {scores['center_y']}（0〜1、低いほど重心が高い位置）

## 参考選手情報（データベースより取得）
{fighter_context}

以下の項目を日本語で簡潔に答えてください。
1. 強み
2. 弱点
3. 適したファイタータイプ
4. 改善ポイント（3つ）
5. ロールモデルにすべき有名選手（1名、理由も・必ず上記参考選手から選ぶこと）"""
            }
        ]
    )

    analysis = message.content[0].text

    return {
        "filename": image.filename,
        "scores": scores,
        "analysis": analysis,
        "message": "分析完了"
    }