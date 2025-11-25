"""
Quick setup script to install FastAPI dependencies and verify the installation.
"""

import subprocess
import sys
from pathlib import Path


def check_command(command):
    """Check if a command is available."""
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("=" * 60)
    print("🔧 AI Content Factory - Web UI Setup")
    print("=" * 60)

    # Check Python version
    print("\n✓ Python version:", sys.version.split()[0])

    # Check if uv is available
    has_uv = check_command("uv")

    if has_uv:
        print("✓ uv package manager detected")
        print("\n📦 Installing dependencies with uv...")
        try:
            subprocess.run(["uv", "sync"], check=True)
            print("✓ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            sys.exit(1)
    else:
        print("⚠ uv not found, using pip instead")
        print("\n📦 Installing dependencies with pip...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "fastapi>=0.115.0",
                "uvicorn[standard]>=0.32.0"
            ], check=True)
            print("✓ FastAPI and Uvicorn installed!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            sys.exit(1)

    # Check if Ollama is running
    print("\n🔍 Checking Ollama...")
    if check_command("ollama"):
        print("✓ Ollama is installed")
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            if "qwen2.5:7b" in result.stdout.lower() or "qwen2.5" in result.stdout.lower():
                print("✓ Model qwen2.5:7b is available")
            else:
                print("⚠ Model qwen2.5:7b not found")
                print("  Run: ollama pull qwen2.5:7b")
        except subprocess.CalledProcessError:
            print("⚠ Could not check Ollama models")
    else:
        print("❌ Ollama not found. Please install from https://ollama.ai")

    # Check if brand voice data exists
    chroma_dir = Path("src/ai_content_factory/data/chroma")
    if chroma_dir.exists():
        print("✓ ChromaDB directory exists")
    else:
        print("⚠ ChromaDB directory not found")
        print("  You may need to run: python src/ai_content_factory/scripts/generate_brand_embeddings.py")

    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\nTo start the web UI, run:")
    print("  python run_web_ui.py")
    print("\nOr manually:")
    print("  uvicorn src.ai_content_factory.api.app:app --reload")
    print("\nThe UI will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    main()
