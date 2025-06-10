#!/usr/bin/env python3
"""Script to run the complete AI Forecasting system (API + Frontend)"""

import streamlit.web.cli as stcli
import os
import sys
import subprocess
import time
import threading
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_api_health():
    """Check if API server is running"""
    try:
        response = requests.get("http://localhost:12000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server in background"""
    print("🚀 Starting API server...")
    
    # Check if API is already running
    if check_api_health():
        print("✅ API server already running on port 12000")
        return None
    
    # Start API server
    api_process = subprocess.Popen([
        sys.executable, "run_api.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for API to be ready
    for i in range(30):  # Wait up to 30 seconds
        if check_api_health():
            print("✅ API server started successfully on port 12000")
            return api_process
        time.sleep(1)
        print(f"⏳ Waiting for API server... ({i+1}/30)")
    
    print("❌ Failed to start API server")
    return None

def main():
    """Main function to start both API and frontend"""
    print("🔮 AI Forecasting & Strategy System")
    print("=" * 50)
    
    # Check if API key is configured
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found!")
        print("📝 Please create a .env file with your API key:")
        print("   OPENROUTER_API_KEY=sk-or-v1-your-api-key-here")
        print("💡 Or set it as an environment variable:")
        print("   export OPENROUTER_API_KEY=sk-or-v1-your-api-key-here")
        sys.exit(1)
    else:
        print(f"✅ API key configured: {api_key[:20]}...")
        
    # Show configuration
    model = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    print(f"🤖 Using model: {model}")
    print(f"🌐 API endpoint: {base_url}")
    
    # Start API server
    api_process = start_api_server()
    
    try:
        print("🌐 Starting Streamlit frontend...")
        print("📱 Frontend will be available at: http://localhost:12001")
        print("📚 API docs available at: http://localhost:12000/docs")
        print("=" * 50)
        
        # Start Streamlit frontend
        sys.argv = [
            "streamlit",
            "run",
            "src/ai_forecasts/frontend/streamlit_app.py",
            "--server.port=12001",
            "--server.address=0.0.0.0",
            "--server.allowRunOnSave=true",
            "--server.enableCORS=true",
            "--server.enableXsrfProtection=false",
            "--browser.gatherUsageStats=false"
        ]
        sys.exit(stcli.main())
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if api_process:
            api_process.terminate()
            api_process.wait()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()