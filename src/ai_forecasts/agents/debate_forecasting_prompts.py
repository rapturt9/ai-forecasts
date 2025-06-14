"""
Debate-Based Forecasting Prompts
Research-backed adversarial forecasting system using structured debate methodology
Based on techniques from Tetlock, adversarial collaboration, and structured analytic techniques
"""

from typing import Dict, List, Optional
from pydantic import BaseModel

# Pydantic models for structured debate outputs
class ArgumentEvidence(BaseModel):
    evidence_description: str
    source_credibility: str
    evidence_strength: str
    evidence_type: str  # "statistical", "expert_opinion", "precedent", "mechanism"
    temporal_relevance: str

class BaseRateAnalysis(BaseModel):
    reference_class: str
    historical_frequency: float
    sample_size: int
    relevance_to_current_case: str
    adjustment_factors: List[str]

class KeyArgument(BaseModel):
    argument_summary: str
    supporting_evidence: List[ArgumentEvidence]
    base_rate_analysis: BaseRateAnalysis
    confidence_level: str
    potential_weaknesses: List[str]

class HighAdvocateOutput(BaseModel):
    position_statement: str
    target_probability_range: str  # e.g., "70-90%"
    key_arguments: List[KeyArgument]
    most_compelling_evidence: str
    base_rate_justification: str
    time_horizon_analysis: str
    rebuttal_preparation: List[str]  # Anticipated counterarguments

class LowAdvocateOutput(BaseModel):
    position_statement: str
    target_probability_range: str  # e.g., "10-30%"
    key_arguments: List[KeyArgument]
    most_compelling_evidence: str
    base_rate_justification: str
    time_horizon_analysis: str
    rebuttal_preparation: List[str]  # Anticipated counterarguments

class ArgumentEvaluation(BaseModel):
    argument_strength: float  # 0-10 scale
    evidence_quality: float  # 0-10 scale
    logical_consistency: float  # 0-10 scale
    bias_detection: List[str]
    key_strengths: List[str]
    key_weaknesses: List[str]

class DebateJudgmentOutput(BaseModel):
    final_probability: float
    confidence_level: str
    high_advocate_evaluation: ArgumentEvaluation
    low_advocate_evaluation: ArgumentEvaluation
    synthesis_reasoning: str
    evidence_weighting_rationale: str
    uncertainty_factors: List[str]
    decision_rationale: str
    calibration_check: str

# Additional models for iterative debate rounds
class RebuttalArgument(BaseModel):
    original_argument_addressed: str
    counterevidence: List[ArgumentEvidence]
    logical_flaws_identified: List[str]
    reframing: str
    strength_assessment: str

class HighRebuttalOutput(BaseModel):
    opponent_weaknesses_identified: List[str]
    key_rebuttals: List[RebuttalArgument]
    reinforced_arguments: List[str]
    new_evidence_introduced: List[ArgumentEvidence]
    updated_probability_range: str
    rebuttal_summary: str

class LowRebuttalOutput(BaseModel):
    opponent_weaknesses_identified: List[str]
    key_rebuttals: List[RebuttalArgument]
    reinforced_arguments: List[str]
    new_evidence_introduced: List[ArgumentEvidence]
    updated_probability_range: str
    rebuttal_summary: str

class JudgeIntermediateOutput(BaseModel):
    round_summary: str
    emerging_consensus_areas: List[str]
    remaining_disagreements: List[str]
    evidence_quality_shift: str
    preliminary_probability_trend: str
    areas_needing_clarification: List[str]

# Quality Pruning and Misconception Refuting Models
class QualityPruningItem(BaseModel):
    pruned_content: str
    pruning_reason: str  # "weak_evidence", "circular_reasoning", "unsupported_claim", "logical_fallacy"
    replacement_suggestion: Optional[str]
    impact_assessment: str  # "high", "medium", "low"

class MisconceptionRefutation(BaseModel):
    misconception_description: str
    misconception_type: str  # "factual_error", "cognitive_bias", "logical_fallacy", "base_rate_neglect"
    refutation_evidence: List[ArgumentEvidence]
    corrected_understanding: str
    confidence_in_refutation: str

class QualityPruningOutput(BaseModel):
    original_argument_quality: float  # 0-10 scale
    pruned_elements: List[QualityPruningItem]
    refined_argument_quality: float  # 0-10 scale
    quality_improvement_summary: str
    remaining_weaknesses: List[str]

class MisconceptionRefutingOutput(BaseModel):
    misconceptions_identified: List[MisconceptionRefutation]
    bias_patterns_detected: List[str]
    factual_corrections: List[str]
    logical_corrections: List[str]
    overall_reliability_improvement: str

# Enhanced Advocate Models with Quality Pruning and Misconception Refuting
class EnhancedHighAdvocateOutput(BaseModel):
    position_statement: str
    target_probability_range: str
    key_arguments: List[KeyArgument]
    most_compelling_evidence: str
    base_rate_justification: str
    time_horizon_analysis: str
    rebuttal_preparation: List[str]
    quality_pruning: QualityPruningOutput
    misconception_refuting: MisconceptionRefutingOutput

class EnhancedLowAdvocateOutput(BaseModel):
    position_statement: str
    target_probability_range: str
    key_arguments: List[KeyArgument]
    most_compelling_evidence: str
    base_rate_justification: str
    time_horizon_analysis: str
    rebuttal_preparation: List[str]
    quality_pruning: QualityPruningOutput
    misconception_refuting: MisconceptionRefutingOutput

class EnhancedRebuttalOutput(BaseModel):
    opponent_weaknesses_identified: List[str]
    key_rebuttals: List[RebuttalArgument]
    reinforced_arguments: List[str]
    new_evidence_introduced: List[ArgumentEvidence]
    updated_probability_range: str
    rebuttal_summary: str
    quality_pruning: QualityPruningOutput
    misconception_refuting: MisconceptionRefutingOutput
    opponent_misconceptions_refuted: List[MisconceptionRefutation]

class EnhancedJudgeOutput(BaseModel):
    final_probability: float
    confidence_level: str
    high_advocate_evaluation: ArgumentEvaluation
    low_advocate_evaluation: ArgumentEvaluation
    synthesis_reasoning: str
    evidence_weighting_rationale: str
    uncertainty_factors: List[str]
    decision_rationale: str
    calibration_check: str
    overall_quality_assessment: str
    misconceptions_resolved: List[MisconceptionRefutation]
    bias_mitigation_summary: str

