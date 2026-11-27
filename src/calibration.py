"""[A] Geometría y calibración (P1): ArUco -> pose de la cámara -> vista cenital y mesa -> robot.

px "originales" = frame de la cámara; px "sin distorsión" = salida de undistort().
H: px sin distorsión -> mm de un plano a cierta altura sobre la mesa.
"""

import warnings

import cv2
import numpy as np

from src import config

_detector = cv2.aruco.ArucoDetector(
    cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, config.ARUCO_DICT))
)

_K = np.float64(config.CAMERA_MATRIX)
_DIST = np.float64(config.DIST_COEFFS)
# alpha=1: no recorta la imagen
_K_UND, _ = cv2.getOptimalNewCameraMatrix(_K, _DIST, config.CAMERA_RESOLUTION, 1)
_UNDISTORT_MAPS = cv2.initUndistortRectifyMap(
    _K, _DIST, None, _K_UND, config.CAMERA_RESOLUTION, cv2.CV_16SC2
)

# Esquinas de un ArUco respecto a su centro, en el orden de OpenCV
_SQUARE = np.float64([[-1, -1], [1, -1], [1, 1], [-1, 1]]) / 2


class CalibrationError(Exception):
    """Faltan ArUco para calibrar o la imagen no es de la cámara calibrada."""


def _check_resolution(frame: np.ndarray) -> None:
    if (frame.shape[1], frame.shape[0]) != config.CAMERA_RESOLUTION:
        raise CalibrationError(
            f"Frame is {frame.shape[1]}x{frame.shape[0]}, "
            f"calibration is for {config.CAMERA_RESOLUTION[0]}x{config.CAMERA_RESOLUTION[1]}"
        )


def undistort(frame: np.ndarray) -> np.ndarray:
    """Imagen original -> imagen sin distorsión (mismo tamaño, sin recortar)."""
    _check_resolution(frame)
    return cv2.remap(frame, *_UNDISTORT_MAPS, cv2.INTER_LINEAR)


def undistort_points(pts_px: np.ndarray) -> np.ndarray:
    """(N, 2) px originales -> (N, 2) px sin distorsión."""
    pts = np.float64(pts_px).reshape(-1, 1, 2)
    return cv2.undistortPoints(pts, _K, _DIST, P=_K_UND).reshape(-1, 2)


def distort_points(pts_px: np.ndarray) -> np.ndarray:
    """(N, 2) px sin distorsión -> (N, 2) px originales."""
    pts = np.float64(pts_px).reshape(-1, 2)
    norm = cv2.undistortPoints(pts.reshape(-1, 1, 2), _K_UND, None).reshape(-1, 2)
    out, _ = cv2.projectPoints(np.c_[norm, np.ones(len(norm))], np.zeros(3), np.zeros(3), _K, _DIST)
    return out.reshape(-1, 2)


def detect_markers(frame: np.ndarray) -> dict[int, np.ndarray]:
    """{id: esquinas (4, 2) en px sin distorsión}."""

    corners, ids, _ = _detector.detectMarkers(undistort(frame))

    if ids is None:
        return {}

    return {
        int(i): c.reshape(4, 2).astype(np.float64)
        for i, c in zip(ids.flatten(), corners)
        if int(i) in config.ARUCO_TABLE_MM
    }


def marker_corners_mm(marker_id: int) -> np.ndarray:
    """(4, 2) esquinas de un ArUco en mm de mesa."""
    return np.float64(config.ARUCO_TABLE_MM[marker_id]) + _SQUARE * config.ARUCO_SIZE_MM


def solve_pose(markers: dict[int, np.ndarray]) -> tuple[np.ndarray, np.ndarray, float]:
    """(rvec, tvec, error RMS en px) a partir de {id: esquinas}."""
    ids = sorted(markers)
    obj = np.vstack([np.c_[marker_corners_mm(i), np.zeros(4)] for i in ids])
    img = np.vstack([markers[i] for i in ids])
    _, rvec, tvec = cv2.solvePnP(obj, img, _K_UND, None, flags=cv2.SOLVEPNP_IPPE)
    proj, _ = cv2.projectPoints(obj, rvec, tvec, _K_UND, None)
    return rvec, tvec, float(np.sqrt(np.mean((proj.reshape(-1, 2) - img) ** 2)))


