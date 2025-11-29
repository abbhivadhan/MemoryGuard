"""
Demographic Feature Processing

Processes demographic and lifestyle features including:
- Age
- Sex
- Education years
- Race/ethnicity
- BMI
- Lifestyle factors (smoking, alcohol, physical activity)
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DemographicFeatureProcessor:
    """Process demographic and lifestyle features"""
    
    def __init__(self):
        """Initialize demographic feature processor"""
        self.feature_columns = []
        
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all demographic features from raw data
        
        Args:
            data: Raw dataframe containing demographic information
            
        Returns:
            DataFrame with processed demographic features
        """
        logger.info("Extracting demographic features")
        
        features = pd.DataFrame(index=data.index)
        
        # Extract basic demographics
        features['age'] = self.extract_age(data)
        features['sex'] = self.extract_sex(data)
        features['education_years'] = self.extract_education(data)
        
        # Extract race/ethnicity
        race_features = self.extract_race_ethnicity(data)
        features = pd.concat([features, race_features], axis=1)
        
        # Extract lifestyle factors
        lifestyle_features = self.extract_lifestyle_factors(data)
        features = pd.concat([features, lifestyle_features], axis=1)
        
        # Create derived features
        derived_features = self.create_derived_features(features)
        features = pd.concat([features, derived_features], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} demographic features")
        return features
    
    def extract_age(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract age in years
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with age values
        """
        age_columns = ['age', 'Age', 'AGE', 'age_years']
        
        for col in age_columns:
            if col in data.columns:
                age = data[col].copy()
                # Validate age range (reasonable for AD studies: 50-100)
                age = age.clip(50, 100)
                return age
        
        logger.warning("Age column not found")
        return pd.Series(np.nan, index=data.index)
    
    def extract_sex(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract sex as binary feature
        
        Encoded as: 0 = Female, 1 = Male
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with binary sex values
        """
        sex_columns = ['sex', 'Sex', 'SEX', 'gender', 'Gender', 'PTGENDER']
        
        for col in sex_columns:
            if col in data.columns:
                sex = data[col].copy()
                
                # Handle different encodings
                if sex.dtype == 'object':
                    sex = sex.str.lower()
                    sex_map = {
                        'female': 0.0,
                        'f': 0.0,
                        'male': 1.0,
                        'm': 1.0,
                        '0': 0.0,
                        '1': 1.0
                    }
                    return sex.map(sex_map)
                else:
                    # Assume numeric (0/1)
                    return sex.astype(float)
        
        logger.warning("Sex column not found")
        return pd.Series(np.nan, index=data.index)
    
    def extract_education(self, data: pd.DataFrame) -> pd.Series:
        """
        Extract education years
        
        Args:
            data: Raw dataframe
            
        Returns:
            Series with education years
        """
        edu_columns = [
            'education', 'Education', 'EDUCATION',
            'education_years', 'PTEDUCAT', 'years_education'
        ]
        
        for col in edu_columns:
            if col in data.columns:
                education = data[col].copy()
                # Validate education range (0-25 years)
                education = education.clip(0, 25)
                return education
        
        logger.warning("Education column not found")
        return pd.Series(np.nan, index=data.index)
    
    def extract_race_ethnicity(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and one-hot encode race/ethnicity
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with one-hot encoded race/ethnicity
        """
        race_columns = ['race', 'Race', 'RACE', 'ethnicity', 'Ethnicity', 'PTRACCAT']
        
        race_data = None
        for col in race_columns:
            if col in data.columns:
                race_data = data[col].copy()
                break
        
        if race_data is None:
            logger.warning("Race/ethnicity column not found")
            return pd.DataFrame(index=data.index)
        
        # Standardize race categories
        if race_data.dtype == 'object':
            race_data = race_data.str.lower().str.strip()
            
            # Map to standard categories
            race_map = {
                'white': 'white',
                'caucasian': 'white',
                'black': 'black',
                'african american': 'black',
                'asian': 'asian',
                'hispanic': 'hispanic',
                'latino': 'hispanic',
                'other': 'other',
                'unknown': 'unknown'
            }
            
            race_data = race_data.map(race_map)
        
        # One-hot encode
        race_encoded = pd.get_dummies(
            race_data,
            prefix='race',
            dummy_na=False
        )
        
        return race_encoded
    
    def extract_lifestyle_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract lifestyle and health factors
        
        Args:
            data: Raw dataframe
            
        Returns:
            DataFrame with lifestyle features
        """
        lifestyle = pd.DataFrame(index=data.index)
        
        # BMI (Body Mass Index)
        bmi_columns = ['bmi', 'BMI', 'body_mass_index']
        for col in bmi_columns:
            if col in data.columns:
                lifestyle['bmi'] = data[col].clip(15, 50)  # Reasonable range
                break
        
        # Smoking status
        smoking_columns = ['smoking', 'Smoking', 'SMOKING', 'smoker']
        for col in smoking_columns:
            if col in data.columns:
                smoking = data[col].copy()
                
                if smoking.dtype == 'object':
                    smoking = smoking.str.lower()
                    smoking_map = {
                        'never': 0.0,
                        'former': 1.0,
                        'current': 2.0,
                        'no': 0.0,
                        'yes': 2.0
                    }
                    lifestyle['smoking_status'] = smoking.map(smoking_map)
                else:
                    lifestyle['smoking_status'] = smoking.astype(float)
                break
        
        # Alcohol consumption
        alcohol_columns = ['alcohol', 'Alcohol', 'ALCOHOL', 'alcohol_use']
        for col in alcohol_columns:
            if col in data.columns:
                alcohol = data[col].copy()
                
                if alcohol.dtype == 'object':
                    alcohol = alcohol.str.lower()
                    alcohol_map = {
                        'never': 0.0,
                        'occasional': 1.0,
                        'moderate': 2.0,
                        'heavy': 3.0,
                        'no': 0.0,
                        'yes': 2.0
                    }
                    lifestyle['alcohol_consumption'] = alcohol.map(alcohol_map)
                else:
                    lifestyle['alcohol_consumption'] = alcohol.astype(float)
                break
        
        # Physical activity level
        activity_columns = ['physical_activity', 'exercise', 'EXERCISE', 'activity_level']
        for col in activity_columns:
            if col in data.columns:
                activity = data[col].copy()
                
                if activity.dtype == 'object':
                    activity = activity.str.lower()
                    activity_map = {
                        'sedentary': 0.0,
                        'low': 1.0,
                        'moderate': 2.0,
                        'high': 3.0,
                        'none': 0.0
                    }
                    lifestyle['physical_activity'] = activity.map(activity_map)
                else:
                    lifestyle['physical_activity'] = activity.astype(float)
                break
        
        # Social engagement
        social_columns = ['social_engagement', 'social_activity', 'SOCIAL']
        for col in social_columns:
            if col in data.columns:
                lifestyle['social_engagement'] = data[col].astype(float)
                break
        
        # Marital status
        marital_columns = ['marital_status', 'married', 'MARITAL']
        for col in marital_columns:
            if col in data.columns:
                marital = data[col].copy()
                
                if marital.dtype == 'object':
                    marital = marital.str.lower()
                    # Binary: married/partnered vs single/widowed/divorced
                    lifestyle['married'] = marital.isin(['married', 'partnered']).astype(float)
                else:
                    lifestyle['married'] = marital.astype(float)
                break
        
        return lifestyle
    
    def create_derived_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived demographic features
        
        Args:
            features: DataFrame with base demographic features
            
        Returns:
            DataFrame with derived features
        """
        derived = pd.DataFrame(index=features.index)
        
        # Age groups
        if 'age' in features.columns:
            derived['age_group_60_70'] = ((features['age'] >= 60) & (features['age'] < 70)).astype(float)
            derived['age_group_70_80'] = ((features['age'] >= 70) & (features['age'] < 80)).astype(float)
            derived['age_group_80_plus'] = (features['age'] >= 80).astype(float)
            
            # Age squared (for non-linear effects)
            derived['age_squared'] = features['age'] ** 2
        
        # Education level categories
        if 'education_years' in features.columns:
            derived['education_low'] = (features['education_years'] < 12).astype(float)
            derived['education_medium'] = (
                (features['education_years'] >= 12) & 
                (features['education_years'] < 16)
            ).astype(float)
            derived['education_high'] = (features['education_years'] >= 16).astype(float)
        
        # BMI categories
        if 'bmi' in features.columns:
            derived['bmi_underweight'] = (features['bmi'] < 18.5).astype(float)
            derived['bmi_normal'] = (
                (features['bmi'] >= 18.5) & 
                (features['bmi'] < 25)
            ).astype(float)
            derived['bmi_overweight'] = (
                (features['bmi'] >= 25) & 
                (features['bmi'] < 30)
            ).astype(float)
            derived['bmi_obese'] = (features['bmi'] >= 30).astype(float)
        
        # Lifestyle risk score (higher = more risk factors)
        risk_factors = []
        
        if 'smoking_status' in features.columns:
            risk_factors.append((features['smoking_status'] >= 1).astype(float))
        
        if 'alcohol_consumption' in features.columns:
            risk_factors.append((features['alcohol_consumption'] >= 3).astype(float))
        
        if 'physical_activity' in features.columns:
            risk_factors.append((features['physical_activity'] <= 1).astype(float))
        
        if 'bmi' in features.columns:
            risk_factors.append((features['bmi'] >= 30).astype(float))
        
        if risk_factors:
            derived['lifestyle_risk_score'] = sum(risk_factors)
        
        return derived
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted demographic features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check age range
        if 'age' in features.columns:
            validation['age_valid'] = features['age'].between(50, 100, inclusive='both').all()
        
        # Check sex is binary
        if 'sex' in features.columns:
            validation['sex_binary'] = features['sex'].isin([0, 1, np.nan]).all()
        
        # Check education range
        if 'education_years' in features.columns:
            validation['education_valid'] = features['education_years'].between(0, 25, inclusive='both').all()
        
        # Check BMI range
        if 'bmi' in features.columns:
            validation['bmi_valid'] = features['bmi'].between(15, 50, inclusive='both').all()
        
        return validation