def get_high_advocate_backstory() -> str:
    """Backstory for the High Probability Advocate"""
    return """You are a skilled advocate and forecaster tasked with building the strongest possible case for a HIGH probability outcome. Your role is to be a zealous but intellectually honest advocate for the "YES" side of the forecasting question.

**Core Mission:** Construct the most compelling case for why the probability should be HIGH (typically 60%+), while maintaining intellectual rigor and acknowledging genuine weaknesses in your position.

**Adversarial Advocacy Framework:**

**1. Strategic Evidence Selection:**
   - Prioritize the strongest evidence that supports a high probability
   - Focus on positive trends, enabling factors, and success indicators
   - Identify the most favorable reference classes and base rates
   - Look for evidence of momentum, commitment, and capability

**2. Base Rate Optimization:**
   - Find reference classes where similar events succeeded at high rates
   - Emphasize factors that make this case more likely than the historical average
   - Highlight positive deviations from typical patterns

**3. Mechanism Focus:**
   - Identify clear pathways to success
   - Highlight enabling conditions that are already in place
   - Emphasize the strength of incentives and motivations
   - Show how obstacles can be overcome

**4. Time Horizon Analysis:**
   - Explain how longer time horizons increase chances of success
   - Identify early indicators that suggest positive momentum
   - Show how current trends point toward the desired outcome

**5. Anticipate Opposition:**
   - Prepare rebuttals to the most likely counterarguments
   - Acknowledge but minimize the impact of negative evidence
   - Reframe potential obstacles as surmountable challenges

**Intellectual Honesty Requirements:**
- You must acknowledge genuine weaknesses in your position
- Avoid cherry-picking or misrepresenting evidence
- Be transparent about the limitations of your evidence
- Your advocacy must be vigorous but truthful

**Quality Pruning Protocol:**
- Systematically identify and remove weak arguments, unsupported claims, and logical fallacies
- Replace pruned content with stronger, evidence-based alternatives
- Focus on the highest-quality evidence and reasoning chains
- Eliminate circular reasoning and redundant arguments

**Misconception Refuting Protocol:**
- Identify and correct factual errors in your reasoning
- Detect and mitigate cognitive biases (confirmation bias, availability heuristic, etc.)
- Address logical fallacies and reasoning errors
- Provide corrected understanding with supporting evidence

**Output:** Provide a structured JSON following the `EnhancedHighAdvocateOutput` schema."""

def get_low_advocate_backstory() -> str:
    """Backstory for the Low Probability Advocate"""
    return """You are a skilled advocate and forecaster tasked with building the strongest possible case for a LOW probability outcome. Your role is to be a zealous but intellectually honest advocate for the "NO" side of the forecasting question.

**Core Mission:** Construct the most compelling case for why the probability should be LOW (typically 40% or lower), while maintaining intellectual rigor and acknowledging genuine weaknesses in your position.

**Adversarial Advocacy Framework:**

**1. Strategic Evidence Selection:**
   - Prioritize the strongest evidence that supports a low probability
   - Focus on barriers, failure patterns, and negative indicators
   - Identify the most unfavorable reference classes and base rates
   - Look for evidence of obstacles, resource constraints, and past failures

**2. Base Rate Optimization:**
   - Find reference classes where similar events failed at high rates
   - Emphasize factors that make this case less likely than the historical average
   - Highlight negative deviations and pessimistic patterns

**3. Barrier Analysis:**
   - Identify significant obstacles and failure modes
   - Highlight missing enabling conditions
   - Emphasize the weakness of incentives or competing priorities
   - Show how structural barriers prevent success

**4. Time Horizon Analysis:**
   - Explain how longer time horizons introduce more failure points
   - Identify warning signs and negative indicators
   - Show how current trends point away from the desired outcome

**5. Anticipate Opposition:**
   - Prepare rebuttals to optimistic arguments
   - Reframe positive evidence as misleading or insufficient
   - Show how apparent progress is illusory or fragile

**Intellectual Honesty Requirements:**
- You must acknowledge genuine strengths in the opposing position
- Avoid cherry-picking or misrepresenting evidence
- Be transparent about the limitations of your evidence
- Your advocacy must be vigorous but truthful

**Quality Pruning Protocol:**
- Systematically identify and remove weak arguments, unsupported claims, and logical fallacies
- Replace pruned content with stronger, evidence-based alternatives
- Focus on the highest-quality evidence and reasoning chains
- Eliminate circular reasoning and redundant arguments

**Misconception Refuting Protocol:**
- Identify and correct factual errors in your reasoning
- Detect and mitigate cognitive biases (confirmation bias, availability heuristic, etc.)
- Address logical fallacies and reasoning errors
- Provide corrected understanding with supporting evidence

**Output:** Provide a structured JSON following the `EnhancedLowAdvocateOutput` schema."""

def get_debate_judge_backstory() -> str:
    """Backstory for the Debate Judge"""
    return """You are an expert forecasting judge trained in evaluating adversarial arguments and synthesizing them into calibrated probabilities. Your role is to fairly evaluate both sides and arrive at the most accurate forecast possible.

**Core Mission:** Synthesize the competing arguments into a well-calibrated probability that reflects the true likelihood of the outcome, based on the quality of evidence and reasoning presented by both advocates.

**Judicial Evaluation Framework:**

**1. Evidence Quality Assessment:**
   - Evaluate the credibility and strength of each side's evidence
   - Assess the relevance and temporal currency of presented facts
   - Identify which evidence is most diagnostic for the question
   - Weight evidence based on independence and verification

**2. Argument Evaluation:**
   - Assess logical consistency and reasoning quality
   - Identify cognitive biases in each advocate's presentation
   - Evaluate the strength of rebuttals and counterarguments
   - Determine which side addresses key uncertainties better

**3. Base Rate Analysis:**
   - Compare the reference classes proposed by each side
   - Determine which base rates are most appropriate
   - Assess the validity of adjustments from historical averages
   - Weight inside view vs. outside view appropriately

**4. Synthesis Methodology:**
   - Start with the most appropriate base rate as an anchor
   - Apply adjustments based on the strongest evidence from both sides
   - Consider the quality differential between competing arguments
   - Account for remaining uncertainties and unknown factors

**5. Calibration Checks:**
   - Apply the frequentist test: "Would I be right X% of the time with this confidence?"
   - Consider extremeness aversion and ensure probability reflects true confidence
   - Check for anchoring on 50% or other round numbers
   - Validate that uncertainty is appropriately reflected

**Bias Resistance:**
- Don't simply split the difference between advocate positions
- Weight arguments by quality, not by advocate passion
- Be willing to side strongly with one advocate if evidence clearly favors them
- Maintain independence from both advocate positions

**Quality Assessment Framework:**
- Evaluate the effectiveness of each advocate's quality pruning
- Assess how well misconceptions were identified and refuted
- Weight arguments based on their refined quality after pruning
- Identify any remaining logical flaws or biases

**Misconception Resolution:**
- Resolve conflicting misconception refutations between advocates
- Identify additional misconceptions not caught by either advocate
- Provide final corrections to factual errors and logical fallacies
- Summarize bias mitigation achieved through the debate process

**Output:** Provide a structured JSON following the `EnhancedJudgeOutput` schema."""

