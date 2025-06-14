#!/usr/bin/env python3
"""
Dynamic Prompt Injection System
Allows runtime modification of debate forecasting prompts without hardcoding
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
import importlib.util

class DynamicPromptInjector:
    """Injects dynamic prompts into the debate forecasting system"""
    
    def __init__(self):
        self.original_prompts_file = Path(__file__).parent / "src" / "ai_forecasts" / "agents" / "debate_forecasting_prompts.py"
        self.temp_prompts_file = None
        self.injected_prompts = {}
    
    def inject_prompts(self, prompts: Dict[str, str]) -> str:
        """Inject new prompts and return path to temporary module"""
        
        # Store the prompts
        self.injected_prompts = prompts
        
        # Read the original file
        with open(self.original_prompts_file, 'r') as f:
            original_content = f.read()
        
        # Create modified content with injected prompts
        modified_content = self._create_modified_content(original_content, prompts)
        
        # Create temporary file
        temp_dir = Path(tempfile.gettempdir()) / "ai_forecasts_prompts"
        temp_dir.mkdir(exist_ok=True)
        
        self.temp_prompts_file = temp_dir / "debate_forecasting_prompts_dynamic.py"
        
        with open(self.temp_prompts_file, 'w') as f:
            f.write(modified_content)
        
        # Set environment variable to use dynamic prompts
        os.environ["DYNAMIC_PROMPTS_FILE"] = str(self.temp_prompts_file)
        
        return str(self.temp_prompts_file)
    
    def _create_modified_content(self, original_content: str, prompts: Dict[str, str]) -> str:
        """Create modified content with injected prompts"""
        
        # Add dynamic prompt functions at the end
        dynamic_functions = f'''

# DYNAMICALLY INJECTED PROMPTS - Generated at runtime
_DYNAMIC_PROMPTS = {json.dumps(prompts, indent=4)}

def get_dynamic_high_advocate_backstory() -> str:
    """Dynamically injected high advocate backstory"""
    return _DYNAMIC_PROMPTS.get("high_advocate", get_high_advocate_backstory())

def get_dynamic_low_advocate_backstory() -> str:
    """Dynamically injected low advocate backstory"""
    return _DYNAMIC_PROMPTS.get("low_advocate", get_low_advocate_backstory())

def get_dynamic_debate_judge_backstory() -> str:
    """Dynamically injected judge backstory"""
    return _DYNAMIC_PROMPTS.get("judge", get_debate_judge_backstory())

# Override the original functions
get_high_advocate_backstory = get_dynamic_high_advocate_backstory
get_low_advocate_backstory = get_dynamic_low_advocate_backstory
get_debate_judge_backstory = get_dynamic_debate_judge_backstory
'''
        
        return original_content + dynamic_functions
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_prompts_file and self.temp_prompts_file.exists():
            self.temp_prompts_file.unlink()
        
        if "DYNAMIC_PROMPTS_FILE" in os.environ:
            del os.environ["DYNAMIC_PROMPTS_FILE"]
    
    def get_search_penalty_from_logs(self, log_file: str) -> tuple[float, int]:
        """Extract search penalty and count from log files"""
        try:
            if not Path(log_file).exists():
                return 0.0, 0
            
            with open(log_file, 'r') as f:
                log_data = json.load(f)
            
            # Look for search count in various places
            total_searches = 0
            
            # Check in session data
            if 'session_data' in log_data:
                session_data = log_data['session_data']
                if 'search_count' in session_data:
                    total_searches = session_data['search_count']
                elif 'api_calls' in session_data:
                    total_searches = session_data['api_calls']
            
            # Check in events for search tracking
            if 'events' in log_data:
                for event in log_data['events']:
                    if 'data' in event and isinstance(event['data'], dict):
                        if 'search_count' in event['data']:
                            total_searches = max(total_searches, event['data']['search_count'])
                        elif 'api_calls' in event['data']:
                            total_searches = max(total_searches, event['data']['api_calls'])
            
            # Calculate penalty: 0.01 for each search beyond 10
            search_penalty = max(0, (total_searches - 10) * 0.01)
            
            return search_penalty, total_searches
            
        except Exception as e:
            print(f"⚠️ Error extracting search metrics from {log_file}: {e}")
            return 0.0, 0

# Global instance for easy access
prompt_injector = DynamicPromptInjector()