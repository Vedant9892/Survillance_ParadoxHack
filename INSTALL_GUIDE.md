# SurvillanceX - Setup and Dependencies

This project is a real-time surveillance system using YOLOv8 for detection and a React-based frontend.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** or **yarn**

## 1. Backend Setup (Python)

Navigate to the root directory and set up a virtual environment:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Main Backend Dependencies:
- `fastapi`, `uvicorn`: Web server
- `ultralytics`: YOLOv8 object detection
- `opencv-python`: Image processing
- `torch`: Deep learning backend
- `numpy`, `pandas`: Data handling
- `motor`: Async MongoDB driver
- `supabase`: Database integration

## 2. Frontend Setup (React + Vite)

Navigate to the `frontend` directory:

```powershell
cd frontend

# Install dependencies
npm install
```

### Main Frontend Dependencies:
- `react`, `react-dom`
- `vite`: Build tool
- `leaflet`: Interactive maps
- `@tensorflow/tfjs`, `@tensorflow-models/coco-ssd`: Local browser-side AI
- `react-router-dom`: Navigation

## 3. Running the Application

You need two terminal sessions running simultaneously.

### Terminal 1: Backend
```powershell
# From root directory
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```powershell
cd frontend
npm run dev
```

The application will be available at:
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