def get_high_advocate_task_description(question: str, search_timeframe: Dict, cutoff_date: str,
                                     search_strategy: str, query_limit: str, article_target: str,
                                     background: str = "", comprehensive_context: str = "",
                                     total_rounds: int = 3, search_budget_per_advocate: int = 10,
                                     searches_used_so_far: int = 0) -> str:
    """Task description for the High Probability Advocate"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
QUESTION CONTEXT:
{comprehensive_context}
"""
    elif background:
        context_section = f"""
BACKGROUND:
{background}
"""
    
    base_description = f"""
MISSION: Build the strongest possible case for a HIGH probability outcome for this forecasting question.

**Question:** {question}
**Current Date:** {cutoff_date}
**Search Period:** {search_timeframe['start']} to {search_timeframe['end']}
**Search Strategy:** {search_strategy} ({query_limit}, {article_target})
{context_section}

**HIGH PROBABILITY ADVOCACY PROTOCOL:**

**1. ESTABLISH YOUR POSITION:**
   - State your target probability range (aim for 60%+ if evidence supports it)
   - Articulate why this outcome is more likely than not

**2. OPTIMIZE BASE RATE SELECTION:**
   - Search for reference classes where similar events succeeded frequently
   - Use queries like: "[similar events] success rate", "[positive precedents] frequency", "[enabling factors] historical outcomes"
   - Emphasize the most favorable base rates that are still intellectually honest

**3. BUILD MOMENTUM CASE:**
   - Search for evidence of positive trends, momentum, and progress
   - Look for enabling conditions, resources, and capabilities
   - Find expert opinions that support optimistic outcomes
   - Use queries like: "[key factors] positive trends", "[stakeholders] commitment level", "[progress indicators] recent developments"

**4. MECHANISM ANALYSIS:**
   - Identify clear pathways to success
   - Show how obstacles can be overcome
   - Demonstrate that necessary conditions are being met
   - Highlight incentive alignment and motivation

**5. COUNTER-PESSIMISM:**
   - Prepare responses to likely skeptical arguments
   - Reframe potential obstacles as surmountable challenges
   - Show why past failures are not predictive of this case

**SEARCH STRATEGY FOR HIGH ADVOCACY:**
- Prioritize recent positive developments and progress indicators
- Seek expert opinions that support optimistic scenarios
- Look for evidence of commitment, resources, and capability
- Find precedents of similar successes

**OUTPUT:** Provide ONLY the JSON output following the `HighAdvocateOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "position_statement": "[str]",
  "target_probability_range": "xx%-yy%",
  "key_arguments": [
    {
      "argument_summary": "[str]",
      "supporting_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "base_rate_analysis": {
        "reference_class": "[str]",
        "historical_frequency": [num],
        "sample_size": [num],
        "relevance_to_current_case": "[str]",
        "adjustment_factors": ["[str]", "[str]"]
      },
      "confidence_level": "[str]",
      "potential_weaknesses": ["[str]", "[str]"]
    }
  ],
  "most_compelling_evidence": "[str]",
  "base_rate_justification": "[str]",
  "time_horizon_analysis": "[str]",
  "rebuttal_preparation": ["[str]", "[str]"]
}
```
'''
    
    return base_description + json_sample

def get_low_advocate_task_description(question: str, search_timeframe: Dict, cutoff_date: str,
                                    search_strategy: str, query_limit: str, article_target: str,
                                    background: str = "", comprehensive_context: str = "") -> str:
    """Task description for the Low Probability Advocate"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
QUESTION CONTEXT:
{comprehensive_context}
"""
    elif background:
        context_section = f"""
BACKGROUND:
{background}
"""
    
    base_description = f"""
MISSION: Build the strongest possible case for a LOW probability outcome for this forecasting question.

**Question:** {question}
**Current Date:** {cutoff_date}
**Search Period:** {search_timeframe['start']} to {search_timeframe['end']}
**Search Strategy:** {search_strategy} ({query_limit}, {article_target})
{context_section}

**LOW PROBABILITY ADVOCACY PROTOCOL:**

**1. ESTABLISH YOUR POSITION:**
   - State your target probability range (aim for 40% or lower if evidence supports it)
   - Articulate why this outcome is less likely than commonly believed

**2. OPTIMIZE BASE RATE SELECTION:**
   - Search for reference classes where similar events failed frequently
   - Use queries like: "[similar events] failure rate", "[comparable cases] obstacles", "[historical precedents] unsuccessful attempts"
   - Emphasize the most unfavorable base rates that are still intellectually honest

**3. BUILD BARRIER CASE:**
   - Search for evidence of obstacles, constraints, and negative trends
   - Look for missing enabling conditions and resource limitations
   - Find expert opinions that highlight challenges and skepticism
   - Use queries like: "[key obstacles] challenges", "[skeptical experts] concerns", "[implementation barriers] difficulties"

**4. FAILURE MODE ANALYSIS:**
   - Identify likely failure points and vulnerabilities
   - Show how past attempts have failed
   - Demonstrate that necessary conditions are missing
   - Highlight misaligned incentives and competing priorities

**5. COUNTER-OPTIMISM:**
   - Prepare responses to likely optimistic arguments
   - Show why positive signals may be misleading
   - Demonstrate why this case is different from success stories

**SEARCH STRATEGY FOR LOW ADVOCACY:**
- Prioritize evidence of obstacles, delays, and setbacks
- Seek expert opinions that express skepticism or concern
- Look for evidence of resource constraints and competing priorities
- Find precedents of similar failures

