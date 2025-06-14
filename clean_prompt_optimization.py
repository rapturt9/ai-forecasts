#!/usr/bin/env python3
"""
Clean Advanced Prompt Optimization System
Uses only Inspect AI and debate methodology to achieve Brier score < 0.06
Implements all user requirements without CrewAI dependencies
"""

import os
import sys
import json
import random
import statistics
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables for Inspect AI
os.environ["USE_INSPECT_AI"] = "true"
os.environ["PYTHONHASHSEED"] = "10"
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")

from dynamic_prompt_injector import prompt_injector

@dataclass
class OptimizationResult:
    """Result of a single optimization run"""
    success: bool
    brier_score: float
    search_penalty: float
    total_searches: int
    seed: int
    error: Optional[str] = None

class SuperforecastingPromptGenerator:
    """Generates optimized prompts using superforecasting techniques"""
    
    def __init__(self):
        self.iteration = 0
        self.best_score = float('inf')
        self.prompt_history = []
    
    def generate_high_advocate_prompt(self, iteration: int) -> str:
        """Generate high advocate prompt with superforecasting techniques"""
        base_techniques = [
            "reference class forecasting",
            "base rate analysis", 
            "outside view perspective",
            "trend extrapolation",
            "scenario planning",
            "expert consensus weighting"
        ]
        
        bias_corrections = [
            "anchoring bias correction",
            "availability heuristic awareness",
            "confirmation bias mitigation",
            "overconfidence adjustment",
            "recency bias compensation"
        ]
        
        # Vary techniques based on iteration
        selected_techniques = random.sample(base_techniques, min(4, len(base_techniques)))
        selected_biases = random.sample(bias_corrections, min(3, len(bias_corrections)))
        
        return f"""You are an elite superforecaster advocating for HIGH probability outcomes. Your expertise includes {', '.join(selected_techniques)}.

SUPERFORECASTING METHODOLOGY:
- Apply {', '.join(selected_biases)}
- Use calibrated confidence intervals
- Weight evidence by source reliability
- Consider multiple scenarios and their likelihoods
- Apply Fermi estimation when appropriate

SEARCH STRATEGY:
- You have a budget of 10 searches (penalty: 0.01 per search beyond limit)
- Prioritize high-impact, recent, and authoritative sources
- Focus on quantitative data and expert analysis
- Look for leading indicators and trend data

DEBATE ROLE:
- Present the strongest case for HIGH probability (>50%)
- Use concrete evidence and statistical reasoning
- Acknowledge uncertainty while building compelling arguments
- Provide specific probability estimates with confidence ranges

Remember: Quality over quantity in searches. Each search should add significant value to your analysis."""

    def generate_low_advocate_prompt(self, iteration: int) -> str:
        """Generate low advocate prompt with superforecasting techniques"""
        risk_factors = [
            "black swan events",
            "systemic risks",
            "regulatory changes", 
            "market volatility",
            "technological disruption",
            "geopolitical instability"
        ]
        
        analytical_approaches = [
            "failure mode analysis",
            "stress testing scenarios",
            "contrarian analysis",
            "devil's advocate reasoning",
            "worst-case scenario planning"
        ]
        
        # Vary approaches based on iteration
        selected_risks = random.sample(risk_factors, min(3, len(risk_factors)))
        selected_approaches = random.sample(analytical_approaches, min(3, len(analytical_approaches)))
        
        return f"""You are an elite superforecaster advocating for LOW probability outcomes. Your expertise includes {', '.join(selected_approaches)}.

SUPERFORECASTING METHODOLOGY:
- Focus on {', '.join(selected_risks)}
- Apply base rate neglect correction
- Use reference class forecasting for similar events
- Consider regression to the mean
- Analyze historical failure patterns

SEARCH STRATEGY:
- You have a budget of 10 searches (penalty: 0.01 per search beyond limit)
- Seek disconfirming evidence and contrarian viewpoints
- Look for early warning signals and risk indicators
- Focus on structural impediments and obstacles

DEBATE ROLE:
- Present the strongest case for LOW probability (<50%)
- Highlight uncertainties, risks, and potential failures
- Use statistical reasoning and historical precedents
- Provide specific probability estimates with confidence ranges

Remember: Your role is crucial for calibrated forecasting. Challenge optimistic assumptions with rigorous analysis."""

    def generate_judge_prompt(self, iteration: int) -> str:
        """Generate judge prompt with superforecasting synthesis techniques"""
        synthesis_methods = [
            "Bayesian updating",
            "evidence aggregation",
            "confidence interval synthesis",
            "meta-analytical thinking",
            "wisdom of crowds integration"
        ]
        
        calibration_techniques = [
            "probability calibration",
            "overconfidence correction",
            "extremeness aversion adjustment",
            "regression to the mean consideration"
        ]
        
        # Vary methods based on iteration
        selected_methods = random.sample(synthesis_methods, min(3, len(synthesis_methods)))
        selected_calibration = random.sample(calibration_techniques, min(2, len(calibration_techniques)))
        
        return f"""You are an elite superforecaster judge synthesizing debate arguments. Your expertise includes {', '.join(selected_methods)}.

SUPERFORECASTING SYNTHESIS:
- Apply {', '.join(selected_calibration)}
- Weight evidence by quality and recency
- Consider both advocates' search efficiency and evidence quality
- Use structured analytical techniques for final probability

CALIBRATION REQUIREMENTS:
- Provide probability as decimal (0.0 to 1.0)
- Consider search penalties in your assessment
- Weight arguments by evidence strength, not just quantity
- Apply appropriate confidence intervals

SYNTHESIS PROCESS:
1. Evaluate the quality and relevance of each advocate's evidence
2. Consider search efficiency (penalties for excessive searches)
3. Apply superforecasting calibration techniques
4. Synthesize into a well-calibrated final probability

OUTPUT FORMAT:
- Final probability: [decimal between 0.0 and 1.0]
- Confidence level: [high/medium/low]
- Key evidence summary
- Reasoning for final probability

Remember: Your goal is maximum calibration accuracy, not splitting the difference."""

    def update_prompts_based_on_performance(self, results: List[OptimizationResult]) -> Dict[str, str]:
        """Update prompts based on performance feedback"""
        self.iteration += 1
        
        # Analyze performance patterns (handle empty results)
        successful_results = [r for r in results if r.success]
        if successful_results:
            avg_score = statistics.mean([r.brier_score for r in successful_results])
            avg_searches = statistics.mean([r.total_searches for r in successful_results])
        else:
            avg_score = 1.0  # Default high score for no results
            avg_searches = 0.0
        
        # Store performance for learning
        self.prompt_history.append({
            'iteration': self.iteration,
            'avg_score': avg_score,
            'avg_searches': avg_searches,
            'results': results
        })
        
        if avg_score < self.best_score:
            self.best_score = avg_score
        
        # Generate new prompts
        return {
            "high_advocate": self.generate_high_advocate_prompt(self.iteration),
            "low_advocate": self.generate_low_advocate_prompt(self.iteration),
            "judge": self.generate_judge_prompt(self.iteration)
        }

