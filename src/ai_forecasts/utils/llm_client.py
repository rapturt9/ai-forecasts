"""LLM client configuration for OpenRouter"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper for OpenRouter LLM client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20"),
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.client = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            default_headers={
                "HTTP-Referer": "https://ai-forecasts.com",
                "X-Title": "AI Forecasting System"
            }
        )
    
    def get_client(self) -> ChatOpenAI:
        """Get the configured LLM client"""
        return self.client