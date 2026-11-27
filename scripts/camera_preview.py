"""Vista en vivo de la cámara. Teclas en pantalla; al salir imprime exposición y ganancia.

Uso: python -m scripts.camera_preview
"""

import time
from collections import deque
from pathlib import Path

import src  # noqa: F401  # antes que cv2 (ver src/__init__.py)
import cv2
import numpy as np
from cv2_enumerate_cameras import enumerate_cameras

from src import config
from src.camera import describe, open_camera, set_manual

# Ventana
WINDOW = "Camera"
SCALE = 0.5  # tamaño de la ventana respecto a la imagen de la cámara
WIDTH = config.CAMERA_RESOLUTION[0]
HEIGHT = config.CAMERA_RESOLUTION[1]
PREVIEW_SIZE = (round(WIDTH * SCALE), round(HEIGHT * SCALE))

# Comandos
CAPTURE_KEYS = {
    "a": Path("captures/arucos"),  # escena con los ArUco: px <-> mm de mesa
    "c": Path("captures/chessboard"),  # tablero: corrección del ojo de pez
}
EXPOSURE_KEYS = {"1": -1, "2": 1}  # paso de exposición
GAIN_KEYS = {"3": -16, "4": 16}  # paso de ganancia
SWITCH_KEY = "n"  # siguiente cámara detectada
PRESET_KEY = "p"  # siguiente combinación de CAMERA_PRESETS
PRESETS = list(config.CAMERA_PRESETS)
LONGEST_PRESET = max([*PRESETS, "custom"], key=len)  # ancho fijo del nombre en pantalla
QUIT_KEYS = {"q", "\x1b"}  # q o ESC

# Texto en pantalla
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
TEXT_COLOR = (0, 255, 0)
LINE_H = 20
MARGIN = 8
COL_GAP = 12
BOX_SHADE = 0.4  # fondo de cada bloque: 0 = negro, 1 = sin oscurecer


def list_cameras() -> list[str]:
    """Nombres de las cámaras; la posición en la lista es su índice en OpenCV (MSMF)."""
    names = [cam.name for cam in enumerate_cameras(cv2.CAP_MSMF)]
    if not names:
        raise SystemExit("No cameras found")
    for i, name in enumerate(names):
        print(f"{i}: {name}")
    return names


def default_camera(names: list[str]) -> int:
    """La que contiene CAMERA_NAME, o la primera."""
    wanted = config.CAMERA_NAME.lower()
    return next((i for i, name in enumerate(names) if wanted in name.lower()), 0)


def open_from(names: list[str], start: int) -> tuple[int, cv2.VideoCapture]:
    """Abre la cámara start; si no abre, prueba las siguientes."""
    for step in range(len(names)):
        index = (start + step) % len(names)
        cap = open_camera(index)
        if cap is not None:
            print(f"Camera {index} ({names[index]}): {describe(cap)}")
            return index, cap
    raise SystemExit("Could not open any camera")


def save_capture(frame: np.ndarray, folder: Path) -> Path:
    """Guarda como NN.png, con NN = mayor número existente + 1."""
    folder.mkdir(parents=True, exist_ok=True)
    nums = [int(p.stem) for p in folder.glob("*.png") if p.stem.isdigit()]
    path = folder / f"{max(nums, default=0) + 1:02d}.png"
    cv2.imwrite(str(path), frame)
    return path


def text_width(text: str) -> int:
    return cv2.getTextSize(text, FONT, FONT_SCALE, 1)[0][0]


def draw_rows(
    img: np.ndarray, rows: list[list[str]], corner: str, fixed: dict[int, str] | None = None
) -> None:
    """Bloque de texto alineado por columnas en una esquina: "tl", "tr", "bl" o "br".

    fixed: {columna: texto más ancho posible}. Esas columnas tienen ancho fijo y se alinean
    a la derecha, para que el bloque no cambie de tamaño cuando cambia el valor.
    """
    fixed = fixed or {}
    n_cols = max(map(len, rows))
    widths = [
        max([text_width(r[c]) for r in rows if c < len(r)] + [text_width(fixed.get(c, ""))])
        for c in range(n_cols)
    ]

    h, w = img.shape[:2]
    box_w = sum(widths) + COL_GAP * (n_cols - 1) + 2 * MARGIN
    box_h = len(rows) * LINE_H + MARGIN
    x0 = w - box_w if corner[1] == "r" else 0
    y0 = h - box_h if corner[0] == "b" else 0

    box = img[y0 : y0 + box_h, x0 : x0 + box_w]
    box[:] = (box * BOX_SHADE).astype(box.dtype)

    for i, row in enumerate(rows):
        x, y = x0 + MARGIN, y0 + 16 + i * LINE_H
        for c, (cell, col_w) in enumerate(zip(row, widths)):
            dx = col_w - text_width(cell) if c in fixed else 0
            cv2.putText(img, cell, (x + dx, y), FONT, FONT_SCALE, TEXT_COLOR, 1, cv2.LINE_AA)
            x += col_w + COL_GAP


