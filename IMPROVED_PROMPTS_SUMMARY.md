# 🎯 Improved Agent Prompts for Granular Forecasting

## ✅ PROMPT ENHANCEMENTS COMPLETED

We have successfully enhanced the CrewAI agent prompts to provide more granular and accurate forecasts using superforecaster methodology.

### 🔧 **KEY IMPROVEMENTS MADE**

#### 1. **Enhanced Synthesis Agent (Final Probability Estimation)**

**BEFORE:** Vague instructions for probability estimation
**AFTER:** Precise 6-step superforecaster methodology:

```
**STEP 1: BASE RATE ANALYSIS (Outside View)**
- Extract the base rate from historical analysis (e.g., "55% of champions defend titles")
- Identify the reference class size and quality
- Start with this base rate as your initial estimate

**STEP 2: SPECIFIC FACTOR ADJUSTMENTS (Inside View)**
- List 3-5 specific factors from current news that could move probability up or down
- For each factor, estimate its impact: Strong (+/-15%), Moderate (+/-8%), Weak (+/-3%)
- Apply adjustments incrementally to base rate

**STEP 3: EVIDENCE QUALITY WEIGHTING**
- High quality evidence (credible sources, recent, relevant): Weight 100%
- Medium quality evidence: Weight 60%
- Low quality evidence: Weight 30%

**STEP 4: EXPERT CONSENSUS INTEGRATION**
- If experts agree: Move 5-10% toward consensus
- If experts disagree: Stay closer to base rate

**STEP 5: CONTRARIAN ADJUSTMENT**
- If strong contrarian evidence: Adjust 3-8% toward uncertainty
- If weak contrarian evidence: Minimal adjustment (1-2%)

**STEP 6: FINAL CALIBRATION**
- Avoid overconfidence: Don't go below 5% or above 95% unless overwhelming evidence
- Round to nearest 1% (e.g., 0.23, 0.67, 0.84)
```

#### 2. **Enhanced Historical Analysis Agent**

**BEFORE:** General base rate analysis
**AFTER:** Specific numerical base rate extraction:

```
**CRITICAL: You must identify specific numerical base rates from the news research**

**STEP 1: REFERENCE CLASS IDENTIFICATION**
- Find the most relevant reference class from news coverage
- Look for historical statistics, success rates, or precedent data

**STEP 2: BASE RATE EXTRACTION**
- Extract specific percentages or ratios from news sources
- If exact numbers aren't available, estimate based on described patterns

**OUTPUT FORMAT (EXACT JSON):**
{
    "primary_base_rate": 0.XX,
    "base_rate_source": "specific news article or study cited",
    "reference_class": "exact description of what the base rate represents",
    "sample_size": "number of cases or time period"
}
```

#### 3. **Enhanced Current Context Analysis Agent**

**BEFORE:** General current conditions analysis
**AFTER:** Specific factor impact assessment:

```
**CRITICAL: Identify specific factors that should adjust the base rate up or down**

**STEP 1: FACTOR IDENTIFICATION**
- List 3-5 specific current factors from news that could influence the outcome

**STEP 2: FACTOR IMPACT ASSESSMENT**
- For each factor, assess its impact strength:
  * Strong impact: Could change probability by 10-20%
  * Moderate impact: Could change probability by 5-10%
  * Weak impact: Could change probability by 1-5%

**OUTPUT FORMAT:**
{
    "positive_factors": [
        {
            "factor": "specific factor name",
            "impact_strength": "strong/moderate/weak",
            "estimated_impact": "+X%",
            "evidence_quality": "high/medium/low"
        }
    ],
    "negative_factors": [...]
}
```

### 📊 **METHODOLOGY IMPROVEMENTS**

#### **Superforecaster Process Integration**
- **Base Rate First:** Always start with outside view (historical precedents)
- **Incremental Adjustments:** Apply specific factor adjustments step-by-step
- **Evidence Weighting:** Quality-weighted evidence integration
- **Calibration:** Avoid overconfidence, precise probability estimates
- **Transparency:** Show mathematical calculations

#### **Precise Probability Estimation**
- **Range:** 0.01 to 0.99 (avoid extreme confidence)
- **Granularity:** Nearest 1% (e.g., 0.23, 0.67, 0.84)
- **Calculation:** Base rate ± adjustments = final probability
- **Example:** 55% - 12% - 8% + 3% - 3% = 35% → 0.35

#### **Structured Output Format**
```json
{
    "probability": 0.XX,
    "base_rate": 0.XX,
    "base_rate_source": "specific historical data from news",
    "adjustments": [
        {"factor": "specific factor 1", "impact": "+/-X%", "reasoning": "evidence from news"},
        {"factor": "specific factor 2", "impact": "+/-X%", "reasoning": "evidence from news"}
    ],
    "evidence_quality": "high/medium/low",
    "expert_consensus": "agree/disagree/mixed",
    "contrarian_strength": "strong/moderate/weak",
    "confidence_level": "high/medium/low",
    "reasoning": "step-by-step calculation showing base rate + adjustments = final probability"
}
```

### 🎯 **EXPECTED IMPROVEMENTS**

#### **More Accurate Predictions**
- **Granular Analysis:** Specific factor identification and quantification
- **Evidence-Based:** Grounded in historical data and current evidence
- **Calibrated:** Appropriate uncertainty representation

#### **Better Brier Scores**
- **Precise Probabilities:** Avoid round numbers like 0.50
- **Incremental Reasoning:** Step-by-step adjustments from base rates
- **Quality Weighting:** Higher weight for better evidence

#### **Transparent Reasoning**
- **Show Work:** Mathematical calculations visible
- **Factor Analysis:** Specific positive/negative factors identified
- **Source Attribution:** Evidence traced to specific news sources

### 🏆 **VALIDATION RESULTS**

#### **Previous System Performance**
- **Brier Score:** 0.0723 (Good accuracy)
- **Methodology:** Basic probability estimation
- **Reasoning:** General analysis without specific calculations

#### **Enhanced System Capabilities**
- **Structured Methodology:** 6-step superforecaster process
- **Quantified Factors:** Specific impact percentages for each factor
- **Mathematical Transparency:** Base rate + adjustments = final probability
- **Evidence Quality:** Weighted by source credibility and relevance

### 🚀 **SYSTEM READY FOR TESTING**

The improved prompts are now integrated into the CrewAI system and ready for comprehensive testing:

1. **Enhanced Agent Prompts:** ✅ Implemented
2. **Superforecaster Methodology:** ✅ Integrated
3. **Structured Output Format:** ✅ Defined
4. **Mathematical Calculations:** ✅ Required
5. **Evidence Weighting:** ✅ Specified

### 📈 **NEXT STEPS**

1. **Run 10-Question Benchmark:** Test improved system with random sample
2. **Compare Brier Scores:** Measure improvement vs previous system
3. **Analyze Reasoning Quality:** Evaluate transparency and granularity
4. **Validate Methodology:** Confirm superforecaster process adherence

**The enhanced CrewAI system is now equipped with professional-grade superforecaster methodology for more accurate and granular probability predictions!** 🎯