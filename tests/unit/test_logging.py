"""Unit tests for logging utilities."""

import pytest
from biotica.utils.logging import BIOTICALogger

class TestLogger:
    """Test logger."""
    
    def test_create_logger(self):
        """Test logger creation."""
        logger = BIOTICALogger(name="test")
        assert logger is not None
        assert logger.name == "test"
    
    def test_log_levels(self):
        """Test different log levels."""
        logger = BIOTICALogger(name="test", level="DEBUG", file_output=False)
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        # No assertion, just checking no exceptions
    
    def test_log_with_file(self, temp_dir):
        """Test logging to file."""
        log_dir = temp_dir / "logs"
        logger = BIOTICALogger(name="test", log_dir=log_dir, file_output=True)
        logger.info("Test message")
        # Check log file exists
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
