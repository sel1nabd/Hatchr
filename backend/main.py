"""
Hatchr Backend - Startup-as-a-Service
Generates full-stack MVP from a single prompt
Using Perplexity Sonar + OpenAI GPT-4
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import asyncio
from datetime import datetime
import os
import json

# Import our generation service
from generation_service import generate_full_stack_app

# Initialize FastAPI app
app = FastAPI(title="Hatchr API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# In-memory storage (replace with real DB for production)
jobs_db: Dict[str, dict] = {}
projects_db: Dict[str, dict] = {}

# === REQUEST/RESPONSE MODELS ===

class GenerateRequest(BaseModel):
    prompt: str
    verified: bool = False

class StatusResponse(BaseModel):
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: int
    steps: List[Dict]
    logs: List[Dict]
    project_id: Optional[str] = None
    project_name: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    tagline: str
    stack: List[str]
    verified: bool
    marketing_assets: Dict
    launch_channels: List[Dict]

# === PLACEHOLDER INTEGRATIONS ===

class ConcordiumService:
    """Placeholder for Concordium blockchain identity verification"""

    @staticmethod
    async def create_founder_identity(user_id: str, verified: bool) -> Dict:
        """Create on-chain proof of founder identity"""
        if not verified:
            return {"concordium_verified": False}

        # TODO: Implement actual Concordium SDK integration
        # - Create identity claim
        # - Store proof hash on-chain
        # - Return verification credential

        return {
            "concordium_verified": True,
            "identity_hash": f"0x{uuid.uuid4().hex[:32]}",
            "blockchain_proof": "concordium://proof/placeholder",
            "timestamp": datetime.utcnow().isoformat()
        }

class LivepeerService:
    """Placeholder for Livepeer Daydream API video generation"""

    @staticmethod
    async def generate_marketing_video(project_summary: str, project_name: str) -> Dict:
        """Generate pitch video using Daydream API"""

        # TODO: Implement actual Livepeer Daydream API
        # - Send project summary as script
        # - Generate 30-second pitch video
        # - Return video URL and thumbnail

        return {
            "video_url": f"https://livepeer.placeholder/videos/{uuid.uuid4()}",
            "thumbnail_url": f"https://livepeer.placeholder/thumbs/{uuid.uuid4()}",
            "duration": 30,
            "status": "generated"
        }

    @staticmethod
    async def generate_pitch_deck(project_summary: str) -> Dict:
        """Generate visual pitch deck"""

        # TODO: Implement Daydream pitch deck generation
        return {
            "deck_url": f"https://livepeer.placeholder/decks/{uuid.uuid4()}",
            "slides": 5,
            "status": "generated"
        }

# === CORE GENERATION LOGIC ===

# NOTE: All generation logic moved to generation_service.py
# This uses GPT-5 + Lovable integration

# === BACKGROUND JOB PROCESSOR ===

async def process_generation(job_id: str, prompt: str, verified: bool):
    """Background task to handle full generation pipeline"""

    try:
        # Step 1: Analyze with GPT-5 and create Lovable URL
        update_step_status(job_id, 0, "in_progress")

        # Call the generation pipeline
        result = await generate_full_stack_app(prompt, job_id, add_log)

        update_step_status(job_id, 0, "completed")
        update_progress(job_id, 50)

        # Extract project data
        project_id = result['project_id']
        project_name = result['project_name']
        lovable_url = result['lovable_url']
        analysis = result['analysis']

        # Step 2: Generate marketing assets (Livepeer)
        update_step_status(job_id, 1, "in_progress")
        add_log(job_id, "Generating marketing materials...", "info")

        video = await LivepeerService.generate_marketing_video(
            f"{project_name}. {analysis['information'][:200]}",
            project_name
        )
        deck = await LivepeerService.generate_pitch_deck(analysis['information'][:500])

        update_step_status(job_id, 1, "completed")
        update_progress(job_id, 75)

        # Step 3: Create founder identity (Concordium)
        update_step_status(job_id, 2, "in_progress")
        concordium_identity = await ConcordiumService.create_founder_identity(job_id, verified)
        update_step_status(job_id, 2, "completed")
        update_progress(job_id, 100)

        # Store project in database
        projects_db[project_id] = {
            "project_id": project_id,
            "project_name": project_name,
            "tagline": analysis['information'][:200],
            "stack": ["Next.js", "TypeScript", "Tailwind CSS", "Supabase"],
            "verified": concordium_identity['concordium_verified'],
            "concordium_identity": concordium_identity,
            "lovable_url": lovable_url,
            "analysis": analysis,
            "marketing_assets": {
                "video": video,
                "pitch_deck": deck
            },
            "launch_channels": generate_launch_channels(),
            "created_at": datetime.utcnow().isoformat()
        }

        # Mark job as completed
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['project_id'] = project_id
        jobs_db[job_id]['project_name'] = project_name

        add_log(job_id, "🎉 Lovable URL ready! Click to build your app.", "success")

    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        add_log(job_id, f"Error: {str(e)}", "error")

# === HELPER FUNCTIONS ===

def add_log(job_id: str, message: str, log_type: str = "info"):
    """Add log entry to job"""
    if job_id in jobs_db:
        jobs_db[job_id]['logs'].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "type": log_type
        })

def update_step_status(job_id: str, step_index: int, status: str):
    """Update status of a specific step"""
    if job_id in jobs_db:
        jobs_db[job_id]['steps'][step_index]['status'] = status

def update_progress(job_id: str, progress: int):
    """Update overall progress percentage"""
    if job_id in jobs_db:
        jobs_db[job_id]['progress'] = progress

def generate_project_name(prompt: str) -> str:
    """Generate project name from prompt"""
    # TODO: Use LLM to generate creative name
    words = prompt.split()[:3]
    return " ".join(w.capitalize() for w in words)

def generate_tagline(prompt: str) -> str:
    """Generate tagline from prompt"""
    # TODO: Use LLM to generate compelling tagline
    return f"A smart solution for {prompt.lower()}"

def generate_launch_channels() -> List[Dict]:
    """Generate recommended launch channels"""
    return [
        {"name": "Product Hunt", "description": "Launch to tech-savvy early adopters", "priority": "high"},
        {"name": "IndieHackers", "description": "Share with indie maker community", "priority": "high"},
        {"name": "Reddit (r/SideProject)", "description": "Get feedback from builders", "priority": "medium"},
        {"name": "Twitter/X", "description": "Build in public, share progress", "priority": "medium"},
        {"name": "Hacker News", "description": "Show HN for technical audience", "priority": "medium"},
        {"name": "LinkedIn", "description": "Reach professional network", "priority": "low"},
    ]

# === API ENDPOINTS ===

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Hatchr API",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/api/generate")
async def generate_startup(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Start generating a startup from a prompt
    Returns job_id for status polling
    """

    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # Create new job
    job_id = str(uuid.uuid4())

    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "progress": 0,
        "steps": [
            {"id": 1, "title": "Analyzing your idea", "status": "pending"},
            {"id": 2, "title": "Generating marketing assets", "status": "pending"},
            {"id": 3, "title": "Creating Lovable link", "status": "pending"},
        ],
        "logs": [
            {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message": "Starting analysis...",
                "type": "info"
            }
        ],
        "project_id": None,
        "project_name": None,
        "created_at": datetime.utcnow().isoformat()
    }

    # Start background generation
    background_tasks.add_task(process_generation, job_id, request.prompt, request.verified)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Startup generation started"
    }

