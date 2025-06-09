#!/usr/bin/env python3
"""Script to run the FastAPI server"""

import uvicorn
import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    uvicorn.run(
        "ai_forecasts.api.main:app",
        host="0.0.0.0",
        port=12000,
        reload=True,
        log_level="info"
    )