import os
import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple


def find_log_directories(base_path: str) -> Dict[str, List[Tuple[str, str]]]:
    """Find all log directories in the specified path structure.
    Returns a dict where each key is a dataset type and each value is a list of tuples (results_path, subtype).
    """
    log_dirs = {
        'codecontest': [],
        'humaneval': [],
        'mbpp': []
    }
    
    logs_base = Path(base_path) / "logs"
    
    if not logs_base.exists():
        print(f"Logs directory not found: {logs_base}")
        return log_dirs
    
    # Search for each dataset type
    for dataset in ['codecontest', 'humaneval', 'mbpp']:
        dataset_path = logs_base / dataset
        if dataset_path.exists():
            # Recursively find results directories and track their subtype
            for root, dirs, files in os.walk(dataset_path):
                if 'results' in dirs:
                    results_path = os.path.join(root, 'results')
                    # Extract the subtype from the path (e.g., 'test', 'plus', 'valid', 'raw')
                    rel_path = os.path.relpath(root, dataset_path)
                    subtype = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path
                    log_dirs[dataset].append((results_path, subtype))
    
    return log_dirs


def parse_solutions_json(solutions_file: str) -> List[Dict]:
    """Parse solutions.json file and extract test results."""
    try:
        with open(solutions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {solutions_file}: {e}")
        return []
    
    results = []
    
    # Iterate through all problems in the solutions file
    for dataset_type, problems in data.items():
        for problem_id, iterations in problems.items():
            for iteration_name, iteration_data in iterations.items():
                # Extract test results
                passed_public = iteration_data.get("test_passed_public", 0)
                failed_public = iteration_data.get("test_failed_public", 0)
                timeout_public = iteration_data.get("test_timeout_public", 0)
                
                passed_private = iteration_data.get("test_passed_private", 0)
                failed_private = iteration_data.get("test_failed_private", 0)
                timeout_private = iteration_data.get("test_timeout_private", 0)
                
                passed_generate = iteration_data.get("test_passed_generate", 0)
                failed_generate = iteration_data.get("test_failed_generate", 0)
                timeout_generate = iteration_data.get("test_timeout_generate", 0)
                
                total_passed = passed_public + passed_private + passed_generate
                total_failed = failed_public + failed_private + failed_generate
                total_timeout = timeout_public + timeout_private + timeout_generate
                total_tests = total_passed + total_failed + total_timeout
                
                # Determine overall status
                if total_passed > 0 and total_failed == 0 and total_timeout == 0:
                    status = "PASSED"
                elif total_tests == 0:
                    status = "NO_TESTS"
                else:
                    status = "FAILED"
                
                result = {
                    'problem_id': problem_id,
                    'iteration': iteration_name,
                    'dataset_type': dataset_type,
                    'status': status,
                    'passed_public': passed_public,
                    'failed_public': failed_public,
                    'timeout_public': timeout_public,
                    'passed_private': passed_private,
                    'failed_private': failed_private,
                    'timeout_private': timeout_private,
                    'passed_generate': passed_generate,
                    'failed_generate': failed_generate,
                    'timeout_generate': timeout_generate,
                    'total_passed': total_passed,
                    'total_failed': total_failed,
                    'total_timeout': total_timeout,
                    'total_tests': total_tests
                }
                results.append(result)
    
    return results


def analyze_log_file(log_file: str) -> Dict:
    """Analyze a single log file for additional information."""
    log_info = {
        'file_name': os.path.basename(log_file),
        'error_count': 0,
        'timeout_detected': False,
        'last_timestamp': None,
        'execution_time': None
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        first_timestamp = None
        last_timestamp = None
        
        for line in lines:
            # Extract timestamps
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                if first_timestamp is None:
                    first_timestamp = timestamp
                last_timestamp = timestamp
            
            # Count errors
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'traceback']):
                log_info['error_count'] += 1
            
            # Check for timeouts
            if 'timeout' in line.lower():
                log_info['timeout_detected'] = True
        
        log_info['last_timestamp'] = last_timestamp
        
        # Calculate execution time if we have both timestamps
        if first_timestamp and last_timestamp:
            try:
                from datetime import datetime
                fmt = '%Y-%m-%d %H:%M:%S.%f'
                start_time = datetime.strptime(first_timestamp, fmt)
                end_time = datetime.strptime(last_timestamp, fmt)
                execution_time = (end_time - start_time).total_seconds()
                log_info['execution_time'] = execution_time
            except:
                pass
                
    except Exception as e:
        print(f"Error analyzing log file {log_file}: {e}")
    
    return log_info


