# Medidas del laboratorio

Qué es cada valor de `src/config.py` que se mide en el laboratorio y cómo se obtiene. El orden de los pasos está en [calibration.md](calibration.md).

![Cómo ve la mesa el sistema](overview.svg)

| Constante | Cómo se obtiene | Estado |
|---|---|---|
| `CAMERA_NAME` | Parte del nombre de la cámara del lab, tal como sale en la lista del preview | Pendiente |
| `CAMERA_PRESET` | Preview, tecla `p`: la combinación con la que la ficha blanca-blanca no se quema | Pendiente |
| `CAMERA_MATRIX` / `DIST_COEFFS` | Tablero de ajedrez: `python -m scripts.calibrate_camera` | Pendiente |
| `CHESSBOARD_SQUARE_MM` | 20 mm, el del tablero de `docs/print/` | Hecho |
| `ARUCO_SIZE_MM` | Regla: lado del cuadrado negro de un ArUco | Hecho |
| `ARUCO_ROBOT_MM` | Freedrive con la punta de los dedos en el centro de los ArUco 0, 1 y 2 (x, y del pendant con signo invertido) | Hecho |
| `ARUCO_TABLE_MM` | Sale de `ARUCO_ROBOT_MM`: 0 en (40, 40), eje x de 0 a 1. Verificar distancias con cinta | Hecho |
| `DOMINO_SIZE_MM` / `DOMINO_THICKNESS_MM` | Regla: ancho, alto y grosor de la ficha | Hecho |
| `DOMINO_GRIP_Z_MM` | z de la mesa (media de los ArUco) + grosor de la ficha / 2 | Hecho |
| `GAME_ZONE_MM` / `POOL_ZONE_MM` | `python -m scripts.draw_zones`; deben quedar al alcance del robot (~530 mm de la base) | Revisar alcance |
| `WARP_PX_PER_MM` | `python -m scripts.suggest_warp_scale` | Repetir tras calibrar el lente |
| `TABLE_SIZE_MM` | Área de la imagen rectificada, hasta el borde de los ArUco | Hecho |