def preset_name(exposure: float, gain: float) -> str:
    """Nombre de la combinación actual, o "custom" si se cambió con las teclas."""
    for name, values in config.CAMERA_PRESETS.items():
        if values == (exposure, gain):
            return name
    return "custom"


def next_preset(exposure: float, gain: float) -> tuple[float, float]:
    name = preset_name(exposure, gain)
    i = PRESETS.index(name) + 1 if name in PRESETS else 0
    return config.CAMERA_PRESETS[PRESETS[i % len(PRESETS)]]


def reported(cap: cv2.VideoCapture) -> tuple[float, float]:
    """(exposición, ganancia) que la cámara dice tener: puede no aplicar lo que se le pide."""
    return cap.get(cv2.CAP_PROP_EXPOSURE), cap.get(cv2.CAP_PROP_GAIN)


def render(
    frame: np.ndarray,
    index: int,
    fps: float,
    exposure: float,
    gain: float,
    real: tuple[float, float],
    counts: dict,
) -> np.ndarray:
    img = cv2.resize(frame, PREVIEW_SIZE, interpolation=cv2.INTER_AREA)
    draw_rows(
        img,
        [
            ["a:", "save arucos", str(counts["a"])],
            ["c:", "save chessboard", str(counts["c"])],
            ["n:", "next camera", str(index)],
            ["q:", "quit"],
        ],
        "tl",
    )
    draw_rows(img, [[f"{fps:.0f}", "fps"]], "tr", fixed={0: "888"})
    draw_rows(
        img,
        [
            ["", "set", "cam", "", ""],
            ["exposure:", f"{exposure:g}", f"{real[0]:g}", "1: down", "2: up"],
            ["gain:", f"{gain:g}", f"{real[1]:g}", "3: down", "4: up"],
        ],
        "bl",
        fixed={1: "-888", 2: "-888"},
    )
    draw_rows(img, [["p:", "preset", preset_name(exposure, gain)]], "br", fixed={2: LONGEST_PRESET})
    return img


def window_closed() -> bool:
    return cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1


def main() -> None:
    names = list_cameras()
    index, cap = open_from(names, default_camera(names))

    exposure, gain = config.CAMERA_EXPOSURE, config.CAMERA_GAIN
    counts = {key: 0 for key in CAPTURE_KEYS}
    stamps = deque(maxlen=30)  # tiempos de los últimos 30 frames
    # redimensionable a mano, conservando la relación de aspecto; arranca en PREVIEW_SIZE
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow(WINDOW, *PREVIEW_SIZE)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Could not read camera frame")
            break

        # fps en cada frame, promediando los últimos 30 (si no, el número baila)
        stamps.append(time.perf_counter())
        fps = (len(stamps) - 1) / (stamps[-1] - stamps[0]) if len(stamps) > 1 else 0.0

        cv2.imshow(WINDOW, render(frame, index, fps, exposure, gain, reported(cap), counts))
        key = chr(cv2.waitKey(1) & 0xFF)

        if key in QUIT_KEYS or window_closed():
            break
        if key in CAPTURE_KEYS:
            print(f"Saved: {save_capture(frame, CAPTURE_KEYS[key])}")
            counts[key] += 1
        elif key == SWITCH_KEY:
            cap.release()  # MSMF no abre la misma cámara dos veces
            index, cap = open_from(names, index + 1)
            exposure, gain = config.CAMERA_EXPOSURE, config.CAMERA_GAIN
        elif key == PRESET_KEY:
            exposure, gain = next_preset(exposure, gain)
            set_manual(cap, exposure, gain)
        elif key in EXPOSURE_KEYS:
            exposure += EXPOSURE_KEYS[key]
            set_manual(cap, exposure, gain)
        elif key in GAIN_KEYS:
            gain = max(0, gain + GAIN_KEYS[key])
            set_manual(cap, exposure, gain)

    print(f"\nCamera: {describe(cap)}")
    print(f'Preset for CAMERA_PRESETS: "name": ({exposure:g}, {gain:g}),')
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
