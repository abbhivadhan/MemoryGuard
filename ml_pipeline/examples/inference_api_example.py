"""
Example usage of the ML Pipeline Inference API

Demonstrates:
- Making predictions with confidence intervals
- Getting SHAP explanations
- Generating progression forecasts
- Batch predictions
"""
import requests
import json
from typing import Dict, Any


# API base URL (adjust as needed)
BASE_URL = "http://localhost:8000"


def make_prediction(features: Dict[str, Any], include_explanation: bool = True):
    """
    Make a single prediction
    
    Args:
        features: Dictionary of feature values
        include_explanation: Whether to include SHAP explanation
    """
    print("\n" + "="*60)
    print("MAKING PREDICTION")
    print("="*60)
    
    payload = {
        "features": features,
        "model_name": "ensemble",
        "include_explanation": include_explanation,
        "include_confidence": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nPrediction ID: {result['prediction_id']}")
        print(f"Prediction: {result['prediction']} ({'AD' if result['prediction'] == 1 else 'Normal'})")
        print(f"Probability: {result['probability']:.3f}")
        print(f"Risk Category: {result['risk_category']}")
        print(f"Model: {result['model_name']} v{result['model_version']}")
        print(f"Generation Time: {result['generation_time']:.3f}s")
        
        if result.get('confidence_interval'):
            ci = result['confidence_interval']
            print(f"\nConfidence Interval (95%):")
            print(f"  Lower: {ci['lower']:.3f}")
            print(f"  Upper: {ci['upper']:.3f}")
        
        if result.get('explanation') and 'top_features' in result['explanation']:
            print(f"\nTop Contributing Features:")
            for feat in result['explanation']['top_features'][:5]:
                print(f"  {feat['feature']}: {feat['shap_value']:.3f} (value: {feat['feature_value']:.2f})")
        
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def make_batch_prediction(features_list: list):
    """
    Make batch predictions
    
    Args:
        features_list: List of feature dictionaries
    """
    print("\n" + "="*60)
    print("MAKING BATCH PREDICTION")
    print("="*60)
    
    payload = {
        "features_list": features_list,
        "model_name": "ensemble",
        "include_explanation": False,  # Faster without explanations
        "include_confidence": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/predict/batch",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nBatch Size: {result['total_count']}")
        print(f"Total Generation Time: {result['generation_time']:.3f}s")
        print(f"Average Time per Prediction: {result['generation_time']/result['total_count']:.3f}s")
        
        print(f"\nPredictions:")
        for i, pred in enumerate(result['predictions'][:5]):  # Show first 5
            print(f"  {i+1}. Prediction: {pred['prediction']}, "
                  f"Probability: {pred['probability']:.3f}, "
                  f"Risk: {pred['risk_category']}")
        
        if len(result['predictions']) > 5:
            print(f"  ... and {len(result['predictions']) - 5} more")
        
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def generate_forecast(patient_id: str, patient_history: list):
    """
    Generate progression forecast
    
    Args:
        patient_id: Patient identifier
        patient_history: List of historical feature dictionaries
    """
    print("\n" + "="*60)
    print("GENERATING PROGRESSION FORECAST")
    print("="*60)
    
    payload = {
        "patient_id": patient_id,
        "patient_history": patient_history
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/forecast",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nPatient ID: {result['patient_id']}")
        print(f"Generation Time: {result['generation_time']:.3f}s")
        
        print(f"\nForecasted MMSE Scores:")
        for horizon, score in result['forecasts'].items():
            uncertainty = result['uncertainty'][horizon]
            print(f"  {horizon}: {score:.1f} ± {uncertainty:.1f}")
        
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def check_cache_status():
    """Check model cache status"""
    print("\n" + "="*60)
    print("CHECKING CACHE STATUS")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/models/cache/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nCached Models: {result['cached_models']}")
        print(f"Cached Interpretability Systems: {result['cached_interpretability_systems']}")
        print(f"Cached Forecasters: {result['cached_forecasters']}")
        print(f"Total Cached: {result['total_cached']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None


def main():
    """Run example API calls"""
    
    # Example 1: Single prediction with explanation
    print("\n" + "#"*60)
    print("# EXAMPLE 1: Single Prediction with SHAP Explanation")
    print("#"*60)
    
    features = {
        "mmse_score": 24.0,
        "moca_score": 22.0,
        "cdr_global": 0.5,
        "csf_ab42": 450.0,
        "csf_tau": 350.0,
        "csf_ptau": 65.0,
        "hippocampus_volume": 6500.0,
        "entorhinal_cortex_thickness": 2.8,
        "ventricular_volume": 45000.0,
        "whole_brain_volume": 1100000.0,
        "age": 72,
        "sex": 1,
        "education_years": 16,
        "apoe_e4_count": 1
    }
    
    prediction_result = make_prediction(features, include_explanation=True)
    
    # Example 2: Batch predictions
    print("\n" + "#"*60)
    print("# EXAMPLE 2: Batch Predictions")
    print("#"*60)
    
    batch_features = [
        {
            "mmse_score": 28.0,
            "age": 65,
            "csf_ab42": 600.0,
            "hippocampus_volume": 7500.0,
            "apoe_e4_count": 0
        },
        {
            "mmse_score": 22.0,
            "age": 75,
            "csf_ab42": 400.0,
            "hippocampus_volume": 6000.0,
            "apoe_e4_count": 2
        },
        {
            "mmse_score": 26.0,
            "age": 70,
            "csf_ab42": 500.0,
            "hippocampus_volume": 7000.0,
            "apoe_e4_count": 1
        }
    ]
    
    batch_result = make_batch_prediction(batch_features)
    
    # Example 3: Progression forecast
    print("\n" + "#"*60)
    print("# EXAMPLE 3: Progression Forecast")
    print("#"*60)
    
    patient_history = [
        {"mmse_score": 28.0, "age": 70, "csf_ab42": 500.0, "hippocampus_volume": 7200.0},
        {"mmse_score": 26.0, "age": 71, "csf_ab42": 480.0, "hippocampus_volume": 7000.0},
        {"mmse_score": 24.0, "age": 72, "csf_ab42": 450.0, "hippocampus_volume": 6800.0},
        {"mmse_score": 22.0, "age": 73, "csf_ab42": 420.0, "hippocampus_volume": 6500.0}
    ]
    
    forecast_result = generate_forecast("PATIENT_001", patient_history)
    
    # Example 4: Check cache status
    print("\n" + "#"*60)
    print("# EXAMPLE 4: Cache Status")
    print("#"*60)
    
    cache_status = check_cache_status()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✓ API is running at {BASE_URL}")
            main()
        else:
            print(f"✗ API returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to API at {BASE_URL}")
        print("  Make sure the API is running:")
        print("  python ml_pipeline/api/main.py")
