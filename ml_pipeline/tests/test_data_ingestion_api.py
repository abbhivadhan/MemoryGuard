"""
Tests for data ingestion API endpoints

Tests all endpoints in the data ingestion API:
- Data upload
- Data source listing
- Quality reports
- Feature extraction
- Feature retrieval
- Feature statistics
"""
import pytest
from fastapi.testclient import TestClient
import pandas as pd
import io
from pathlib import Path

from ml_pipeline.api.main import app


client = TestClient(app)


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing"""
    data = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'age': [65, 70, 75],
        'mmse_score': [28, 24, 20],
        'csf_ab42': [500, 450, 400],
        'hippocampus_volume': [7000, 6500, 6000]
    })
    
    # Convert to CSV bytes
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    return csv_bytes


@pytest.fixture
def sample_json_data():
    """Create sample JSON data for testing"""
    data = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003'],
        'age': [65, 70, 75],
        'mmse_score': [28, 24, 20]
    })
    
    # Convert to JSON bytes
    json_str = data.to_json(orient='records')
    return json_str.encode('utf-8')


class TestDataUploadEndpoint:
    """Test data upload endpoint"""
    
    def test_upload_csv_success(self, sample_csv_data):
        """Test successful CSV upload"""
        response = client.post(
            "/api/v1/data/ingest?format=csv&validate=true",
            files={"file": ("test_data.csv", sample_csv_data, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'dataset_id' in data
        assert data['filename'] == 'test_data.csv'
        assert data['format'] == 'csv'
        assert data['num_records'] == 3
        assert data['num_columns'] == 5
        assert data['validation_status'] in ['passed', 'warning', 'not_validated']
    
    def test_upload_json_success(self, sample_json_data):
        """Test successful JSON upload"""
        response = client.post(
            "/api/v1/data/ingest?format=json&validate=true",
            files={"file": ("test_data.json", sample_json_data, "application/json")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'dataset_id' in data
        assert data['format'] == 'json'
        assert data['num_records'] == 3
    
    def test_upload_without_validation(self, sample_csv_data):
        """Test upload without validation"""
        response = client.post(
            "/api/v1/data/ingest?format=csv&validate=false",
            files={"file": ("test_data.csv", sample_csv_data, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['validation_status'] == 'not_validated'
    
    def test_upload_unsupported_format(self, sample_csv_data):
        """Test upload with unsupported format"""
        response = client.post(
            "/api/v1/data/ingest?format=xml&validate=false",
            files={"file": ("test_data.xml", sample_csv_data, "text/xml")}
        )
        
        assert response.status_code == 400
        assert 'Unsupported format' in response.json()['detail']
    
    def test_upload_dicom_not_implemented(self, sample_csv_data):
        """Test DICOM upload (not yet implemented)"""
        response = client.post(
            "/api/v1/data/ingest?format=dicom&validate=false",
            files={"file": ("test_data.dcm", sample_csv_data, "application/dicom")}
        )
        
        assert response.status_code == 400
        assert 'DICOM parsing not yet implemented' in response.json()['detail']


class TestDataSourceListingEndpoint:
    """Test data source listing endpoint"""
    
    def test_list_sources_success(self):
        """Test successful data source listing"""
        response = client.get("/api/v1/data/sources")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'sources' in data
        assert 'total_sources' in data
        assert data['total_sources'] == 3
        
        # Check for expected sources
        source_names = [s['source_name'] for s in data['sources']]
        assert 'ADNI' in source_names
        assert 'OASIS' in source_names
        assert 'NACC' in source_names
    
    def test_source_metadata(self):
        """Test that sources have required metadata"""
        response = client.get("/api/v1/data/sources")
        data = response.json()
        
        for source in data['sources']:
            assert 'source_name' in source
            assert 'source_type' in source
            assert 'description' in source
            assert 'available_data_types' in source
            assert isinstance(source['available_data_types'], list)
            assert len(source['available_data_types']) > 0


class TestQualityReportEndpoint:
    """Test quality report endpoint"""
    
    def test_quality_report_not_found(self):
        """Test quality report for non-existent dataset"""
        response = client.get("/api/v1/data/quality/nonexistent_id")
        
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()
    
    def test_quality_report_success(self, sample_csv_data):
        """Test quality report for uploaded dataset"""
        # First upload a dataset
        upload_response = client.post(
            "/api/v1/data/ingest?format=csv&validate=false",
            files={"file": ("test_data.csv", sample_csv_data, "text/csv")}
        )
        dataset_id = upload_response.json()['dataset_id']
        
        # Get quality report
        response = client.get(f"/api/v1/data/quality/{dataset_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'dataset_id' in data
        assert 'validation_passed' in data
        assert 'report' in data
        assert isinstance(data['report'], dict)


class TestFeatureExtractionEndpoint:
    """Test feature extraction endpoint"""
    
    def test_feature_extraction_not_found(self):
        """Test feature extraction for non-existent dataset"""
        response = client.post(
            "/api/v1/data/features/extract",
            json={
                "dataset_id": "nonexistent_id",
                "patient_id_col": "patient_id",
                "visit_date_col": "visit_date"
            }
        )
        
        assert response.status_code == 404
    
    def test_feature_extraction_success(self, sample_csv_data):
        """Test successful feature extraction"""
        # First upload a dataset
        upload_response = client.post(
            "/api/v1/data/ingest?format=csv&validate=false",
            files={"file": ("test_data.csv", sample_csv_data, "text/csv")}
        )
        dataset_id = upload_response.json()['dataset_id']
        
        # Extract features
        response = client.post(
            "/api/v1/data/features/extract",
            json={
                "dataset_id": dataset_id,
                "patient_id_col": "patient_id",
                "include_temporal": False,
                "save_to_store": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'dataset_id' in data
        assert 'num_features' in data
        assert 'feature_names' in data
        assert 'num_records' in data
        assert isinstance(data['feature_names'], list)


class TestFeatureRetrievalEndpoint:
    """Test feature retrieval endpoint"""
    
    def test_get_patient_features_not_found(self):
        """Test retrieving features for non-existent patient"""
        response = client.get("/api/v1/data/features/nonexistent_patient")
        
        # Should return 404 or 500 depending on whether feature store exists
        assert response.status_code in [404, 500]


class TestFeatureStatisticsEndpoint:
    """Test feature statistics endpoint"""
    
    def test_get_feature_statistics_empty(self):
        """Test getting statistics when feature store is empty"""
        response = client.get("/api/v1/data/features/statistics")
        
        # Should return 404 if no features exist
        assert response.status_code in [404, 500]


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/data/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'healthy'
        assert data['service'] == 'data-ingestion-api'


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self, sample_csv_data):
        """Test complete workflow: upload -> validate -> extract features"""
        # Step 1: Upload data
        upload_response = client.post(
            "/api/v1/data/ingest?format=csv&validate=true",
            files={"file": ("test_data.csv", sample_csv_data, "text/csv")}
        )
        assert upload_response.status_code == 200
        dataset_id = upload_response.json()['dataset_id']
        
        # Step 2: Get quality report
        quality_response = client.get(f"/api/v1/data/quality/{dataset_id}")
        assert quality_response.status_code == 200
        
        # Step 3: Extract features
        extract_response = client.post(
            "/api/v1/data/features/extract",
            json={
                "dataset_id": dataset_id,
                "patient_id_col": "patient_id",
                "include_temporal": False,
                "save_to_store": False
            }
        )
        assert extract_response.status_code == 200
        
        # Verify we got features
        extract_data = extract_response.json()
        assert extract_data['num_features'] > 0
        assert extract_data['num_records'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