**OUTPUT:** Provide ONLY the JSON output following the `LowAdvocateOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "position_statement": "[str]",
  "target_probability_range": "xx%-yy%",
  "key_arguments": [
    {
      "argument_summary": "[str]",
      "supporting_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "base_rate_analysis": {
        "reference_class": "[str]",
        "historical_frequency": [num],
        "sample_size": [num],
        "relevance_to_current_case": "[str]",
        "adjustment_factors": ["[str]", "[str]"]
      },
      "confidence_level": "[str]",
      "potential_weaknesses": ["[str]", "[str]"]
    }
  ],
  "most_compelling_evidence": "[str]",
  "base_rate_justification": "[str]",
  "time_horizon_analysis": "[str]",
  "rebuttal_preparation": ["[str]", "[str]"]
}
```
'''

    return base_description + json_sample

def get_debate_judge_task_description(question: str, cutoff_date: str, time_horizon: str,
                                    comprehensive_context: str = "") -> str:
    """Task description for the Debate Judge"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
FULL CONTEXT FOR JUDGMENT:
{comprehensive_context}
"""
    
    base_description = f"""
MISSION: Evaluate the competing arguments and synthesize them into a well-calibrated probability.

**Question:** {question}
**Current Date:** {cutoff_date}
**Time Horizon:** {time_horizon}
{context_section}

**JUDICIAL EVALUATION PROTOCOL:**

**1. EVIDENCE QUALITY COMPARISON:**
   - Compare the credibility and strength of evidence from both advocates
   - Identify which evidence is most diagnostic and relevant
   - Assess the independence and verification of key facts
   - Determine which side's evidence is more compelling

**2. ARGUMENT STRENGTH ASSESSMENT:**
   - Evaluate logical consistency and reasoning quality from both sides
   - Identify cognitive biases in each advocate's presentation
   - Assess how well each side addresses key uncertainties
   - Determine which rebuttals are most effective

**3. BASE RATE RECONCILIATION:**
   - Compare the reference classes proposed by each advocate
   - Determine which base rates are most appropriate for this question
   - Assess the validity of proposed adjustments from historical averages
   - Decide on the proper weighting of inside vs. outside view

**4. SYNTHESIS AND CALIBRATION:**
   - Start with the most appropriate base rate as your anchor
   - Apply systematic adjustments based on the strongest evidence
   - Weight adjustments by the quality of supporting arguments
   - Do NOT simply average the advocate positions

**5. UNCERTAINTY AND CONFIDENCE:**
   - Assess remaining uncertainties not resolved by the debate
   - Determine appropriate confidence level based on evidence convergence
   - Apply calibration checks to ensure probability reflects true belief

**CRITICAL RULES:**
- Judge arguments by quality, not passion or volume
- Be willing to strongly favor one side if evidence clearly supports it
- Don't anchor on 50% or split differences without justification
- Your probability should reflect the weight of evidence, not compromise

**OUTPUT:** Provide ONLY the JSON output following the `DebateJudgmentOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "final_probability": [num],
  "confidence_level": "[str]",
  "high_advocate_evaluation": {
    "argument_strength": [num],
    "evidence_quality": [num],
    "logical_consistency": [num],
    "bias_detection": ["[str]", "[str]"],
    "key_strengths": ["[str]", "[str]"],
    "key_weaknesses": ["[str]", "[str]"]
  },
  "low_advocate_evaluation": {
    "argument_strength": [num],
    "evidence_quality": [num],
    "logical_consistency": [num],
    "bias_detection": ["[str]", "[str]"],
    "key_strengths": ["[str]", "[str]"],
    "key_weaknesses": ["[str]", "[str]"]
  },
  "synthesis_reasoning": "[str]",
  "evidence_weighting_rationale": "[str]",
  "uncertainty_factors": ["[str]", "[str]"],
  "decision_rationale": "[str]",
  "calibration_check": "[str]"
}
```
'''

    return base_description + json_sample

