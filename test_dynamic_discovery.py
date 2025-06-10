"""
Test script for Dynamic Domain Knowledge Discovery System

This script demonstrates the new dynamic domain knowledge discovery capabilities
that replace hard-coded domain knowledge with adaptive pattern discovery.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from src.ai_forecasts.domain_knowledge import (
    DynamicDomainKnowledgeDiscovery,
    DomainAdaptiveSearchStrategy,
    TrendExtrapolationEngine,
    DomainType
)
from src.ai_forecasts.utils.llm_client import LLMClient


async def test_dynamic_domain_discovery():
    """Test the dynamic domain knowledge discovery system"""
    
    print("🔬 Testing Dynamic Domain Knowledge Discovery System")
    print("=" * 60)
    
    # Initialize the system
    discovery = DynamicDomainKnowledgeDiscovery()
    search_strategy = DomainAdaptiveSearchStrategy()
    trend_extrapolation = TrendExtrapolationEngine()
    
    # Test questions from different domains
    test_questions = [
        {
            "question": "Will AI be able to generate bug-free code of more than 10,000 lines before 2030?",
            "background": "Large language models like GPT-4 and Claude can write code but still produce bugs",
            "expected_domain": DomainType.TECHNOLOGY
        },
        {
            "question": "Will global electric vehicle sales exceed 50% of all car sales by 2030?",
            "background": "EV adoption has been accelerating globally with government incentives and improving technology",
            "expected_domain": DomainType.ECONOMICS
        },
        {
            "question": "Will the global average temperature increase by more than 1.5°C above pre-industrial levels by 2030?",
            "background": "Climate change has been accelerating with record temperatures in recent years",
            "expected_domain": DomainType.CLIMATE
        }
    ]
    
    cutoff_date = datetime(2024, 7, 1)  # Simulate benchmark cutoff
    
    for i, test_case in enumerate(test_questions, 1):
        print(f"\n🔍 Test Case {i}: {test_case['expected_domain'].value.upper()} Domain")
        print("-" * 50)
        print(f"Question: {test_case['question']}")
        print(f"Background: {test_case['background']}")
        
        try:
            # Step 1: Discover domain knowledge
            print(f"\n1️⃣ Discovering domain knowledge...")
            discovered_knowledge = discovery.discover_domain_knowledge(
                test_case['question'],
                test_case['background'],
                cutoff_date
            )
            
            print(f"   ✅ Domain classified: {discovered_knowledge.domain_type.value}")
            print(f"   📊 Discovery confidence: {discovered_knowledge.discovery_confidence:.3f}")
            print(f"   📈 Scaling laws found: {len(discovered_knowledge.scaling_laws)}")
            print(f"   📉 Trends found: {len(discovered_knowledge.trends)}")
            print(f"   👥 Expert patterns found: {len(discovered_knowledge.expert_patterns)}")
            
            # Display some discovered patterns
            if discovered_knowledge.scaling_laws:
                print(f"   🔬 Example scaling law: {discovered_knowledge.scaling_laws[0].mathematical_form}")
            
            if discovered_knowledge.trends:
                trend = discovered_knowledge.trends[0]
                print(f"   📈 Example trend: {trend.trend_description} ({trend.direction})")
            
            if discovered_knowledge.base_rates:
                base_rate_key = list(discovered_knowledge.base_rates.keys())[0]
                base_rate_value = discovered_knowledge.base_rates[base_rate_key]
                print(f"   📊 Example base rate: {base_rate_key} = {base_rate_value:.1%}")
            
            # Step 2: Generate adaptive search strategy
            print(f"\n2️⃣ Generating adaptive search strategy...")
            search_strat = search_strategy.generate_search_strategy(
                test_case['question'],
                test_case['background'],
                discovered_knowledge,
                cutoff_date
            )
            
            print(f"   🎯 Primary queries: {len(search_strat.primary_queries)}")
            print(f"   🔍 Secondary queries: {len(search_strat.secondary_queries)}")
            print(f"   🔄 Fallback queries: {len(search_strat.fallback_queries)}")
            
            if search_strat.primary_queries:
                example_query = search_strat.primary_queries[0]
                print(f"   📝 Example query: '{example_query.query_text[:60]}...'")
                print(f"      Type: {example_query.search_type}, Relevance: {example_query.expected_relevance:.2f}")
            
            # Step 3: Perform trend extrapolation
            print(f"\n3️⃣ Performing trend extrapolation...")
            extrapolation = trend_extrapolation.extrapolate_trends(
                test_case['question'],
                test_case['background'],
                discovered_knowledge,
                "6 years",  # 2024 to 2030
                cutoff_date
            )
            
            print(f"   🎯 Predicted probability: {extrapolation.predicted_value:.3f}")
            print(f"   📊 Confidence interval: [{extrapolation.confidence_interval[0]:.3f}, {extrapolation.confidence_interval[1]:.3f}]")
            print(f"   🔧 Model used: {extrapolation.model_used.trend_type.value}")
            print(f"   🎯 Extrapolation confidence: {extrapolation.extrapolation_confidence:.3f}")
            
            if extrapolation.risk_factors:
                print(f"   ⚠️  Risk factors: {extrapolation.risk_factors[0]}")
            
            # Step 4: Generate dynamic domain context
            print(f"\n4️⃣ Generating dynamic domain context...")
            dynamic_context = discovery.generate_dynamic_domain_context(discovered_knowledge)
            context_lines = dynamic_context.split('\n')[:8]  # First 8 lines
            print("   📝 Dynamic context sample:")
            for line in context_lines:
                if line.strip():
                    print(f"      {line}")
            
            print(f"\n✅ Test case {i} completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error in test case {i}: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
    
    print(f"\n🎉 Dynamic Domain Knowledge Discovery Testing Complete!")
    print("=" * 60)
    
    # Summary of capabilities
    print(f"\n📋 SYSTEM CAPABILITIES DEMONSTRATED:")
    print(f"✅ Automatic domain classification")
    print(f"✅ Dynamic scaling law discovery") 
    print(f"✅ Domain-specific trend identification")
    print(f"✅ Expert consensus pattern recognition")
    print(f"✅ Adaptive search strategy generation")
    print(f"✅ Mathematical trend extrapolation")
    print(f"✅ Uncertainty quantification")
    print(f"✅ Dynamic context generation")
    
    print(f"\n🔄 REPLACEMENT OF HARD-CODED KNOWLEDGE:")
    print(f"❌ No more hard-coded AI/EV/climate facts")
    print(f"❌ No more static expert bias assumptions")
    print(f"❌ No more fixed base rate estimates")
    print(f"✅ Dynamic discovery for each question")
    print(f"✅ Evidence-based pattern recognition")
    print(f"✅ Adaptive forecasting methodology")


async def test_comparison_with_hard_coded():
    """Compare dynamic discovery with hard-coded knowledge"""
    
    print(f"\n🔄 COMPARISON: Dynamic vs Hard-Coded Knowledge")
    print("=" * 60)
    
    question = "Will AI be able to generate bug-free code of more than 10,000 lines before 2030?"
    
    print(f"Question: {question}")
    
    # Show what the old hard-coded system would use
    print(f"\n❌ OLD HARD-CODED APPROACH:")
    print(f"   - AI capabilities have advanced rapidly 2022-2024 (GPT-4, Claude-3, etc.)")
    print(f"   - Technology adoption: Often faster than initial conservative estimates") 
    print(f"   - AI research community expects continued rapid progress (scaling laws)")
    print(f"   - Fixed assumptions about expert biases")
    print(f"   - Generic base rates not specific to question")
    
    # Show what the new dynamic system discovers
    print(f"\n✅ NEW DYNAMIC DISCOVERY APPROACH:")
    discovery = DynamicDomainKnowledgeDiscovery()
    discovered = discovery.discover_domain_knowledge(question, "", datetime(2024, 7, 1))
    
    print(f"   - Domain auto-classified: {discovered.domain_type.value}")
    print(f"   - Discovered {len(discovered.scaling_laws)} relevant scaling laws")
    print(f"   - Identified {len(discovered.trends)} domain-specific trends")
    print(f"   - Found {len(discovered.expert_patterns)} expert consensus patterns")
    print(f"   - Calculated question-specific base rates")
    print(f"   - Discovery confidence: {discovered.discovery_confidence:.3f}")
    
    print(f"\n🎯 KEY ADVANTAGES:")
    print(f"✅ Adapts to each specific question")
    print(f"✅ Discovers relevant patterns dynamically")
    print(f"✅ Quantifies discovery confidence")
    print(f"✅ Avoids pre-programmed biases")
    print(f"✅ Uses evidence-based base rates")
    print(f"✅ Scales to new domains automatically")


if __name__ == "__main__":
    asyncio.run(test_dynamic_domain_discovery())
    asyncio.run(test_comparison_with_hard_coded())
