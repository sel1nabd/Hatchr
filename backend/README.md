# Hatchr Backend

**Startup-as-a-Service API** - Generate full-stack MVPs from a single prompt.

## Features

- **Prompt → Startup**: Submit an idea, get a complete codebase
- **Competitor Discovery**: Auto-find and analyze similar products
- **MVP Generation**: LLM-powered full-stack code generation
- **Concordium Integration**: Blockchain-verified founder identity (placeholder)
- **Livepeer Marketing**: Auto-generated pitch videos via Daydream API (placeholder)
- **Real-time Progress**: WebSocket-style polling for live build logs

## Tech Stack

- **FastAPI** - High-performance async Python framework
- **Pydantic** - Data validation and settings management
- **uvicorn** - ASGI server
- **httpx** - Async HTTP client (for external APIs)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Server

```bash
python main.py
# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

## API Endpoints

### `POST /api/generate`

Start generating a startup from a prompt.

**Request:**
```json
{
  "prompt": "AI scheduling tool for freelancers",
  "verified": true
}
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "processing",
  "message": "Startup generation started"
}
```

### `GET /api/status/{job_id}`

Poll generation status and logs.

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "processing",
  "progress": 66,
  "steps": [
    {"id": 1, "title": "Finding competitors", "status": "completed"},
    {"id": 2, "title": "Building MVP", "status": "in_progress"},
    {"id": 3, "title": "Packaging startup", "status": "pending"}
  ],
  "logs": [
    {"timestamp": "14:32:01", "message": "Found 3 competitors", "type": "success"},
    {"timestamp": "14:32:03", "message": "Generating components...", "type": "info"}
  ],
  "project_id": null,
  "project_name": null
}
```

### `GET /api/project/{project_id}`

Get complete project details including marketing assets.

**Response:**
```json
{
  "project_id": "proj-123",
  "project_name": "AI Scheduling Tool",
  "tagline": "A smart solution for ai scheduling tool for freelancers",
  "stack": ["Next.js 14", "Supabase", "Tailwind CSS", "TypeScript"],
  "verified": true,
  "marketing_assets": {
    "video": {
      "video_url": "https://livepeer.placeholder/videos/...",
      "thumbnail_url": "https://livepeer.placeholder/thumbs/...",
      "duration": 30
    },
    "pitch_deck": {
      "deck_url": "https://livepeer.placeholder/decks/...",
      "slides": 5
    }
  },
  "launch_channels": [...]
}
```

### `GET /api/download/{project_id}`

Download generated project as ZIP (coming soon).

### `POST /api/deploy/{project_id}`

Deploy project to Vercel (coming soon).

## Architecture

```
┌─────────────────┐
│  Next.js Client │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
├─────────────────┤
│ • Job Queue     │
│ • Background    │
│   Tasks         │
└────────┬────────┘
         │
         ├─────► DiscoveryService (find competitors)
         ├─────► MVPGeneratorService (generate code)
         ├─────► PackagingService (zip project)
         ├─────► ConcordiumService (verify identity)
         └─────► LivepeerService (create videos)
```

## Core Services

### DiscoveryService
- Search for similar startups (Google API placeholder)
- Extract competitor features (web scraping placeholder)
- Analyze tech stacks (BuiltWith API placeholder)

### MVPGeneratorService
- Generate Next.js pages and components
- Create API routes
- Set up Supabase schema
- Configure Tailwind and TypeScript
- Create Docker setup

### PackagingService
- Organize file structure
- Create Dockerfile
- Generate README and docs
- Create downloadable ZIP

### ConcordiumService (Placeholder)
- Create on-chain founder identity
- Store verification proof on blockchain
- Issue identity credentials

### LivepeerService (Placeholder)
- Generate pitch videos via Daydream API
- Create visual pitch decks
- Auto-generate marketing materials

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI app and all endpoints
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── README.md           # This file
└── generated_projects/ # Output directory (created at runtime)
```

### Adding Real Implementations

The current backend uses **placeholder functions** for complex integrations. To implement real features:

1. **Competitor Discovery**: Add Google Custom Search API and web scraping with Playwright
2. **MVP Generation**: Integrate OpenAI/Anthropic APIs for code generation
3. **Concordium**: Add Concordium SDK for blockchain verification
4. **Livepeer**: Add Livepeer Daydream API for video generation

### Testing

```bash
# Install dev dependencies
pip install pytest httpx

# Run tests
pytest

# Or test manually with curl:
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Airbnb for pets", "verified": true}'
```

## Deployment

### Docker

```bash
docker build -t hatchr-backend .
docker run -p 8000:8000 hatchr-backend
```

### Production Considerations

- Replace in-memory `jobs_db` with **Redis** or **PostgreSQL**
- Add proper **authentication** and **rate limiting**
- Use **Celery** or **RQ** for background job queue
- Set up **monitoring** and **error tracking** (Sentry, etc.)
- Add **file storage** (S3, Google Cloud Storage) for generated projects

## License

MIT
