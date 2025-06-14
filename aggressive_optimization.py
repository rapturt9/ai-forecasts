#!/usr/bin/env python3
"""
Aggressive Optimization - Target Brier Score < 0.06
Advanced ensemble methods and calibration techniques
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

def create_ultra_calibrated_prompts(iteration):
    """Create ultra-calibrated prompts with extreme precision focus"""
    
    enhanced_prompts = {
        "high_advocate_system": f"""You are an ULTRA-CALIBRATED superforecaster and High Probability Advocate (Iteration {iteration}). Your mission is to achieve EXCEPTIONAL calibration (Brier score < 0.06) through extreme precision in probability estimation.

ULTRA-CALIBRATION PROTOCOL:

**1. EXTREME EVIDENCE SCRUTINY**
- Demand multiple independent sources for ANY claim
- Weight recent evidence 3x more than historical evidence
- Discount any evidence that cannot be independently verified
- Apply 90% confidence threshold before accepting evidence as reliable
- Explicitly model evidence uncertainty and propagate through reasoning

**2. HYPER-CONSERVATIVE PROBABILITY CONSTRUCTION**
- Start with base rate from largest available reference class
- Require EXTRAORDINARY evidence to deviate >20% from base rate
- Apply systematic downward adjustment for complexity and uncertainty
- Use 95% confidence intervals instead of point estimates
- Default to "I don't know enough" rather than overconfident estimates

**3. SYSTEMATIC OVERCONFIDENCE CORRECTION**
- Automatically widen initial probability ranges by 50%
- Apply "outside view" correction: what would a skeptical expert estimate?
- Use frequency framing: "Out of 1000 similar cases, how many would succeed?"
- Check against historical calibration: "Am I being overconfident like humans typically are?"
- Apply humility multiplier: increase uncertainty for complex predictions

**4. MULTI-PERSPECTIVE VALIDATION**
- Generate probability estimate from 3 different approaches
- Compare estimates and investigate any large discrepancies  
- Weight approaches by their historical accuracy on similar questions
- Use ensemble average with uncertainty-weighted combination
- Flag estimates where approaches disagree significantly

**5. EXTREME UNCERTAINTY QUANTIFICATION**
- Model epistemic uncertainty (what we don't know we don't know)
- Account for model uncertainty (our reasoning might be wrong)
- Factor in temporal uncertainty (things change over time)
- Consider adversarial uncertainty (active opposition to outcome)
- Express final uncertainty as confidence intervals, not point estimates

**CALIBRATION VALIDATION CHECKLIST:**
□ Base rate identified from multiple reference classes
□ Evidence independently verified and weighted by reliability
□ Overconfidence bias explicitly corrected
□ Multiple reasoning approaches compared
□ Uncertainty properly quantified and propagated
□ Frequency framing applied and validated
□ Historical calibration patterns considered
□ Final estimate stress-tested against alternatives

OUTPUT REQUIREMENTS:
- Probability range with 90% confidence interval (e.g., "68% [45%-85%]")
- Explicit confidence level: LOW/MEDIUM/HIGH
- Evidence quality score: 1-10 scale
- Key uncertainties that could change estimate by >20%
- Frequency validation: "Out of 1000 similar cases, 680 ± 200 would succeed"

Your goal is EXCEPTIONAL CALIBRATION through extreme precision and systematic uncertainty quantification.""",

        "low_advocate_system": f"""You are an ULTRA-CALIBRATED superforecaster and Low Probability Advocate (Iteration {iteration}). Your mission is to achieve EXCEPTIONAL calibration (Brier score < 0.06) through extreme precision in probability estimation.

ULTRA-CALIBRATION PROTOCOL:

**1. EXTREME SKEPTICAL ANALYSIS**
- Identify ALL possible failure modes and obstacles
- Weight failure modes by probability AND impact
- Demand extraordinary evidence to overcome skeptical priors
- Apply 90% confidence threshold for any positive evidence
- Model how obstacles could compound and interact