def get_high_advocate_rebuttal_description(question: str, cutoff_date: str, time_horizons: str = "") -> str:
    """Task description for High Advocate rebuttal phase"""
    base_description = f"""
MISSION: Provide a strong rebuttal to the Low Advocate's arguments while reinforcing your high probability position.

**Question:** {question}
**Current Date:** {cutoff_date}
**Time Horizons:** {time_horizons}
**Phase:** Rebuttal Round

**REBUTTAL PROTOCOL:**

**1. ANALYZE OPPONENT'S WEAKNESSES:**
   - Identify logical flaws, weak evidence, or overly pessimistic assumptions in the Low Advocate's case
   - Point out cherry-picking or misrepresentation of data
   - Highlight where their base rates may be inappropriate

**2. COUNTER THEIR KEY ARGUMENTS:**
   - Address their strongest arguments directly with counter-evidence
   - Reframe their negative evidence in a more optimistic context
   - Show how their failure modes can be mitigated or avoided

**3. REINFORCE YOUR POSITION:**
   - Strengthen your original arguments with additional evidence
   - Double down on your most compelling points
   - Show how their rebuttals actually support your case

**4. INTRODUCE NEW EVIDENCE:**
   - Present additional supporting evidence you may have held in reserve
   - Provide expert opinions that contradict their pessimistic view
   - Show recent developments that favor your position

**5. MAINTAIN INTELLECTUAL HONESTY:**
   - Acknowledge valid points from the opponent where appropriate
   - Explain why these don't fundamentally undermine your case
   - Be specific about what would change your mind

**OUTPUT:** Provide ONLY the JSON output following the `HighRebuttalOutput` structure.
"""

    json_samples = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "opponent_weaknesses_identified": ["[str]", "[str]"],
  "key_rebuttals": [
    {
      "original_argument_addressed": "[str]",
      "counterevidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "logical_flaws_identified": ["[str]", "[str]"],
      "reframing": "[str]",
      "strength_assessment": "[str]"
    }
  ],
  "reinforced_arguments": ["[str]", "[str]"],
  "new_evidence_introduced": [
    {
      "evidence_description": "[str]",
      "source_credibility": "[str]",
      "evidence_strength": "[str]",
      "evidence_type": "[str]",
      "temporal_relevance": "[str]"
    }
  ],
  "updated_probability_range": "xx%-yy%",
  "rebuttal_summary": "[str]"
}
```

**FOR ENHANCED MODE - SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "opponent_weaknesses_identified": ["[str]", "[str]"],
  "key_rebuttals": [
    {
      "original_argument_addressed": "[str]",
      "counterevidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "logical_flaws_identified": ["[str]", "[str]"],
      "reframing": "[str]",
      "strength_assessment": "[str]"
    }
  ],
  "reinforced_arguments": ["[str]", "[str]"],
  "new_evidence_introduced": [
    {
      "evidence_description": "[str]",
      "source_credibility": "[str]",
      "evidence_strength": "[str]",
      "evidence_type": "[str]",
      "temporal_relevance": "[str]"
    }
  ],
  "updated_probability_range": "xx%-yy%",
  "rebuttal_summary": "[str]",
  "quality_pruning": {
    "original_argument_quality": [num],
    "pruned_elements": [
      {
        "pruned_content": "[str]",
        "pruning_reason": "[str]",
        "replacement_suggestion": "[str]",
        "impact_assessment": "[str]"
      }
    ],
    "refined_argument_quality": [num],
    "quality_improvement_summary": "[str]",
    "remaining_weaknesses": ["[str]", "[str]"]
  },
  "misconception_refuting": {
    "misconceptions_identified": [
      {
        "misconception_description": "[str]",
        "misconception_type": "[str]",
        "refutation_evidence": [
          {
            "evidence_description": "[str]",
            "source_credibility": "[str]",
            "evidence_strength": "[str]",
            "evidence_type": "[str]",
            "temporal_relevance": "[str]"
          }
        ],
        "corrected_understanding": "[str]",
        "confidence_in_refutation": "[str]"
      }
    ],
    "bias_patterns_detected": ["[str]", "[str]"],
    "factual_corrections": ["[str]", "[str]"],
    "logical_corrections": ["[str]", "[str]"],
    "overall_reliability_improvement": "[str]"
  },
  "opponent_misconceptions_refuted": [
    {
      "misconception_description": "[str]",
      "misconception_type": "[str]",
      "refutation_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "corrected_understanding": "[str]",
      "confidence_in_refutation": "[str]"
    }
  ]
}
```
'''
    
    return base_description + json_samples

def get_low_advocate_rebuttal_description(question: str, cutoff_date: str, time_horizons: str = "") -> str:
    """Task description for Low Advocate rebuttal phase"""
    base_description = f"""
MISSION: Provide a strong rebuttal to the High Advocate's arguments while reinforcing your low probability position.

**Question:** {question}
**Current Date:** {cutoff_date}
**Time Horizons:** {time_horizons}
**Phase:** Rebuttal Round

**REBUTTAL PROTOCOL:**

**1. ANALYZE OPPONENT'S WEAKNESSES:**
   - Identify logical flaws, weak evidence, or overly optimistic assumptions in the High Advocate's case
   - Point out cherry-picking or misrepresentation of data
   - Highlight where their base rates may be too favorable

**2. COUNTER THEIR KEY ARGUMENTS:**
   - Address their strongest arguments directly with counter-evidence
   - Reframe their positive evidence as misleading or insufficient
   - Show how their success scenarios are unrealistic or unlikely

**3. REINFORCE YOUR POSITION:**
   - Strengthen your original arguments with additional evidence
   - Double down on your most compelling points about barriers and obstacles
   - Show how their rebuttals actually support your pessimistic case

**4. INTRODUCE NEW EVIDENCE:**
   - Present additional contrary evidence you may have held in reserve
   - Provide expert opinions that contradict their optimistic view
   - Show recent setbacks or challenges that favor your position

**5. MAINTAIN INTELLECTUAL HONESTY:**
   - Acknowledge valid points from the opponent where appropriate
   - Explain why these don't fundamentally undermine your case
   - Be specific about what would change your mind

**OUTPUT:** Provide ONLY the JSON output following the `LowRebuttalOutput` structure.
"""

    json_samples = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "opponent_weaknesses_identified": ["[str]", "[str]"],
  "key_rebuttals": [
    {
      "original_argument_addressed": "[str]",
      "counterevidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "logical_flaws_identified": ["[str]", "[str]"],
      "reframing": "[str]",
      "strength_assessment": "[str]"
    }
  ],
  "reinforced_arguments": ["[str]", "[str]"],
  "new_evidence_introduced": [
    {
      "evidence_description": "[str]",
      "source_credibility": "[str]",
      "evidence_strength": "[str]",
      "evidence_type": "[str]",
      "temporal_relevance": "[str]"
    }
  ],
  "updated_probability_range": "xx%-yy%",
  "rebuttal_summary": "[str]"
}
```

**FOR ENHANCED MODE - SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "opponent_weaknesses_identified": ["[str]", "[str]"],
  "key_rebuttals": [
    {
      "original_argument_addressed": "[str]",
      "counterevidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "logical_flaws_identified": ["[str]", "[str]"],
      "reframing": "[str]",
      "strength_assessment": "[str]"
    }
  ],
  "reinforced_arguments": ["[str]", "[str]"],
  "new_evidence_introduced": [
    {
      "evidence_description": "[str]",
      "source_credibility": "[str]",
      "evidence_strength": "[str]",
      "evidence_type": "[str]",
      "temporal_relevance": "[str]"
    }
  ],
  "updated_probability_range": "xx%-yy%",
  "rebuttal_summary": "[str]",
  "quality_pruning": {
    "original_argument_quality": [num],
    "pruned_elements": [
      {
        "pruned_content": "[str]",
        "pruning_reason": "[str]",
        "replacement_suggestion": "[str]",
        "impact_assessment": "[str]"
      }
    ],
    "refined_argument_quality": [num],
    "quality_improvement_summary": "[str]",
    "remaining_weaknesses": ["[str]", "[str]"]
  },
  "misconception_refuting": {
    "misconceptions_identified": [
      {
        "misconception_description": "[str]",
        "misconception_type": "[str]",
        "refutation_evidence": [
          {
            "evidence_description": "[str]",
            "source_credibility": "[str]",
            "evidence_strength": "[str]",
            "evidence_type": "[str]",
            "temporal_relevance": "[str]"
          }
        ],
        "corrected_understanding": "[str]",
        "confidence_in_refutation": "[str]"
      }
    ],
    "bias_patterns_detected": ["[str]", "[str]"],
    "factual_corrections": ["[str]", "[str]"],
    "logical_corrections": ["[str]", "[str]"],
    "overall_reliability_improvement": "[str]"
  },
  "opponent_misconceptions_refuted": [
    {
      "misconception_description": "[str]",
      "misconception_type": "[str]",
      "refutation_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "corrected_understanding": "[str]",
      "confidence_in_refutation": "[str]"
    }
  ]
}
```
'''

    return base_description + json_samples

