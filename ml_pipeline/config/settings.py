"""
Configuration settings for the ML pipeline
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_ROOT: Path = PROJECT_ROOT / "ml_pipeline" / "data_storage"
    RAW_DATA_PATH: Path = DATA_ROOT / "raw"
    PROCESSED_DATA_PATH: Path = DATA_ROOT / "processed"
    FEATURES_PATH: Path = DATA_ROOT / "features"
    MODELS_PATH: Path = DATA_ROOT / "models"
    METADATA_PATH: Path = DATA_ROOT / "metadata"
    LOGS_PATH: Path = PROJECT_ROOT / "ml_pipeline" / "logs"
    
    # Data sources
    ADNI_API_KEY: Optional[str] = None
    ADNI_API_URL: str = "https://ida.loni.usc.edu/services"
    OASIS_DATA_PATH: Optional[Path] = None
    NACC_DATA_PATH: Optional[Path] = None
    
    # Database settings
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ml_pipeline"
    POSTGRES_USER: str = "ml_user"
    POSTGRES_PASSWORD: str = "ml_password"
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Object storage (MinIO/S3)
    STORAGE_TYPE: str = "minio"  # or "s3"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    S3_BUCKET: str = "alzheimer-ml-data"
    S3_REGION: str = "us-east-1"
    
    # ML Configuration
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    TRAINING_BATCH_SIZE: int = 32
    RANDOM_SEED: int = 42
    N_CROSS_VALIDATION_FOLDS: int = 5
    
    # Model settings
    MIN_AUC_ROC: float = 0.80
    MODEL_IMPROVEMENT_THRESHOLD: float = 0.05  # 5% improvement
    MAX_MODEL_VERSIONS: int = 10
    
    # Data quality thresholds
    MIN_COMPLETENESS: float = 0.70
    DRIFT_THRESHOLD: float = 0.2
    PSI_THRESHOLD: float = 0.2
    
    # Performance settings
    MAX_TRAINING_TIME_HOURS: int = 2
    MAX_FEATURE_EXTRACTION_TIME_SECONDS: int = 60
    MAX_SHAP_GENERATION_TIME_SECONDS: int = 2
    
    # Monitoring
    DRIFT_CHECK_INTERVAL_DAYS: int = 7
    RETRAINING_SCHEDULE: str = "monthly"
    PERFORMANCE_ALERT_EMAIL: Optional[str] = None
    LOG_RETENTION_DAYS: int = 90
    AUDIT_LOG_RETENTION_YEARS: int = 7
    
    # Security
    ENCRYPTION_KEY: Optional[str] = None
    ENABLE_AUDIT_LOGGING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
settings.FEATURES_PATH.mkdir(parents=True, exist_ok=True)
settings.MODELS_PATH.mkdir(parents=True, exist_ok=True)
settings.METADATA_PATH.mkdir(parents=True, exist_ok=True)
settings.LOGS_PATH.mkdir(parents=True, exist_ok=True)
