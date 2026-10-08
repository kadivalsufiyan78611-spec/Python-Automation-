"""
Enhanced Automated Reporting Script with Advanced Error Handling
"""

import requests
import json
import logging
import datetime
import os
import sys
import time
from pathlib import Path
from error_handler import ErrorHandler

class EnhancedAutomatedReporter:
    def __init__(self):
        self.base_dir = Path.home() / "automated_reporting_lab"
        self.logs_dir = self.base_dir / "logs"
        self.reports_dir = self.base_dir / "reports"
        
        
        self.error_handler = ErrorHandler(self.logs_dir / "errors.log")
        
        self.setup_logging()
        self.stats = {
            'total_runs': 0,
            'successes': 0,
            'failures': 0,
            'last_run': None,
            'error_details': []
        }
        
    def setup_logging(self):
        """Configure comprehensive logging"""
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        
        log_file = self.logs_dir / "application.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('automated_reporter')
    
    @property
    def error_handler_retry(self):
        """Get retry decorator from error handler"""
        return self.error_handler.retry_on_failure(max_retries=3, delay=2)
    
    @error_handler_retry
    def fetch_api_data(self):
        """Fetch data from API with retry mechanism"""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        
        self.logger.info(f"Fetching data from: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        self.logger.info("API data fetched successfully")
        
        return {
            'success': True,
            'data': data,
            'timestamp': datetime.datetime.now().isoformat(),
            'status_code': response.status_code
        }
    
    def load_existing_stats(self):
        """Load existing statistics with error handling"""
        stats_file = self.reports_dir / "stats.json"
        
        result = self.error_handler.safe_execute(
            self._load_stats_file, stats_file
        )
        
        if result['success'] and result['result']:
            self.stats.update(result['result'])
            self.logger.info("Existing statistics loaded")
        else:
            self.logger.warning("Could not load existing statistics, using defaults")
    
    def _load_stats_file(self, stats_file):
        """Helper method to load stats file"""
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_stats(self):
        """Save statistics with error handling"""
        stats_file = self.reports_dir / "stats.json"
        
        
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        result = self.error_handler.safe_execute(
            self._save_stats_file, stats_file, self.stats
        )
        
        if result['success']:
            self.logger.info("Statistics saved successfully")
        else:
            self.logger.error("Failed to save statistics")
    
    def _save_stats_file(self, stats_file, stats_data):
        """Helper method to save stats file"""
        with open(stats_file, 'w') as f:
            json.dump(stats_data, f, indent=2)
    
    def update_stats(self, success, error_info=None):
        """Update execution statistics"""
        self.stats['total_runs'] += 1
        self.stats['last_run'] = datetime.datetime.now().isoformat()
        
        if success:
            self.stats['successes'] += 1
        else:
            self.stats['failures'] += 1
            if error_info:
                self.stats['error_details'].append(error_info)
                
                self.stats['error_details'] = self.stats['error_details'][-10:]
    
    def run_scheduled_task(self):
        """Execute the main scheduled task with comprehensive error handling"""
        self.logger.info("=== Starting Enhanced Scheduled Task ===")
        
        try:
            
            self.load_existing_stats()
            
            
            result = self.fetch_api_data()
            
            
            self.update_stats(True)
            
            
            self.save_stats()
            
            self.logger.info("=== Scheduled Task Completed Successfully ===")
            return True
            
        except Exception as e:
            
            error_info = self.error_handler.log_error(e, "Main scheduled task execution")
            
            
            self.update_stats(False, error_info)
            
            
            self.save_stats()
            
            self.logger.error("=== Scheduled Task Failed ===")
            return False

def main():
    """Main execution function"""
    print("Starting Enhanced Automated Reporting Script...")
    
    try:
        reporter = EnhancedAutomatedReporter()
        success = reporter.run_scheduled_task()
        
        if success:
            print("Task completed successfully!")
            sys.exit(0)
        else:
            print("Task completed with errors. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
