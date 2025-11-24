"""Parsers for OASIS data formats."""

import logging
from typing import Dict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MRIVolumetricParser:
    """Parser for OASIS MRI volumetric data."""
    
    def __init__(self):
        """Initialize MRI volumetric parser."""
        self.expected_columns = [
            'patient_id', 'visit_date', 'scan_id', 'hippocampus_left',
            'hippocampus_right', 'hippocampus_total', 'entorhinal_cortex',
            'ventricle_volume', 'whole_brain_volume', 'icv', 'normalized_brain_volume'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse MRI volumetric data.
        
        Args:
            raw_data: Raw DataFrame from OASIS
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty MRI volumetric data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} MRI volumetric records")
        
        parsed = pd.DataFrame()
        
        # Map OASIS column names to standardized names
        # OASIS uses different naming conventions across versions
        column_mapping = {
            # Common identifiers
            'Subject': 'patient_id',
            'MR ID': 'scan_id',
            'MRI ID': 'scan_id',
            'Visit': 'visit_date',
            'Age': 'age',
            
            # Volumetric measures (in mm³)
            'eTIV': 'icv',
            'nWBV': 'normalized_brain_volume',
            'ASF': 'atlas_scaling_factor',
            
            # Hippocampus
            'Left-Hippocampus': 'hippocampus_left',
            'Right-Hippocampus': 'hippocampus_right',
            
            # Other structures
            'Left-Lateral-Ventricle': 'left_ventricle',
            'Right-Lateral-Ventricle': 'right_ventricle',
            'Left-Entorhinal': 'entorhinal_left',
            'Right-Entorhinal': 'entorhinal_right',
            'BrainSegVol': 'whole_brain_volume',
            'BrainSegVolNotVent': 'brain_volume_no_ventricles'
        }
        
        # Rename columns if they exist
        for oasis_col, std_col in column_mapping.items():
            if oasis_col in raw_data.columns:
                parsed[std_col] = raw_data[oasis_col]
        
        # Calculate derived measures
        if 'hippocampus_left' in parsed.columns and 'hippocampus_right' in parsed.columns:
            parsed['hippocampus_total'] = (
                pd.to_numeric(parsed['hippocampus_left'], errors='coerce') +
                pd.to_numeric(parsed['hippocampus_right'], errors='coerce')
            )
        
        if 'left_ventricle' in parsed.columns and 'right_ventricle' in parsed.columns:
            parsed['ventricle_volume'] = (
                pd.to_numeric(parsed['left_ventricle'], errors='coerce') +
                pd.to_numeric(parsed['right_ventricle'], errors='coerce')
            )
        
        if 'entorhinal_left' in parsed.columns and 'entorhinal_right' in parsed.columns:
            parsed['entorhinal_cortex'] = (
                pd.to_numeric(parsed['entorhinal_left'], errors='coerce') +
                pd.to_numeric(parsed['entorhinal_right'], errors='coerce')
            )
        
        # Convert date column if present
        if 'visit_date' in parsed.columns:
            parsed['visit_date'] = pd.to_datetime(parsed['visit_date'], errors='coerce')
        
        # Convert numeric columns
        numeric_cols = [
            'hippocampus_left', 'hippocampus_right', 'hippocampus_total',
            'entorhinal_cortex', 'ventricle_volume', 'whole_brain_volume',
            'icv', 'normalized_brain_volume', 'age'
        ]
        for col in numeric_cols:
            if col in parsed.columns:
                parsed[col] = pd.to_numeric(parsed[col], errors='coerce')
        
        # Normalize volumes by ICV if not already normalized
        if 'icv' in parsed.columns and parsed['icv'].notna().any():
            for vol_col in ['hippocampus_total', 'ventricle_volume', 'whole_brain_volume']:
                if vol_col in parsed.columns:
                    normalized_col = f'{vol_col}_normalized'
                    parsed[normalized_col] = parsed[vol_col] / parsed['icv']
        
        # Validate ranges (volumes should be positive)
        volume_cols = [col for col in parsed.columns if 'volume' in col.lower() or 'hippocampus' in col.lower()]
        for col in volume_cols:
            if col in parsed.columns:
                parsed.loc[parsed[col] < 0, col] = np.nan
        
        # Add metadata
        parsed['data_source'] = 'OASIS'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} MRI volumetric records")
        return parsed


