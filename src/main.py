"""CLI: python -m src.main --image data/escena.png --number 4"""
import argparse
import json

import cv2

from src.logic import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca un número de dominó en juego y pool.")
    parser.add_argument("--image", required=True, help="imagen de la captura")
    parser.add_argument("--number", type=int, required=True, choices=range(7), help="número N (0-6)")
    args = parser.parse_args()

    frame = cv2.imread(args.image)
    if frame is None:
        raise SystemExit(f"No se pudo leer la imagen: {args.image}")

    print(json.dumps(run(frame, args.number), indent=2))


if __name__ == "__main__":
    main()
