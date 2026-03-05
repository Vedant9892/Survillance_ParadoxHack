"""VideoProcessingService — orchestrates the full accident detection pipeline."""

import os
import uuid

import cv2

from backend.config.settings import settings
from backend.utils.video_utils import extract_frames, get_video_metadata, format_timestamp
from backend.agents.accident_detection_agent import AccidentDetectionAgent
from backend.agents.accident_analysis_agent import AccidentAnalysisAgent
from backend.agents.report_generation_agent import ReportGenerationAgent
from backend.agents.alert_agent import AlertAgent
from backend.services import mongodb_service, supabase_service


# Singletons
_accident_detector = AccidentDetectionAgent()
_accident_analyzer = AccidentAnalysisAgent()
_report_generator = ReportGenerationAgent()
_alert_agent = AlertAgent()


async def process_accident_video(file_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline:
      1. Save video locally
      2. Extract frames → AccidentDetectionAgent
      3. Save accident frames locally → store URLs in MongoDB
      4. AccidentAnalysisAgent (Grok)
      5. ReportGenerationAgent → fetch frame URLs from MongoDB → save report to Supabase
      6. AlertAgent → save alert to Supabase
      7. Return response
    """
    video_id = uuid.uuid4().hex[:12]

    # 1. Save video locally
    os.makedirs(settings.VIDEOS_DIR, exist_ok=True)
    video_path = os.path.join(settings.VIDEOS_DIR, f"{video_id}_{filename}")
    with open(video_path, "wb") as f:
        f.write(file_bytes)

    video_metadata = get_video_metadata(video_path)

    # Record video in MongoDB
    try:
        mongodb_service.save_video_record(video_id, filename, video_path)
    except Exception as e:
        print(f"[Pipeline] MongoDB video record failed: {e}")

    # 2. Extract frames & detect accidents
    frames = extract_frames(video_path, interval_sec=0.5)
    accident_detections = _accident_detector.analyze_video_frames(frames)

    if not accident_detections:
        return {
            "accident_detected": False,
            "timestamp": None,
            "incident_type": None,
            "severity": None,
            "vehicles": [],
            "snapshot": None,
            "message": "No accidents detected in the video.",
        }

    # 3. Save accident frames locally + store URLs in MongoDB
    os.makedirs(settings.ACCIDENT_FRAMES_DIR, exist_ok=True)
    accident_frames_data = []

    for det in accident_detections:
        matching = [f for f in frames if f["frame_index"] == det.get("frame_index")]
        if matching:
            frame_img = matching[0]["frame"]
            accident_frames_data.append(frame_img)

            frame_filename = f"{video_id}_frame_{det['frame_index']}.jpg"
            frame_path = os.path.join(settings.ACCIDENT_FRAMES_DIR, frame_filename)
            cv2.imwrite(frame_path, frame_img)

            # Store URL in MongoDB
            try:
                mongodb_service.save_frame_url(
                    video_id=video_id,
                    frame_url=frame_path,
                    timestamp=format_timestamp(det.get("timestamp_sec", 0)),
                )
            except Exception as e:
                print(f"[Pipeline] MongoDB frame save failed: {e}")

    # 4. Analyze best accident frame with Grok
    primary_det = max(accident_detections, key=lambda d: d["confidence"])
    primary_idx = accident_detections.index(primary_det)
    primary_frame = (
        accident_frames_data[primary_idx]
        if primary_idx < len(accident_frames_data)
        else accident_frames_data[0]
    )

    analysis = await _accident_analyzer.analyze(primary_frame, primary_det["reason"])

    # 5. Generate report (fetches frame URLs from MongoDB internally)
    report = _report_generator.generate(
        video_id=video_id,
        video_name=filename,
        video_metadata=video_metadata,
        accident_detections=accident_detections,
        analysis_result=analysis,
        video_path=video_path,
    )

    # Save report to Supabase
    report_id = None
    try:
        db_report = {
            "video_name": report["video_name"],
            "created_at": report["created_at"],
            "timestamp": report["timestamp"],
            "incident_type": report["incident_type"],
            "severity": report["severity"],
            "confidence": report["confidence"],
            "report_text": report["report_text"][:5000],
            "emergency_required": report["emergency_required"],
            "vehicle_count": report["vehicle_count"],
            "person_count": report["person_count"],
            "snapshot_url": report["snapshot_url"],
            "detection_reason": report["detection_reason"],
        }
        saved = supabase_service.save_accident_report(db_report)
        report_id = saved.get("id")
    except Exception as e:
        print(f"[Pipeline] Supabase report save failed: {e}")

    # 6. Create alert
    _alert_agent.create_alert(report)

    return {
        "accident_detected": True,
        "timestamp": report["timestamp"],
        "incident_type": report["incident_type"],
        "severity": report["severity"],
        "vehicles": report["vehicles"],
        "snapshot": report["snapshot_url"],
        "report_id": report_id,
        "report": report,
    }
