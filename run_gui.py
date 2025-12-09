#!/usr/bin/env python3
"""
Run script for IaC Factory GUI.
This script starts the FastAPI server for the GUI.
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def main():
    """Main entry point for the GUI server."""
    try:
        import uvicorn
        from backend.main import app
    except ImportError as e:
        print(f"❌ Error: Missing dependency - {e}")
        print("\n📦 Please install the GUI package:")
        print("   pip install -e .")
        print("\n   Or install dependencies:")
        print("   pip install fastapi uvicorn[standard] pydantic python-multipart")
        sys.exit(1)
    
    print("🚀 Starting IaC Factory GUI...")
    print("📍 Server will be available at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop\n")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(current_dir / "backend"), str(current_dir / "frontend")]
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
