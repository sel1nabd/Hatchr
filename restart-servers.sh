#!/bin/bash

echo "🚀 Starting Hatchr Servers"
echo "=========================="
echo ""

# Kill any existing processes on ports 8001 and 3000
echo "🔍 Checking for existing processes..."
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ Ports cleared"
echo ""

# Start backend
echo "🟦 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
mkdir -p projects tmp
python main.py &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   URL: http://localhost:8001"
echo "   Docs: http://localhost:8001/docs"
echo ""

# Start frontend
echo "🟩 Starting Frontend (Next.js)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   URL: http://localhost:3000"
echo ""

echo "=========================="
echo "🎉 Hatchr is running!"
echo "=========================="
echo ""
echo "Open http://localhost:3000 to get started"
echo ""
echo "To stop servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for user interrupt
wait
