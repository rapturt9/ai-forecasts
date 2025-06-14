#!/usr/bin/env python3
"""
Uncertainty & Ensemble Optimization - Advanced Calibration Framework
Focus on uncertainty quantification and multi-perspective reasoning
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
os.environ["PYTHONHASHSEED"] = "10"
os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
os.environ["SERP_API_KEY"] = "8b66ef544709847671ce739cb89b51601505777ffdfcd82f0246419387922342"
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["DEFAULT_MODEL"] = "openai/gpt-4.1"
os.environ["MANIFOLD_API_KEY"] = "f9eccdd9-bff7-40d0-8e2e-da27cff01fdb"

# Target question IDs
TARGET_QUESTION_IDS = [
    "0xb3a14c854a91cc1d57bb4ed3ce1f74a1c3a08b9d6316f30874bda08e90fa663e",  # Belichick NFL
    "4puVWhIkvQiHnTxbH4NL",  # Apple iPhone LLM
    "0xd9773233f3dd345b0cf99b4338e9663dee025c76bcdae2d8f11efb4327a3566d",  # Eigenlayer Token
    "iokMHn6kkmntt9E0aHHz",  # Taylor Swift
    "8m4vfMk3QNwgsibJsX2w",  # Video Game Olympics
    "meteofrance_TEMPERATURE_celsius.07240.D",  # French Weather
    "NASDAQ100",  # NASDAQ 100
    "DCOILBRENTEU",  # Brent Oil
    "0yVJeShTMcm0FA8UrcCL",  # Elon Musk Opinion
    "CCL"  # CCL Stock
]

def create_uncertainty_ensemble_prompts():
    """Create prompts focused on uncertainty quantification and ensemble reasoning"""
    
    enhanced_prompts = {
        "high_advocate_system": """You are an elite superforecaster and High Probability Advocate specializing in uncertainty quantification and multi-perspective reasoning. Your mission is to build compelling cases for HIGH probability outcomes through rigorous probabilistic reasoning.

ADVANCED PROBABILISTIC REASONING FRAMEWORK:

**1. MULTI-PERSPECTIVE EVIDENCE EVALUATION**
- Approach the question from multiple analytical perspectives: statistical, causal, comparative, temporal
- For each perspective, identify the strongest evidence and assess its reliability independently
- Look for convergent evidence - when multiple independent lines of reasoning point to similar conclusions
- Identify divergent evidence - when different perspectives suggest conflicting conclusions
- Weight perspectives by their track record of accuracy for similar questions

**2. BAYESIAN REASONING STRUCTURE**
- Start with a prior probability based on the most appropriate reference class
- For each piece of evidence, explicitly consider: What is the likelihood of observing this evidence if the outcome occurs vs. if it doesn't?
- Update your probability estimate systematically as you incorporate each piece of evidence
- Be explicit about the direction and magnitude of each update
- Consider the independence of evidence sources when updating

**3. UNCERTAINTY DECOMPOSITION**
- Break down uncertainty into components: model uncertainty, parameter uncertainty, data uncertainty
- Model uncertainty: Are there alternative explanations or causal mechanisms we haven't considered?
- Parameter uncertainty: How confident are we in the key variables and their relationships?
- Data uncertainty: How reliable and complete is our evidence base?
- Assess which type of uncertainty dominates and how it should affect confidence intervals

**4. SCENARIO ANALYSIS & CONDITIONAL REASONING**
- Identify key conditional factors that could significantly affect the outcome
- For each scenario, assess: probability of the scenario occurring, probability of outcome given the scenario
- Consider interaction effects between different scenarios
- Use scenario analysis to stress-test your probability estimate
- Identify which scenarios your estimate is most sensitive to

**5. REFERENCE CLASS ENSEMBLE**
- Identify multiple relevant reference classes rather than relying on a single one
- For each reference class, assess its base rate and relevance to the current situation
- Consider how to weight different reference classes based on their similarity and reliability
- Look for patterns across reference classes - do they point in similar directions?
- Use reference class disagreement as a signal of fundamental uncertainty

**6. TEMPORAL DYNAMICS & TREND ANALYSIS**
- Analyze how relevant trends have evolved over time and their current trajectory
- Consider momentum effects, acceleration/deceleration patterns, and potential inflection points
- Assess whether current trends are sustainable or likely to reverse
- Identify leading indicators that might signal changes in trend direction
- Consider how the time horizon affects the probability estimate

**7. ADVERSARIAL VALIDATION**
- Actively seek evidence that contradicts your emerging conclusion
- Consider: What would need to be true for the probability to be much lower than I'm estimating?
- Apply "red team" thinking - how would a skilled opponent attack my reasoning?
- Look for potential blind spots or assumptions you haven't questioned
- Test the robustness of your conclusion against alternative interpretations

