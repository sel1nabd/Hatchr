# Hatchr Comprehensive Logging Guide

## Overview

I've added extensive logging throughout the entire Hatchr system so you can monitor everything in dev tools and production logs. Every major operation now logs detailed information about what's happening.

---

## Logging Configuration

All modules use Python's `logging` module with a consistent format:

```
2025-10-25 14:32:15,123 - module_name - INFO - Message
```

**Log Levels Used:**
- `INFO` - Normal operations, successful actions
- `WARNING` - Non-critical issues, fallbacks
- `ERROR` - Failures, exceptions
- `DEBUG` - Detailed debugging info (currently minimal)

---

## What Gets Logged

### 1. **Request/Response Middleware** (`main.py`)

Every HTTP request logs:
```
================================================================================
📥 INCOMING REQUEST
   Method: POST
   Path: /api/generate
   Query Params: {}
   Client: 127.0.0.1
================================================================================
```

Every response logs:
```
================================================================================
📤 RESPONSE SENT
   Status Code: 200
   Duration: 1.234s
   Path: /api/generate
================================================================================
```

### 2. **Multi-Tenant Host** (`multitenant_service.py`)

**When loading a project:**
```
================================================================================
🔄 LOADING PROJECT INTO MULTI-TENANT HOST
   Project Name: Todo API
   Project ID: abc123-def456
   Code Length: 5432 characters
================================================================================
📦 Creating module: generated_project_abc123_def456
✅ Module created successfully
⚙️  Executing generated code...
📝 Code execution stdout: ...
✅ Found FastAPI app instance in generated code
📊 Generated app has 8 routes
================================================================================
✅ SUCCESSFULLY LOADED PROJECT: Todo API
   Total hosted projects: 1
================================================================================
```

**When routing requests:**
```
================================================================================
🔀 ROUTING REQUEST TO GENERATED PROJECT
   Project ID: abc123-def456
   Method: GET
   Path: /projects/abc123-def456/items
   Query Params: {'limit': '10'}
================================================================================
✅ Found app for project abc123-def456
🎯 Routing to generated app path: /items
📡 Calling generated app...
================================================================================
✅ SUCCESSFULLY ROUTED TO GENERATED PROJECT
   Project: abc123-def456
   Target Path: /items
================================================================================
```

### 3. **Deployment Service** (`deploy_service.py`)

**When deploying:**
```
================================================================================
🚀 DEPLOYING TO MULTI-TENANT HOST
   Project: Todo API
   Project ID: abc123-def456
   Base URL: https://hatchr.onrender.com
   Code Length: 5432 characters
================================================================================
📦 Loading project into multi-tenant host...
✅ Project loaded successfully
================================================================================
✅ DEPLOYMENT SUCCESSFUL!
   Service ID: abc123-def456
   Live URL: https://hatchr.onrender.com/projects/abc123-def456
   API Docs: https://hatchr.onrender.com/projects/abc123-def456/docs
   Hosting Type: Multi-Tenant
================================================================================
```

**When checking status:**
```
🔍 Checking status of project: abc123-def456
✅ Project abc123-def456 is LIVE
```

### 4. **Database Operations** (`database.py`)

**When storing a project:**
```
================================================================================
💾 STORING PROJECT IN DATABASE
   Project: Todo API
   Project ID: abc123-def456
   Files: ['main.py', 'requirements.txt', 'README.md']
================================================================================
✅ Project stored successfully in database
   Database: /path/to/hatchr.db
================================================================================
```

**When retrieving:**
```
🔍 Retrieving project from database: abc123-def456
✅ Found project: Todo API
   Created: 2025-10-25T14:32:15.123Z
   Files reconstructed: ['main.py', 'requirements.txt', 'README.md']
```

### 5. **Startup Event** (`main.py`)

When the server starts:
```
✅ Database initialized at /path/to/hatchr.db

================================================================================
🔄 RELOADING GENERATED PROJECTS INTO MULTI-TENANT HOST
================================================================================
📦 Found 3 projects in database
   ✅ Loaded: Todo API (abc123...)
   ✅ Loaded: Blog Platform (def456...)
   ✅ Loaded: E-commerce API (ghi789...)
================================================================================
✅ MULTI-TENANT HOST READY - 3 projects loaded
================================================================================
```

---

## How to View Logs

### Local Development

**Terminal:**
```bash
cd backend
../venv/bin/python main.py
```

You'll see all logs in real-time in your terminal.

### Production (Render)

1. **Render Dashboard:**
   - Go to https://dashboard.render.com
   - Select your `hatchr-backend` service
   - Click "Logs" tab
   - See real-time logs with all the details

2. **Via Render CLI:**
   ```bash
   render logs hatchr-backend -f
   ```

