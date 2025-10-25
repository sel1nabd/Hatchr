# Startup Branding Generator - Frontend Integration Guide

## Overview

The `generate_startup_branding()` function is the main function for frontend integration. It takes a startup idea and generates:
1. **Logo Image** - Professional startup logo
2. **Promotional Video** - Animated video from the logo

Perfect for your Hatchr platform where users describe their startup and get instant branding assets!

---

## Function Signature

```python
from lpfuncs import generate_startup_branding

result = generate_startup_branding(
    startup_idea: str,              # Required: Description of the startup
    startup_name: str = "",         # Optional: Name of the startup
    style: str = "modern",          # Optional: Visual style
    color_scheme: str = "",         # Optional: Color preferences
    logo_width: int = 1024,         # Optional: Logo width
    logo_height: int = 1024,        # Optional: Logo height
    video_fps: int = 8,             # Optional: Video frame rate
    motion_intensity: int = 140,    # Optional: Motion level (1-255)
    include_video: bool = True      # Optional: Generate video or not
)
```

---

## Parameters

### Required
- **`startup_idea`** (str): Description of the startup
  - Example: `"AI-powered task management for freelancers"`
  - Example: `"Sustainable fashion marketplace for eco-conscious consumers"`

### Optional
- **`startup_name`** (str): Name of the startup (will be included in prompt)
  - Default: `""`
  - Example: `"TaskMaster"`, `"EcoThreads"`

- **`style`** (str): Visual style for the logo
  - Options: `"modern"`, `"minimalist"`, `"playful"`, `"professional"`, `"tech"`, `"elegant"`
  - Default: `"modern"`

- **`color_scheme`** (str): Color preferences
  - Default: `""`
  - Example: `"blue and purple gradient"`, `"earth tones"`, `"neon colors"`

- **`logo_width`** / **`logo_height`** (int): Logo dimensions
  - Default: `1024x1024` (square, perfect for logos)
  - Can adjust for different aspect ratios

- **`video_fps`** (int): Video frame rate
  - Default: `8` (smooth motion)
  - Range: `1-30`

- **`motion_intensity`** (int): How dynamic the video is
  - Default: `140`
  - Range: `1-255` (higher = more motion)

- **`include_video`** (bool): Whether to generate video
  - Default: `True`
  - Set to `False` for faster logo-only generation

---

## Return Value

Returns a dictionary with the following structure:

```python
{
    "success": True,                    # Whether generation succeeded
    "logo_url": "https://...",          # URL to the logo image
    "video_url": "https://...",         # URL to the promotional video (or None)
    "logo_prompt": "...",               # The actual prompt used
    "metadata": {
        "startup_idea": "...",
        "startup_name": "...",
        "style": "modern",
        "color_scheme": "...",
        "logo_dimensions": "1024x1024",
        "video_fps": 8,
        "motion_intensity": 140
    }
}
```

### On Failure:
```python
{
    "success": False,
    "error": "Error message here",
    "logo_url": None,
    "video_url": None,
    ...
}
```

---

## Usage Examples

### Example 1: Basic Usage (Frontend Style)

```python
from lpfuncs import generate_startup_branding

# User input from frontend form
user_input = {
    "idea": "AI scheduling assistant for busy professionals",
    "name": "CalendarAI"
}

# Generate branding
result = generate_startup_branding(
    startup_idea=user_input["idea"],
    startup_name=user_input["name"]
)

# Send back to frontend
if result["success"]:
    response = {
        "logo": result["logo_url"],
        "video": result["video_url"],
        "message": "Branding generated successfully!"
    }
else:
    response = {
        "error": result["error"],
        "message": "Failed to generate branding"
    }
```

### Example 2: With Style Customization

```python
result = generate_startup_branding(
    startup_idea="Sustainable fashion marketplace connecting eco-conscious consumers",
    startup_name="EcoThreads",
    style="elegant",
    color_scheme="earth tones, green and beige"
)

print(f"Logo: {result['logo_url']}")
print(f"Video: {result['video_url']}")
```

### Example 3: Logo Only (Faster)

```python
# For quick prototyping or when video isn't needed
result = generate_startup_branding(
    startup_idea="Food delivery service for healthy meals",
    startup_name="HealthBite",
    style="playful",
    color_scheme="fresh greens and orange",
    include_video=False  # Skip video generation
)

# Only returns logo
print(f"Logo: {result['logo_url']}")
print(f"Video: {result['video_url']}")  # Will be None
```

### Example 4: High Motion Promotional Video

```python
result = generate_startup_branding(
    startup_idea="Fitness app with AI personal trainer",
    startup_name="FitGenius",
    style="tech",
    color_scheme="electric blue and neon pink",
    video_fps=10,           # Smoother video
    motion_intensity=200    # Very dynamic motion
)
```

---

## FastAPI Integration

### Add to your `main.py`:

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from lpfuncs import generate_startup_branding
import uuid

app = FastAPI()

class BrandingRequest(BaseModel):
    startup_idea: str
    startup_name: str = ""
    style: str = "modern"
    color_scheme: str = ""

# Store for jobs (use Redis in production)
jobs = {}

