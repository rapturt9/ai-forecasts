"""Agent logging utility for tracking agent activities"""

import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class AgentLogger:
    """Simple logger to track agent activities during forecasting"""
    
    def __init__(self, log_file: str = None):
        self.logs: List[Dict[str, Any]] = []
        self.start_time = None
        self.log_file = log_file
        self.session_id = None
        
        # Ensure logs directory exists if log_file is provided
        if self.log_file:
            log_dir = Path(self.log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def start_session(self, session_type: str, request_data: Dict[str, Any], session_id: str = None):
        """Start a new logging session"""
        self.start_time = time.time()
        self.logs = []
        self.session_id = session_id or f"{session_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_log = {
            "session_type": session_type,
            "session_id": self.session_id,
            "request_data": request_data
        }
        
        self.log("session_start", f"Starting {session_type} analysis", start_log)
        
        # Write session start to file if configured
        if self.log_file:
            self._write_to_file()
    
    def log(self, agent: str, message: str, details: Dict[str, Any] = None):
        """Log an agent activity"""
        timestamp = datetime.now().isoformat()
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        log_entry = {
            "timestamp": timestamp,
            "elapsed_seconds": round(elapsed, 2),
            "agent": agent,
            "message": message,
            "session_id": self.session_id
        }
        
        if details:
            log_entry["details"] = details
        
        self.logs.append(log_entry)
        
        # Also print to console for immediate feedback
        print(f"[{elapsed:6.2f}s] {agent}: {message}")
        
        # Write to file if configured
        if self.log_file:
            self._write_to_file()
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all logs from current session"""
        return self.logs
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the logging session"""
        if not self.logs:
            return {"total_time": 0, "agent_count": 0, "activities": []}
        
        total_time = self.logs[-1]["elapsed_seconds"] if self.logs else 0
        agents = set(log["agent"] for log in self.logs)
        
        return {
            "total_time": total_time,
            "agent_count": len(agents),
            "activities": [f"{log['agent']}: {log['message']}" for log in self.logs],
            "agents_used": list(agents)
        }
    
    def info(self, message: str, details: Dict[str, Any] = None):
        """Log an info message"""
        self.log("system", message, details)
    
    def warning(self, message: str, details: Dict[str, Any] = None):
        """Log a warning message"""
        self.log("warning", message, details)
    
    def error(self, message: str, details: Dict[str, Any] = None):
        """Log an error message"""
        self.log("error", message, details)
    
    def _write_to_file(self):
        """Write current logs to file"""
        if not self.log_file:
            return
            
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    "session_id": self.session_id,
                    "start_time": self.start_time,
                    "logs": self.logs
                }, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to write to log file {self.log_file}: {e}")
    
    def finalize_session(self):
        """Finalize the current session and ensure logs are written"""
        if self.logs:
            total_time = self.logs[-1]["elapsed_seconds"] if self.logs else 0
            self.log("session_end", f"Session completed in {total_time:.2f}s")
            
        if self.log_file:
            self._write_to_file()
            print(f"📁 Logs saved to: {self.log_file}")


# Global logger instance (without file logging by default)
agent_logger = AgentLogger()