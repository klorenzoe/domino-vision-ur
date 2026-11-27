"""Dibuja las zonas de juego y pool. Uso: python -m scripts.draw_zones [imagen]  (por defecto assets/scene.png)"""

import sys
from pathlib import Path

import cv2
import numpy as np

from src import calibration, config

ZONES = {
    "GAME": (config.GAME_ZONE_MM, (0, 200, 0)),
    "POOL": (config.POOL_ZONE_MM, (0, 140, 255)),
}


def zone_outline_mm(zone, n=50):
    """Muestreado: con distorsión los lados salen curvos."""
    x0, y0, x1, y1 = zone
    corners = np.float64([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    t = np.linspace(0, 1, n, endpoint=False)[:, None]
    return np.vstack([a + t * (b - a) for a, b in zip(corners[:-1], corners[1:])])


def draw(img, to_px, thickness):
    overlay = img.copy()
    for name, (zone, color) in ZONES.items():
        pts = np.int32(to_px(zone_outline_mm(zone)))
        cv2.fillPoly(overlay, [pts], color)
        cv2.polylines(img, [pts], True, color, thickness)
        x, y = pts[0]
        cv2.putText(img, name, (int(x) + 8, int(y) + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)
    return cv2.addWeighted(overlay, 0.25, img, 0.75, 0)


path = sys.argv[1] if len(sys.argv) > 1 else "assets/scene.png"
img = cv2.imread(path)
if img is None:
    sys.exit(f"Could not read {path}")

warped, H = calibration.rectify(img)
k = config.WARP_PX_PER_MM

out = draw(img.copy(), lambda p: calibration.table_mm_to_px_many(p, H), 3)
out_warped = draw(warped.copy(), lambda p: p * k, 2)

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/zones.png", out)
cv2.imwrite("output/zones_warped.png", out_warped)
print("Saved output/zones.png and output/zones_warped.png")
