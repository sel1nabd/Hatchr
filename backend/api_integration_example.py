"""
Example API integration for lpfuncs.py with FastAPI
Shows how to add the startup branding endpoint to main.py
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

# Import the branding function
from lpfuncs import generate_startup_branding

app = FastAPI()

# Request model for frontend
class StartupBrandingRequest(BaseModel):
    startup_idea: str
    startup_name: Optional[str] = ""
    style: Optional[str] = "modern"  # modern, minimalist, playful, professional, tech, elegant
    color_scheme: Optional[str] = ""
    include_video: Optional[bool] = True


# Response model
class StartupBrandingResponse(BaseModel):
    job_id: str
    status: str
    message: str


# Store for async jobs (in production, use Redis or database)
branding_jobs = {}


@app.post("/api/generate-branding", response_model=StartupBrandingResponse)
async def generate_branding_endpoint(
    request: StartupBrandingRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate startup logo and promotional video.
    
    Frontend sends:
    {
        "startup_idea": "AI task manager for freelancers",
        "startup_name": "TaskAI",
        "style": "modern",
        "color_scheme": "blue and purple",
        "include_video": true
    }
    
    Returns job_id to poll for status.
    """
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    branding_jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "logo_url": None,
        "video_url": None,
        "error": None
    }
    
    # Start background task
    background_tasks.add_task(
        process_branding,
        job_id,
        request.startup_idea,
        request.startup_name,
        request.style,
        request.color_scheme,
        request.include_video
    )
    
    return StartupBrandingResponse(
        job_id=job_id,
        status="processing",
        message="Branding generation started"
    )


async def process_branding(
    job_id: str,
    startup_idea: str,
    startup_name: str,
    style: str,
    color_scheme: str,
    include_video: bool
):
    """Background task to generate branding"""
    
    try:
        # Update progress
        branding_jobs[job_id]["progress"] = 10
        
        # Call the branding function
        result = generate_startup_branding(
            startup_idea=startup_idea,
            startup_name=startup_name,
            style=style,
            color_scheme=color_scheme,
            include_video=include_video,
            motion_intensity=140
        )
        
        if result["success"]:
            branding_jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "logo_url": result["logo_url"],
                "video_url": result["video_url"],
                "metadata": result["metadata"]
            })
        else:
            branding_jobs[job_id].update({
                "status": "failed",
                "progress": 0,
                "error": result.get("error", "Unknown error")
            })
            
    except Exception as e:
        branding_jobs[job_id].update({
            "status": "failed",
            "progress": 0,
            "error": str(e)
        })


@app.get("/api/branding-status/{job_id}")
async def get_branding_status(job_id: str):
    """
    Check status of branding generation job.
    
    Frontend polls this endpoint to get updates.
    """
    
    if job_id not in branding_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return branding_jobs[job_id]


# Example usage in your existing main.py:
"""
Add to your main.py:

from lpfuncs import generate_startup_branding

# In your process_generation function or similar:
async def generate_startup_assets(startup_name: str, startup_description: str):
    
    # Generate branding
    branding = generate_startup_branding(
        startup_idea=startup_description,
        startup_name=startup_name,
        style="modern",
        include_video=True
    )
    
    if branding["success"]:
        return {
            "logo": branding["logo_url"],
            "promo_video": branding["video_url"]
        }
    else:
        raise Exception(f"Branding generation failed: {branding['error']}")
"""

if __name__ == "__main__":
    import uvicorn
    print("Starting example API server...")
    print("Test with:")
    print('  curl -X POST http://localhost:8001/api/generate-branding \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"startup_idea": "AI task manager", "startup_name": "TaskAI"}\'')
    uvicorn.run(app, host="0.0.0.0", port=8001)
