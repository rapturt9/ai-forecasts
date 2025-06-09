#!/usr/bin/env python3
"""
Run benchmark against Manifold Markets data
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_forecasts.benchmark.manifold_benchmark import ManifoldBenchmark
from ai_forecasts.benchmark.benchmark_runner import BenchmarkRunner
from ai_forecasts.agents.orchestrator import ForecastOrchestrator
from ai_forecasts.utils.llm_client import LLMClient


async def main():
    """Main benchmark execution"""
    
    print("🔍 AI Forecasting System Benchmark")
    print("=" * 50)
    
    # Step 1: Collect Manifold Markets data
    print("\n📊 Step 1: Collecting Manifold Markets data...")
    
    manifold = ManifoldBenchmark()
    
    try:
        # Fetch resolved questions
        questions = manifold.fetch_resolved_questions(
            limit=100,
            min_volume=100,  # Only questions with decent trading volume
            days_back=45     # Last 45 days
        )
        
        print(f"✅ Collected {len(questions)} resolved questions")
        
        # Show breakdown
        ai_questions = manifold.get_ai_related_questions()
        tech_questions = manifold.get_tech_questions()
        
        print(f"   - AI-related: {len(ai_questions)}")
        print(f"   - Tech-related: {len(tech_questions)}")
        
        if len(questions) == 0:
            print("❌ No questions collected. Using sample data instead.")
            # Create sample benchmark data
            sample_data = create_sample_benchmark()
            benchmark_file = "sample_benchmark.json"
            with open(benchmark_file, 'w') as f:
                import json
                json.dump(sample_data, f, indent=2)
        else:
            # Save benchmark dataset
            benchmark_file = manifold.save_benchmark_data("manifold_benchmark.json")
        
    except Exception as e:
        print(f"❌ Error collecting Manifold data: {e}")
        print("Using sample data instead...")
        sample_data = create_sample_benchmark()
        benchmark_file = "sample_benchmark.json"
        with open(benchmark_file, 'w') as f:
            import json
            json.dump(sample_data, f, indent=2)
    
    # Step 2: Initialize forecasting system
    print("\n🤖 Step 2: Initializing AI forecasting system...")
    
    try:
        # Initialize orchestrator (it will create its own LLM client)
        orchestrator = ForecastOrchestrator()
        runner = BenchmarkRunner(orchestrator)
        print("✅ System initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        return
    
    # Step 3: Run benchmark
    print("\n🎯 Step 3: Running benchmark...")
    
    try:
        # Run on a subset for quick testing
        results = await runner.run_benchmark_suite(
            benchmark_file, 
            max_cases=5  # Start with 5 cases for testing
        )
        
        print("✅ Benchmark completed!")
        
        # Step 4: Display results
        print("\n📈 Step 4: Results Summary")
        print("-" * 30)
        
        info = results["benchmark_info"]
        metrics = results["aggregate_metrics"]
        analysis = results["analysis"]
        
        print(f"Total cases: {info['total_cases']}")
        print(f"Successful: {info['successful_cases']}")
        print(f"Failed: {info['failed_cases']}")
        print(f"Success rate: {metrics.get('success_rate', 0):.1%}")
        
        if "mean_brier_score" in metrics:
            print(f"\n🎯 Accuracy Metrics:")
            print(f"  Brier Score: {metrics['mean_brier_score']:.3f} (lower is better)")
            print(f"  Binary Accuracy: {metrics.get('mean_binary_accuracy', 0):.1%}")
            print(f"  Avg Confidence: {metrics.get('mean_confidence', 0):.1%}")
        
        if "market_beat_rate" in metrics:
            print(f"\n📊 Market Comparison:")
            print(f"  Beat market rate: {metrics['market_beat_rate']:.1%}")
            print(f"  Avg improvement: {metrics.get('mean_market_improvement', 0):.3f}")
        
        print(f"\n⚡ Performance:")
        print(f"  Avg execution time: {metrics.get('mean_execution_time', 0):.1f}s")
        
        if analysis.get("performance_level"):
            print(f"\n🏆 Overall Performance: {analysis['performance_level']}")
        
        if analysis.get("strengths"):
            print(f"\n💪 Strengths:")
            for strength in analysis["strengths"]:
                print(f"  • {strength}")
        
        if analysis.get("weaknesses"):
            print(f"\n⚠️  Areas for Improvement:")
            for weakness in analysis["weaknesses"]:
                print(f"  • {weakness}")
        
        if analysis.get("recommendations"):
            print(f"\n🔧 Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
        
        # Save detailed results
        results_file = runner.save_results("benchmark_results.json")
        print(f"\n💾 Detailed results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()


def create_sample_benchmark():
    """Create sample benchmark data when Manifold API is unavailable"""
    from datetime import datetime
    
    return {
        "created_at": datetime.now().isoformat(),
        "total_questions": 5,
        "benchmark_cases": [
            {
                "case_id": "sample_001",
                "source": "sample_data",
                "question": "Will OpenAI release GPT-5 by end of 2024?",
                "description": "Question about OpenAI's next major model release",
                "initial_conditions": "As of 2024-01-01: OpenAI has released GPT-4, competition in AI is increasing rapidly",
                "target_outcome": "Will OpenAI release GPT-5 by end of 2024?",
                "time_horizon": "1 year",
                "ground_truth": {
                    "resolution": "NO",
                    "final_probability": 0.25,
                    "market_volume": 1000,
                    "resolution_date": "2024-12-31T23:59:59"
                },
                "metadata": {
                    "category": "ai",
                    "tags": ["openai", "gpt", "ai"],
                    "created_date": "2024-01-01T00:00:00",
                    "close_date": "2024-12-31T23:59:59"
                }
            },
            {
                "case_id": "sample_002",
                "source": "sample_data",
                "question": "Will any AI company reach $100B valuation in 2024?",
                "description": "Question about AI company valuations",
                "initial_conditions": "As of 2024-01-01: AI investment is booming, several companies valued highly",
                "target_outcome": "Will any AI company reach $100B valuation in 2024?",
                "time_horizon": "1 year",
                "ground_truth": {
                    "resolution": "YES",
                    "final_probability": 0.75,
                    "market_volume": 800,
                    "resolution_date": "2024-12-31T23:59:59"
                },
                "metadata": {
                    "category": "business",
                    "tags": ["ai", "valuation", "startup"],
                    "created_date": "2024-01-01T00:00:00",
                    "close_date": "2024-12-31T23:59:59"
                }
            },
            {
                "case_id": "sample_003",
                "source": "sample_data",
                "question": "Will there be a major AI safety incident in 2024?",
                "description": "Question about AI safety and potential incidents",
                "initial_conditions": "As of 2024-01-01: AI capabilities advancing rapidly, safety concerns growing",
                "target_outcome": "Will there be a major AI safety incident in 2024?",
                "time_horizon": "1 year",
                "ground_truth": {
                    "resolution": "NO",
                    "final_probability": 0.15,
                    "market_volume": 600,
                    "resolution_date": "2024-12-31T23:59:59"
                },
                "metadata": {
                    "category": "ai-safety",
                    "tags": ["ai", "safety", "risk"],
                    "created_date": "2024-01-01T00:00:00",
                    "close_date": "2024-12-31T23:59:59"
                }
            },
            {
                "case_id": "sample_004",
                "source": "sample_data",
                "question": "Will Tesla achieve full self-driving by end of 2024?",
                "description": "Question about autonomous vehicle progress",
                "initial_conditions": "As of 2024-01-01: Tesla has advanced FSD beta, regulatory approval pending",
                "target_outcome": "Will Tesla achieve full self-driving by end of 2024?",
                "time_horizon": "1 year",
                "ground_truth": {
                    "resolution": "NO",
                    "final_probability": 0.20,
                    "market_volume": 1200,
                    "resolution_date": "2024-12-31T23:59:59"
                },
                "metadata": {
                    "category": "technology",
                    "tags": ["tesla", "autonomous", "fsd"],
                    "created_date": "2024-01-01T00:00:00",
                    "close_date": "2024-12-31T23:59:59"
                }
            },
            {
                "case_id": "sample_005",
                "source": "sample_data",
                "question": "Will Apple release an AI assistant better than Siri in 2024?",
                "description": "Question about Apple's AI development",
                "initial_conditions": "As of 2024-01-01: Apple lagging in AI, pressure to compete with ChatGPT",
                "target_outcome": "Will Apple release an AI assistant better than Siri in 2024?",
                "time_horizon": "1 year",
                "ground_truth": {
                    "resolution": "YES",
                    "final_probability": 0.60,
                    "market_volume": 900,
                    "resolution_date": "2024-12-31T23:59:59"
                },
                "metadata": {
                    "category": "technology",
                    "tags": ["apple", "ai", "assistant"],
                    "created_date": "2024-01-01T00:00:00",
                    "close_date": "2024-12-31T23:59:59"
                }
            }
        ]
    }


if __name__ == "__main__":
    asyncio.run(main())