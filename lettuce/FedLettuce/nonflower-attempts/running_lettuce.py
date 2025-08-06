#!/usr/bin/env python3
"""
Simple way to call LETTUCE CLI from Python - just like you would in terminal
"""

import subprocess
import os

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
    cmd = ["uv", "run", "--env-file", ".env", "lettuce-cli", "--informal_names"] + terms + ['--no-use_llm']
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        # Run the command from the cwd directory
        result = subprocess.run(
            cmd, # the command to run
            capture_output=True, # result will contain stdout and stderr
            text=True,
            cwd="/home/apyba3/lettuce/lettuce"
        )
        
        # if the cli command was run successfully, print the output
        if result.returncode == 0: # 0 = success, 1 = not success
            print("✓ Success!")
            print(f"Output type = {type(result.stdout)}")
            print(result.stdout)
        else: # if the cli command failed, print the error messages
            print("✗ Failed!")
            print("Error:")
            print(result.stderr)
            
        return result.stdout # and in both of those above cases, always return the cli command output
        
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
    call_lettuce_simple(["ibuprofen", "tylenol"])

if __name__ == "__main__":
    main()