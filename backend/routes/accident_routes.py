"""Accident routes — video upload and accident detection endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.video_processing_service import process_accident_video

router = APIRouter()


@router.post("/upload_accident_video")
async def upload_accident_video(file: UploadFile = File(...)):
    """
    Upload a video file → run full accident detection pipeline → return report.

    Flow:
      Video → Local Storage + MongoDB
      → AccidentDetectionAgent
      → AccidentAnalysisAgent (Grok)
      → ReportGenerationAgent → Supabase
      → AlertAgent
      → Response
    """
    # Validate file type
    allowed_types = {
        "video/mp4", "video/avi", "video/x-msvideo",
        "video/quicktime", "video/x-matroska",
    }
    content_type = file.content_type or ""
    if content_type not in allowed_types and not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = await process_accident_video(file_bytes, file.filename or "upload.mp4")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")
