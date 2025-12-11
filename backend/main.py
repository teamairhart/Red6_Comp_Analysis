"""
Competitive Intelligence Platform - FastAPI Backend
"""
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import prompts_router, research_router, reports_router, sources_router, schedule_router, ticker_router

app = FastAPI(
    title="Competitive Intelligence API",
    description="API for competitive intelligence research platform",
    version="1.0.0"
)

# Configure CORS - reads from environment variable or defaults to localhost
# Set CORS_ORIGINS to a comma-separated list of allowed origins for production
cors_origins_str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(prompts_router)
app.include_router(research_router)
app.include_router(reports_router)
app.include_router(sources_router)
app.include_router(schedule_router)
app.include_router(ticker_router)


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
