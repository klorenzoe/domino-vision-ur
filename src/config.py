"""Constantes del proyecto. Cómo medir cada una: docs/config.md.

Marcos: imagen (px) · mesa (mm, origen arriba-izq, x der, y abajo; arriba = robot) · robot (mm, base UR).
"""

ARUCO_DICT = "DICT_4X4_50"
ARUCO_SIZE_MM = 80.0

# Centros en robot (ROS = pendant con x, y invertidos), con freedrive. El 3 no se alcanza y no se usa
ARUCO_ROBOT_MM: dict[int, tuple[float, float, float]] = {
    0: (75.95, 145.09, -173.45),
    1: (-499.65, 147.33, -174.00),
    2: (52.64, 529.62, -174.91),
}

# Centros en mesa, sacados de ARUCO_ROBOT_MM. ArUco pegados derechos (se usan sus esquinas)
ARUCO_TABLE_MM: dict[int, tuple[float, float]] = {
    0: (40.0, 40.0),
    1: (615.6, 40.0),
    2: (64.8, 424.4),
}

MIN_ARUCO_VISIBLE = 2
MAX_REPROJECTION_ERROR_PX = 3.0  # aviso si se supera

CAMERA_NAME = (
    "ELP"  # parte del nombre de la cámara del lab; si no está, se abre la primera
)

CAMERA_RESOLUTION = (1920, 1080)  # (width, height)
CAMERA_FPS = 30

# (exposición, ganancia)
CAMERA_PRESETS = {
    "sweep": (-4, 128),    # mejor del lab
    "low_gain": (-4, 48),  # menos ruido, más oscura
    "no_gain": (-4, 0),    # sin ruido de ganancia
    "safe": (-5, 128),     # lejos de saturar si hay más luz
    "fast": (-6, 128),     # menos estela al mover cosas, oscura
    "bright": (-3, 64),    # más luz, puede saturar o bajar fps
}
CAMERA_PRESET = "low_gain"  # la que se usa por defecto
CAMERA_EXPOSURE, CAMERA_GAIN = CAMERA_PRESETS[CAMERA_PRESET]

CHESSBOARD_INNER = (9, 6)  # esquinas internas (columnas, filas)
CHESSBOARD_SQUARE_MM = 20.0  # docs/print/chessboard-9x6-20mm-a4.pdf

# TODO: rehacer con scripts/calibrate_camera.py
CAMERA_MATRIX = ((1110.0, 0.0, 960.0), (0.0, 1110.0, 540.0), (0.0, 0.0, 1.0))
DIST_COEFFS = (-0.2266, 0.0308, 0.0, 0.0, 0.0)  # (k1, k2, p1, p2, k3)

TABLE_SIZE_MM = (680.0, 465.0)  # (width, height) de la imagen rectificada
WARP_PX_PER_MM = 2.13
DOMINO_SIZE_MM = (24.1, 48.5)  # (width, height), ficha parada
DOMINO_THICKNESS_MM = 9.0

# rectify() endereza la cara de arriba de las fichas
RECTIFY_HEIGHT_MM = (
    DOMINO_THICKNESS_MM
)

# agarre en z del robot: mesa + grosor / 2
DOMINO_GRIP_Z_MM = -169.6

# (x_min, y_min, x_max, y_max) en mm de mesa. El robot alcanza ~530 mm desde la base
GAME_ZONE_MM = (35.0, 195.0, 635.0, 340.0)
POOL_ZONE_MM = (135.0, 30.0, 540.0, 190.0)
