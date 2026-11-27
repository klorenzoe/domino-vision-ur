import os

# Cámara rápida (MSMF): tiene que definirse antes de importar cv2
os.environ.setdefault("OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS", "0")