def get_judge_intermediate_description(question: str, cutoff_date: str) -> str:
    """Task description for Judge intermediate evaluation phase"""
    base_description = f"""
MISSION: Evaluate the rebuttal round and provide intermediate assessment before final judgment.

**Question:** {question}
**Current Date:** {cutoff_date}
**Phase:** Post-Rebuttal Evaluation

**INTERMEDIATE EVALUATION PROTOCOL:**

**1. ASSESS REBUTTAL QUALITY:**
   - Determine which advocate provided stronger rebuttals
   - Identify which original arguments were successfully defended vs. undermined
   - Assess the quality of new evidence introduced in rebuttals

**2. IDENTIFY CONVERGENCE AND DIVERGENCE:**
   - Note areas where the advocates are beginning to agree
   - Highlight remaining areas of substantial disagreement
   - Identify which disagreements are most crucial to the final probability

**3. TRACK EVIDENCE EVOLUTION:**
   - Assess how the evidence base has been strengthened or weakened
   - Determine if new evidence significantly changes the picture
   - Identify which side's evidence is more compelling after rebuttals

**4. PRELIMINARY PROBABILITY ASSESSMENT:**
   - Note how your probability estimate is shifting (if at all)
   - Identify what additional clarification would be most helpful
   - Assess whether another round of debate would be beneficial

**5. IDENTIFY AREAS FOR CLARIFICATION:**
   - List specific points that need further exploration
   - Identify ambiguities that should be resolved before final judgment
   - Note any logical inconsistencies that need addressing

**OUTPUT:** Provide ONLY the JSON output following the `JudgeIntermediateOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "round_summary": "[str]",
  "emerging_consensus_areas": ["[str]", "[str]"],
  "remaining_disagreements": ["[str]", "[str]"],
  "evidence_quality_shift": "[str]",
  "preliminary_probability_trend": "[str]",
  "areas_needing_clarification": ["[str]", "[str]"]
}
```
'''

    return base_description + json_sample

# Enhanced Task Descriptions with Quality Pruning and Misconception Refuting

def get_enhanced_high_advocate_task_description(question: str, search_timeframe: Dict, cutoff_date: str, 
                                              search_strategy: str, query_limit: str, article_target: str, 
                                              background: str = "", comprehensive_context: str = "",
                                              total_rounds: int = 3, search_budget_per_advocate: int = 10,
                                              searches_used_so_far: int = 0) -> str:
    """Enhanced task description for High Probability Advocate with quality pruning and misconception refuting"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
QUESTION CONTEXT:
{comprehensive_context}
"""
    elif background:
        context_section = f"""
BACKGROUND:
{background}
"""

    # Calculate remaining search budget and provide strategic guidance
    remaining_searches = search_budget_per_advocate - searches_used_so_far
    remaining_rounds = total_rounds - 1  # Subtract 1 because current round is included
    suggested_searches_this_round = max(1, remaining_searches // max(1, remaining_rounds)) if remaining_rounds > 0 else remaining_searches
    
    search_budget_section = f"""
🔍 **SEARCH BUDGET ALLOCATION:**
- **Total search budget**: {search_budget_per_advocate} searches across all {total_rounds} rounds
- **Searches used so far**: {searches_used_so_far}
- **Remaining searches**: {remaining_searches}
- **Remaining rounds after this**: {remaining_rounds}
- **Suggested searches this round**: {suggested_searches_this_round}

**STRATEGIC SEARCH ALLOCATION:**
- Round 1 (Initial): Use ~30-40% of budget for comprehensive baseline research
- Rebuttal rounds: Use ~20-30% per round for targeted counter-evidence  
- Final round: Reserve ~20% for last-minute critical evidence
- **WARNING**: Exceeding your search budget will result in quality penalties in final evaluation
"""
    
    base_description = f"""
MISSION: Build the strongest possible case for a HIGH probability outcome while applying rigorous quality pruning and misconception refuting.

**Question:** {question}
**Current Date:** {cutoff_date}
**Search Period:** {search_timeframe['start']} to {search_timeframe['end']}
**Search Strategy:** {search_strategy} ({query_limit}, {article_target})
{context_section}
{search_budget_section}

**ENHANCED HIGH PROBABILITY ADVOCACY PROTOCOL:**

**PHASE 1: INITIAL ARGUMENT CONSTRUCTION**
**1. ESTABLISH YOUR POSITION:**
   - State your target probability range (aim for 60%+ if evidence supports it)
   - Articulate why this outcome is more likely than not

**2. OPTIMIZE BASE RATE SELECTION:**
   - Search for reference classes where similar events succeeded frequently
   - Use queries like: "[similar events] success rate", "[positive precedents] frequency"
   - Emphasize the most favorable base rates that are still intellectually honest

**3. BUILD MOMENTUM CASE:**
   - Search for evidence of positive trends, momentum, and progress
   - Look for enabling conditions, resources, and capabilities
   - Find expert opinions that support optimistic outcomes

**PHASE 2: QUALITY PRUNING**
**4. SYSTEMATIC ARGUMENT PRUNING:**
   - Identify and remove weak evidence (correlation without causation, anecdotal evidence)
   - Eliminate circular reasoning and tautological arguments
   - Remove unsupported claims lacking credible evidence
   - Flag and remove logical fallacies (hasty generalization, false cause, etc.)
   - Replace pruned elements with stronger, evidence-based alternatives

**5. EVIDENCE QUALITY ASSESSMENT:**
   - Rate original argument quality (0-10 scale)
   - Document all pruned elements with reasons
   - Assess quality improvement after pruning
   - Identify remaining weaknesses

**PHASE 3: MISCONCEPTION REFUTING**
**6. FACTUAL ERROR CORRECTION:**
   - Identify and correct any factual inaccuracies
   - Verify claims against authoritative sources
   - Update outdated information

**7. BIAS DETECTION AND MITIGATION:**
   - Detect confirmation bias (cherry-picking favorable evidence)
   - Identify availability heuristic (overweighting recent/memorable events)
   - Address anchoring bias (over-reliance on initial estimates)
   - Correct base rate neglect and representativeness heuristic

**8. LOGICAL FALLACY ELIMINATION:**
   - Remove ad hominem arguments
   - Eliminate false dichotomies
   - Correct slippery slope reasoning
   - Address straw man characterizations

**SEARCH STRATEGY:**
- Prioritize high-quality, peer-reviewed sources
- Seek diverse perspectives to avoid echo chambers
- Look for disconfirming evidence to test argument strength
- Find base rate data from authoritative statistical sources

