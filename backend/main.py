"""
FastAPI backend for iac-factory GUI.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import sys
import os
from pathlib import Path

# Add project root to path for iac-factory imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from gui.backend.api_routes import router as api_router
    from gui.backend.code_generation import router as codegen_router
except ImportError:
    # Fallback for direct execution
    from api_routes import router as api_router
    from code_generation import router as codegen_router

app = FastAPI(title="IaC Factory GUI", version="0.1.0")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)
app.include_router(codegen_router)

# Mount static files
app.mount("/static", StaticFiles(directory="gui/frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    with open("gui/frontend/index.html", "r") as f:
        return f.read()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
