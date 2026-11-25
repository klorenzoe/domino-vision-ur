"""Constantes del proyecto (completar con mediciones reales, PLAN.md §12).

Marcos: imagen (px) · mesa (mm, origen arriba-izq, x der, y abajo; arriba = robot) · robot (mm, base UR).

### TODO (laboratorio):
- Pegar los ArUco a ras de cada esquina en el orden de la hoja (0 arriba-izq, 1 arriba-der,
  2 abajo-izq, 3 abajo-der). Verificar con scripts/inspect_aruco.py.
- Medir con cinta TABLE_SIZE_MM y verificar ARUCO_TABLE_MM con regla.
- ARUCO_ROBOT_MM: freedrive a los ArUco 0, 1 y 2 (el 3 queda fuera de alcance), con el TCP
  en la punta de los dedos; el pendant da x, y con signo invertido respecto a ROS.
- TILE_Z_MM = z de los ArUco + grosor de la ficha / 2.
- Comprobar el alcance del robot en GAME_ZONE_MM y POOL_ZONE_MM; recortarlas si no llega.
- Revisar WARP_PX_PER_MM: lado en px de los ArUco del fondo / ARUCO_SIZE_MM.
"""

ARUCO_DICT = "DICT_4X4_50"
ARUCO_SIZE_MM = 80.0  # no se usa para H

# id -> centro en mesa: marcador con su borde a ras de cada esquina (centro a 40 mm de los bordes).
ARUCO_TABLE_MM: dict[int, tuple[float, float]] = {
    0: (40, 40),
    1: (600, 40),
    2: (40, 460),
    3: (600, 460),
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
