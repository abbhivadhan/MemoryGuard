"""
Example usage of Data Ingestion API

Demonstrates:
1. Uploading data (CSV format)
2. Listing available data sources
3. Getting quality reports
4. Extracting features
5. Retrieving patient features
6. Getting feature statistics
"""
import requests
import pandas as pd
import io
import json
from pathlib import Path


# API base URL
BASE_URL = "http://localhost:8000/api/v1/data"


def create_sample_data():
    """Create sample biomedical data for testing"""
    data = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'age': [65, 70, 75, 68, 72],
        'sex': [1, 0, 1, 0, 1],
        'education_years': [16, 12, 18, 14, 16],
        'mmse_score': [28, 24, 20, 26, 22],
        'moca_score': [27, 22, 18, 25, 21],
        'cdr_global': [0.0, 0.5, 1.0, 0.5, 0.5],
        'csf_ab42': [500, 450, 400, 480, 430],
        'csf_tau': [300, 350, 400, 320, 360],
        'csf_ptau': [50, 60, 70, 55, 65],
        'hippocampus_volume': [7000, 6500, 6000, 6800, 6300],
        'apoe_e4_count': [0, 1, 2, 1, 1]
    })
    return data


def example_1_upload_data():
    """Example 1: Upload CSV data"""
    print("\n" + "="*60)
    print("Example 1: Upload Data")
    print("="*60)
    
    # Create sample data
    data = create_sample_data()
    
    # Convert to CSV
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Upload
    files = {'file': ('sample_data.csv', csv_content, 'text/csv')}
    params = {'format': 'csv', 'validate': True}
    
    response = requests.post(f"{BASE_URL}/ingest", files=files, params=params)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Upload successful!")
        print(f"  Dataset ID: {result['dataset_id']}")
        print(f"  Records: {result['num_records']}")
        print(f"  Columns: {result['num_columns']}")
        print(f"  Validation: {result['validation_status']}")
        
        if result.get('validation_summary'):
            print(f"  PHI Detected: {result['validation_summary']['phi_detected']}")
            print(f"  Completeness: {result['validation_summary']['completeness']:.2%}")
        
        return result['dataset_id']
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(f"  Error: {response.json()}")
        return None


def example_2_list_sources():
    """Example 2: List available data sources"""
    print("\n" + "="*60)
    print("Example 2: List Data Sources")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/sources")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {result['total_sources']} data sources:")
        
        for source in result['sources']:
            print(f"\n  {source['source_name']}:")
            print(f"    Type: {source['source_type']}")
            print(f"    Description: {source['description']}")
            print(f"    Data Types: {', '.join(source['available_data_types'][:3])}...")
    else:
        print(f"✗ Failed to list sources: {response.status_code}")


def example_3_quality_report(dataset_id):
    """Example 3: Get quality report"""
    print("\n" + "="*60)
    print("Example 3: Get Quality Report")
    print("="*60)
    
    if not dataset_id:
        print("✗ No dataset ID provided")
        return
    
    response = requests.get(f"{BASE_URL}/quality/{dataset_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Quality report generated:")
        print(f"  Dataset: {result['dataset_id']}")
        print(f"  Validation Passed: {result['validation_passed']}")
        
        report = result['report']
        if 'phi_detection' in report:
            print(f"  PHI Detected: {report['phi_detection']['phi_detected']}")
        
        if 'completeness' in report:
            comp = report['completeness']
            if 'validation' in comp:
                print(f"  Overall Completeness: {comp['validation']['overall_completeness']:.2%}")
        
        if 'duplicates' in report:
            dup = report['duplicates']
            print(f"  Duplicate Rows: {dup.get('duplicate_rows', 0)}")
    else:
        print(f"✗ Failed to get quality report: {response.status_code}")


def example_4_extract_features(dataset_id):
    """Example 4: Extract features"""
    print("\n" + "="*60)
    print("Example 4: Extract Features")
    print("="*60)
    
    if not dataset_id:
        print("✗ No dataset ID provided")
        return
    
    payload = {
        "dataset_id": dataset_id,
        "patient_id_col": "patient_id",
        "include_temporal": False,
        "save_to_store": False
    }
    
    response = requests.post(f"{BASE_URL}/features/extract", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Feature extraction completed:")
        print(f"  Dataset: {result['dataset_id']}")
        print(f"  Features: {result['num_features']}")
        print(f"  Records: {result['num_records']}")
        print(f"  Processing Time: {result['processing_time']:.2f}s")
        print(f"  Saved to Store: {result['saved_to_store']}")
        
        print(f"\n  Sample Features:")
        for feat in result['feature_names'][:10]:
            print(f"    - {feat}")
        if len(result['feature_names']) > 10:
            print(f"    ... and {len(result['feature_names']) - 10} more")
    else:
        print(f"✗ Feature extraction failed: {response.status_code}")
        print(f"  Error: {response.json()}")


def example_5_get_patient_features():
    """Example 5: Get patient features"""
    print("\n" + "="*60)
    print("Example 5: Get Patient Features")
    print("="*60)
    
    patient_id = "P001"
    response = requests.get(f"{BASE_URL}/features/{patient_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retrieved features for patient {result['patient_id']}:")
        print(f"  Total Features: {result['num_features']}")
        print(f"  Last Updated: {result['last_updated']}")
        
        print(f"\n  Sample Features:")
        for i, (key, value) in enumerate(result['features'].items()):
            if i >= 10:
                print(f"    ... and {len(result['features']) - 10} more")
                break
            print(f"    {key}: {value}")
    else:
        print(f"✗ Failed to get patient features: {response.status_code}")
        print(f"  Note: Feature store may not be initialized")


def example_6_feature_statistics():
    """Example 6: Get feature statistics"""
    print("\n" + "="*60)
    print("Example 6: Get Feature Statistics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/features/statistics")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Feature statistics retrieved:")
        print(f"  Total Features: {result['num_features']}")
        
        print(f"\n  Sample Statistics:")
        for i, (feature, stats) in enumerate(result['feature_statistics'].items()):
            if i >= 5:
                print(f"    ... and {result['num_features'] - 5} more features")
                break
            print(f"\n    {feature}:")
            print(f"      Mean: {stats['mean']:.2f}")
            print(f"      Std: {stats['std']:.2f}")
            print(f"      Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
            print(f"      Missing: {stats['missing_percentage']:.1f}%")
    else:
        print(f"✗ Failed to get feature statistics: {response.status_code}")
        print(f"  Note: Feature store may not be initialized")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Data Ingestion API Examples")
    print("="*60)
    print("\nMake sure the API server is running:")
    print("  python -m uvicorn ml_pipeline.api.main:app --reload")
    print()
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("✗ API is not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to API. Make sure it's running on http://localhost:8000")
        return
    
    print("✓ API is running\n")
    
    # Run examples
    dataset_id = example_1_upload_data()
    example_2_list_sources()
    example_3_quality_report(dataset_id)
    example_4_extract_features(dataset_id)
    example_5_get_patient_features()
    example_6_feature_statistics()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
