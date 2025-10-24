# Hatchr - Setup Guide

## Overview

**Hatchr** is a Startup-as-a-Service platform that generates full-stack MVPs from a single prompt.

- **Frontend**: Next.js 14 + Tailwind CSS + TypeScript
- **Backend**: FastAPI + Python
- **Features**: Competitor discovery, MVP generation, Concordium verification (placeholder), Livepeer marketing (placeholder)

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Backend runs at: **http://localhost:8000**

API docs: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Test the Flow

1. Open http://localhost:3000
2. Enter a startup idea (e.g., "AI scheduling tool for freelancers")
3. Check "Mark as verified founder" (optional)
4. Click "Generate Startup"
5. Watch live progress on /generate page
6. View marketing assets and launch guide on /launch page

## API Endpoints

### Start Generation
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Airbnb for pets", "verified": true}'
```

### Check Status
```bash
curl http://localhost:8000/api/status/{job_id}
```

### Get Project Details
```bash
curl http://localhost:8000/api/project/{project_id}
```

## Architecture

```
┌──────────────────────┐
│   User enters prompt │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Frontend (Next.js) │
│   • Home page        │
│   • Progress page    │
│   • Launch page      │
└──────────┬───────────┘
           │ HTTP/REST
           ▼
┌──────────────────────┐
│   Backend (FastAPI)  │
│   • Job management   │
│   • Background tasks │
└──────────┬───────────┘
           │
           ├──► DiscoveryService (find competitors)
           ├──► MVPGeneratorService (generate code)
           ├──► PackagingService (create zip)
           ├──► ConcordiumService (blockchain proof)
           └──► LivepeerService (pitch videos)
```

## Current Implementation Status

### ✅ Completed
- Full FastAPI backend with all endpoints
- Background job processing
- Real-time status polling and logs
- Next.js frontend (3 pages)
- Tailwind UI components
- CORS configuration
- In-memory job storage

### 🔄 Placeholder Implementations
These are functional placeholders ready to be replaced with real integrations:

1. **ConcordiumService** - Returns mock blockchain verification
   - TODO: Integrate Concordium SDK
   - TODO: Store identity proofs on-chain

2. **LivepeerService** - Returns mock video URLs
   - TODO: Integrate Livepeer Daydream API
   - TODO: Generate actual pitch videos

3. **DiscoveryService** - Returns hardcoded competitors
   - TODO: Add Google Custom Search API
   - TODO: Add web scraping (Playwright)
   - TODO: Add BuiltWith API for tech stacks

4. **MVPGeneratorService** - Simulates code generation
   - TODO: Integrate LLM (OpenAI/Anthropic)
   - TODO: Generate actual Next.js code
   - TODO: Create Supabase schema

5. **PackagingService** - Creates mock project
   - TODO: Generate actual file structure
   - TODO: Create downloadable ZIP
   - TODO: Add Dockerfile template

6. **Deploy endpoint** - Returns placeholder URL
   - TODO: Integrate Vercel API
   - TODO: Auto-deploy generated projects

## File Structure

```
Hatchr/
├── backend/
│   ├── main.py              # Complete FastAPI app
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example        # Environment variables
│   ├── README.md           # Backend documentation
│   └── venv/               # Virtual environment
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Home/prompt page
│   │   ├── generate/
│   │   │   └── page.tsx    # Progress page
│   │   └── launch/
│   │       └── page.tsx    # Launch guide page
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
└── SETUP.md               # This file
```

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
# LLM APIs (for code generation)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Competitor Discovery
GOOGLE_CUSTOM_SEARCH_API_KEY=your_key_here
BUILTWITH_API_KEY=your_key_here

# Concordium (blockchain verification)
CONCORDIUM_NODE_URL=https://node.testnet.concordium.com
CONCORDIUM_WALLET_KEY=your_key_here

# Livepeer (video generation)
LIVEPEER_API_KEY=your_key_here
LIVEPEER_GATEWAY_URL=https://livepeer.studio/api
```

## Next Steps

1. **Test the demo** - Everything works end-to-end with mock data
2. **Add real LLM integration** - Replace MVPGeneratorService placeholders
3. **Add real competitor discovery** - Integrate Google API and web scraping
4. **Integrate Concordium** - Add actual blockchain verification
5. **Integrate Livepeer** - Generate real pitch videos
6. **Add database** - Replace in-memory storage with PostgreSQL/Redis
7. **Add authentication** - Secure the API
8. **Deploy** - Host on Vercel (frontend) + Render/Railway (backend)

## Demo Testing

The backend is fully functional and can be tested immediately:

```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Start frontend
cd frontend && npm run dev

# Terminal 3: Test API directly
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "AI scheduling tool", "verified": true}'
```

## Production Considerations

- Add proper database (PostgreSQL + Redis)
- Use Celery/RQ for background jobs
- Add authentication and rate limiting
- Implement file storage (S3/Google Cloud)
- Add monitoring and error tracking
- Set up CI/CD pipeline
- Add comprehensive tests

## License

MIT
