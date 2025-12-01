from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application settings with environment-based configuration.
    Supports development, staging, and production environments.
    """
    
    # Application
    APP_NAME: str = "MemoryGuard"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Supabase Database
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/memoryguard"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATA_ENCRYPTION_KEY: Optional[str] = None
    AUDIT_LOG_PATH: str = "./logs/audit.log"
    INPUT_VALIDATION_ENABLED: bool = True
    MAX_JSON_PAYLOAD_BYTES: int = 5 * 1024 * 1024  # 5MB (for base64 images)
    MAX_INPUT_STRING_LENGTH: int = 10_000
    CONTENT_SECURITY_POLICY: str = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "connect-src 'self' https://www.googleapis.com https://oauth2.googleapis.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    PERMISSIONS_POLICY: str = (
        "geolocation=(), camera=(), microphone=(), display-capture=(), "
        "fullscreen=(self), payment=()"
    )
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Google Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_RATE_LIMIT_PER_MINUTE: int = 60
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_MAX_RETRIES: int = 3
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            # Handle empty string
            if not v or v.strip() == '':
                return ["http://localhost:3000"]
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_EXTENSIONS: Union[List[str], str] = [".dcm", ".nii", ".nii.gz", ".jpg", ".png"]
    
    @field_validator('ALLOWED_UPLOAD_EXTENSIONS', mode='before')
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse ALLOWED_UPLOAD_EXTENSIONS from string or list"""
        if isinstance(v, str):
            if not v or v.strip() == '':
                return [".dcm", ".nii", ".nii.gz", ".jpg", ".png"]
            return [ext.strip() for ext in v.split(',') if ext.strip()]
        return v
    
    # ML Model Settings
    ML_MODEL_PATH: str = "models/"
    ML_BATCH_SIZE: int = 32
    
    # Medical Imaging Settings
    IMAGING_STORAGE_PATH: str = "./data/imaging"
    IMAGING_ENCRYPTION_KEY: Optional[str] = None  # Will be generated if not provided
    IMAGING_MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Sentry Error Tracking
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENABLED: bool = False
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of transactions
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1  # 10% of transactions
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        return self.ENVIRONMENT.lower() == "staging"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_production_settings(self) -> List[str]:
        """
        Validate that all required settings for production are configured.
        Returns list of missing or invalid settings.
        """
        errors = []
        
        if self.is_production:
            if self.JWT_SECRET == "your-secret-key-change-in-production":
                errors.append("JWT_SECRET must be changed in production")
            
            if not self.SUPABASE_URL:
                errors.append("SUPABASE_URL is required in production")
            
            if not self.SUPABASE_SERVICE_KEY:
                errors.append("SUPABASE_SERVICE_KEY is required in production")
            
            if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
                errors.append("Google OAuth credentials are required in production")
            
            if not self.GEMINI_API_KEY:
                errors.append("GEMINI_API_KEY is required in production")
            
            if self.DEBUG:
                errors.append("DEBUG should be False in production")
        
        return errors


class DevelopmentSettings(Settings):
    """Development environment specific settings"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class StagingSettings(Settings):
    """Staging environment specific settings"""
    ENVIRONMENT: str = "staging"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


class ProductionSettings(Settings):
    """Production environment specific settings"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_PER_MINUTE: int = 60  # Stricter rate limiting in production


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings instance based on ENVIRONMENT variable.
    Uses caching to avoid re-reading environment variables.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()

# Validate production settings on import
if settings.is_production:
    validation_errors = settings.validate_production_settings()
    if validation_errors:
        raise ValueError(
            f"Production configuration errors:\n" + "\n".join(f"- {error}" for error in validation_errors)
        )
