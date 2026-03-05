"""Video utility helpers — save uploads, extract frames, get metadata."""

import os
import uuid
import tempfile

import cv2
import numpy as np


def save_upload_to_temp(file_bytes: bytes, suffix: str = ".mp4") -> str:
    """Write uploaded bytes to a temp file and return the path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(file_bytes)
    tmp.close()
    return tmp.name


def extract_frames(video_path: str, interval_sec: float = 1.0) -> list[dict]:
    """
    Extract frames from a video at the given interval.

    Returns:
        List of {"frame": np.ndarray, "timestamp_sec": float, "frame_index": int}
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(1, int(fps * interval_sec))

    frames: list[dict] = []
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_interval == 0:
            frames.append(
                {
                    "frame": frame,
                    "timestamp_sec": round(idx / fps, 2),
                    "frame_index": idx,
                }
            )
        idx += 1

    cap.release()
    return frames


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_video_metadata(video_path: str) -> dict:
    """Return basic metadata about a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {}
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps else 0
    cap.release()
    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_sec": round(duration, 2),
        "duration_str": format_timestamp(duration),
    }
