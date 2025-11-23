"""
SQLAlchemy ORM models for feature store and model registry
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, JSON, 
    Boolean, Text, Index, ForeignKey
)
from sqlalchemy.orm import relationship

from ml_pipeline.data_storage.database import Base


class ProcessedFeature(Base):
    """
    Processed features for ML training
    Stores patient features extracted from raw biomedical data
    """
    __tablename__ = "processed_features"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), nullable=False, index=True)
    visit_date = Column(DateTime, nullable=False)
    
    # Cognitive features
    mmse_score = Column(Float)
    moca_score = Column(Float)
    cdr_global = Column(Float)
    adas_cog_score = Column(Float)
    
    # Biomarker features
    csf_ab42 = Column(Float)
    csf_tau = Column(Float)
    csf_ptau = Column(Float)
    ab42_tau_ratio = Column(Float)
    ptau_tau_ratio = Column(Float)
    
    # Imaging features
    hippocampus_left_volume = Column(Float)
    hippocampus_right_volume = Column(Float)
    hippocampus_total_volume = Column(Float)
    entorhinal_cortex_thickness = Column(Float)
    ventricular_volume = Column(Float)
    whole_brain_volume = Column(Float)
    
    # Genetic features
    apoe_genotype = Column(String(10))
    apoe_e4_count = Column(Integer)
    apoe_risk_category = Column(String(20))
    
    # Demographics
    age = Column(Integer)
    sex = Column(String(1))
    education_years = Column(Integer)
    
    # Target variable
    diagnosis = Column(Integer)  # 0: Normal, 1: MCI, 2: AD
    
    # Metadata
    data_source = Column(String(20), nullable=False)  # ADNI, OASIS, NACC
    feature_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_patient_visit', 'patient_id', 'visit_date'),
        Index('idx_diagnosis', 'diagnosis'),
        Index('idx_data_source', 'data_source'),
    )


class ModelVersion(Base):
    """
    Model registry for versioning and tracking ML models
    """
    __tablename__ = "model_versions"
    
    # Primary key
    version_id = Column(String(50), primary_key=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # random_forest, xgboost, neural_network
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    deployed_at = Column(DateTime)
    
    # Performance metrics
    accuracy = Column(Float)
    balanced_accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    roc_auc = Column(Float)
    pr_auc = Column(Float)
    
    # Training information
    dataset_version = Column(String(50))
    n_training_samples = Column(Integer)
    n_validation_samples = Column(Integer)
    n_test_samples = Column(Integer)
    hyperparameters = Column(JSON)
    feature_names = Column(JSON)
    
    # Deployment status
    status = Column(String(20), default='registered')  # registered, production, archived
    
    # Storage location
    artifact_path = Column(String(255))
    
    # Additional metadata
    training_duration_seconds = Column(Float)
    notes = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_model_status', 'model_name', 'status'),
        Index('idx_created_at', 'created_at'),
    )


class DataQualityReport(Base):
    """
    Data quality validation reports
    """
    __tablename__ = "data_quality_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(50), unique=True, nullable=False)
    
    # Dataset information
    dataset_name = Column(String(100), nullable=False)
    dataset_version = Column(String(50))
    data_source = Column(String(20))
    
    # Quality metrics
    total_records = Column(Integer)
    completeness_score = Column(Float)
    phi_detected = Column(Boolean, default=False)
    duplicate_count = Column(Integer)
    outlier_count = Column(Integer)
    
    # Detailed results
    completeness_by_column = Column(JSON)
    outliers_by_column = Column(JSON)
    range_violations = Column(JSON)
    validation_errors = Column(JSON)
    
    # Status
    passed = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_dataset_name', 'dataset_name'),
        Index('idx_created_at', 'created_at'),
    )


class DataDriftReport(Base):
    """
    Data drift detection reports
    """
    __tablename__ = "data_drift_reports"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(50), unique=True, nullable=False)
    
    # Reference and comparison data
    reference_dataset = Column(String(100))
    comparison_dataset = Column(String(100))
    
    # Drift metrics
    drift_detected = Column(Boolean)
    features_with_drift = Column(JSON)
    ks_test_results = Column(JSON)
    psi_scores = Column(JSON)
    
    # Recommendations
    retraining_recommended = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_drift_detected', 'drift_detected'),
        Index('idx_created_at', 'created_at'),
    )


class TrainingJob(Base):
    """
    ML training job tracking
    """
    __tablename__ = "training_jobs"
    
    # Primary key
    job_id = Column(String(50), primary_key=True)
    
    # Job information
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50))
    
    # Status
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Configuration
    config = Column(JSON)
    dataset_version = Column(String(50))
    
    # Results
    result_version_id = Column(String(50), ForeignKey('model_versions.version_id'))
    error_message = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_started_at', 'started_at'),
    )


class AuditLog(Base):
    """
    Audit log for compliance (7-year retention)
    """
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event information
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    operation = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    
    # Details
    resource_type = Column(String(50))  # data, model, feature
    resource_id = Column(String(100))
    action = Column(String(50))  # create, read, update, delete, train, deploy
    
    # Additional context
    details = Column(JSON)
    ip_address = Column(String(45))
    
    # Result
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Indexes
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_user_operation', 'user_id', 'operation'),
        Index('idx_resource', 'resource_type', 'resource_id'),
    )
