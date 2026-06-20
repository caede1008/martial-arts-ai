import cv2
import numpy as np
import base64
import io
from PIL import Image

# 骨格の接続関係（MediaPipeの33点）
POSE_CONNECTIONS = [
    (11, 12),  # 左肩 - 右肩
    (11, 13),  # 左肩 - 左肘
    (13, 15),  # 左肘 - 左手首
    (12, 14),  # 右肩 - 右肘
    (14, 16),  # 右肘 - 右手首
    (11, 23),  # 左肩 - 左腰
    (12, 24),  # 右肩 - 右腰
    (23, 24),  # 左腰 - 右腰
    (23, 25),  # 左腰 - 左膝
    (25, 27),  # 左膝 - 左足首
    (24, 26),  # 右腰 - 右膝
    (26, 28),  # 右膝 - 右足首
    (15, 17),  # 左手首 - 左小指
    (15, 19),  # 左手首 - 左人差し指
    (16, 18),  # 右手首 - 右小指
    (16, 20),  # 右手首 - 右人差し指
    (27, 29),  # 左足首 - 左かかと
    (28, 30),  # 右足首 - 右かかと
]

# 部位ごとの色分け
PART_COLORS = {
    "upper": (52, 152, 219),   # 青: 上半身
    "lower": (46, 204, 113),   # 緑: 下半身
    "arms":  (231, 76, 60),    # 赤: 腕
    "core":  (155, 89, 182),   # 紫: 体幹
}

def get_connection_color(start_idx: int, end_idx: int) -> tuple:
    """接続部位に応じた色を返す"""
    arm_points = {13, 14, 15, 16, 17, 18, 19, 20}
    lower_points = {23, 24, 25, 26, 27, 28, 29, 30}
    core_points = {11, 12, 23, 24}

    if start_idx in arm_points or end_idx in arm_points:
        return PART_COLORS["arms"]
    elif start_idx in lower_points or end_idx in lower_points:
        return PART_COLORS["lower"]
    elif start_idx in core_points and end_idx in core_points:
        return PART_COLORS["core"]
    else:
        return PART_COLORS["upper"]


def generate_skeleton_visualization(image_bytes: bytes, landmarks: list) -> str:
    """
    画像に骨格を描画してbase64文字列で返す

    landmarks: MediaPipeのpose_landmarks[0]
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]

    # 画像を少し暗くしてオーバーレイしやすくする
    overlay = img.copy()
    img = cv2.addWeighted(img, 0.6, np.zeros_like(img), 0.4, 0)

    # 骨格の線を描画
    for start_idx, end_idx in POSE_CONNECTIONS:
        if start_idx >= len(landmarks) or end_idx >= len(landmarks):
            continue

        start = landmarks[start_idx]
        end   = landmarks[end_idx]

        # 可視性が低い点はスキップ
        if start.visibility < 0.5 or end.visibility < 0.5:
            continue

        x1, y1 = int(start.x * w), int(start.y * h)
        x2, y2 = int(end.x * w), int(end.y * h)

        color = get_connection_color(start_idx, end_idx)
        cv2.line(img, (x1, y1), (x2, y2), color, 3, cv2.LINE_AA)

    # 関節点を描画
    for i, lm in enumerate(landmarks):
        if lm.visibility < 0.5:
            continue
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(img, (x, y), 6, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (x, y), 4, (229, 62, 62), -1, cv2.LINE_AA)

    # リーチラインを描画（左手首〜右手首）
    lw = landmarks[15]
    rw = landmarks[16]
    if lw.visibility > 0.5 and rw.visibility > 0.5:
        x1, y1 = int(lw.x * w), int(lw.y * h)
        x2, y2 = int(rw.x * w), int(rw.y * h)
        cv2.line(img, (x1, y1), (x2, y2), (255, 215, 0), 2, cv2.LINE_AA)
        cv2.putText(img, "REACH", ((x1 + x2) // 2 - 30, (y1 + y2) // 2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 215, 0), 2)

    # 凡例を描画
    legend_items = [
        ("Upper body", PART_COLORS["upper"]),
        ("Arms",       PART_COLORS["arms"]),
        ("Core",       PART_COLORS["core"]),
        ("Lower body", PART_COLORS["lower"]),
    ]
    for i, (label, color) in enumerate(legend_items):
        y = 20 + i * 25
        cv2.rectangle(img, (10, y), (25, y + 15), color, -1)
        cv2.putText(img, label, (30, y + 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # base64に変換
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    img_base64 = base64.b64encode(buf.tobytes()).decode("utf-8")

    return img_base64