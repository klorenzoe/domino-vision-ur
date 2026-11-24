"""Detecta los ArUco de una imagen e imprime id y centro en px.

Uso: python -m scripts.inspect_aruco data/escena_ejemplo.png
"""
import sys
from pathlib import Path

import cv2

from src import config

img = cv2.imread(sys.argv[1])

dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, config.ARUCO_DICT))

corners, ids, _ = cv2.aruco.ArucoDetector(dictionary).detectMarkers(img)

if ids is None:
    sys.exit("No se detectaron ArUco")

for marker_id, c in sorted(zip(ids.flatten(), corners), key=lambda t: t[0]):
    cx, cy = c[0].mean(axis=0)
    print(f"id {marker_id}: centro_px=({cx:.1f}, {cy:.1f})")

cv2.aruco.drawDetectedMarkers(img, corners, ids)

Path("output").mkdir(exist_ok=True)
cv2.imwrite("output/aruco_inspect.png", img)
