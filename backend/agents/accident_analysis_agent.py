"""AccidentAnalysisAgent — sends accident frame to Grok for deeper analysis."""

from backend.services.grok_service import analyze_frame_with_grok
from backend.utils.image_utils import encode_frame_to_base64

import numpy as np


class AccidentAnalysisAgent:
    """Uses Grok AI to produce a detailed accident analysis from a frame."""

    SYSTEM_PROMPT = (
        "You are an expert traffic accident analyst AI. "
        "Analyze the surveillance frame showing a potential vehicle accident. "
        "Provide: 1) Description of the scene, 2) Severity (minor/moderate/severe/critical), "
        "3) Estimated number of vehicles involved, 4) Whether emergency services are needed, "
        "5) Recommended immediate actions."
    )

    async def analyze(self, frame: np.ndarray, detection_context: str) -> dict:
        """
        Send accident frame to Grok and return structured analysis.

        Args:
            frame: the accident frame (BGR ndarray)
            detection_context: text from AccidentDetectionAgent

        Returns:
            {"severity": str, "analysis": str, "emergency_required": bool}
        """
        image_b64 = encode_frame_to_base64(frame)
        prompt = f"Accident detection context: {detection_context}. Analyze this frame."

        analysis_text = await analyze_frame_with_grok(image_b64, prompt)

        # Parse severity from Grok response (simple heuristic)
        text_lower = analysis_text.lower()
        if "critical" in text_lower:
            severity = "critical"
        elif "severe" in text_lower:
            severity = "severe"
        elif "moderate" in text_lower:
            severity = "moderate"
        else:
            severity = "minor"

        emergency = severity in ("severe", "critical") or "emergency" in text_lower

        return {
            "severity": severity,
            "analysis": analysis_text,
            "emergency_required": emergency,
        }
