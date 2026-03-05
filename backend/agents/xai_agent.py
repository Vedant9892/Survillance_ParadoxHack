"""XAI Agent — generates explainable AI reasoning for why a frame was flagged."""


class XAIAgent:
    """
    Produces a structured, human-readable explanation of:
      - Why the frame was flagged as a threat
      - Which objects / behaviors triggered it
    """

    def explain(
        self,
        detections: list[dict],
        incidents: list[dict],
        grok_analysis: str | None = None,
    ) -> str:
        """
        Build an XAI explanation from detection data + incidents + Grok report.

        Returns:
            Multi-line explanation string.
        """
        lines: list[str] = ["=== XAI Threat Explanation ===", ""]

        # --- Objects detected ---
        threat_objects = [d for d in detections if d.get("is_threat")]
        person_count = sum(1 for d in detections if d["label"] == "person")

        lines.append("DETECTED OBJECTS:")
        if threat_objects:
            for obj in threat_objects:
                lines.append(
                    f"  - THREAT OBJECT: {obj['label'].upper()} "
                    f"(confidence: {obj['confidence']:.1%}, bbox: {obj['bbox']})"
                )
        if person_count:
            lines.append(f"  - Persons in frame: {person_count}")
        if not threat_objects and not person_count:
            lines.append("  - No notable objects")

        lines.append("")

        # --- Behavioral triggers ---
        lines.append("BEHAVIORAL TRIGGERS:")
        if incidents:
            for inc in incidents:
                inc_type = inc.get("incident_type") or inc.get("type", "Unknown")
                conf = inc.get("confidence", 0)
                lines.append(f"  - {inc_type} (confidence: {conf:.1%})")
        else:
            lines.append("  - No behavioral incidents")

        lines.append("")

        # --- Why flagged ---
        lines.append("REASONING:")
        reasons: list[str] = []
        if threat_objects:
            labels = ", ".join(o["label"] for o in threat_objects)
            reasons.append(f"Dangerous object(s) detected: {labels}")
        if any("crowd" in (inc.get("incident_type") or inc.get("type", "")).lower() for inc in incidents):
            reasons.append(f"Abnormal crowd density ({person_count} persons clustered)")
        if any("weapon" in (inc.get("incident_type") or inc.get("type", "")).lower() for inc in incidents):
            reasons.append("Weapon detected in proximity to a person")
        if any("assault" in (inc.get("incident_type") or inc.get("type", "")).lower() for inc in incidents):
            reasons.append("Physical assault indicators (overlapping person bounding boxes)")

        if reasons:
            for r in reasons:
                lines.append(f"  → {r}")
        else:
            lines.append("  → General suspicious activity pattern")

        # --- Grok cross-reference ---
        if grok_analysis:
            lines.append("")
            lines.append("GROK AI CROSS-REFERENCE:")
            # Take first 300 chars to keep it concise
            summary = grok_analysis[:500].strip()
            lines.append(f"  {summary}")

        return "\n".join(lines)
