import asyncio
import json
import logging
from typing import Dict, Any
import sys
from semantic_kernel.functions.kernel_arguments import KernelArguments

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import your metrics function
from plugins.ComparisonPlugin.analyze_metrics_function import analyze_metrics

async def test_evaluate_models():
    """Test the analyze_metrics function with sample model outputs."""
    
    print("\n===== METRICS EVALUATION TEST =====\n")
    
    # Sample prompt and responses
    prompt = "Explain quantum computing in simple terms."
    
    model_responses = {
        "gpt4": "Quantum computing uses quantum bits or qubits that can exist in multiple states simultaneously, unlike classical bits that are either 0 or 1, enabling them to perform complex calculations much faster for certain problems.",
        "phi4": "Quantum computing leverages quantum mechanics principles to process information using qubits, which can represent multiple states at once, potentially solving certain complex problems exponentially faster than classical computers.",
        "llama": "Quantum computing uses principles of quantum physics to perform calculations. Unlike regular computers that use bits (0 or 1), quantum computers use quantum bits or 'qubits' that can exist in multiple states simultaneously, potentially solving certain problems much faster.",
        "gpt4nano": "Quantum computing uses quantum bits (qubits) that can be in multiple states at once, unlike classical bits which are either 0 or 1, allowing quantum computers to solve certain problems much faster than classical computers."
    }
    
    # Metrics data format matching your function's expected input
    metrics_payload = [
        {"model_id": "gpt4", "timing": {"total_response_time": 1.2}, "tokens": {"prompt_tokens": 10, "completion_tokens": 42, "total_tokens": 52}, "cost": {"total_cost": 0.0}},
        {"model_id": "phi4", "timing": {"total_response_time": 1.1}, "tokens": {"prompt_tokens": 11, "completion_tokens": 44, "total_tokens": 55}, "cost": {"total_cost": 0.0}},
        {"model_id": "llama", "timing": {"total_response_time": 1.5}, "tokens": {"prompt_tokens": 10, "completion_tokens": 53, "total_tokens": 63}, "cost": {"total_cost": 0.0}},
        {"model_id": "gpt4nano", "timing": {"total_response_time": 0.9}, "tokens": {"prompt_tokens": 10, "completion_tokens": 39, "total_tokens": 49}, "cost": {"total_cost": 0.0}}
    ]
    
    # Create arguments for the analyze_metrics function
    args = KernelArguments()
    args["prompt"] = prompt  # This was missing, causing the KeyError
    args["metrics"] = json.dumps(metrics_payload)
    args["responses"] = model_responses
    
    # Call the analyze_metrics function
    try:
        print(f"Running metrics analysis on {len(model_responses)} model responses...")
        result = await analyze_metrics(args)
        metrics_data = json.loads(result)
        
        if "error" in metrics_data and metrics_data.get("error"):
            print(f"❌ Error: {metrics_data['error']}")
        
        # Print results in a formatted table
        if "comparisons" in metrics_data and metrics_data["comparisons"]:
            print("\n===== EVALUATION METRICS RESULTS =====\n")
            print(f"{'Model':10} | {'BLEU':6} | {'ROUGE-1':7} | {'ROUGE-L':7} | {'CosSim':7} | {'Combined':8}")
            print("-" * 60)
            
            for item in metrics_data["comparisons"]:
                print(f"{item['model_id']:10} | {item['BLEU']:6.4f} | {item['ROUGE_1']:7.4f} | {item['ROUGE_L']:7.4f} | {item['SemanticCosineSimilarity']:7.4f} | {item['CombinedScore']:8.4f}")
            
            # Print performance metrics
            print("\n===== PERFORMANCE METRICS =====\n")
            print(f"{'Model':10} | {'Response Time':12} | {'Tokens':6} | {'Tokens/Sec':10}")
            print("-" * 50)
            
            for item in metrics_data["comparisons"]:
                metrics = item["metrics"]
                print(f"{item['model_id']:10} | {metrics['response_time']:12.2f}s | {metrics['tokens']['total_tokens']:6} | {metrics['tokens_per_second']:10.2f}")
            
            # Determine best model by combined score
            best_model = max(metrics_data["comparisons"], key=lambda x: x["CombinedScore"])
            print(f"\n✅ Best model by combined score: {best_model['model_id']} ({best_model['CombinedScore']:.4f})")
        else:
            print("❌ No comparison results found.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_evaluate_models())





    # now the thing is that , how can these thing be implememented to the compare endpoint as well, basically teh compare endpoint when run it has results from all 4 selected models, can something like this be implemenmted there as well