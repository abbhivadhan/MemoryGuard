"""
Model Management API Example

Demonstrates how to use the Model Management API endpoints to:
1. List all registered models
2. List versions for a specific model
3. Promote a model to production
4. Get production model information
5. Compare model versions
6. View deployment history
"""
import requests
import json
from typing import Dict, List

# API base URL
BASE_URL = "http://localhost:8000"


def list_all_models() -> List[Dict]:
    """
    List all registered models in the registry
    
    GET /api/v1/models
    """
    print("\n" + "="*60)
    print("1. Listing All Registered Models")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/models")
    response.raise_for_status()
    
    models = response.json()
    
    print(f"\nFound {len(models)} models in registry:\n")
    for model in models:
        print(f"Model: {model['model_name']}")
        print(f"  Total Versions: {model['total_versions']}")
        print(f"  Production Version: {model['production_version']}")
        print(f"  Latest Version: {model['latest_version']}")
        print()
    
    return models


def list_model_versions(model_name: str, limit: int = 10) -> List[Dict]:
    """
    List all versions for a specific model
    
    GET /api/v1/models/{model_name}/versions
    """
    print("\n" + "="*60)
    print(f"2. Listing Versions for Model: {model_name}")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/models/{model_name}/versions",
        params={"limit": limit}
    )
    response.raise_for_status()
    
    versions = response.json()
    
    print(f"\nFound {len(versions)} versions:\n")
    for version in versions:
        print(f"Version: {version['version_id']}")
        print(f"  Type: {version['model_type']}")
        print(f"  Status: {version['status']}")
        print(f"  Created: {version['created_at']}")
        print(f"  ROC-AUC: {version['roc_auc']:.4f}" if version['roc_auc'] else "  ROC-AUC: N/A")
        print(f"  Accuracy: {version['accuracy']:.4f}" if version['accuracy'] else "  Accuracy: N/A")
        print(f"  Dataset: {version['dataset_version']}")
        print()
    
    return versions


def get_production_model(model_name: str) -> Dict:
    """
    Get the currently deployed production model
    
    GET /api/v1/models/{model_name}/production
    """
    print("\n" + "="*60)
    print(f"3. Getting Production Model: {model_name}")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/models/{model_name}/production")
    response.raise_for_status()
    
    production_model = response.json()
    
    print(f"\nProduction Model Information:")
    print(f"  Version: {production_model['version_id']}")
    print(f"  Type: {production_model['model_type']}")
    print(f"  Deployed: {production_model['deployed_at']}")
    print(f"  Dataset: {production_model['dataset_version']}")
    print(f"\n  Metrics:")
    for metric, value in production_model['metrics'].items():
        if value is not None:
            print(f"    {metric}: {value:.4f}")
    print(f"\n  Artifact Path: {production_model['artifact_path']}")
    
    return production_model


def promote_model_to_production(model_name: str, version_id: str, user_id: str = "system") -> Dict:
    """
    Promote a model version to production
    
    POST /api/v1/models/{model_name}/promote/{version_id}
    """
    print("\n" + "="*60)
    print(f"4. Promoting Model to Production")
    print("="*60)
    print(f"  Model: {model_name}")
    print(f"  Version: {version_id}")
    print(f"  User: {user_id}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/models/{model_name}/promote/{version_id}",
        json={"user_id": user_id}
    )
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✓ {result['message']}")
    if result['previous_production']:
        print(f"  Previous production version: {result['previous_production']}")
    
    return result


def compare_model_versions(model_name: str, metric: str = "roc_auc") -> Dict:
    """
    Compare metrics across model versions
    
    GET /api/v1/models/{model_name}/compare
    """
    print("\n" + "="*60)
    print(f"5. Comparing Model Versions by {metric}")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/models/{model_name}/compare",
        params={"metric": metric}
    )
    response.raise_for_status()
    
    comparison = response.json()
    
    print(f"\nModel: {comparison['model_name']}")
    print(f"Sorted by: {comparison['comparison_metric']}\n")
    
    for i, version in enumerate(comparison['versions'][:5], 1):  # Top 5
        print(f"{i}. Version: {version['version_id']}")
        print(f"   Status: {version['status']}")
        print(f"   {metric}: {version['metrics'].get(metric, 'N/A')}")
        print(f"   Created: {version['created_at']}")
        print()
    
    return comparison


def get_deployment_history(model_name: str, limit: int = 5) -> Dict:
    """
    Get deployment history for a model
    
    GET /api/v1/models/{model_name}/deployment-history
    """
    print("\n" + "="*60)
    print(f"6. Deployment History for {model_name}")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/models/{model_name}/deployment-history",
        params={"limit": limit}
    )
    response.raise_for_status()
    
    history = response.json()
    
    print(f"\nTotal Deployments: {history['deployment_count']}\n")
    
    for i, deployment in enumerate(history['deployments'], 1):
        print(f"{i}. Timestamp: {deployment['timestamp']}")
        print(f"   Version: {deployment['version_id']}")
        print(f"   Previous: {deployment['previous_version']}")
        print(f"   User: {deployment['user_id']}")
        print(f"   Success: {deployment['success']}")
        print()
    
    return history


def get_registry_statistics() -> Dict:
    """
    Get overall registry statistics
    
    GET /api/v1/models/statistics/registry
    """
    print("\n" + "="*60)
    print("7. Registry Statistics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/models/statistics/registry")
    response.raise_for_status()
    
    data = response.json()
    stats = data['registry_statistics']
    
    print(f"\nRegistry Overview:")
    print(f"  Total Models: {stats['total_models']}")
    print(f"  Total Versions: {stats['total_versions']}")
    print(f"  Production Models: {stats['production_models']}")
    print(f"  Archived Models: {stats['archived_models']}")
    
    print(f"\n  Average Production Metrics:")
    for metric, value in stats['average_production_metrics'].items():
        print(f"    {metric}: {value:.4f}")
    
    print(f"\n  Timestamp: {data['timestamp']}")
    
    return data


def main():
    """
    Main example workflow
    """
    print("\n" + "="*60)
    print("MODEL MANAGEMENT API EXAMPLE")
    print("="*60)
    print("\nThis example demonstrates the Model Management API endpoints.")
    print("Make sure the API server is running on http://localhost:8000")
    
    try:
        # 1. List all models
        models = list_all_models()
        
        if not models:
            print("\n⚠ No models found in registry.")
            print("Please train and register some models first.")
            return
        
        # Use the first model for examples
        model_name = models[0]['model_name']
        
        # 2. List versions for the model
        versions = list_model_versions(model_name, limit=10)
        
        # 3. Get production model (if exists)
        try:
            production_model = get_production_model(model_name)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"\n⚠ No production model found for {model_name}")
                production_model = None
            else:
                raise
        
        # 4. Compare versions
        if len(versions) > 1:
            comparison = compare_model_versions(model_name, metric="roc_auc")
        
        # 5. Get deployment history
        history = get_deployment_history(model_name, limit=5)
        
        # 6. Get registry statistics
        stats = get_registry_statistics()
        
        # 7. Example: Promote a model (commented out to avoid changing state)
        # if versions and not production_model:
        #     latest_version = versions[0]['version_id']
        #     result = promote_model_to_production(
        #         model_name=model_name,
        #         version_id=latest_version,
        #         user_id="example_user"
        #     )
        
        print("\n" + "="*60)
        print("✓ Example completed successfully!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server.")
        print("Please make sure the server is running:")
        print("  python -m ml_pipeline.api.main")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
