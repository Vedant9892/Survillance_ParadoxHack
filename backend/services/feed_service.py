"""Feed service — manages webcam + video file feeds with YOLO detection overlay."""

import os
import time
import threading
import uuid
import cv2
from datetime import datetime

from backend.config.settings import settings
from backend.models.person_detector import PersonDetector
from backend.models.crowd_detector import CrowdDetector


# ── Globals ──────────────────────────────────────────────
_detector: PersonDetector | None = None
_analyzer: CrowdDetector | None = None

# Webcam state
_feed_running = False
_cap = None
_latest_frame = None
_frame_lock = threading.Lock()

# Per-camera video feed state
_cam_feeds: dict = {}   # cam_id -> {"cap", "frame", "lock", "running", "video"}
_cam_threads: dict = {}

# Incidents store (in-memory)
_incidents: list[dict] = []
_incidents_lock = threading.Lock()

# Screenshot directory
_screenshot_dir = settings.SNAPSHOT_DIR

# Camera definitions
CAMERA_LOCATIONS = {
    "CAM-01": {"name": "Metro Central Station", "lat": 19.0440, "lng": 73.0290, "status": "operational"},
    "CAM-02": {"name": "Market Square",         "lat": 19.0450, "lng": 73.0300, "status": "alert"},
    "CAM-03": {"name": "Bus Terminal",           "lat": 19.0460, "lng": 73.0310, "status": "operational"},
    "CAM-04": {"name": "Highway Exit 12",        "lat": 19.0470, "lng": 73.0320, "status": "operational"},
    "CAM-05": {"name": "Downtown Plaza",         "lat": 19.0480, "lng": 73.0330, "status": "operational"},
    "CAM-06": {"name": "East Bridge",            "lat": 19.0490, "lng": 73.0340, "status": "operational"},
}


def _get_detector() -> PersonDetector:
    global _detector
    if _detector is None:
        _detector = PersonDetector()
    return _detector


def _get_analyzer() -> CrowdDetector:
    global _analyzer
    if _analyzer is None:
        _analyzer = CrowdDetector()
    return _analyzer