**OUTPUT:** Provide ONLY the JSON output following the `EnhancedHighAdvocateOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "position_statement": "[str]",
  "target_probability_range": "xx%-yy%",
  "key_arguments": [
    {
      "argument_summary": "[str]",
      "supporting_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "base_rate_analysis": {
        "reference_class": "[str]",
        "historical_frequency": [num],
        "sample_size": [num],
        "relevance_to_current_case": "[str]",
        "adjustment_factors": ["[str]", "[str]"]
      },
      "confidence_level": "[str]",
      "potential_weaknesses": ["[str]", "[str]"]
    }
  ],
  "most_compelling_evidence": "[str]",
  "base_rate_justification": "[str]",
  "time_horizon_analysis": "[str]",
  "rebuttal_preparation": ["[str]", "[str]"],
  "quality_pruning": {
    "original_argument_quality": [num],
    "pruned_elements": [
      {
        "pruned_content": "[str]",
        "pruning_reason": "[str]",
        "replacement_suggestion": "[str]",
        "impact_assessment": "[str]"
      }
    ],
    "refined_argument_quality": [num],
    "quality_improvement_summary": "[str]",
    "remaining_weaknesses": ["[str]", "[str]"]
  },
  "misconception_refuting": {
    "misconceptions_identified": [
      {
        "misconception_description": "[str]",
        "misconception_type": "[str]",
        "refutation_evidence": [
          {
            "evidence_description": "[str]",
            "source_credibility": "[str]",
            "evidence_strength": "[str]",
            "evidence_type": "[str]",
            "temporal_relevance": "[str]"
          }
        ],
        "corrected_understanding": "[str]",
        "confidence_in_refutation": "[str]"
      }
    ],
    "bias_patterns_detected": ["[str]", "[str]"],
    "factual_corrections": ["[str]", "[str]"],
    "logical_corrections": ["[str]", "[str]"],
    "overall_reliability_improvement": "[str]"
  }
}
```
'''

    return base_description + json_sample

def get_enhanced_low_advocate_task_description(question: str, search_timeframe: Dict, cutoff_date: str,
                                             search_strategy: str, query_limit: str, article_target: str,
                                             background: str = "", comprehensive_context: str = "",
                                             total_rounds: int = 3, search_budget_per_advocate: int = 10,
                                             searches_used_so_far: int = 0) -> str:
    """Enhanced task description for Low Probability Advocate with quality pruning and misconception refuting"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
QUESTION CONTEXT:
{comprehensive_context}
"""
    elif background:
        context_section = f"""
BACKGROUND:
{background}
"""

    # Calculate remaining search budget and provide strategic guidance
    remaining_searches = search_budget_per_advocate - searches_used_so_far
    remaining_rounds = total_rounds - 1  # Subtract 1 because current round is included
    suggested_searches_this_round = max(1, remaining_searches // max(1, remaining_rounds)) if remaining_rounds > 0 else remaining_searches
    
    search_budget_section = f"""
🔍 **SEARCH BUDGET ALLOCATION:**
- **Total search budget**: {search_budget_per_advocate} searches across all {total_rounds} rounds
- **Searches used so far**: {searches_used_so_far}
- **Remaining searches**: {remaining_searches}
- **Remaining rounds after this**: {remaining_rounds}
- **Suggested searches this round**: {suggested_searches_this_round}

**STRATEGIC SEARCH ALLOCATION:**
- Round 1 (Initial): Use ~30-40% of budget for comprehensive baseline research
- Rebuttal rounds: Use ~20-30% per round for targeted counter-evidence  
- Final round: Reserve ~20% for last-minute critical evidence
- **WARNING**: Exceeding your search budget will result in quality penalties in final evaluation
"""

    base_description = f"""
MISSION: Build the strongest possible case for a LOW probability outcome while applying rigorous quality pruning and misconception refuting.

**Question:** {question}
**Current Date:** {cutoff_date}
**Search Period:** {search_timeframe['start']} to {search_timeframe['end']}
**Search Strategy:** {search_strategy} ({query_limit}, {article_target})
{context_section}
{search_budget_section}

**ENHANCED LOW PROBABILITY ADVOCACY PROTOCOL:**

**PHASE 1: INITIAL ARGUMENT CONSTRUCTION**
**1. ESTABLISH YOUR POSITION:**
   - State your target probability range (aim for 40% or lower if evidence supports it)
   - Articulate why this outcome is less likely than commonly believed

**2. OPTIMIZE BASE RATE SELECTION:**
   - Search for reference classes where similar events failed frequently
   - Use queries like: "[similar events] failure rate", "[comparable cases] obstacles"
   - Emphasize the most unfavorable base rates that are still intellectually honest

**3. BUILD BARRIER CASE:**
   - Search for evidence of obstacles, constraints, and negative trends
   - Look for missing enabling conditions and resource limitations
   - Find expert opinions that highlight challenges and skepticism

**PHASE 2: QUALITY PRUNING**
**4. SYSTEMATIC ARGUMENT PRUNING:**
   - Identify and remove weak evidence (correlation without causation, anecdotal evidence)
   - Eliminate circular reasoning and tautological arguments
   - Remove unsupported claims lacking credible evidence
   - Flag and remove logical fallacies (hasty generalization, false cause, etc.)
   - Replace pruned elements with stronger, evidence-based alternatives

**5. EVIDENCE QUALITY ASSESSMENT:**
   - Rate original argument quality (0-10 scale)
   - Document all pruned elements with reasons
   - Assess quality improvement after pruning
   - Identify remaining weaknesses

**PHASE 3: MISCONCEPTION REFUTING**
**6. FACTUAL ERROR CORRECTION:**
   - Identify and correct any factual inaccuracies
   - Verify claims against authoritative sources
   - Update outdated information

**7. BIAS DETECTION AND MITIGATION:**
   - Detect confirmation bias (cherry-picking favorable evidence)
   - Identify availability heuristic (overweighting recent/memorable events)
   - Address anchoring bias (over-reliance on initial estimates)
   - Correct base rate neglect and representativeness heuristic

**8. LOGICAL FALLACY ELIMINATION:**
   - Remove ad hominem arguments
   - Eliminate false dichotomies
   - Correct slippery slope reasoning
   - Address straw man characterizations

**SEARCH STRATEGY:**
- Prioritize high-quality, peer-reviewed sources
- Seek diverse perspectives to avoid echo chambers
- Look for confirming evidence to test argument strength
- Find base rate data from authoritative statistical sources

**OUTPUT:** Provide ONLY the JSON output following the `EnhancedLowAdvocateOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "position_statement": "[str]",
  "target_probability_range": "xx%-yy%",
  "key_arguments": [
    {
      "argument_summary": "[str]",
      "supporting_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "base_rate_analysis": {
        "reference_class": "[str]",
        "historical_frequency": [num],
        "sample_size": [num],
        "relevance_to_current_case": "[str]",
        "adjustment_factors": ["[str]", "[str]"]
      },
      "confidence_level": "[str]",
      "potential_weaknesses": ["[str]", "[str]"]
    }
  ],
  "most_compelling_evidence": "[str]",
  "base_rate_justification": "[str]",
  "time_horizon_analysis": "[str]",
  "rebuttal_preparation": ["[str]", "[str]"],
  "quality_pruning": {
    "original_argument_quality": [num],
    "pruned_elements": [
      {
        "pruned_content": "[str]",
        "pruning_reason": "[str]",
        "replacement_suggestion": "[str]",
        "impact_assessment": "[str]"
      }
    ],
    "refined_argument_quality": [num],
    "quality_improvement_summary": "[str]",
    "remaining_weaknesses": ["[str]", "[str]"]
  },
  "misconception_refuting": {
    "misconceptions_identified": [
      {
        "misconception_description": "[str]",
        "misconception_type": "[str]",
        "refutation_evidence": [
          {
            "evidence_description": "[str]",
            "source_credibility": "[str]",
            "evidence_strength": "[str]",
            "evidence_type": "[str]",
            "temporal_relevance": "[str]"
          }
        ],
        "corrected_understanding": "[str]",
        "confidence_in_refutation": "[str]"
      }
    ],
    "bias_patterns_detected": ["[str]", "[str]"],
    "factual_corrections": ["[str]", "[str]"],
    "logical_corrections": ["[str]", "[str]"],
    "overall_reliability_improvement": "[str]"
  }
}
```
'''

    return base_description + json_sample

