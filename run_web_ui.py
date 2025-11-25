"""
Startup script for the AI Content Factory web interface.
Run this to launch the FastAPI server and open the web UI.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    """Launch the FastAPI server and open the web interface."""
    print("=" * 60)
    print("🚀 AI Content Factory - Web Interface")
    print("=" * 60)

    # Get the path to the API app
    api_path = Path(__file__).parent / "src" / "ai_content_factory" / "api" / "app.py"

    if not api_path.exists():
        print(f"❌ Error: Could not find app.py at {api_path}")
        sys.exit(1)

    print("\n📦 Starting FastAPI server...")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - Dashboard: http://localhost:8000")
    print("\n⏳ Please wait while the server starts...\n")

    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8000")

    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start the FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.ai_content_factory.api.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        print("   Thank you for using AI Content Factory!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
