"""Multi-Input CNN for ecosystem classification."""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import json
import warnings
import os
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. AI features disabled.")

@dataclass
class ClassificationResult:
    """Result from AI classifier."""
    biome: str
    confidence: float
    probabilities: Dict[str, float]
    attention_maps: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SpectralStream(nn.Module):
    """1D-CNN for hyperspectral data processing."""
    
    def __init__(self, input_channels: int = 200, n_classes: int = 22):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(64)
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        self.pool = nn.MaxPool1d(2)
        self.dropout = nn.Dropout(0.3)
        
        # Adaptive pooling to handle variable input lengths
        self.adaptive_pool = nn.AdaptiveAvgPool1d(16)
        
        # Calculate features after convolutions
        self.fc1 = nn.Linear(128 * 16, 256)
        self.fc2 = nn.Linear(256, 128)
        
    def forward(self, x):
        # x shape: (batch, 1, n_bands)
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = F.relu(self.bn3(self.conv3(x)))
        
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        
        return x

class TemporalStream(nn.Module):
    """Process time-series vegetation indices."""
    
    def __init__(self, input_size: int = 12, hidden_size: int = 128, 
                 num_layers: int = 2, n_classes: int = 22):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers, 
                           batch_first=True, dropout=0.3, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, 64)  # *2 for bidirectional
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, x):
        # x shape: (batch, seq_len, features)
        lstm_out, (hidden, cell) = self.lstm(x)
        # Concatenate forward and backward hidden states
        hidden_combined = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        x = F.relu(self.fc(hidden_combined))
        x = self.dropout(x)
        return x

class ClimateStream(nn.Module):
    """Process climate variables."""
    
    def __init__(self, input_size: int = 19, hidden_sizes: List[int] = [64, 32]):
        super().__init__()
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        self.mlp = nn.Sequential(*layers)
        self.output_size = prev_size
        
    def forward(self, x):
        return self.mlp(x)

class TerrainStream(nn.Module):
    """Process terrain variables."""
    
    def __init__(self, input_size: int = 8, hidden_sizes: List[int] = [32, 16]):
        super().__init__()
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        self.mlp = nn.Sequential(*layers)
        self.output_size = prev_size
        
    def forward(self, x):
        return self.mlp(x)

