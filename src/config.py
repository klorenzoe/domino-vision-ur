"""Constantes del proyecto (completar con mediciones reales, PLAN.md §12).

Marcos: imagen (px) · mesa (mm, origen arriba-izq, x der, y abajo; arriba = robot) · robot (mm, base UR).
"""

ARUCO_DICT = "DICT_4X4_50"
ARUCO_SIZE_MM = 80.0  # no se usa para H
# id -> centro en mesa: marcador con su borde a ras de cada esquina (centro a 40 mm de los bordes).
ARUCO_TABLE_MM: dict[int, tuple[float, float]] = {
    0: (600.0, 460.0),
    1: (40.0, 460.0),
    2: (600.0, 40.0),
    3: (40.0, 40.0),
}


# id -> centro en robot. TODO: medir con freedrive
ARUCO_ROBOT_MM: dict[int, tuple[float, float, float]] = {}

MIN_ARUCO_VISIBLE = 4  # H con los 4 centros

TABLE_SIZE_MM = (640.0, 500.0)  # (ancho, alto)
WARP_PX_PER_MM = 2.0

# TODO: medir hasta tocar la mesa, leer Z en Move (Feature: Base); TILE_Z_MM = Z + grosor_ficha / 2
TILE_Z_MM = -60.0  # punto de agarre en z del robot

# (x_min, y_min, x_max, y_max) en mm de mesa.
# TODO: ajustar en el laboratorio (estimadas de escena_ejemplo)
GAME_ZONE_MM = (0.0, 210.0, 640.0, 420.0)
POOL_ZONE_MM = (100.0, 0.0, 540.0, 200.0)
