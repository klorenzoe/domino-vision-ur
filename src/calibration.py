"""[A] Geometría y calibración (P1).

Detección de ArUco, homografía imagen->mesa y transformación mesa->robot,
recalculadas en cada captura (calibración automática).
"""

import cv2
import numpy as np

from src import config

_detector = cv2.aruco.ArucoDetector(
    cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, config.ARUCO_DICT))
)


def detect_markers(frame: np.ndarray) -> dict[int, np.ndarray]:
    """Devuelve {id: centro (x, y) en px} de los ArUco de config.ARUCO_TABLE_MM."""

    corners, ids, _ = _detector.detectMarkers(frame)

    if ids is None:
        return {}

    return {
        int(i): c.reshape(4, 2).mean(axis=0)
        for i, c in zip(ids.flatten(), corners)
        if int(i) in config.ARUCO_TABLE_MM
    }


def rectify(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (imagen rectificada cenital, homografía H). Falla si hay < 3 ArUco."""
    raise NotImplementedError


def px_to_table_mm(pt_px: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """Pixel de la imagen original -> mm en el plano de la mesa."""
    raise NotImplementedError


def table_to_robot(pt_mm: tuple[float, float]) -> tuple[float, float, float]:
    """mm de la mesa -> XYZ en el marco base del robot (usa TILE_Z_MM para Z)."""
    raise NotImplementedError