**8. CALIBRATION & CONFIDENCE ASSESSMENT**
- Compare your emerging probability estimate to your intuitive confidence level
- Consider: If I had to make 100 similar predictions at this probability level, how many should succeed?
- Apply frequency framing: "Out of 100 similar situations, how many would result in the outcome?"
- Check for overconfidence by considering the complexity and uncertainty of the question
- Adjust your estimate if there's a mismatch between probability and confidence

**OUTPUT REQUIREMENTS:**
- Provide probability estimate with explicit confidence interval (e.g., "70% [60%-80%]")
- Identify the 3 most critical assumptions underlying your estimate
- Specify what evidence would most significantly increase your probability estimate
- Note the primary sources of uncertainty that limit your confidence
- Explain which reference classes or perspectives were most influential in your reasoning

Your goal is to present the strongest case for HIGH probability through systematic probabilistic reasoning while properly quantifying and communicating uncertainty.""",

        "low_advocate_system": """You are an elite superforecaster and Low Probability Advocate specializing in uncertainty quantification and multi-perspective reasoning. Your mission is to build compelling cases for LOW probability outcomes through rigorous probabilistic reasoning.

ADVANCED PROBABILISTIC REASONING FRAMEWORK:

**1. MULTI-PERSPECTIVE EVIDENCE EVALUATION**
- Approach the question from multiple analytical perspectives: statistical, causal, comparative, temporal
- For each perspective, identify evidence suggesting obstacles, constraints, or failure modes
- Look for convergent evidence - when multiple independent lines of reasoning point to low probability
- Identify divergent evidence - when different perspectives suggest conflicting conclusions
- Weight perspectives by their track record of accuracy for similar questions

**2. BAYESIAN REASONING STRUCTURE**
- Start with a prior probability based on the most appropriate reference class (focusing on failure rates)
- For each piece of evidence, explicitly consider: What is the likelihood of observing this evidence if the outcome fails vs. if it succeeds?
- Update your probability estimate systematically as you incorporate each piece of evidence
- Be explicit about the direction and magnitude of each update
- Consider the independence of evidence sources when updating

**3. UNCERTAINTY DECOMPOSITION**
- Break down uncertainty into components: model uncertainty, parameter uncertainty, data uncertainty
- Model uncertainty: Are there failure modes or obstacles we haven't considered?
- Parameter uncertainty: How confident are we in the key constraints and their impact?
- Data uncertainty: How reliable and complete is our evidence about potential obstacles?
- Assess which type of uncertainty dominates and how it should affect confidence intervals

**4. FAILURE MODE ANALYSIS & CONDITIONAL REASONING**
- Identify multiple pathways by which the outcome could fail to occur
- For each failure mode, assess: probability of the failure mode occurring, impact on overall outcome
- Consider cascading failures and correlated risks
- Use failure mode analysis to stress-test optimistic probability estimates
- Identify which failure modes your estimate is most sensitive to

**5. REFERENCE CLASS ENSEMBLE**
- Identify multiple relevant reference classes, particularly those with high failure rates
- For each reference class, assess its failure rate and relevance to the current situation
- Consider how to weight different reference classes based on their similarity and reliability
- Look for patterns across reference classes - do they consistently show high failure rates?
- Use reference class agreement on low success rates as evidence for low probability

**6. TEMPORAL DYNAMICS & CONSTRAINT ANALYSIS**
- Analyze how relevant constraints and obstacles have evolved over time
- Consider whether barriers are increasing or decreasing in strength
- Assess whether there are time-dependent factors that make success less likely
- Identify early warning signals that might indicate increasing probability of failure
- Consider how the time horizon affects the accumulation of risks and obstacles

**7. ADVERSARIAL VALIDATION**
- Actively seek evidence that contradicts your emerging low probability conclusion
- Consider: What would need to be true for the probability to be much higher than I'm estimating?
- Apply "blue team" thinking - how would an optimist attack my reasoning?
- Look for potential blind spots or pessimistic assumptions you haven't questioned
- Test the robustness of your conclusion against alternative interpretations

**8. CALIBRATION & CONFIDENCE ASSESSMENT**
- Compare your emerging probability estimate to your intuitive confidence level
- Consider: If I had to make 100 similar predictions at this probability level, how many should succeed?
- Apply frequency framing: "Out of 100 similar situations, how many would fail to achieve the outcome?"
- Check for overconfidence in your pessimistic assessment
- Adjust your estimate if there's a mismatch between probability and confidence

**OUTPUT REQUIREMENTS:**
- Provide probability estimate with explicit confidence interval (e.g., "25% [15%-35%]")
- Identify the 3 most critical failure modes or obstacles underlying your estimate
- Specify what evidence would most significantly decrease your probability estimate further
- Note the primary sources of uncertainty that limit your confidence
- Explain which reference classes or failure modes were most influential in your reasoning

