#!/usr/bin/env python3
"""
Simple API test to verify OpenRouter works
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_openrouter_api():
    """Test OpenRouter API directly"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://ai-forecasts.com",
        "X-Title": "AI Forecasting System",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": os.getenv("DEFAULT_MODEL", "openai/gpt-4o-2024-11-20"),
        "messages": [
            {
                "role": "user", 
                "content": "What is the probability that global temperatures in 2024 will exceed 2023? Give a number between 0 and 1."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        print("🌐 Making API request...")
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Response: {content}")
            
            # Try to extract a probability
            import re
            prob_match = re.search(r'0\.\d+', content)
            if prob_match:
                probability = float(prob_match.group())
                actual_outcome = 0.7565624485542961
                brier_score = (probability - actual_outcome) ** 2
                
                print()
                print("📊 BENCHMARK RESULT")
                print("=" * 25)
                print(f"🎯 AI Prediction: {probability:.4f}")
                print(f"✅ Actual Outcome: {actual_outcome:.4f}")
                print(f"📈 Brier Score: {brier_score:.6f}")
                
                return brier_score
            else:
                print("⚠️ Could not extract probability from response")
                return None
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    brier_score = test_openrouter_api()
    if brier_score is not None:
        print(f"\n🏆 FINAL BRIER SCORE: {brier_score:.6f}")
    else:
        print("\n❌ Test failed")