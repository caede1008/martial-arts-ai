import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms, models
from pathlib import Path
from PIL import Image
import json

# ===== 設定 =====
DATA_DIR   = Path("ml/world_top_figter")
MODEL_DIR  = Path("ml/models")
MODEL_PATH = MODEL_DIR / "fighter_cnn_v1.pt"
CLASSES    = ["bjj", "boxing", "muaythai", "wrestling"]
BATCH_SIZE = 8
EPOCHS     = 30
LR         = 0.0005
IMG_SIZE   = 224

MODEL_DIR.mkdir(exist_ok=True)

# ===== カスタムデータセット =====
class FighterDataset(Dataset):
    def __init__(self, transform=None):
        self.samples = []
        self.transform = transform

        for i, cls in enumerate(CLASSES):
            folder = DATA_DIR / cls
            for img_path in folder.glob("*"):
                if img_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".jfif", ".webp"]:
                    # ワンホットラベル作成
                    label = [0.0] * len(CLASSES)
                    label[i] = 1.0
                    self.samples.append((img_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, torch.tensor(label, dtype=torch.float32)


# ===== データ前処理 =====
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

# ===== データセット読み込み =====
print("📂 データセット読み込み中...")
full_dataset = FighterDataset(transform=train_transform)
print(f"  総枚数: {len(full_dataset)}枚")

# 訓練8割・検証2割に分割
train_size = int(0.8 * len(full_dataset))
val_size   = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
val_dataset.dataset.transform = val_transform

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False)

print(f"  訓練: {train_size}枚 / 検証: {val_size}枚")

# ===== モデル定義（ResNet18転移学習）=====
print("\n🧠 モデル準備中...")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"  使用デバイス: {device}")
model = model.to(device)

# ===== 学習設定 =====
criterion = nn.BCEWithLogitsLoss()  # マルチラベル用
optimizer = optim.Adam(model.parameters(), lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

# ===== 学習ループ =====
print("\n🚀 学習開始!")
best_val_loss = float("inf")
history = {"train_loss": [], "val_loss": [], "val_scores": []}

for epoch in range(EPOCHS):
    # 訓練フェーズ
    model.train()
    train_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # 検証フェーズ
    model.eval()
    val_loss = 0.0
    all_outputs = []

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs  = model(images)
            loss     = criterion(outputs, labels)
            val_loss += loss.item()
            all_outputs.append(torch.sigmoid(outputs).cpu())

    train_loss_avg = train_loss / len(train_loader)
    val_loss_avg   = val_loss   / len(val_loader)

    history["train_loss"].append(round(train_loss_avg, 4))
    history["val_loss"].append(round(val_loss_avg, 4))

    print(f"  Epoch {epoch+1:2d}/{EPOCHS} | "
          f"train_loss: {train_loss_avg:.4f} | "
          f"val_loss: {val_loss_avg:.4f}")

    scheduler.step()

    # ベストモデルを保存
    if val_loss_avg < best_val_loss:
        best_val_loss = val_loss_avg
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"  ✅ モデル保存 (val_loss: {val_loss_avg:.4f})")

# ===== 結果保存 =====
with open(MODEL_DIR / "history.json", "w") as f:
    json.dump(history, f, indent=2)

print(f"\n🎉 学習完了!")
print(f"  最小検証損失: {best_val_loss:.4f}")
print(f"  モデル保存先: {MODEL_PATH}")