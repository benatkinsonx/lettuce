# groundtruth_checker.py
"""
Call LETTUCE CLI from Python and check ground truth
"""
# ALL LETTUCE ONLY CLIENT LOGIC WORKS
import subprocess
import os
import ast
import pandas as pd
import re

def call_lettuce_simple(informal_names):
    """Call LETTUCE CLI from Python, passing list of terms"""
    if isinstance(informal_names, str):
        terms = [informal_names]
    else:
        terms = informal_names

    print(informal_names)
    cmd = ["uv", "run", "--env-file", ".env", "lettuce-cli", "--informal_names"] + terms + ['--no-use_llm']
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
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
            # topk_results = [d['content'] for d in query_dict['Vector Search Results']]
            topk_results = [
                d.get('concept') or d.get('content')
                for d in query_dict['Vector Search Results']
            ]
            informal_term = query_dict['query']
            results_dict[informal_term] = topk_results

        if result.returncode == 0:
            print('Success!')
            print('RESULTS_DICT:')
            print(f'{results_dict}')
        else:
            print('Failed :(')
            print('Error:')
            print(result.stderr)

        return results_dict

    except Exception as e:
        print(f"Error: {e}")
        return None

def standardise_text(text):
    pattern = r'\W+'
    replacement = ''
    string_being_operated_on = text.lower().strip()
    return re.sub(pattern, replacement, string_being_operated_on)

def ground_truth_checker(df):
    """Check which inputs fail to retrieve the expected output"""
    informal_names = df['input_data'].tolist()
    results_dict = call_lettuce_simple(informal_names)

    incorrectly_mapped = []
    for _, row in df.iterrows():
        input_term = row['input_data']
        ground_truth = row['expected_output']

        if input_term in results_dict:
            top5_vecsearch = results_dict[input_term]
            # if ground_truth.lower() not in [s.lower() for s in top5_vecsearch]:
            if standardise_text(ground_truth) not in [standardise_text(s) for s in top5_vecsearch]:
                incorrectly_mapped.append(input_term)

    print(f"\n❌ Terms that failed to match expected output:\n{incorrectly_mapped}\n")
    return incorrectly_mapped

def main():
    print("Running LETTUCE Ground Truth Checker")
    print("=" * 40)

    # Define test data
    data = {
        'input_data': ["Memantine HCL", 'Ppaliperidone (3-month)', 'aceTaminophen', 'Trazodone HCL'],
        'expected_output': ['memantine hydrochloride', 'paliperidone', 'AcetamInophen', 'trazodone hydrochloride']
    }
    df = pd.DataFrame(data)

    ground_truth_checker(df)

if __name__ == "__main__":
    main()
