"""
Enhanced Error Handling Module
Provides comprehensive error handling and recovery mechanisms
"""

import logging
import traceback
import functools
import time
from datetime import datetime
from pathlib import Path

class ErrorHandler:
    def __init__(self, log_file_path):
        self.log_file_path = Path(log_file_path)
        self.setup_error_logging()
        
    def setup_error_logging(self):
        """Set up dedicated error logging"""
        
        self.error_logger = logging.getLogger('error_handler')
        self.error_logger.setLevel(logging.ERROR)
        
        
        error_handler = logging.FileHandler(self.log_file_path)
        error_handler.setLevel(logging.ERROR)
        
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        
        if not self.error_logger.handlers:
            self.error_logger.addHandler(error_handler)
    
    def log_error(self, error, context=""):
        """Log error with full traceback and context"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.error_logger.error(f"ERROR DETAILS: {error_info}")
        
        return error_info
    
    def retry_on_failure(self, max_retries=3, delay=1):
        """Decorator for retrying failed operations"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            self.log_error(
                                e, 
                                f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay} seconds"
                            )
                            time.sleep(delay)
                        else:
                            self.log_error(
                                e, 
                                f"All {max_retries + 1} attempts failed for {func.__name__}"
                            )
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def safe_execute(self, func, *args, **kwargs):
        """Safely execute a function with error handling"""
        try:
            return {
                'success': True,
                'result': func(*args, **kwargs),
                'error': None
            }
        except Exception as e:
            error_info = self.log_error(e, f"Safe execution of {func.__name__}")
            return {
                'success': False,
                'result': None,
                'error': error_info
            }
