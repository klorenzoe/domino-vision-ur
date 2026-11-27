"""Cámara con resolución, exposición y ganancia fijas (config)."""

import cv2

from src import config


def open_camera(index: int) -> cv2.VideoCapture | None:
    """None si no existe o no da imagen."""
    # MSMF: con DSHOW esta cámara va a 5 fps en 1080p
    cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
    if not cap.isOpened():
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_RESOLUTION[1])
    cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
    set_manual(cap, config.CAMERA_EXPOSURE, config.CAMERA_GAIN)

    if not cap.read()[0]:
        cap.release()
        return None
    return cap


def set_manual(cap: cv2.VideoCapture, exposure: float, gain: float) -> None:
    """La cámara recuerda el último ajuste (también el automático de otras apps)."""
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual, 0.75 = automática
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    cap.set(cv2.CAP_PROP_GAIN, gain)


def describe(cap: cv2.VideoCapture) -> str:
    """Ajustes que reporta la cámara."""
    return (
        f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} "
        f"exp={cap.get(cv2.CAP_PROP_EXPOSURE):g} gain={cap.get(cv2.CAP_PROP_GAIN):g}"
    )
