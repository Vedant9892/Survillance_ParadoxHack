# SurvillanceX

SurvillanceX is an AI-powered surveillance platform designed for threat detection, incident monitoring, and explainable security analysis. The repository combines a FastAPI backend for detection and telemetry workflows with a Vite-based React frontend for operational monitoring and review.

## Project Overview

The application is built to process live or recorded security footage, analyze frames for potential threats, and present results through a web dashboard. The backend orchestrates detection services, AI analysis, storage of evidence frames, and API responses. The frontend provides a structured operator interface for reviewing incidents, live feeds, maps, alerts, and model-driven analysis outputs.

## Professional Project Description

This project is intended for security and operations teams that need a practical surveillance workflow with centralized monitoring and decision support. It focuses on automated detection, explainable AI reasoning, and clear incident visibility rather than raw model output alone. The codebase is organized to support local development, iterative feature expansion, and deployment of backend and frontend components as separate services.

## Key Features

- AI-assisted threat detection pipeline with frame-level analysis.
- Explainable output for threat reasoning and incident review.
- FastAPI backend with modular routes and service layers.
- React and Vite frontend for dashboard-style surveillance monitoring.
- Persistent storage for snapshots, logs, and video-related artifacts.
- Support for live feed, incidents, map, alerts, agents, and video analysis views.
- Environment-driven configuration for API keys, model paths, and storage locations.

## Tech Stack / Technologies Used

- Python and FastAPI for the backend API.
- Uvicorn for ASGI server execution.
- React for the frontend user interface.
- Vite for frontend development and bundling.
- OpenCV for frame processing and image handling.
- Ultralytics YOLOv8 for detection workflows.
- TensorFlow.js and COCO-SSD for browser-side analysis capabilities.
- Supabase and MongoDB integrations for external storage and data services.
- Python dotenv support for environment configuration.

## File Structure

```text
Survillance_ParadoxHack/
├── backend/
│   ├── agents/
│   ├── config/
│   │   └── settings.py
│   ├── models/
│   ├── routes/
│   │   ├── accident_routes.py
│   │   ├── detection_routes.py
│   │   └── feed_routes.py
│   ├── services/
│   │   ├── detection_service.py
│   │   ├── feed_service.py
│   │   ├── grok_service.py
│   │   ├── mongodb_service.py
│   │   ├── supabase_service.py
│   │   └── video_processing_service.py
│   ├── utils/
│   ├── __init__.py
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Agents/
│   │   │   ├── Alerts/
│   │   │   ├── Dashboard/
│   │   │   ├── Incidents/
│   │   │   ├── LiveFeed/
│   │   │   ├── MapView/
│   │   │   └── VideoAnalysis/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── package-lock.json
├── data/
│   ├── accident_frames/
│   ├── snapshots/
│   └── videos/
├── scripts/
│   └── run_server.sh
├── requirements.txt
├── .env.example
├── INSTALL_GUIDE.md
└── README.md
```

## Installation Instructions

### Prerequisites

- Python 3.11 or later.
- Node.js 18 or later.
- npm.
- Access to the required API and storage services, including Grok, Supabase, and MongoDB if you intend to use the full backend pipeline.

### Backend Installation

Create and activate a Python virtual environment from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

### Frontend Installation

Install the frontend dependencies:

```powershell
cd frontend
npm install
```

## How to Run the Project

### 1. Configure Environment Variables

Copy `.env.example` to `.env` in the repository root and fill in the required values.

Important values typically include:

- `GROK_API_KEY`
- `GROK_API_URL`
- `GROK_MODEL`
- `YOLO_MODEL_PATH`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `MONGODB_URI`
- `MONGODB_DB`
- `HOST`
- `PORT`

### 2. Start the Backend

Run the FastAPI server from the repository root:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternatively, on Unix-like systems you can use the helper script:

```bash
bash scripts/run_server.sh
```

The backend API will be available at `http://localhost:8000`.

### 3. Start the Frontend

Open a second terminal and start the React app:

```powershell
cd frontend
npm run dev
```

The frontend will typically be available at `http://localhost:5173`.

### 4. Verify the Services

- Open `http://localhost:8000/api/health` to confirm backend status.
- Open `http://localhost:8000/docs` for the generated API documentation.
- Open the frontend URL to access the surveillance dashboard.

## Environment Variables

Configuration is loaded from `.env` at the repository root.

| Variable | Purpose |
| --- | --- |
| `GROK_API_KEY` | xAI Grok API key used for threat analysis. |
| `GROK_API_URL` | Grok chat completions endpoint. |
| `GROK_MODEL` | Model name used for AI analysis. |
| `YOLO_MODEL_PATH` | Path to YOLO model weights. |
| `CROWD_THRESHOLD` | Minimum person count required to classify crowd conditions. |
| `SNAPSHOT_DIR` | Output directory for saved evidence frames. |
| `SUPABASE_URL` | Supabase project URL. |
| `SUPABASE_KEY` | Supabase service key or API key. |
| `MONGODB_URI` | MongoDB connection string. |
| `MONGODB_DB` | MongoDB database name. |
| `VIDEOS_DIR` | Directory for source or archived video files. |
| `ACCIDENT_FRAMES_DIR` | Directory for incident frame captures. |
| `HOST` | Backend bind host. |
| `PORT` | Backend port. |

## Usage Instructions

1. Start the backend and frontend services.
2. Open the frontend dashboard in a browser.
3. Review the dashboard for system status, incident counts, and live monitoring indicators.
4. Navigate to Live Feed to observe current camera streams and detections.
5. Use Incidents to inspect detected events and stored evidence.
6. Review Map, Agents, Alerts, and Video Analysis views for deeper operational insight.
7. Confirm backend health and API availability when troubleshooting or deploying updates.

## Scripts / Commands

### Backend

Run these from the repository root unless otherwise noted.

| Command | Description |
| --- | --- |
| `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` | Start the FastAPI backend in development mode. |
| `bash scripts/run_server.sh` | Start the backend using the helper shell script on Unix-like systems. |

### Frontend

Run these from the `frontend` directory.

| Command | Description |
| --- | --- |
| `npm run dev` | Start the Vite development server. |
| `npm run build` | Build the frontend for production. |
| `npm run preview` | Preview the production build locally. |

## Contribution Guidelines

1. Create a dedicated branch for your changes.
2. Keep edits focused on a single concern and preserve the existing TypeScript, Python, and React style.
3. Update documentation when you add routes, configuration, or operator-facing behavior.
4. Verify the backend and frontend still start successfully after your changes.
5. Keep pull requests concise and include a clear summary of the functional impact.

## License Information

No explicit license file is included in this repository. If you intend to publish or distribute the project, add a license that matches your deployment and collaboration requirements.