#!/usr/bin/env python3
"""
Frontend Runner - Starts the Next.js trading interface with AI forecasting backend
"""

import os
import sys
import subprocess
import time
import threading
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_frontend_health():
    """Check if frontend server is running"""
    try:
        response = requests.get("http://localhost:12000", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_frontend_server():
    """Start the Next.js frontend server"""
    print("🚀 Starting Next.js Trading Interface...")
    
    frontend_dir = Path(__file__).parent / "trading-interface"
    
    if not frontend_dir.exists():
        print("❌ Trading interface directory not found")
        return False
    
    try:
        # Change to frontend directory and start dev server
        os.chdir(frontend_dir)
        
        # Install dependencies if needed
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start development server
        print("🌐 Starting development server on port 12000...")
        subprocess.run([
            "npm", "run", "dev", 
            "--", "--port", "12000", 
            "--hostname", "0.0.0.0"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
        return True

def main():
    """Main function to start the trading interface"""
    print("🤖 AI Forecasting Trading System")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set them in your .env file")
    
    # Start frontend
    if not check_frontend_health():
        start_frontend_server()
    else:
        print("✅ Frontend already running at http://localhost:12000")

if __name__ == "__main__":
    main()