@app.post("/api/generate-branding")
async def create_branding(request: BrandingRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing"}
    
    background_tasks.add_task(
        process_branding,
        job_id,
        request.startup_idea,
        request.startup_name,
        request.style,
        request.color_scheme
    )
    
    return {"job_id": job_id, "status": "processing"}

async def process_branding(job_id, idea, name, style, colors):
    result = generate_startup_branding(
        startup_idea=idea,
        startup_name=name,
        style=style,
        color_scheme=colors
    )
    
    jobs[job_id] = {
        "status": "completed" if result["success"] else "failed",
        "logo_url": result.get("logo_url"),
        "video_url": result.get("video_url"),
        "error": result.get("error")
    }

@app.get("/api/branding-status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})
```

---

## Frontend Integration (TypeScript/React)

```typescript
// api.ts
export async function generateBranding(data: {
  startupIdea: string;
  startupName?: string;
  style?: string;
  colorScheme?: string;
}) {
  const response = await fetch('http://localhost:8000/api/generate-branding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      startup_idea: data.startupIdea,
      startup_name: data.startupName || '',
      style: data.style || 'modern',
      color_scheme: data.colorScheme || ''
    })
  });
  
  return response.json();
}

export async function checkBrandingStatus(jobId: string) {
  const response = await fetch(`http://localhost:8000/api/branding-status/${jobId}`);
  return response.json();
}

// Component usage
async function handleGenerateBranding() {
  const { job_id } = await generateBranding({
    startupIdea: "AI task manager for freelancers",
    startupName: "TaskMaster"
  });
  
  // Poll for status
  const interval = setInterval(async () => {
    const status = await checkBrandingStatus(job_id);
    
    if (status.status === 'completed') {
      setLogoUrl(status.logo_url);
      setVideoUrl(status.video_url);
      clearInterval(interval);
    }
  }, 3000);
}
```

---

## Style Guide

### Available Styles:

1. **`modern`** - Clean, contemporary, sleek, minimalist
2. **`minimalist`** - Ultra simple, geometric, understated
3. **`playful`** - Colorful, fun, friendly, whimsical
4. **`professional`** - Corporate, refined, sophisticated
5. **`tech`** - Futuristic, digital, innovative, high-tech
6. **`elegant`** - Luxurious, premium, refined, classy

### Color Scheme Examples:

- `"blue and purple gradient"`
- `"earth tones, green and beige"`
- `"vibrant neon colors"`
- `"monochrome black and white"`
- `"warm orange and yellow"`
- `"cool blues and teals"`
- `"corporate navy and silver"`

---

## Performance

- **Logo Generation**: ~10-20 seconds
- **Video Generation**: ~30-60 seconds
- **Total Time**: ~40-80 seconds for complete branding

**Recommendation**: Use background tasks and polling for better UX!

---

## Error Handling

```python
result = generate_startup_branding(startup_idea="...")

if not result["success"]:
    # Handle error
    error_msg = result.get("error", "Unknown error")
    
    if "API key" in error_msg:
        # API key issue
        pass
    elif "timeout" in error_msg.lower():
        # Network timeout
        pass
    else:
        # Generic error
        pass
else:
    # Success - use the assets
    logo = result["logo_url"]
    video = result["video_url"]
```

---

## Tips for Best Results

1. **Be Descriptive**: More detailed startup ideas produce better logos
2. **Specify Colors**: Color schemes help guide the AI
3. **Choose Appropriate Style**: Match style to your startup's personality
4. **Motion Intensity**: 100-150 for subtle, 150-200 for dynamic videos
5. **Square Logos**: 1024x1024 works best for logos and app icons

---

## Testing

```bash
# Test imports
python test_lpfuncs.py

# Run example with API call (requires API key)
python lpfuncs_examples.py

# Or test directly
python -c "from lpfuncs import generate_startup_branding; \
  print(generate_startup_branding('AI task manager', 'TaskAI', include_video=False))"
```

---

## Environment Setup

```bash
# Required environment variable
export LIVEPEER_API_KEY='your_livepeer_api_key_here'

# Or in .env file
echo "LIVEPEER_API_KEY=your_key_here" >> .env
```

---

## Full Example: Complete User Flow

```python
# 1. User submits form
user_data = {
    "idea": "AI-powered scheduling assistant for busy professionals",
    "name": "CalendarAI",
    "style": "modern",
    "colors": "blue and purple"
}

# 2. Generate branding
print("🚀 Generating branding...")
result = generate_startup_branding(
    startup_idea=user_data["idea"],
    startup_name=user_data["name"],
    style=user_data["style"],
    color_scheme=user_data["colors"]
)

# 3. Handle result
if result["success"]:
    print(f"✅ Success!")
    print(f"📊 Logo: {result['logo_url']}")
    print(f"🎬 Video: {result['video_url']}")
    
    # Save to database
    save_to_database({
        "user_id": user.id,
        "startup_name": result["metadata"]["startup_name"],
        "logo_url": result["logo_url"],
        "video_url": result["video_url"],
        "created_at": datetime.now()
    })
    
    # Return to user
    return {
        "success": True,
        "assets": {
            "logo": result["logo_url"],
            "video": result["video_url"]
        }
    }
else:
    print(f"❌ Failed: {result['error']}")
    return {"success": False, "error": result["error"]}
```
