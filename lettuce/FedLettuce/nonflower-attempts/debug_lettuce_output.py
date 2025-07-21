#!/usr/bin/env python3
"""
Debug the actual LETTUCE output format to understand what we're getting
"""

import subprocess
import json
import ast

def capture_raw_lettuce_output():
    """Capture and analyze the raw LETTUCE output"""
    print("=== Capturing Raw LETTUCE Output ===")
    
    cmd = ["uv", "run", "--env-file", ".env", "lettuce-cli", 
           "--informal_names", "ibuprofen"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/home/apyba3/lettuce/lettuce"
        )
        
        if result.returncode == 0:
            print("✓ LETTUCE completed")
            print(f"Raw output length: {len(result.stdout)} characters")
            print("\n" + "="*60)
            print("FULL RAW OUTPUT:")
            print("="*60)
            print(result.stdout)
            print("="*60)
            
            # Try different parsing approaches
            output = result.stdout.strip()
            
            print("\n=== Analysis ===")
            
            # 1. Check if there are multiple JSON objects
            json_objects = []
            brace_count = 0
            current_obj = ""
            in_string = False
            escape_next = False
            
            for char in output:
                if escape_next:
                    escape_next = False
                    current_obj += char
                    continue
                    
                if char == '\\':
                    escape_next = True
                    current_obj += char
                    continue
                    
                if char == '"':
                    in_string = not in_string
                    
                current_obj += char
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and current_obj.strip().startswith('{'):
                            json_objects.append(current_obj.strip())
                            current_obj = ""
            
            print(f"Found {len(json_objects)} potential JSON objects")
            
            # 2. Look for the end marker and what comes after
            end_marker = "-------------- End ---------------"
            end_pos = output.find(end_marker)
            
            if end_pos != -1:
                after_end = output[end_pos + len(end_marker):].strip()
                print(f"\nContent after end marker ({len(after_end)} chars):")
                print(repr(after_end[:200]))
                
                # Try to parse what's after the end marker
                if after_end.startswith('['):
                    print("\nTrying to parse as Python list...")
                    try:
                        data = ast.literal_eval(after_end)
                        print(f"✓ Successfully parsed as Python: {len(data)} items")
                        return data, "python"
                    except Exception as e:
                        print(f"✗ Python parsing failed: {e}")
                
                if after_end.startswith('['):
                    print("\nTrying to parse as JSON...")
                    try:
                        data = json.loads(after_end)
                        print(f"✓ Successfully parsed as JSON: {len(data)} items")
                        return data, "json"
                    except Exception as e:
                        print(f"✗ JSON parsing failed: {e}")
            
            # 3. Look for individual JSON objects that match the paper format
            print(f"\nTrying to parse {len(json_objects)} individual JSON objects...")
            parsed_objects = []
            for i, obj in enumerate(json_objects):
                try:
                    parsed = json.loads(obj)
                    parsed_objects.append(parsed)
                    print(f"✓ Object {i+1}: {list(parsed.keys())}")
                except Exception as e:
                    print(f"✗ Object {i+1} failed: {e}")
            
            if parsed_objects:
                return parsed_objects, "individual_json"
            
        else:
            print(f"✗ LETTUCE failed: {result.stderr}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return None, None

def analyze_lettuce_structure(data, format_type):
    """Analyze the structure of parsed LETTUCE data"""
    print(f"\n=== Structure Analysis ({format_type}) ===")
    
    if not data:
        print("No data to analyze")
        return
    
    if isinstance(data, list):
        print(f"List with {len(data)} items")
        
        for i, item in enumerate(data):
            print(f"\nItem {i+1}:")
            if isinstance(item, dict):
                print(f"  Keys: {list(item.keys())}")
                
                # Look for informal term
                for key in ['query', 'informal_name', 'search_term']:
                    if key in item:
                        print(f"  Informal term ({key}): {item[key]}")
                
                # Look for results
                for key in ['Vector Search Results', 'llm_answer', 'OMOP matches', 'reply', 'CONCEPT']:
                    if key in item:
                        value = item[key]
                        print(f"  {key}: {type(value)}")
                        if isinstance(value, list):
                            print(f"    Length: {len(value)}")
                            if len(value) > 0:
                                print(f"    First item: {type(value[0])}")
                                if isinstance(value[0], dict):
                                    print(f"    First item keys: {list(value[0].keys())}")
                        elif isinstance(value, str):
                            print(f"    Value: {value}")
            else:
                print(f"  Type: {type(item)}")

def main():
    """Debug LETTUCE output format"""
    print("LETTUCE Output Format Debug")
    print("=" * 50)
    
    data, format_type = capture_raw_lettuce_output()
    
    if data:
        analyze_lettuce_structure(data, format_type)
        
        print(f"\n=== Recommendation ===")
        if format_type == "python":
            print("Use ast.literal_eval() for parsing")
        elif format_type == "json":
            print("Use json.loads() for parsing")
        elif format_type == "individual_json":
            print("Parse individual JSON objects separately")
        
    else:
        print("Could not parse LETTUCE output")

if __name__ == "__main__":
    main()