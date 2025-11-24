"""Parsers for NACC data formats."""

import logging
from typing import Dict, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ClinicalAssessmentParser:
    """Parser for NACC clinical assessment data (UDS forms)."""
    
    def __init__(self):
        """Initialize clinical assessment parser."""
        self.expected_columns = [
            'patient_id', 'visit_date', 'visit_number', 'mmse_score',
            'moca_score', 'cdr_global', 'cdr_sob', 'diagnosis',
            'functional_status', 'behavioral_symptoms'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse clinical assessment data.
        
        Args:
            raw_data: Raw DataFrame from NACC
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty clinical assessment data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} clinical assessment records")
        
        parsed = pd.DataFrame()
        
        # Map NACC column names to standardized names
        # NACC uses specific UDS variable names
        column_mapping = {
            'NACCID': 'patient_id',
            'VISITNUM': 'visit_number',
            'VISITDATE': 'visit_date',
            'VISITMO': 'visit_month',
            'VISITDAY': 'visit_day',
            'VISITYR': 'visit_year',
            
            # Cognitive assessments
            'MMSE': 'mmse_score',
            'MMSECOMP': 'mmse_complete',
            'MOCA': 'moca_score',
            'MOCACOMP': 'moca_complete',
            
            # CDR scores
            'CDRGLOB': 'cdr_global',
            'CDRSB': 'cdr_sob',
            'MEMORY': 'cdr_memory',
            'ORIENT': 'cdr_orientation',
            'JUDGMENT': 'cdr_judgment',
            'COMMUN': 'cdr_community',
            'HOMEHOBB': 'cdr_home',
            'PERSCARE': 'cdr_personal_care',
            
            # Diagnosis
            'NORMCOG': 'normal_cognition',
            'DEMENTED': 'dementia',
            'NACCALZD': 'alzheimer_diagnosis',
            'NACCALZP': 'alzheimer_probable',
            
            # Functional status
            'NACCFAQ': 'faq_score',
            'NACCGDS': 'gds_score',
            
            # Behavioral
            'NPIQINF': 'npi_informant',
            'NPIQINFX': 'npi_score'
        }
        
        # Rename columns if they exist
        for nacc_col, std_col in column_mapping.items():
            if nacc_col in raw_data.columns:
                parsed[std_col] = raw_data[nacc_col]
        
        # Construct visit date from components if not directly available
        if 'visit_date' not in parsed.columns:
            if all(col in parsed.columns for col in ['visit_year', 'visit_month', 'visit_day']):
                try:
                    parsed['visit_date'] = pd.to_datetime(
                        parsed[['visit_year', 'visit_month', 'visit_day']].rename(
                            columns={'visit_year': 'year', 'visit_month': 'month', 'visit_day': 'day'}
                        ),
                        errors='coerce'
                    )
                except Exception as e:
                    logger.warning(f"Failed to construct visit_date: {e}")
                    parsed['visit_date'] = pd.NaT
        else:
            parsed['visit_date'] = pd.to_datetime(parsed['visit_date'], errors='coerce')
        
        # Convert cognitive scores to numeric
        if 'mmse_score' in parsed.columns:
            parsed['mmse_score'] = pd.to_numeric(parsed['mmse_score'], errors='coerce')
            # Validate MMSE range (0-30)
            parsed.loc[~parsed['mmse_score'].between(0, 30), 'mmse_score'] = np.nan
        
        if 'moca_score' in parsed.columns:
            parsed['moca_score'] = pd.to_numeric(parsed['moca_score'], errors='coerce')
            # Validate MoCA range (0-30)
            parsed.loc[~parsed['moca_score'].between(0, 30), 'moca_score'] = np.nan
        
        # Convert CDR scores
        if 'cdr_global' in parsed.columns:
            parsed['cdr_global'] = pd.to_numeric(parsed['cdr_global'], errors='coerce')
            # Validate CDR global (0, 0.5, 1, 2, 3)
            valid_cdr = [0, 0.5, 1, 2, 3]
            parsed.loc[~parsed['cdr_global'].isin(valid_cdr), 'cdr_global'] = np.nan
        
        if 'cdr_sob' in parsed.columns:
            parsed['cdr_sob'] = pd.to_numeric(parsed['cdr_sob'], errors='coerce')
            # Validate CDR sum of boxes (0-18)
            parsed.loc[~parsed['cdr_sob'].between(0, 18), 'cdr_sob'] = np.nan
        
        # Create diagnosis field
        if 'normal_cognition' in parsed.columns and 'dementia' in parsed.columns:
            parsed['diagnosis'] = 'Unknown'
            parsed.loc[parsed['normal_cognition'] == 1, 'diagnosis'] = 'Normal'
            parsed.loc[parsed['dementia'] == 1, 'diagnosis'] = 'Dementia'
            
            # Refine with Alzheimer's diagnosis
            if 'alzheimer_diagnosis' in parsed.columns:
                parsed.loc[
                    (parsed['dementia'] == 1) & (parsed['alzheimer_diagnosis'] == 1),
                    'diagnosis'
                ] = 'Alzheimer'
        
        # Convert functional scores
        if 'faq_score' in parsed.columns:
            parsed['faq_score'] = pd.to_numeric(parsed['faq_score'], errors='coerce')
            parsed.loc[~parsed['faq_score'].between(0, 30), 'faq_score'] = np.nan
        
        if 'gds_score' in parsed.columns:
            parsed['gds_score'] = pd.to_numeric(parsed['gds_score'], errors='coerce')
            parsed.loc[~parsed['gds_score'].between(0, 15), 'gds_score'] = np.nan
        
        # Add metadata
        parsed['data_source'] = 'NACC'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} clinical assessment records")
        return parsed


