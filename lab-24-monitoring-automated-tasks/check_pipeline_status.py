"""
Pipeline Status Checker
Utility to check the status of the monitoring pipeline
"""

import csv
import os
from datetime import datetime, timedelta

def check_pipeline_status():
    """Check the status of the last pipeline execution"""
    report_file = "reports/pipeline_report.csv"
    
    if not os.path.exists(report_file):
        print("No pipeline report found. Pipeline may not have run yet.")
        return
    
    print("=" * 60)
    print("PIPELINE STATUS REPORT")
    print("=" * 60)
    
    
    with open(report_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        steps = list(reader)
    
    if not steps:
        print("No pipeline steps found in report.")
        return
    
    
    latest_timestamp = max(steps, key=lambda x: x['timestamp'])['timestamp']
    latest_time = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00').replace('+00:00', ''))
    
    print(f"Last Pipeline Execution: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time Since Last Run: {datetime.now() - latest_time}")
    print()
    
    
    status_counts = {}
    for step in steps:
        status = step['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Step Status Summary:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    print()
    
    
    print("Recent Pipeline Steps:")
    print("-" * 60)
    for step in steps[-10:]:  
        timestamp = datetime.fromisoformat(step['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
        print(f"{timestamp.strftime('%H:%M:%S')} | {step['step_name']:<15} | {step['status']:<8} | {step['message']}")
    
    
    failed_steps = [step for step in steps if step['status'] == 'FAILED']
    if failed_steps:
        print()
        print("FAILED STEPS DETECTED:")
        print("-" * 60)
        for step in failed_steps:
            timestamp = datetime.fromisoformat(step['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
            print(f"{timestamp.strftime('%H:%M:%S')} | {step['step_name']:<15} | {step['message']}")

if __name__ == "__main__":
    check_pipeline_status()
