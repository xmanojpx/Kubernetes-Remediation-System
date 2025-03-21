from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from ..remediation.agent import RemediationAgent
import logging
from prometheus_client import make_asgi_app
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kubernetes Remediation API",
    description="API for managing Kubernetes cluster remediation actions",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Initialize the remediation agent
agent = RemediationAgent()

class Prediction(BaseModel):
    issue_type: str
    confidence: float
    target: Dict
    details: Optional[Dict] = None

class RemediationResponse(BaseModel):
    timestamp: str
    prediction: Dict
    actions: List[Dict]
    success: bool
    error: Optional[str] = None

@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/remediate")
async def remediate(prediction: Prediction):
    """Handle a prediction and execute remediation actions."""
    try:
        result = agent.handle_prediction(prediction.dict())
        return result
    except Exception as e:
        logger.error(f"Error handling prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions")
async def get_actions():
    """Get history of remediation actions."""
    return {"actions": agent.get_action_history()}

@app.get("/effectiveness")
async def get_effectiveness():
    """Get effectiveness metrics of remediation actions."""
    return agent.get_effectiveness_metrics()

@app.post("/actions/{action_id}/false-positive")
async def mark_false_positive(action_id: str, action_type: str):
    """Mark an action as a false positive for learning."""
    success = agent.mark_false_positive(action_id, action_type)
    if not success:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"status": "success"}

# Mount static files after API routes
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 