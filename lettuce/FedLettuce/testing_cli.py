#!/usr/bin/env python3
"""
Test the improved LETTUCE parsing
"""

import sys
import os
import json
import subprocess
from typing import List, Dict, Tuple

def run_lettuce_on_terms(informal_terms: List[str], top_k: int = 5) -> List[Dict]:
    """Test the improved parsing function"""
    try:
        print(f"Running LETTUCE on {len(informal_terms)} terms with top_k={top_k}")
        
        cmd = [
            "uv", "run", "--env-file", ".env", "lettuce-cli",
            "--informal_names"
        ] + informal_terms + [
            "--embedding-top-k", str(top_k),
            "--vector_search",
            "--use_llm"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=180,
            cwd="/home/apyba3/lettuce/lettuce"
        )
        
        if result.returncode == 0:
            print("✓ LETTUCE CLI completed successfully")
            
            output = result.stdout.strip()
            
            # Look for the end marker
            end_marker = "-------------- End ---------------"
            end_pos = output.find(end_marker)
            
            if end_pos != -1:
                json_start_search = output[end_pos + len(end_marker):].strip()
                
                # Find JSON array starting with [{'query':
                json_start = json_start_search.find("[{'query':")
                if json_start != -1:
                    json_part = json_start_search[json_start:]
                    
                    print(f"Found JSON at position {json_start}")
                    print(f"JSON part: {json_part[:100]}...")
                    
                    try:
                        lettuce_results = json.loads(json_part)
                        print(f"✓ Parsed {len(lettuce_results)} results from LETTUCE")
                        
                        if lettuce_results and len(lettuce_results) > 0:
                            sample_keys = list(lettuce_results[0].keys())
                            print(f"Sample result keys: {sample_keys}")
                        
                        return lettuce_results
                        
                    except json.JSONDecodeError as e:
                        print(f"✗ Failed to parse LETTUCE JSON: {e}")
                        return []
                else:
                    print("✗ No JSON array starting with [{'query': found")
                    print(f"Content after end marker: {json_start_search[:200]}...")
                    return []
            else:
                print("✗ No 'End' marker found in LETTUCE output")
                return []
        else:
            print(f"✗ LETTUCE CLI failed: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def test_ground_truth_checking():
    """Test the ground truth checking with sample data"""
    print("\n=== Testing Ground Truth Checking ===")
    
    # Sample ground truth (you'll replace this with real data)
    sample_ground_truth = {
        "ibuprofen": "ibuprofen",  # Should match LLM answer
        "tylenol": "acetaminophen"  # Should match vector search result
    }
    
    # Test with sample terms
    results = run_lettuce_on_terms(["ibuprofen", "tylenol"], top_k=3)
    
    if results:
        print(f"\nGot {len(results)} results from LETTUCE")
        
        # Show the structure
        for i, result in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"Query: {result.get('query', 'N/A')}")
            print(f"Vector Search Results: {len(result.get('Vector Search Results', []))} items")
            print(f"LLM Answer: {result.get('llm_answer', 'N/A')}")
            print(f"OMOP Matches: {result.get('OMOP matches', 'N/A')}")
        
        # Test ground truth checking (simplified version)
        print(f"\n--- Ground Truth Check ---")
        for result in results:
            query = result.get('query', '')
            if query in sample_ground_truth:
                expected = sample_ground_truth[query]
                
                # Check LLM answer
                llm_answer = result.get('llm_answer', '')
                if expected.lower() in llm_answer.lower():
                    print(f"✓ {query} → LLM found '{expected}' in '{llm_answer}'")
                else:
                    print(f"✗ {query} → LLM '{llm_answer}' doesn't contain '{expected}'")
                
                # Check vector search
                vector_results = result.get('Vector Search Results', [])
                vector_found = False
                for vr in vector_results[:3]:
                    if expected.lower() in vr.get('content', '').lower():
                        print(f"✓ {query} → Vector found '{expected}' in '{vr.get('content')}'")
                        vector_found = True
                        break
                if not vector_found:
                    vector_contents = [vr.get('content', '') for vr in vector_results[:3]]
                    print(f"✗ {query} → Vector results {vector_contents} don't contain '{expected}'")

def main():
    """Test the improved LETTUCE integration"""
    print("Improved LETTUCE Integration Test")
    print("=" * 50)
    
    test_ground_truth_checking()
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    main()