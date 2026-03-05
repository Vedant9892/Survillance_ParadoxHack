"""Detection service — orchestrates the full detection pipeline."""

from backend.models.person_detector import PersonDetector
from backend.models.crowd_detector import CrowdDetector
from backend.agents.detection_agent import DetectionAgent
from backend.agents.threat_agent import ThreatAgent
from backend.agents.xai_agent import XAIAgent
from backend.utils.image_utils import decode_base64_image, encode_frame_to_base64, save_snapshot

import numpy as np

# Singletons — initialized once when the module is imported
_person_detector = PersonDetector()
_crowd_detector = CrowdDetector()
_detection_agent = DetectionAgent(_person_detector, _crowd_detector)
_threat_agent = ThreatAgent()
_xai_agent = XAIAgent()


async def run_detection_pipeline(image_b64: str) -> dict:
    """
    Full pipeline:
      1. DetectionAgent → detections + incidents
      2. If threat → ThreatAgent (Grok) → analysis
      3. XAIAgent → explanation
      4. Return combined result
    """
    # Decode image
    frame = decode_base64_image(image_b64)
    h, w = frame.shape[:2]

    # Step 1 — Detection
    result = _detection_agent.run(frame, w, h)

    if not result["threat"]:
        return {
            "threat": False,
            "detections": result["detections"],
            "incidents": [],
            "analysis": None,
            "explanation": None,
        }

    # Save snapshot for evidence
    snapshot_path = save_snapshot(frame)

    # Build incident description
    incident_desc = "; ".join(inc["incident_type"] for inc in result["incidents"])

    # Step 2 — Threat analysis via Grok
    frame_b64 = encode_frame_to_base64(frame)
    analysis = await _threat_agent.analyze(frame_b64, incident_desc)

    # Step 3 — XAI explanation
    explanation = _xai_agent.explain(result["detections"], result["incidents"], analysis)

    return {
        "threat": True,
        "detections": result["detections"],
        "incidents": [
            {"type": inc["incident_type"], "confidence": inc["confidence"]}
            for inc in result["incidents"]
        ],
        "analysis": analysis,
        "explanation": explanation,
        "snapshot": snapshot_path,
    }