@app.get("/api/status/{job_id}")
async def get_status(job_id: str) -> StatusResponse:
    """
    Poll generation status
    Returns current progress, steps, and logs
    """

    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    return StatusResponse(
        job_id=job['job_id'],
        status=job['status'],
        progress=job['progress'],
        steps=job['steps'],
        logs=job['logs'],
        project_id=job.get('project_id'),
        project_name=job.get('project_name')
    )

@app.get("/api/project/{project_id}")
async def get_project(project_id: str) -> ProjectResponse:
    """
    Get complete project details including marketing assets
    """

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    return ProjectResponse(**project)

@app.get("/api/lovable-url/{project_id}")
async def get_lovable_url(project_id: str):
    """
    Get the Lovable build URL for a project
    """

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    lovable_url = project.get('lovable_url')

    if not lovable_url:
        raise HTTPException(status_code=404, detail="Lovable URL not generated yet")

    return {
        "project_id": project_id,
        "lovable_url": lovable_url,
        "project_name": project['project_name']
    }

@app.post("/api/deploy/{project_id}")
async def deploy_project(project_id: str):
    """
    Deploy project to Vercel
    """

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # TODO: Implement Vercel deployment
    # - Use Vercel API
    # - Create deployment
    # - Return deployment URL

    return {
        "status": "deploying",
        "message": "Deployment feature coming soon",
        "deployment_url": "https://your-project.vercel.app"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
