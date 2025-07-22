"""
MarkerEngine API v1
-------------------
This FastAPI application provides endpoints to interact with the MarkerEngine.
It allows for listing analysis profiles and running text analyses.
"""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any, List
import uuid

# --- Local Modules ---
# Assuming they are in the same directory or the python path is configured correctly.
from .profile_manager import ProfileManager

# --- API Initialization ---
app = FastAPI(
    title="MarkerEngine API",
    version="1.0",
    description="API for running semantic and systemic text analysis based on marker profiles.",
)

# --- Global Objects & Configuration ---
# Load the ProfileManager on startup
try:
    REGISTRY_PATH = Path(__file__).parent / 'registry.yaml'
    profile_manager = ProfileManager(REGISTRY_PATH)
    print(f"✅ ProfileManager loaded successfully from: {REGISTRY_PATH}")
except FileNotFoundError:
    print(f"❌ CRITICAL: registry.yaml not found. The API will not work correctly.")
    profile_manager = None # Ensure it exists but is None

# --- In-memory storage for analysis jobs (for this prototype) ---
analysis_jobs: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models for Request/Response validation ---
class AnalysisRequest(BaseModel):
    profile_id: str
    text_content: str
    context: Dict[str, Any] = {}

class AnalysisStatus(BaseModel):
    status: str
    analysis_id: str
    poll_url: str

class ProfileInfo(BaseModel):
    id: str
    name: str
    description: str
    focus_tags: List[str]

class ProfileList(BaseModel):
    profiles: List[ProfileInfo]


# --- Dummy Analysis Function (to be replaced with actual engine logic) ---
async def run_dummy_analysis(profile_id: str, text: str) -> Dict[str, Any]:
    """
    A placeholder function that simulates a long-running analysis task.
    """
    print(f"Starting dummy analysis for profile '{profile_id}'...")
    await asyncio.sleep(5)  # Simulate a 5-second analysis
    
    # Load the profile to get its structure
    profile_data = profile_manager.load_profile(profile_id)
    
    result = {
        "profile_used": profile_id,
        "marker_counts": {"C_AMBIVALENCE": 5, "A_DELAYED_REPLY": 2},
        "drift_axis": {"trend": "increasing_ambivalence"},
        "full_profile_data": profile_data # For demonstration
    }
    print("Dummy analysis complete.")
    return result


# --- API Endpoints ---

@app.get("/api/v1/profiles", response_model=ProfileList)
async def get_available_profiles():
    """
    Returns a list of all available analysis profiles that can be used.
    """
    if not profile_manager:
        raise HTTPException(status_code=500, detail="ProfileManager not initialized. Check server logs.")

    profiles = profile_manager.find_profiles_by_tags()
    # Filter to only include fields defined in ProfileInfo model
    profiles_for_response = [
        ProfileInfo(
            id=p.get('id'),
            name=p.get('name'),
            description=p.get('description'),
            focus_tags=p.get('focus_tags', [])
        ) for p in profiles
    ]
    return {"profiles": profiles_for_response}


@app.post("/api/v1/analyses", response_model=AnalysisStatus, status_code=202)
async def start_analysis(request: AnalysisRequest):
    """
    Accepts a text for analysis and starts an asynchronous analysis job.
    """
    if not profile_manager:
        raise HTTPException(status_code=500, detail="ProfileManager not initialized.")

    # Check if profile exists
    if not profile_manager.load_profile(request.profile_id):
        raise HTTPException(status_code=404, detail=f"Profile with ID '{request.profile_id}' not found.")
        
    job_id = str(uuid.uuid4())
    analysis_jobs[job_id] = {"status": "pending", "result": None}

    # Run the analysis in the background
    # In a real application, this would be handed off to a task queue like Celery
    asyncio.create_task(run_and_store_analysis(job_id, request.profile_id, request.text_content))

    return {
        "status": "pending",
        "analysis_id": job_id,
        "poll_url": f"/api/v1/analyses/{job_id}"
    }

async def run_and_store_analysis(job_id: str, profile_id: str, text: str):
    """Helper coroutine to run analysis and update the job store."""
    analysis_jobs[job_id]["status"] = "processing"
    result = await run_dummy_analysis(profile_id, text)
    analysis_jobs[job_id]["status"] = "completed"
    analysis_jobs[job_id]["result"] = result


@app.get("/api/v1/analyses/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """
    Polls for the result of a previously started analysis job.
    """
    job = analysis_jobs.get(analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found.")
    
    return job

# To run this API, save it as 'api.py' and run the following command in your terminal:
# uvicorn Marker_assist_bot.Schema_LOADER.api:app --reload 