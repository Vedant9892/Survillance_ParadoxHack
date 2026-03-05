"""ReportGenerationAgent — assembles a structured accident report."""

from datetime import datetime
from backend.utils.video_utils import format_timestamp
from backend.services import mongodb_service


class ReportGenerationAgent:
    """Compiles detection + analysis results into a final accident report."""

    def generate(
        self,
        video_id: str,
        video_name: str,
        video_metadata: dict,
        accident_detections: list[dict],
        analysis_result: dict,
        video_path: str,
    ) -> dict:
        """
        Build a structured accident report.
        Fetches frame URLs from MongoDB.
        """
        primary = max(accident_detections, key=lambda d: d["confidence"]) if accident_detections else {}

        # Fetch frame URLs from MongoDB
        frame_docs = mongodb_service.get_frame_urls(video_id)
        frame_urls = [doc["frame_url"] for doc in frame_docs]

        # Build vehicles list from primary detection
        vehicles = []
        if primary:
            for det in primary.get("detections", []):
                if det["label"] in ("car", "truck", "bus", "motorcycle", "bicycle"):
                    vehicles.append(det["label"])

        report = {
            "video_name": video_name,
            "video_path": video_path,
            "created_at": datetime.now().isoformat(),
            "video_duration": video_metadata.get("duration_str", "N/A"),

            # Primary accident
            "timestamp": format_timestamp(primary.get("timestamp_sec", 0)),
            "timestamp_sec": primary.get("timestamp_sec", 0),
            "confidence": primary.get("confidence", 0),
            "detection_reason": primary.get("reason", ""),
            "vehicle_count": primary.get("vehicle_count", 0),
            "person_count": primary.get("person_count", 0),
            "vehicles": vehicles,

            # Grok analysis
            "incident_type": analysis_result.get("incident_type", "Vehicle Collision"),
            "severity": analysis_result.get("severity", "unknown"),
            "report_text": analysis_result.get("analysis", ""),
            "emergency_required": analysis_result.get("emergency_required", False),

            # Evidence
            "snapshot_url": frame_urls[0] if frame_urls else "",
            "frame_urls": frame_urls,
            "total_detections": len(accident_detections),
        }

        return report
