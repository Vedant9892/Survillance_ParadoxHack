"""AlertAgent — creates and dispatches alerts for detected accidents."""

from datetime import datetime
from backend.services import supabase_service


class AlertAgent:
    """Creates alert records and saves them to Supabase."""

    def create_alert(self, report: dict) -> dict:
        """
        Build an alert from an accident report and persist to Supabase.

        Returns:
            Saved alert dict.
        """
        severity = report.get("severity", "unknown")
        priority_map = {"critical": "P1", "severe": "P2", "moderate": "P3", "minor": "P4"}

        alert = {
            "type": "accident",
            "priority": priority_map.get(severity, "P4"),
            "severity": severity,
            "title": f"Accident Detected — {severity.upper()}",
            "description": report.get("detection_reason", ""),
            "timestamp": datetime.now().isoformat(),
            "emergency_required": report.get("emergency_required", False),
            "video_path": report.get("video_path", ""),
            "confidence": report.get("confidence", 0),
        }

        self._console_alert(alert)

        try:
            saved = supabase_service.save_alert(alert)
            return saved
        except Exception as e:
            print(f"[AlertAgent] Supabase save failed: {e}")
            return alert

    @staticmethod
    def _console_alert(alert: dict):
        print(f"\n[!] ACCIDENT ALERT — {alert['priority']}")
        print(f"    Severity    : {alert['severity'].upper()}")
        print(f"    Description : {alert['description']}")
        print(f"    Time        : {alert['timestamp']}")
        print(f"    Emergency   : {'YES' if alert['emergency_required'] else 'No'}")
        print(f"    Confidence  : {alert['confidence']:.1%}\n")
