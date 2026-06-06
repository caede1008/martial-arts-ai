import json
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'MS Gothic'  # 日本語フォント

# ===== 設定 =====
DATA_DIR   = Path("ml/data/raw")
MODEL_PATH = Path("ml/models/fighter_cnn_v1.pt")
HISTORY_PATH = Path("ml/models/history.json")
CLASSES    = ["slender", "muscular", "standard", "heavyweight"]
IMG_SIZE   = 224

# ===== 学習曲線を表示 =====
def plot_history():
    with open(HISTORY_PATH) as f:
        history = json.load(f)

    epochs = range(1, len(history["train_acc"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # 精度グラフ
    ax1.plot(epochs, history["train_acc"], label="訓練精度", marker="o")
    ax1.plot(epochs, history["val_acc"],   label="検証精度", marker="o")
    ax1.set_title("精度の推移")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.legend()
    ax1.grid(True)

    # 損失グラフ
    ax2.plot(epochs, history["train_loss"], label="訓練損失", marker="o")
    ax2.plot(epochs, history["val_loss"],   label="検証損失", marker="o")
    ax2.set_title("損失の推移")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("ml/models/learning_curve.png")
    plt.show()
    print("✅ 学習曲線を ml/models/learning_curve.png に保存しました")


# ===== 混同行列を表示 =====
def plot_confusion_matrix():
    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])

    dataset = datasets.ImageFolder(root=str(DATA_DIR), transform=transform)
    _, val_dataset = torch.utils.data.random_split(
        dataset, [int(0.8 * len(dataset)), len(dataset) - int(0.8 * len(dataset))]
    )
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)

    # モデル読み込み
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    # 予測
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images)
            preds   = outputs.argmax(1)
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    # 混同行列を計算
    cm = [[0] * len(CLASSES) for _ in range(len(CLASSES))]
    for pred, label in zip(all_preds, all_labels):
        cm[label][pred] += 1

    # 混同行列を表示
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    plt.colorbar(im)

    ax.set_xticks(range(len(CLASSES)))
    ax.set_yticks(range(len(CLASSES)))
    ax.set_xticklabels(CLASSES, rotation=45, ha="right")
    ax.set_yticklabels(CLASSES)
    ax.set_xlabel("予測")
    ax.set_ylabel("正解")
    ax.set_title("混同行列")

    for i in range(len(CLASSES)):
        for j in range(len(CLASSES)):
            ax.text(j, i, cm[i][j], ha="center", va="center",
                    color="white" if cm[i][j] > 2 else "black")

    plt.tight_layout()
    plt.savefig("ml/models/confusion_matrix.png")
    plt.show()
    print("✅ 混同行列を ml/models/confusion_matrix.png に保存しました")


if __name__ == "__main__":
    print("📊 学習結果を可視化します\n")
    plot_history()
    plot_confusion_matrix()