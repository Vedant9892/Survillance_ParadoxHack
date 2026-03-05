"""DetectionAgent — receives a frame, runs person + crowd models, decides if suspicious."""

import numpy as np
from backend.models.person_detector import PersonDetector
from backend.models.crowd_detector import CrowdDetector


class DetectionAgent:
    """
    Receives frames → runs person detection + crowd/behavior analysis
    → returns detections and whether a threat was found.
    """

    def __init__(self, person_detector: PersonDetector, crowd_detector: CrowdDetector):
        self.person_detector = person_detector
        self.crowd_detector = crowd_detector

    def run(self, frame: np.ndarray, frame_width: int, frame_height: int) -> dict:
        """
        Returns:
            {
                "threat": bool,
                "detections": [...],
                "incidents": [...]
            }
        """
        detections = self.person_detector.detect(frame)
        incidents = self.crowd_detector.analyze(detections, frame_width, frame_height)

        # Also flag if any single detection is a direct threat (weapon)
        has_weapon = any(d["is_threat"] for d in detections)
        is_threat = bool(incidents) or has_weapon

        return {
            "threat": is_threat,
            "detections": [
                {
                    "label": d["label"],
                    "confidence": round(d["confidence"], 3),
                    "bbox": d["bbox"],
                    "is_threat": d["is_threat"],
                }
                for d in detections
            ],
            "incidents": incidents,
        }
