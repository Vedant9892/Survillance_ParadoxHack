"""MongoDB service — stores image/frame URL references."""

from pymongo import MongoClient
from backend.config.settings import settings


_client: MongoClient | None = None


def get_db():
    """Return the survillancex MongoDB database handle."""
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client[settings.MONGODB_DB]


# ── Frame URLs ───────────────────────────────────────────

def save_frame_url(video_id: str, frame_url: str, timestamp: str) -> str:
    """
    Store a frame URL document.

    Returns:
        Inserted document ID as string.
    """
    doc = {
        "video_id": video_id,
        "frame_url": frame_url,
        "timestamp": timestamp,
    }
    result = get_db()["frames"].insert_one(doc)
    return str(result.inserted_id)


def get_frame_urls(video_id: str) -> list[dict]:
    """Fetch all frame URL docs for a given video_id."""
    cursor = get_db()["frames"].find(
        {"video_id": video_id}, {"_id": 0}
    )
    return list(cursor)


def save_video_record(video_id: str, filename: str, local_path: str) -> str:
    """Store a video metadata document. Returns inserted ID."""
    doc = {
        "video_id": video_id,
        "filename": filename,
        "local_path": local_path,
    }
    result = get_db()["videos"].insert_one(doc)
    return str(result.inserted_id)
