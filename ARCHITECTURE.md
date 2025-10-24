# Hatchr - System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER JOURNEY                          │
└─────────────────────────────────────────────────────────────┘

1. User enters prompt: "AI scheduling tool for freelancers"
                     ↓
2. Submit to backend (/api/generate)
                     ↓
3. Receive job_id, redirect to progress page
                     ↓
4. Poll /api/status/{job_id} every 2s
                     ↓
5. Watch 3 steps complete:
   - Finding competitors ✓
   - Building MVP ✓
   - Packaging startup ✓
                     ↓
6. Receive project_id when complete
                     ↓
7. Fetch /api/project/{project_id}
                     ↓
8. Display marketing assets & launch guide
```

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                            │
│                     (Next.js 14 + TypeScript)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Home Page     │  │  Progress Page  │  │  Launch Page    │ │
│  │   (/)           │  │  (/generate)    │  │  (/launch)      │ │
│  │                 │  │                 │  │                 │ │
│  │ • Prompt input  │  │ • 3 steps UI    │  │ • Project info  │ │
│  │ • Concordium ✓  │  │ • Progress bar  │  │ • Video/deck    │ │
│  │ • Submit button │  │ • Live logs     │  │ • Channels      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│         │                     │                     │            │
│         └─────────────────────┼─────────────────────┘            │
│                               │                                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │
                                │ HTTP/REST (CORS enabled)
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                               ↓                                  │
│                     BACKEND API LAYER                            │
│                     (FastAPI + Python)                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    API ENDPOINTS                           │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ POST   /api/generate         → Create job                 │ │
│  │ GET    /api/status/{job_id}  → Poll progress              │ │
│  │ GET    /api/project/{id}     → Get project details        │ │
│  │ GET    /api/download/{id}    → Download ZIP (TODO)        │ │
│  │ POST   /api/deploy/{id}      → Deploy to Vercel (TODO)    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 BACKGROUND TASK QUEUE                      │ │
│  │              (FastAPI BackgroundTasks)                     │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  async def process_generation():                          │ │
│  │      1. Run DiscoveryService                              │ │
│  │      2. Run MVPGeneratorService                           │ │
│  │      3. Run PackagingService                              │ │
│  │      4. Run LivepeerService                               │ │
│  │      5. Run ConcordiumService                             │ │
│  │      6. Update job status → "completed"                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   IN-MEMORY STORAGE                        │ │
│  │              (Replace with Redis + PostgreSQL)             │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │  jobs_db = {                                              │ │
│  │    "job-id-123": {                                        │ │
│  │      status: "processing",                                │ │
│  │      progress: 66,                                        │ │
│  │      steps: [...],                                        │ │
│  │      logs: [...]                                          │ │
│  │    }                                                      │ │
│  │  }                                                        │ │
│  │                                                           │ │
│  │  projects_db = {                                          │ │
│  │    "project-id-456": {                                    │ │
│  │      project_name: "...",                                 │ │
│  │      stack: [...],                                        │ │
│  │      marketing_assets: {...}                             │ │
│  │    }                                                      │ │
│  │  }                                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
┌──────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                                │
│                 (Placeholder Implementations)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │  DiscoveryService   │  │ MVPGeneratorService │               │
│  ├─────────────────────┤  ├─────────────────────┤               │
│  │ • Find competitors  │  │ • Generate Next.js  │               │
│  │ • Analyze features  │  │ • Create Supabase   │               │
│  │ • Extract tech      │  │ • Setup Tailwind    │               │
│  │                     │  │ • Add Docker        │               │
│  │ [PLACEHOLDER]       │  │ [PLACEHOLDER]       │               │
│  │ TODO: Google API    │  │ TODO: OpenAI/Claude │               │
│  │ TODO: Playwright    │  │                     │               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                   │
│  ┌─────────────────────┐  ┌─────────────────────┐               │
│  │  PackagingService   │  │ ConcordiumService   │               │
│  ├─────────────────────┤  ├─────────────────────┤               │
│  │ • Create structure  │  │ • Create identity   │               │
│  │ • Generate files    │  │ • Store on-chain    │               │
│  │ • Create ZIP        │  │ • Issue proof       │               │
│  │                     │  │                     │               │
│  │ [PLACEHOLDER]       │  │ [PLACEHOLDER]       │               │
│  │ TODO: File writer   │  │ TODO: Concordium SDK│               │
│  └─────────────────────┘  └─────────────────────┘               │
│                                                                   │
│  ┌─────────────────────┐                                         │
│  │  LivepeerService    │                                         │
│  ├─────────────────────┤                                         │
│  │ • Generate video    │                                         │
│  │ • Create pitch deck │                                         │
│  │ • Auto marketing    │                                         │
│  │                     │                                         │
│  │ [PLACEHOLDER]       │                                         │
│  │ TODO: Daydream API  │                                         │
│  └─────────────────────┘                                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow: Job Processing

```
Time  │ Action                           │ Status Updates
──────┼──────────────────────────────────┼───────────────────────
T+0s  │ POST /api/generate               │ job created
      │ • Create job_id                  │ status: "processing"
      │ • Start background task          │ progress: 0%
      │ • Return job_id to user          │ step 1: "pending"
──────┼──────────────────────────────────┼───────────────────────
T+1s  │ DiscoveryService starts          │ step 1: "in_progress"
      │ • Search competitors             │ progress: 10%
      │ • Log: "Searching..."            │
