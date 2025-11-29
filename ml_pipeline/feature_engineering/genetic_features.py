"""
Genetic Feature Encoding

Encodes genetic risk factors for Alzheimer's disease including:
- APOE genotype (e2, e3, e4 alleles)
- APOE e4 allele count
- Risk stratification based on APOE status
- Family history of dementia
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class GeneticFeatureEncoder:
    """Encode genetic risk factors as ML features"""
    
    def __init__(self):
        """Initialize genetic feature encoder"""
        self.feature_columns = []
        
        # APOE genotype combinations
        self.apoe_genotypes = [
            'e2/e2', 'e2/e3', 'e2/e4',
            'e3/e3', 'e3/e4', 'e4/e4'
        ]
        
        # Risk levels based on APOE genotype
        self.risk_levels = {
            'e2/e2': 'low',
            'e2/e3': 'low',
            'e2/e4': 'moderate',
            'e3/e3': 'baseline',
            'e3/e4': 'moderate',
            'e4/e4': 'high'
        }
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all genetic features from raw data
        
        Args:
            data: Raw dataframe containing genetic information
            
        Returns:
            DataFrame with encoded genetic features
        """
        logger.info("Extracting genetic features")
        
        features = pd.DataFrame(index=data.index)
        
        # Parse APOE genotype
        apoe_genotype = self.parse_apoe_genotype(data)
        
        # One-hot encode genotype
        genotype_features = self.encode_apoe_genotype(apoe_genotype)
        features = pd.concat([features, genotype_features], axis=1)
        
        # Calculate e4 allele count
        features['apoe_e4_count'] = self.calculate_e4_count(apoe_genotype)
        
        # Create risk stratification
        risk_features = self.create_risk_stratification(apoe_genotype)
        features = pd.concat([features, risk_features], axis=1)
        
        # Extract family history
        family_history = self.extract_family_history(data)
        features = pd.concat([features, family_history], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} genetic features")
        return features
    
    def parse_apoe_genotype(self, data: pd.DataFrame) -> pd.Series:
        """
        Parse APOE genotype from various formats
        
        APOE has three common alleles: e2, e3, e4
        Each person has two alleles (one from each parent)
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with standardized APOE genotype strings
        """
        # Try different column name variations
        apoe_columns = ['APOE', 'apoe', 'APOE_genotype', 'apoe_genotype', 'APOE4']
        
        genotype = None
        for col in apoe_columns:
            if col in data.columns:
                genotype = data[col].copy()
                break
        
        if genotype is None:
            logger.warning("APOE genotype column not found")
            return pd.Series(np.nan, index=data.index)
        
        # Standardize format to "e#/e#"
        genotype = genotype.astype(str).str.lower()
        
        # Handle different formats
        def standardize_genotype(g):
            if pd.isna(g) or g == 'nan':
                return np.nan
            
            # Remove spaces and convert to lowercase
            g = g.replace(' ', '').lower()
            
            # Format: "e3/e4" or "e3e4"
            if '/' in g:
                parts = g.split('/')
                if len(parts) == 2:
                    allele1 = parts[0] if parts[0].startswith('e') else f'e{parts[0]}'
                    allele2 = parts[1] if parts[1].startswith('e') else f'e{parts[1]}'
                    # Sort alleles (e2 < e3 < e4)
                    alleles = sorted([allele1, allele2])
                    return f'{alleles[0]}/{alleles[1]}'
            
            # Format: "33", "34", "44" (numeric only)
            if g.isdigit() and len(g) == 2:
                allele1 = f'e{g[0]}'
                allele2 = f'e{g[1]}'
                alleles = sorted([allele1, allele2])
                return f'{alleles[0]}/{alleles[1]}'
            
            # Format: "e3e4"
            if g.startswith('e') and len(g) == 4:
                allele1 = g[:2]
                allele2 = g[2:]
                alleles = sorted([allele1, allele2])
                return f'{alleles[0]}/{alleles[1]}'
            
            return np.nan
        
        genotype = genotype.apply(standardize_genotype)
        
        return genotype
    
    def encode_apoe_genotype(self, genotype: pd.Series) -> pd.DataFrame:
        """
        One-hot encode APOE genotype
        
        Args:
            genotype: Series with APOE genotype strings
            
        Returns:
            DataFrame with one-hot encoded genotypes
        """
        encoded = pd.DataFrame(index=genotype.index)
        
        # Create binary indicator for each genotype
        for gt in self.apoe_genotypes:
            encoded[f'apoe_{gt.replace("/", "_")}'] = (genotype == gt).astype(float)
        
        # Handle missing values
        has_genotype = genotype.notna()
        for col in encoded.columns:
            encoded.loc[~has_genotype, col] = np.nan
        
        return encoded
    
    def calculate_e4_count(self, genotype: pd.Series) -> pd.Series:
        """
        Calculate number of APOE e4 alleles (0, 1, or 2)
        
        The e4 allele is the primary genetic risk factor for late-onset AD:
        - 0 e4 alleles: baseline risk
        - 1 e4 allele: 3-4x increased risk
        - 2 e4 alleles: 8-12x increased risk
        
        Args:
            genotype: Series with APOE genotype strings
            
        Returns:
            Series with e4 allele count
        """
        def count_e4(g):
            if pd.isna(g):
                return np.nan
            return g.count('e4')
        
        e4_count = genotype.apply(count_e4)
        
        return e4_count
    
    def create_risk_stratification(self, genotype: pd.Series) -> pd.DataFrame:
        """
        Create risk stratification categories based on APOE genotype
        
        Args:
            genotype: Series with APOE genotype strings
            
        Returns:
            DataFrame with risk stratification features
        """
        risk = pd.DataFrame(index=genotype.index)
        
        # Map genotype to risk level
        risk['apoe_risk_level'] = genotype.map(self.risk_levels)
        
        # One-hot encode risk levels
        risk_dummies = pd.get_dummies(
            risk['apoe_risk_level'],
            prefix='apoe_risk',
            dummy_na=False
        )
        risk = pd.concat([risk, risk_dummies], axis=1)
        
        # Binary indicators
        risk['apoe_e4_carrier'] = (genotype.str.contains('e4', na=False)).astype(float)
        risk['apoe_e4_homozygous'] = (genotype == 'e4/e4').astype(float)
        risk['apoe_e2_carrier'] = (genotype.str.contains('e2', na=False)).astype(float)
        
        # Handle missing values
        has_genotype = genotype.notna()
        for col in risk.columns:
            if col != 'apoe_risk_level':
                risk.loc[~has_genotype, col] = np.nan
        
        return risk
    
    def extract_family_history(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract family history of dementia
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with family history features
        """
        family = pd.DataFrame(index=data.index)
        
        # Family history of dementia (binary)
        fh_columns = [
            'family_history_dementia',
            'family_history',
            'FAMHIST',
            'fh_dementia'
        ]
        
        for col in fh_columns:
            if col in data.columns:
                # Convert to binary (1 = positive family history, 0 = negative)
                values = data[col].copy()
                
                # Handle different encodings
                if values.dtype == 'object':
                    values = values.str.lower()
                    family['family_history_dementia'] = values.map({
                        'yes': 1.0,
                        'no': 0.0,
                        'y': 1.0,
                        'n': 0.0,
                        'true': 1.0,
                        'false': 0.0,
                        '1': 1.0,
                        '0': 0.0
                    })
                else:
                    # Assume numeric (0/1)
                    family['family_history_dementia'] = values.astype(float)
                
                break
        
        # If not found, set to NaN
        if 'family_history_dementia' not in family.columns:
            family['family_history_dementia'] = np.nan
        
        # Number of affected relatives (if available)
        if 'num_affected_relatives' in data.columns:
            family['num_affected_relatives'] = data['num_affected_relatives']
        
        # Age of onset in family (if available)
        if 'family_onset_age' in data.columns:
            family['family_onset_age'] = data['family_onset_age']
        
        return family
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted genetic features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check e4 count is 0, 1, or 2
        if 'apoe_e4_count' in features.columns:
            validation['e4_count_valid'] = features['apoe_e4_count'].isin([0, 1, 2, np.nan]).all()
        
        # Check binary features are 0 or 1
        binary_features = [
            'apoe_e4_carrier',
            'apoe_e4_homozygous',
            'apoe_e2_carrier',
            'family_history_dementia'
        ]
        
        for feature in binary_features:
            if feature in features.columns:
                validation[f'{feature}_binary'] = features[feature].isin([0, 1, np.nan]).all()
        
        # Check one-hot encoded features sum to 1 (when not missing)
        genotype_cols = [col for col in features.columns if col.startswith('apoe_e') and '_e' in col]
        if genotype_cols:
            genotype_sum = features[genotype_cols].sum(axis=1)
            # Should be 1 when not missing, 0 when all are NaN
            validation['genotype_onehot_valid'] = (
                (genotype_sum == 1) | (genotype_sum == 0)
            ).all()
        
        return validation
