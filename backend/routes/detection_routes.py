"""Detection routes — POST /detect endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.detection_service import run_detection_pipeline

router = APIRouter()


class DetectRequest(BaseModel):
    image: str  # base64-encoded image


class IncidentOut(BaseModel):
    type: str
    confidence: float


class DetectResponse(BaseModel):
    threat: bool
    detections: list[dict] = []
    incidents: list[IncidentOut] = []
    analysis: str | None = None
    explanation: str | None = None


@router.post("/detect", response_model=DetectResponse)
async def detect(req: DetectRequest):
    """
    Receive a base64 image → run full detection pipeline → return result.

    Flow: DetectionAgent → ThreatAgent (Grok) → XAIAgent → response
    """
    try:
        result = await run_detection_pipeline(req.image)
        return DetectResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
