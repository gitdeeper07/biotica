"""Simple workflow integration tests."""

import pytest
import numpy as np
from biotica import BIOTICACore
from biotica.ibr.composite import IBRComposite

class TestSimpleWorkflow:
    """Test basic workflow."""
    
    def test_parameter_to_ibr(self):
        """Test computing IBR from parameters."""
        core = BIOTICACore()
        
        params = {
            'VCA': 0.85,
            'MDI': 0.78,
            'PTS': 0.82,
            'HFI': 0.71,
            'BNC': 0.68,
            'SGH': 0.73,
            'AES': 0.88,
            'TMI': 0.79,
            'RRC': 0.65
        }
        
        result = core.compute_ibr(params)
        assert 'score' in result
        assert 0 <= result['score'] <= 1
    
    def test_ibr_composite(self):
        """Test IBR composite calculator."""
        ibr = IBRComposite(plot_id="test_001")
        
        ibr.set_parameter('VCA', 0.85)
        ibr.set_parameter('MDI', 0.78)
        
        result = ibr.compute()
        assert result.plot_id == "test_001"
        assert result.score > 0
