"""NACC data loader for National Alzheimer's Coordinating Center data."""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from ml_pipeline.config.settings import Settings
from ml_pipeline.data_ingestion.nacc.parsers import (
    ClinicalAssessmentParser,
    MedicalHistoryParser
)

logger = logging.getLogger(__name__)


class NACCDataLoader:
    """
    Loader for NACC (National Alzheimer's Coordinating Center) data.
    
    Supports loading:
    - Clinical assessments (UDS forms)
    - Cognitive test batteries
    - Medical history
    - Neuropathology data
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize NACC data loader.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        self.data_dir = Path(self.settings.NACC_DATA_PATH or (Path(self.settings.RAW_DATA_PATH) / "nacc"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize parsers
        self.clinical_parser = ClinicalAssessmentParser()
        self.medical_history_parser = MedicalHistoryParser()
        
        logger.info("NACC data loader initialized")
    
    def download_nacc_data(self, modules: List[str]) -> Path:
        """
        Download NACC data modules.
        
        Args:
            modules: List of NACC modules to download
                    (e.g., ['UDS', 'neuropath', 'biomarkers'])
        
        Returns:
            Path to downloaded data directory
        
        Raises:
            ValueError: If modules list is empty
        """
        if not modules:
            raise ValueError("At least one module must be specified")
        
        logger.info(f"Downloading NACC modules: {modules}")
        
        # For demo purposes, we'll simulate the download
        # In production, NACC data is typically requested through their website
        # and downloaded manually: https://naccdata.org/
        
        for module in modules:
            module_dir = self.data_dir / module
            module_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Simulated download - NACC {module} data should be placed in {module_dir}")
        
        logger.info(f"NACC data directory: {self.data_dir}")
        return self.data_dir
    
    def load_nacc_data(
        self,
        modules: Optional[List[str]] = None,
        data_dir: Optional[Path] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load NACC dataset.
        
        Args:
            modules: Optional list of modules to load. If None, loads all available.
            data_dir: Optional custom data directory
        
        Returns:
            Dictionary with module names as keys and DataFrames as values
        """
        if data_dir is None:
            data_dir = self.data_dir
        
        logger.info(f"Loading NACC data from {data_dir}")
        
        # Load different data types
        clinical = self.load_clinical_assessments(data_dir)
        medical_history = self.load_medical_history(data_dir)
        
        data = {
            'clinical': clinical,
            'medical_history': medical_history
        }
        
        # Filter by requested modules if specified
        if modules:
            data = {k: v for k, v in data.items() if k in modules}
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"Loaded {total_records} total NACC records")
        
        return data
    
    def load_clinical_assessments(self, data_dir: Path) -> pd.DataFrame:
        """
        Load and parse clinical assessment data (UDS forms).
        
        Args:
            data_dir: Directory containing NACC data
        
        Returns:
            DataFrame with parsed clinical assessments
        """
        logger.info(f"Loading clinical assessments from {data_dir}")
        
        # Look for UDS (Uniform Data Set) files
        uds_files = (
            list(data_dir.glob("*UDS*.csv")) +
            list(data_dir.glob("*clinical*.csv")) +
            list(data_dir.glob("*assessment*.csv"))
        )
        
        if not uds_files:
            logger.warning(f"No clinical assessment files found in {data_dir}")
            return pd.DataFrame()
        
        # Load and combine all clinical files
        dfs = []
        for file_path in uds_files:
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
        
        # Parse using clinical parser
        parsed_data = self.clinical_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} clinical assessment records")
        return parsed_data
    
    def load_medical_history(self, data_dir: Path) -> pd.DataFrame:
        """
        Load and parse medical history data.
        
        Args:
            data_dir: Directory containing NACC data
        
        Returns:
            DataFrame with parsed medical history
        """
        logger.info(f"Loading medical history from {data_dir}")
        
        # Look for medical history files
        history_files = (
            list(data_dir.glob("*medical*.csv")) +
            list(data_dir.glob("*history*.csv")) +
            list(data_dir.glob("*health*.csv"))
        )
        
        if not history_files:
            logger.warning(f"No medical history files found in {data_dir}")
            return pd.DataFrame()
        
        # Load and combine all history files
        dfs = []
        for file_path in history_files:
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
        
        # Parse using medical history parser
        parsed_data = self.medical_history_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} medical history records")
        return parsed_data
    
    def load_neuropathology(self, data_dir: Optional[Path] = None) -> pd.DataFrame:
        """
        Load neuropathology data.
        
        Args:
            data_dir: Optional custom data directory
        
        Returns:
            DataFrame with neuropathology data
        """
        if data_dir is None:
            data_dir = self.data_dir
        
        logger.info(f"Loading neuropathology data from {data_dir}")
        
        # Look for neuropathology files
        neuropath_files = list(data_dir.glob("*neuropath*.csv"))
        
        if not neuropath_files:
            logger.warning(f"No neuropathology files found in {data_dir}")
            return pd.DataFrame()
        
        # Load and combine all neuropathology files
        dfs = []
        for file_path in neuropath_files:
            try:
                df = pd.read_csv(file_path)
                dfs.append(df)
                logger.info(f"Loaded {len(df)} records from {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine all dataframes
        neuropath_data = pd.concat(dfs, ignore_index=True)
        
        # Add metadata
        neuropath_data['data_source'] = 'NACC'
        neuropath_data['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Loaded {len(neuropath_data)} neuropathology records")
        return neuropath_data
    
    def merge_nacc_data(
        self,
        clinical: pd.DataFrame,
        medical_history: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge clinical and medical history data.
        
        Args:
            clinical: Clinical assessment DataFrame
            medical_history: Medical history DataFrame
        
        Returns:
            Merged DataFrame
        """
        logger.info("Merging NACC clinical and medical history data")
        
        if clinical.empty:
            return medical_history
        if medical_history.empty:
            return clinical
        
        # Merge on patient_id
        merged = clinical.merge(
            medical_history,
            on='patient_id',
            how='outer',
            suffixes=('_clinical', '_history')
        )
        
        logger.info(f"Merged dataset contains {len(merged)} records")
        return merged