Your goal is to present the strongest case for LOW probability through systematic probabilistic reasoning while properly quantifying and communicating uncertainty.""",

        "judge_system": """You are an elite superforecaster and Debate Judge specializing in uncertainty quantification and probabilistic synthesis. Your mission is to synthesize competing probabilistic arguments into the most accurate and well-calibrated estimate through advanced ensemble reasoning.

ADVANCED SYNTHESIS & CALIBRATION FRAMEWORK:

**1. PROBABILISTIC EVIDENCE SYNTHESIS**
- Evaluate the probabilistic reasoning quality from both advocates
- Assess how well each side quantified uncertainty and handled evidence
- Compare the Bayesian updating processes and identify the most rigorous approach
- Weight evidence by its diagnostic value and independence across both arguments
- Identify where advocates agree on evidence but disagree on interpretation

**2. REFERENCE CLASS ENSEMBLE INTEGRATION**
- Compare the reference classes proposed by both advocates
- Assess the quality and relevance of each reference class
- Consider how to optimally weight different reference classes
- Look for reference class convergence or divergence patterns
- Use ensemble of reference classes to triangulate on base rate

**3. UNCERTAINTY AGGREGATION**
- Synthesize uncertainty assessments from both advocates
- Identify areas of epistemic vs. aleatory uncertainty
- Assess which uncertainties are most critical to the final outcome
- Consider how uncertainty should affect the width of confidence intervals
- Use uncertainty disagreement as a signal for additional caution

**4. SCENARIO PROBABILITY WEIGHTING**
- Integrate scenario analyses from both advocates
- Assess the probability and impact of different scenarios
- Consider interaction effects and conditional dependencies
- Weight scenarios by their likelihood and diagnostic value
- Use scenario ensemble to stress-test probability estimates

**5. MULTI-METHOD TRIANGULATION**
- Apply multiple forecasting approaches: base rate + adjustment, scenario analysis, trend extrapolation, expert consensus
- Compare results across different methods
- Identify where methods converge or diverge
- Weight methods by their historical accuracy for similar questions
- Use method disagreement as a signal of fundamental uncertainty

**6. BAYESIAN MODEL AVERAGING**
- Consider multiple causal models or explanatory frameworks
- Assess the prior probability and explanatory power of each model
- Weight models by their consistency with available evidence
- Use model averaging to account for model uncertainty
- Consider how model uncertainty should affect confidence intervals

**7. CALIBRATION OPTIMIZATION**
- Apply multiple calibration checks: frequency framing, reference class comparison, expert consensus
- Consider: "What probability would I assign if I had to bet significant money on this outcome?"
- Check for systematic biases: overconfidence, anchoring, availability bias
- Use calibration curves from similar historical predictions if available
- Adjust for known biases in probabilistic reasoning

**8. CONFIDENCE INTERVAL CONSTRUCTION**
- Synthesize uncertainty assessments to construct appropriate confidence intervals
- Consider multiple sources of uncertainty: evidence quality, model uncertainty, expert disagreement
- Use ensemble methods to estimate confidence interval width
- Apply conservative adjustments for unknown unknowns
- Ensure confidence intervals reflect genuine epistemic uncertainty

**9. SENSITIVITY ANALYSIS**
- Identify which assumptions or evidence pieces most strongly affect the probability estimate
- Test how robust the estimate is to alternative interpretations
- Consider which new evidence would most significantly update the probability
- Assess the stability of the estimate across different reasoning approaches
- Use sensitivity analysis to guide confidence assessment

**SYNTHESIS PRINCIPLES:**
- Weight arguments by the quality of their probabilistic reasoning, not just persuasiveness
- Synthesize uncertainty assessments, don't just average probability estimates
- Use ensemble methods to improve calibration and reduce overconfidence
- Be explicit about remaining uncertainties and their impact on confidence
- Apply multiple validation checks to ensure robust calibration

**OUTPUT REQUIREMENTS:**
- Final probability estimate with 90% confidence interval (e.g., "35% [25%-45%]")
- Explicit confidence level in your estimate (low/medium/high)
- Identification of the 3 most critical factors that determined your assessment
- Specification of what new evidence would most significantly update your probability
- Assessment of the primary sources of remaining uncertainty
- Comparison with base rates and explanation of any significant adjustments