class MedicalHistoryParser:
    """Parser for NACC medical history data."""
    
    def __init__(self):
        """Initialize medical history parser."""
        self.expected_columns = [
            'patient_id', 'hypertension', 'diabetes', 'hyperlipidemia',
            'cardiovascular_disease', 'stroke', 'tbi', 'depression',
            'smoking_status', 'alcohol_use', 'bmi', 'family_history_dementia'
        ]
    
    def parse(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse medical history data.
        
        Args:
            raw_data: Raw DataFrame from NACC
        
        Returns:
            Parsed DataFrame with standardized columns
        """
        if raw_data.empty:
            logger.warning("Empty medical history data")
            return pd.DataFrame(columns=self.expected_columns)
        
        logger.info(f"Parsing {len(raw_data)} medical history records")
        
        parsed = pd.DataFrame()
        
        # Map NACC column names to standardized names
        column_mapping = {
            'NACCID': 'patient_id',
            
            # Medical conditions (typically 0=No, 1=Yes, 8=N/A, 9=Unknown)
            'HYPERTEN': 'hypertension',
            'DIABETES': 'diabetes',
            'HYPERCHO': 'hyperlipidemia',
            'B12DEF': 'b12_deficiency',
            'THYROID': 'thyroid_disease',
            
            # Cardiovascular
            'CVHATT': 'heart_attack',
            'CVAFIB': 'atrial_fibrillation',
            'CVANGIO': 'angioplasty',
            'CVBYPASS': 'bypass_surgery',
            'CVPACE': 'pacemaker',
            'CVCHF': 'congestive_heart_failure',
            
            # Neurological
            'STROKE': 'stroke',
            'TIA': 'tia',
            'PD': 'parkinsons',
            'SEIZURES': 'seizures',
            'TBI': 'tbi',
            'TBIBRIEF': 'tbi_brief',
            'TBIEXTEN': 'tbi_extended',
            
            # Psychiatric
            'DEP2YRS': 'depression',
            'DEPOTHR': 'depression_other',
            'ANXIETY': 'anxiety',
            'PSYCHOSIS': 'psychosis',
            
            # Lifestyle
            'SMOKYRS': 'smoking_years',
            'PACKSPER': 'packs_per_day',
            'ALCOHOL': 'alcohol_use',
            'ABUSOTHR': 'substance_abuse',
            
            # Physical measures
            'HEIGHT': 'height',
            'WEIGHT': 'weight',
            
            # Family history
            'NACCFAM': 'family_history_dementia',
            'NACCMOM': 'mother_dementia',
            'NACCDAD': 'father_dementia'
        }
        
        # Rename columns if they exist
        for nacc_col, std_col in column_mapping.items():
            if nacc_col in raw_data.columns:
                parsed[std_col] = raw_data[nacc_col]
        
        # Convert binary medical conditions (0/1)
        binary_conditions = [
            'hypertension', 'diabetes', 'hyperlipidemia', 'stroke', 'tbi',
            'depression', 'heart_attack', 'atrial_fibrillation', 'parkinsons',
            'seizures', 'anxiety', 'family_history_dementia'
        ]
        
        for condition in binary_conditions:
            if condition in parsed.columns:
                parsed[condition] = pd.to_numeric(parsed[condition], errors='coerce')
                # Convert to boolean (1=Yes, 0=No, others=NaN)
                parsed[condition] = parsed[condition].map({0: False, 1: True})
        
        # Calculate BMI if height and weight available
        if 'height' in parsed.columns and 'weight' in parsed.columns:
            height_m = pd.to_numeric(parsed['height'], errors='coerce') * 0.0254  # inches to meters
            weight_kg = pd.to_numeric(parsed['weight'], errors='coerce') * 0.453592  # pounds to kg
            parsed['bmi'] = weight_kg / (height_m ** 2)
            # Validate BMI range
            parsed.loc[~parsed['bmi'].between(10, 60), 'bmi'] = np.nan
        
        # Determine smoking status
        if 'smoking_years' in parsed.columns:
            smoking_years = pd.to_numeric(parsed['smoking_years'], errors='coerce')
            parsed['smoking_status'] = 'Never'
            parsed.loc[smoking_years > 0, 'smoking_status'] = 'Former'
            # Note: NACC doesn't always distinguish current vs former clearly
        
        # Determine cardiovascular disease (any cardiovascular condition)
        cv_conditions = [
            'heart_attack', 'atrial_fibrillation', 'congestive_heart_failure',
            'angioplasty', 'bypass_surgery'
        ]
        cv_cols_present = [col for col in cv_conditions if col in parsed.columns]
        if cv_cols_present:
            parsed['cardiovascular_disease'] = parsed[cv_cols_present].any(axis=1)
        
        # Remove duplicates (keep first occurrence per patient)
        if 'patient_id' in parsed.columns:
            parsed = parsed.drop_duplicates(subset=['patient_id'], keep='first')
        
        # Add metadata
        parsed['data_source'] = 'NACC'
        parsed['ingestion_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Successfully parsed {len(parsed)} medical history records")
        return parsed
