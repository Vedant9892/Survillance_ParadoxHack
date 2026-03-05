"""ThreatAgent — sends frame to Grok AI and retrieves threat analysis."""

from backend.services.grok_service import analyze_frame_with_grok


class ThreatAgent:
    """Sends suspicious frames to Grok for AI-powered threat analysis."""

    async def analyze(self, image_b64: str, incident_description: str) -> str:
        """
        Args:
            image_b64: base64-encoded JPEG frame
            incident_description: human-readable description of what was detected

        Returns:
            Threat analysis report string from Grok.
        """
        return await analyze_frame_with_grok(image_b64, incident_description)