──────┼──────────────────────────────────┼───────────────────────
T+2s  │ DiscoveryService completes       │ step 1: "completed"
      │ • Found 3 competitors            │ progress: 33%
      │ • Analyzed features              │ step 2: "in_progress"
──────┼──────────────────────────────────┼───────────────────────
T+3s  │ MVPGeneratorService starts       │ progress: 40%
      │ • Generate components            │
      │ • Log: "Generating Next.js..."   │
──────┼──────────────────────────────────┼───────────────────────
T+5s  │ MVPGeneratorService completes    │ step 2: "completed"
      │ • 45 files generated             │ progress: 66%
      │ • Stack configured               │ step 3: "in_progress"
──────┼──────────────────────────────────┼───────────────────────
T+6s  │ PackagingService starts          │ progress: 75%
      │ • Create Dockerfile              │
      │ • Package files                  │
──────┼──────────────────────────────────┼───────────────────────
T+7s  │ PackagingService completes       │ step 3: "completed"
      │ • Create project_id              │ progress: 90%
──────┼──────────────────────────────────┼───────────────────────
T+8s  │ Marketing generation             │ progress: 95%
      │ • Livepeer: video + deck         │
      │ • Concordium: identity proof     │
──────┼──────────────────────────────────┼───────────────────────
T+9s  │ Complete!                        │ status: "completed"
      │ • Store in projects_db           │ progress: 100%
      │ • Return project_id              │ project_id: "..."
```

## Frontend → Backend Communication

```
┌─────────────┐                    ┌─────────────┐
│  Home Page  │                    │   Backend   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  POST /api/generate              │
       │  {prompt, verified}              │
       │─────────────────────────────────→│
       │                                  │
       │  {job_id, status}                │
       │←─────────────────────────────────│
       │                                  │
       │  redirect to /generate           │
       │                                  │
       ↓                                  │
┌──────────────┐                          │
│Progress Page │                          │
└──────┬───────┘                          │
       │                                  │
       │  GET /api/status/{job_id}        │
       │─────────────────────────────────→│
       │                                  │
       │  {progress, steps, logs}         │
       │←─────────────────────────────────│
       │                                  │
       │  ... poll every 2 seconds ...    │
       │                                  │
       │  GET /api/status/{job_id}        │
       │─────────────────────────────────→│
       │                                  │
       │  {status: "completed",           │
       │   project_id: "..."}             │
       │←─────────────────────────────────│
       │                                  │
       │  redirect to /launch             │
       │                                  │
       ↓                                  │
┌─────────────┐                           │
│ Launch Page │                           │
└──────┬──────┘                           │
       │                                  │
       │  GET /api/project/{id}           │
       │─────────────────────────────────→│
       │                                  │
       │  {name, stack, assets, etc}      │
       │←─────────────────────────────────│
       │                                  │
```

## Placeholder → Real Implementation Map

| Service | Current | Real Implementation |
|---------|---------|---------------------|
| **DiscoveryService** | Hardcoded 3 competitors | Google Custom Search API<br>Playwright web scraping<br>BuiltWith API |
| **MVPGeneratorService** | Simulated delays | OpenAI GPT-4 / Claude 3.5<br>Template engine<br>File writer |
| **PackagingService** | Returns project_id | Create directory structure<br>Write all files<br>ZIP archive |
| **ConcordiumService** | Mock hash | Concordium SDK<br>Create identity<br>Store proof on-chain |
| **LivepeerService** | Placeholder URLs | Livepeer Daydream API<br>Generate video<br>Create pitch deck |

## Scalability Path

### Current (MVP Demo)
```
Single Python process
In-memory storage
FastAPI BackgroundTasks
```

### Production Scale
```
┌─────────────────────────────────┐
│  Load Balancer (NGINX/Traefik) │
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐   ┌─────▼──────┐
│  FastAPI   │   │  FastAPI   │  (multiple instances)
│  Instance  │   │  Instance  │
└─────┬──────┘   └─────┬──────┘
      │                 │
      └────────┬────────┘
               │
      ┌────────▼────────┐
      │  Redis (Jobs)   │  (task queue)
      └─────────────────┘
               │
      ┌────────▼────────┐
      │  Celery Workers │  (background tasks)
      └─────────────────┘
               │
      ┌────────▼────────┐
      │   PostgreSQL    │  (persistent storage)
      └─────────────────┘
```

## Security Considerations

1. **API Authentication** (TODO)
   - Add JWT tokens
   - User sessions
   - API keys for external access

2. **Rate Limiting** (TODO)
   - Per-user limits
   - IP-based throttling
   - Queue management

3. **Input Validation** ✓
   - Pydantic models
   - Type checking
   - Sanitization

4. **CORS** ✓
   - Configured for localhost
   - Update for production domains

## Monitoring & Observability (TODO)

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │
    ┌────┼────┐
    │    │    │
    ↓    ↓    ↓
┌────────────────┐  ┌──────────┐  ┌──────────┐
│  Logging       │  │ Metrics  │  │ Tracing  │
│  (Sentry)      │  │ (Prom)   │  │ (Jaeger) │
└────────────────┘  └──────────┘  └──────────┘
```

## Summary

**Current Status**: Fully functional demo with placeholder services
**Next Step**: Replace placeholders with real integrations
**Architecture**: Scalable, modular, production-ready foundation
**Code Quality**: Well-documented, type-safe, async-first