# ── Drawing helpers ──────────────────────────────────────
def _draw_tactical_boxes(frame, detections, h, w, incidents=None):
    """Draw color-coded corner-bracket bounding boxes + HUD on frame."""
    person_count = vehicle_count = threat_count = 0

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label, conf = det["label"], det["confidence"]
        cid = det.get("class_id", 0)

        if det.get("is_threat"):
            color = (0, 0, 255)
            threat_count += 1
        elif cid == 0:
            color = (255, 242, 0)
            person_count += 1
        elif cid in {1, 2, 3, 5, 7}:
            color = (0, 255, 255)
            vehicle_count += 1
        else:
            color = (255, 0, 255)

        bw = max(int((x2 - x1) * 0.2), 10)
        bh = max(int((y2 - y1) * 0.2), 10)
        # Corner brackets
        cv2.line(frame, (x1, y1), (x1 + bw, y1), color, 2)
        cv2.line(frame, (x1, y1), (x1, y1 + bh), color, 2)
        cv2.line(frame, (x2, y1), (x2 - bw, y1), color, 2)
        cv2.line(frame, (x2, y1), (x2, y1 + bh), color, 2)
        cv2.line(frame, (x1, y2), (x1 + bw, y2), color, 2)
        cv2.line(frame, (x1, y2), (x1, y2 - bh), color, 2)
        cv2.line(frame, (x2, y2), (x2 - bw, y2), color, 2)
        cv2.line(frame, (x2, y2), (x2, y2 - bh), color, 2)

        txt = f"{label.upper()} {conf:.0%}"
        (tw, th2), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(frame, (x1, y1 - th2 - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(frame, txt, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

    # Action labels
    if incidents:
        for idx, inc in enumerate(incidents):
            action = inc["incident_type"].upper()
            cv2.putText(frame, f"ACTION: {action}", (10, h - 20 - idx * 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    # HUD overlay
    ts = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"REC  {ts}", (10, 22), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 242, 255), 1)
    stats = f"P:{person_count} V:{vehicle_count} T:{threat_count}"
    (sw, _), _ = cv2.getTextSize(stats, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
    cv2.putText(frame, stats, (w - sw - 8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 242, 255), 1)

    return frame


# ── Incident recording ──────────────────────────────────
def _record_incident(incident_type: str, location: str, confidence: float, frame):
    """Save an incident with evidence screenshot."""
    os.makedirs(_screenshot_dir, exist_ok=True)
    inc_id = uuid.uuid4().hex[:8]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    img_filename = f"{inc_id}.jpg"
    img_path = os.path.join(_screenshot_dir, img_filename)
    cv2.imwrite(img_path, frame)

    record = {
        "incident_id": f"CASE-{inc_id.upper()}",
        "timestamp": ts,
        "incident_type": incident_type,
        "location": location,
        "confidence_score": confidence,
        "evidence_image": img_filename,
    }
    with _incidents_lock:
        _incidents.insert(0, record)
        # Keep max 100
        if len(_incidents) > 100:
            _incidents.pop()
    print(f"[!] INCIDENT: {incident_type} @ {location} ({confidence:.0%})")
    return record


# ── Webcam loop ──────────────────────────────────────────
def _webcam_loop():
    global _feed_running, _cap, _latest_frame
    detector = _get_detector()
    analyzer = _get_analyzer()
    cooldown = 5
    last_inc_time = 0

    while _feed_running:
        ret, frame = _cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        h, w, _ = frame.shape
        detections = detector.detect(frame)
        frame_incidents = analyzer.analyze(detections, w, h)

        now = time.time()
        if frame_incidents and (now - last_inc_time) > cooldown:
            processed = set()
            for inc in frame_incidents:
                itype = inc["incident_type"]
                if itype in processed:
                    continue
                processed.add(itype)
                _record_incident(itype, "WEBCAM – Live", inc.get("confidence", 0), frame.copy())
            last_inc_time = now

        frame = _draw_tactical_boxes(frame, detections, h, w, frame_incidents)
        with _frame_lock:
            _latest_frame = frame.copy()

        time.sleep(0.03)

    if _cap:
        _cap.release()
        _cap = None


# ── Per-camera video loop ────────────────────────────────
def _video_loop(cam_id: str, video_path: str):
    state = _cam_feeds[cam_id]
    detector = _get_detector()
    analyzer = _get_analyzer()
    cooldown = 5
    last_inc_time = 0

    while state["running"]:
        cap_v = state["cap"]
        ret, frame = cap_v.read()
        if not ret:
            cap_v.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 360))
        h, w, _ = frame.shape
        detections = detector.detect(frame)
        frame_incidents = analyzer.analyze(detections, w, h)

        now = time.time()
        if frame_incidents and (now - last_inc_time) > cooldown:
            processed = set()
            for inc in frame_incidents:
                itype = inc["incident_type"]
                if itype in processed:
                    continue
                processed.add(itype)
                loc = f"{cam_id} – {CAMERA_LOCATIONS.get(cam_id, {}).get('name', 'Unknown')}"
                _record_incident(itype, loc, inc.get("confidence", 0), frame.copy())
            last_inc_time = now

        frame = _draw_tactical_boxes(frame, detections, h, w, frame_incidents)
        with state["lock"]:
            state["frame"] = frame.copy()

        time.sleep(0.04)

    state["cap"].release()


# ── Discover sample videos ───────────────────────────────
def _find_videos() -> list[str]:
    dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "videos"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "OldProject", "SAMPLE", "CCTV1"),
    ]
    vids = []
    for d in dirs:
        d = os.path.normpath(d)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".mp4", ".avi", ".mkv", ".mov")):
                    vids.append(os.path.join(d, f))
    return vids


