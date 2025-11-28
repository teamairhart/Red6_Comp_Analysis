"""
Competitive Intelligence Platform - FastAPI Backend
"""
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import prompts_router, research_router, reports_router

app = FastAPI(
    title="Competitive Intelligence API",
    description="API for competitive intelligence research platform",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prompts_router)
app.include_router(research_router)
app.include_router(reports_router)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"status": "ok", "message": "Competitive Intelligence API"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
