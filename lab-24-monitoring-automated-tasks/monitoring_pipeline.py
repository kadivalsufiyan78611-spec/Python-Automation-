"""
End-to-End Monitoring & Reporting Pipeline
A comprehensive data processing pipeline with monitoring and error handling
"""

import csv
import json
import logging
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Any

class MonitoringPipeline:
    def __init__(self):
        self.setup_logging()
        self.pipeline_steps = []
        self.max_retries = 3
        self.data_file = "data/processed_data.csv"
        self.report_file = "reports/pipeline_report.csv"
        
    def setup_logging(self):
        """Configure logging for the pipeline"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/pipeline.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_step(self, step_name: str, status: str, message: str = ""):
        """Log pipeline step with status"""
        timestamp = datetime.now().isoformat()
        step_info = {
            'step_name': step_name,
            'status': status,
            'timestamp': timestamp,
            'message': message
        }
        self.pipeline_steps.append(step_info)
        
        if status == 'SUCCESS':
            self.logger.info(f"Step '{step_name}' completed successfully. {message}")
        elif status == 'FAILED':
            self.logger.error(f"Step '{step_name}' failed. {message}")
        elif status == 'RETRY':
            self.logger.warning(f"Step '{step_name}' retry attempt. {message}")
        else:
            self.logger.info(f"Step '{step_name}' status: {status}. {message}")
    
    def fetch_data(self) -> List[Dict[str, Any]]:
        """Simulate data fetching from external source"""
        step_name = "fetch_data"
        self.log_step(step_name, "STARTED", "Beginning data fetch operation")
        
        try:
            
            time.sleep(1)  
            
            
            sample_data = []
            for i in range(100):
                record = {
                    'id': i + 1,
                    'name': f'Item_{i+1}',
                    'value': random.randint(10, 1000),
                    'category': random.choice(['A', 'B', 'C', 'D']),
                    'timestamp': datetime.now().isoformat()
                }
                sample_data.append(record)
            
            
            if random.random() < 0.1:
                raise Exception("Network timeout during data fetch")
            
            self.log_step(step_name, "SUCCESS", f"Fetched {len(sample_data)} records")
            return sample_data
            
        except Exception as e:
            self.log_step(step_name, "FAILED", str(e))
            raise
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process the fetched data"""
        step_name = "process_data"
        self.log_step(step_name, "STARTED", f"Processing {len(raw_data)} records")
        
        try:
            processed_data = []
            
            for record in raw_data:
                
                processed_record = {
                    'id': record['id'],
                    'name': record['name'].upper(),
                    'value': record['value'],
                    'category': record['category'],
                    'processed_value': record['value'] * 1.1,  
                    'status': 'PROCESSED',
                    'timestamp': record['timestamp']
                }
                processed_data.append(processed_record)
            
            
            if random.random() < 0.05:
                raise Exception("Data processing error: Invalid data format")
            
            self.log_step(step_name, "SUCCESS", f"Processed {len(processed_data)} records")
            return processed_data
            
        except Exception as e:
            self.log_step(step_name, "FAILED", str(e))
            raise
    
    def store_data(self, processed_data: List[Dict[str, Any]]) -> bool:
        """Store processed data to CSV file"""
        step_name = "store_data"
        self.log_step(step_name, "STARTED", f"Storing {len(processed_data)} records to CSV")
        
        try:
            
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            
            with open(self.data_file, 'w', newline='') as csvfile:
                if processed_data:
                    fieldnames = processed_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(processed_data)
            
            
            if random.random() < 0.03:
                raise Exception("Disk space insufficient for data storage")
            
            self.log_step(step_name, "SUCCESS", f"Stored {len(processed_data)} records to {self.data_file}")
            return True
            
        except Exception as e:
            self.log_step(step_name, "FAILED", str(e))
            raise
    
    def execute_step_with_retry(self, step_function, *args, **kwargs):
        """Execute a step with retry logic"""
        step_name = step_function.__name__
        
        for attempt in range(1, self.max_retries + 1):
            try:
                if attempt > 1:
                    self.log_step(step_name, "RETRY", f"Attempt {attempt}/{self.max_retries}")
                    time.sleep(2 ** (attempt - 1))  
                
                result = step_function(*args, **kwargs)
                return result
                
            except Exception as e:
                if attempt == self.max_retries:
                    self.log_step(step_name, "FAILED", f"Max retries exceeded: {str(e)}")
                    raise
                else:
                    self.log_step(step_name, "RETRY", f"Attempt {attempt} failed: {str(e)}")
    
    def generate_report(self):
        """Generate pipeline execution report"""
        step_name = "generate_report"
        self.log_step(step_name, "STARTED", "Generating pipeline execution report")
        
        try:
            
            os.makedirs(os.path.dirname(self.report_file), exist_ok=True)
            
            
            with open(self.report_file, 'w', newline='') as csvfile:
                fieldnames = ['step_name', 'status', 'timestamp', 'message']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for step in self.pipeline_steps:
                    writer.writerow({
                        'step_name': step['step_name'],
                        'status': step['status'],
                        'timestamp': step['timestamp'],
                        'message': step.get('message', '')
                    })
            
            self.log_step(step_name, "SUCCESS", f"Report generated: {self.report_file}")
            
        except Exception as e:
            self.log_step(step_name, "FAILED", str(e))
            raise
    
    def run_pipeline(self):
        """Execute the complete pipeline"""
        pipeline_start = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("STARTING MONITORING PIPELINE EXECUTION")
        self.logger.info("=" * 60)
        
        try:
            
            raw_data = self.execute_step_with_retry(self.fetch_data)
            
            
            processed_data = self.execute_step_with_retry(self.process_data, raw_data)
            
            
            self.execute_step_with_retry(self.store_data, processed_data)
            
            
            self.generate_report()
            
            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()
            
            self.logger.info("=" * 60)
            self.logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {duration:.2f} seconds")
            self.logger.info("=" * 60)
            
        except Exception as e:
            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()
            
            self.logger.error("=" * 60)
            self.logger.error(f"PIPELINE FAILED after {duration:.2f} seconds: {str(e)}")
            self.logger.error("=" * 60)
            
            
            try:
                self.generate_report()
            except:
                pass
            
            raise

def main():
    """Main execution function"""
    pipeline = MonitoringPipeline()
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
