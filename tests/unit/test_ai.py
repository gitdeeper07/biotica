"""Unit tests for AI classification module."""

import pytest
import numpy as np
from biotica.ai.mi_cnn import MICNNClassifier, ClassificationResult

# Skip tests if PyTorch not available
pytest.importorskip("torch")

class TestMICNNClassifier:
    """Test MI-CNN classifier."""
    
    def test_initialization(self):
        """Test classifier initialization."""
        model = MICNNClassifier(
            n_classes=22,
            spectral_channels=200,
            temporal_features=12,
            climate_features=19,
            terrain_features=8
        )
        
        assert model is not None
        assert hasattr(model, 'spectral_stream')
        assert hasattr(model, 'temporal_stream')
        assert hasattr(model, 'climate_stream')
        assert hasattr(model, 'terrain_stream')
    
    def test_forward_pass(self):
        """Test forward pass."""
        import torch
        
        model = MICNNClassifier()
        batch_size = 4
        
        # Create dummy inputs
        spectral = torch.randn(batch_size, 1, 200)
        temporal = torch.randn(batch_size, 12, 12)
        climate = torch.randn(batch_size, 19)
        terrain = torch.randn(batch_size, 8)
        
        # Forward pass
        logits, attn_weights = model(spectral, temporal, climate, terrain)
        
        assert logits.shape == (batch_size, 22)
        assert attn_weights is not None
    
    def test_forward_with_missing_inputs(self):
        """Test forward pass with missing inputs."""
        import torch
        
        model = MICNNClassifier()
        batch_size = 4
        
        # Only spectral input
        spectral = torch.randn(batch_size, 1, 200)
        logits, _ = model(spectral=spectral)
        assert logits.shape == (batch_size, 22)
        
        # Only temporal input
        temporal = torch.randn(batch_size, 12, 12)
        logits, _ = model(temporal=temporal)
        assert logits.shape == (batch_size, 22)
    
    def test_predict(self):
        """Test prediction."""
        model = MICNNClassifier()
        
        # Create dummy inputs
        spectral = np.random.randn(200)
        temporal = np.random.randn(12, 12)
        
        biome_names = [f"Biome_{i}" for i in range(22)]
        
        result = model.predict(
            spectral=spectral,
            temporal=temporal,
            biome_names=biome_names
        )
        
        assert isinstance(result, ClassificationResult)
        assert result.biome in biome_names
        assert 0 <= result.confidence <= 1
        assert len(result.probabilities) == 22
    
    def test_save_load(self, temp_dir):
        """Test model saving and loading."""
        model = MICNNClassifier()
        
        # Save model
        save_path = temp_dir / "test_model"
        model.save_pretrained(save_path)
        
        # Check files exist
        assert (save_path / "config.json").exists()
        assert (save_path / "weights.pt").exists()
        
        # Load model
        loaded_model = MICNNClassifier.from_pretrained(save_path)
        assert loaded_model is not None

class TestClassificationResult:
    """Test ClassificationResult dataclass."""
    
    def test_creation(self):
        """Test ClassificationResult creation."""
        result = ClassificationResult(
            biome="Tropical Rainforest",
            confidence=0.95,
            probabilities={"Tropical Rainforest": 0.95, "Savanna": 0.05},
            attention_maps=np.random.randn(10, 10)
        )
        
        assert result.biome == "Tropical Rainforest"
        assert result.confidence == 0.95
        assert len(result.probabilities) == 2
        assert result.attention_maps.shape == (10, 10)
