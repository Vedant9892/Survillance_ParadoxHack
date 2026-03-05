import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration — reads from .env or environment variables."""

    # Grok API (xAI)
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")
    GROK_API_URL: str = os.getenv(
        "GROK_API_URL", "https://api.x.ai/v1/chat/completions"
    )
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-3-latest")

    # YOLO
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")

    # Detection thresholds
    CROWD_THRESHOLD: int = int(os.getenv("CROWD_THRESHOLD", "5"))

    # Snapshot storage
    SNAPSHOT_DIR: str = os.getenv(
        "SNAPSHOT_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "snapshots"),
    )

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "survillancex")

    # Local data paths
    VIDEOS_DIR: str = os.getenv(
        "VIDEOS_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "videos"),
    )
    ACCIDENT_FRAMES_DIR: str = os.getenv(
        "ACCIDENT_FRAMES_DIR",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "accident_frames"),
    )

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
