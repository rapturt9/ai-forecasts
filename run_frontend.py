#!/usr/bin/env python3
"""Script to run the Streamlit frontend"""

import streamlit.web.cli as stcli
import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "src/ai_forecasts/frontend/streamlit_app.py",
        "--server.port=12001",
        "--server.address=0.0.0.0",
        "--server.allowRunOnSave=true",
        "--server.enableCORS=true",
        "--server.enableXsrfProtection=false"
    ]
    sys.exit(stcli.main())