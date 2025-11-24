"""Main data acquisition service integrating all loaders."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from ml_pipeline.config.settings import Settings
from ml_pipeline.data_ingestion.adni import ADNIDataLoader
from ml_pipeline.data_ingestion.oasis import OASISDataLoader
from ml_pipeline.data_ingestion.nacc import NACCDataLoader
from ml_pipeline.data_ingestion.schema_validator import SchemaValidator
from ml_pipeline.data_ingestion.provenance_tracker import (
    ProvenanceTracker,
    DataSource,
    ProcessingStage
)

logger = logging.getLogger(__name__)


class DataAcquisitionService:
    """
    Main service for acquiring biomedical data from multiple sources.
    
    Integrates ADNI, OASIS, and NACC data loaders with schema validation
    and provenance tracking.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize data acquisition service.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        
        # Initialize loaders
        self.adni_loader = ADNIDataLoader(self.settings)
        self.oasis_loader = OASISDataLoader(self.settings)
        self.nacc_loader = NACCDataLoader(self.settings)
        
        # Initialize validators and trackers
        self.schema_validator = SchemaValidator()
        self.provenance_tracker = ProvenanceTracker(self.settings)
        
        logger.info("Data acquisition service initialized")
    
    def acquire_adni_data(
        self,
        data_types: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        validate: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Acquire ADNI data with validation and provenance tracking.
        
        Args:
            data_types: List of data types to acquire. If None, acquires all.
            date_range: Optional date range filter
            validate: Whether to validate data against schema
        
        Returns:
            Dictionary mapping data type to DataFrame
        """
        logger.info("Acquiring ADNI data")
        
        if data_types is None:
            data_types = ['cognitive', 'biomarkers', 'mri', 'genetic']
        
        results = {}
        
        for data_type in data_types:
            logger.info(f"Loading ADNI {data_type} data")
            
            # Load data
            if data_type == 'cognitive':
                data = self.adni_loader.load_cognitive_assessments(date_range=date_range)
                schema_name = 'adni_cognitive'
            elif data_type == 'biomarkers':
                data = self.adni_loader.load_csf_biomarkers(date_range=date_range)
                schema_name = 'adni_biomarker'
            elif data_type == 'mri':
                data = self.adni_loader.load_mri_metadata(date_range=date_range)
                schema_name = None  # No specific schema for MRI metadata
            elif data_type == 'genetic':
                data = self.adni_loader.load_genetic_data()
                schema_name = None  # No specific schema for genetic data
            else:
                logger.warning(f"Unknown ADNI data type: {data_type}")
                continue
            
            # Validate if requested and schema available
            if validate and schema_name:
                validation_result = self.schema_validator.validate(data, schema_name)
                self.schema_validator.log_validation_errors(validation_result)
                
                if not validation_result.valid:
                    logger.error(f"Validation failed for ADNI {data_type} data")
                    # Continue anyway but log the issue
            
            # Track provenance
            if not data.empty:
                provenance_record = self.provenance_tracker.track_ingestion(
                    dataset_name=f"adni_{data_type}",
                    data_source=DataSource.ADNI,
                    data=data,
                    metadata={
                        'date_range': str(date_range) if date_range else None,
                        'validated': validate
                    }
                )
                logger.info(f"Tracked provenance: {provenance_record.record_id}")
            
            results[data_type] = data
        
        total_records = sum(len(df) for df in results.values())
        logger.info(f"Acquired {total_records} total ADNI records")
        
        return results
    
    def acquire_oasis_data(
        self,
        version: str = "OASIS-3",
        validate: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Acquire OASIS data with validation and provenance tracking.
        
        Args:
            version: OASIS version to acquire
            validate: Whether to validate data against schema
        
        Returns:
            Dictionary with 'mri', 'demographics', and 'cdr' DataFrames
        """
        logger.info(f"Acquiring OASIS {version} data")
        
        # Load data
        data = self.oasis_loader.load_oasis_data(version=version)
        
        # Validate MRI data if requested
        if validate and not data['mri'].empty:
            validation_result = self.schema_validator.validate(data['mri'], 'oasis_mri')
            self.schema_validator.log_validation_errors(validation_result)
            
            if not validation_result.valid:
                logger.error("Validation failed for OASIS MRI data")
        
        # Track provenance for each data type
        for data_type, df in data.items():
            if not df.empty:
                provenance_record = self.provenance_tracker.track_ingestion(
                    dataset_name=f"oasis_{version.lower()}_{data_type}",
                    data_source=DataSource.OASIS,
                    data=df,
                    metadata={
                        'version': version,
                        'validated': validate
                    }
                )
                logger.info(f"Tracked provenance: {provenance_record.record_id}")
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"Acquired {total_records} total OASIS records")
        
        return data
    
    def acquire_nacc_data(
        self,
        modules: Optional[List[str]] = None,
        validate: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Acquire NACC data with validation and provenance tracking.
        
        Args:
            modules: List of NACC modules to acquire. If None, acquires all.
            validate: Whether to validate data against schema
        
        Returns:
            Dictionary mapping module name to DataFrame
        """
        logger.info("Acquiring NACC data")
        
        # Load data
        data = self.nacc_loader.load_nacc_data(modules=modules)
        
        # Validate clinical data if requested
        if validate and 'clinical' in data and not data['clinical'].empty:
            validation_result = self.schema_validator.validate(data['clinical'], 'nacc_clinical')
            self.schema_validator.log_validation_errors(validation_result)
            
            if not validation_result.valid:
                logger.error("Validation failed for NACC clinical data")
        
        # Track provenance for each module
        for module, df in data.items():
            if not df.empty:
                provenance_record = self.provenance_tracker.track_ingestion(
                    dataset_name=f"nacc_{module}",
                    data_source=DataSource.NACC,
                    data=df,
                    metadata={
                        'modules': modules,
                        'validated': validate
                    }
                )
                logger.info(f"Tracked provenance: {provenance_record.record_id}")
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"Acquired {total_records} total NACC records")
        
        return data
    
    def acquire_all_data(
        self,
        validate: bool = True
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Acquire data from all sources.
        
        Args:
            validate: Whether to validate data against schemas
        
        Returns:
            Nested dictionary with source -> data_type -> DataFrame
        """
        logger.info("Acquiring data from all sources")
        
        all_data = {
            'adni': self.acquire_adni_data(validate=validate),
            'oasis': self.acquire_oasis_data(validate=validate),
            'nacc': self.acquire_nacc_data(validate=validate)
        }
        
        # Calculate total records
        total_records = 0
        for source_data in all_data.values():
            total_records += sum(len(df) for df in source_data.values())
        
        logger.info(f"Acquired {total_records} total records from all sources")
        
        return all_data
    
    def get_data_summary(
        self,
        data: Dict[str, Dict[str, pd.DataFrame]]
    ) -> pd.DataFrame:
        """
        Get summary statistics for acquired data.
        
        Args:
            data: Nested dictionary of acquired data
        
        Returns:
            DataFrame with summary statistics
        """
        summary_rows = []
        
        for source, source_data in data.items():
            for data_type, df in source_data.items():
                summary_rows.append({
                    'source': source,
                    'data_type': data_type,
                    'num_records': len(df),
                    'num_columns': len(df.columns),
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                    'has_nulls': df.isnull().any().any(),
                    'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                })
        
        summary_df = pd.DataFrame(summary_rows)
        return summary_df
