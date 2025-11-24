"""ADNI data loader for accessing Alzheimer's Disease Neuroimaging Initiative data."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ml_pipeline.config.settings import Settings
from ml_pipeline.data_ingestion.adni.parsers import (
    CognitiveAssessmentParser,
    CSFBiomarkerParser,
    MRIMetadataParser,
    GeneticDataParser
)

logger = logging.getLogger(__name__)


class ADNIDataLoader:
    """
    Loader for ADNI (Alzheimer's Disease Neuroimaging Initiative) data.
    
    Supports downloading and parsing:
    - Cognitive assessments (MMSE, ADAS-Cog, CDR)
    - CSF biomarkers (Aβ42, t-Tau, p-Tau)
    - MRI metadata and volumetric data
    - APOE genotype data
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize ADNI data loader.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        self.base_url = self.settings.ADNI_BASE_URL
        self.api_key = self.settings.ADNI_API_KEY
        self.data_dir = Path(self.settings.RAW_DATA_PATH) / "adni"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize parsers
        self.cognitive_parser = CognitiveAssessmentParser()
        self.biomarker_parser = CSFBiomarkerParser()
        self.mri_parser = MRIMetadataParser()
        self.genetic_parser = GeneticDataParser()
        
        # Setup HTTP session with retry logic
        self.session = self._create_session()
        
        logger.info("ADNI data loader initialized")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def download_adni_data(
        self,
        data_type: str,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        cohort: Optional[str] = None
    ) -> Path:
        """
        Download ADNI data for specified type and date range.
        
        Args:
            data_type: Type of data ('cognitive', 'biomarker', 'mri', 'genetic')
            date_range: Optional tuple of (start_date, end_date)
            cohort: Optional cohort filter (e.g., 'ADNI1', 'ADNI2', 'ADNI3')
        
        Returns:
            Path to downloaded data file
        
        Raises:
            ValueError: If data_type is invalid
            requests.RequestException: If download fails
        """
        valid_types = ['cognitive', 'biomarker', 'mri', 'genetic', 'demographics']
        if data_type not in valid_types:
            raise ValueError(f"Invalid data_type. Must be one of {valid_types}")
        
        logger.info(f"Downloading ADNI {data_type} data")
        
        # Build request parameters
        params = {
            'api_key': self.api_key,
            'data_type': data_type
        }
        
        if date_range:
            params['start_date'] = date_range[0].isoformat()
            params['end_date'] = date_range[1].isoformat()
        
        if cohort:
            params['cohort'] = cohort
        
        # For demo purposes, we'll simulate the download
        # In production, this would make actual API calls to ADNI
        output_file = self.data_dir / f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            # Simulated download - in production, replace with actual API call
            # response = self.session.get(f"{self.base_url}/data", params=params, timeout=30)
            # response.raise_for_status()
            # with open(output_file, 'wb') as f:
            #     f.write(response.content)
            
            # For now, create placeholder file
            logger.warning(f"Simulated download - creating placeholder file at {output_file}")
            output_file.touch()
            
            logger.info(f"Downloaded ADNI {data_type} data to {output_file}")
            return output_file
            
        except requests.RequestException as e:
            logger.error(f"Failed to download ADNI data: {e}")
            raise
    
    def load_cognitive_assessments(
        self,
        file_path: Optional[Path] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Load and parse cognitive assessment data.
        
        Args:
            file_path: Path to existing data file, or None to download
            date_range: Optional date range filter
        
        Returns:
            DataFrame with parsed cognitive assessments
        """
        if file_path is None:
            file_path = self.download_adni_data('cognitive', date_range)
        
        logger.info(f"Loading cognitive assessments from {file_path}")
        
        # Load raw data
        if file_path.exists() and file_path.stat().st_size > 0:
            raw_data = pd.read_csv(file_path)
        else:
            # Return empty DataFrame with expected schema
            raw_data = pd.DataFrame()
        
        # Parse using cognitive parser
        parsed_data = self.cognitive_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} cognitive assessment records")
        return parsed_data
    
    def load_csf_biomarkers(
        self,
        file_path: Optional[Path] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Load and parse CSF biomarker data.
        
        Args:
            file_path: Path to existing data file, or None to download
            date_range: Optional date range filter
        
        Returns:
            DataFrame with parsed CSF biomarkers
        """
        if file_path is None:
            file_path = self.download_adni_data('biomarker', date_range)
        
        logger.info(f"Loading CSF biomarkers from {file_path}")
        
        # Load raw data
        if file_path.exists() and file_path.stat().st_size > 0:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.DataFrame()
        
        # Parse using biomarker parser
        parsed_data = self.biomarker_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} CSF biomarker records")
        return parsed_data
    
    def load_mri_metadata(
        self,
        file_path: Optional[Path] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> pd.DataFrame:
        """
        Load and parse MRI metadata.
        
        Args:
            file_path: Path to existing data file, or None to download
            date_range: Optional date range filter
        
        Returns:
            DataFrame with parsed MRI metadata
        """
        if file_path is None:
            file_path = self.download_adni_data('mri', date_range)
        
        logger.info(f"Loading MRI metadata from {file_path}")
        
        # Load raw data
        if file_path.exists() and file_path.stat().st_size > 0:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.DataFrame()
        
        # Parse using MRI parser
        parsed_data = self.mri_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} MRI metadata records")
        return parsed_data
    
    def load_genetic_data(
        self,
        file_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Load and parse genetic data (APOE genotype).
        
        Args:
            file_path: Path to existing data file, or None to download
        
        Returns:
            DataFrame with parsed genetic data
        """
        if file_path is None:
            file_path = self.download_adni_data('genetic')
        
        logger.info(f"Loading genetic data from {file_path}")
        
        # Load raw data
        if file_path.exists() and file_path.stat().st_size > 0:
            raw_data = pd.read_csv(file_path)
        else:
            raw_data = pd.DataFrame()
        
        # Parse using genetic parser
        parsed_data = self.genetic_parser.parse(raw_data)
        
        logger.info(f"Loaded {len(parsed_data)} genetic data records")
        return parsed_data
    
    def load_all_data(
        self,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all ADNI data types.
        
        Args:
            date_range: Optional date range filter
        
        Returns:
            Dictionary mapping data type to DataFrame
        """
        logger.info("Loading all ADNI data")
        
        data = {
            'cognitive': self.load_cognitive_assessments(date_range=date_range),
            'biomarkers': self.load_csf_biomarkers(date_range=date_range),
            'mri': self.load_mri_metadata(date_range=date_range),
            'genetic': self.load_genetic_data()
        }
        
        total_records = sum(len(df) for df in data.values())
        logger.info(f"Loaded {total_records} total ADNI records across all data types")
        
        return data
