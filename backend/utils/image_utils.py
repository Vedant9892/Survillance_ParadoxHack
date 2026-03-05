"""Image utility helpers — encode / decode / save frames."""

import base64
import os
import uuid
from datetime import datetime

import cv2
import numpy as np

from backend.config.settings import settings


def decode_base64_image(b64_string: str) -> np.ndarray:
    """Decode a base64-encoded image string into an OpenCV BGR frame."""
    # Strip optional data-uri header
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    img_bytes = base64.b64decode(b64_string)
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode image")
    return frame


def encode_frame_to_base64(frame: np.ndarray, ext: str = ".jpg") -> str:
    """Encode an OpenCV frame to a base64 string."""
    _, buf = cv2.imencode(ext, frame)
    return base64.b64encode(buf).decode("utf-8")


def save_snapshot(frame: np.ndarray) -> str:
    """Save frame to data/snapshots/ and return the file path."""
    os.makedirs(settings.SNAPSHOT_DIR, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.jpg"
    path = os.path.join(settings.SNAPSHOT_DIR, filename)
    cv2.imwrite(path, frame)
    return path
