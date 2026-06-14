import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
from pathlib import Path

CLASSES    = ["bjj", "boxing", "muaythai", "wrestling"]
MODEL_PATH = Path(__file__).parent.parent.parent.parent / "ml/models/fighter_cnn_v1.pt"
IMG_SIZE   = 224

_model = None

def _load_model():
    """モデルを起動時に1回だけ読み込む"""
    global _model
    if _model is not None:
        return _model

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    _model = model
    print("✅ CNNモデル読み込み完了")
    return _model

_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

def predict(image_bytes: bytes) -> dict:
    """画像バイトデータから競技適性スコアを返す"""
    model = _load_model()

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = _transform(img).unsqueeze(0)

    with torch.no_grad():
        output = torch.sigmoid(model(tensor))

    scores = {cls: round(float(score), 3)
              for cls, score in zip(CLASSES, output[0])}

    # 最も高いスコアの競技
    top_class = max(scores, key=scores.get)

    return {
        "scores": scores,
        "top_class": top_class,
        "top_score": scores[top_class],
    }