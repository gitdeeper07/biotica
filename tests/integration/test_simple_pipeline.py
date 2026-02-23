"""Simple pipeline integration test."""

import pytest
import numpy as np
from biotica import BIOTICACore
from biotica.ibr.composite import IBRComposite

class TestSimplePipeline:
    """Test simple pipeline."""
    
    def test_basic_workflow(self):
        """Test basic workflow."""
        # Initialize
        core = BIOTICACore()
        
        # Compute one parameter
        vca = core.compute_vca(ndvi=0.75, lai=5.0, gpp=1500)
        assert 0 <= vca.value <= 1
        assert vca.uncertainty > 0
        
        # Create IBR with one parameter
        ibr = IBRComposite()
        ibr.set_parameter('VCA', vca.value)
        
        # Compute (will have warnings but should work)
        result = ibr.compute(validate=False)
        assert result.score > 0
        assert result.plot_id is None
    
    def test_full_parameters(self):
        """Test with all parameters."""
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
        
        ibr = IBRComposite(plot_id="test_001")
        ibr.set_parameters(params)
        result = ibr.compute()
        
        assert result.plot_id == "test_001"
        assert result.score > 0
        assert result.classification is not None
        assert len(result.contributions) == 9
