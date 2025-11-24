"""Parsers for ADNI data formats."""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CognitiveAssessmentParser:
    """Parser for ADNI cognitive assessment data."""
    
    def __init__(self):
        """Initialize cognitive assessment parser."""
        self.expected_columns = [
            'patient_id', 'visit_date', 'mmse_score', 'adas_cog_score',
            'cdr_global', 'cdr_sob', 'moca_score'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse cognitive assessment data.
        
        Args:
            raw_data: Raw DataFrame from ADNI
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty cognitive assessment data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} cognitive assessment records")
        
        parsed = pd.DataFrame()
        
        # Map ADNI column names to standardized names
        column_mapping = {
            'RID': 'patient_id',
            'EXAMDATE': 'visit_date',
            'MMSE': 'mmse_score',
            'ADAS_COG': 'adas_cog_score',
            'CDGLOBAL': 'cdr_global',
            'CDRSB': 'cdr_sob',
            'MOCA': 'moca_score'
        }
        
        # Rename columns if they exist
        for adni_col, std_col in column_mapping.items():
            if adni_col in raw_data.columns:
                parsed[std_col] = raw_data[adni_col]
            else:
                parsed[std_col] = np.nan
        
        # Convert date column
        if 'visit_date' in parsed.columns:
            parsed['visit_date'] = pd.to_datetime(parsed['visit_date'], errors='coerce')
        
        # Validate score ranges
        if 'mmse_score' in parsed.columns:
            parsed['mmse_score'] = pd.to_numeric(parsed['mmse_score'], errors='coerce')
            parsed.loc[~parsed['mmse_score'].between(0, 30), 'mmse_score'] = np.nan
        
        if 'moca_score' in parsed.columns:
            parsed['moca_score'] = pd.to_numeric(parsed['moca_score'], errors='coerce')
            parsed.loc[~parsed['moca_score'].between(0, 30), 'moca_score'] = np.nan
        
        if 'cdr_global' in parsed.columns:
            parsed['cdr_global'] = pd.to_numeric(parsed['cdr_global'], errors='coerce')
            parsed.loc[~parsed['cdr_global'].between(0, 3), 'cdr_global'] = np.nan
        
        # Add metadata
        parsed['data_source'] = 'ADNI'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} cognitive assessment records")
        return parsed


class CSFBiomarkerParser:
    """Parser for ADNI CSF biomarker data."""
    
    def __init__(self):
        """Initialize CSF biomarker parser."""
        self.expected_columns = [
            'patient_id', 'visit_date', 'csf_ab42', 'csf_tau',
            'csf_ptau', 'ab42_tau_ratio', 'ptau_tau_ratio'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse CSF biomarker data.
        
        Args:
            raw_data: Raw DataFrame from ADNI
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty CSF biomarker data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} CSF biomarker records")
        
        parsed = pd.DataFrame()
        
        # Map ADNI column names to standardized names
        column_mapping = {
            'RID': 'patient_id',
            'EXAMDATE': 'visit_date',
            'ABETA': 'csf_ab42',
            'TAU': 'csf_tau',
            'PTAU': 'csf_ptau'
        }
        
        # Rename columns if they exist
        for adni_col, std_col in column_mapping.items():
            if adni_col in raw_data.columns:
                parsed[std_col] = raw_data[adni_col]
            else:
                parsed[std_col] = np.nan
        
        # Convert date column
        if 'visit_date' in parsed.columns:
            parsed['visit_date'] = pd.to_datetime(parsed['visit_date'], errors='coerce')
        
        # Convert biomarker values to numeric
        for col in ['csf_ab42', 'csf_tau', 'csf_ptau']:
            if col in parsed.columns:
                parsed[col] = pd.to_numeric(parsed[col], errors='coerce')
        
        # Calculate ratios
        if 'csf_ab42' in parsed.columns and 'csf_tau' in parsed.columns:
            parsed['ab42_tau_ratio'] = parsed['csf_ab42'] / parsed['csf_tau']
        else:
            parsed['ab42_tau_ratio'] = np.nan
        
        if 'csf_ptau' in parsed.columns and 'csf_tau' in parsed.columns:
            parsed['ptau_tau_ratio'] = parsed['csf_ptau'] / parsed['csf_tau']
        else:
            parsed['ptau_tau_ratio'] = np.nan
        
        # Validate ranges (typical CSF values in pg/mL)
        if 'csf_ab42' in parsed.columns:
            parsed.loc[~parsed['csf_ab42'].between(0, 2000), 'csf_ab42'] = np.nan
        
        if 'csf_tau' in parsed.columns:
            parsed.loc[~parsed['csf_tau'].between(0, 1500), 'csf_tau'] = np.nan
        
        if 'csf_ptau' in parsed.columns:
            parsed.loc[~parsed['csf_ptau'].between(0, 200), 'csf_ptau'] = np.nan
        
        # Add metadata
        parsed['data_source'] = 'ADNI'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} CSF biomarker records")
        return parsed


