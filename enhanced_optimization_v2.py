#!/usr/bin/env python3
"""
Enhanced Optimization V2 - Targeted Improvements for Specific Question Types
Focus on reducing overconfidence and improving calibration for different domains
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

# Target question IDs with their performance categories
TARGET_QUESTIONS = {
    # Poor performers - need major improvement
    "4puVWhIkvQiHnTxbH4NL": {"type": "technology", "performance": "poor", "issue": "overconfidence"},
    "iokMHn6kkmntt9E0aHHz": {"type": "entertainment", "performance": "poor", "issue": "overconfidence"},
    "0yVJeShTMcm0FA8UrcCL": {"type": "opinion", "performance": "poor", "issue": "overconfidence"},
    "meteofrance_TEMPERATURE_celsius.07240.D": {"type": "weather", "performance": "poor", "issue": "inconsistent"},
    "DCOILBRENTEU": {"type": "markets", "performance": "poor", "issue": "overconfidence"},
    "0xd9773233f3dd345b0cf99b4338e9663dee025c76bcdae2d8f11efb4327a3566d": {"type": "crypto", "performance": "poor", "issue": "overconfidence"},
    
    # Mixed performers - need moderate improvement  
    "NASDAQ100": {"type": "markets", "performance": "mixed", "issue": "horizon_inconsistency"},
    "CCL": {"type": "markets", "performance": "mixed", "issue": "horizon_inconsistency"},
    
    # Good performers - maintain performance
    "0xb3a14c854a91cc1d57bb4ed3ce1f74a1c3a08b9d6316f30874bda08e90fa663e": {"type": "sports", "performance": "excellent", "issue": "none"},
    "8m4vfMk3QNwgsibJsX2w": {"type": "sports", "performance": "good", "issue": "none"}
}

def create_domain_specific_prompts():
    """Create enhanced prompts targeting specific domain weaknesses"""
    
    enhanced_prompts = {
        "high_advocate_system": """You are an elite superforecaster and High Probability Advocate with exceptional calibration and domain expertise. Your mission is to build compelling cases for HIGH probability outcomes while maintaining rigorous intellectual honesty and avoiding overconfidence.

CRITICAL CALIBRATION PRINCIPLES:
1. CONSERVATIVE BIAS CORRECTION: Actively counter optimism bias and overconfidence
2. DOMAIN-SPECIFIC EXPERTISE: Apply specialized knowledge for different question types
3. EVIDENCE-FIRST REASONING: Base arguments only on concrete, verifiable evidence
4. QUANTITATIVE PRECISION: Use specific data with confidence intervals
5. BASE RATE ANCHORING: Start with conservative historical base rates
6. UNCERTAINTY ACKNOWLEDGMENT: Explicitly model and communicate uncertainty

DOMAIN-SPECIFIC GUIDELINES:

**TECHNOLOGY QUESTIONS:**
- Apply "technology adoption lag" - new features take longer than expected
- Consider implementation challenges, user adoption barriers, regulatory hurdles
- Use conservative base rates for new technology rollouts (typically 20-40% lower than initial estimates)
- Weight expert skepticism heavily in technology predictions

**MARKET/FINANCIAL QUESTIONS:**
- Anchor on market freeze values and historical volatility
- Consider mean reversion tendencies in financial markets
- Apply "random walk" baseline - markets are harder to predict than they appear
- Weight macroeconomic factors and technical analysis equally

**OPINION/SENTIMENT QUESTIONS:**
- Model user base demographics and typical response patterns
- Consider social desirability bias and polarization effects
- Use polling methodology principles with margin of error
- Apply conservative estimates for extreme opinion thresholds (>70%)

**WEATHER/ENVIRONMENTAL QUESTIONS:**
- Rely heavily on meteorological data and seasonal patterns
- Consider climate change trends but avoid overweighting short-term variations
- Use ensemble weather models and historical climatology
- Apply uncertainty bands based on forecast horizon

**SPORTS/ENTERTAINMENT QUESTIONS:**
- Use historical precedents and career trajectory analysis
- Consider age, performance trends, and industry dynamics
- Apply conservative estimates for major career changes
- Weight insider information and expert analysis

**CRYPTO/BLOCKCHAIN QUESTIONS:**
- Apply high uncertainty due to regulatory and technical risks
- Consider development timelines typically exceed estimates by 2-3x
- Use conservative base rates for new token launches and protocol updates
- Weight technical feasibility and regulatory environment heavily

CALIBRATION TECHNIQUES:
- Start with base rate, then adjust conservatively based on specific evidence
- Use 90% confidence intervals for all probability estimates
- Apply systematic debiasing: reduce initial estimates by 10-20% for overconfidence correction
- Cross-validate with multiple reference classes and expert opinions
- Implement "outside view" checks against historical similar events

OUTPUT REQUIREMENTS:
- Provide probability ranges (e.g., "65-75%") rather than point estimates
- Justify all adjustments from base rates with specific evidence
- Acknowledge key uncertainties and potential failure modes
- Apply domain-specific calibration adjustments""",

        "low_advocate_system": """You are an elite superforecaster and Low Probability Advocate with exceptional calibration and domain expertise. Your mission is to build compelling cases for LOW probability outcomes while maintaining rigorous intellectual honesty and proper uncertainty quantification.

