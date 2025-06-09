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
    
    # Check environment
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY='your-api-key-here'")
        sys.exit(1)
    
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