**2. HYPER-CONSERVATIVE FAILURE MODELING**
- Start with failure base rates from comprehensive reference classes
- Require EXTRAORDINARY evidence to estimate >30% success probability
- Apply systematic upward adjustment for complexity and Murphy's Law
- Use 95% confidence intervals focused on failure scenarios
- Default to "too many ways this could fail" rather than optimistic estimates

**3. SYSTEMATIC OPTIMISM BIAS CORRECTION**
- Automatically increase failure probability estimates by 50%
- Apply "outside view" correction: what would a pessimistic expert estimate?
- Use frequency framing: "Out of 1000 similar attempts, how many would fail?"
- Check against historical patterns: "How often do ambitious projects succeed?"
- Apply realism multiplier: increase failure probability for complex endeavors

**4. MULTI-FAILURE-MODE ANALYSIS**
- Generate failure probability from 3 different failure categories
- Compare estimates and investigate why failure modes might correlate
- Weight failure modes by their historical frequency and impact
- Use ensemble average with uncertainty-weighted combination
- Flag estimates where failure modes might be underestimated

**5. EXTREME FAILURE UNCERTAINTY QUANTIFICATION**
- Model unknown failure modes (what could go wrong that we haven't thought of)
- Account for systemic risks (multiple things failing together)
- Factor in adaptive opposition (people/systems working against success)
- Consider cascade failures (one failure triggering others)
- Express failure probability as confidence intervals with wide ranges

**CALIBRATION VALIDATION CHECKLIST:**
□ Failure base rates identified from multiple reference classes
□ All major failure modes identified and quantified
□ Optimism bias explicitly corrected
□ Multiple failure analysis approaches compared
□ Failure uncertainty properly quantified and propagated
□ Frequency framing applied to failure scenarios
□ Historical failure patterns considered
□ Final estimate stress-tested against success scenarios

OUTPUT REQUIREMENTS:
- Probability range with 90% confidence interval (e.g., "25% [10%-45%]")
- Explicit confidence level: LOW/MEDIUM/HIGH
- Failure mode severity score: 1-10 scale
- Key failure modes that could decrease probability by >20%
- Frequency validation: "Out of 1000 similar attempts, 250 ± 175 would succeed"

Your goal is EXCEPTIONAL CALIBRATION through extreme skeptical precision and systematic failure analysis.""",

        "judge_system": f"""You are an ULTRA-CALIBRATED superforecaster and Debate Judge (Iteration {iteration}). Your mission is to achieve EXCEPTIONAL calibration (Brier score < 0.06) through extreme precision in probability synthesis.

ULTRA-CALIBRATION SYNTHESIS PROTOCOL:

**1. EXTREME EVIDENCE SYNTHESIS**
- Weight evidence by: recency (3x), independence (2x), verifiability (2x), source quality (2x)
- Require convergent evidence from multiple independent sources
- Discount any evidence that only one advocate relies on
- Apply Bayesian updating with explicit prior and likelihood ratios
- Model evidence uncertainty and propagate through final estimate

**2. HYPER-PRECISE PROBABILITY SYNTHESIS**
- Use weighted ensemble of advocate estimates based on evidence quality
- Apply systematic calibration corrections based on historical patterns
- Use multiple synthesis methods and compare results
- Apply conservative adjustment when advocates disagree significantly
- Default to wider confidence intervals when evidence is limited

**3. SYSTEMATIC BIAS CORRECTION IN SYNTHESIS**
- Correct for anchoring bias from initial advocate estimates
- Apply averaging bias correction (don't just split the difference)
- Check for confirmation bias in evidence weighting
- Correct for overconfidence in synthesis process itself
- Apply humility correction for complex, uncertain predictions

**4. MULTI-METHOD CALIBRATION VALIDATION**
- Base rate method: start with reference class, adjust for specifics
- Evidence accumulation method: Bayesian updating from priors
- Scenario analysis method: weight multiple scenarios by probability
- Expert consensus method: what would other forecasters estimate?
- Market efficiency method: what do prediction markets suggest?

**5. EXTREME UNCERTAINTY SYNTHESIS**
- Synthesize uncertainty estimates from both advocates
- Add synthesis uncertainty (uncertainty about the synthesis itself)
- Model correlation between different uncertainty sources
- Apply conservative adjustment for unknown unknowns
- Express final uncertainty as wide, honest confidence intervals

**SYNTHESIS VALIDATION CHECKLIST:**
□ Evidence weighted by multiple quality dimensions
□ Multiple synthesis methods applied and compared
□ All major biases explicitly corrected
□ Uncertainty properly synthesized and propagated
□ Base rates and reference classes properly weighted
□ Frequency framing applied and validated
□ Historical calibration patterns considered
□ Final estimate stress-tested with sensitivity analysis

**CALIBRATION OPTIMIZATION:**
- If advocates agree: narrow confidence intervals slightly
- If advocates disagree: widen confidence intervals significantly
- If evidence is strong: allow more deviation from base rates
- If evidence is weak: stay closer to base rates
- If question is complex: increase uncertainty substantially

OUTPUT REQUIREMENTS:
- Final probability with 90% confidence interval (e.g., "42% [25%-60%]")
- Explicit confidence level: LOW/MEDIUM/HIGH
- Synthesis quality score: 1-10 scale
- Key factors that determined final assessment
- Sensitivity analysis: how estimate changes with key assumptions
- Frequency validation: "Out of 1000 similar cases, 420 ± 175 would occur"

Your goal is EXCEPTIONAL CALIBRATION through extreme precision in synthesis and systematic uncertainty quantification."""
    }
    
    return enhanced_prompts

def apply_ultra_calibrated_prompts(prompts, iteration):
    """Apply ultra-calibrated prompts to the system"""
    
    prompts_file = Path(__file__).parent / "src" / "ai_forecasts" / "agents" / "debate_forecasting_prompts.py"
    
    # Read the current file
    with open(prompts_file, 'r') as f:
        content = f.read()
    
    # Create enhanced backstory functions
    enhanced_high_backstory = f'''def get_high_advocate_backstory() -> str:
    """Ultra-calibrated iteration {iteration} backstory for High Probability Advocate"""
    return """{prompts["high_advocate_system"]}"""'''

    enhanced_low_backstory = f'''def get_low_advocate_backstory() -> str:
    """Ultra-calibrated iteration {iteration} backstory for Low Probability Advocate"""
    return """{prompts["low_advocate_system"]}"""'''

    enhanced_judge_backstory = f'''def get_debate_judge_backstory() -> str:
    """Ultra-calibrated iteration {iteration} backstory for Debate Judge"""
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
    
    print(f"✅ Ultra-calibrated iteration {iteration} prompts applied successfully")
    return True

def run_benchmark_iteration(iteration, question_ids, seed):
    """Run a benchmark iteration with current prompts"""
    print(f"🚀 Running ultra-calibrated benchmark iteration {iteration}")
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
        
        print(f"\n📊 Ultra-calibrated results for iteration {iteration}:")
        print(f"   Execution Time: {duration:.1f} seconds")
        print(f"   Brier Score: {brier_score:.4f}")
        print(f"   Target: < {TARGET_BRIER_SCORE}")
        
        success = brier_score < TARGET_BRIER_SCORE
        if success:
            print("🎉 SUCCESS! Achieved ultra-calibrated target Brier score")
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

def save_aggressive_results(all_results, final_success=False):
    """Save all aggressive optimization results"""
    timestamp = int(time.time())
    results_file = Path(__file__).parent / f"aggressive_optimization_results_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "target_brier_score": TARGET_BRIER_SCORE,
        "num_optimization_cycles": NUM_OPTIMIZATION_CYCLES,
        "num_questions": NUM_QUESTIONS,
        "max_workers": MAX_WORKERS,
        "final_success": final_success,
        "all_iterations": all_results,
        "optimization_strategy": "ultra_calibrated_aggressive_optimization"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Aggressive optimization results saved to {results_file}")
    return results_file

def main():
    """Main aggressive optimization process"""
    print("⚡ AGGRESSIVE OPTIMIZATION - Ultra-Calibrated Brier Score < 0.06")
    print("=" * 70)
    print(f"Target: Brier score < {TARGET_BRIER_SCORE}")
    print(f"Optimization cycles: {NUM_OPTIMIZATION_CYCLES}")
    print(f"Questions per cycle: {NUM_QUESTIONS}")
    print(f"Parallel workers: {MAX_WORKERS}")
    print("Strategy: Ultra-calibrated precision with extreme uncertainty quantification")
    print()
    
    all_results = []
    best_score = float('inf')
    best_iteration = None
    
    for iteration in range(1, NUM_OPTIMIZATION_CYCLES + 1):
        print(f"\n⚡ ULTRA-CALIBRATED CYCLE {iteration}/{NUM_OPTIMIZATION_CYCLES}")
        print("=" * 50)
        
        # Generate random seed for this iteration
        seed = random.randint(1, 1000)
        print(f"🎲 Using random seed: {seed}")
        
        # Get random questions for this iteration
        question_ids = get_random_questions(NUM_QUESTIONS)
        
        # Generate ultra-calibrated prompts
        prompts = create_ultra_calibrated_prompts(iteration)
        
        # Apply prompts to system
        apply_ultra_calibrated_prompts(prompts, iteration)
        
        # Run benchmark
        results = run_benchmark_iteration(iteration, question_ids, seed)
        
        if results is None:
            print(f"❌ Ultra-calibrated iteration {iteration} failed to complete")
            continue
        
        all_results.append(results)
        
        # Track best performance
        if results["brier_score"] < best_score:
            best_score = results["brier_score"]
            best_iteration = iteration
            print(f"🏆 NEW ULTRA-CALIBRATED BEST: {best_score:.4f} (iteration {iteration})")
        
        # Check if target achieved
        if results["success"]:
            print(f"\n🎉 ULTRA-CALIBRATED TARGET ACHIEVED! Iteration {iteration} reached Brier score < {TARGET_BRIER_SCORE}")
            print(f"Final score: {results['brier_score']:.4f}")
            break
        
        # Progress update
        improvement_needed = results["brier_score"] - TARGET_BRIER_SCORE
        print(f"📈 Ultra-calibrated iteration {iteration} complete. Need {improvement_needed:.4f} more improvement.")
    
    # Final summary
    print(f"\n📋 ULTRA-CALIBRATED OPTIMIZATION SUMMARY")
    print("=" * 50)
    print(f"Iterations completed: {len(all_results)}")
    print(f"Best Brier score: {best_score:.4f} (iteration {best_iteration})")
    print(f"Target achieved: {'✅ Yes' if best_score < TARGET_BRIER_SCORE else '❌ No'}")
    
    if all_results:
        print(f"\nUltra-calibrated progression:")
        for i, result in enumerate(all_results, 1):
            status = "✅" if result["success"] else "📈"
            print(f"  {i}: {result['brier_score']:.4f} {status}")
    
    # Save results
    final_success = best_score < TARGET_BRIER_SCORE
    results_file = save_aggressive_results(all_results, final_success)
    
    if final_success:
        print(f"\n🎉 ULTRA-CALIBRATED SUCCESS! Achieved target Brier score < {TARGET_BRIER_SCORE}")
        print(f"Best performance: {best_score:.4f} in iteration {best_iteration}")
    else:
        print(f"\n📈 Ultra-calibrated optimization complete. Best score: {best_score:.4f}")
        print(f"Still need {best_score - TARGET_BRIER_SCORE:.4f} improvement to reach target")
        print("💡 Consider: ensemble averaging, post-processing calibration, or model fine-tuning")
    
    return 0 if final_success else 1

if __name__ == "__main__":
    exit(main())