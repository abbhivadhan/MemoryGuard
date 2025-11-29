"""
FastAPI endpoints for data ingestion and management

Provides REST API for:
- Data upload (CSV, JSON, DICOM)
- Data source listing
- Quality reports
- Feature extraction
- Feature retrieval
- Feature statistics

Implements Requirements:
- 1.4: Support CSV, JSON, and DICOM file formats
- 1.1, 1.2, 1.3: List available datasets (ADNI, OASIS, NACC)
- 4.6: Return validation results
- 3.1-3.8: Trigger feature engineering
- 12.4: Return patient features
- 10.1: Return feature distributions
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import io
import json
import time
import uuid
from pathlib import Path

from ml_pipeline.data_ingestion.data_acquisition_service import DataAcquisitionService
from ml_pipeline.data_validation.data_validation_engine import DataValidationEngine
from ml_pipeline.feature_engineering.pipeline import FeatureEngineeringPipeline
from ml_pipeline.data_storage.feature_store import FeatureStore
from ml_pipeline.config.logging_config import main_logger
from ml_pipeline.config.settings import Settings


# Initialize router
router = APIRouter(prefix="/api/v1/data", tags=["data-ingestion"])

# Initialize services
_settings = Settings()
_acquisition_service = None
_validation_engine = None
_feature_pipeline = None
_feature_store = None


def get_acquisition_service() -> DataAcquisitionService:
    """Get data acquisition service instance"""
    global _acquisition_service
    if _acquisition_service is None:
        _acquisition_service = DataAcquisitionService(_settings)
    return _acquisition_service


def get_validation_engine() -> DataValidationEngine:
    """Get data validation engine instance"""
    global _validation_engine
    if _validation_engine is None:
        _validation_engine = DataValidationEngine()
    return _validation_engine


def get_feature_pipeline() -> FeatureEngineeringPipeline:
    """Get feature engineering pipeline instance"""
    global _feature_pipeline
    if _feature_pipeline is None:
        _feature_pipeline = FeatureEngineeringPipeline()
    return _feature_pipeline


def get_feature_store() -> FeatureStore:
    """Get feature store instance"""
    global _feature_store
    if _feature_store is None:
        _feature_store = FeatureStore()
    return _feature_store


# Request/Response models

class DataUploadResponse(BaseModel):
    """Response for data upload"""
    dataset_id: str
    filename: str
    format: str
    num_records: int
    num_columns: int
    validation_status: str
    validation_summary: Optional[Dict[str, Any]] = None
    timestamp: str
    processing_time: float


class DataSource(BaseModel):
    """Data source information"""
    source_name: str
    source_type: str
    description: str
    available_data_types: List[str]
    total_records: Optional[int] = None
    last_updated: Optional[str] = None


class DataSourceListResponse(BaseModel):
    """Response for data source listing"""
    sources: List[DataSource]
    total_sources: int


class QualityReportResponse(BaseModel):
    """Response for quality report"""
    dataset_id: str
    dataset_name: str
    validation_passed: bool
    report: Dict[str, Any]
    timestamp: str


class FeatureExtractionRequest(BaseModel):
    """Request for feature extraction"""
    dataset_id: str
    patient_id_col: str = Field("patient_id", description="Name of patient ID column")
    visit_date_col: str = Field("visit_date", description="Name of visit date column")
    include_temporal: bool = Field(True, description="Include temporal features")
    save_to_store: bool = Field(True, description="Save features to feature store")


class FeatureExtractionResponse(BaseModel):
    """Response for feature extraction"""
    dataset_id: str
    num_features: int
    feature_names: List[str]
    num_records: int
    saved_to_store: bool
    timestamp: str
    processing_time: float


class PatientFeaturesResponse(BaseModel):
    """Response for patient features"""
    patient_id: str
    features: Dict[str, Any]
    num_features: int
    last_updated: str


class FeatureStatisticsResponse(BaseModel):
    """Response for feature statistics"""
    num_features: int
    feature_statistics: Dict[str, Dict[str, Any]]
    timestamp: str


# Helper functions

def parse_uploaded_file(file: UploadFile, format: str) -> pd.DataFrame:
    """
    Parse uploaded file into DataFrame
    
    Args:
        file: Uploaded file
        format: File format (csv, json, dicom)
        
    Returns:
        DataFrame with parsed data
        
    Raises:
        HTTPException if parsing fails
    """
    try:
        content = file.file.read()
        
        if format == 'csv':
            df = pd.read_csv(io.BytesIO(content))
        elif format == 'json':
            df = pd.read_json(io.BytesIO(content))
        elif format == 'dicom':
            # DICOM parsing would require pydicom
            # For now, return error
            raise HTTPException(
                status_code=400,
                detail="DICOM parsing not yet implemented. Please use CSV or JSON format."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Supported formats: csv, json"
            )
        
        return df
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse file: {str(e)}"
        )


def save_dataset(dataset_id: str, data: pd.DataFrame, filename: str) -> Path:
    """
    Save dataset to storage
    
    Args:
        dataset_id: Unique dataset ID
        data: DataFrame to save
        filename: Original filename
        
    Returns:
        Path to saved file
    """
    # Save to raw data directory
    raw_dir = Path("ml_pipeline/data_storage/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = raw_dir / f"{dataset_id}_{filename}.parquet"
    data.to_parquet(filepath, index=False)
    
    main_logger.info(f"Saved dataset to {filepath}")
    return filepath


def load_dataset(dataset_id: str) -> pd.DataFrame:
    """
    Load dataset from storage
    
    Args:
        dataset_id: Dataset ID
        
    Returns:
        DataFrame with dataset
        
    Raises:
        HTTPException if dataset not found
    """
    raw_dir = Path("ml_pipeline/data_storage/raw")
    
    # Find file with matching dataset_id
    matching_files = list(raw_dir.glob(f"{dataset_id}_*.parquet"))
    
    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found: {dataset_id}"
        )
    
    filepath = matching_files[0]
    return pd.read_parquet(filepath)


# API Endpoints

@router.post("/ingest", response_model=DataUploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    format: str = Query(..., description="File format: csv, json, or dicom"),
    validate: bool = Query(True, description="Run validation checks"),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and ingest biomedical data
    
    Implements Requirement 1.4:
    - Accept CSV, JSON, DICOM formats
    - Validate data format and structure
    - Store data for processing
    
    Args:
        file: Uploaded file
        format: File format (csv, json, dicom)
        validate: Whether to run validation checks
        
    Returns:
        Upload response with validation status
    """
    start_time = time.time()
    dataset_id = str(uuid.uuid4())
    
    try:
        main_logger.info(
            f"Receiving data upload: {file.filename} (format={format})",
            extra={'operation': 'data_upload', 'dataset_id': dataset_id}
        )
        
        # Parse uploaded file
        data = parse_uploaded_file(file, format)
        
        main_logger.info(
            f"Parsed data: {data.shape[0]} records, {data.shape[1]} columns"
        )
        
        # Save dataset
        save_dataset(dataset_id, data, file.filename)
        
        # Validate if requested
        validation_status = "not_validated"
        validation_summary = None
        
        if validate:
            validation_engine = get_validation_engine()
            quick_results = validation_engine.quick_validate(data)
            
            if quick_results['quick_validation_passed']:
                validation_status = "passed"
            elif quick_results['phi_detected']:
                validation_status = "failed_phi_detected"
            else:
                validation_status = "warning"
            
            validation_summary = {
                'phi_detected': quick_results['phi_detected'],
                'completeness': quick_results['completeness'],
                'duplicates_detected': quick_results['duplicates_detected']
            }
            
            main_logger.info(f"Validation status: {validation_status}")
        
        processing_time = time.time() - start_time
        
        return DataUploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            format=format,
            num_records=len(data),
            num_columns=len(data.columns),
            validation_status=validation_status,
            validation_summary=validation_summary,
            timestamp=datetime.utcnow().isoformat(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Data upload failed: {str(e)}",
            extra={'operation': 'data_upload', 'dataset_id': dataset_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=DataSourceListResponse)
async def list_data_sources():
    """
    List available data sources
    
    Implements Requirements 1.1, 1.2, 1.3:
    - List ADNI datasets
    - List OASIS datasets
    - List NACC datasets
    
    Returns:
        List of available data sources with metadata
    """
    try:
        sources = [
            DataSource(
                source_name="ADNI",
                source_type="external",
                description="Alzheimer's Disease Neuroimaging Initiative - longitudinal multicenter study",
                available_data_types=[
                    "cognitive_assessments",
                    "csf_biomarkers",
                    "mri_scans",
                    "pet_imaging",
                    "genetic_data",
                    "demographics"
                ],
                total_records=None,  # Would be populated from actual data
                last_updated=None
            ),
            DataSource(
                source_name="OASIS",
                source_type="external",
                description="Open Access Series of Imaging Studies - publicly available neuroimaging datasets",
                available_data_types=[
                    "mri_scans",
                    "volumetric_data",
                    "cdr_scores",
                    "demographics",
                    "longitudinal_data"
                ],
                total_records=None,
                last_updated=None
            ),
            DataSource(
                source_name="NACC",
                source_type="external",
                description="National Alzheimer's Coordinating Center - clinical and neuropathological research data",
                available_data_types=[
                    "clinical_assessments",
                    "neuropathology",
                    "cognitive_tests",
                    "medical_history"
                ],
                total_records=None,
                last_updated=None
            )
        ]
        
        main_logger.info(
            f"Listed {len(sources)} data sources",
            extra={'operation': 'list_sources'}
        )
        
        return DataSourceListResponse(
            sources=sources,
            total_sources=len(sources)
        )
        
    except Exception as e:
        main_logger.error(
            f"Failed to list data sources: {str(e)}",
            extra={'operation': 'list_sources'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/{dataset_id}", response_model=QualityReportResponse)
async def get_quality_report(dataset_id: str):
    """
    Get data quality report for a dataset
    
    Implements Requirement 4.6:
    - Return validation results
    - Generate comprehensive quality report
    - Include completeness, outliers, duplicates, etc.
    
    Args:
        dataset_id: Dataset ID
        
    Returns:
        Quality report with validation results
    """
    start_time = time.time()
    
    try:
        main_logger.info(
            f"Generating quality report for dataset: {dataset_id}",
            extra={'operation': 'quality_report', 'dataset_id': dataset_id}
        )
        
        # Load dataset
        data = load_dataset(dataset_id)
        
        # Generate comprehensive quality report
        validation_engine = get_validation_engine()
        report = validation_engine.validate_dataset(
            data,
            dataset_name=dataset_id,
            strict_mode=False
        )
        
        processing_time = time.time() - start_time
        
        main_logger.info(
            f"Quality report generated in {processing_time:.2f}s",
            extra={'operation': 'quality_report', 'dataset_id': dataset_id}
        )
        
        return QualityReportResponse(
            dataset_id=dataset_id,
            dataset_name=dataset_id,
            validation_passed=report['validation_passed'],
            report=report,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Failed to generate quality report: {str(e)}",
            extra={'operation': 'quality_report', 'dataset_id': dataset_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/features/extract", response_model=FeatureExtractionResponse)
async def extract_features(
    request: FeatureExtractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger feature engineering on a dataset
    
    Implements Requirements 3.1-3.8:
    - Extract cognitive assessment scores
    - Process CSF biomarker values
    - Extract volumetric measurements from MRI
    - Encode APOE genotype
    - Normalize continuous features
    - Handle missing data
    - Generate feature importance report
    - Create temporal features
    
    Args:
        request: Feature extraction request
        
    Returns:
        Feature extraction response with metadata
    """
    start_time = time.time()
    
    try:
        main_logger.info(
            f"Starting feature extraction for dataset: {request.dataset_id}",
            extra={'operation': 'feature_extraction', 'dataset_id': request.dataset_id}
        )
        
        # Load dataset
        data = load_dataset(request.dataset_id)
        
        # Initialize feature pipeline
        pipeline = FeatureEngineeringPipeline(
            include_temporal=request.include_temporal
        )
        
        # Extract features
        features = pipeline.fit_transform(
            data,
            patient_id_col=request.patient_id_col,
            visit_date_col=request.visit_date_col
        )
        
        # Get feature names
        feature_names = list(features.columns)
        
        # Save to feature store if requested
        saved_to_store = False
        if request.save_to_store:
            try:
                feature_store = get_feature_store()
                feature_store.save_features(
                    features,
                    dataset_name=request.dataset_id,
                    partition_by='date'
                )
                saved_to_store = True
                main_logger.info(f"Features saved to feature store")
            except Exception as e:
                main_logger.warning(f"Failed to save to feature store: {e}")
        
        processing_time = time.time() - start_time
        
        main_logger.info(
            f"Feature extraction completed: {len(feature_names)} features, "
            f"{len(features)} records in {processing_time:.2f}s",
            extra={'operation': 'feature_extraction', 'dataset_id': request.dataset_id}
        )
        
        return FeatureExtractionResponse(
            dataset_id=request.dataset_id,
            num_features=len(feature_names),
            feature_names=feature_names,
            num_records=len(features),
            saved_to_store=saved_to_store,
            timestamp=datetime.utcnow().isoformat(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Feature extraction failed: {str(e)}",
            extra={'operation': 'feature_extraction', 'dataset_id': request.dataset_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features/{patient_id}", response_model=PatientFeaturesResponse)
async def get_patient_features(patient_id: str):
    """
    Retrieve features for a specific patient
    
    Implements Requirement 12.4:
    - Return patient features from feature store
    - Fast retrieval using indexing
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient features
    """
    try:
        main_logger.info(
            f"Retrieving features for patient: {patient_id}",
            extra={'operation': 'get_patient_features', 'patient_id': patient_id}
        )
        
        # Load from feature store
        feature_store = get_feature_store()
        
        try:
            features_df = feature_store.get_patient_features(patient_id)
            
            if features_df.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"No features found for patient: {patient_id}"
                )
            
            # Convert to dictionary
            features_dict = features_df.iloc[0].to_dict()
            
            # Remove NaN values
            features_dict = {
                k: (None if pd.isna(v) else float(v) if isinstance(v, (np.floating, np.integer)) else v)
                for k, v in features_dict.items()
            }
            
            return PatientFeaturesResponse(
                patient_id=patient_id,
                features=features_dict,
                num_features=len(features_dict),
                last_updated=datetime.utcnow().isoformat()
            )
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Feature store not initialized or patient not found: {patient_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Failed to retrieve patient features: {str(e)}",
            extra={'operation': 'get_patient_features', 'patient_id': patient_id}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features/statistics", response_model=FeatureStatisticsResponse)
async def get_feature_statistics():
    """
    Get feature distribution statistics
    
    Implements Requirement 10.1:
    - Return feature distributions
    - Monitor input feature distributions over time
    
    Returns:
        Feature statistics including mean, std, min, max, etc.
    """
    try:
        main_logger.info(
            "Retrieving feature statistics",
            extra={'operation': 'get_feature_statistics'}
        )
        
        # Load from feature store
        feature_store = get_feature_store()
        
        try:
            # Get all features
            features_df = feature_store.load_features()
            
            if features_df.empty:
                raise HTTPException(
                    status_code=404,
                    detail="No features found in feature store"
                )
            
            # Calculate statistics for numeric columns
            numeric_cols = features_df.select_dtypes(include=[np.number]).columns
            
            feature_statistics = {}
            for col in numeric_cols:
                stats = {
                    'mean': float(features_df[col].mean()),
                    'std': float(features_df[col].std()),
                    'min': float(features_df[col].min()),
                    'max': float(features_df[col].max()),
                    'median': float(features_df[col].median()),
                    'q25': float(features_df[col].quantile(0.25)),
                    'q75': float(features_df[col].quantile(0.75)),
                    'missing_count': int(features_df[col].isna().sum()),
                    'missing_percentage': float(features_df[col].isna().mean() * 100)
                }
                feature_statistics[col] = stats
            
            main_logger.info(
                f"Retrieved statistics for {len(feature_statistics)} features"
            )
            
            return FeatureStatisticsResponse(
                num_features=len(feature_statistics),
                feature_statistics=feature_statistics,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Feature store not initialized"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(
            f"Failed to retrieve feature statistics: {str(e)}",
            extra={'operation': 'get_feature_statistics'}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "data-ingestion-api",
        "timestamp": datetime.utcnow().isoformat()
    }
