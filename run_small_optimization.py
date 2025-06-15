#!/usr/bin/env python3
"""
Run a small optimization test to verify the system works
"""

from clean_prompt_optimization import CleanPromptOptimizer

def main():
    print("🚀 Starting small optimization test...")
    
    optimizer = CleanPromptOptimizer()
    
    # Run optimization with just 2 seeds and 1 iteration to test
    print("Running parallel optimization with 2 seeds...")
    
    try:
        results = optimizer.run_parallel_optimization(seeds=[42, 123], iteration=1)
        
        print(f"✅ Optimization completed!")
        print(f"   Number of results: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"   Result {i+1}: Success={result.success}, Brier={result.brier_score:.4f}, Seed={result.seed}")
        
        # Calculate average Brier score
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_brier = sum(r.brier_score for r in successful_results) / len(successful_results)
            print(f"   Average Brier score: {avg_brier:.4f}")
            
            if avg_brier < 0.06:
                print("🎉 Target Brier score achieved!")
            else:
                print(f"📈 Need to improve: {avg_brier:.4f} > 0.06")
        
        return results
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()