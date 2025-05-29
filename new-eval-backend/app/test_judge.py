import json
import sys

def test_judge_parsing():
    # Sample response from your logs
    test_response = {
        "content": "```json\n{\n  \"gpt4\": {\n    \"personalization\": 7,\n    \"relevance\": 9,\n    \"fluency\": 9,\n    \"coherence\": 9,\n    \"creativity\": 8,\n    \"reasons\": {\n      \"personalization\": \"Includes commentary style.\",\n      \"relevance\": \"Accurately describes roles.\",\n      \"fluency\": \"Smooth structure.\",\n      \"coherence\": \"Logical flow.\",\n      \"creativity\": \"Unique aspects.\"\n    }\n  },\n  \"phi4\": {\n    \"personalization\": 6,\n    \"relevance\": 6,\n    \"fluency\": 8,\n    \"coherence\": 7,\n    \"creativity\": 5\n  }\n}\n```",
        "model": "gpt-4o",
        "metrics": {"responseTime": 4.5, "promptTokens": 308, "completionTokens": 505},
        "id": "gpt-4o-Evaluate"
    }
    
    print("Step 1: Result object type:", type(test_response))
    print("Step 2: Has content field:", "content" in test_response)
    
    # Extract content
    result_str = test_response["content"]
    print("Step 3: Content starts with:", result_str[:20])
    
    # Extract JSON from markdown - debugging steps
    print("Step 4: Contains markdown:", "```json" in result_str)
    parts = result_str.split("```json", 1)
    print("Step 5: After first split:", parts[1][:20])
    
    json_block = parts[1].split("```", 1)[0].strip()
    print("Step 6: Extracted JSON block (first 30 chars):", json_block[:30])
    
    # Character by character check of the first few bytes
    print("\nStep 7: Examining first 10 characters:")
    for i, char in enumerate(json_block[:10]):
        print(f"Position {i}: '{char}' (ASCII: {ord(char)})")
    
    # Try parsing with different approaches
    try:
        parsed1 = json.loads(json_block)
        print("Step 8: SUCCESS - Parsed with json.loads()")
        print("Keys:", list(parsed1.keys()))
    except Exception as e:
        print("Step 8: FAILED - json.loads() error:", e)
    
    # Save to file and try again
    with open("test_json.json", "w") as f:
        f.write(json_block)
    
    try:
        with open("test_json.json", "r") as f:
            parsed2 = json.load(f)
        print("Step 9: SUCCESS - Parsed from file")
        print("Keys:", list(parsed2.keys()))
    except Exception as e:
        print("Step 9: FAILED - json.load() from file error:", e)

if __name__ == "__main__":
    test_judge_parsing()