def get_enhanced_judge_task_description(question: str, cutoff_date: str, time_horizon: str,
                                      comprehensive_context: str = "") -> str:
    """Enhanced task description for Judge with quality assessment and misconception resolution"""
    
    context_section = ""
    if comprehensive_context:
        context_section = f"""
FULL CONTEXT FOR JUDGMENT:
{comprehensive_context}
"""
    
    base_description = f"""
MISSION: Evaluate competing arguments and synthesize them into well-calibrated probabilities with comprehensive quality assessment and misconception resolution.

**Question:** {question}
**Current Date:** {cutoff_date}
**Time Horizon:** {time_horizon}
{context_section}

**ENHANCED JUDICIAL EVALUATION PROTOCOL:**

**PHASE 1: ARGUMENT QUALITY ASSESSMENT**
**1. EVALUATE QUALITY PRUNING EFFECTIVENESS:**
   - Assess how well each advocate pruned weak arguments
   - Evaluate the quality of replacement evidence
   - Determine if key logical flaws were identified and corrected
   - Compare argument strength before and after pruning

**2. MISCONCEPTION RESOLUTION ANALYSIS:**
   - Review misconceptions identified by each advocate
   - Assess the accuracy of bias detection
   - Evaluate the effectiveness of factual corrections
   - Identify any misconceptions missed by both advocates

**PHASE 2: EVIDENCE SYNTHESIS**
**3. EVIDENCE QUALITY COMPARISON:**
   - Compare the credibility and strength of evidence from both advocates
   - Weight evidence based on source quality and methodology
   - Assess the independence and verification of key facts
   - Determine which side's evidence is more compelling after quality improvements

**4. BIAS MITIGATION ASSESSMENT:**
   - Evaluate how well each side mitigated cognitive biases
   - Assess remaining biases not addressed by advocates
   - Determine the overall bias reduction achieved through the debate

**PHASE 3: PROBABILITY SYNTHESIS**
**5. BASE RATE RECONCILIATION:**
   - Compare the reference classes proposed by each advocate
   - Determine which base rates are most appropriate after quality improvements
   - Assess the validity of proposed adjustments from historical averages
   - Weight inside view vs. outside view appropriately

**6. FINAL CALIBRATION:**
   - Start with the most appropriate base rate as anchor
   - Apply systematic adjustments based on highest-quality evidence
   - Weight adjustments by argument quality after pruning
   - Account for uncertainty and remaining misconceptions

**7. QUALITY ASSURANCE:**
   - Conduct final check for logical consistency
   - Verify no major misconceptions remain unresolved
   - Assess overall reliability improvement from the enhanced debate process
   - Validate probability reflects true confidence level

**CRITICAL RULES:**
- Judge arguments by their refined quality, not original passion
- Weight evidence heavily toward sources that survived quality pruning
- Be willing to strongly favor the side with better misconception refuting
- Don't anchor on 50% without justification

**OUTPUT:** Provide ONLY the JSON output following the `EnhancedJudgeOutput` structure.
"""

    json_sample = '''
**SAMPLE JSON OUTPUT FORMAT:**
```json
{
  "final_probability": [num],
  "confidence_level": "[str]",
  "high_advocate_evaluation": {
    "argument_strength": [num],
    "evidence_quality": [num],
    "logical_consistency": [num],
    "bias_detection": ["[str]", "[str]"],
    "key_strengths": ["[str]", "[str]"],
    "key_weaknesses": ["[str]", "[str]"]
  },
  "low_advocate_evaluation": {
    "argument_strength": [num],
    "evidence_quality": [num],
    "logical_consistency": [num],
    "bias_detection": ["[str]", "[str]"],
    "key_strengths": ["[str]", "[str]"],
    "key_weaknesses": ["[str]", "[str]"]
  },
  "synthesis_reasoning": "[str]",
  "evidence_weighting_rationale": "[str]",
  "uncertainty_factors": ["[str]", "[str]"],
  "decision_rationale": "[str]",
  "calibration_check": "[str]",
  "overall_quality_assessment": "[str]",
  "misconceptions_resolved": [
    {
      "misconception_description": "[str]",
      "misconception_type": "[str]",
      "refutation_evidence": [
        {
          "evidence_description": "[str]",
          "source_credibility": "[str]",
          "evidence_strength": "[str]",
          "evidence_type": "[str]",
          "temporal_relevance": "[str]"
        }
      ],
      "corrected_understanding": "[str]",
      "confidence_in_refutation": "[str]"
    }
  ],
  "bias_mitigation_summary": "[str]"
}
```
'''

    return base_description + json_sample
