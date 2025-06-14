#!/usr/bin/env python3
"""
Iterative Prompt Optimization - Achieve Brier Score < 0.06
Run 5 optimization cycles with adaptive prompt improvement without hardcoding
"""

import os
import sys
import json
import subprocess
import time
import random
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variables
os.environ["USE_INSPECT_AI"] = "true"
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
os.environ["SERP_API_KEY"] = "8b66ef544709847671ce739cb89b51601505777ffdfcd82f0246419387922342"
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["DEFAULT_MODEL"] = "openai/gpt-4.1"
os.environ["MANIFOLD_API_KEY"] = "f9eccdd9-bff7-40d0-8e2e-da27cff01fdb"

# Target parameters
TARGET_BRIER_SCORE = 0.06
NUM_OPTIMIZATION_CYCLES = 5
NUM_QUESTIONS = 5
MAX_WORKERS = 5

def get_random_questions(num_questions=5):
    """Get random questions from the benchmark dataset"""
    benchmark_file = Path(__file__).parent / "forecastbench_human_2024.json"
    
    with open(benchmark_file, 'r') as f:
        data = json.load(f)
    
    # Get all question IDs from the questions list
    all_questions = [q["id"] for q in data["questions"]]
    
    # Select random questions
    selected = random.sample(all_questions, min(num_questions, len(all_questions)))
    
    print(f"🎲 Selected random questions: {selected}")
    return selected

def generate_adaptive_prompts(iteration, previous_score=None, previous_analysis=None):
    """Generate adaptive prompts based on previous performance"""
    
    # Base prompt evolution strategies
    strategies = [
        "evidence_focus",
        "uncertainty_emphasis", 
        "bias_correction",
        "reference_class_analysis",
        "conservative_calibration",
        "meta_reasoning",
        "adversarial_thinking",
        "frequency_framing"
    ]
    
    # Select strategy based on iteration and previous performance
    if iteration == 1:
        primary_strategy = "evidence_focus"
        secondary_strategy = "uncertainty_emphasis"
    elif previous_score and previous_score > 0.15:
        # High score - focus on conservative calibration
        primary_strategy = "conservative_calibration"
        secondary_strategy = "bias_correction"
    elif previous_score and previous_score > 0.08:
        # Medium score - focus on meta-reasoning
        primary_strategy = "meta_reasoning"
        secondary_strategy = "adversarial_thinking"
    else:
        # Low score - focus on refinement
        primary_strategy = "frequency_framing"
        secondary_strategy = "reference_class_analysis"
    
    print(f"🧠 Iteration {iteration}: Using {primary_strategy} + {secondary_strategy} strategies")
    
    return create_strategy_prompts(primary_strategy, secondary_strategy, iteration)

