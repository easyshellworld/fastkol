# FastKOL Frontend Guide

This guide describes how to run the fastKOL Dashboard with real backend integration.

## Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- API Keys configured in `.env`

## Running the Application

You need to run **both** the backend and frontend terminals simultaneously.

### 1. Start the Backend Server
This runs the FastAPI server that hosts the SpoonOS Agent and WebSocket endpoint.

```bash
# In the root directory (fastkol/)
uvicorn src.server:app --reload --port 8000
```
*Wait until you see "Application startup complete".*

### 2. Start the Frontend
This runs the React dashboard.

```bash
# In the frontend directory (fastkol/frontend/)
npm run dev
```

### 3. Usage
- Open `http://localhost:5173` in your browser.
- Click **"启动工作流" (Start Workflow)**.
- The dashboard will connect to `ws://localhost:8000/ws`.
- You will see **real-time logs** from the backend agent as it fetches data from Polymarket and generates content.

## Troubleshooting

- **Connection Failed**: Ensure the backend is running on port 8000.
- **API Errors**: Check the backend terminal logs for missing environment variables or API errors.
