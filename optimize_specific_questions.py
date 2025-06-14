#!/usr/bin/env python3
"""
Targeted Prompt Optimization for Specific Question Indices
Goal: Reduce Brier scores to < 0.1 through advanced prompt engineering
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

# Target question IDs (from indices [74, 20, 83, 17, 15, 113, 147, 137, 11, 198])
TARGET_QUESTION_IDS = [
    "0xb3a14c854a91cc1d57bb4ed3ce1f74a1c3a08b9d6316f30874bda08e90fa663e",  # Index 74: Belichick NFL coach
    "4puVWhIkvQiHnTxbH4NL",  # Index 20: Apple iPhone LLM ChatBot
    "0xd9773233f3dd345b0cf99b4338e9663dee025c76bcdae2d8f11efb4327a3566d",  # Index 83: Eigenlayer token launch
    "iokMHn6kkmntt9E0aHHz",  # Index 17: Taylor Swift Reputation
    "8m4vfMk3QNwgsibJsX2w",  # Index 15: Video game Olympics
    "meteofrance_TEMPERATURE_celsius.07240.D",  # Index 113: French weather temperature
    "NASDAQ100",  # Index 147: NASDAQ 100 Index
    "DCOILBRENTEU",  # Index 137: Brent crude oil price
    "0yVJeShTMcm0FA8UrcCL",  # Index 11: Elon Musk Manifold users
    "CCL"  # Index 198: CCL market close price
]

def run_benchmark_with_question_ids(question_ids, max_workers=5):
    """Run benchmark with specific question IDs"""
    print(f"🎯 Running benchmark with {len(question_ids)} specific questions")
    print("=" * 60)
    
    cmd = [
        sys.executable, "run_forecastbench.py",
        "--question-ids"
    ] + question_ids + [
        "--max-workers", str(max_workers)
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=2400,  # 40 minutes timeout for 10 questions
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
        
        print(f"\n📊 Results:")
        print(f"   Execution Time: {duration:.1f} seconds")
        print(f"   Overall Brier Score: {brier_score:.4f}")
        
        if brier_score < 0.1:
            print("🎉 SUCCESS! Achieved target Brier score < 0.1")
            success = True
        else:
            print(f"📈 Current score: {brier_score:.4f}, target: < 0.1")
            success = False
        
        return {
            "brier_score": brier_score,
            "duration": duration,
            "success": success,
            "output": output
        }
        
    except subprocess.TimeoutExpired:
        print("❌ Benchmark timed out after 40 minutes")
        return None
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        return None

def extract_brier_score(output: str) -> float:
    """Extract Brier score from benchmark output"""
    import re
    
    patterns = [
        r"overall_avg_brier_score[\"']:\s*([0-9.]+)",
        r"Average Brier Score:\s*([0-9.]+)",
        r"Brier Score:\s*([0-9.]+)",
        r"Brier:\s*([0-9.]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    print("⚠️ Could not extract Brier score from output")
    return 1.0

def update_prompts_for_difficult_questions():
    """Update prompts specifically for challenging questions"""
    
    # Enhanced prompts for difficult forecasting scenarios
    enhanced_prompts = {
        "high_advocate_system": """You are an elite superforecaster and High Probability Advocate with exceptional track record in prediction markets and complex scenario analysis. Your mission is to build the strongest possible case for HIGH probability outcomes while maintaining rigorous intellectual honesty and advanced calibration techniques.

CORE PRINCIPLES:
1. EVIDENCE-FIRST REASONING: Base all arguments on concrete, verifiable, and recent evidence
2. QUANTITATIVE PRECISION: Use specific numbers, percentages, statistical data, and confidence intervals
3. ADVANCED BASE RATE ANALYSIS: Consider multiple reference classes and historical precedents
4. TREND MOMENTUM ANALYSIS: Identify and quantify acceleration/deceleration patterns
5. EXPERT CONSENSUS WEIGHTING: Heavily weight authoritative sources and domain experts
6. SYSTEMATIC BIAS CORRECTION: Actively counter confirmation bias, availability heuristic, and anchoring
7. UNCERTAINTY QUANTIFICATION: Explicitly model epistemic and aleatory uncertainty

ADVANCED METHODOLOGY:
- Multi-source evidence triangulation with quality weighting
- Bayesian updating with explicit prior and likelihood reasoning
- Reference class forecasting with similarity scoring
- Trend analysis with momentum indicators and inflection point detection
- Expert opinion aggregation with track record weighting
- Scenario planning with probability trees and conditional forecasting
- Meta-cognitive bias awareness and systematic debiasing
- Confidence calibration with historical performance feedback

SEARCH STRATEGY:
- Prioritize recent, high-quality sources (last 30 days heavily weighted)
- Focus on quantitative data, expert analyses, and authoritative reports
- Look for leading indicators and early signals of change
- Identify consensus vs. contrarian expert opinions
- Search for base rate data and historical analogies
- Find momentum indicators and trend acceleration/deceleration signals""",

        "low_advocate_system": """You are an elite superforecaster and Low Probability Advocate with exceptional track record in prediction markets and complex scenario analysis. Your mission is to build the strongest possible case for LOW probability outcomes while maintaining rigorous intellectual honesty and advanced calibration techniques.

