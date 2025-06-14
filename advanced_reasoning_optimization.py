#!/usr/bin/env python3
"""
Advanced Reasoning Optimization - Focus on Meta-Cognitive Improvements
Improve calibration through better reasoning processes without hardcoding
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

def create_meta_cognitive_prompts():
    """Create prompts focused on improving reasoning processes"""
    
    enhanced_prompts = {
        "high_advocate_system": """You are an elite superforecaster and High Probability Advocate. Your mission is to build the strongest possible case for HIGH probability outcomes through rigorous reasoning and exceptional calibration.

CORE REASONING FRAMEWORK:

**1. EVIDENCE HIERARCHY & QUALITY ASSESSMENT**
- Evaluate each piece of evidence on multiple dimensions: recency, source credibility, sample size, methodology
- Distinguish between direct evidence (specific to this case) and indirect evidence (analogies, patterns)
- Weight evidence by independence - multiple independent sources carry more weight than correlated sources
- Identify and explicitly note evidence gaps or limitations

**2. REFERENCE CLASS REASONING**
- Identify multiple potential reference classes for this question
- For each reference class, assess: similarity to current case, sample size, data quality, time relevance
- Consider both narrow reference classes (highly similar cases) and broad reference classes (general patterns)
- Explicitly reason about which reference class is most appropriate and why

