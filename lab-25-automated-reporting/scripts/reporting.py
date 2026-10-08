"""
Automated Reporting Script with Error Handling
This script fetches data from an API, handles errors, and generates reports
"""

import requests
import json
import logging
import datetime
import os
import sys
import time
from pathlib import Path

class AutomatedReporter:
    def __init__(self):
        self.base_dir = Path.home() / "automated_reporting_lab"
        self.logs_dir = self.base_dir / "logs"
        self.reports_dir = self.base_dir / "reports"
        self.setup_logging()
        self.stats = {
            'total_runs': 0,
            'successes': 0,
            'failures': 0,
            'last_run': None
        }
        
    def setup_logging(self):
        """Configure logging for the application"""
        log_file = self.logs_dir / "errors.log"
        
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def fetch_api_data(self):
        """Fetch data from a public API with error handling"""
        try:
            
            url = "https://jsonplaceholder.typicode.com/posts/1"
            
            self.logger.info(f"Attempting to fetch data from: {url}")
            
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()  
            
            data = response.json()
            self.logger.info("Successfully fetched API data")
            
            return {
                'success': True,
                'data': data,
                'timestamp': datetime.datetime.now().isoformat(),
                'status_code': response.status_code
            }
            
        except requests.exceptions.Timeout:
            error_msg = "API request timed out"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to API"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error occurred: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except json.JSONDecodeError:
            error_msg = "Failed to decode JSON response"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error occurred: {e}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def update_stats(self, success):
        """Update execution statistics"""
        self.stats['total_runs'] += 1
        self.stats['last_run'] = datetime.datetime.now().isoformat()
        
        if success:
            self.stats['successes'] += 1
        else:
            self.stats['failures'] += 1
    
    def load_existing_stats(self):
        """Load existing statistics from file"""
        stats_file = self.reports_dir / "stats.json"
        
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                    self.logger.info("Loaded existing statistics")
        except Exception as e:
            self.logger.error(f"Failed to load existing stats: {e}")
    
    def save_stats(self):
        """Save current statistics to file"""
        stats_file = self.reports_dir / "stats.json"
        
        try:
            
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
                
            self.logger.info("Statistics saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")
    
    def run_scheduled_task(self):
        """Execute the main scheduled task"""
        self.logger.info("Starting scheduled task execution")
        
        try:
            
            self.load_existing_stats()
            
            
            result = self.fetch_api_data()
            
            
            self.update_stats(result['success'])
            
            
            self.save_stats()
            
            if result['success']:
                self.logger.info("Scheduled task completed successfully")
                return True
            else:
                self.logger.error("Scheduled task failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Critical error in scheduled task: {e}")
            self.update_stats(False)
            self.save_stats()
            return False

def main():
    """Main execution function"""
    print("Starting Automated Reporting Script...")
    
    reporter = AutomatedReporter()
    success = reporter.run_scheduled_task()
    
    if success:
        print("Task completed successfully!")
        sys.exit(0)
    else:
        print("Task completed with errors. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
