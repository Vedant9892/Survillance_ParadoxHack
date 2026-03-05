"""SurvillanceX — FastAPI backend entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.routes.detection_routes import router as detection_router
from backend.routes.accident_routes import router as accident_router
from backend.routes.feed_routes import router as feed_router
from backend.config.settings import settings
from backend.services.feed_service import start_camera_feeds


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — spin up CCTV video feeds with YOLO detection
    print("\n🛡️  SurvillanceX starting...")
    os.makedirs(settings.SNAPSHOT_DIR, exist_ok=True)
    n = start_camera_feeds()
    print(f"   ✅ {n} camera video feeds started")
    print(f"   🌐 Server on http://localhost:{settings.PORT}\n")
    yield
    # Shutdown
    print("🛑 SurvillanceX shutting down...")


app = FastAPI(
    title="SurvillanceX",
    description="AI-powered surveillance threat detection API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(feed_router, prefix="/api")
app.include_router(detection_router, prefix="/api")
app.include_router(accident_router, prefix="/api")


# Health check
@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "model": "YOLOv8n",
        "grok_configured": bool(settings.GROK_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL),
        "mongodb_configured": bool(settings.MONGODB_URI),
    }


# Serve snapshots
snapshot_dir = settings.SNAPSHOT_DIR
os.makedirs(snapshot_dir, exist_ok=True)
app.mount("/api/snapshots", StaticFiles(directory=snapshot_dir), name="snapshots")

# Serve screenshots (evidence images)
@app.get("/api/screenshots/{filename}")
async def serve_screenshot(filename: str):
    path = os.path.join(snapshot_dir, filename)
    if os.path.isfile(path):
        return FileResponse(path, media_type="image/jpeg")
    return {"error": "not found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