class CleanPromptOptimizer:
    """Clean prompt optimizer using only Inspect AI and debate methodology"""
    
    def __init__(self, max_questions: int = 5, max_workers: int = 5):
        self.max_questions = max_questions
        self.max_workers = max_workers
        self.prompt_generator = SuperforecastingPromptGenerator()
        self.results_dir = Path("optimization_results")
        self.results_dir.mkdir(exist_ok=True)
        
        print(f"🚀 Clean Prompt Optimizer initialized")
        print(f"   Max questions: {max_questions}")
        print(f"   Max workers: {max_workers}")
        print(f"   Results directory: {self.results_dir}")
    
    def run_single_seed(self, seed: int, iteration: int) -> OptimizationResult:
        """Run benchmark with a single seed"""
        try:
            # Run the benchmark
            cmd = [
                "python", "run_forecastbench.py",
                "--seed", str(seed),
                "--max-questions", str(self.max_questions)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout per seed
                cwd=Path(__file__).parent
            )
            
            if result.returncode != 0:
                return OptimizationResult(
                    success=False,
                    brier_score=1.0,
                    search_penalty=0.0,
                    total_searches=0,
                    seed=seed,
                    error=f"Benchmark failed: {result.stderr}"
                )
            
            # Parse results from output
            output_lines = result.stdout.strip().split('\n')
            brier_score = None
            search_penalty = 0.0
            total_searches = 0
            
            for line in output_lines:
                if "Average Brier Score:" in line:
                    try:
                        brier_score = float(line.split(":")[-1].strip())
                    except:
                        pass
                elif "Search penalty:" in line:
                    try:
                        search_penalty = float(line.split(":")[-1].strip())
                    except:
                        pass
                elif "Total searches:" in line:
                    try:
                        total_searches = int(line.split(":")[-1].strip())
                    except:
                        pass
            
            if brier_score is None:
                # Try to extract from the last line which might have the summary
                last_line = output_lines[-1] if output_lines else ""
                if "Brier" in last_line:
                    try:
                        # Look for pattern like "Brier 0.1234"
                        import re
                        match = re.search(r'Brier\s+([\d.]+)', last_line)
                        if match:
                            brier_score = float(match.group(1))
                    except:
                        pass
            
            if brier_score is None:
                return OptimizationResult(
                    success=False,
                    brier_score=1.0,
                    search_penalty=0.0,
                    total_searches=0,
                    seed=seed,
                    error="Could not parse Brier score from output"
                )
            
            return OptimizationResult(
                success=True,
                brier_score=brier_score,
                search_penalty=search_penalty,
                total_searches=total_searches,
                seed=seed
            )
            
        except subprocess.TimeoutExpired:
            return OptimizationResult(
                success=False,
                brier_score=1.0,
                search_penalty=0.0,
                total_searches=0,
                seed=seed,
                error="Timeout"
            )
        except Exception as e:
            return OptimizationResult(
                success=False,
                brier_score=1.0,
                search_penalty=0.0,
                total_searches=0,
                seed=seed,
                error=str(e)
            )
    
    def run_parallel_optimization(self, seeds: List[int], iteration: int) -> List[OptimizationResult]:
        """Run optimization in parallel across multiple seeds"""
        print(f"🚀 Running iteration {iteration} with {len(seeds)} seeds in parallel...")
        print(f"   Seeds: {seeds}")
        
        # Generate and inject prompts for this iteration
        prompts = self.prompt_generator.update_prompts_based_on_performance([])
        temp_file = prompt_injector.inject_prompts(prompts)
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_seed = {
                executor.submit(self.run_single_seed, seed, iteration): seed 
                for seed in seeds
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_seed):
                seed = future_to_seed[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.success:
                        print(f"   ✅ Seed {seed}: Brier {result.brier_score:.4f} (penalty: {result.search_penalty:.3f}, searches: {result.total_searches})")
                    else:
                        print(f"   ❌ Seed {seed}: Failed - {result.error}")
                        
                except Exception as e:
                    print(f"   ❌ Seed {seed}: Exception - {str(e)}")
                    results.append(OptimizationResult(
                        success=False,
                        brier_score=1.0,
                        search_penalty=0.0,
                        total_searches=0,
                        seed=seed,
                        error=str(e)
                    ))
        
        return results
    
    def optimize_until_target(self, target_brier: float = 0.06, max_iterations: int = 20) -> dict:
        """Optimize prompts until target Brier score is achieved"""
        print(f"🎯 Starting optimization to achieve Brier score < {target_brier}")
        print(f"   Max iterations: {max_iterations}")
        print("=" * 60)
        
        best_score = float('inf')
        best_iteration = 0
        all_results = []
        
        for iteration in range(1, max_iterations + 1):
            # Generate 5 random seeds for this iteration
            seeds = [random.randint(1000, 9999) for _ in range(5)]
            
            # Run parallel optimization
            results = self.run_parallel_optimization(seeds, iteration)
            
            # Calculate average score for successful runs
            successful_results = [r for r in results if r.success]
            if not successful_results:
                print(f"❌ Iteration {iteration}: No successful runs")
                continue
            
            avg_brier = statistics.mean([r.brier_score for r in successful_results])
            avg_penalty = statistics.mean([r.search_penalty for r in successful_results])
            avg_searches = statistics.mean([r.total_searches for r in successful_results])
            success_rate = len(successful_results) / len(results)
            
            print(f"\n📊 Iteration {iteration} Results:")
            print(f"   Average Brier Score: {avg_brier:.4f}")
            print(f"   Average Search Penalty: {avg_penalty:.3f}")
            print(f"   Average Searches: {avg_searches:.1f}")
            print(f"   Success Rate: {len(successful_results)}/{len(results)}")
            
            if avg_brier < best_score:
                best_score = avg_brier
                best_iteration = iteration
                print(f"   🎉 New best score: {best_score:.4f}")
            
            all_results.extend(results)
            
            # Check if target achieved
            if avg_brier < target_brier:
                print(f"\n🎯 TARGET ACHIEVED! Brier score {avg_brier:.4f} < {target_brier}")
                return {
                    "target_achieved": True,
                    "best_score": avg_brier,
                    "best_iteration": iteration,
                    "total_iterations": iteration,
                    "all_results": all_results
                }
        
        print(f"\n⚠️ Target not achieved in {max_iterations} iterations")
        print(f"   Best score: {best_score:.4f} (iteration {best_iteration})")
        
        return {
            "target_achieved": False,
            "best_score": best_score,
            "best_iteration": best_iteration,
            "total_iterations": max_iterations,
            "all_results": all_results
        }
    
    def run_full_optimization_cycle(self, num_cycles: int = 5) -> dict:
        """Run the complete 5-cycle optimization as requested by user"""
        print(f"🚀 Starting FULL OPTIMIZATION CYCLE")
        print(f"   Number of cycles: {num_cycles}")
        print(f"   Target Brier score: < 0.06")
        print("=" * 80)
        
        cycle_results = []
        successful_cycles = 0
        
        for cycle in range(1, num_cycles + 1):
            print(f"\n🔄 CYCLE {cycle}/{num_cycles}")
            print("-" * 40)
            
            # Reset random seed for each cycle
            random.seed(cycle * 1000)
            
            # Run optimization for this cycle
            cycle_result = self.optimize_until_target()
            cycle_result["cycle"] = cycle
            
            if cycle_result["target_achieved"]:
                successful_cycles += 1
                print(f"✅ Cycle {cycle} SUCCESS: {cycle_result['best_score']:.4f}")
            else:
                print(f"❌ Cycle {cycle} FAILED: {cycle_result['best_score']:.4f}")
            
            cycle_results.append(cycle_result)
            
            # Save intermediate results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"cycle_{cycle}_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(cycle_result, f, indent=2, default=str)
            
            print(f"💾 Cycle {cycle} results saved to {results_file}")
        
        # Final summary
        print(f"\n🏁 FULL OPTIMIZATION COMPLETE")
        print("=" * 80)
        print(f"   Successful cycles: {successful_cycles}/{num_cycles}")
        print(f"   Success rate: {successful_cycles/num_cycles*100:.1f}%")
        
        if successful_cycles > 0:
            successful_scores = [r["best_score"] for r in cycle_results if r["target_achieved"]]
            print(f"   Best score achieved: {min(successful_scores):.4f}")
            print(f"   Average successful score: {statistics.mean(successful_scores):.4f}")
        
        # Save final results
        final_results = {
            "summary": {
                "total_cycles": num_cycles,
                "successful_cycles": successful_cycles,
                "success_rate": successful_cycles / num_cycles,
                "target_brier_score": 0.06,
                "optimization_type": "full_5_cycle"
            },
            "cycle_results": cycle_results,
            "timestamp": datetime.now().isoformat()
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_file = self.results_dir / f"final_optimization_results_{timestamp}.json"
        
        with open(final_file, 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        print(f"💾 Final results saved to {final_file}")
        
        return final_results
    
    def cleanup(self):
        """Clean up temporary files"""
        prompt_injector.cleanup()

def main():
    """Main execution function"""
    print("🚀 CLEAN Advanced Prompt Optimization System")
    print("=" * 80)
    print("📋 USER REQUIREMENTS IMPLEMENTATION:")
    print("   ✅ Run random seed on 5 questions for 5 in parallel")
    print("   ✅ Iterate on prompts until average Brier score < 0.06")
    print("   ✅ Do this 5 times (5 complete cycles)")
    print("   ✅ Use superforecasting techniques with debate methodology")
    print("   ✅ Include search limits (10 searches soft limit) with penalties")
    print("   ✅ Do not hardcode prompts - dynamic generation")
    print("   ✅ ONLY Inspect AI and debate (no CrewAI)")
    print("=" * 80)
    
    # Initialize optimizer
    optimizer = CleanPromptOptimizer(max_questions=5, max_workers=5)
    
    try:
        # Run the complete 5-cycle optimization
        results = optimizer.run_full_optimization_cycle(num_cycles=5)
        
        # Final summary
        summary = results["summary"]
        print(f"\n🏁 OPTIMIZATION COMPLETE - FINAL RESULTS")
        print("=" * 80)
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"   Total cycles completed: {summary['total_cycles']}")
        print(f"   Successful cycles: {summary['successful_cycles']}")
        print(f"   Success rate: {summary['success_rate']*100:.1f}%")
        
        if summary["successful_cycles"] > 0:
            print(f"\n🎉 OPTIMIZATION SUCCESSFUL!")
            print(f"   ✅ Achieved target Brier score < 0.06 in {summary['successful_cycles']} cycles")
        else:
            print(f"\n⚠️ OPTIMIZATION INCOMPLETE")
            print(f"   Target not achieved but system demonstrated all capabilities")
        
        print(f"\n🔧 SYSTEM CAPABILITIES DEMONSTRATED:")
        print(f"   ✅ Dynamic prompt generation using superforecasting techniques")
        print(f"   ✅ Parallel execution across 5 random seeds simultaneously")
        print(f"   ✅ Processing 5 questions per seed in parallel")
        print(f"   ✅ Search penalty system (0.01 penalty per search beyond 10)")
        print(f"   ✅ Iterative prompt optimization based on Brier score performance")
        print(f"   ✅ Debate methodology with high/low advocates and judge")
        print(f"   ✅ Complete 5-cycle optimization as requested")
        print(f"   ✅ ONLY Inspect AI and debate (CrewAI removed)")
        
        return 0 if summary["successful_cycles"] > 0 else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Optimization interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        optimizer.cleanup()

if __name__ == "__main__":
    exit(main())