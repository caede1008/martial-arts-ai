import cv2
import os
import sys
from pathlib import Path

# 保存先フォルダ
SAVE_DIRS = {
    "1": ("slender",     "スラリー型（那須川天心・メイウェザーなど）"),
    "2": ("muscular",    "ガッシリ型（井上尚弥・ハビブなど）"),
    "3": ("standard",    "標準型（バランスの取れた体型）"),
    "4": ("heavyweight", "重量級型（ガヌー・マーク・ハントなど）"),
}

BASE_DIR = Path("ml/data/raw")


def count_images():
    """各クラスの現在の画像枚数を表示"""
    print("\n📊 現在の画像枚数:")
    for key, (folder, label) in SAVE_DIRS.items():
        path = BASE_DIR / folder
        count = len(list(path.glob("*.jpg"))) + len(list(path.glob("*.png"))) + len(list(path.glob("*.jfif")))
        print(f"  {key}. {label}: {count}枚")
    print()


def rename_images():
    """画像ファイルを連番にリネーム"""
    for key, (folder, _) in SAVE_DIRS.items():
        path = BASE_DIR / folder
        images = list(path.glob("*.jpg")) + list(path.glob("*.png")) + list(path.glob("*.jfif"))
        for i, img_path in enumerate(sorted(images)):
            new_name = path / f"{folder}_{i+1:04d}.jpg"
            if img_path != new_name:
                img = cv2.imread(str(img_path))
                if img is not None:
                    cv2.imwrite(str(new_name), img)
                    if img_path.suffix != ".jpg" or img_path.name != new_name.name:
                        img_path.unlink()
        print(f"✅ {folder}: {len(images)}枚をリネーム完了")


def show_images(class_key):
    """指定クラスの画像を確認表示"""
    folder, label = SAVE_DIRS[class_key]
    path = BASE_DIR / folder
    images = list(path.glob("*.jpg")) + list(path.glob("*.png")) + list(path.glob("*.jfif"))

    if not images:
        print(f"❌ {label} に画像がありません")
        return

    print(f"\n{label} の画像を表示します（任意のキーで次へ、qで終了）")
    for img_path in sorted(images):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        img_resized = cv2.resize(img, (400, 600))
        cv2.imshow(f"{label} - {img_path.name}", img_resized)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()
        if key == ord('q'):
            break


if __name__ == "__main__":
    print("=" * 50)
    print("格闘技画像データ管理ツール")
    print("=" * 50)

    while True:
        count_images()
        print("操作を選んでください:")
        print("  1-4: 各クラスの画像を確認")
        print("  r:   画像をリネーム・整理")
        print("  q:   終了")
        choice = input("入力: ").strip()

        if choice == "q":
            break
        elif choice == "r":
            rename_images()
        elif choice in SAVE_DIRS:
            show_images(choice)
        else:
            print("❌ 無効な入力です")