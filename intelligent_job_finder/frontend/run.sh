#!/bin/bash

echo "🚀 Starting Intelligent Job Finder Frontend..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔗 Backend API should be running at: http://localhost:8000"
echo "-" * 50

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server..."
npm run dev 