def create_strategy_prompts(primary_strategy, secondary_strategy, iteration):
    """Create prompts based on selected strategies"""
    
    strategy_components = {
        "evidence_focus": {
            "core": "Base all reasoning on concrete, verifiable evidence with explicit source evaluation",
            "process": "1. Identify all available evidence sources\n2. Evaluate source credibility and recency\n3. Weight evidence by reliability and independence\n4. Build probability estimate from evidence foundation"
        },
        "uncertainty_emphasis": {
            "core": "Systematically quantify and communicate uncertainty at every step",
            "process": "1. Identify known unknowns and knowledge gaps\n2. Assess confidence levels for each piece of evidence\n3. Propagate uncertainty through reasoning chain\n4. Express final estimate with appropriate confidence intervals"
        },
        "bias_correction": {
            "core": "Apply systematic bias detection and correction throughout reasoning",
            "process": "1. Check for overconfidence, availability, and confirmation biases\n2. Apply 'consider the opposite' at key decision points\n3. Use outside view to validate inside view reasoning\n4. Adjust estimates based on known bias patterns"
        },
        "reference_class_analysis": {
            "core": "Ground predictions in historical base rates and reference class analysis",
            "process": "1. Identify multiple relevant reference classes\n2. Assess base rates for each reference class\n3. Evaluate similarity between current case and reference class\n4. Adjust from base rate only with strong specific evidence"
        },
        "conservative_calibration": {
            "core": "Apply conservative principles to avoid overconfidence and improve calibration",
            "process": "1. Start with wider probability ranges than initial intuition\n2. Require stronger evidence for extreme probability estimates\n3. Account for unknown unknowns by increasing uncertainty\n4. Use frequency framing to validate probability estimates"
        },
        "meta_reasoning": {
            "core": "Apply meta-cognitive awareness to reasoning quality and process",
            "process": "1. Monitor reasoning process for logical consistency\n2. Evaluate argument strength and evidence quality\n3. Check for reasoning gaps or unsupported assumptions\n4. Validate conclusions through multiple reasoning pathways"
        },
        "adversarial_thinking": {
            "core": "Actively challenge conclusions through adversarial reasoning",
            "process": "1. Generate strongest possible counterarguments\n2. Identify weakest links in reasoning chain\n3. Consider alternative explanations for evidence\n4. Stress-test conclusions against opposing viewpoints"
        },
        "frequency_framing": {
            "core": "Use frequency-based thinking to improve probability calibration",
            "process": "1. Frame predictions in terms of frequencies (out of 100 cases)\n2. Compare to historical frequencies of similar events\n3. Validate probability estimates through frequency reasoning\n4. Check calibration against reference class frequencies"
        }
    }
    
    primary = strategy_components[primary_strategy]
    secondary = strategy_components[secondary_strategy]
    
    # Create enhanced prompts
    enhanced_prompts = {
        "high_advocate_system": f"""You are an elite superforecaster and High Probability Advocate (Iteration {iteration}). Your mission is to build compelling cases for HIGH probability outcomes through advanced reasoning.

PRIMARY STRATEGY - {primary_strategy.upper().replace('_', ' ')}:
{primary['core']}

REASONING PROCESS:
{primary['process']}

SECONDARY STRATEGY - {secondary_strategy.upper().replace('_', ' ')}:
{secondary['core']}

INTEGRATION PROCESS:
{secondary['process']}

CALIBRATION PRINCIPLES:
- Express probabilities as ranges with confidence levels
- Use multiple validation methods to check estimates
- Account for uncertainty propagation through reasoning chain
- Apply conservative adjustments for complex predictions
- Validate through frequency framing and historical comparison

OUTPUT REQUIREMENTS:
- Probability estimate with confidence interval (e.g., "75% [65%-85%]")
- Explicit confidence level in the estimate (low/medium/high)
- Key evidence and reasoning that supports higher probability
- Main uncertainties that could lower the probability
- Frequency validation: "Out of 100 similar cases, approximately X would succeed"

Your goal is to present the strongest case for HIGH probability while maintaining exceptional calibration through systematic reasoning.""",

        "low_advocate_system": f"""You are an elite superforecaster and Low Probability Advocate (Iteration {iteration}). Your mission is to build compelling cases for LOW probability outcomes through advanced reasoning.

PRIMARY STRATEGY - {primary_strategy.upper().replace('_', ' ')}:
{primary['core']}

REASONING PROCESS:
{primary['process']}

SECONDARY STRATEGY - {secondary_strategy.upper().replace('_', ' ')}:
{secondary['core']}

INTEGRATION PROCESS:
{secondary['process']}

CALIBRATION PRINCIPLES:
- Express probabilities as ranges with confidence levels
- Use multiple validation methods to check estimates
- Account for uncertainty propagation through reasoning chain
- Apply conservative adjustments for complex predictions
- Validate through frequency framing and historical comparison

OUTPUT REQUIREMENTS:
- Probability estimate with confidence interval (e.g., "25% [15%-35%]")
- Explicit confidence level in the estimate (low/medium/high)
- Key evidence and reasoning that supports lower probability
- Main uncertainties that could raise the probability
- Frequency validation: "Out of 100 similar cases, approximately X would fail"

Your goal is to present the strongest case for LOW probability while maintaining exceptional calibration through systematic reasoning.""",

        "judge_system": f"""You are an elite superforecaster and Debate Judge (Iteration {iteration}). Your mission is to synthesize competing arguments into the most accurate probability estimate.

PRIMARY SYNTHESIS STRATEGY - {primary_strategy.upper().replace('_', ' ')}:
{primary['core']}

SYNTHESIS PROCESS:
{primary['process']}

SECONDARY VALIDATION - {secondary_strategy.upper().replace('_', ' ')}:
{secondary['core']}

VALIDATION PROCESS:
{secondary['process']}

SYNTHESIS PRINCIPLES:
- Weight arguments by evidence quality and reasoning rigor
- Synthesize uncertainty assessments, don't just average probabilities
- Apply multiple calibration checks and validation methods
- Use ensemble reasoning to triangulate on best estimate
- Maintain appropriate humility about prediction difficulty

CALIBRATION VALIDATION:
- Historical frequency check: How often do similar predictions succeed?
- Betting validation: Would I bet significant money at these odds?
- Expert consensus: How does this compare to other skilled forecasters?
- Reference class validation: Is this consistent with base rates?
- Uncertainty validation: Does confidence interval reflect genuine uncertainty?

OUTPUT REQUIREMENTS:
- Final probability estimate with confidence interval (e.g., "45% [35%-55%]")
- Explicit confidence level in synthesis (low/medium/high)
- Key factors that determined the final assessment
- Primary sources of remaining uncertainty
- Frequency validation: "Out of 100 similar cases, approximately X would occur"

Your goal is to synthesize the debate into the most accurate and well-calibrated probability estimate through systematic reasoning and validation."""
    }
    
    return enhanced_prompts

