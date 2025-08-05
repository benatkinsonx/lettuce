#!/usr/bin/env python3
"""
Simple way to call LETTUCE CLI from Python - just like you would in terminal
"""

import subprocess
import os
import ast

def call_lettuce_simple(informal_names):
    """
    Call LETTUCE CLI exactly like you would in terminal
    
    Args:
        informal_names: List of terms or single term
    """
    # ensures input is always a list --> so it can be concatenated onto cmd terminal command
    if isinstance(informal_names, str):
        terms = [informal_names]
    else:
        terms = informal_names
    
    # command you would run in terminal
    cmd = ["uv", "run", "--env-file", ".env", "lettuce-cli", "--informal_names"] + terms
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Run the command from the cwd directory
        result = subprocess.run(
            cmd, # the command to run
            capture_output=True, # result will contain stdout and stderr
            text=True,
            cwd="/home/apyba3/lettuce/lettuce"
        )
        
        raw_output = result.stdout
        clean_raw_output = raw_output.replace('\n', '')

        endmarker = '-------------- End ---------------'
        endmarker_pos = clean_raw_output.find(endmarker)

        clean_results_str = clean_raw_output[endmarker_pos + len(endmarker):]
        clean_results_dict = ast.literal_eval(clean_results_str)

        results_dict = {}
        for query_dict in clean_results_dict:
            llm_answer = query_dict['llm_answer']
            informal_term = query_dict['query']
            results_dict[informal_term] = llm_answer

        if result.returncode == 0:
            print('Success!')
            print('Output:')
            print(results_dict)
        else:
            print('Failed :(')
            print('Error:')
            print(result.stderr)
            
        return llm_answer # and in both of those above cases, always return the results
        
    except Exception as e: # for an unexpected error, print the error and return None
        print(f"Error: {e}")
        return None

def main():
    """Test the simple approach"""
    print("Simple LETTUCE CLI Call")
    print("=" * 30)
    
    # # Test with single term (exactly like your terminal command)
    # print("=== Single term test ===")
    # call_lettuce_simple("ibuprofen")
    
    # Testing with multiple terms
    print("\n=== Multiple terms test ===")
    call_lettuce_simple(["Memantine HCL", "Ppaliperidone (3-month)"])

if __name__ == "__main__":
    main()