"""
Report Generation Module
Creates detailed daily summary reports
"""

import json
import datetime
from pathlib import Path
from collections import defaultdict
import logging

class ReportGenerator:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports"
        self.logs_dir = self.base_dir / "logs"
        
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        
        self.logger = logging.getLogger('report_generator')
    
    def load_statistics(self):
        """Load current statistics"""
        stats_file = self.reports_dir / "stats.json"
        
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'total_runs': 0,
                    'successes': 0,
                    'failures': 0,
                    'last_run': None,
                    'error_details': []
                }
        except Exception as e:
            self.logger.error(f"Failed to load statistics: {e}")
            return {}
    
    def analyze_error_patterns(self, error_details):
        """Analyze error patterns from error details"""
        error_types = defaultdict(int)
        error_contexts = defaultdict(int)
        
        for error in error_details:
            if isinstance(error, dict):
                error_type = error.get('error_type', 'Unknown')
                context = error.get('context', 'Unknown')
                
                error_types[error_type] += 1
                error_contexts[context] += 1
        
        return {
            'error_types': dict(error_types),
            'error_contexts': dict(error_contexts)
        }
    
    def calculate_success_rate(self, stats):
        """Calculate success rate percentage"""
        total = stats.get('total_runs', 0)
        successes = stats.get('successes', 0)
        
        if total == 0:
            return 0.0
        
        return (successes / total) * 100
    
    def generate_daily_report(self):
        """Generate comprehensive daily summary report"""
        stats = self.load_statistics()
        
        if not stats:
            self.logger.error("No statistics available for report generation")
            return False
        
        
        success_rate = self.calculate_success_rate(stats)
        error_analysis = self.analyze_error_patterns(stats.get('error_details', []))
        
        
        report_content = self._create_report_content(stats, success_rate, error_analysis)
        
        
        return self._save_report(report_content)
    
    def _create_report_content(self, stats, success_rate, error_analysis):
        """Create the actual report content"""
        current_time = datetime.datetime.now()
        
        report_lines = [
            "=" * 60,
            "AUTOMATED REPORTING SYSTEM - DAILY SUMMARY",
            "=" * 60,
            f"Report Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Report Date: {current_time.strftime('%Y-%m-%d')}",
            "",
            "EXECUTION SUMMARY",
            "-" * 20,
            f"Total Runs: {stats.get('total_runs', 0)}",
            f"Successful Runs: {stats.get('successes', 0)}",
            f"Failed Runs: {stats.get('failures', 0)}",
            f"Success Rate: {success_rate:.2f}%",
            f"Last Run: {stats.get('last_run', 'Never')}",
            "",
        ]
        
        
        if success_rate >= 95:
            status = "EXCELLENT"
        elif success_rate >= 80:
            status = "GOOD"
        elif success_rate >= 60:
            status = "FAIR"
        else:
            status = "NEEDS ATTENTION"
        
        report_lines.extend([
            "PERFORMANCE ASSESSMENT",
            "-" * 22,
            f"Overall Status: {status}",
            "",
        ])
        
        
        if stats.get('failures', 0) > 0:
            report_lines.extend([
                "ERROR ANALYSIS",
                "-" * 14,
            ])
            
            
            if error_analysis['error_types']:
                report_lines.append("Error Types:")
                for error_type, count in error_analysis['error_types'].items():
                    report_lines.append(f"  - {error_type}: {count} occurrences")
                report_lines.append("")
            
            
            if error_analysis['error_contexts']:
                report_lines.append("Error Contexts:")
                for context, count in error_analysis['error_contexts'].items():
                    if context != 'Unknown':
                        report_lines.append(f"  - {context}: {count} occurrences")
                report_lines.append("")
            
            
            recent_errors = stats.get('error_details', [])[-3:]  
            if recent_errors:
                report_lines.extend([
                    "RECENT ERRORS (Last 3)",
                    "-" * 21,
                ])
                
                for i, error in enumerate(recent_errors, 1):
                    if isinstance(error, dict):
                        timestamp = error.get('timestamp', 'Unknown')
                        error_type = error.get('error_type', 'Unknown')
                        message = error.get('error_message', 'No message')
                        
                        report_lines.extend([
                            f"{i}. {timestamp}",
                            f"   Type: {error_type}",
                            f"   Message: {message}",
                            ""
                        ])
        
        
        report_lines.extend([
            "RECOMMENDATIONS",
            "-" * 15,
        ])
        
        if success_rate >= 95:
            report_lines.append("✓ System is performing excellently. Continue monitoring.")
        elif success_rate >= 80:
            report_lines.append("• System is performing well. Monitor for any degradation.")
        elif success_rate >= 60:
            report_lines.append("⚠ System performance is fair. Consider investigating errors.")
        else:
            report_lines.append("⚠ System needs attention. Immediate investigation recommended.")
        
        if stats.get('failures', 0) > 0:
            report_lines.append("• Review error logs for detailed troubleshooting information.")
        
        report_lines.extend([
            "",
            "=" * 60,
            "End of Report",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def _save_report(self, content):
        """Save the report to file"""
        try:
            
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            report_file = self.reports_dir / f"daily_report_{current_date}.txt"
            
            
            generic_report = self.reports_dir / "report.txt"
            
            
            with open(report_file, 'w') as f:
                f.write(content)
            
            with open(generic_report, 'w') as f:
                f.write(content)
            
            self.logger.info(f"Report saved to {report_file} and {generic_report}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            return False
    
    def generate_json_report(self):
        """Generate a JSON version of the report for programmatic access"""
        stats = self.load_statistics()
        
        if not stats:
            return False
        
        success_rate = self.calculate_success_rate(stats)
        error_analysis = self.analyze_error_patterns(stats.get('error_details', []))
        
        json_report = {
            'report_metadata': {
                'generated_at': datetime.datetime.now().isoformat(),
                'report_date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'report_type': 'daily_summary'
            },
            'execution_summary': {
                'total_runs': stats.get('total_runs', 0),
                'successful_runs': stats.get('successes', 0),
                'failed_runs': stats.get('failures', 0),
                'success_rate_percent': round(success_rate, 2),
                'last_run': stats.get('last_run')
            },
            'error_analysis': error_analysis,
            'performance_status': self._get_performance_status(success_rate),
            'recommendations': self._get_recommendations(success_rate, stats.get('failures', 0))
        }
        
        try:
            json_file = self.reports_dir / "daily_report.json"
            with open(json_file, 'w') as f:
                json.dump(json_report, f, indent=2)
            
            self.logger.info(f"JSON report saved to {json_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON report: {e}")
            return False
    
    def _get_performance_status(self, success_rate):
        """Get performance status based on success rate"""
        if success_rate >= 95:
            return "EXCELLENT"
        elif success_rate >= 80:
            return "GOOD"
        elif success_rate >= 60:
            return "FAIR"
        else:
            return "NEEDS_ATTENTION"
    
    def _get_recommendations(self, success_rate, failure_count):
        """Get recommendations based on performance"""
        recommendations = []
        
        if success_rate >= 95:
            recommendations.append("System is performing excellently. Continue monitoring.")
        elif success_rate >= 80:
            recommendations.append("System is performing well. Monitor for any degradation.")
        elif success_rate >= 60:
            recommendations.append("System performance is fair. Consider investigating errors.")
        else:
            recommendations.append("System needs attention. Immediate investigation recommended.")
        
        if failure_count > 0:
            recommendations.append("Review error logs for detailed troubleshooting information.")
        
        return recommendations

def main():
    """Main function for standalone report generation"""
    base_dir = Path.home() / "automated_reporting_lab"
    generator = ReportGenerator(base_dir)
    
    print("Generating daily summary report...")
    
    
    if generator.generate_daily_report():
        print("✓ Text report generated successfully")
    else:
        print("✗ Failed to generate text report")
    
    
    if generator.generate_json_report():
        print("✓ JSON report generated successfully")
    else:
        print("✗ Failed to generate JSON report")

if __name__ == "__main__":
    main()
