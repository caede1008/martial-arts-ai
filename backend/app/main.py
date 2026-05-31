from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # OpenCVのBGRをRGBに変換
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # MediaPipe新APIで骨格解析
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(base_options=base_options)

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        results = landmarker.detect(mp_image)

    if not results.pose_landmarks:
        return {"error": "骨格を検出できませんでした。全身が映った画像を使ってください。"}

    lm = results.pose_landmarks[0]

    # リーチ：左手首(15)〜右手首(16)
    reach = abs(lm[15].x - lm[16].x)
    # スタンス幅：左足首(27)〜右足首(28)
    stance = abs(lm[27].x - lm[28].x)
    # 重心：両肩(11,12)の中点Y
    center_y = (lm[11].y + lm[12].y) / 2

    return {
        "filename": image.filename,
        "reach_ratio": round(reach, 3),
        "stance_ratio": round(stance, 3),
        "center_y": round(center_y, 3),
        "message": "骨格解析成功"
    }