def process_results_directory(results_dir: str, dataset_name: str, subtype: str) -> Tuple[List[Dict], Dict]:
    """Process a single results directory."""
    solutions_file = os.path.join(results_dir, 'solutions.json')
    
    # Parse solutions.json
    if not os.path.exists(solutions_file):
        print(f"No solutions.json found in {results_dir}")
        return [], {}
    
    results = parse_solutions_json(solutions_file)
    
    # Add dataset name, subtype, and directory info to results
    for result in results:
        result['dataset_name'] = dataset_name
        result['subtype'] = subtype
        result['results_directory'] = results_dir
    
    # Analyze log files
    log_files = [f for f in os.listdir(results_dir) if f.endswith('.log')]
    log_analysis = {}
    
    for log_file in log_files:
        log_path = os.path.join(results_dir, log_file)
        log_info = analyze_log_file(log_path)
        log_analysis[log_file] = log_info
    
    return results, log_analysis


def calculate_summary_stats(df: pd.DataFrame) -> Dict:
    """Calculate summary statistics for a dataset."""
    total_problems = len(df)
    passed_problems = len(df[df['status'] == 'PASSED'])
    failed_problems = len(df[df['status'] == 'FAILED'])
    no_test_problems = len(df[df['status'] == 'NO_TESTS'])
    
    accuracy = (passed_problems / total_problems * 100) if total_problems > 0 else 0
    
    return {
        'total_problems': total_problems,
        'passed_problems': passed_problems,
        'failed_problems': failed_problems,
        'no_test_problems': no_test_problems,
        'accuracy_percent': accuracy,
        'total_tests_run': df['total_tests'].sum(),
        'total_tests_passed': df['total_passed'].sum(),
        'total_tests_failed': df['total_failed'].sum(),
        'total_tests_timeout': df['total_timeout'].sum()
    }


