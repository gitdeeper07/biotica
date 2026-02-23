"""Bayesian weight determination for IBR parameters.

Implements the 3-stage Bayesian weight estimation described in the paper.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import warnings
import logging

logger = logging.getLogger(__name__)

# Optional imports for Bayesian methods
try:
    import pymc3 as pm
    import arviz as az
    BAYESIAN_AVAILABLE = True
except ImportError:
    BAYESIAN_AVAILABLE = False
    warnings.warn("PyMC3 not available. Using fallback weight estimation methods.")

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available. PCA methods disabled.")

@dataclass
class WeightResult:
    """Results from weight estimation."""
    weights: Dict[str, float]
    uncertainties: Dict[str, float] = field(default_factory=dict)
    posterior_samples: Optional[np.ndarray] = None
    convergence: bool = True
    method: str = "fixed"
    n_effective_samples: Optional[int] = None
    rhat: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BayesianWeights:
    """
    Bayesian weight determination for IBR parameters.
    
    Implements the 3-stage Bayesian PCA weight estimation
    described in the paper (Section 3.2, Equations 13-17).
    
    Stages:
    1. Prior specification from literature values
    2. Bayesian updating with training data
    3. Posterior predictive validation
    """
    
    # Default weights from paper Table 2 (based on 3412 plots)
    DEFAULT_WEIGHTS = {
        'VCA': 0.20,  # Vegetative Carbon Absorption
        'MDI': 0.15,  # Microbial Diversity Index
        'PTS': 0.12,  # Phenological Time Shift
        'HFI': 0.11,  # Hydrological Flux Index
        'BNC': 0.10,  # Biogeochemical Nutrient Cycle
        'SGH': 0.09,  # Species Genetic Heterogeneity
        'AES': 0.08,  # Anthropogenic Encroachment Score
        'TMI': 0.08,  # Trophic Metadata Integration
        'RRC': 0.07,  # Regenerative Recovery Capacity
    }
    
    # Prior uncertainties from paper (Table S4)
    PRIOR_UNCERTAINTIES = {
        'VCA': 0.03,
        'MDI': 0.04,
        'PTS': 0.05,
        'HFI': 0.04,
        'BNC': 0.03,
        'SGH': 0.05,
        'AES': 0.06,
        'TMI': 0.05,
        'RRC': 0.06
    }
    
    def __init__(self, 
                 n_chains: int = 4,
                 n_samples: int = 2000,
                 n_tune: int = 1000,
                 target_accept: float = 0.95,
                 random_seed: int = 42):
        """
        Initialize Bayesian weight estimator.
        
        Args:
            n_chains: Number of MCMC chains
            n_samples: Number of posterior samples per chain
            n_tune: Number of tuning samples
            target_accept: Target acceptance rate for HMC
            random_seed: Random seed for reproducibility
        """
        self.n_chains = n_chains
        self.n_samples = n_samples
        self.n_tune = n_tune
        self.target_accept = target_accept
        self.random_seed = random_seed
        self.result = None
        self.trace = None
        self.model = None
        
    def estimate_from_data(self, 
                          X: np.ndarray,
                          y: np.ndarray,
                          parameter_names: List[str],
                          sample_weight: Optional[np.ndarray] = None,
                          use_pca_init: bool = True) -> WeightResult:
        """
        Estimate weights using Bayesian regression.
        
        Implements Equation (14) from paper:
        w ~ N(μ_prior, σ_prior²)
        y ~ N(Xw, σ²)
        
        Args:
            X: Parameter matrix (n_samples, n_parameters)
            y: Target IBR scores (n_samples,)
            parameter_names: List of parameter names
            sample_weight: Optional sample weights
            use_pca_init: Whether to initialize with PCA
            
        Returns:
            WeightResult object with estimated weights
        """
        if not BAYESIAN_AVAILABLE:
            logger.warning("PyMC3 not available. Using fallback weights.")
            return self._fallback_weights(parameter_names)
        
        n_params = X.shape[1]
        n_samples = X.shape[0]
        
        # Validate input
        if len(parameter_names) != n_params:
            raise ValueError(f"Expected {n_params} parameter names, got {len(parameter_names)}")
        
        # Standardize X for better sampling
        X_scaled = (X - X.mean(axis=0)) / X.std(axis=0)
        y_scaled = (y - y.mean()) / y.std()
        
        # Get prior means from default weights
        prior_means = np.array([self.DEFAULT_WEIGHTS.get(name, 0.1) 
                               for name in parameter_names])
        
        # Get prior uncertainties
        prior_sds = np.array([self.PRIOR_UNCERTAINTIES.get(name, 0.05)
                             for name in parameter_names])
        
        # Optional PCA initialization
        init_vals = None
        if use_pca_init and SKLEARN_AVAILABLE:
            try:
                pca = PCA(n_components=1)
                pca.fit(X_scaled)
                init_vals = np.abs(pca.components_[0])
                init_vals = init_vals / init_vals.sum()  # Normalize
                logger.info(f"PCA initialization: {dict(zip(parameter_names, init_vals))}")
            except Exception as e:
                logger.warning(f"PCA initialization failed: {e}")
        
        with pm.Model() as model:
            self.model = model
            
            # Priors for weights - Equation (14)
            if init_vals is not None:
                # Use PCA as initial guess
                weights = pm.Normal('weights',
                                   mu=prior_means,
                                   sigma=prior_sds,
                                   shape=n_params,
                                   initval=init_vals)
            else:
                weights = pm.Normal('weights',
                                   mu=prior_means,
                                   sigma=prior_sds,
                                   shape=n_params)
            
            # Prior for noise - Equation (15)
            sigma = pm.HalfNormal('sigma', sigma=0.1)
            
            # Linear predictor - Equation (16)
            mu = pm.math.dot(X_scaled, weights)
            
            # Likelihood - Equation (17)
            if sample_weight is not None:
                # Weighted likelihood
                sigma_weighted = sigma / np.sqrt(sample_weight)
                y_obs = pm.Normal('y_obs',
                                 mu=mu,
                                 sigma=sigma_weighted,
                                 observed=y_scaled)
            else:
                y_obs = pm.Normal('y_obs',
                                 mu=mu,
                                 sigma=sigma,
                                 observed=y_scaled)
            
            # Sample from posterior
            logger.info(f"Sampling {self.n_chains} chains with {self.n_samples} samples each...")
            
            trace = pm.sample(
                draws=self.n_samples,
                tune=self.n_tune,
                chains=self.n_chains,
                target_accept=self.target_accept,
                random_seed=self.random_seed,
                return_inferencedata=True,
                progressbar=True
            )
            
            self.trace = trace
        
        # Extract results
        weight_samples = trace.posterior['weights'].values
        weight_samples = weight_samples.reshape(-1, n_params)
        
        weight_means = weight_samples.mean(axis=0)
        weight_stds = weight_samples.std(axis=0)
        
        # Calculate effective sample size and R-hat
        n_eff = az.ess(trace).to_array().values
        rhat = az.rhat(trace).to_array().values
        
        # Create dictionaries
        weights_dict = {
            name: float(weight_means[i])
            for i, name in enumerate(parameter_names)
        }
        
        uncertainties_dict = {
            name: float(weight_stds[i])
            for i, name in enumerate(parameter_names)
        }
        
        rhat_dict = {
            name: float(rhat[i]) if i < len(rhat) else 1.0
            for i, name in enumerate(parameter_names)
        }
        
        # Normalize to sum to 1 (post-processing)
        total = sum(weights_dict.values())
        weights_dict = {k: v/total for k, v in weights_dict.items()}
        
        # Check convergence
        max_rhat = max(rhat_dict.values()) if rhat_dict else 1.0
        converged = max_rhat < 1.1
        
        return WeightResult(
            weights=weights_dict,
            uncertainties=uncertainties_dict,
            posterior_samples=weight_samples,
            convergence=converged,
            method="bayesian",
            n_effective_samples=int(n_eff.mean()) if n_eff.size > 0 else None,
            rhat=rhat_dict,
            metadata={
                'n_samples': n_samples,
                'n_params': n_params,
                'n_chains': self.n_chains,
                'n_posterior_samples': weight_samples.shape[0],
                'max_rhat': float(max_rhat),
                'converged': converged
            }
        )
    
    def estimate_with_cv(self,
                        X: np.ndarray,
                        y: np.ndarray,
                        parameter_names: List[str],
                        n_folds: int = 5,
                        random_seed: Optional[int] = None) -> List[WeightResult]:
        """
        Cross-validated weight estimation.
        
        Args:
            X: Parameter matrix
            y: Target values
            parameter_names: Parameter names
            n_folds: Number of CV folds
            random_seed: Random seed
            
        Returns:
            List of WeightResult objects for each fold
        """
        from sklearn.model_selection import KFold
        
        if random_seed is None:
            random_seed = self.random_seed
        
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=random_seed)
        results = []
        
        for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
            logger.info(f"Processing fold {fold + 1}/{n_folds}")
            
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Estimate weights on training data
            result = self.estimate_from_data(
                X_train, y_train, parameter_names
            )
            
            # Add validation metadata
            y_pred = np.dot(X_val, np.array([result.weights[p] for p in parameter_names]))
            mse = np.mean((y_val - y_pred) ** 2)
            r2 = 1 - mse / np.var(y_val)
            
            result.metadata['fold'] = fold
            result.metadata['validation_mse'] = float(mse)
            result.metadata['validation_r2'] = float(r2)
            
            results.append(result)
        
        return results
    
    def _fallback_weights(self, parameter_names: List[str]) -> WeightResult:
        """Return default weights when Bayesian estimation unavailable."""
        weights = {
            name: self.DEFAULT_WEIGHTS.get(name, 0.1)
            for name in parameter_names
        }
        
        # Normalize to sum to 1
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        uncertainties = {
            name: self.PRIOR_UNCERTAINTIES.get(name, 0.05)
            for name in parameter_names
        }
        
        return WeightResult(
            weights=weights,
            uncertainties=uncertainties,
            convergence=True,
            method="fixed",
            metadata={'note': 'Using default weights from paper'}
        )
    
    @staticmethod
    def pca_weights(X: np.ndarray,
                   parameter_names: List[str],
                   n_components: int = 1) -> WeightResult:
        """
        PCA-based weight estimation.
        
        Uses principal component loadings as weights.
        Implements the PCA initialization described in paper.
        
        Args:
            X: Parameter matrix
            parameter_names: Parameter names
            n_components: Number of components to use
            
        Returns:
            WeightResult object
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for PCA weights")
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit PCA
        pca = PCA(n_components=n_components)
        pca.fit(X_scaled)
        
        if n_components == 1:
            # Use first component loadings
            loadings = pca.components_[0]
            weights_abs = np.abs(loadings)
            weights_norm = weights_abs / weights_abs.sum()
            
            weights_dict = {
                name: float(weights_norm[i])
                for i, name in enumerate(parameter_names)
            }
            
            uncertainties = {
                name: 0.1 for name in parameter_names
            }
            
            return WeightResult(
                weights=weights_dict,
                uncertainties=uncertainties,
                method="pca",
                metadata={
                    'explained_variance_ratio': float(pca.explained_variance_ratio_[0]),
                    'n_components': 1
                }
            )
        else:
            # Multiple components - weight by explained variance
            weights_dict = {}
            for i in range(n_components):
                comp_name = f"PC{i+1}"
                loadings = pca.components_[i]
                weights_abs = np.abs(loadings)
                weights_norm = weights_abs / weights_abs.sum()
                
                weights_dict[comp_name] = {
                    name: float(weights_norm[j])
                    for j, name in enumerate(parameter_names)
                }
            
            return WeightResult(
                weights={},  # Not a single set of weights
                method="pca_multi",
                metadata={
                    'components': weights_dict,
                    'explained_variance_ratios': pca.explained_variance_ratio_.tolist(),
                    'n_components': n_components
                }
            )
    
    def compare_models(self,
                      X: np.ndarray,
                      y: np.ndarray,
                      parameter_names: List[str],
                      model_names: List[str] = ['bayesian', 'pca', 'fixed']) -> Dict[str, Any]:
        """
        Compare different weight estimation methods.
        
        Args:
            X: Parameter matrix
            y: Target values
            parameter_names: Parameter names
            model_names: List of methods to compare
            
        Returns:
            Dictionary with comparison results
        """
        results = {}
        
        for method in model_names:
            if method == 'bayesian' and BAYESIAN_AVAILABLE:
                result = self.estimate_from_data(X, y, parameter_names)
                results['bayesian'] = result
            elif method == 'pca' and SKLEARN_AVAILABLE:
                result = self.pca_weights(X, parameter_names)
                results['pca'] = result
            elif method == 'fixed':
                result = self._fallback_weights(parameter_names)
                results['fixed'] = result
        
        # Calculate predictions and metrics
        metrics = {}
        for name, result in results.items():
            if result.weights:
                weights_array = np.array([result.weights[p] for p in parameter_names])
                y_pred = np.dot(X, weights_array)
                mse = np.mean((y - y_pred) ** 2)
                r2 = 1 - mse / np.var(y)
                
                metrics[name] = {
                    'mse': float(mse),
                    'rmse': float(np.sqrt(mse)),
                    'r2': float(r2)
                }
        
        return {
            'results': results,
            'metrics': metrics,
            'best_method': min(metrics.items(), key=lambda x: x[1]['mse'])[0]
        }
    
    def save_weights(self, filepath: Union[str, Path], result: WeightResult):
        """Save weight results to JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'weights': result.weights,
            'uncertainties': result.uncertainties,
            'method': result.method,
            'convergence': result.convergence,
            'metadata': result.metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Weights saved to {filepath}")
    
    def load_weights(self, filepath: Union[str, Path]) -> WeightResult:
        """Load weight results from JSON file."""
        filepath = Path(filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return WeightResult(
            weights=data['weights'],
            uncertainties=data.get('uncertainties', {}),
            method=data.get('method', 'loaded'),
            convergence=data.get('convergence', True),
            metadata=data.get('metadata', {})
        )

# Example usage
if __name__ == "__main__":
    # Generate synthetic data for testing
    np.random.seed(42)
    n_samples = 100
    n_params = 9
    param_names = list(BayesianWeights.DEFAULT_WEIGHTS.keys())
    
    # Simulate parameter values
    X = np.random.uniform(0.3, 0.9, (n_samples, n_params))
    
    # True weights (slightly modified from defaults)
    true_weights = np.array([0.18, 0.16, 0.13, 0.10, 0.11, 0.09, 0.08, 0.08, 0.07])
    y = np.dot(X, true_weights) + np.random.normal(0, 0.05, n_samples)
    
    # Initialize estimator
    estimator = BayesianWeights()
    
    # Estimate weights
    result = estimator.estimate_from_data(X, y, param_names)
    print("Estimated weights:")
    for name, weight in result.weights.items():
        print(f"  {name}: {weight:.3f} ± {result.uncertainties[name]:.3f}")
    
    print(f"\nConvergence: {result.convergence}")
    print(f"Method: {result.method}")
    
    # Compare methods
    comparison = estimator.compare_models(X, y, param_names)
    print("\nModel comparison:")
    for method, metrics in comparison['metrics'].items():
        print(f"  {method}: RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
    print(f"\nBest method: {comparison['best_method']}")
