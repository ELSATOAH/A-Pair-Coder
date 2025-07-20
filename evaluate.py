import os
import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple


def find_log_directories(base_path: str) -> Dict[str, List[str]]:
    """Find all log directories in the specified path structure."""
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
            # Recursively find results directories
            for root, dirs, files in os.walk(dataset_path):
                if 'results' in dirs:
                    results_path = os.path.join(root, 'results')
                    log_dirs[dataset].append(results_path)
    
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


def process_results_directory(results_dir: str, dataset_name: str) -> Tuple[List[Dict], Dict]:
    """Process a single results directory."""
    solutions_file = os.path.join(results_dir, 'solutions.json')
    
    # Parse solutions.json
    if not os.path.exists(solutions_file):
        print(f"No solutions.json found in {results_dir}")
        return [], {}
    
    results = parse_solutions_json(solutions_file)
    
    # Add dataset name and directory info to results
    for result in results:
        result['dataset_name'] = dataset_name
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
    base_path = r"/path/to/your/logs"  # Change this to your logs base path
    output_dir = r"/path/to/your/output"  # Change this to your output directory

    # Find all log directories
    log_dirs = find_log_directories(base_path)
    
    print("Found log directories:")
    for dataset, dirs in log_dirs.items():
        print(f"  {dataset}: {len(dirs)} directories")
        for dir_path in dirs:
            print(f"    - {dir_path}")
    
    all_results = []
    dataset_summaries = {}
    
    # Process each dataset
    for dataset_name, results_directories in log_dirs.items():
        if not results_directories:
            print(f"\nNo results directories found for {dataset_name}")
            continue
            
        print(f"\nProcessing {dataset_name} dataset...")
        
        dataset_results = []
        
        for results_dir in results_directories:
            print(f"  Processing: {results_dir}")
            results, log_analysis = process_results_directory(results_dir, dataset_name)
            dataset_results.extend(results)
            all_results.extend(results)
        
        if dataset_results:
            # Create DataFrame for this dataset
            df = pd.DataFrame(dataset_results)
            
            # Calculate summary statistics
            summary = calculate_summary_stats(df)
            dataset_summaries[dataset_name] = summary
            
            # Save detailed CSV for this dataset
            detailed_csv = os.path.join(output_dir, f"paircoder_detailed_{dataset_name}.csv")
            df.to_csv(detailed_csv, index=False)
            print(f"  Detailed results saved to: {detailed_csv}")
            
            # Print summary
            print(f"  Summary:")
            print(f"    Total problems: {summary['total_problems']}")
            print(f"    Passed: {summary['passed_problems']} ({summary['accuracy_percent']:.1f}%)")
            print(f"    Failed: {summary['failed_problems']}")
            print(f"    No tests: {summary['no_test_problems']}")
    
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
        
        if overall_total > 0:
            overall_accuracy = (overall_passed / overall_total * 100)
            print(f"\nOVERALL ACCURACY: {overall_passed}/{overall_total} ({overall_accuracy:.1f}%)")
        
        # Create summary CSV
        summary_df = pd.DataFrame([
            {
                'dataset': dataset_name,
                'total_problems': summary['total_problems'],
                'passed_problems': summary['passed_problems'],
                'failed_problems': summary['failed_problems'],
                'no_test_problems': summary['no_test_problems'],
                'accuracy_percent': summary['accuracy_percent'],
                'total_tests_run': summary['total_tests_run'],
                'total_tests_passed': summary['total_tests_passed'],
                'total_tests_failed': summary['total_tests_failed'],
                'total_tests_timeout': summary['total_tests_timeout']
            }
            for dataset_name, summary in dataset_summaries.items()
        ])
        
        summary_csv = os.path.join(output_dir, "paircoder_summary.csv")
        summary_df.to_csv(summary_csv, index=False)
        print(f"\nSummary statistics saved to: {summary_csv}")
    
    else:
        print("\nNo results found to process!")


if __name__ == "__main__":
    main()
