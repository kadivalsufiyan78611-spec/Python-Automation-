"""
Comprehensive Report Generator
Creates detailed analysis reports from pipeline execution data
"""

import csv
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

class ComprehensiveReportGenerator:
    def __init__(self):
        self.pipeline_report_file = "reports/pipeline_report.csv"
        self.health_report_file = "reports/health_report.json"
        self.summary_report_file = "reports/comprehensive_summary.html"
        
    def load_pipeline_data(self):
        """Load pipeline execution data"""
        if not os.path.exists(self.pipeline_report_file):
            return []
        
        with open(self.pipeline_report_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    
    def analyze_execution_patterns(self, pipeline_data):
        """Analyze pipeline execution patterns"""
        if not pipeline_data:
            return {}
        
        
        executions = []
        current_execution = []
        
        for step in pipeline_data:
            if step['step_name'] == 'fetch_data' and step['status'] == 'STARTED':
                if current_execution:
                    executions.append(current_execution)
                current_execution = [step]
            else:
                current_execution.append(step)
        
        if current_execution:
            executions.append(current_execution)
        
        
        execution_analysis = []
        for i, execution in enumerate(executions):
            start_time = None
            end_time = None
            success = True
            steps_count = len(execution)
            
            for step in execution:
                timestamp = datetime.fromisoformat(step['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
                if start_time is None or timestamp < start_time:
                    start_time = timestamp
                if end_time is None or timestamp > end_time:
                    end_time = timestamp
                if step['status'] == 'FAILED':
                    success = False
            
            duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
            
            execution_analysis.append({
                'execution_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'duration_seconds': duration,
                'success': success,
                'steps_count': steps_count
            })
        
        return execution_analysis
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        pipeline_data = self.load_pipeline_data()
        execution_analysis = self.analyze_execution_patterns(pipeline_data)
        
        
        total_executions = len(execution_analysis)
        successful_executions = sum(1 for ex in execution_analysis if ex['success'])
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        avg_duration = sum(ex['duration_seconds'] for ex in execution_analysis) / total_executions if total_executions > 0 else 0
        
        
        step_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0, 'retry': 0})
        for step in pipeline_data:
            step_name = step['step_name']
            status = step['status']
            step_stats[step_name]['total'] += 1
            step_stats[step_name][status.lower()] += 1
        
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Pipeline Comprehensive Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: green; }}
        .failed {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Pipeline Comprehensive Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Executions:</strong> {total_executions}
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> <span class="{'success' if success_rate > 90 else 'warning' if success_rate > 70 else 'failed'}">{success_rate:.1f}%</span>
        </div>
        <div class="metric">
            <strong>Average Duration:</strong> {avg_duration:.2f} seconds
        </div>
    </div>
    
    <div class="section">
        <h2>Step Performance</h2>
        <table>
            <tr>
                <th>Step Name</th>
                <th>Total Runs</th>
                <th>Success</th>
                <th>Failed</th>
                <th>Retries</th>
                <th>Success Rate</th>
            </tr>
        """
        
        for step_name, stats in step_stats.items():
            if stats['total'] > 0:
                step_success_rate = (stats['success'] / stats['total']) * 100
                html_content += f"""
            <tr>
                <td>{step_name}</td>
                <td>{stats['total']}</td>
                <td class="success">{stats['success']}</td>
                <td class="failed">{stats['failed']}</td>
                <td class="warning">{stats['retry']}</td>
                <td class="{'success' if step_success_rate > 90 else 'warning' if step_success_rate > 70 else 'failed'}">{step_success_rate:.1f}%</td>
            </tr>
                """
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>Recent Executions</h2>
        <table>
            <tr>
                <th>Execution ID</th>
                <th>Start Time</th>
                <th>Duration (seconds)</th>
                <th>Status</th>
                <th>Steps Count</th>
            </tr>
        """
