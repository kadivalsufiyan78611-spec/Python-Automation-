"""
Pipeline Health Monitor
Advanced monitoring for pipeline health and performance
"""

import csv
import json
import os
import psutil
from datetime import datetime, timedelta

class PipelineHealthMonitor:
    def __init__(self):
        self.health_report_file = "reports/health_report.json"
        self.pipeline_report_file = "reports/pipeline_report.csv"
        self.log_file = "logs/pipeline.log"
        
    def check_system_resources(self):
        """Check system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_file_health(self):
        """Check health of pipeline files"""
        file_health = {}
        
        files_to_check = [
            self.pipeline_report_file,
            self.log_file,
            "data/processed_data.csv"
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                file_health[file_path] = {
                    'exists': True,
                    'size_bytes': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'readable': os.access(file_path, os.R_OK),
                    'writable': os.access(file_path, os.W_OK)
                }
            else:
                file_health[file_path] = {
                    'exists': False,
                    'size_bytes': 0,
                    'last_modified': None,
                    'readable': False,
                    'writable': False
                }
        
        return file_health
    
    def analyze_pipeline_performance(self):
        """Analyze pipeline performance from reports"""
        if not os.path.exists(self.pipeline_report_file):
            return {'error': 'No pipeline report found'}
        
        with open(self.pipeline_report_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            steps = list(reader)
        
        if not steps:
            return {'error': 'No pipeline steps found'}
        
        
        step_counts = {}
        success_rate = {}
        
        for step in steps:
            step_name = step['step_name']
            status = step['status']
            
            if step_name not in step_counts:
                step_counts[step_name] = {'total': 0, 'success': 0, 'failed': 0, 'retry': 0}
            
            step_counts[step_name]['total'] += 1
            
            if status == 'SUCCESS':
                step_counts[step_name]['success'] += 1
            elif status == 'FAILED':
                step_counts[step_name]['failed'] += 1
            elif status == 'RETRY':
                step_counts[step_name]['retry'] += 1
        
        
        for step_name, counts in step_counts.items():
            if counts['total'] > 0:
                success_rate[step_name] = (counts['success'] / counts['total']) * 100
        
        return {
            'step_counts': step_counts,
            'success_rates': success_rate,
            'total_executions': len([s for s in steps if s['step_name'] == 'fetch_data' and s['status'] == 'STARTED'])
        }
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'system_resources': self.check_system_resources(),
            'file_health': self.check_file_health(),
            'pipeline_performance': self.analyze_pipeline_performance()
        }
        
        
        os.makedirs(os.path.dirname(self.health_report_file), exist_ok=True)
        
        
        with open(self.health_report_file, 'w') as jsonfile:
            json.dump(health_data, jsonfile, indent=2)
        
        return health_data
    
    def display_health_summary(self):
        """Display health summary to console"""
        health_data = self.generate_health_report()
        
        print("=" * 60)
        print("PIPELINE HEALTH SUMMARY")
        print("=" * 60)
        print(f"Report Generated: {health_data['timestamp']}")
        print()
        
        
        resources = health_data['system_resources']
        print("System Resources:")
        print(f"  CPU Usage: {resources['cpu_percent']:.1f}%")
        print(f"  Memory Usage: {resources['memory_percent']:.1f}%")
        print(f"  Disk Usage: {resources['disk_percent']:.1f}%")
        print()
        
        
        print("File Health:")
        for file_path, health in health_data['file_health'].items():
            status = "OK" if health['exists'] and health['readable'] else "ISSUE"
            size_mb = health['size_bytes'] / (1024 * 1024) if health['size_bytes'] > 0 else 0
            print(f"  {file_path}: {status} ({size_mb:.2f} MB)")
        print()
        
        
        performance = health_data['pipeline_performance']
        if 'error' not in performance:
            print("Pipeline Performance:")
            print(f"  Total Pipeline Executions: {performance['total_executions']}")
            print("  Step Success Rates:")
            for step_name, rate in performance['success_rates'].items():
                print(f"    {step_name}: {rate:.1f}%")
        else:
            print(f"Pipeline Performance: {performance['error']}")
        
        print()
        print(f"Detailed report saved to: {self.health_report_file}")

def main():
    monitor = PipelineHealthMonitor()
    monitor.display_health_summary()

if __name__ == "__main__":
    main()
