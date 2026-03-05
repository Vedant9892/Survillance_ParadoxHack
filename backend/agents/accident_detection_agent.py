"""AccidentDetectionAgent — analyzes frames for vehicle collisions / accidents."""

import numpy as np
from backend.models.person_detector import PersonDetector


class AccidentDetectionAgent:
    """
    Processes extracted video frames and detects potential accidents.

    Heuristics:
      - Multiple vehicles in close proximity / overlapping bboxes
      - Sudden presence of persons near vehicles (post-crash scene)
      - Vehicles with abnormal aspect ratios (rotated / flipped)
    """

    VEHICLE_LABELS = {"car", "truck", "bus", "motorcycle", "bicycle"}

    def __init__(self, detector: PersonDetector | None = None):
        self.detector = detector or PersonDetector()

    def analyze_frame(self, frame: np.ndarray) -> dict:
        """
        Analyze a single frame for accident indicators.

        Returns:
            {
                "accident_detected": bool,
                "confidence": float,
                "detections": [...],
                "reason": str
            }
        """
        detections = self.detector.detect(frame)
        h, w = frame.shape[:2]

        vehicles = [d for d in detections if d["label"] in self.VEHICLE_LABELS]
        persons = [d for d in detections if d["label"] == "person"]

        accident = False
        confidence = 0.0
        reason = ""

        # --- Heuristic 1: Vehicle overlap (collision indicator) ---
        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                iou = self._iou(vehicles[i]["bbox"], vehicles[j]["bbox"])
                if iou > 0.10:
                    accident = True
                    confidence = max(confidence, min(vehicles[i]["confidence"], vehicles[j]["confidence"]))
                    reason = (
                        f"Vehicle overlap detected: {vehicles[i]['label']} and "
                        f"{vehicles[j]['label']} (IoU={iou:.2f})"
                    )
                    break
            if accident:
                break

        # --- Heuristic 2: Person very close to vehicle (post-crash scene) ---
        if not accident and vehicles and persons:
            for v in vehicles:
                for p in persons:
                    v_cx = (v["bbox"][0] + v["bbox"][2]) / 2
                    v_cy = (v["bbox"][1] + v["bbox"][3]) / 2
                    p_cx = (p["bbox"][0] + p["bbox"][2]) / 2
                    p_cy = (p["bbox"][1] + p["bbox"][3]) / 2
                    dist = ((v_cx - p_cx) ** 2 + (v_cy - p_cy) ** 2) ** 0.5
                    # Person within ~15% of frame width from vehicle center
                    if dist < w * 0.15:
                        accident = True
                        confidence = max(confidence, (v["confidence"] + p["confidence"]) / 2)
                        reason = f"Person detected in close proximity to {v['label']} (possible post-crash)"
                        break
                if accident:
                    break

        # --- Heuristic 3: Multiple vehicles clustered abnormally ---
        if not accident and len(vehicles) >= 3:
            centers = [((v["bbox"][0] + v["bbox"][2]) / 2, (v["bbox"][1] + v["bbox"][3]) / 2) for v in vehicles]
            avg_dist = self._avg_pairwise_dist(centers)
            if avg_dist < w * 0.12:
                accident = True
                confidence = sum(v["confidence"] for v in vehicles) / len(vehicles)
                reason = f"{len(vehicles)} vehicles abnormally clustered (avg dist={avg_dist:.0f}px)"

        return {
            "accident_detected": accident,
            "confidence": round(confidence, 3),
            "detections": [
                {"label": d["label"], "confidence": round(d["confidence"], 3), "bbox": d["bbox"]}
                for d in detections
            ],
            "reason": reason,
            "vehicle_count": len(vehicles),
            "person_count": len(persons),
        }

    def analyze_video_frames(self, frames: list[dict]) -> list[dict]:
        """
        Analyze a sequence of extracted frames.

        Args:
            frames: list of {"frame": ndarray, "timestamp_sec": float, ...}

        Returns:
            list of accident detections with timestamps.
        """
        results = []
        for f in frames:
            analysis = self.analyze_frame(f["frame"])
            if analysis["accident_detected"]:
                analysis["timestamp_sec"] = f["timestamp_sec"]
                analysis["frame_index"] = f["frame_index"]
                results.append(analysis)
        return results

    @staticmethod
    def _iou(box1, box2) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        if inter == 0:
            return 0.0
        a1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        a2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return inter / float(a1 + a2 - inter)

    @staticmethod
    def _avg_pairwise_dist(centers: list[tuple]) -> float:
        if len(centers) < 2:
            return float("inf")
        total, count = 0.0, 0
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                total += ((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2) ** 0.5
                count += 1
        return total / count
