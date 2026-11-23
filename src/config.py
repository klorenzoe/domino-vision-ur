"""Constantes del proyecto. Completar con las mediciones reales (ver PLAN.md §12)."""

# ArUco: id -> posición del centro en el marco base del robot (mm). Medir una sola vez.
ARUCO_ROBOT_MM: dict[int, tuple[float, float, float]] = {}
ARUCO_SIZE_MM: float | None = None  # lado real del marcador
ARUCO_DICT = "DICT_4X4_50"  # confirmar con los marcadores impresos

# Altura Z de las fichas en el marco del robot (mm): mesa + mitad del grosor.
TILE_Z_MM: float | None = None

# Regiones en coordenadas de mesa (mm): (x_min, y_min, x_max, y_max).
GAME_ZONE_MM: tuple[float, float, float, float] | None = None
POOL_ZONE_MM: tuple[float, float, float, float] | None = None

MIN_ARUCO_VISIBLE = 3
