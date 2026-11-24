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


class CalibrationError(Exception):
    """Faltan ArUco para calibrar."""


def compute_homography(frame: np.ndarray) -> np.ndarray:
    """H (3x3): px de la imagen original -> mm de la mesa, con los 4 centros de los ArUco."""

    markers = detect_markers(frame)

    if len(markers) < config.MIN_ARUCO_VISIBLE:
        raise CalibrationError(
            f"Fewer than {config.MIN_ARUCO_VISIBLE} ArUco markers visible"
        )

    ids = sorted(markers)
    src = np.float32([markers[i] for i in ids])
    dst = np.float32([config.ARUCO_TABLE_MM[i] for i in ids])

    return cv2.getPerspectiveTransform(src, dst)


def rectify(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (imagen cenital de la mesa, H). En la imagen: 1 mm = WARP_PX_PER_MM px."""
    H = compute_homography(frame)
    k = config.WARP_PX_PER_MM
    w, h = config.TABLE_SIZE_MM
    warped = cv2.warpPerspective(
        frame, np.diag([k, k, 1.0]) @ H, (round(w * k), round(h * k))
    )
    return warped, H


def px_to_table_mm(pt_px: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """Pixel de la imagen original -> mm en el plano de la mesa."""
    x, y = cv2.perspectiveTransform(np.float64([[pt_px]]), H)[0, 0]
    return float(x), float(y)


def table_mm_to_px(pt_mm: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """mm de la mesa -> pixel de la imagen original."""
    return px_to_table_mm(pt_mm, np.linalg.inv(H))


def _fit_table_to_robot() -> tuple[np.ndarray, np.ndarray]:
    """Transformación rígida 2D (R, t) mesa -> robot con Kabsch sobre los ArUco medidos.

    Sin corrección de det(R): la mesa (y hacia abajo) es un espejo del robot (z arriba).
    """

    ids = sorted(config.ARUCO_ROBOT_MM)

    if len(ids) < 3:  # con 2 no se distingue rotación de espejo
        raise CalibrationError("ARUCO_ROBOT_MM needs at least 3 markers")

    a = np.float64([config.ARUCO_TABLE_MM[i] for i in ids])
    b = np.float64([config.ARUCO_ROBOT_MM[i][:2] for i in ids])

    a0, b0 = a.mean(axis=0), b.mean(axis=0)

    u, _, vt = np.linalg.svd((a - a0).T @ (b - b0))
    R = vt.T @ u.T

    return R, b0 - R @ a0


def table_to_robot(pt_mm: tuple[float, float]) -> tuple[float, float, float]:
    """mm de la mesa -> XYZ en el marco base del robot (usa TILE_Z_MM para Z)."""
    R, t = _fit_table_to_robot()
    x, y = R @ np.float64(pt_mm) + t
    return float(x), float(y), config.TILE_Z_MM


def table_angle_to_robot_deg(angle_deg: float) -> float:
    """Ángulo de una dirección en la mesa -> ángulo de esa dirección en el robot (grados)."""
    a = np.radians(angle_deg)
    R, _ = _fit_table_to_robot()
    dx, dy = R @ np.float64([np.cos(a), np.sin(a)])
    return float(np.degrees(np.arctan2(dy, dx)))
