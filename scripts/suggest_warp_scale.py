"""Recomienda WARP_PX_PER_MM: la resolución que tiene la cámara en las zonas de juego y pool.

Uso: python -m scripts.suggest_warp_scale [imagen]  (por defecto assets/scene.png)
"""

import sys

import cv2
import numpy as np

from src import calibration, config

path = sys.argv[1] if len(sys.argv) > 1 else "assets/scene.png"
img = cv2.imread(path)
if img is None:
    sys.exit(f"Could not read {path}")

H = calibration.compute_homography(img)


def px_per_mm(zone):
    """px de la imagen original por mm de mesa en el centro de la zona."""
    x0, y0, x1, y1 = zone
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = calibration.table_mm_to_px_many([(cx, cy), (cx + 10, cy), (cx, cy + 10)], H)
    return min(np.linalg.norm(pts[1] - pts[0]), np.linalg.norm(pts[2] - pts[0])) / 10


scales = {name: px_per_mm(z) for name, z in (("game", config.GAME_ZONE_MM), ("pool", config.POOL_ZONE_MM))}
for name, s in scales.items():
    print(f"{name}: {s:.2f} px/mm")

print(f"\nCurrent:     WARP_PX_PER_MM = {config.WARP_PX_PER_MM}")
print(f"Recommended: WARP_PX_PER_MM = {max(scales.values()):.2f}  (no detail lost in any zone)")
