#!/usr/bin/env python3
"""
Test optimized prompts with seed 50
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables
os.environ["USE_INSPECT_AI"] = "true"
os.environ["PYTHONHASHSEED"] = "50"  # Changed to seed 50
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
os.environ["SERP_API_KEY"] = "8b66ef544709847671ce739cb89b51601505777ffdfcd82f0246419387922342"
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["DEFAULT_MODEL"] = "openai/gpt-4.1"

def run_benchmark_seed_50():
    """Run benchmark with seed 50"""
    print("🚀 Testing Optimized Prompts with Seed 50")
    print("=" * 50)
    
    cmd = [
        sys.executable, "run_forecastbench.py",
        "--max-questions", "5",
        "--max-workers", "5"
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes timeout
            cwd=Path(__file__).parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode != 0:
            print(f"❌ Benchmark failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        # Extract Brier score from output
        output = result.stdout
        brier_score = extract_brier_score(output)
        
        print(f"\n📊 Results for Seed 50:")
        print(f"   Execution Time: {duration:.1f} seconds")
        print(f"   Brier Score: {brier_score:.4f}")
        
        if brier_score < 0.05:
            print("🎉 SUCCESS! Achieved target Brier score < 0.05")
            success = True
        else:
            print(f"📈 Current score: {brier_score:.4f}, target: < 0.05")
            success = False
        
        # Save results
        results = {
            "seed": 50,
            "brier_score": brier_score,
            "duration_seconds": duration,
            "target_achieved": brier_score < 0.05,
            "timestamp": datetime.now().isoformat(),
            "success": success
        }
        
        results_file = Path(__file__).parent / f"seed_50_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to {results_file}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ Benchmark timed out after 30 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        return False

def extract_brier_score(output: str) -> float:
    """Extract Brier score from benchmark output"""
    import re
    
    # Look for patterns like "Average Brier Score: 0.123" or "Brier: 0.123"
    patterns = [
        r"overall_avg_brier_score[\"']:\s*([0-9.]+)",
        r"Average Brier Score:\s*([0-9.]+)",
        r"Brier Score:\s*([0-9.]+)",
        r"Brier:\s*([0-9.]+)",
        r"avg_brier_score[\"']:\s*([0-9.]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    # If no pattern found, return a high score to indicate failure
    print("⚠️ Could not extract Brier score from output")
    print("📄 Output preview:")
    print(output[-500:])  # Show last 500 chars
    return 1.0

if __name__ == "__main__":
    success = run_benchmark_seed_50()
    exit(0 if success else 1)