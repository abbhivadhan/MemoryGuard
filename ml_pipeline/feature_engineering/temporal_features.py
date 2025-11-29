"""
Temporal Feature Engineering

Creates temporal features from longitudinal data including:
- Time since baseline
- Rate of cognitive decline
- Biomarker change rates
- Visit frequency
- Trajectory features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TemporalFeatureEngineer:
    """Engineer temporal features from longitudinal data"""
    
    def __init__(self):
        """Initialize temporal feature engineer"""
        self.feature_columns = []
        
    def extract_features(
        self,
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        visit_date_col: str = 'visit_date'
    ) -> pd.DataFrame:
        """
        Extract all temporal features from longitudinal data
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Name of patient ID column
            visit_date_col: Name of visit date column
            
        Returns:
            DataFrame with temporal features
        """
        logger.info("Extracting temporal features")
        
        # Ensure date column is datetime
        if visit_date_col in data.columns:
            data[visit_date_col] = pd.to_datetime(data[visit_date_col])
        
        features = pd.DataFrame(index=data.index)
        
        # Calculate time since baseline
        features['time_since_baseline'] = self.calculate_time_since_baseline(
            data, patient_id_col, visit_date_col
        )
        
        # Calculate visit number
        features['visit_number'] = self.calculate_visit_number(
            data, patient_id_col, visit_date_col
        )
        
        # Calculate cognitive decline rates
        cognitive_rates = self.calculate_cognitive_decline_rates(
            data, patient_id_col, visit_date_col
        )
        features = pd.concat([features, cognitive_rates], axis=1)
        
        # Calculate biomarker change rates
        biomarker_rates = self.calculate_biomarker_change_rates(
            data, patient_id_col, visit_date_col
        )
        features = pd.concat([features, biomarker_rates], axis=1)
        
        # Calculate visit frequency
        features['visit_frequency'] = self.calculate_visit_frequency(
            data, patient_id_col, visit_date_col
        )
        
        # Calculate trajectory features
        trajectory_features = self.calculate_trajectory_features(
            data, patient_id_col, visit_date_col
        )
        features = pd.concat([features, trajectory_features], axis=1)
        
        self.feature_columns = features.columns.tolist()
        
        logger.info(f"Extracted {len(self.feature_columns)} temporal features")
        return features
    
    def calculate_time_since_baseline(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.Series:
        """
        Calculate time since baseline visit in months
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            Series with months since baseline
        """
        if visit_date_col not in data.columns:
            logger.warning(f"Visit date column '{visit_date_col}' not found")
            return pd.Series(np.nan, index=data.index)
        
        # Get baseline date for each patient
        baseline_dates = data.groupby(patient_id_col)[visit_date_col].min()
        
        # Calculate time difference
        time_since_baseline = data.apply(
            lambda row: (
                row[visit_date_col] - baseline_dates[row[patient_id_col]]
            ).days / 30.44  # Average days per month
            if pd.notna(row[visit_date_col]) else np.nan,
            axis=1
        )
        
        return time_since_baseline
    
    def calculate_visit_number(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.Series:
        """
        Calculate visit number for each patient (1, 2, 3, ...)
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            Series with visit numbers
        """
        if visit_date_col not in data.columns:
            logger.warning(f"Visit date column '{visit_date_col}' not found")
            return pd.Series(1, index=data.index)
        
        # Sort by patient and date
        sorted_data = data.sort_values([patient_id_col, visit_date_col])
        
        # Assign visit numbers
        visit_numbers = sorted_data.groupby(patient_id_col).cumcount() + 1
        
        # Reindex to match original order
        visit_numbers = visit_numbers.reindex(data.index)
        
        return visit_numbers
    
    def calculate_cognitive_decline_rates(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.DataFrame:
        """
        Calculate rate of cognitive decline for various assessments
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            DataFrame with cognitive decline rates
        """
        rates = pd.DataFrame(index=data.index)
        
        # Cognitive measures to track
        cognitive_measures = {
            'mmse_total': 'mmse_decline_rate',
            'moca_total': 'moca_decline_rate',
            'cdr_global': 'cdr_change_rate',
            'adas_cog_total': 'adas_cog_change_rate'
        }
        
        for measure, rate_name in cognitive_measures.items():
            if measure in data.columns and visit_date_col in data.columns:
                rates[rate_name] = self._calculate_change_rate(
                    data, patient_id_col, visit_date_col, measure
                )
        
        return rates
    
    def calculate_biomarker_change_rates(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.DataFrame:
        """
        Calculate rate of biomarker changes
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            DataFrame with biomarker change rates
        """
        rates = pd.DataFrame(index=data.index)
        
        # Biomarkers to track
        biomarkers = {
            'csf_ab42': 'ab42_change_rate',
            'csf_tau': 'tau_change_rate',
            'csf_ptau': 'ptau_change_rate',
            'hippocampus_total': 'hippocampus_atrophy_rate'
        }
        
        for biomarker, rate_name in biomarkers.items():
            if biomarker in data.columns and visit_date_col in data.columns:
                rates[rate_name] = self._calculate_change_rate(
                    data, patient_id_col, visit_date_col, biomarker
                )
        
        return rates
    
    def _calculate_change_rate(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str,
        measure_col: str
    ) -> pd.Series:
        """
        Calculate rate of change for a measure (change per month)
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            measure_col: Measure column name
            
        Returns:
            Series with change rates
        """
        change_rates = []
        
        for idx, row in data.iterrows():
            patient_id = row[patient_id_col]
            current_date = row[visit_date_col]
            current_value = row[measure_col]
            
            # Get patient's previous visits
            patient_data = data[
                (data[patient_id_col] == patient_id) &
                (data[visit_date_col] < current_date)
            ].sort_values(visit_date_col)
            
            if len(patient_data) == 0 or pd.isna(current_value):
                # No previous data or missing current value
                change_rates.append(0.0)
            else:
                # Get most recent previous visit
                prev_row = patient_data.iloc[-1]
                prev_value = prev_row[measure_col]
                prev_date = prev_row[visit_date_col]
                
                if pd.isna(prev_value):
                    change_rates.append(0.0)
                else:
                    # Calculate change per month
                    time_diff_months = (current_date - prev_date).days / 30.44
                    
                    if time_diff_months > 0:
                        rate = (current_value - prev_value) / time_diff_months
                        change_rates.append(rate)
                    else:
                        change_rates.append(0.0)
        
        return pd.Series(change_rates, index=data.index)
    
    def calculate_visit_frequency(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.Series:
        """
        Calculate average time between visits (in months)
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            Series with visit frequency
        """
        if visit_date_col not in data.columns:
            return pd.Series(np.nan, index=data.index)
        
        frequencies = []
        
        for idx, row in data.iterrows():
            patient_id = row[patient_id_col]
            
            # Get all visits for this patient
            patient_visits = data[
                data[patient_id_col] == patient_id
            ][visit_date_col].sort_values()
            
            if len(patient_visits) <= 1:
                frequencies.append(np.nan)
            else:
                # Calculate average time between visits
                time_diffs = patient_visits.diff().dropna()
                avg_diff_months = time_diffs.mean().days / 30.44
                frequencies.append(avg_diff_months)
        
        return pd.Series(frequencies, index=data.index)
    
    def calculate_trajectory_features(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str
    ) -> pd.DataFrame:
        """
        Calculate trajectory features (stable, declining, improving)
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            
        Returns:
            DataFrame with trajectory features
        """
        trajectories = pd.DataFrame(index=data.index)
        
        # MMSE trajectory
        if 'mmse_total' in data.columns:
            trajectories['mmse_trajectory'] = self._classify_trajectory(
                data, patient_id_col, visit_date_col, 'mmse_total', declining_threshold=-2
            )
        
        # Hippocampal volume trajectory
        if 'hippocampus_total' in data.columns:
            trajectories['hippocampus_trajectory'] = self._classify_trajectory(
                data, patient_id_col, visit_date_col, 'hippocampus_total', declining_threshold=-100
            )
        
        return trajectories
    
    def _classify_trajectory(
        self,
        data: pd.DataFrame,
        patient_id_col: str,
        visit_date_col: str,
        measure_col: str,
        declining_threshold: float
    ) -> pd.Series:
        """
        Classify trajectory as stable (0), declining (1), or improving (2)
        
        Args:
            data: DataFrame with longitudinal data
            patient_id_col: Patient ID column name
            visit_date_col: Visit date column name
            measure_col: Measure column name
            declining_threshold: Threshold for classifying as declining
            
        Returns:
            Series with trajectory classifications
        """
        trajectories = []
        
        for idx, row in data.iterrows():
            patient_id = row[patient_id_col]
            current_date = row[visit_date_col]
            
            # Get patient's data up to current visit
            patient_data = data[
                (data[patient_id_col] == patient_id) &
                (data[visit_date_col] <= current_date)
            ].sort_values(visit_date_col)
            
            if len(patient_data) < 2:
                # Not enough data to determine trajectory
                trajectories.append(0)  # Assume stable
            else:
                # Calculate overall change
                first_value = patient_data[measure_col].iloc[0]
                last_value = patient_data[measure_col].iloc[-1]
                
                if pd.isna(first_value) or pd.isna(last_value):
                    trajectories.append(0)
                else:
                    change = last_value - first_value
                    
                    if change <= declining_threshold:
                        trajectories.append(1)  # Declining
                    elif change >= abs(declining_threshold):
                        trajectories.append(2)  # Improving
                    else:
                        trajectories.append(0)  # Stable
        
        return pd.Series(trajectories, index=data.index)
    
    def get_feature_names(self) -> List[str]:
        """Get list of extracted feature names"""
        return self.feature_columns
    
    def validate_features(self, features: pd.DataFrame) -> Dict[str, bool]:
        """
        Validate extracted temporal features
        
        Args:
            features: DataFrame with extracted features
            
        Returns:
            Dictionary with validation results
        """
        validation = {}
        
        # Check time since baseline is non-negative
        if 'time_since_baseline' in features.columns:
            validation['time_since_baseline_nonnegative'] = (
                features['time_since_baseline'] >= 0
            ).all()
        
        # Check visit number is positive integer
        if 'visit_number' in features.columns:
            validation['visit_number_positive'] = (
                features['visit_number'] >= 1
            ).all()
        
        # Check trajectory values are 0, 1, or 2
        trajectory_cols = [col for col in features.columns if 'trajectory' in col]
        for col in trajectory_cols:
            validation[f'{col}_valid'] = features[col].isin([0, 1, 2, np.nan]).all()
        
        return validation