class CDRDemographicsParser:
    """Parser for OASIS CDR scores and demographics."""
    
    def __init__(self):
        """Initialize CDR and demographics parser."""
        self.demographics_columns = [
            'patient_id', 'age', 'sex', 'education_years', 'race', 'ethnicity'
        ]
        self.cdr_columns = [
            'patient_id', 'visit_date', 'cdr_global', 'cdr_sob',
            'cdr_memory', 'cdr_orientation', 'cdr_judgment',
            'cdr_community', 'cdr_home', 'cdr_personal_care'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Parse CDR and demographics data.
        
        Args:
            raw_data: Raw DataFrame from OASIS
        
        Returns:
            Dictionary with 'demographics' and 'cdr' DataFrames
        """
        if raw_data.empty:
            logger.warning("Empty CDR/demographics data")
            return {
                'demographics': pd.DataFrame(columns=self.demographics_columns),
                'cdr': pd.DataFrame(columns=self.cdr_columns)
            }
        
        logger.info(f"Parsing {len(raw_data)} CDR/demographics records")
        
        # Parse demographics
        demographics = self._parse_demographics(raw_data)
        
        # Parse CDR scores
        cdr = self._parse_cdr(raw_data)
        
        logger.info(f"Successfully parsed {len(demographics)} demographics and {len(cdr)} CDR records")
        
        return {
            'demographics': demographics,
            'cdr': cdr
        }
    
    def _parse_demographics(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Parse demographics data."""
        demographics = pd.DataFrame()
        
        # Map OASIS column names to standardized names
        column_mapping = {
            'Subject': 'patient_id',
            'M/F': 'sex',
            'Hand': 'handedness',
            'Age': 'age',
            'Educ': 'education_years',
            'SES': 'socioeconomic_status',
            'Race': 'race',
            'Ethnicity': 'ethnicity'
        }
        
        # Rename columns if they exist
        for oasis_col, std_col in column_mapping.items():
            if oasis_col in raw_data.columns:
                demographics[std_col] = raw_data[oasis_col]
        
        # Standardize sex values
        if 'sex' in demographics.columns:
            demographics['sex'] = demographics['sex'].map({
                'M': 'M',
                'F': 'F',
                'Male': 'M',
                'Female': 'F'
            })
        
        # Convert numeric columns
        if 'age' in demographics.columns:
            demographics['age'] = pd.to_numeric(demographics['age'], errors='coerce')
            # Validate age range
            demographics.loc[~demographics['age'].between(18, 120), 'age'] = np.nan
        
        if 'education_years' in demographics.columns:
            demographics['education_years'] = pd.to_numeric(demographics['education_years'], errors='coerce')
            # Validate education range
            demographics.loc[~demographics['education_years'].between(0, 30), 'education_years'] = np.nan
        
        # Remove duplicates (keep first occurrence per patient)
        if 'patient_id' in demographics.columns:
            demographics = demographics.drop_duplicates(subset=['patient_id'], keep='first')
        
        # Add metadata
        demographics['data_source'] = 'OASIS'
        demographics['ingestion_timestamp'] = pd.Timestamp.now()
        
        return demographics
    
    def _parse_cdr(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Parse CDR scores."""
        cdr = pd.DataFrame()
        
        # Map OASIS column names to standardized names
        column_mapping = {
            'Subject': 'patient_id',
            'Visit': 'visit_date',
            'CDR': 'cdr_global',
            'CDRSUM': 'cdr_sob',
            'CDMEMORY': 'cdr_memory',
            'CDORIENT': 'cdr_orientation',
            'CDJUDGE': 'cdr_judgment',
            'CDCOMMUN': 'cdr_community',
            'CDHOME': 'cdr_home',
            'CDCARE': 'cdr_personal_care'
        }
        
        # Rename columns if they exist
        for oasis_col, std_col in column_mapping.items():
            if oasis_col in raw_data.columns:
                cdr[std_col] = raw_data[oasis_col]
        
        # Convert date column
        if 'visit_date' in cdr.columns:
            cdr['visit_date'] = pd.to_datetime(cdr['visit_date'], errors='coerce')
        
        # Convert CDR scores to numeric
        cdr_cols = [col for col in cdr.columns if col.startswith('cdr_')]
        for col in cdr_cols:
            cdr[col] = pd.to_numeric(cdr[col], errors='coerce')
        
        # Validate CDR global score (0, 0.5, 1, 2, 3)
        if 'cdr_global' in cdr.columns:
            valid_cdr = [0, 0.5, 1, 2, 3]
            cdr.loc[~cdr['cdr_global'].isin(valid_cdr), 'cdr_global'] = np.nan
        
        # Validate CDR sum of boxes (0-18)
        if 'cdr_sob' in cdr.columns:
            cdr.loc[~cdr['cdr_sob'].between(0, 18), 'cdr_sob'] = np.nan
        
        # Add metadata
        cdr['data_source'] = 'OASIS'
        cdr['ingestion_timestamp'] = pd.Timestamp.now()
        
        return cdr
