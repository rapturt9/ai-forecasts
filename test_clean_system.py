#!/usr/bin/env python3
"""
Test the clean optimization system with minimal settings
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables
os.environ["USE_INSPECT_AI"] = "true"
os.environ["PYTHONHASHSEED"] = "42"
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")

from clean_prompt_optimization import CleanPromptOptimizer

def main():
    """Test the clean system with 1 iteration, 1 seed, 2 questions"""
    print("🧪 Testing Clean Optimization System")
    print("=" * 50)
    print("Testing: 1 iteration, 1 seed, 2 questions")
    print("Purpose: Verify clean system works without CrewAI")
    print("=" * 50)
    
    # Create optimizer with minimal settings
    optimizer = CleanPromptOptimizer(max_questions=2, max_workers=1)
    
    try:
        # Test single iteration with one seed
        seeds = [42]
        iteration = 1
        
        print(f"🚀 Running test iteration {iteration} with seed {seeds[0]}...")
        
        # Run the optimization
        results = optimizer.run_parallel_optimization(seeds, iteration)
        
        # Check results
        if results and len(results) > 0:
            result = results[0]
            print(f"\n📊 Test Results:")
            print(f"   Success: {result.success}")
            print(f"   Brier Score: {result.brier_score:.4f}")
            print(f"   Search Penalty: {result.search_penalty:.3f}")
            print(f"   Total Searches: {result.total_searches}")
            
            if result.success:
                print("🎉 Clean system test PASSED!")
                print("   System is ready for full optimization")
                return 0
            else:
                print("❌ Clean system test FAILED!")
                print(f"   Error: {result.error}")
                return 1
        else:
            print("❌ No results returned from optimization")
            return 1
            
    except Exception as e:
        print(f"❌ Clean system test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Always cleanup
        optimizer.cleanup()

if __name__ == "__main__":
    exit(main())