"""OASIS data loader for Open Access Series of Imaging Studies."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from ml_pipeline.config.settings import Settings
from ml_pipeline.data_ingestion.oasis.parsers import (
    MRIVolumetricParser,
    CDRDemographicsParser
)

logger = logging.getLogger(__name__)


class OASISDataLoader:
    """
    Loader for OASIS (Open Access Series of Imaging Studies) data.
    
    Supports loading:
    - MRI volumetric data
    - CDR scores
    - Demographics
    - Longitudinal data (OASIS-3)
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize OASIS data loader.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        self.data_dir = Path(self.settings.OASIS_DATA_PATH or (Path(self.settings.RAW_DATA_PATH) / "oasis"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize parsers
        self.mri_parser = MRIVolumetricParser()
        self.cdr_demographics_parser = CDRDemographicsParser()
        
        logger.info("OASIS data loader initialized")
    
    def download_oasis_data(self, version: str = "OASIS-3") -> Path:
        """
        Download OASIS dataset version.
        
        Args:
            version: OASIS version ('OASIS-1', 'OASIS-2', 'OASIS-3')
        
        Returns:
            Path to downloaded data directory
        
        Raises:
            ValueError: If version is invalid
        """
        valid_versions = ['OASIS-1', 'OASIS-2', 'OASIS-3']
        if version not in valid_versions:
            raise ValueError(f"Invalid version. Must be one of {valid_versions}")
        
        logger.info(f"Downloading OASIS {version} data")
        
        version_dir = self.data_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # For demo purposes, we'll simulate the download
        # In production, this would download from OASIS website or XNAT
        # OASIS data is typically downloaded manually from:
        # https://www.oasis-brains.org/
        
        logger.warning(f"Simulated download - OASIS data should be placed in {version_dir}")
        logger.info(f"OASIS {version} data directory: {version_dir}")
        
        return version_dir
    
    def load_oasis_data(
        self,
        version: str = "OASIS-3",
        data_dir: Optional[Path] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load OASIS dataset.
        
        Args:
            version: OASIS version to load
            data_dir: Optional custom data directory
        
        Returns:
            Dictionary with 'mri', 'demographics', and 'cdr' DataFrames
        """
        if data_dir is None:
            data_dir = self.data_dir / version
        
        logger.info(f"Loading OASIS {version} data from {data_dir}")
        
        # Load different data types
        mri_data = self.load_mri_volumetric(data_dir)
        demographics_cdr = self.load_cdr_demographics(data_dir)
        
        data = {
            'mri': mri_data,
            'demographics': demographics_cdr['demographics'],
            'cdr': demographics_cdr['cdr']
        }
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"Loaded {total_records} total OASIS records")
        
        return data
    
    def load_mri_volumetric(self, data_dir: Path) -> pd.DataFrame:
        """
        Load and parse MRI volumetric data.
        
        Args:
            data_dir: Directory containing OASIS data
        
        Returns:
            DataFrame with parsed MRI volumetric data
        """
        logger.info(f"Loading MRI volumetric data from {data_dir}")
        
        # Look for common OASIS file patterns
        mri_files = list(data_dir.glob("*MR*.csv")) + list(data_dir.glob("*volumetric*.csv"))
        
        if not mri_files:
            logger.warning(f"No MRI volumetric files found in {data_dir}")
            return pd.DataFrame()
        
        # Load and combine all MRI files
        dfs = []
        for file_path in mri_files:
            try:
                df = pd.read_csv(file_path)
                dfs.append(df)
                logger.info(f"Loaded {len(df)} records from {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine all dataframes
        raw_data = pd.concat(dfs, ignore_index=True)
        
        # Parse using MRI parser
        parsed_data = self.mri_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} MRI volumetric records")
        return parsed_data
    
    def load_cdr_demographics(self, data_dir: Path) -> Dict[str, pd.DataFrame]:
        """
        Load and parse CDR scores and demographics.
        
        Args:
            data_dir: Directory containing OASIS data
        
        Returns:
            Dictionary with 'demographics' and 'cdr' DataFrames
        """
        logger.info(f"Loading CDR and demographics from {data_dir}")
        
        # Look for common OASIS file patterns
        demo_files = (
            list(data_dir.glob("*demographics*.csv")) +
            list(data_dir.glob("*clinical*.csv")) +
            list(data_dir.glob("*CDR*.csv"))
        )
        
        if not demo_files:
            logger.warning(f"No demographics/CDR files found in {data_dir}")
            return {
                'demographics': pd.DataFrame(),
                'cdr': pd.DataFrame()
            }
        
        # Load and combine all files
        dfs = []
        for file_path in demo_files:
            try:
                df = pd.read_csv(file_path)
                dfs.append(df)
                logger.info(f"Loaded {len(df)} records from {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        if not dfs:
            return {
                'demographics': pd.DataFrame(),
                'cdr': pd.DataFrame()
            }
        
        # Combine all dataframes
        raw_data = pd.concat(dfs, ignore_index=True)
        
        # Parse using CDR/demographics parser
        parsed_data = self.cdr_demographics_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data['demographics'])} demographics and {len(parsed_data['cdr'])} CDR records")
        return parsed_data
    
    def load_longitudinal_data(
        self,
        data_dir: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Load longitudinal data from OASIS-3.
        
        Args:
            data_dir: Optional custom data directory
        
        Returns:
            DataFrame with longitudinal visit data
        """
        if data_dir is None:
            data_dir = self.data_dir / "OASIS-3"
        
        logger.info(f"Loading OASIS-3 longitudinal data from {data_dir}")
        
        # Load all data types
        data = self.load_oasis_data(version="OASIS-3", data_dir=data_dir)
        
        # Merge MRI, demographics, and CDR data by patient_id and visit_date
        longitudinal = data['mri'].copy()
        
        if not data['demographics'].empty:
            longitudinal = longitudinal.merge(
                data['demographics'],
                on='patient_id',
                how='left',
                suffixes=('', '_demo')
            )
        
        if not data['cdr'].empty:
            longitudinal = longitudinal.merge(
                data['cdr'],
                on=['patient_id', 'visit_date'],
                how='left',
                suffixes=('', '_cdr')
            )
        
        # Sort by patient and visit date
        if 'visit_date' in longitudinal.columns:
            longitudinal = longitudinal.sort_values(['patient_id', 'visit_date'])
        
        logger.info(f"Created longitudinal dataset with {len(longitudinal)} records")
        return longitudinal
