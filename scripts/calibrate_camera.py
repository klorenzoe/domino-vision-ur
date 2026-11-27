"""CAMERA_MATRIX y DIST_COEFFS con un tablero de ajedrez (RMS < 0.5 px es buena).

1. python -m scripts.camera_preview, tecla c  (15-25 capturas, tablero por toda la imagen)
2. python -m scripts.calibrate_camera
"""

import sys
from pathlib import Path

import cv2
import numpy as np

from src import config

cols, rows = config.CHESSBOARD_INNER
board = np.zeros((cols * rows, 3), np.float32)
board[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * config.CHESSBOARD_SQUARE_MM

folder = Path(sys.argv[1] if len(sys.argv) > 1 else "captures/chessboard")
paths = sorted(folder.glob("*.png"))
if not paths:
    sys.exit(
        f"No captures in {folder}. Save them with key c in: python -m scripts.camera_preview"
    )

obj_pts, img_pts = [], []
for path in paths:
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if (gray.shape[1], gray.shape[0]) != config.CAMERA_RESOLUTION:
        print(
            f"{path.name}: {gray.shape[1]}x{gray.shape[0]}, not CAMERA_RESOLUTION, skipped"
        )
        continue
    # SB: robusto con distorsión fuerte
    found, corners = cv2.findChessboardCornersSB(gray, (cols, rows))
    print(f"{path.name}: {'ok' if found else 'board not found'}")
    if found:
        obj_pts.append(board)
        img_pts.append(corners)

if len(img_pts) < 10:
    sys.exit(f"Only {len(img_pts)} valid images, at least 10 needed")

rms, K, dist, _, _ = cv2.calibrateCamera(
    obj_pts, img_pts, config.CAMERA_RESOLUTION, None, None
)

print(f"\nRMS: {rms:.2f} px with {len(img_pts)} images\n")

print(
    "CAMERA_MATRIX = ("
    + ", ".join("(" + ", ".join(f"{v:.1f}" for v in row) + ")" for row in K)
    + ")"
)

print(
    "DIST_COEFFS = ("
    + ", ".join(f"{v:.4f}" for v in dist.ravel())
    + ")  # (k1, k2, p1, p2, k3)"
)