class MRIMetadataParser:
    """Parser for ADNI MRI metadata."""
    
    def __init__(self):
        """Initialize MRI metadata parser."""
        self.expected_columns = [
            'patient_id', 'visit_date', 'scan_date', 'field_strength',
            'manufacturer', 'hippocampus_volume', 'ventricle_volume',
            'whole_brain_volume', 'icv'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse MRI metadata.
        
        Args:
            raw_data: Raw DataFrame from ADNI
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty MRI metadata")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} MRI metadata records")
        
        parsed = pd.DataFrame()
        
        # Map ADNI column names to standardized names
        column_mapping = {
            'RID': 'patient_id',
            'EXAMDATE': 'visit_date',
            'SCANDATE': 'scan_date',
            'MAGSTRENGTH': 'field_strength',
            'MANUFACTURER': 'manufacturer',
            'HIPPO': 'hippocampus_volume',
            'VENTRICLES': 'ventricle_volume',
            'WHOLEBRAIN': 'whole_brain_volume',
            'ICV': 'icv'
        }
        
        # Rename columns if they exist
        for adni_col, std_col in column_mapping.items():
            if adni_col in raw_data.columns:
                parsed[std_col] = raw_data[adni_col]
            else:
                parsed[std_col] = np.nan
        
        # Convert date columns
        for date_col in ['visit_date', 'scan_date']:
            if date_col in parsed.columns:
                parsed[date_col] = pd.to_datetime(parsed[date_col], errors='coerce')
        
        # Convert numeric columns
        numeric_cols = ['field_strength', 'hippocampus_volume', 'ventricle_volume',
                       'whole_brain_volume', 'icv']
        for col in numeric_cols:
            if col in parsed.columns:
                parsed[col] = pd.to_numeric(parsed[col], errors='coerce')
        
        # Validate field strength (typical values: 1.5T or 3T)
        if 'field_strength' in parsed.columns:
            parsed.loc[~parsed['field_strength'].isin([1.5, 3.0]), 'field_strength'] = np.nan
        
        # Add metadata
        parsed['data_source'] = 'ADNI'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} MRI metadata records")
        return parsed


class GeneticDataParser:
    """Parser for ADNI genetic data (APOE genotype)."""
    
    def __init__(self):
        """Initialize genetic data parser."""
        self.expected_columns = [
            'patient_id', 'apoe_genotype', 'apoe_e4_count', 'apoe_risk_category'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse genetic data.
        
        Args:
            raw_data: Raw DataFrame from ADNI
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty genetic data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} genetic data records")
        
        parsed = pd.DataFrame()
        
        # Map ADNI column names to standardized names
        column_mapping = {
            'RID': 'patient_id',
            'APGEN1': 'apoe_allele1',
            'APGEN2': 'apoe_allele2'
        }
        
        # Rename columns if they exist
        for adni_col, std_col in column_mapping.items():
            if adni_col in raw_data.columns:
                parsed[std_col] = raw_data[adni_col]
        
        # Create genotype string
        if 'apoe_allele1' in parsed.columns and 'apoe_allele2' in parsed.columns:
            parsed['apoe_genotype'] = (
                'e' + parsed['apoe_allele1'].astype(str) + '/' +
                'e' + parsed['apoe_allele2'].astype(str)
            )
        else:
            parsed['apoe_genotype'] = np.nan
        
        # Count e4 alleles
        if 'apoe_allele1' in parsed.columns and 'apoe_allele2' in parsed.columns:
            parsed['apoe_e4_count'] = (
                (parsed['apoe_allele1'] == 4).astype(int) +
                (parsed['apoe_allele2'] == 4).astype(int)
            )
        else:
            parsed['apoe_e4_count'] = np.nan
        
        # Determine risk category
        def categorize_risk(e4_count):
            if pd.isna(e4_count):
                return np.nan
            elif e4_count == 0:
                return 'low'
            elif e4_count == 1:
                return 'moderate'
            else:  # e4_count == 2
                return 'high'
        
        if 'apoe_e4_count' in parsed.columns:
            parsed['apoe_risk_category'] = parsed['apoe_e4_count'].apply(categorize_risk)
        else:
            parsed['apoe_risk_category'] = np.nan
        
        # Drop intermediate columns
        parsed = parsed.drop(columns=['apoe_allele1', 'apoe_allele2'], errors='ignore')
        
        # Add metadata
        parsed['data_source'] = 'ADNI'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} genetic data records")
        return parsed
