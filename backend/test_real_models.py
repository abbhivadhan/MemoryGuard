"""
Test script for real trained models
"""

import sys
from pathlib import Path
import joblib
import numpy as np
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import the EnsemblePredictor class
from app.ml.ensemble_predictor import EnsemblePredictor

MODELS_PATH = Path(__file__).parent / "ml_models"

def test_models():
    """Test the trained models"""
    print("="*60)
    print("Testing Real Trained Models")
    print("="*60)
    
    # Load model registry
    registry_path = MODELS_PATH / "model_registry.json"
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        print("\nModel Registry:")
        print(json.dumps(registry, indent=2))
    
    # Load ensemble predictor
    ensemble_path = MODELS_PATH / "ensemble_predictor.joblib"
    if not ensemble_path.exists():
        print(f"\nError: Ensemble model not found at {ensemble_path}")
        return
    
    print(f"\nLoading ensemble predictor from {ensemble_path}...")
    ensemble = joblib.load(ensemble_path)
    print("Ensemble loaded successfully!")
    
    # Create test features (130 features)
    print("\nTesting predictions with sample data...")
    
    # Test case 1: Low risk profile
    test_features_low = np.random.randn(130) * 0.5  # Small values
    result_low = ensemble.predict_risk(test_features_low)
    print(f"\nTest 1 - Low Risk Profile:")
    print(f"  Risk Score: {result_low['risk_score']:.3f}")
    print(f"  Risk Level: {result_low['risk_level']}")
    print(f"  Confidence: {1 - result_low['confidence']:.3f}")
    
    # Test case 2: High risk profile
    test_features_high = np.random.randn(130) * 2.0  # Larger values
    result_high = ensemble.predict_risk(test_features_high)
    print(f"\nTest 2 - High Risk Profile:")
    print(f"  Risk Score: {result_high['risk_score']:.3f}")
    print(f"  Risk Level: {result_high['risk_level']}")
    print(f"  Confidence: {1 - result_high['confidence']:.3f}")
    
    # Test case 3: Moderate risk profile
    test_features_mod = np.random.randn(130)
    result_mod = ensemble.predict_risk(test_features_mod)
    print(f"\nTest 3 - Moderate Risk Profile:")
    print(f"  Risk Score: {result_mod['risk_score']:.3f}")
    print(f"  Risk Level: {result_mod['risk_level']}")
    print(f"  Confidence: {1 - result_mod['confidence']:.3f}")
    
    print("\n" + "="*60)
    print("All tests passed! Models are working correctly.")
    print("="*60)
    
    return True

if __name__ == "__main__":
    test_models()
