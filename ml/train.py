import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from pathlib import Path
import json

# ===== 設定 =====
DATA_DIR   = Path("ml/data/raw")
MODEL_DIR  = Path("ml/models")
MODEL_PATH = MODEL_DIR / "fighter_cnn_v1.pt"
CLASSES    = ["slender", "muscular", "standard", "heavyweight"]
BATCH_SIZE = 8
EPOCHS     = 20
LR         = 0.001
IMG_SIZE   = 224

MODEL_DIR.mkdir(exist_ok=True)

# ===== データ前処理 =====
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),       # 左右反転（データ拡張）
    transforms.RandomRotation(10),           # 少し回転（データ拡張）
    transforms.ColorJitter(brightness=0.2),  # 明るさ変化（データ拡張）
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
full_dataset = datasets.ImageFolder(root=str(DATA_DIR))
print(f"  クラス: {full_dataset.classes}")
print(f"  総枚数: {len(full_dataset)}枚")

# 訓練8割・検証2割に分割
train_size = int(0.8 * len(full_dataset))
val_size   = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

# 前処理を適用
train_dataset.dataset.transform = train_transform
val_dataset.dataset.transform   = val_transform

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False)

print(f"  訓練: {train_size}枚 / 検証: {val_size}枚")

# ===== モデル定義（ResNet18転移学習）=====
print("\n🧠 モデル準備中...")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# 最終層だけ付け替える（4クラス分類用）
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"  使用デバイス: {device}")
model = model.to(device)

# ===== 学習設定 =====
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# ===== 学習ループ =====
print("\n🚀 学習開始!")
best_val_acc = 0.0
history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

for epoch in range(EPOCHS):
    # 訓練フェーズ
    model.train()
    train_loss, train_correct = 0.0, 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss    += loss.item()
        train_correct += (outputs.argmax(1) == labels).sum().item()

    # 検証フェーズ
    model.eval()
    val_loss, val_correct = 0.0, 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs  = model(images)
            loss     = criterion(outputs, labels)
            val_loss    += loss.item()
            val_correct += (outputs.argmax(1) == labels).sum().item()

    # 精度計算
    train_acc = train_correct / train_size
    val_acc   = val_correct   / val_size

    history["train_loss"].append(round(train_loss / len(train_loader), 4))
    history["train_acc"].append(round(train_acc, 4))
    history["val_loss"].append(round(val_loss / len(val_loader), 4))
    history["val_acc"].append(round(val_acc, 4))

    print(f"  Epoch {epoch+1:2d}/{EPOCHS} | "
          f"train_loss: {train_loss/len(train_loader):.4f} | "
          f"train_acc: {train_acc:.4f} | "
          f"val_loss: {val_loss/len(val_loader):.4f} | "
          f"val_acc: {val_acc:.4f}")

    scheduler.step()

    # ベストモデルを保存
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"  ✅ モデル保存 (val_acc: {val_acc:.4f})")

# ===== 結果保存 =====
with open(MODEL_DIR / "history.json", "w") as f:
    json.dump(history, f, indent=2)

print(f"\n🎉 学習完了!")
print(f"  最高検証精度: {best_val_acc:.4f}")
print(f"  モデル保存先: {MODEL_PATH}")