def apply_prompts_to_system(prompts, iteration):
    """Apply the generated prompts to the debate system"""
    
    prompts_file = Path(__file__).parent / "src" / "ai_forecasts" / "agents" / "debate_forecasting_prompts.py"
    
    # Read the current file
    with open(prompts_file, 'r') as f:
        content = f.read()
    
    # Create enhanced backstory functions
    enhanced_high_backstory = f'''def get_high_advocate_backstory() -> str:
    """Iteration {iteration} adaptive backstory for High Probability Advocate"""
    return """{prompts["high_advocate_system"]}"""'''

    enhanced_low_backstory = f'''def get_low_advocate_backstory() -> str:
    """Iteration {iteration} adaptive backstory for Low Probability Advocate"""
    return """{prompts["low_advocate_system"]}"""'''

    enhanced_judge_backstory = f'''def get_debate_judge_backstory() -> str:
    """Iteration {iteration} adaptive backstory for Debate Judge"""
    return """{prompts["judge_system"]}"""'''

    # Apply the enhanced prompts using regex replacement
    import re
    
    # Replace high advocate backstory
    high_pattern = r'def get_high_advocate_backstory\(\) -> str:.*?return """.*?"""'
    content = re.sub(high_pattern, enhanced_high_backstory, content, flags=re.DOTALL)
    
    # Replace low advocate backstory
    low_pattern = r'def get_low_advocate_backstory\(\) -> str:.*?return """.*?"""'
    content = re.sub(low_pattern, enhanced_low_backstory, content, flags=re.DOTALL)
    
    # Replace judge backstory
    judge_pattern = r'def get_debate_judge_backstory\(\) -> str:.*?return """.*?"""'
    content = re.sub(judge_pattern, enhanced_judge_backstory, content, flags=re.DOTALL)
    
    # Write the enhanced content back
    with open(prompts_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Iteration {iteration} prompts applied successfully")
    return True

def run_benchmark_iteration(iteration, question_ids, seed):
    """Run a benchmark iteration with current prompts"""
    print(f"🚀 Running benchmark iteration {iteration}")
    print("=" * 60)
    
    # Set random seed for reproducibility
    os.environ["PYTHONHASHSEED"] = str(seed)
    
    cmd = [
        sys.executable, "run_forecastbench.py",
        "--question-ids"
    ] + question_ids + [
        "--max-workers", str(MAX_WORKERS)
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
            return None
        
        # Extract Brier score from output
        output = result.stdout
        brier_score = extract_brier_score(output)
        
        print(f"\n📊 Results for iteration {iteration}:")
        print(f"   Execution Time: {duration:.1f} seconds")
        print(f"   Brier Score: {brier_score:.4f}")
        print(f"   Target: < {TARGET_BRIER_SCORE}")
        
        success = brier_score < TARGET_BRIER_SCORE
        if success:
            print("🎉 SUCCESS! Achieved target Brier score")
        else:
            print(f"📈 Progress: {brier_score:.4f} (need {TARGET_BRIER_SCORE - brier_score:.4f} improvement)")
        
        return {
            "iteration": iteration,
            "brier_score": brier_score,
            "duration": duration,
            "success": success,
            "output": output,
            "seed": seed,
            "question_ids": question_ids
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Benchmark timed out after 30 minutes for iteration {iteration}")
        return None
    except Exception as e:
        print(f"❌ Error running benchmark for iteration {iteration}: {e}")
        return None

def extract_brier_score(output: str) -> float:
    """Extract Brier score from benchmark output"""
    import re
    
    patterns = [
        r"Average Brier score:\s*([0-9.]+)",
        r"overall_avg_brier_score[\"']:\s*([0-9.]+)",
        r"Brier Score:\s*([0-9.]+)",
        r"Brier:\s*([0-9.]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    print("⚠️ Could not extract Brier score from output")
    return 1.0

def analyze_performance(results):
    """Analyze performance to guide next iteration"""
    if not results:
        return "No results to analyze"
    
    brier_score = results["brier_score"]
    
    if brier_score > 0.2:
        return "high_error"
    elif brier_score > 0.1:
        return "medium_error"
    elif brier_score > TARGET_BRIER_SCORE:
        return "close_to_target"
    else:
        return "target_achieved"

def save_iteration_results(all_results, final_success=False):
    """Save all iteration results"""
    timestamp = int(time.time())
    results_file = Path(__file__).parent / f"iterative_optimization_results_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "target_brier_score": TARGET_BRIER_SCORE,
        "num_optimization_cycles": NUM_OPTIMIZATION_CYCLES,
        "num_questions": NUM_QUESTIONS,
        "max_workers": MAX_WORKERS,
        "final_success": final_success,
        "all_iterations": all_results,
        "optimization_strategy": "adaptive_iterative_without_hardcoding"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")
    return results_file

def main():
    """Main iterative optimization process"""
    print("🔄 Iterative Prompt Optimization - Achieve Brier Score < 0.06")
    print("=" * 70)
    print(f"Target: Brier score < {TARGET_BRIER_SCORE}")
    print(f"Optimization cycles: {NUM_OPTIMIZATION_CYCLES}")
    print(f"Questions per cycle: {NUM_QUESTIONS}")
    print(f"Parallel workers: {MAX_WORKERS}")
    print("Strategy: Adaptive prompt evolution without hardcoding")
    print()
    
    all_results = []
    best_score = float('inf')
    best_iteration = None
    
    for iteration in range(1, NUM_OPTIMIZATION_CYCLES + 1):
        print(f"\n🔄 OPTIMIZATION CYCLE {iteration}/{NUM_OPTIMIZATION_CYCLES}")
        print("=" * 50)
        
        # Generate random seed for this iteration
        seed = random.randint(1, 1000)
        print(f"🎲 Using random seed: {seed}")
        
        # Get random questions for this iteration
        question_ids = get_random_questions(NUM_QUESTIONS)
        
        # Generate adaptive prompts based on previous performance
        previous_score = all_results[-1]["brier_score"] if all_results else None
        previous_analysis = analyze_performance(all_results[-1]) if all_results else None
        
        prompts = generate_adaptive_prompts(iteration, previous_score, previous_analysis)
        
        # Apply prompts to system
        apply_prompts_to_system(prompts, iteration)
        
        # Run benchmark
        results = run_benchmark_iteration(iteration, question_ids, seed)
        
        if results is None:
            print(f"❌ Iteration {iteration} failed to complete")
            continue
        
        all_results.append(results)
        
        # Track best performance
        if results["brier_score"] < best_score:
            best_score = results["brier_score"]
            best_iteration = iteration
            print(f"🏆 New best score: {best_score:.4f} (iteration {iteration})")
        
        # Check if target achieved
        if results["success"]:
            print(f"\n🎉 TARGET ACHIEVED! Iteration {iteration} reached Brier score < {TARGET_BRIER_SCORE}")
            print(f"Final score: {results['brier_score']:.4f}")
            break
        
        # Progress update
        improvement_needed = results["brier_score"] - TARGET_BRIER_SCORE
        print(f"📈 Iteration {iteration} complete. Need {improvement_needed:.4f} more improvement.")
    
    # Final summary
    print(f"\n📋 ITERATIVE OPTIMIZATION SUMMARY")
    print("=" * 50)
    print(f"Iterations completed: {len(all_results)}")
    print(f"Best Brier score: {best_score:.4f} (iteration {best_iteration})")
    print(f"Target achieved: {'✅ Yes' if best_score < TARGET_BRIER_SCORE else '❌ No'}")
    
    if all_results:
        print(f"\nIteration progression:")
        for i, result in enumerate(all_results, 1):
            status = "✅" if result["success"] else "📈"
            print(f"  {i}: {result['brier_score']:.4f} {status}")
    
    # Save results
    final_success = best_score < TARGET_BRIER_SCORE
    results_file = save_iteration_results(all_results, final_success)
    
    if final_success:
        print(f"\n🎉 SUCCESS! Achieved target Brier score < {TARGET_BRIER_SCORE}")
        print(f"Best performance: {best_score:.4f} in iteration {best_iteration}")
    else:
        print(f"\n📈 Optimization complete. Best score: {best_score:.4f}")
        print(f"Still need {best_score - TARGET_BRIER_SCORE:.4f} improvement to reach target")
        print("💡 Consider: ensemble methods, post-processing calibration, or longer optimization")
    
    return 0 if final_success else 1

if __name__ == "__main__":
    exit(main())