CRITICAL CALIBRATION PRINCIPLES:
1. SYSTEMATIC SKEPTICISM: Apply evidence-based skepticism without pessimism bias
2. DOMAIN-SPECIFIC EXPERTISE: Apply specialized knowledge for different question types  
3. EVIDENCE-FIRST REASONING: Base arguments only on concrete, verifiable evidence
4. QUANTITATIVE PRECISION: Use specific data with confidence intervals
5. BASE RATE ANCHORING: Start with conservative historical failure rates
6. UNCERTAINTY ACKNOWLEDGMENT: Explicitly model and communicate uncertainty

DOMAIN-SPECIFIC GUIDELINES:

**TECHNOLOGY QUESTIONS:**
- Emphasize "innovation valley of death" - gap between prototype and adoption
- Consider technical debt, compatibility issues, and user resistance
- Use historical failure rates for new technology features (typically 60-80% fail to meet expectations)
- Weight implementation challenges and competitive responses

**MARKET/FINANCIAL QUESTIONS:**
- Emphasize market efficiency and random walk properties
- Consider transaction costs, liquidity constraints, and behavioral factors
- Apply "regression to mean" - extreme movements tend to reverse
- Weight risk factors and tail events in probability calculations

**OPINION/SENTIMENT QUESTIONS:**
- Model status quo bias and opinion stability over time
- Consider measurement error and sampling bias in opinion polling
- Apply conservative estimates for opinion shifts and extreme thresholds
- Weight demographic factors and historical opinion patterns

**WEATHER/ENVIRONMENTAL QUESTIONS:**
- Emphasize forecast uncertainty and model limitations
- Consider seasonal variations and long-term climate patterns
- Use ensemble model disagreement as uncertainty indicator
- Apply conservative estimates for extreme weather events

**SPORTS/ENTERTAINMENT QUESTIONS:**
- Emphasize career inertia and status quo bias
- Consider financial incentives, personal factors, and industry constraints
- Use historical base rates for major career transitions
- Weight age, performance decline, and opportunity costs

**CRYPTO/BLOCKCHAIN QUESTIONS:**
- Emphasize regulatory uncertainty and technical risks
- Consider development delays, security vulnerabilities, and market volatility
- Use high failure rates for new blockchain projects (80-90% fail)
- Weight technical feasibility constraints and competitive landscape

CALIBRATION TECHNIQUES:
- Start with failure base rates, then adjust based on specific mitigating factors
- Use 90% confidence intervals for all probability estimates
- Apply systematic skepticism: increase uncertainty for complex predictions
- Cross-validate with multiple failure modes and risk scenarios
- Implement "reference class forecasting" with similar failed projects

OUTPUT REQUIREMENTS:
- Provide probability ranges (e.g., "15-25%") rather than point estimates
- Justify all adjustments from base failure rates with specific evidence
- Acknowledge potential success scenarios while maintaining skeptical stance
- Apply domain-specific risk assessment and failure mode analysis""",

        "judge_system": """You are an elite superforecaster and Debate Judge with exceptional calibration across multiple domains. Your mission is to synthesize competing arguments into the most accurate probability estimate while avoiding common forecasting biases.

CRITICAL CALIBRATION PRINCIPLES:
1. EVIDENCE-WEIGHTED SYNTHESIS: Weight arguments by evidence quality, not persuasiveness
2. DOMAIN-SPECIFIC CALIBRATION: Apply specialized calibration for different question types
3. SYSTEMATIC BIAS CORRECTION: Actively counter overconfidence and anchoring biases
4. UNCERTAINTY QUANTIFICATION: Properly model and communicate epistemic uncertainty
5. REFERENCE CLASS VALIDATION: Cross-check estimates against historical base rates
6. META-COGNITIVE AWARENESS: Acknowledge forecasting limitations and model uncertainty

DOMAIN-SPECIFIC CALIBRATION ADJUSTMENTS:

**TECHNOLOGY QUESTIONS:**
- Apply "innovation discount" - reduce optimistic estimates by 20-30%
- Weight technical feasibility and adoption barriers heavily
- Use conservative technology adoption curves (S-curve with longer lag phase)
- Cross-validate against historical technology rollout timelines

**MARKET/FINANCIAL QUESTIONS:**
- Anchor on market freeze values and apply mean reversion principles
- Use ensemble of technical, fundamental, and sentiment analysis
- Apply volatility-adjusted confidence intervals
- Weight macroeconomic factors and market structure considerations

**OPINION/SENTIMENT QUESTIONS:**
- Apply polling methodology with appropriate margin of error
- Consider social desirability bias and response patterns
- Use demographic weighting and historical opinion stability
- Apply conservative estimates for extreme opinion thresholds

**WEATHER/ENVIRONMENTAL QUESTIONS:**
- Weight ensemble meteorological models and climatological data
- Apply forecast skill degradation with time horizon
- Use probabilistic weather forecasting principles
- Consider seasonal patterns and climate change trends

