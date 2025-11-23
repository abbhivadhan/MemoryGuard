-- Database schema for ML Pipeline
-- Feature Store and Model Registry

-- Create database (run as superuser)
-- CREATE DATABASE ml_pipeline;
-- CREATE USER ml_user WITH PASSWORD 'ml_password';
-- GRANT ALL PRIVILEGES ON DATABASE ml_pipeline TO ml_user;

-- Connect to ml_pipeline database
\c ml_pipeline;

-- Processed Features Table
CREATE TABLE IF NOT EXISTS processed_features (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    visit_date TIMESTAMP NOT NULL,
    
    -- Cognitive features
    mmse_score FLOAT,
    moca_score FLOAT,
    cdr_global FLOAT,
    adas_cog_score FLOAT,
    
    -- Biomarker features
    csf_ab42 FLOAT,
    csf_tau FLOAT,
    csf_ptau FLOAT,
    ab42_tau_ratio FLOAT,
    ptau_tau_ratio FLOAT,
    
    -- Imaging features
    hippocampus_left_volume FLOAT,
    hippocampus_right_volume FLOAT,
    hippocampus_total_volume FLOAT,
    entorhinal_cortex_thickness FLOAT,
    ventricular_volume FLOAT,
    whole_brain_volume FLOAT,
    
    -- Genetic features
    apoe_genotype VARCHAR(10),
    apoe_e4_count INTEGER,
    apoe_risk_category VARCHAR(20),
    
    -- Demographics
    age INTEGER,
    sex VARCHAR(1),
    education_years INTEGER,
    
    -- Target variable
    diagnosis INTEGER,  -- 0: Normal, 1: MCI, 2: AD
    
    -- Metadata
    data_source VARCHAR(20) NOT NULL,
    feature_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for processed_features
CREATE INDEX idx_patient_id ON processed_features(patient_id);
CREATE INDEX idx_patient_visit ON processed_features(patient_id, visit_date);
CREATE INDEX idx_diagnosis ON processed_features(diagnosis);
CREATE INDEX idx_data_source ON processed_features(data_source);

-- Model Versions Table
CREATE TABLE IF NOT EXISTS model_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    
    -- Performance metrics
    accuracy FLOAT,
    balanced_accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    pr_auc FLOAT,
    
    -- Training information
    dataset_version VARCHAR(50),
    n_training_samples INTEGER,
    n_validation_samples INTEGER,
    n_test_samples INTEGER,
    hyperparameters JSONB,
    feature_names JSONB,
    
    -- Deployment status
    status VARCHAR(20) DEFAULT 'registered',
    
    -- Storage location
    artifact_path VARCHAR(255),
    
    -- Additional metadata
    training_duration_seconds FLOAT,
    notes TEXT
);

-- Indexes for model_versions
CREATE INDEX idx_model_name ON model_versions(model_name);
CREATE INDEX idx_model_status ON model_versions(model_name, status);
CREATE INDEX idx_created_at ON model_versions(created_at);

-- Data Quality Reports Table
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Dataset information
    dataset_name VARCHAR(100) NOT NULL,
    dataset_version VARCHAR(50),
    data_source VARCHAR(20),
    
    -- Quality metrics
    total_records INTEGER,
    completeness_score FLOAT,
    phi_detected BOOLEAN DEFAULT FALSE,
    duplicate_count INTEGER,
    outlier_count INTEGER,
    
    -- Detailed results
    completeness_by_column JSONB,
    outliers_by_column JSONB,
    range_violations JSONB,
    validation_errors JSONB,
    
    -- Status
    passed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for data_quality_reports
CREATE INDEX idx_dqr_dataset_name ON data_quality_reports(dataset_name);
CREATE INDEX idx_dqr_created_at ON data_quality_reports(created_at);

-- Data Drift Reports Table
CREATE TABLE IF NOT EXISTS data_drift_reports (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Reference and comparison data
    reference_dataset VARCHAR(100),
    comparison_dataset VARCHAR(100),
    
    -- Drift metrics
    drift_detected BOOLEAN,
    features_with_drift JSONB,
    ks_test_results JSONB,
    psi_scores JSONB,
    
    -- Recommendations
    retraining_recommended BOOLEAN,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for data_drift_reports
CREATE INDEX idx_ddr_drift_detected ON data_drift_reports(drift_detected);
CREATE INDEX idx_ddr_created_at ON data_drift_reports(created_at);

-- Training Jobs Table
CREATE TABLE IF NOT EXISTS training_jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    
    -- Job information
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Configuration
    config JSONB,
    dataset_version VARCHAR(50),
    
    -- Results
    result_version_id VARCHAR(50) REFERENCES model_versions(version_id),
    error_message TEXT
);

-- Indexes for training_jobs
CREATE INDEX idx_tj_status ON training_jobs(status);
CREATE INDEX idx_tj_started_at ON training_jobs(started_at);

-- Audit Logs Table (7-year retention)
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    
    -- Event information
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operation VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    
    -- Details
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    action VARCHAR(50),
    
    -- Additional context
    details JSONB,
    ip_address VARCHAR(45),
    
    -- Result
    success BOOLEAN,
    error_message TEXT
);

-- Indexes for audit_logs
CREATE INDEX idx_al_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_al_user_operation ON audit_logs(user_id, operation);
CREATE INDEX idx_al_resource ON audit_logs(resource_type, resource_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ml_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ml_user;

-- Comments
COMMENT ON TABLE processed_features IS 'Processed features for ML training from biomedical datasets';
COMMENT ON TABLE model_versions IS 'Model registry with versioning and performance metrics';
COMMENT ON TABLE data_quality_reports IS 'Data quality validation reports';
COMMENT ON TABLE data_drift_reports IS 'Data drift detection reports';
COMMENT ON TABLE training_jobs IS 'ML training job tracking';
COMMENT ON TABLE audit_logs IS 'Audit log for compliance (7-year retention)';