def main():
    # Configuration
    base_path = r"c:\Users\Taylan\Desktop\ML\seeee\A-Pair-Coder\Examples\PairCoder-main"  # Change this to your logs base path
    output_dir = r"c:\Users\Taylan\Desktop\ML\seeee\A-Pair-Coder\eval"  # Change this to your output directory

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Find all log directories
    log_dirs = find_log_directories(base_path)
    
    print("Found log directories:")
    for dataset, dirs in log_dirs.items():
        print(f"  {dataset}: {len(dirs)} directories")
        for dir_path, subtype in dirs:
            print(f"    - {subtype}: {dir_path}")
    
    all_results = []
    dataset_summaries = {}
    subtype_results = {}  # To store results by dataset_subtype combination
    
    # Process each dataset
    for dataset_name, results_directories in log_dirs.items():
        if not results_directories:
            print(f"\nNo results directories found for {dataset_name}")
            continue
            
        print(f"\nProcessing {dataset_name} dataset...")
        
        dataset_results = []
        
        for results_dir, subtype in results_directories:
            print(f"  Processing: {subtype} - {results_dir}")
            results, log_analysis = process_results_directory(results_dir, dataset_name, subtype)
            dataset_results.extend(results)
            all_results.extend(results)
            
            # Store results by subtype for separate CSV files
            dataset_subtype_key = f"{dataset_name}_{subtype}"
            if dataset_subtype_key not in subtype_results:
                subtype_results[dataset_subtype_key] = []
            subtype_results[dataset_subtype_key].extend(results)
        
        if dataset_results:
            # Create DataFrame for this dataset (all subtypes combined)
            df = pd.DataFrame(dataset_results)
            
            # Calculate summary statistics
            summary = calculate_summary_stats(df)
            dataset_summaries[dataset_name] = summary
            
            # Print summary
            print(f"  Summary:")
            print(f"    Total problems: {summary['total_problems']}")
            print(f"    Passed: {summary['passed_problems']} ({summary['accuracy_percent']:.1f}%)")
            print(f"    Failed: {summary['failed_problems']}")
            print(f"    No tests: {summary['no_test_problems']}")
    
    # Save separate CSV files for each dataset_subtype combination
    print(f"\nSaving separate detailed files for each subtype...")
    for dataset_subtype_key, results in subtype_results.items():
        if results:
            df = pd.DataFrame(results)
            detailed_csv = os.path.join(output_dir, f"paircoder_detailed_{dataset_subtype_key}.csv")
            df.to_csv(detailed_csv, index=False)
            print(f"  Detailed results saved to: {detailed_csv}")
            
            # Calculate and print subtype summary
            summary = calculate_summary_stats(df)
            print(f"    {dataset_subtype_key} Summary: {summary['passed_problems']}/{summary['total_problems']} ({summary['accuracy_percent']:.1f}%)")
    
    # Create combined results
    if all_results:
        combined_df = pd.DataFrame(all_results)
        combined_csv = os.path.join(output_dir, "paircoder_combined_results.csv")
        combined_df.to_csv(combined_csv, index=False)
        print(f"\nCombined results saved to: {combined_csv}")
        
        # Create overall summary
        print("\n" + "="*60)
        print("OVERALL SUMMARY")
        print("="*60)
        
        overall_total = 0
        overall_passed = 0
        
        for dataset_name, summary in dataset_summaries.items():
            print(f"\n{dataset_name.upper()}:")
            print(f"  Total problems: {summary['total_problems']}")
            print(f"  Passed: {summary['passed_problems']} ({summary['accuracy_percent']:.1f}%)")
            print(f"  Failed: {summary['failed_problems']}")
            print(f"  Total tests run: {summary['total_tests_run']}")
            print(f"  Tests passed: {summary['total_tests_passed']}")
            print(f"  Tests failed: {summary['total_tests_failed']}")
            print(f"  Tests timeout: {summary['total_tests_timeout']}")
            
            overall_total += summary['total_problems']
            overall_passed += summary['passed_problems']
        
        # Show breakdown by subtype
        print(f"\nBREAKDOWN BY SUBTYPE:")
        for dataset_subtype_key, results in subtype_results.items():
            if results:
                df = pd.DataFrame(results)
                summary = calculate_summary_stats(df)
                print(f"  {dataset_subtype_key}: {summary['passed_problems']}/{summary['total_problems']} ({summary['accuracy_percent']:.1f}%)")
        
        if overall_total > 0:
            overall_accuracy = (overall_passed / overall_total * 100)
            print(f"\nOVERALL ACCURACY: {overall_passed}/{overall_total} ({overall_accuracy:.1f}%)")
        
        # Create summary CSV (including subtype breakdown)
        summary_rows = []
        
        # Add dataset-level summaries
        for dataset_name, summary in dataset_summaries.items():
            summary_rows.append({
                'dataset': dataset_name,
                'subtype': 'all',
                'total_problems': summary['total_problems'],
                'passed_problems': summary['passed_problems'],
                'failed_problems': summary['failed_problems'],
                'no_test_problems': summary['no_test_problems'],
                'accuracy_percent': summary['accuracy_percent'],
                'total_tests_run': summary['total_tests_run'],
                'total_tests_passed': summary['total_tests_passed'],
                'total_tests_failed': summary['total_tests_failed'],
                'total_tests_timeout': summary['total_tests_timeout']
            })
        
        # Add subtype-level summaries
        for dataset_subtype_key, results in subtype_results.items():
            if results:
                df = pd.DataFrame(results)
                summary = calculate_summary_stats(df)
                dataset_name, subtype = dataset_subtype_key.split('_', 1)
                summary_rows.append({
                    'dataset': dataset_name,
                    'subtype': subtype,
                    'total_problems': summary['total_problems'],
                    'passed_problems': summary['passed_problems'],
                    'failed_problems': summary['failed_problems'],
                    'no_test_problems': summary['no_test_problems'],
                    'accuracy_percent': summary['accuracy_percent'],
                    'total_tests_run': summary['total_tests_run'],
                    'total_tests_passed': summary['total_tests_passed'],
                    'total_tests_failed': summary['total_tests_failed'],
                    'total_tests_timeout': summary['total_tests_timeout']
                })
        
        summary_df = pd.DataFrame(summary_rows)
        summary_csv = os.path.join(output_dir, "paircoder_summary.csv")
        summary_df.to_csv(summary_csv, index=False)
        print(f"\nSummary statistics saved to: {summary_csv}")
    
    else:
        print("\nNo results found to process!")


if __name__ == "__main__":
    main()
