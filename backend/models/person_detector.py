"""Person detector — wraps YOLOv8 for person + weapon + object detection."""

import numpy as np
import cv2
from ultralytics import YOLO
from backend.config.settings import settings


class PersonDetector:
    """Detects persons, weapons, vehicles, bags using YOLOv8."""

    TARGET_CLASSES = {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
        24: "backpack",
        26: "handbag",
        28: "suitcase",
        43: "knife",
        44: "scissors",
        67: "cell phone",
    }

    THREAT_CLASSES = {43, 44}
    VEHICLE_CLASSES = {1, 2, 3, 5, 7}
    BAG_CLASSES = {24, 26, 28}

    def __init__(self, model_path: str | None = None):
        self.model = YOLO(model_path or settings.YOLO_MODEL_PATH)
        # Warmup: triggers model fuse() once so concurrent threads don't race
        self.model(np.zeros((1, 1, 3), dtype=np.uint8), verbose=False)

    def detect(self, frame) -> list[dict]:
        results = self.model(frame, verbose=False)[0]
        detections = []

        for box in results.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            # Adaptive confidence thresholds
            if class_id in self.THREAT_CLASSES:
                threshold = 0.2
            elif class_id == 0:
                threshold = 0.35
            elif class_id in self.VEHICLE_CLASSES:
                threshold = 0.4
            elif class_id in self.BAG_CLASSES:
                threshold = 0.3
            else:
                threshold = 0.4

            if confidence > threshold and class_id in self.TARGET_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                detections.append(
                    {
                        "label": self.TARGET_CLASSES[class_id],
                        "confidence": confidence,
                        "bbox": (x1, y1, x2, y2),
                        "class_id": class_id,
                        "is_threat": class_id in self.THREAT_CLASSES,
                    }
                )

        return detections
