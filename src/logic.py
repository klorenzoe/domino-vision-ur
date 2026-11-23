"""[D] Lógica de negocio (P4).

Contrato de salida: ver PLAN.md §3.
"""
import numpy as np


def run(frame: np.ndarray, n: int) -> dict:
    """Procesa una captura para el número `n` y devuelve el reporte (dict del §3).

    1. Rectifica y detecta fichas.
    2. Asigna juego/pool por regiones en coordenadas de mesa.
    3. Revisa los extremos de la fila; si `n` no está, reporta y termina.
    4. Si está, busca en el pool la ficha con `n` más cercana al robot.
    """
    raise NotImplementedError
