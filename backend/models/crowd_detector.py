"""Crowd detector — analyzes spatial clustering + weapon proximity + assault heuristics."""

import time
from backend.config.settings import settings


class CrowdDetector:
    """Behavioral analysis for crowds, weapon proximity, and physical assault."""

    def __init__(
        self,
        crowd_threshold: int | None = None,
        crowd_proximity_radius: int = 120,
        weapon_proximity_radius: int = 150,
    ):
        self.crowd_threshold = crowd_threshold or settings.CROWD_THRESHOLD
        self.crowd_proximity_radius_sq = crowd_proximity_radius ** 2
        self.weapon_proximity_radius_sq = weapon_proximity_radius ** 2

        # Temporal state for multi-frame confirmation
        self.temporal_state = {"weapon_near_person": 0, "physical_assault": 0}
        self.required_frames = {"weapon_near_person": 3, "physical_assault": 4}

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

    def analyze(self, detections: list[dict], frame_width: int, frame_height: int) -> list[dict]:
        """Return list of incident dicts detected in this frame."""
        incidents: list[dict] = []
        now = time.time()

        persons, weapons = [], []
        for det in detections:
            bbox = det["bbox"]
            cx, cy = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
            item = {"label": det["label"], "conf": det["confidence"], "bbox": bbox, "center": (cx, cy)}
            if det["label"] == "person":
                persons.append(item)
            elif det["label"] in ("knife", "gun", "scissors"):
                weapons.append(item)

        # --- 1. Dense crowd ---
        if len(persons) >= self.crowd_threshold:
            dense_clusters = 0
            crowd_bboxes = []
            for i, p1 in enumerate(persons):
                close = sum(
                    1
                    for j, p2 in enumerate(persons)
                    if i != j
                    and (p1["center"][0] - p2["center"][0]) ** 2
                    + (p1["center"][1] - p2["center"][1]) ** 2
                    < self.crowd_proximity_radius_sq
                )
                if close >= 3:
                    dense_clusters += 1
                    crowd_bboxes.append(p1["bbox"])
            if dense_clusters >= self.crowd_threshold - 1:
                incidents.append(
                    {
                        "incident_type": "Dense crowd gathering detected",
                        "timestamp": now,
                        "confidence": sum(p["conf"] for p in persons[: self.crowd_threshold]) / self.crowd_threshold,
                        "bboxes": crowd_bboxes,
                    }
                )

        # --- 2. Weapon near person ---
        weapon_threat = False
        threat_bboxes, threat_conf = [], 0.0
        for w in weapons:
            for p in persons:
                dist_sq = (w["center"][0] - p["center"][0]) ** 2 + (w["center"][1] - p["center"][1]) ** 2
                if dist_sq < self.weapon_proximity_radius_sq:
                    weapon_threat = True
                    threat_bboxes.extend([w["bbox"], p["bbox"]])
                    threat_conf = max(threat_conf, w["conf"])
                    break
            if weapon_threat:
                break

        if weapon_threat:
            self.temporal_state["weapon_near_person"] += 1
        else:
            self.temporal_state["weapon_near_person"] = 0

        if self.temporal_state["weapon_near_person"] >= self.required_frames["weapon_near_person"]:
            incidents.append(
                {
                    "incident_type": "Weapon detected near individual",
                    "timestamp": now,
                    "confidence": threat_conf,
                    "bboxes": threat_bboxes,
                }
            )
            self.temporal_state["weapon_near_person"] = 0

        # --- 3. Physical assault ---
        assault_detected = False
        assault_bboxes, assault_conf = [], 0.0
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                p1, p2 = persons[i], persons[j]
                iou = self._iou(p1["bbox"], p2["bbox"])
                dist_sq = (p1["center"][0] - p2["center"][0]) ** 2 + (p1["center"][1] - p2["center"][1]) ** 2
                if iou > 0.15 or dist_sq < (frame_width * 0.05) ** 2:
                    p1_top = (p1["bbox"][0], p1["bbox"][1], p1["bbox"][2], p1["bbox"][1] + int((p1["bbox"][3] - p1["bbox"][1]) * 0.3))
                    p2_top = (p2["bbox"][0], p2["bbox"][1], p2["bbox"][2], p2["bbox"][1] + int((p2["bbox"][3] - p2["bbox"][1]) * 0.3))
                    if self._iou(p1["bbox"], p2_top) > 0.05 or self._iou(p2["bbox"], p1_top) > 0.05:
                        assault_detected = True
                        assault_bboxes.extend([p1["bbox"], p2["bbox"]])
                        assault_conf = (p1["conf"] + p2["conf"]) / 2.0
                        break
            if assault_detected:
                break

        if assault_detected:
            self.temporal_state["physical_assault"] += 1
        else:
            self.temporal_state["physical_assault"] = 0

        if self.temporal_state["physical_assault"] >= self.required_frames["physical_assault"]:
            incidents.append(
                {
                    "incident_type": "Potential physical assault detected",
                    "timestamp": now,
                    "confidence": assault_conf,
                    "bboxes": assault_bboxes,
                }
            )
            self.temporal_state["physical_assault"] = 0

        return incidents
