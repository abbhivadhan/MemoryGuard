"""PHI Detection Module - Detects Protected Health Information in datasets"""

import re
import pandas as pd
from typing import List, Dict, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PHIDetector:
    """Detect Protected Health Information (PHI) according to HIPAA Safe Harbor method"""
    
    # 18 HIPAA identifiers
    HIPAA_IDENTIFIERS = [
        'names',
        'geographic_subdivisions',
        'dates',
        'phone_numbers',
        'fax_numbers',
        'email_addresses',
        'ssn',
        'medical_record_numbers',
        'health_plan_numbers',
        'account_numbers',
        'certificate_numbers',
        'vehicle_identifiers',
        'device_identifiers',
        'urls',
        'ip_addresses',
        'biometric_identifiers',
        'full_face_photos',
        'other_unique_identifiers'
    ]
    
    def __init__(self):
        """Initialize PHI detector with regex patterns"""
        self.patterns = self._create_regex_patterns()
        self.quarantine_path = None
        
    def _create_regex_patterns(self) -> Dict[str, re.Pattern]:
        """Create regex patterns for 18 HIPAA identifiers"""
        patterns = {
            # Social Security Numbers
            'ssn': re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
            
            # Phone numbers (US format)
            'phone_numbers': re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            
            # Fax numbers (similar to phone)
            'fax_numbers': re.compile(r'\b(?:fax|FAX)[\s:]*(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            
            # Email addresses
            'email_addresses': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # URLs
            'urls': re.compile(r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'),
            
            # IP addresses (IPv4)
            'ip_addresses': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            
            # Medical Record Numbers (MRN format)
            'medical_record_numbers': re.compile(r'\b(?:MRN|mrn|medical[_\s]?record)[:\s#]*[A-Z0-9]{6,12}\b', re.IGNORECASE),
            
            # Account numbers (generic pattern)
            'account_numbers': re.compile(r'\b(?:account|acct)[:\s#]*[A-Z0-9]{6,20}\b', re.IGNORECASE),
            
            # Certificate/License numbers
            'certificate_numbers': re.compile(r'\b(?:cert|certificate|license)[:\s#]*[A-Z0-9]{6,20}\b', re.IGNORECASE),
            
            # Vehicle identifiers (VIN)
            'vehicle_identifiers': re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b'),
            
            # Device identifiers (serial numbers)
            'device_identifiers': re.compile(r'\b(?:serial|device|SN)[:\s#]*[A-Z0-9]{8,20}\b', re.IGNORECASE),
            
            # Dates (various formats) - except year-only
            'dates': re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b', re.IGNORECASE),
            
            # Names (common patterns - basic detection)
            'names': re.compile(r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
            
            # Geographic subdivisions smaller than state (ZIP codes)
            'geographic_subdivisions': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
        }
        
        return patterns
    
    def detect_phi(self, data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Detect potential PHI in dataset
        
        Args:
            data: DataFrame to scan for PHI
            
        Returns:
            Dictionary mapping PHI types to list of columns containing them
        """
        logger.info(f"Scanning dataset with {len(data.columns)} columns for PHI")
        
        phi_detected = {}
        
        for column in data.columns:
            # Check column name for PHI indicators
            column_phi = self._check_column_name(column)
            if column_phi:
                for phi_type in column_phi:
                    if phi_type not in phi_detected:
                        phi_detected[phi_type] = []
                    phi_detected[phi_type].append(column)
            
            # Check column values for PHI patterns
            if data[column].dtype == 'object':
                value_phi = self._check_column_values(data[column])
                for phi_type in value_phi:
                    if phi_type not in phi_detected:
                        phi_detected[phi_type] = []
                    if column not in phi_detected[phi_type]:
                        phi_detected[phi_type].append(column)
        
        if phi_detected:
            logger.warning(f"PHI detected in {len(phi_detected)} categories")
        else:
            logger.info("No PHI detected in dataset")
        
        return phi_detected
    
    def _check_column_name(self, column_name: str) -> Set[str]:
        """Check if column name suggests PHI"""
        phi_keywords = {
            'names': ['name', 'patient_name', 'first_name', 'last_name', 'full_name'],
            'email_addresses': ['email', 'e_mail', 'email_address'],
            'phone_numbers': ['phone', 'telephone', 'mobile', 'cell'],
            'ssn': ['ssn', 'social_security', 'social_security_number'],
            'medical_record_numbers': ['mrn', 'medical_record', 'patient_id'],
            'dates': ['dob', 'date_of_birth', 'birth_date', 'admission_date', 'discharge_date'],
            'geographic_subdivisions': ['zip', 'zipcode', 'postal_code', 'address', 'street'],
            'ip_addresses': ['ip', 'ip_address', 'ip_addr'],
        }
        
        detected = set()
        column_lower = column_name.lower()
        
        for phi_type, keywords in phi_keywords.items():
            if any(keyword in column_lower for keyword in keywords):
                detected.add(phi_type)
        
        return detected
    
    def _check_column_values(self, series: pd.Series) -> Set[str]:
        """Check column values for PHI patterns using regex"""
        detected = set()
        
        # Sample up to 1000 non-null values for performance
        sample = series.dropna().head(1000)
        
        if len(sample) == 0:
            return detected
        
        # Convert to string and concatenate for pattern matching
        sample_text = ' '.join(sample.astype(str))
        
        for phi_type, pattern in self.patterns.items():
            if pattern.search(sample_text):
                detected.add(phi_type)
        
        return detected
    
    def quarantine_data(self, data: pd.DataFrame, phi_columns: List[str], 
                       quarantine_path: str) -> pd.DataFrame:
        """
        Quarantine data containing PHI
        
        Args:
            data: Original DataFrame
            phi_columns: List of columns containing PHI
            quarantine_path: Path to save quarantined data
            
        Returns:
            DataFrame with PHI columns removed
        """
        logger.warning(f"Quarantining {len(phi_columns)} columns with PHI")
        
        # Save quarantined data
        quarantined = data[phi_columns].copy()
        quarantined['quarantine_timestamp'] = datetime.now()
        quarantined['quarantine_reason'] = 'PHI_DETECTED'
        
        quarantined.to_csv(quarantine_path, index=False)
        logger.info(f"Quarantined data saved to {quarantine_path}")
        
        # Remove PHI columns from original data
        clean_data = data.drop(columns=phi_columns)
        
        return clean_data
    
    def validate_no_phi(self, data: pd.DataFrame) -> bool:
        """
        Validate that dataset contains no PHI
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if no PHI detected, False otherwise
        """
        phi_detected = self.detect_phi(data)
        
        if phi_detected:
            logger.error(f"PHI validation failed: {list(phi_detected.keys())}")
            return False
        
        logger.info("PHI validation passed: No PHI detected")
        return True
    
    def get_phi_report(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive PHI detection report
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary with PHI detection results and statistics
        """
        phi_detected = self.detect_phi(data)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_columns': len(data.columns),
            'total_rows': len(data),
            'phi_detected': bool(phi_detected),
            'phi_categories': list(phi_detected.keys()),
            'phi_columns': phi_detected,
            'affected_columns_count': len(set(col for cols in phi_detected.values() for col in cols)),
            'validation_passed': not bool(phi_detected)
        }
        
        return report
