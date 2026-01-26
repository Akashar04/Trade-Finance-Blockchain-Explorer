#!/bin/bash
# Quick start script for Trade Finance Frontend

echo "================================"
echo "Trade Finance Frontend Setup"
echo "================================"
echo ""

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"
echo ""

# Navigate to frontend
cd "$(dirname "$0")/frontend" || exit 1

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Start development server
echo ""
echo "================================"
echo "Starting development server..."
echo "================================"
echo ""
echo "Frontend will open at: http://localhost:3000"
echo "Backend API at: http://localhost:8000"
echo "API Docs at: http://localhost:8000/docs"
echo ""

npm start
