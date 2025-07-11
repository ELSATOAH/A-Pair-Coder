import os
import json
import pandas as pd
import zipfile
from pathlib import Path

def find_result_files(base_path):
    """Find all result files in the logs directory structure"""
    result_files = {
        'resultsmbpp': [],
        'resultshumaneval': [],
        'resultscodecontest': []
    }
    
    logs_dir = Path(base_path) / "logs"
    if not logs_dir.exists():
        print(f"Logs directory not found: {logs_dir}")
        return result_files
    
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith('.zip'):
                if 'resultsmbpp' in file:
                    result_files['resultsmbpp'].append(os.path.join(root, file))
                elif 'resultshumaneval' in file:
                    result_files['resultshumaneval'].append(os.path.join(root, file))
                elif 'resultscodecontest' in file:
                    result_files['resultscodecontest'].append(os.path.join(root, file))
    
    return result_files

def load_json_from_zip(zip_path):
    """Load JSON data from a ZIP file"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            json_files = [f for f in zip_ref.namelist() if f.endswith('.json')]
            if not json_files:
                print(f"No JSON files found in {zip_path}")
                return {}
            
            with zip_ref.open(json_files[0]) as json_file:
                return json.load(json_file)
    except Exception as e:
        print(f"Error loading {zip_path}: {e}")
        return {}

def load_json_data(file_path):
    """Load JSON data from file or ZIP"""
    if file_path.endswith('.zip'):
        return load_json_from_zip(file_path)
    else:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}

def extract_fail_reason(iter_data):
    # Suche nach typischen Fehlerfeldern
    for key in ["sandbox_result", "error_message", "traceback", "exception", "stderr", "fail_reason"]:
        val = iter_data.get(key)
        if val and isinstance(val, str) and val.strip():
            return val.strip().replace('\n', ' | ')
    return ""

def evaluate_structured_json(data, dataset_name):
    """Evaluate the structured JSON data for a dataset, alle Iterationen!"""
    results = []
    for prob_id, iterations in data.items():
        for iter_name, iter_data in iterations.items():
            passed = iter_data.get("test_passed_public", 0) + iter_data.get("test_passed_private", 0)
            failed = iter_data.get("test_failed_public", 0) + iter_data.get("test_failed_private", 0)
            timeout = iter_data.get("test_timeout_public", 0) + iter_data.get("test_timeout_private", 0)
            total = passed + failed + timeout

            result = {
                "problem_id": prob_id,
                "iteration": iter_name,
                "dataset": dataset_name,
                "status": "Passed" if passed > 0 and failed == 0 else "Failed",
                # 'fail_reason'
                "passed_tests": passed,
                "failed_tests": failed,
                "timeout_tests": timeout,
                "total_tests": total
            }
            results.append(result)
    return pd.DataFrame(results)

def evaluate_results(base_path=".", output_dir="."):
    """Main function to evaluate all results"""
    all_result_files = find_result_files(base_path)
    
    print("Found result files:")
    for dataset, files in all_result_files.items():
        print(f"  {dataset}: {len(files)} files")
        for file in files:
            print(f"    - {file}")
    
    dataframes = {}
    
    if all_result_files['resultsmbpp']:
        print("\nProcessing MBPP results...")
        data_mbpp = load_json_data(all_result_files['resultsmbpp'][0])
        df_mbpp = evaluate_structured_json(data_mbpp, "mbpp")
        dataframes['mbpp'] = df_mbpp
        
        mbpp_csv = os.path.join(output_dir, "paircoder_detailed_mbpp.csv")
        df_mbpp.to_csv(mbpp_csv, index=False)
        print(f"MBPP results saved to: {mbpp_csv}")
        
        total_problems = len(df_mbpp)
        passed_problems = len(df_mbpp[df_mbpp['status'] == 'Passed'])
        print(f"MBPP Summary: {passed_problems}/{total_problems} problems passed ({passed_problems/total_problems*100:.1f}%)")
    
    if all_result_files['resultshumaneval']:
        print("\nProcessing HumanEval results...")
        data_humaneval = load_json_data(all_result_files['resultshumaneval'][0])
        df_humaneval = evaluate_structured_json(data_humaneval, "humaneval")
        dataframes['humaneval'] = df_humaneval
        
        humaneval_csv = os.path.join(output_dir, "paircoder_detailed_humaneval.csv")
        df_humaneval.to_csv(humaneval_csv, index=False)
        print(f"HumanEval results saved to: {humaneval_csv}")
        
        total_problems = len(df_humaneval)
        passed_problems = len(df_humaneval[df_humaneval['status'] == 'Passed'])
        print(f"HumanEval Summary: {passed_problems}/{total_problems} problems passed ({passed_problems/total_problems*100:.1f}%)")
    
    if all_result_files['resultscodecontest']:
        print("\nProcessing CodeContest results...")
        data_codecontest = load_json_data(all_result_files['resultscodecontest'][0])
        df_codecontest = evaluate_structured_json(data_codecontest, "codecontest")
        dataframes['codecontest'] = df_codecontest
        
        codecontest_csv = os.path.join(output_dir, "paircoder_detailed_codecontest.csv")
        df_codecontest.to_csv(codecontest_csv, index=False)
        print(f"CodeContest results saved to: {codecontest_csv}")
        
        total_problems = len(df_codecontest)
        passed_problems = len(df_codecontest[df_codecontest['status'] == 'Passed'])
        print(f"CodeContest Summary: {passed_problems}/{total_problems} problems passed ({passed_problems/total_problems*100:.1f}%)")
    
    if dataframes:
        print("\n" + "="*50)
        print("OVERALL SUMMARY")
        print("="*50)
        
        for dataset_name, df in dataframes.items():
            total = len(df)
            passed = len(df[df['status'] == 'Passed'])
            failed = len(df[df['status'] == 'Failed'])
            
            print(f"{dataset_name.upper()}:")
            print(f"  Total problems: {total}")
            print(f"  Passed: {passed} ({passed/total*100:.1f}%)")
            print(f"  Failed: {failed} ({failed/total*100:.1f}%)")
            print()
        
        if len(dataframes) > 1:
            combined_df = pd.concat(dataframes.values(), ignore_index=True)
            combined_csv = os.path.join(output_dir, "paircoder_combined_results.csv")
            combined_df.to_csv(combined_csv, index=False)
            print(f"Combined results saved to: {combined_csv}")
    
    return dataframes

def print_log_report(file_path, dataset_name):
    """creates a table for log files."""
    print(f"\n{'='*60}")
    print(f"Logfile: {file_path}")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*60}")
    data = load_json_data(file_path)
    if not data:
        print("  [WARN] No data load!")
        return
    df = evaluate_structured_json(data, dataset_name)
    if df.empty:
        print("  [WARN] no evaulable data!")
        return
    print(df[['problem_id', 'status', 'passed_tests', 'failed_tests', 'timeout_tests', 'total_tests']].to_string(index=False))
    print(f"{'-'*60}")
    total = len(df)
    passed = len(df[df['status'] == 'Passed'])
    failed = len(df[df['status'] == 'Failed'])
    print(f"  summary: {passed} Passed, {failed} Failed, total: {total}")
    print(f"{'='*60}\n")

def print_logs(zip_path):
    """printing previews of logs."""
    import re
    print(f"\n{'*'*60}")
    print(f"all Log files in: {zip_path}")
    print(f"{'*'*60}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            log_files = [f for f in zip_ref.namelist() if f.endswith('.log')]
            if not log_files:
                print("  [INFO] no logs found.")
                return
            for logname in sorted(log_files):
                print(f"\n--- {logname} ---")
                with zip_ref.open(logname) as logf:
                    try:
                        lines = logf.read().decode(errors='replace').splitlines()
                    except Exception as e:
                        print(f"  [WARN] could not read file: {e}")
                        continue
                    important = []
                    for line in lines:
                        l = line.lower()
                        if any(word in l for word in ['error', 'fail', 'timeout', 'traceback', 'exception']):
                            important.append(line)
                    preview = lines[:2] + (["..."] if len(lines) > 4 else []) + lines[-2:]
                    print("  preview:")
                    for l in preview:
                        print("   ", l)
                    if important:
                        print("  important line:")
                        for l in important:
                            print("   ", l)
                    else:
                        print("  [INFO] No important lines found.")
    except Exception as e:
        print(f"[ERROR] Could not open zip: {e}")
    print(f"{'*'*60}\n")

if __name__ == "__main__":
    base_path = r"\Examples\PairCoder-main"

    results = evaluate_results(base_path, base_path)

    all_result_files = find_result_files(base_path)
    for dataset, files in all_result_files.items():
        for file in files:
            print_log_report(file, dataset.replace('results', ''))
            print_logs(file)