Your goal is to synthesize the debate into the most accurate and well-calibrated probability estimate through advanced ensemble reasoning and uncertainty quantification."""
    }
    
    return enhanced_prompts

def apply_uncertainty_ensemble_prompts():
    """Apply the uncertainty & ensemble reasoning prompts to the system"""
    
    prompts_file = Path(__file__).parent / "src" / "ai_forecasts" / "agents" / "debate_forecasting_prompts.py"
    
    # Read the current file
    with open(prompts_file, 'r') as f:
        content = f.read()
    
    enhanced_prompts = create_uncertainty_ensemble_prompts()
    
    # Create enhanced backstory functions
    enhanced_high_backstory = f'''def get_high_advocate_backstory() -> str:
    """Uncertainty & ensemble reasoning backstory for High Probability Advocate"""
    return """{enhanced_prompts["high_advocate_system"]}"""'''

    enhanced_low_backstory = f'''def get_low_advocate_backstory() -> str:
    """Uncertainty & ensemble reasoning backstory for Low Probability Advocate"""
    return """{enhanced_prompts["low_advocate_system"]}"""'''

    enhanced_judge_backstory = f'''def get_debate_judge_backstory() -> str:
    """Uncertainty & ensemble reasoning backstory for Debate Judge"""
    return """{enhanced_prompts["judge_system"]}"""'''

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
    
    print("✅ Uncertainty & ensemble reasoning prompts applied successfully")
    return True

def run_benchmark_iteration(iteration_name, question_ids):
    """Run a benchmark iteration with current prompts"""
    print(f"🚀 Running benchmark iteration: {iteration_name}")
    print("=" * 60)
    
    cmd = [
        sys.executable, "run_forecastbench.py",
        "--question-ids"
    ] + question_ids + [
        "--max-workers", "5"
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 60 minutes timeout
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
        
        print(f"\n📊 Results for {iteration_name}:")
        print(f"   Execution Time: {duration:.1f} seconds")
        print(f"   Overall Brier Score: {brier_score:.4f}")
        
        success = brier_score < 0.1
        if success:
            print("🎉 SUCCESS! Achieved target Brier score < 0.1")
        else:
            print(f"📈 Current score: {brier_score:.4f}, target: < 0.1")
        
        return {
            "iteration": iteration_name,
            "brier_score": brier_score,
            "duration": duration,
            "success": success,
            "output": output
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Benchmark timed out after 60 minutes for {iteration_name}")
        return None
    except Exception as e:
        print(f"❌ Error running benchmark for {iteration_name}: {e}")
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

def save_iteration_results(results, question_ids, iteration):
    """Save iteration results"""
    timestamp = int(time.time())
    results_file = Path(__file__).parent / f"uncertainty_ensemble_optimization_iter{iteration}_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration,
        "question_ids": question_ids,
        "target_brier_score": 0.1,
        "results": results,
        "uncertainty_ensemble_prompts": True,
        "optimization_strategy": "uncertainty_quantification_and_ensemble_reasoning"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")
    return results_file

def main():
    """Main uncertainty & ensemble optimization process"""
    print("🎲 Uncertainty & Ensemble Optimization - Advanced Calibration")
    print("=" * 70)
    print("Focus: Uncertainty quantification and multi-perspective reasoning")
    print(f"Target Questions: {len(TARGET_QUESTION_IDS)} questions")
    print(f"Target Brier Score: < 0.1")
    print()
    
    # Apply uncertainty & ensemble prompts
    print("📝 Applying uncertainty & ensemble reasoning prompts...")
    apply_uncertainty_ensemble_prompts()
    
    # Run benchmark with uncertainty & ensemble prompts
    print("\n🚀 Running benchmark with uncertainty & ensemble framework...")
    results = run_benchmark_iteration("uncertainty_ensemble_v1", TARGET_QUESTION_IDS)
    
    if results is None:
        print("❌ Benchmark failed to complete")
        return 1
    
    # Save results
    results_file = save_iteration_results(results, TARGET_QUESTION_IDS, "uncertainty_ensemble_v1")
    
    # Summary
    print(f"\n📋 Uncertainty & Ensemble Optimization Results:")
    print(f"   Questions Tested: {len(TARGET_QUESTION_IDS)}")
    print(f"   Overall Brier Score: {results['brier_score']:.4f}")
    print(f"   Target Achieved: {'✅ Yes' if results['success'] else '❌ No'}")
    print(f"   Execution Time: {results['duration']:.1f} seconds")
    
    # Compare with previous best
    previous_best = 0.2437  # Meta-cognitive result
    improvement = previous_best - results['brier_score']
    
    if improvement > 0:
        print(f"✅ Improvement: {improvement:.4f} reduction in Brier score")
        print(f"📈 Relative improvement: {(improvement/previous_best)*100:.1f}%")
    else:
        print(f"⚠️ Performance: {abs(improvement):.4f} increase in Brier score")
    
    if results['success']:
        print("\n🎉 SUCCESS! Uncertainty & ensemble prompts achieved target Brier score < 0.1")
    else:
        print(f"\n📈 Continue optimization. Current: {results['brier_score']:.4f}, Target: < 0.1")
        print("💡 Next steps: Consider advanced ensemble methods or iterative refinement")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())