"""[A] Geometría y calibración (P1).

Detección de ArUco, homografía imagen->mesa y transformación mesa->robot,
recalculadas en cada captura (calibración automática).
"""
import numpy as np


def rectify(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (imagen rectificada cenital, homografía H). Falla si hay < 3 ArUco."""
    raise NotImplementedError


def px_to_table_mm(pt_px: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """Pixel de la imagen original -> mm en el plano de la mesa."""
    raise NotImplementedError


def table_to_robot(pt_mm: tuple[float, float]) -> tuple[float, float, float]:
    """mm de la mesa -> XYZ en el marco base del robot (usa TILE_Z_MM para Z)."""
    raise NotImplementedError
