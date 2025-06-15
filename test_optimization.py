#!/usr/bin/env python3
"""
Simple test of the optimization system
"""

import sys
import time
from clean_prompt_optimization import CleanPromptOptimizer

def test_single_benchmark():
    """Test running a single benchmark"""
    print("🧪 Testing single benchmark run...")
    
    optimizer = CleanPromptOptimizer()
    
    # Test running a single seed
    try:
        print("Running single seed with seed 42...")
        result = optimizer.run_single_seed(seed=42, iteration=1)
        print(f"✅ Single seed result: {result}")
        return result
    except Exception as e:
        print(f"❌ Single seed failed: {e}")
        return None

def test_prompt_generation():
    """Test prompt generation"""
    print("🧪 Testing prompt generation...")
    
    from clean_prompt_optimization import SuperforecastingPromptGenerator
    generator = SuperforecastingPromptGenerator()
    
    try:
        # Test generating prompts for different iterations
        high_prompt = generator.generate_high_advocate_prompt(iteration=1)
        low_prompt = generator.generate_low_advocate_prompt(iteration=1)
        judge_prompt = generator.generate_judge_prompt(iteration=1)
        
        print(f"✅ Generated prompts successfully")
        print(f"   High advocate prompt length: {len(high_prompt)}")
        print(f"   Low advocate prompt length: {len(low_prompt)}")
        print(f"   Judge prompt length: {len(judge_prompt)}")
        
        return {'high_advocate': high_prompt, 'low_advocate': low_prompt, 'judge': judge_prompt}
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting optimization system tests...")
    
    # Test 1: Single benchmark
    benchmark_result = test_single_benchmark()
    
    if benchmark_result:
        print(f"✅ Benchmark test passed")
        
        # Test 2: Prompt generation
        prompt_result = test_prompt_generation()
        
        if prompt_result:
            print("✅ All tests passed!")
        else:
            print("❌ Prompt generation test failed")
    else:
        print("❌ Benchmark test failed")