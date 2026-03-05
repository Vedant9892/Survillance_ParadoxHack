"""Feed routes — MJPEG streaming, webcam control, status, incidents, cameras."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
import cv2

from backend.services.feed_service import (
    start_webcam_feed,
    stop_webcam_feed,
    is_feed_running,
    get_latest_webcam_frame,
    get_camera_frame,
    gen_mjpeg_webcam,
    gen_mjpeg_camera,
    get_incidents,
    get_cameras_info,
    get_system_status,
    CAMERA_LOCATIONS,
)

router = APIRouter()


# ── Webcam control ─────────────────────────────────────
@router.post("/feed/start")
async def feed_start():
    result = start_webcam_feed()
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/feed/stop")
async def feed_stop():
    return stop_webcam_feed()


# ── MJPEG streams ─────────────────────────────────────
@router.get("/feed")
async def webcam_feed():
    if not is_feed_running():
        raise HTTPException(status_code=400, detail="Webcam feed not started")
    return StreamingResponse(
        gen_mjpeg_webcam(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/feed/{cam_id}")
async def camera_feed(cam_id: str):
    cam_id = cam_id.upper()
    if cam_id not in CAMERA_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Camera {cam_id} not found")
    frame = get_camera_frame(cam_id)
    if frame is None:
        # Return a placeholder dark frame instead of 404
        import numpy as np
        placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
        cv2.putText(placeholder, f"{cam_id} — Connecting...", (150, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 242, 255), 1)
        _, jpg = cv2.imencode(".jpg", placeholder)
        return Response(content=jpg.tobytes(), media_type="image/jpeg")

    return StreamingResponse(
        gen_mjpeg_camera(cam_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# ── Snapshot ───────────────────────────────────────────
@router.get("/feed/snapshot")
async def snapshot():
    frame = get_latest_webcam_frame()
    if frame is None:
        raise HTTPException(status_code=404, detail="No frame available")
    _, jpg = cv2.imencode(".jpg", frame)
    return Response(content=jpg.tobytes(), media_type="image/jpeg")


# ── Data endpoints ─────────────────────────────────────
@router.get("/incidents")
async def incidents_list():
    return get_incidents(limit=20)


@router.get("/cameras")
async def cameras_list():
    return get_cameras_info()


@router.get("/status")
async def system_status():
    return get_system_status()