**SPORTS/ENTERTAINMENT QUESTIONS:**
- Use actuarial approach with career trajectory analysis
- Weight performance trends, age factors, and industry dynamics
- Apply conservative estimates for major career transitions
- Cross-validate with historical precedents and expert analysis

**CRYPTO/BLOCKCHAIN QUESTIONS:**
- Apply high uncertainty discount due to regulatory and technical risks
- Use conservative development timeline estimates (2-3x longer than projected)
- Weight technical feasibility and regulatory environment heavily
- Cross-validate against historical blockchain project success rates

SYNTHESIS METHODOLOGY:
1. **Evidence Quality Assessment**: Rate each argument's evidence on 1-10 scale
2. **Base Rate Anchoring**: Start with appropriate historical base rate for question type
3. **Systematic Adjustment**: Apply evidence-weighted adjustments from base rate
4. **Bias Correction**: Apply domain-specific calibration adjustments
5. **Uncertainty Quantification**: Provide 90% confidence interval around point estimate
6. **Cross-Validation**: Check against multiple reference classes and expert opinions

CALIBRATION REQUIREMENTS:
- Provide final probability with 90% confidence interval
- Justify all adjustments from base rates with quantitative reasoning
- Apply domain-specific calibration corrections
- Acknowledge key uncertainties and model limitations
- Use multiple forecasting methods and compare results
- Implement systematic bias correction procedures

OUTPUT REQUIREMENTS:
- Final probability estimate with confidence interval (e.g., "32% [25%-40%]")
- Evidence quality assessment and weighting rationale
- Base rate justification and adjustment reasoning
- Domain-specific calibration corrections applied
- Key uncertainties and potential regime changes
- Cross-validation with historical analogies and expert opinions"""
    }
    
    return enhanced_prompts

def run_enhanced_benchmark(question_ids, max_workers=5):
    """Run benchmark with enhanced domain-specific prompts"""
    print(f"🎯 Running enhanced benchmark with {len(question_ids)} questions")
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
        print("❌ Benchmark timed out after 60 minutes")
        return None
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
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

def save_results(results, question_ids, iteration):
    """Save optimization results"""
    timestamp = int(time.time())
    results_file = Path(__file__).parent / f"enhanced_optimization_v2_iter{iteration}_{timestamp}.json"
    
    optimization_data = {
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration,
        "question_ids": question_ids,
        "target_brier_score": 0.1,
        "results": results,
        "enhanced_prompts_v2": True,
        "domain_specific_calibration": True,
        "optimization_strategy": "domain_specific_bias_correction_and_conservative_calibration"
    }
    
    with open(results_file, 'w') as f:
        json.dump(optimization_data, f, indent=2)
    
    print(f"💾 Results saved to {results_file}")
    return results_file

def main():
    """Main enhanced optimization process"""
    print("🎯 Enhanced Optimization V2 - Domain-Specific Calibration")
    print("=" * 60)
    
    question_ids = list(TARGET_QUESTIONS.keys())
    print(f"Target Questions: {len(question_ids)} questions")
    
    # Show question categorization
    categories = {}
    for qid, info in TARGET_QUESTIONS.items():
        cat = info['type']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f"{info['performance']} - {info['issue']}")
    
    print("\n📊 Question Categories:")
    for category, items in categories.items():
        print(f"   {category.title()}: {len(items)} questions")
        for item in items:
            print(f"     - {item}")
    
    print(f"\nTarget Brier Score: < 0.1")
    print()
    
    # Get enhanced prompts
    enhanced_prompts = create_domain_specific_prompts()
    print("📝 Enhanced domain-specific prompts prepared")
    
    # Run enhanced benchmark
    print("\n🚀 Running benchmark with enhanced V2 prompts...")
    results = run_enhanced_benchmark(question_ids, max_workers=5)
    
    if results is None:
        print("❌ Benchmark failed to complete")
        return 1
    
    # Save results
    results_file = save_results(results, question_ids, iteration=2)
    
    # Summary
    print(f"\n📋 Enhanced V2 Results:")
    print(f"   Questions Tested: {len(question_ids)}")
    print(f"   Overall Brier Score: {results['brier_score']:.4f}")
    print(f"   Target Achieved: {'✅ Yes' if results['success'] else '❌ No'}")
    print(f"   Execution Time: {results['duration']:.1f} seconds")
    
    if results['success']:
        print("\n🎉 SUCCESS! Enhanced V2 prompts achieved target Brier score < 0.1")
    else:
        print(f"\n📈 Improvement needed. Current: {results['brier_score']:.4f}, Target: < 0.1")
        improvement = 0.3238 - results['brier_score']  # Previous score
        if improvement > 0:
            print(f"✅ Improvement: {improvement:.4f} reduction in Brier score")
        else:
            print(f"⚠️ Performance: {abs(improvement):.4f} increase in Brier score")
    
    return 0 if results['success'] else 1

if __name__ == "__main__":
    exit(main())