3. **API (if needed):**
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.render.com/v1/services/YOUR_SERVICE_ID/logs
   ```

---

## Example: Complete Request Flow Logs

When a user generates a new project, you'll see logs like this:

```
[Incoming Request]
================================================================================
📥 INCOMING REQUEST
   Method: POST
   Path: /api/generate
   Query Params: {}
   Client: 192.168.1.100
================================================================================

[GPT-4o Enrichment - from generation_service.py]
================================================================================
🔵 GPT-4O PROMPT ENRICHMENT STARTING
📥 USER IDEA: Build a todo list API
================================================================================
🔄 Calling OpenAI GPT-4o...
✅ GPT-4o ENRICHMENT COMPLETE
   Project: TaskMaster API
   Examples: Todoist, Microsoft To Do, Any.do
   Features: 5 identified
================================================================================

[Sonnet Code Generation - from generation_service.py]
================================================================================
🟣 SONNET 4.5 CODE GENERATION STARTING
📥 Project: TaskMaster API
================================================================================
🔄 Calling Anthropic Sonnet 4.5...
✅ SONNET 4.5 GENERATION COMPLETE
   Response Length: 12345 chars
   Input Tokens: 2000
   Output Tokens: 3000
================================================================================
📁 Extracted 3 files:
   - main.py (5432 chars)
   - requirements.txt (150 chars)
   - README.md (1200 chars)
================================================================================

[Database Storage]
================================================================================
💾 STORING PROJECT IN DATABASE
   Project: TaskMaster API
   Project ID: abc123-def456
   Files: ['main.py', 'requirements.txt', 'README.md']
================================================================================
✅ Project stored successfully in database
================================================================================

[Deployment]
================================================================================
🚀 DEPLOYING TO MULTI-TENANT HOST
   Project: TaskMaster API
   Project ID: abc123-def456
   Base URL: https://hatchr.onrender.com
================================================================================
[... loading logs ...]
✅ DEPLOYMENT SUCCESSFUL!
   Live URL: https://hatchr.onrender.com/projects/abc123-def456
================================================================================

[Response Sent]
================================================================================
📤 RESPONSE SENT
   Status Code: 200
   Duration: 45.678s
   Path: /api/generate
================================================================================
```

---

## Monitoring Tips

### 1. **Watch for Errors**

Look for lines with `❌` emoji - these indicate failures:

```
❌ FAILED TO LOAD PROJECT: Todo API
   Error: Generated code does not contain 'app' variable
```

### 2. **Track Performance**

Look for duration logs:
```
📤 RESPONSE SENT
   Duration: 1.234s  <-- Request took 1.2 seconds
```

### 3. **Monitor Multi-Tenant Host**

Check startup logs to see how many projects loaded:
```
✅ MULTI-TENANT HOST READY - 15 projects loaded
```

### 4. **Debug Routing Issues**

If a generated project isn't accessible, look for:
```
❌ Project abc123 not found in multi-tenant host
   Available projects: ['def456', 'ghi789']
```

---

## Log Analysis Commands

**Count requests:**
```bash
grep "INCOMING REQUEST" logs.txt | wc -l
```

**Find errors:**
```bash
grep "❌" logs.txt
```

**Track specific project:**
```bash
grep "abc123-def456" logs.txt
```

**Monitor deployment times:**
```bash
grep "Duration:" logs.txt | grep "api/generate"
```

---

## What Makes This Logging Special

1. **Emoji Icons** 🎨
   - Makes logs visually scannable
   - Easy to spot different event types
   - `📥` = Request in, `📤` = Response out, `✅` = Success, `❌` = Error

2. **Separator Lines** 📊
   - `===` lines make log sections clear
   - Easy to see where one operation ends and another begins

3. **Contextual Information** 📝
   - Every log includes relevant details (IDs, names, URLs)
   - No need to correlate multiple log lines

4. **Hierarchical Structure** 🏗️
   - Indented details under main log messages
   - Shows relationships between operations

5. **Performance Metrics** ⚡
   - Request durations logged
   - Token counts for AI calls
   - File sizes and counts

---

## Logging Best Practices (Already Implemented)

✅ Every major function logs entry and exit
✅ Errors include full context and tracebacks
✅ Success messages confirm operations completed
✅ IDs included for tracking across services
✅ Timestamps automatic via logging config
✅ Consistent format across all modules

---

## Testing the Logging

Run a test request:

```bash
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a simple blog API", "verified": false}'
```

Watch your terminal/logs explode with detailed information! 🎆

---

**Your Hatchr system now has production-grade logging! 📊✨**

Every action is tracked, every error is caught, and you can monitor everything in real-time.
