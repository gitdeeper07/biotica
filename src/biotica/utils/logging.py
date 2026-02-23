"""Logging utilities for BIOTICA."""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import json
import traceback

class BIOTICALogger:
    """Custom logger for BIOTICA with file and console output."""
    
    # Log levels
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # Colors for console output
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def __init__(self,
                 name: str = 'biotica',
                 log_dir: Optional[Union[str, Path]] = None,
                 level: str = 'INFO',
                 console_output: bool = True,
                 file_output: bool = True,
                 json_format: bool = False):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Enable console output
            file_output: Enable file output
            json_format: Use JSON format for logs
        """
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path.cwd() / 'logs'
        self.level = self.LEVELS.get(level.upper(), logging.INFO)
        self.json_format = json_format
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.handlers = []  # Remove existing handlers
        
        # Create formatters
        if json_format:
            self.console_formatter = self._json_formatter
            self.file_formatter = self._json_formatter
        else:
            self.console_formatter = self._color_formatter
            self.file_formatter = self._standard_formatter
        
        # Add handlers
        if console_output:
            self._add_console_handler()
        
        if file_output:
            self._add_file_handler()
    
    def _color_formatter(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        
        # Format message
        if record.exc_info:
            exc_text = traceback.format_exception(*record.exc_info)
            msg = f"{record.getMessage()}\n{''.join(exc_text)}"
        else:
            msg = record.getMessage()
        
        return (f"{color}[{timestamp}] {levelname:8} - {self.name} - {msg}"
                f"{self.COLORS['RESET']}")
    
    def _standard_formatter(self, record: logging.LogRecord) -> str:
        """Standard log format."""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        if record.exc_info:
            exc_text = traceback.format_exception(*record.exc_info)
            msg = f"{record.getMessage()}\n{''.join(exc_text)}"
        else:
            msg = record.getMessage()
        
        return f"[{timestamp}] {record.levelname:8} - {self.name} - {msg}"
    
    def _json_formatter(self, record: logging.LogRecord) -> str:
        """JSON log format."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': self.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        if record.exc_info:
            log_entry['exception'] = traceback.format_exception(*record.exc_info)
        
        if hasattr(record, 'extra'):
            log_entry['extra'] = record.extra
        
        return json.dumps(log_entry)
    
    def _add_console_handler(self):
        """Add console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add file handler."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with date
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = self.log_dir / f"{self.name}_{date_str}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.level)
        
        if self.json_format:
            formatter = logging.Formatter(
                fmt='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(msg, *args, **kwargs)
    
    def log_execution_time(self, func):
        """Decorator to log function execution time."""
        import time
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                self.debug(f"{func.__name__} executed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                self.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
                raise
        
        return wrapper

class ProgressLogger:
    """Simple progress logger for long operations."""
    
    def __init__(self,
                 total: int,
                 description: str = "Progress",
                 logger: Optional[BIOTICALogger] = None,
                 log_interval: int = 10):
        """
        Initialize progress logger.
        
        Args:
            total: Total number of items
            description: Description of operation
            logger: BIOTICALogger instance
            log_interval: Log progress every N percent
        """
        self.total = total
        self.description = description
        self.logger = logger or BIOTICALogger(level='INFO', console_output=True, file_output=False)
        self.log_interval = log_interval
        self.current = 0
        self.last_percent = 0
        
        self.logger.info(f"{description}: Starting (0/{total})")
    
    def update(self, n: int = 1):
        """Update progress by n items."""
        self.current += n
        percent = int(100 * self.current / self.total)
        
        if percent >= self.last_percent + self.log_interval or self.current == self.total:
            self.logger.info(f"{self.description}: {percent}% ({self.current}/{self.total})")
            self.last_percent = percent
    
    def finish(self):
        """Mark progress as complete."""
        self.logger.info(f"{self.description}: Complete ({self.current}/{self.total})")

def setup_logging(config: Optional[Dict[str, Any]] = None) -> BIOTICALogger:
    """
    Set up logging for BIOTICA.
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        Configured logger
    """
    if config is None:
        config = {}
    
    return BIOTICALogger(
        name=config.get('name', 'biotica'),
        log_dir=config.get('log_dir'),
        level=config.get('level', 'INFO'),
        console_output=config.get('console_output', True),
        file_output=config.get('file_output', True),
        json_format=config.get('json_format', False)
    )

# Example usage
if __name__ == "__main__":
    # Basic logging
    logger = BIOTICALogger(name='test', level='DEBUG')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # JSON logging
    json_logger = BIOTICALogger(name='json_test', json_format=True, file_output=False)
    json_logger.info("This is a JSON formatted message")
    
    # Progress logging
    progress = ProgressLogger(total=100, description="Processing data")
    for i in range(100):
        # Do work
        import time
        time.sleep(0.01)
        progress.update()
    progress.finish()
    
    # Decorator example
    @logger.log_execution_time
    def slow_function():
        import time
        time.sleep(1)
        return "Done"
    
    result = slow_function()
    print(f"Function returned: {result}")