class MICNNClassifier(nn.Module):
    """
    Multi-Input CNN for ecosystem classification.
    
    Architecture from paper Section 4.2:
    - Four parallel streams for different data types
    - Feature fusion layer
    - Final classification layer
    """
    
    def __init__(self, 
                 n_classes: int = 22,
                 spectral_channels: int = 200,
                 temporal_features: int = 12,
                 climate_features: int = 19,
                 terrain_features: int = 8,
                 fusion_size: int = 256):
        """
        Initialize MI-CNN classifier.
        
        Args:
            n_classes: Number of biome classes
            spectral_channels: Number of spectral bands
            temporal_features: Number of temporal features
            climate_features: Number of climate variables
            terrain_features: Number of terrain variables
            fusion_size: Size of fusion layer
        """
        super().__init__()
        
        # Initialize streams
        self.spectral_stream = SpectralStream(spectral_channels, n_classes)
        self.temporal_stream = TemporalStream(temporal_features, n_classes=n_classes)
        self.climate_stream = ClimateStream(climate_features)
        self.terrain_stream = TerrainStream(terrain_features)
        
        # Calculate total features after streams
        spectral_out = 128
        temporal_out = 64
        climate_out = 32
        terrain_out = 16
        total_features = spectral_out + temporal_out + climate_out + terrain_out
        
        # Fusion layers
        self.fusion1 = nn.Linear(total_features, fusion_size)
        self.fusion2 = nn.Linear(fusion_size, 128)
        self.fusion_dropout = nn.Dropout(0.4)
        
        # Classification head
        self.classifier = nn.Linear(128, n_classes)
        
        # Attention mechanism for interpretability
        self.attention = nn.MultiheadAttention(embed_dim=128, num_heads=4, batch_first=True)
        
    def forward(self, 
                spectral: Optional[torch.Tensor] = None,
                temporal: Optional[torch.Tensor] = None,
                climate: Optional[torch.Tensor] = None,
                terrain: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            spectral: Spectral data tensor (batch, 1, n_bands)
            temporal: Temporal data tensor (batch, seq_len, features)
            climate: Climate data tensor (batch, climate_features)
            terrain: Terrain data tensor (batch, terrain_features)
            
        Returns:
            Classification logits
        """
        features = []
        
        # Process each available stream
        if spectral is not None:
            spectral_feat = self.spectral_stream(spectral)
            features.append(spectral_feat)
        
        if temporal is not None:
            temporal_feat = self.temporal_stream(temporal)
            features.append(temporal_feat)
        
        if climate is not None:
            climate_feat = self.climate_stream(climate)
            features.append(climate_feat)
        
        if terrain is not None:
            terrain_feat = self.terrain_stream(terrain)
            features.append(terrain_feat)
        
        # Concatenate all features
        if not features:
            raise ValueError("At least one input stream must be provided")
        
        combined = torch.cat(features, dim=1)
        
        # Fusion layers
        x = F.relu(self.fusion1(combined))
        x = self.fusion_dropout(x)
        x = F.relu(self.fusion2(x))
        
        # Self-attention for interpretability
        x = x.unsqueeze(1)  # Add sequence dimension
        attn_out, attn_weights = self.attention(x, x, x)
        x = attn_out.squeeze(1)
        
        # Classification
        logits = self.classifier(x)
        
        return logits, attn_weights
    
    def predict(self, 
                spectral: Optional[np.ndarray] = None,
                temporal: Optional[np.ndarray] = None,
                climate: Optional[np.ndarray] = None,
                terrain: Optional[np.ndarray] = None,
                biome_names: Optional[List[str]] = None) -> ClassificationResult:
        """
        Make prediction for a single sample.
        
        Args:
            spectral: Spectral data
            temporal: Temporal data
            climate: Climate data
            terrain: Terrain data
            biome_names: List of biome names
            
        Returns:
            ClassificationResult object
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for prediction")
        
        self.eval()
        
        # Convert to tensors
        tensors = {}
        if spectral is not None:
            tensors['spectral'] = torch.FloatTensor(spectral).unsqueeze(0).unsqueeze(0)
        if temporal is not None:
            tensors['temporal'] = torch.FloatTensor(temporal).unsqueeze(0)
        if climate is not None:
            tensors['climate'] = torch.FloatTensor(climate).unsqueeze(0)
        if terrain is not None:
            tensors['terrain'] = torch.FloatTensor(terrain).unsqueeze(0)
        
        with torch.no_grad():
            logits, attn_weights = self.forward(**tensors)
            probs = F.softmax(logits, dim=1)
            
        probs_np = probs.squeeze().cpu().numpy()
        pred_class = int(probs.argmax(dim=1))
        confidence = float(probs.max())
        
        # Default biome names if not provided
        if biome_names is None:
            biome_names = [f"Biome_{i}" for i in range(len(probs_np))]
        
        probabilities = {
            name: float(prob)
            for name, prob in zip(biome_names, probs_np)
        }
        
        # Get attention maps for interpretability
        attention_maps = attn_weights.squeeze().cpu().numpy() if attn_weights is not None else None
        
        return ClassificationResult(
            biome=biome_names[pred_class],
            confidence=confidence,
            probabilities=probabilities,
            attention_maps=attention_maps,
            metadata={
                'pred_class': pred_class,
                'input_shapes': {
                    'spectral': spectral.shape if spectral is not None else None,
                    'temporal': temporal.shape if temporal is not None else None,
                    'climate': climate.shape if climate is not None else None,
                    'terrain': terrain.shape if terrain is not None else None
                }
            }
        )
    
    @classmethod
    def from_pretrained(cls, model_path: Union[str, Path], **kwargs):
        """Load pretrained model."""
        model_path = Path(model_path)
        
        # Load configuration
        config_path = model_path / 'config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = kwargs
        
        # Create model
        model = cls(**config)
        
        # Load weights
        weights_path = model_path / 'weights.pt'
        if weights_path.exists():
            state_dict = torch.load(weights_path, map_location='cpu')
            model.load_state_dict(state_dict)
        
        model.eval()
        return model
    
    def save_pretrained(self, save_path: Union[str, Path]):
        """Save model and configuration."""
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config = {
            'n_classes': self.classifier.out_features,
            'spectral_channels': self.spectral_stream.conv1.in_channels,
            'temporal_features': self.temporal_stream.lstm.input_size,
            'climate_features': self.climate_stream.mlp[0].in_features,
            'terrain_features': self.terrain_stream.mlp[0].in_features,
        }
        
        with open(save_path / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save weights
        torch.save(self.state_dict(), save_path / 'weights.pt')

class Trainer:
    """Trainer for MI-CNN model."""
    
    def __init__(self, 
                 model: MICNNClassifier,
                 learning_rate: float = 0.001,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch in train_loader:
            self.optimizer.zero_grad()
            
            # Move data to device
            spectral = batch['spectral'].to(self.device) if 'spectral' in batch else None
            temporal = batch['temporal'].to(self.device) if 'temporal' in batch else None
            climate = batch['climate'].to(self.device) if 'climate' in batch else None
            terrain = batch['terrain'].to(self.device) if 'terrain' in batch else None
            labels = batch['label'].to(self.device)
            
            # Forward pass
            logits, _ = self.model(spectral, temporal, climate, terrain)
            loss = self.criterion(logits, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = logits.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        
        return {
            'loss': total_loss / len(train_loader),
            'accuracy': 100. * correct / total
        }
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                spectral = batch['spectral'].to(self.device) if 'spectral' in batch else None
                temporal = batch['temporal'].to(self.device) if 'temporal' in batch else None
                climate = batch['climate'].to(self.device) if 'climate' in batch else None
                terrain = batch['terrain'].to(self.device) if 'terrain' in batch else None
                labels = batch['label'].to(self.device)
                
                logits, _ = self.model(spectral, temporal, climate, terrain)
                loss = self.criterion(logits, labels)
                
                total_loss += loss.item()
                _, predicted = logits.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        
        return {
            'loss': total_loss / len(val_loader),
            'accuracy': 100. * correct / total
        }
    
    def fit(self, 
            train_loader: DataLoader,
            val_loader: DataLoader,
            epochs: int = 100,
            early_stopping_patience: int = 10):
        """Train model."""
        best_val_loss = float('inf')
        patience_counter = 0
        history = []
        
        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader)
            
            # Validate
            val_metrics = self.validate(val_loader)
            
            # Update learning rate
            self.scheduler.step(val_metrics['loss'])
            
            # Logging
            print(f"Epoch {epoch+1}/{epochs}: "
                  f"Train Loss: {train_metrics['loss']:.4f}, "
                  f"Train Acc: {train_metrics['accuracy']:.2f}%, "
                  f"Val Loss: {val_metrics['loss']:.4f}, "
                  f"Val Acc: {val_metrics['accuracy']:.2f}%")
            
            history.append({
                'epoch': epoch,
                'train_loss': train_metrics['loss'],
                'train_acc': train_metrics['accuracy'],
                'val_loss': val_metrics['loss'],
                'val_acc': val_metrics['accuracy']
            })
            
            # Early stopping
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), 'best_model.pt')
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
        
        return history