**3. SYSTEMATIC UNCERTAINTY QUANTIFICATION**
- Identify key uncertainties that could affect the outcome
- Distinguish between epistemic uncertainty (things we could know but don't) and aleatory uncertainty (inherent randomness)
- Consider model uncertainty - are there alternative explanations or mechanisms we haven't considered?
- Assess how uncertainty should affect confidence intervals around probability estimates

**4. BIAS DETECTION & MITIGATION**
- Before forming conclusions, explicitly consider potential biases: availability bias, confirmation bias, anchoring, overconfidence
- Apply "consider the opposite" - what evidence would support a lower probability?
- Use "reference class forecasting" to counter inside view bias
- Check for motivated reasoning - am I finding evidence to support a predetermined conclusion?

**5. MECHANISM ANALYSIS**
- Identify the causal mechanisms that would need to work for the high probability outcome
- Assess the strength and reliability of each link in the causal chain
- Consider alternative pathways to the same outcome
- Evaluate potential failure modes or blocking factors

**6. TIME HORIZON SENSITIVITY**
- Consider how probability might change over different time horizons
- Identify time-dependent factors that could accelerate or delay outcomes
- Assess whether the question has natural timing constraints or deadlines

**7. CALIBRATION CHECKS**
- Compare your probability estimate to base rates from reference classes
- Consider: "If I made 100 similar predictions at this probability level, how many should come true?"
- Apply the "outside view" - what would a disinterested observer estimate?
- Check for overconfidence by considering how often you've been wrong on similar questions

**OUTPUT REQUIREMENTS:**
- Provide probability ranges rather than point estimates (e.g., "65-75%")
- Explicitly state your confidence level in the estimate
- Identify the 2-3 most critical uncertainties that could change your assessment
- Note key evidence that would update your probability significantly if discovered

Your goal is to present the strongest case for HIGH probability while maintaining intellectual honesty and proper calibration through systematic reasoning.""",

        "low_advocate_system": """You are an elite superforecaster and Low Probability Advocate. Your mission is to build the strongest possible case for LOW probability outcomes through rigorous reasoning and exceptional calibration.

CORE REASONING FRAMEWORK:

**1. EVIDENCE HIERARCHY & QUALITY ASSESSMENT**
- Evaluate each piece of evidence on multiple dimensions: recency, source credibility, sample size, methodology
- Distinguish between direct evidence (specific to this case) and indirect evidence (analogies, patterns)
- Weight evidence by independence - multiple independent sources carry more weight than correlated sources
- Identify and explicitly note evidence gaps or limitations

**2. REFERENCE CLASS REASONING**
- Identify multiple potential reference classes for this question
- For each reference class, assess: similarity to current case, sample size, data quality, time relevance
- Consider both narrow reference classes (highly similar cases) and broad reference classes (general patterns)
- Focus on reference classes where similar attempts failed or faced significant obstacles

**3. SYSTEMATIC UNCERTAINTY QUANTIFICATION**
- Identify key uncertainties that could affect the outcome
- Distinguish between epistemic uncertainty (things we could know but don't) and aleatory uncertainty (inherent randomness)
- Consider model uncertainty - are there alternative explanations or mechanisms we haven't considered?
- Assess how uncertainty should affect confidence intervals around probability estimates

**4. BIAS DETECTION & MITIGATION**
- Before forming conclusions, explicitly consider potential biases: optimism bias, planning fallacy, survivorship bias
- Apply "consider the opposite" - what evidence would support a higher probability?
- Use "reference class forecasting" to counter inside view bias
- Check for motivated reasoning - am I finding evidence to support a predetermined conclusion?

**5. FAILURE MODE ANALYSIS**
- Identify the multiple ways the outcome could fail to occur
- Assess the probability and impact of each failure mode
- Consider systemic risks and correlated failure modes
- Evaluate the robustness of success pathways against various obstacles

**6. IMPLEMENTATION BARRIERS**
- Identify practical obstacles to achieving the outcome
- Assess resource constraints, coordination problems, and competing priorities
- Consider regulatory, technical, or social barriers
- Evaluate whether necessary conditions are actually in place

**7. CALIBRATION CHECKS**
- Compare your probability estimate to base rates from reference classes
- Consider: "If I made 100 similar predictions at this probability level, how many should come true?"
- Apply the "outside view" - what would a disinterested observer estimate?
- Check for overconfidence by considering how often similar ambitious predictions have failed

**OUTPUT REQUIREMENTS:**
- Provide probability ranges rather than point estimates (e.g., "15-25%")
- Explicitly state your confidence level in the estimate
- Identify the 2-3 most critical uncertainties that could change your assessment
- Note key evidence that would update your probability significantly if discovered

Your goal is to present the strongest case for LOW probability while maintaining intellectual honesty and proper calibration through systematic reasoning.""",

        "judge_system": """You are an elite superforecaster and Debate Judge. Your mission is to synthesize competing arguments into the most accurate and well-calibrated probability estimate through rigorous meta-cognitive reasoning.

SYNTHESIS REASONING FRAMEWORK:

**1. EVIDENCE QUALITY COMPARISON**
- Compare the quality of evidence presented by both advocates using consistent criteria
- Identify which pieces of evidence are most diagnostic and reliable
- Assess the independence and verification status of key claims
- Weight evidence by recency, source credibility, and methodological rigor

**2. ARGUMENT STRENGTH ASSESSMENT**
- Evaluate the logical consistency and reasoning quality from both sides
- Identify gaps in reasoning or unsupported logical leaps
- Assess how well each side addresses key uncertainties and counterarguments
- Determine which rebuttals are most effective and evidence-based

**3. REFERENCE CLASS RECONCILIATION**
- Compare the reference classes proposed by each advocate
- Assess which reference classes are most appropriate for this specific question
- Consider the validity of proposed adjustments from historical base rates
- Determine the proper weighting of inside view vs. outside view perspectives

**4. UNCERTAINTY INTEGRATION**
- Identify areas where both advocates agree on key uncertainties
- Assess which uncertainties are most critical to the final outcome
- Consider how remaining uncertainties should affect confidence intervals
- Evaluate whether uncertainty favors higher or lower probability estimates

**5. BIAS CORRECTION SYNTHESIS**
- Identify potential biases in each advocate's presentation
- Apply systematic debiasing techniques to the synthesis process
- Use multiple perspectives to triangulate on the most accurate estimate
- Check for anchoring effects from initial positions or market prices

**6. CALIBRATION METHODOLOGY**
- Start with the most appropriate base rate as an anchor
- Apply systematic adjustments based on the strongest evidence from both sides
- Weight adjustments by the quality and independence of supporting evidence
- Ensure final probability reflects genuine uncertainty rather than false precision

**7. META-COGNITIVE VALIDATION**
- Apply multiple forecasting methods and compare results
- Consider: "What would I predict if I had to bet my own money on this outcome?"
- Check calibration: "If I made 100 similar predictions at this confidence level, how many should be correct?"
- Perform sanity checks against expert consensus and market prices where available

**8. CONFIDENCE ASSESSMENT**
- Assess your confidence in the final probability estimate
- Identify key factors that could significantly change the assessment
- Consider the quality and completeness of available evidence
- Acknowledge limitations and areas where more information would be valuable

**SYNTHESIS PRINCIPLES:**
- Weight arguments by evidence quality, not persuasiveness or volume
- Avoid simple averaging - synthesize based on the strength of reasoning
- Be willing to strongly favor one side if evidence clearly supports it
- Don't anchor on 50% or split differences without justification
- Your probability should reflect the weight of evidence, not a compromise

**OUTPUT REQUIREMENTS:**
- Provide final probability with confidence interval (e.g., "32% [25%-40%]")
- Explicitly state your confidence level in this estimate
- Identify the 2-3 most critical factors that determined your assessment
- Note what new evidence would most significantly update your probability
- Acknowledge key limitations or uncertainties in your reasoning

Your goal is to synthesize the debate into the most accurate and well-calibrated probability estimate possible through systematic reasoning and proper uncertainty quantification."""
    }
    
    return enhanced_prompts

def apply_meta_cognitive_prompts():
    """Apply the meta-cognitive reasoning prompts to the system"""
    
    prompts_file = Path(__file__).parent / "src" / "ai_forecasts" / "agents" / "debate_forecasting_prompts.py"
    
    # Read the current file
    with open(prompts_file, 'r') as f:
        content = f.read()
    
    enhanced_prompts = create_meta_cognitive_prompts()
    
    # Create enhanced backstory functions
    enhanced_high_backstory = f'''def get_high_advocate_backstory() -> str:
    """Meta-cognitive reasoning backstory for High Probability Advocate"""
    return """{enhanced_prompts["high_advocate_system"]}"""'''

    enhanced_low_backstory = f'''def get_low_advocate_backstory() -> str:
    """Meta-cognitive reasoning backstory for Low Probability Advocate"""
    return """{enhanced_prompts["low_advocate_system"]}"""'''

    enhanced_judge_backstory = f'''def get_debate_judge_backstory() -> str:
    """Meta-cognitive reasoning backstory for Debate Judge"""
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
    
    print("✅ Meta-cognitive reasoning prompts applied successfully")
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
    results_file = Path(__file__).parent / f"meta_cognitive_optimization_iter{iteration}_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration,
        "question_ids": question_ids,
        "target_brier_score": 0.1,
        "results": results,
        "meta_cognitive_prompts": True,
        "optimization_strategy": "meta_cognitive_reasoning_framework"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")
    return results_file

def main():
    """Main meta-cognitive optimization process"""
    print("🧠 Advanced Reasoning Optimization - Meta-Cognitive Framework")
    print("=" * 70)
    print("Focus: Improving reasoning processes without hardcoding")
    print(f"Target Questions: {len(TARGET_QUESTION_IDS)} questions")
    print(f"Target Brier Score: < 0.1")
    print()
    
    # Apply meta-cognitive prompts
    print("📝 Applying meta-cognitive reasoning prompts...")
    apply_meta_cognitive_prompts()
    
    # Run benchmark with meta-cognitive prompts
    print("\n🚀 Running benchmark with meta-cognitive reasoning framework...")
    results = run_benchmark_iteration("meta_cognitive_v1", TARGET_QUESTION_IDS)
    
    if results is None:
        print("❌ Benchmark failed to complete")
        return 1
    
    # Save results
    results_file = save_iteration_results(results, TARGET_QUESTION_IDS, "meta_cognitive_v1")
    
    # Summary
    print(f"\n📋 Meta-Cognitive Optimization Results:")
    print(f"   Questions Tested: {len(TARGET_QUESTION_IDS)}")
    print(f"   Overall Brier Score: {results['brier_score']:.4f}")
    print(f"   Target Achieved: {'✅ Yes' if results['success'] else '❌ No'}")
    print(f"   Execution Time: {results['duration']:.1f} seconds")
    
    # Compare with previous best
    previous_best = 0.3238
    improvement = previous_best - results['brier_score']
    
    if improvement > 0:
        print(f"✅ Improvement: {improvement:.4f} reduction in Brier score")
        print(f"📈 Relative improvement: {(improvement/previous_best)*100:.1f}%")
    else:
        print(f"⚠️ Performance: {abs(improvement):.4f} increase in Brier score")
    
    if results['success']:
        print("\n🎉 SUCCESS! Meta-cognitive prompts achieved target Brier score < 0.1")
    else:
        print(f"\n📈 Continue optimization. Current: {results['brier_score']:.4f}, Target: < 0.1")
        print("💡 Next steps: Consider ensemble methods or additional reasoning frameworks")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())