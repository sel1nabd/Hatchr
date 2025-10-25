# Hatchr Setup Guide

## Complete AI-Powered Startup Generator
**GPT-4o + Sonnet 4.5 + Render.com = Instant Deployable Backends**

---

## What Does This Do?

Hatchr generates **complete, deployable FastAPI backends** from a single prompt:

1. **User Input**: "Build a task manager for remote teams"
2. **GPT-4o**: Researches competitors, identifies features, creates detailed spec
3. **Sonnet 4.5**: Generates complete FastAPI + SQLite code in one shot
4. **Local Storage**: Saves files to `projects/` folder and creates zip
5. **Render Deployment**: Auto-deploys to Render.com
6. **Result**: Live backend URL like `https://task-mgmt-xyz.onrender.com`

---

## Prerequisites

You need 3 API keys:

### 1. OpenAI API Key (GPT-4o) ✅ ALREADY CONFIGURED
- Already set in `.env`
- No action needed

### 2. Anthropic API Key (Sonnet 4.5) ⚠️ REQUIRED
- Already set in `.env` with your key
- Verified: `sk-ant-api03-9rug9UBBrYnpto...`

### 3. Render.com API Key (Deployment) ⚠️ REQUIRED
- Go to: https://dashboard.render.com/u/settings#api-keys
- Create new API key
- Add to `.env`: `RENDER_API_KEY=rnd_...`
- Free tier available

---

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p projects tmp

# Run the backend
python main.py
```

Backend starts at: `http://localhost:8001`
API docs: `http://localhost:8001/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend starts at: `http://localhost:3000`

---

## Configuration

Add your Render API key to `.env`:

```bash
# In backend/.env
RENDER_API_KEY=rnd_your-key-here
```

All other keys are already configured!

---

## Testing Without Deployment

To test code generation without deploying to Render:

```bash
# Start backend
cd backend && python main.py

# In another terminal, send test request
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a simple todo API", "verified": false}'

# Check generated files in:
ls -la projects/
```

---

## Full Flow Test

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open: http://localhost:3000
4. Enter prompt: "Build a recipe sharing API"
5. Click "Generate Startup"
6. Watch progress (2-5 minutes)
7. Get live URL when complete!

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/generate` | Start generation |
| `GET /api/status/{job_id}` | Poll job status |
| `GET /api/project/{project_id}` | Get project details |
| `GET /download/{project_id}` | Download project zip |

---

## File Structure

```
backend/
├── main.py                 # Main FastAPI app
├── generation_service.py   # GPT-4o + Sonnet logic
├── deploy_service.py       # Render deployment
├── projects/               # Generated projects
│   └── {uuid}/
│       ├── main.py
│       ├── requirements.txt
│       └── README.md
└── tmp/                    # Zip files
    └── {uuid}.zip
```

---

## Costs

- **GPT-4o**: ~$0.01-0.02 per generation
- **Sonnet 4.5**: ~$0.03-0.05 per generation
- **Render.com**: Free tier (750 hours/month)

**Total**: ~$0.05 per startup + free hosting

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Key is already in `.env`, restart backend

### "RENDER_API_KEY not found"
- Add your Render API key to `.env`
- Get it from: https://dashboard.render.com/u/settings#api-keys

### Generated code has errors
- Check `projects/{uuid}/` for generated files
- Sonnet is 99% reliable but you can manually edit if needed

---

## Production Deployment

Update `base_url` in `main.py` line 130:

```python
# Change from:
base_url = "http://localhost:8001"

# To your deployed URL:
base_url = "https://your-hatchr-app.onrender.com"
```

---

Built with ❤️ using GPT-4o, Sonnet 4.5, and Render.com
