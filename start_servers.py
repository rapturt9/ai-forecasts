#!/usr/bin/env python3
"""
Startup script for AI Forecasting & Trading System
Starts both the Python FastAPI server and Next.js frontend
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def start_python_api():
    """Start the Python FastAPI server"""
    print("🚀 Starting Python FastAPI server...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PORT'] = '8000'
    
    # Start the FastAPI server
    process = subprocess.Popen([
        sys.executable, 'api_server.py'
    ], env=env, cwd=Path(__file__).parent)
    
    return process

def start_nextjs_frontend():
    """Start the Next.js frontend"""
    print("🌐 Starting Next.js frontend...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PORT'] = '12000'
    env['PYTHON_API_URL'] = 'http://localhost:8000'
    
    # Start the Next.js server
    process = subprocess.Popen([
        'npm', 'run', 'dev'
    ], env=env, cwd=Path(__file__).parent / 'trading-interface')
    
    return process

def main():
    """Main startup function"""
    print("🤖 AI Forecasting & Trading System Startup")
    print("=" * 50)
    
    # Check if API keys are set
    required_keys = ['OPENROUTER_API_KEY', 'SERP_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"⚠️  Warning: Missing API keys: {', '.join(missing_keys)}")
        print("   The system will use demo/mock data for missing services")
        print()
    
    processes = []
    
    try:
        # Start Python API server
        python_process = start_python_api()
        processes.append(python_process)
        
        # Wait a moment for the API server to start
        time.sleep(3)
        
        # Start Next.js frontend
        nextjs_process = start_nextjs_frontend()
        processes.append(nextjs_process)
        
        print()
        print("✅ Both servers started successfully!")
        print()
        print("📊 Python API Server: http://localhost:8000")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/")
        print()
        print("🌐 Next.js Frontend: http://localhost:12000")
        print("   - Main Interface: http://localhost:12000/")
        print()
        print("🔗 Production URLs:")
        print("   - Frontend: https://work-1-xfrnjmbnxyapapro.prod-runtime.all-hands.dev")
        print("   - API: https://work-2-xfrnjmbnxyapapro.prod-runtime.all-hands.dev")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ Process {i} has died with return code {process.returncode}")
                    return
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate all processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()