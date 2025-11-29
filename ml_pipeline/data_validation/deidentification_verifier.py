"""De-identification Verification Module - Verifies proper de-identification and k-anonymity"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class DeidentificationVerifier:
    """Verify de-identification and k-anonymity of datasets"""
    
    # Direct identifiers that must be removed
    DIRECT_IDENTIFIERS = [
        'name', 'patient_name', 'first_name', 'last_name', 'full_name',
        'ssn', 'social_security_number',
        'email', 'email_address',
        'phone', 'phone_number', 'telephone',
        'address', 'street_address',
        'medical_record_number', 'mrn',
        'account_number',
        'certificate_number',
        'license_number',
        'vehicle_identifier', 'vin',
        'device_identifier', 'serial_number',
        'url', 'web_address',
        'ip_address', 'ip',
        'biometric_identifier',
        'photo', 'image', 'photograph'
    ]
    
    # Quasi-identifiers used for k-anonymity checking
    QUASI_IDENTIFIERS = [
        'age', 'birth_year', 'year_of_birth',
        'sex', 'gender',
        'race', 'ethnicity',
        'zip_code', 'postal_code', 'zip3',
        'state', 'city',
        'education', 'education_level',
        'occupation',
        'marital_status'
    ]
    
    def __init__(self, k_threshold: int = 5):
        """
        Initialize de-identification verifier
        
        Args:
            k_threshold: Minimum k value for k-anonymity (default: 5)
        """
        self.k_threshold = k_threshold
        logger.info(f"Initialized DeidentificationVerifier with k={k_threshold}")
    
    def verify_no_direct_identifiers(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Verify that no direct identifiers are present in the dataset
        
        Args:
            data: DataFrame to verify
            
        Returns:
            Tuple of (verification_passed, list_of_found_identifiers)
        """
        logger.info("Verifying removal of direct identifiers")
        
        found_identifiers = []
        
        for column in data.columns:
            column_lower = column.lower().replace('_', ' ')
            
            for identifier in self.DIRECT_IDENTIFIERS:
                if identifier.replace('_', ' ') in column_lower:
                    found_identifiers.append(column)
                    break
        
        if found_identifiers:
            logger.error(f"Direct identifiers found: {found_identifiers}")
            return False, found_identifiers
        
        logger.info("No direct identifiers found")
        return True, []
    
    def verify_date_generalization(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Verify that dates are properly generalized (only years allowed, no specific dates)
        
        Args:
            data: DataFrame to verify
            
        Returns:
            Tuple of (verification_passed, list_of_problematic_columns)
        """
        logger.info("Verifying date generalization")
        
        problematic_columns = []
        
        # Check for date-like columns
        date_keywords = ['date', 'dob', 'birth', 'admission', 'discharge', 'visit']
        
        for column in data.columns:
            column_lower = column.lower()
            
            # Skip if column name suggests it's just a year
            if 'year' in column_lower:
                continue
            
            # Check if column name suggests a date
            if any(keyword in column_lower for keyword in date_keywords):
                # Check if values look like specific dates (not just years)
                sample = data[column].dropna().head(100)
                
                if len(sample) > 0:
                    # Check if values are datetime objects or date strings
                    if pd.api.types.is_datetime64_any_dtype(data[column]):
                        problematic_columns.append(column)
                    elif data[column].dtype == 'object':
                        # Check for date-like strings
                        sample_str = sample.astype(str).iloc[0]
                        if '-' in sample_str or '/' in sample_str:
                            # Might be a date string
                            if len(sample_str.split('-')) > 1 or len(sample_str.split('/')) > 1:
                                problematic_columns.append(column)
        
        if problematic_columns:
            logger.warning(f"Dates not properly generalized: {problematic_columns}")
            return False, problematic_columns
        
        logger.info("Date generalization verified")
        return True, []
    
    def check_k_anonymity(self, data: pd.DataFrame, 
                         quasi_identifiers: List[str] = None) -> Dict:
        """
        Check k-anonymity of the dataset
        
        Args:
            data: DataFrame to check
            quasi_identifiers: List of quasi-identifier columns (auto-detected if None)
            
        Returns:
            Dictionary with k-anonymity results
        """
        logger.info(f"Checking k-anonymity (k >= {self.k_threshold})")
        
        # Auto-detect quasi-identifiers if not provided
        if quasi_identifiers is None:
            quasi_identifiers = self._detect_quasi_identifiers(data)
        
        if not quasi_identifiers:
            logger.warning("No quasi-identifiers found in dataset")
            return {
                'k_anonymity_satisfied': True,
                'min_k': None,
                'quasi_identifiers': [],
                'warning': 'No quasi-identifiers detected'
            }
        
        logger.info(f"Using quasi-identifiers: {quasi_identifiers}")
        
        # Group by quasi-identifiers and count occurrences
        try:
            grouped = data.groupby(quasi_identifiers).size()
            min_k = grouped.min()
            max_k = grouped.max()
            mean_k = grouped.mean()
            
            # Count how many groups have k < threshold
            groups_below_threshold = (grouped < self.k_threshold).sum()
            total_groups = len(grouped)
            
            k_satisfied = min_k >= self.k_threshold
            
            result = {
                'k_anonymity_satisfied': k_satisfied,
                'min_k': int(min_k),
                'max_k': int(max_k),
                'mean_k': float(mean_k),
                'k_threshold': self.k_threshold,
                'quasi_identifiers': quasi_identifiers,
                'total_groups': total_groups,
                'groups_below_threshold': int(groups_below_threshold),
                'percentage_below_threshold': float(groups_below_threshold / total_groups * 100)
            }
            
            if k_satisfied:
                logger.info(f"k-anonymity satisfied: min_k={min_k} >= {self.k_threshold}")
            else:
                logger.error(f"k-anonymity NOT satisfied: min_k={min_k} < {self.k_threshold}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking k-anonymity: {str(e)}")
            return {
                'k_anonymity_satisfied': False,
                'error': str(e),
                'quasi_identifiers': quasi_identifiers
            }
    
    def _detect_quasi_identifiers(self, data: pd.DataFrame) -> List[str]:
        """Detect quasi-identifier columns in the dataset"""
        detected = []
        
        for column in data.columns:
            column_lower = column.lower().replace('_', ' ')
            
            for qi in self.QUASI_IDENTIFIERS:
                if qi.replace('_', ' ') in column_lower:
                    detected.append(column)
                    break
        
        return detected
    
    def verify_age_generalization(self, data: pd.DataFrame, 
                                  age_columns: List[str] = None) -> Tuple[bool, Dict]:
        """
        Verify that ages over 89 are generalized to 90+ (HIPAA requirement)
        
        Args:
            data: DataFrame to verify
            age_columns: List of age columns (auto-detected if None)
            
        Returns:
            Tuple of (verification_passed, details_dict)
        """
        logger.info("Verifying age generalization (ages > 89 should be 90+)")
        
        if age_columns is None:
            age_columns = [col for col in data.columns if 'age' in col.lower()]
        
        if not age_columns:
            return True, {'message': 'No age columns found'}
        
        violations = {}
        
        for col in age_columns:
            if col in data.columns:
                # Check for ages > 89
                if pd.api.types.is_numeric_dtype(data[col]):
                    ages_over_89 = data[col][data[col] > 89].dropna()
                    
                    if len(ages_over_89) > 0:
                        # Check if they're all exactly 90 (generalized)
                        unique_ages = ages_over_89.unique()
                        if not all(age == 90 for age in unique_ages):
                            violations[col] = {
                                'count': len(ages_over_89),
                                'unique_values': sorted(unique_ages.tolist())
                            }
        
        if violations:
            logger.warning(f"Age generalization violations found: {violations}")
            return False, violations
        
        logger.info("Age generalization verified")
        return True, {}
    
    def verify_zip_code_generalization(self, data: pd.DataFrame,
                                      zip_columns: List[str] = None) -> Tuple[bool, Dict]:
        """
        Verify that ZIP codes are generalized to 3 digits (HIPAA requirement)
        
        Args:
            data: DataFrame to verify
            zip_columns: List of ZIP code columns (auto-detected if None)
            
        Returns:
            Tuple of (verification_passed, details_dict)
        """
        logger.info("Verifying ZIP code generalization (should be 3 digits)")
        
        if zip_columns is None:
            zip_columns = [col for col in data.columns 
                          if 'zip' in col.lower() or 'postal' in col.lower()]
        
        if not zip_columns:
            return True, {'message': 'No ZIP code columns found'}
        
        violations = {}
        
        for col in zip_columns:
            if col in data.columns:
                # Check ZIP code length
                sample = data[col].dropna().astype(str).head(100)
                
                if len(sample) > 0:
                    # Check if any ZIP codes are longer than 3 digits
                    long_zips = sample[sample.str.len() > 3]
                    
                    if len(long_zips) > 0:
                        violations[col] = {
                            'count': len(long_zips),
                            'examples': long_zips.head(5).tolist()
                        }
        
        if violations:
            logger.warning(f"ZIP code generalization violations: {violations}")
            return False, violations
        
        logger.info("ZIP code generalization verified")
        return True, {}
    
    def comprehensive_verification(self, data: pd.DataFrame) -> Dict:
        """
        Perform comprehensive de-identification verification
        
        Args:
            data: DataFrame to verify
            
        Returns:
            Dictionary with all verification results
        """
        logger.info("Starting comprehensive de-identification verification")
        
        # Check direct identifiers
        no_direct_ids, found_ids = self.verify_no_direct_identifiers(data)
        
        # Check date generalization
        dates_ok, date_issues = self.verify_date_generalization(data)
        
        # Check k-anonymity
        k_anonymity_result = self.check_k_anonymity(data)
        
        # Check age generalization
        age_ok, age_issues = self.verify_age_generalization(data)
        
        # Check ZIP code generalization
        zip_ok, zip_issues = self.verify_zip_code_generalization(data)
        
        # Overall verification
        all_checks_passed = (
            no_direct_ids and 
            dates_ok and 
            k_anonymity_result.get('k_anonymity_satisfied', False) and
            age_ok and 
            zip_ok
        )
        
        result = {
            'verification_passed': all_checks_passed,
            'timestamp': pd.Timestamp.now().isoformat(),
            'checks': {
                'no_direct_identifiers': {
                    'passed': no_direct_ids,
                    'found_identifiers': found_ids
                },
                'date_generalization': {
                    'passed': dates_ok,
                    'issues': date_issues
                },
                'k_anonymity': k_anonymity_result,
                'age_generalization': {
                    'passed': age_ok,
                    'violations': age_issues
                },
                'zip_code_generalization': {
                    'passed': zip_ok,
                    'violations': zip_issues
                }
            }
        }
        
        if all_checks_passed:
            logger.info("✓ All de-identification checks passed")
        else:
            logger.error("✗ De-identification verification failed")
        
        return result