def estimate_pose(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(rvec, tvec) de la mesa con los ArUco visibles."""

    markers = detect_markers(frame)
    seen = sorted(markers)

    if len(markers) < config.MIN_ARUCO_VISIBLE:
        raise CalibrationError(
            f"Only ArUco {seen} visible, need {config.MIN_ARUCO_VISIBLE} of "
            f"{sorted(config.ARUCO_TABLE_MM)}"
        )

    rvec, tvec, err = solve_pose(markers)
    if err > config.MAX_REPROJECTION_ERROR_PX:
        warnings.warn(
            f"ArUco reprojection error {err:.1f} px "
            f"(max {config.MAX_REPROJECTION_ERROR_PX}): check ARUCO_TABLE_MM, "
            "ARUCO_SIZE_MM and the camera calibration"
        )
    return rvec, tvec


def plane_homography(rvec: np.ndarray, tvec: np.ndarray, height_mm: float) -> np.ndarray:
    """H (3x3): px sin distorsión -> mm (x, y) del plano a height_mm sobre la mesa."""
    R, _ = cv2.Rodrigues(rvec)
    # (x, y, -h) -> px: K · (x·r1 + y·r2 + t - h·r3)
    to_px = _K_UND @ np.c_[R[:, 0], R[:, 1], np.ravel(tvec) - height_mm * R[:, 2]]
    H = np.linalg.inv(to_px)
    return H / H[2, 2]


def compute_homography(frame: np.ndarray, height_mm: float = config.RECTIFY_HEIGHT_MM) -> np.ndarray:
    """H (3x3): px sin distorsión -> mm del plano a height_mm sobre la mesa."""
    return plane_homography(*estimate_pose(frame), height_mm)


def rectify(
    frame: np.ndarray, height_mm: float = config.RECTIFY_HEIGHT_MM
) -> tuple[np.ndarray, np.ndarray]:
    """Imagen original -> (vista cenital, H), con 1 mm = WARP_PX_PER_MM px.

    Por defecto endereza la cara de arriba de las fichas: miden igual en toda la imagen.
    """
    H = compute_homography(frame, height_mm)
    k = config.WARP_PX_PER_MM
    w, h = config.TABLE_SIZE_MM
    u, v = np.meshgrid(np.arange(round(w * k)), np.arange(round(h * k)))
    mm = np.c_[u.ravel(), v.ravel()] / k
    src = table_mm_to_px_many(mm, H).reshape(*u.shape, 2).astype(np.float32)
    warped = cv2.remap(frame, src[..., 0], src[..., 1], cv2.INTER_LINEAR)
    return warped, H


def zones_px() -> dict[str, tuple[int, int, int, int]]:
    """{"safe", "game", "pool"} -> (x0, y0, x1, y1) en px de rectify(). safe = juego + pool."""
    k = config.WARP_PX_PER_MM
    game, pool = config.GAME_ZONE_MM, config.POOL_ZONE_MM
    zones = {
        "safe": (*np.minimum(game[:2], pool[:2]), *np.maximum(game[2:], pool[2:])),
        "game": game,
        "pool": pool,
    }
    return {name: tuple(round(v * k) for v in zone) for name, zone in zones.items()}


def px_to_table_mm_many(pts_px: np.ndarray, H: np.ndarray) -> np.ndarray:
    """(N, 2) px de la imagen original -> (N, 2) mm en el plano de H."""
    und = undistort_points(pts_px).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(und, H).reshape(-1, 2)


def table_mm_to_px_many(pts_mm: np.ndarray, H: np.ndarray) -> np.ndarray:
    """(N, 2) mm en el plano de H -> (N, 2) px de la imagen original."""
    pts = np.float64(pts_mm).reshape(-1, 1, 2)
    return distort_points(cv2.perspectiveTransform(pts, np.linalg.inv(H)))


def px_to_table_mm(pt_px: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """Pixel de la imagen original -> mm en el plano de H."""
    x, y = px_to_table_mm_many([pt_px], H)[0]
    return float(x), float(y)


def table_mm_to_px(pt_mm: tuple[float, float], H: np.ndarray) -> tuple[float, float]:
    """mm en el plano de H -> pixel de la imagen original."""
    x, y = table_mm_to_px_many([pt_mm], H)[0]
    return float(x), float(y)


def _fit_table_to_robot() -> tuple[np.ndarray, np.ndarray]:
    """(R, t) mesa -> robot con Kabsch. Sin corregir det(R): la mesa es un espejo del robot."""

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
    """mm de la mesa -> XYZ en el marco base del robot (usa DOMINO_GRIP_Z_MM para Z)."""
    R, t = _fit_table_to_robot()
    x, y = R @ np.float64(pt_mm) + t
    return float(x), float(y), config.DOMINO_GRIP_Z_MM


def table_angle_to_robot_deg(angle_deg: float) -> float:
    """Ángulo en la mesa -> ángulo en el robot (grados)."""
    a = np.radians(angle_deg)
    R, _ = _fit_table_to_robot()
    dx, dy = R @ np.float64([np.cos(a), np.sin(a)])
    return float(np.degrees(np.arctan2(dy, dx)))
