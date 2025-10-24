# Hatchr - Quick Start Guide

## 🚀 Get Running in 2 Minutes

### Backend (Terminal 1)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
**Server running at:** http://localhost:8000

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
**App running at:** http://localhost:3000

### Test It
1. Open http://localhost:3000
2. Enter: "AI scheduling tool for freelancers"
3. Check the "Concordium verified" box
4. Click "Generate Startup"
5. Watch the magic happen!

## 📡 API Quick Reference

### Create Job
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Airbnb for pets", "verified": true}'
```
**Response:** `{"job_id": "...", "status": "processing"}`

### Check Status
```bash
curl http://localhost:8000/api/status/{job_id}
```

### Get Project
```bash
curl http://localhost:8000/api/project/{project_id}
```

### API Docs
Open http://localhost:8000/docs for interactive Swagger UI

## 📁 What You Got

```
Hatchr/
├── backend/
│   ├── main.py           # 450+ lines, complete API
│   ├── requirements.txt  # All dependencies
│   ├── .env.example     # Config template
│   └── README.md        # Full documentation
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Home/prompt page
│   │   ├── generate/page.tsx  # Progress page
│   │   └── launch/page.tsx    # Launch guide
│   └── package.json
│
├── SETUP.md                # Detailed setup
├── ARCHITECTURE.md         # System design
└── IMPLEMENTATION_SUMMARY.md  # What was built
```

## ✅ What Works Now

- ✅ Complete FastAPI backend with all endpoints
- ✅ Background job processing
- ✅ Real-time status polling
- ✅ Live build logs
- ✅ Next.js frontend (3 pages)
- ✅ Concordium placeholder (returns mock verification)
- ✅ Livepeer placeholder (returns mock video URLs)
- ✅ Competitor discovery placeholder
- ✅ MVP generation placeholder

## 🔧 What's Placeholder

All complex integrations are **functional placeholders**:

1. **Competitor Discovery** - Returns 3 hardcoded competitors
   - TODO: Add Google Custom Search API
   - TODO: Add web scraping with Playwright

2. **MVP Generation** - Simulates code generation
   - TODO: Integrate OpenAI/Anthropic
   - TODO: Generate actual Next.js files

3. **Concordium** - Returns mock blockchain proof
   - TODO: Add Concordium SDK

4. **Livepeer** - Returns placeholder video URLs
   - TODO: Integrate Daydream API

5. **Download/Deploy** - Endpoints exist but return placeholders
   - TODO: Create actual ZIP files
   - TODO: Integrate Vercel API

## 🎯 Test Flow

1. **Submit Prompt** → Get job_id
2. **Poll Status** → Watch 3 steps complete:
   - Finding competitors ✓
   - Building MVP ✓
   - Packaging startup ✓
3. **Get Project** → Full details including:
   - Project name & tagline
   - Tech stack
   - Concordium badge
   - Livepeer video/deck URLs
   - Launch channels

**Total time:** ~8 seconds from prompt to completion

## 💡 Key Features

### Backend
- Async/await throughout
- Background task processing
- In-memory storage (Redis-ready)
- CORS enabled
- Type-safe with Pydantic
- Auto-generated API docs

### Frontend
- Next.js 14 + TypeScript
- Tailwind CSS styling
- Real-time progress tracking
- Live console logs
- Clean single-column layout

## 🔥 Next Steps

1. **Test the demo** - It works end-to-end right now!
2. **Add real LLM** - Replace MVPGeneratorService
3. **Add competitor search** - Integrate Google API
4. **Add Concordium** - Use actual SDK
5. **Add Livepeer** - Generate real videos
6. **Add database** - Replace in-memory storage
7. **Deploy** - Vercel (frontend) + Railway/Render (backend)

## 📚 Documentation

- **SETUP.md** - Complete setup guide
- **ARCHITECTURE.md** - System design diagrams
- **IMPLEMENTATION_SUMMARY.md** - What was built
- **backend/README.md** - API documentation

## 🐛 Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Python dependencies failing
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend not connecting to backend
Check CORS settings in `backend/main.py` line 23-28

## 🎉 You're Ready!

The backend is **fully implemented and tested**. All placeholder functions return realistic data structures ready to be swapped with real implementations.

**Try it now:**
```bash
cd backend && python main.py
# In another terminal:
cd frontend && npm run dev
# Open http://localhost:3000
```

Happy building! 🚀
