"""
Example usage of Monitoring API endpoints

Demonstrates all three monitoring endpoints:
1. GET /api/v1/monitoring/drift - Drift detection results
2. GET /api/v1/monitoring/performance - Performance monitoring
3. POST /api/v1/monitoring/trigger-retrain - Manual retraining trigger

Requirements validated:
- 10.2: Detect statistical drift using Kolmogorov-Smirnov tests
- 10.3: Calculate Population Stability Index (PSI) for all features
- 10.5: Track prediction accuracy on recent data
- 11.2: Trigger retraining when data drift is detected
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"


def example_drift_detection():
    """
    Example: Get drift detection results
    
    Endpoint: GET /api/v1/monitoring/drift
    Requirements: 10.2, 10.3
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Drift Detection")
    print("="*80)
    
    # Request drift detection results
    params = {
        "model_name": "random_forest",
        "days": 7  # Last 7 days
    }
    
    print(f"\nRequest: GET {BASE_URL}/api/v1/monitoring/drift")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/monitoring/drift",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✓ Success! Drift detection results:")
            print(f"  - Timestamp: {data['timestamp']}")
            print(f"  - Model: {data['model_name']}")
            print(f"  - Dataset: {data['dataset_name']}")
            print(f"  - Drift Detected: {data['drift_detected']}")
            print(f"  - Retraining Recommended: {data['retraining_recommended']}")
            print(f"  - Features with Drift: {len(data['features_with_drift'])}")
            
            if data['features_with_drift']:
                print(f"\n  Features with drift:")
                for feature in data['features_with_drift'][:5]:  # Show first 5
                    print(f"    - {feature}")
            
            # Show feature-level results
            print(f"\n  Feature-level results (showing first 3):")
            for feature_result in data['feature_results'][:3]:
                print(f"    - {feature_result['feature_name']}:")
                print(f"      KS drift: {feature_result['ks_drift_detected']}")
                print(f"      PSI score: {feature_result['psi_score']:.4f}")
                print(f"      PSI drift: {feature_result['psi_drift_detected']}")
            
            # Show summary
            print(f"\n  Summary:")
            for key, value in data['summary'].items():
                print(f"    - {key}: {value}")
            
            return data
            
        elif response.status_code == 404:
            print(f"\n⚠ No drift reports found: {response.json()['detail']}")
            return None
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"  {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Make sure the API server is running")
        print("  Start with: uvicorn ml_pipeline.api.main:app --reload")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def example_performance_monitoring():
    """
    Example: Get performance monitoring results
    
    Endpoint: GET /api/v1/monitoring/performance
    Requirements: 10.5
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Performance Monitoring")
    print("="*80)
    
    # Request performance monitoring
    params = {
        "model_name": "random_forest",
        "days": 30  # Last 30 days
    }
    
    print(f"\nRequest: GET {BASE_URL}/api/v1/monitoring/performance")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/monitoring/performance",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✓ Success! Performance monitoring results:")
            print(f"  - Model: {data['model_name']}")
            print(f"  - Performance Degraded: {data['performance_degraded']}")
            
            # Current performance
            if data['current_performance']:
                current = data['current_performance']
                metrics = current['metrics']
                print(f"\n  Current Performance ({current['timestamp']}):")
                print(f"    - Accuracy: {metrics['accuracy']:.4f}")
                print(f"    - Precision: {metrics['precision']:.4f}")
                print(f"    - Recall: {metrics['recall']:.4f}")
                print(f"    - F1 Score: {metrics['f1_score']:.4f}")
                if metrics.get('roc_auc'):
                    print(f"    - ROC AUC: {metrics['roc_auc']:.4f}")
                print(f"    - Samples: {metrics['n_samples']}")
            
            # Baseline comparison
            if data['baseline_metrics']:
                print(f"\n  Baseline Metrics:")
                for metric, value in data['baseline_metrics'].items():
                    print(f"    - {metric}: {value:.4f}")
            
            # Degradation details
            if data['degradation_details']:
                details = data['degradation_details']
                print(f"\n  ⚠ Performance Degradation Detected:")
                print(f"    - Metric: {details['metric']}")
                print(f"    - Baseline: {details['baseline_value']:.4f}")
                print(f"    - Recent Average: {details['recent_average']:.4f}")
                print(f"    - Change: {details['relative_change']*100:.2f}%")
            
            # Summary
            print(f"\n  Summary:")
            for key, value in data['summary'].items():
                print(f"    - {key}: {value}")
            
            # Recent history
            print(f"\n  Recent History ({len(data['recent_history'])} entries):")
            for entry in data['recent_history'][:3]:  # Show first 3
                print(f"    - {entry['timestamp']}: accuracy={entry['metrics']['accuracy']:.4f}")
            
            return data
            
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"  {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Make sure the API server is running")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def example_trigger_retraining():
    """
    Example: Trigger manual retraining
    
    Endpoint: POST /api/v1/monitoring/trigger-retrain
    Requirements: 11.2
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Manual Retraining Trigger")
    print("="*80)
    
    # Request body
    request_data = {
        "reason": "Manual retraining triggered from example script",
        "user_id": "data_scientist_1",
        "dataset_name": "train_features",
        "target_column": "diagnosis"
    }
    
    print(f"\nRequest: POST {BASE_URL}/api/v1/monitoring/trigger-retrain")
    print(f"Body: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/monitoring/trigger-retrain",
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✓ Success! Retraining triggered:")
            print(f"  - Job ID: {data['job_id']}")
            print(f"  - Triggered At: {data['triggered_at']}")
            print(f"  - Estimated Completion: {data['estimated_completion_time']}")
            print(f"  - Message: {data['message']}")
            
            print("\n  The retraining job is now running in the background.")
            print("  It will:")
            print("    1. Load new training data")
            print("    2. Retrain all models (RF, XGBoost, Neural Network)")
            print("    3. Evaluate new models against production")
            print("    4. Automatically promote if 5% better")
            
            return data
            
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"  {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Make sure the API server is running")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def example_additional_endpoints():
    """
    Example: Additional monitoring endpoints
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Additional Monitoring Endpoints")
    print("="*80)
    
    # Drift history
    print("\n1. Drift History:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/monitoring/drift/history",
            params={"model_name": "random_forest", "days": 30}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Retrieved {data['n_reports']} drift reports")
        else:
            print(f"   ⚠ Status: {response.status_code}")
    except:
        print("   ✗ Connection error")
    
    # Performance trend
    print("\n2. Performance Trend:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/monitoring/performance/trend",
            params={"model_name": "random_forest", "metric": "accuracy", "days": 30}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Trend direction: {data['trend_direction']}")
            print(f"   ✓ Trend change: {data['trend_change']:.4f}")
        else:
            print(f"   ⚠ Status: {response.status_code}")
    except:
        print("   ✗ Connection error")
    
    # Health check
    print("\n3. Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/health-check")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {data['status']}")
            print(f"   ✓ Components:")
            for component, status in data['components'].items():
                print(f"      - {component}: {status}")
        else:
            print(f"   ⚠ Status: {response.status_code}")
    except:
        print("   ✗ Connection error")


def main():
    """
    Run all monitoring API examples
    """
    print("\n" + "="*80)
    print("MONITORING API EXAMPLES")
    print("="*80)
    print("\nThis script demonstrates all monitoring API endpoints:")
    print("1. Drift Detection (GET /api/v1/monitoring/drift)")
    print("2. Performance Monitoring (GET /api/v1/monitoring/performance)")
    print("3. Manual Retraining Trigger (POST /api/v1/monitoring/trigger-retrain)")
    print("\nMake sure the API server is running:")
    print("  uvicorn ml_pipeline.api.main:app --reload")
    
    # Run examples
    example_drift_detection()
    example_performance_monitoring()
    example_trigger_retraining()
    example_additional_endpoints()
    
    print("\n" + "="*80)
    print("EXAMPLES COMPLETE")
    print("="*80)
    print("\nAll monitoring endpoints have been demonstrated.")
    print("\nFor more information, see:")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Requirements: .kiro/specs/biomedical-data-ml-pipeline/requirements.md")
    print("  - Design: .kiro/specs/biomedical-data-ml-pipeline/design.md")


if __name__ == "__main__":
    main()
