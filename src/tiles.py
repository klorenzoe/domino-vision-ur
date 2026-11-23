"""[B] Segmentación de fichas (P2)."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Tile:
    contour: np.ndarray
    center_px: tuple[float, float]
    angle_deg: float
    size_px: tuple[float, float]
    crop: np.ndarray  # recorte enderezado, relación 2:1
    halves: tuple[np.ndarray, np.ndarray]  # (mitad A, mitad B)


def detect_tiles(img: np.ndarray) -> list[Tile]:
    """Detecta todas las fichas de la imagen y devuelve sus recortes y geometría."""
    raise NotImplementedError