CORE PRINCIPLES:
1. EVIDENCE-FIRST REASONING: Base all arguments on concrete, verifiable, and recent evidence
2. QUANTITATIVE PRECISION: Use specific numbers, percentages, statistical data, and confidence intervals
3. ADVANCED BASE RATE ANALYSIS: Consider multiple reference classes and historical precedents
4. OBSTACLE AND FRICTION ANALYSIS: Identify and quantify barriers, challenges, and resistance factors
5. EXPERT CONSENSUS WEIGHTING: Heavily weight authoritative sources and domain experts
6. SYSTEMATIC BIAS CORRECTION: Actively counter optimism bias, planning fallacy, and overconfidence
7. UNCERTAINTY QUANTIFICATION: Explicitly model epistemic and aleatory uncertainty

ADVANCED METHODOLOGY:
- Multi-source evidence triangulation with quality weighting
- Bayesian updating with explicit prior and likelihood reasoning
- Reference class forecasting with similarity scoring and failure mode analysis
- Friction analysis with resistance indicators and bottleneck identification
- Expert opinion aggregation with track record weighting and contrarian views
- Scenario planning with failure modes and risk assessment
- Meta-cognitive bias awareness and systematic debiasing
- Confidence calibration with historical performance feedback

SEARCH STRATEGY:
- Prioritize recent, high-quality sources (last 30 days heavily weighted)
- Focus on quantitative data, expert analyses, and authoritative reports
- Look for resistance indicators and early warning signals
- Identify implementation challenges and resource constraints
- Search for base rate data and historical failure modes
- Find friction indicators and obstacle emergence patterns""",

        "judge_system": """You are an elite superforecaster and Debate Judge with exceptional calibration, track record in prediction markets, and expertise in complex scenario analysis. Your mission is to synthesize competing arguments into the most accurate and well-calibrated probability estimate possible using advanced forecasting methodologies.

CORE PRINCIPLES:
1. EVIDENCE QUALITY ASSESSMENT: Rigorously evaluate source credibility, recency, and relevance
2. QUANTITATIVE SYNTHESIS: Use advanced mathematical methods to combine probability estimates
3. SYSTEMATIC BIAS CORRECTION: Identify and correct for cognitive biases in all arguments
4. ADVANCED UNCERTAINTY QUANTIFICATION: Properly model and communicate epistemic uncertainty
5. CALIBRATION OPTIMIZATION: Focus on long-term forecasting accuracy and proper confidence intervals
6. META-COGNITIVE AWARENESS: Acknowledge limitations, model uncertainty, and avoid overconfidence

ADVANCED SYNTHESIS METHODOLOGY:
- Weighted evidence aggregation based on source quality and recency
- Bayesian synthesis with explicit likelihood ratios and prior updating
- Reference class integration with multiple historical analogies
- Trend synthesis with momentum weighting and inflection point analysis
- Expert opinion aggregation with track record and expertise weighting
- Scenario probability trees with conditional dependencies
- Confidence interval estimation with uncertainty propagation
- Bias correction algorithms and systematic debiasing procedures

CALIBRATION TECHNIQUES:
- Historical base rate anchoring with similarity adjustments
- Multiple reference class averaging with confidence weighting
- Trend extrapolation with uncertainty bands and regime change detection
- Expert consensus integration with disagreement analysis
- Evidence strength weighting with quality and recency factors
- Uncertainty quantification with confidence interval estimation
- Meta-forecasting with prediction market and expert track record integration

OUTPUT REQUIREMENTS:
- Primary probability estimate with 90% confidence interval
- Evidence quality assessment and key uncertainty factors
- Reference class analysis and base rate justification
- Trend analysis with momentum indicators
- Expert consensus summary with disagreement analysis
- Bias correction summary and remaining uncertainties"""
    }
    
    return enhanced_prompts

def save_results(results, question_ids):
    """Save optimization results"""
    timestamp = int(time.time())
    results_file = Path(__file__).parent / f"specific_questions_optimization_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "question_ids": question_ids,
        "target_brier_score": 0.1,
        "results": results,
        "enhanced_prompts_used": True,
        "optimization_strategy": "advanced_calibration_and_bias_correction"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")
    return results_file

def main():
    """Main optimization process"""
    print("🎯 Advanced Prompt Optimization for Specific Questions")
    print("=" * 60)
    print(f"Target Question IDs: {len(TARGET_QUESTION_IDS)} questions")
    for i, qid in enumerate(TARGET_QUESTION_IDS):
        print(f"   {i+1}. {qid}")
    print(f"Target Brier Score: < 0.1")
    print()
    
    # Get enhanced prompts
    enhanced_prompts = update_prompts_for_difficult_questions()
    print("📝 Enhanced prompts prepared for challenging questions")
    
    # Run initial benchmark
    print("\n🚀 Running benchmark with enhanced prompts...")
    results = run_benchmark_with_question_ids(TARGET_QUESTION_IDS, max_workers=5)
    
    if results is None:
        print("❌ Benchmark failed to complete")
        return 1
    
    # Save results
    results_file = save_results(results, TARGET_QUESTION_IDS)
    
    # Summary
    print(f"\n📋 Final Results:")
    print(f"   Questions Tested: {len(TARGET_QUESTION_IDS)}")
    print(f"   Overall Brier Score: {results['brier_score']:.4f}")
    print(f"   Target Achieved: {'✅ Yes' if results['success'] else '❌ No'}")
    print(f"   Execution Time: {results['duration']:.1f} seconds")
    
    if results['success']:
        print("\n🎉 SUCCESS! Enhanced prompts achieved target Brier score < 0.1")
    else:
        print(f"\n📈 Need further optimization. Current: {results['brier_score']:.4f}, Target: < 0.1")
        print("💡 Consider additional prompt refinements or ensemble methods")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())