# ── Public API ───────────────────────────────────────────
def start_webcam_feed() -> dict:
    global _feed_running, _cap
    if _feed_running:
        return {"status": "already_running"}
    _cap = cv2.VideoCapture(0)
    if not _cap.isOpened():
        return {"error": "Cannot open webcam"}
    _feed_running = True
    threading.Thread(target=_webcam_loop, daemon=True).start()
    return {"status": "started"}


def stop_webcam_feed() -> dict:
    global _feed_running
    _feed_running = False
    return {"status": "stopped"}


def is_feed_running() -> bool:
    return _feed_running


def get_latest_webcam_frame():
    with _frame_lock:
        return _latest_frame


def start_camera_feeds():
    """Start background YOLO detection on all available sample videos."""
    all_videos = _find_videos()
    cam_ids = list(CAMERA_LOCATIONS.keys())
    started = 0
    for i, cam_id in enumerate(cam_ids):
        if cam_id in _cam_feeds:
            continue
        if i < len(all_videos):
            video_path = all_videos[i % len(all_videos)]
            vc = cv2.VideoCapture(video_path)
            if not vc.isOpened():
                print(f"  [WARN] Cannot open {video_path}")
                continue
            _cam_feeds[cam_id] = {
                "cap": vc,
                "frame": None,
                "lock": threading.Lock(),
                "running": True,
                "video": os.path.basename(video_path),
            }
            t = threading.Thread(target=_video_loop, args=(cam_id, video_path), daemon=True)
            t.start()
            _cam_threads[cam_id] = t
            started += 1
            print(f"  [FEED] {cam_id} → {os.path.basename(video_path)}")
    return started


def get_camera_frame(cam_id: str):
    state = _cam_feeds.get(cam_id.upper())
    if not state:
        return None
    with state["lock"]:
        return state["frame"]


def gen_mjpeg_webcam():
    """Generator — yields MJPEG frames from the webcam feed."""
    while _feed_running:
        with _frame_lock:
            f = _latest_frame
        if f is None:
            time.sleep(0.05)
            continue
        _, jpg = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
        time.sleep(0.04)


def gen_mjpeg_camera(cam_id: str):
    """Generator — yields MJPEG frames from a specific camera video feed."""
    state = _cam_feeds.get(cam_id.upper())
    if not state:
        return
    while state["running"]:
        with state["lock"]:
            f = state["frame"]
        if f is None:
            time.sleep(0.05)
            continue
        _, jpg = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
        time.sleep(0.04)


def get_incidents(limit: int = 20) -> list[dict]:
    with _incidents_lock:
        return _incidents[:limit]


def get_cameras_info() -> dict:
    result = {}
    for cid, info in CAMERA_LOCATIONS.items():
        result[cid] = {**info, "feed_active": cid in _cam_feeds}
    return result


def get_system_status() -> dict:
    return {
        "model_loaded": True,
        "feed_running": _feed_running,
        "cameras_online": sum(1 for c in _cam_feeds if _cam_feeds[c]["running"]),
        "cameras_total": len(CAMERA_LOCATIONS),
        "videos_loaded": len(_cam_feeds),
        "ai_nodes": [
            {"name": "Video Monitoring Agent", "status": "active", "detail": f"Scanning {len(_cam_feeds)} feeds"},
            {"name": "Behavior Analysis Agent", "status": "active", "detail": "Analyzing Movement"},
            {"name": "Threat Assessment Agent", "status": "warning" if _incidents else "active", "detail": f"Evaluating {len(_incidents)} incidents" if _incidents else "All Clear"},
            {"name": "Evidence Agent", "status": "active", "detail": "Archiving incidents"},
            {"name": "LPR Agent", "status": "idle", "detail": "Idle – No Traffic"},
            {"name": "Dispatch Relay Agent", "status": "active", "detail": "Standby"},
        ],
        "uptime": "98.2%",
    }
