"""Agent logging utility for tracking agent activities"""

import time
from typing import List, Dict, Any
from datetime import datetime


class AgentLogger:
    """Simple logger to track agent activities during forecasting"""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.start_time = None
    
    def start_session(self, session_type: str, request_data: Dict[str, Any]):
        """Start a new logging session"""
        self.start_time = time.time()
        self.logs = []
        self.log("session_start", f"Starting {session_type} analysis", {
            "session_type": session_type,
            "request_data": request_data
        })
    
    def log(self, agent: str, message: str, details: Dict[str, Any] = None):
        """Log an agent activity"""
        timestamp = datetime.now().isoformat()
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        log_entry = {
            "timestamp": timestamp,
            "elapsed_seconds": round(elapsed, 2),
            "agent": agent,
            "message": message
        }
        
        if details:
            log_entry["details"] = details
        
        self.logs.append(log_entry)
    
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


# Global logger instance
agent_logger = AgentLogger()