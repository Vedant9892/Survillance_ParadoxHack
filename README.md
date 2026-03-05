# SurvillanceX

AI-powered surveillance system with threat detection, Grok AI analysis, and explainable AI reasoning.

## Architecture

```
SurvillanceX/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── config/settings.py         # Environment-based configuration
│   ├── routes/detection_routes.py # POST /api/detect endpoint
│   ├── services/
│   │   ├── detection_service.py   # Orchestrates full pipeline
│   │   └── grok_service.py        # Grok AI integration
│   ├── agents/
│   │   ├── detection_agent.py     # Runs YOLO + behavior analysis
│   │   ├── threat_agent.py        # Sends frame to Grok for analysis
│   │   └── xai_agent.py           # Generates explainable reasoning
│   ├── models/
│   │   ├── person_detector.py     # YOLOv8 person/weapon detector
│   │   └── crowd_detector.py      # Crowd + assault behavior analyzer
│   └── utils/image_utils.py       # Base64 encode/decode, snapshot saving
├── frontend/                      # React dashboard (Vite)
├── data/snapshots/                # Saved evidence frames
├── data/logs/                     # Log files
├── requirements.txt
├── .env                           # API keys & config
└── yolov8n.pt                     # YOLOv8 model weights
```

## Pipeline Flow

```
POST /api/detect { "image": "<base64>" }
  → DetectionAgent (YOLO + behavior analysis)
  → If threat detected:
      → ThreatAgent (sends frame to Grok AI)
      → XAIAgent (generates explanation)
  → Response:
      {
        "threat": true,
        "analysis": "...Grok report...",
        "explanation": "...XAI reasoning..."
      }
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env with your GROK_API_KEY

# 3. Run backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Run frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path          | Description                     |
|--------|---------------|---------------------------------|
| POST   | /api/detect   | Run detection pipeline on frame |
| GET    | /api/health   | System health check             |

## Environment Variables

| Variable        | Default                                    | Description           |
|-----------------|--------------------------------------------|-----------------------|
| GROK_API_KEY    | (required)                                 | xAI Grok API key      |
| GROK_API_URL    | https://api.x.ai/v1/chat/completions       | Grok endpoint         |
| GROK_MODEL      | grok-3-latest                              | Grok model name       |
| YOLO_MODEL_PATH | yolov8n.pt                                 | Path to YOLO weights  |
| CROWD_THRESHOLD | 5                                          | Min persons for crowd |
| PORT            | 8000                                       | Server port           |
