"""Data ingestion module for biomedical datasets."""

from .data_acquisition_service import DataAcquisitionService
from .schema_validator import SchemaValidator, ValidationResult
from .provenance_tracker import ProvenanceTracker, ProvenanceRecord, DataSource, ProcessingStage
from .adni import ADNIDataLoader
from .oasis import OASISDataLoader
from .nacc import NACCDataLoader

__all__ = [
    'DataAcquisitionService',
    'SchemaValidator',
    'ValidationResult',
    'ProvenanceTracker',
    'ProvenanceRecord',
    'DataSource',
    'ProcessingStage',
    'ADNIDataLoader',
    'OASISDataLoader',
    'NACCDataLoader'
]
