"""
Disease progression forecasting for Alzheimer's patients.
Implements 6, 12, and 24-month forecasts using historical data.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)


class ProgressionForecaster:
    """
    Forecasts Alzheimer's disease progression over time.
    """
    
    def __init__(self):
        """Initialize progression forecaster."""
        self.cognitive_decline_rates = {
            'mmse_score': -2.5,  # points per year (average decline)
            'moca_score': -2.0,
            'cdr_score': 0.5
        }
        
        self.biomarker_progression_rates = {
            'csf_abeta42': -50,  # pg/mL per year
            'csf_tau': 30,
            'csf_ptau': 5
        }
        
        self.imaging_progression_rates = {
            'hippocampal_volume': -100,  # mm³ per year
            'entorhinal_thickness': -0.05,  # mm per year
            'cortical_thickness': -0.02
        }
    
    def forecast_progression(
        self,
        current_metrics: Dict[str, float],
        historical_data: Optional[List[Dict]] = None,
        forecast_months: List[int] = [6, 12, 24]
    ) -> Dict:
        """
        Forecast disease progression for specified time periods.
        
        Args:
            current_metrics: Current health metrics
            historical_data: Optional historical metrics for trend analysis
            forecast_months: List of months to forecast (e.g., [6, 12, 24])
            
        Returns:
            Dictionary with forecasts for each time period
        """
        logger.info(f"Forecasting progression for {forecast_months} months")
        
        forecasts = {}
        
        # Calculate personalized progression rates if historical data available
        if historical_data and len(historical_data) >= 2:
            progression_rates = self._calculate_personalized_rates(
                historical_data, current_metrics
            )
        else:
            # Use population average rates
            progression_rates = self._get_default_rates()
        
        # Generate forecasts for each time period
        for months in forecast_months:
            years = months / 12.0
            
            forecast = self._generate_forecast(
                current_metrics,
                progression_rates,
                years
            )
            
            forecasts[f'{months}_months'] = forecast
        
        return {
            'forecasts': forecasts,
            'progression_rates': progression_rates,
            'confidence_level': self._calculate_confidence(historical_data)
        }
    
    def _calculate_personalized_rates(
        self,
        historical_data: List[Dict],
        current_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate personalized progression rates from historical data.
        
        Args:
            historical_data: List of historical metric dictionaries
            current_metrics: Current metrics
            
        Returns:
            Dictionary of progression rates per year
        """
        rates = {}
        
        # Sort historical data by date
        sorted_data = sorted(
            historical_data,
            key=lambda x: x.get('recorded_at', datetime.now())
        )
        
        # Calculate rates for each metric
        for metric_name in current_metrics.keys():
            values = []
            timestamps = []
            
            for record in sorted_data:
                if metric_name in record:
                    values.append(record[metric_name])
                    timestamps.append(record.get('recorded_at', datetime.now()))
            
            # Add current value
            values.append(current_metrics[metric_name])
            timestamps.append(datetime.now())
            
            if len(values) >= 2:
                # Calculate rate using linear regression
                rate = self._calculate_rate_of_change(timestamps, values)
                rates[metric_name] = rate
            else:
                # Use default rate
                rates[metric_name] = self._get_default_rate(metric_name)
        
        return rates
    
    def _calculate_rate_of_change(
        self,
        timestamps: List[datetime],
        values: List[float]
    ) -> float:
        """
        Calculate rate of change using linear regression.
        
        Args:
            timestamps: List of timestamps
            values: List of metric values
            
        Returns:
            Rate of change per year
        """
        if len(timestamps) < 2:
            return 0.0
        
        # Convert timestamps to years from first measurement
        base_time = timestamps[0]
        years = np.array([
            (t - base_time).days / 365.25 for t in timestamps
        ]).reshape(-1, 1)
        
        values_array = np.array(values)
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(years, values_array)
        
        # Return slope (rate per year)
        return float(model.coef_[0])
    
    def _get_default_rates(self) -> Dict[str, float]:
        """Get default population-average progression rates."""
        rates = {}
        rates.update(self.cognitive_decline_rates)
        rates.update(self.biomarker_progression_rates)
        rates.update(self.imaging_progression_rates)
        return rates
    
    def _get_default_rate(self, metric_name: str) -> float:
        """Get default rate for a specific metric."""
        all_rates = self._get_default_rates()
        return all_rates.get(metric_name, 0.0)
    
    def _generate_forecast(
        self,
        current_metrics: Dict[str, float],
        progression_rates: Dict[str, float],
        years: float
    ) -> Dict:
        """
        Generate forecast for a specific time period.
        
        Args:
            current_metrics: Current metric values
            progression_rates: Progression rates per year
            years: Number of years to forecast
            
        Returns:
            Dictionary with forecasted values
        """
        forecast = {
            'metrics': {},
            'risk_score': 0.0,
            'stage_prediction': 'unknown'
        }
        
        # Forecast each metric
        for metric_name, current_value in current_metrics.items():
            rate = progression_rates.get(metric_name, 0.0)
            forecasted_value = current_value + (rate * years)
            
            # Apply bounds
            forecasted_value = self._apply_metric_bounds(
                metric_name, forecasted_value
            )
            
            forecast['metrics'][metric_name] = forecasted_value
        
        # Calculate risk score based on forecasted metrics
        forecast['risk_score'] = self._calculate_risk_score(
            forecast['metrics']
        )
        
        # Predict disease stage
        forecast['stage_prediction'] = self._predict_stage(
            forecast['metrics']
        )
        
        return forecast
    
    def _apply_metric_bounds(
        self,
        metric_name: str,
        value: float
    ) -> float:
        """
        Apply realistic bounds to forecasted metric values.
        
        Args:
            metric_name: Name of the metric
            value: Forecasted value
            
        Returns:
            Bounded value
        """
        bounds = {
            'mmse_score': (0, 30),
            'moca_score': (0, 30),
            'cdr_score': (0, 3),
            'csf_abeta42': (0, 2000),
            'csf_tau': (0, 1500),
            'csf_ptau': (0, 150),
            'hippocampal_volume': (1000, 5000),
            'entorhinal_thickness': (0.5, 5.0),
            'cortical_thickness': (1.0, 4.0)
        }
        
        if metric_name in bounds:
            min_val, max_val = bounds[metric_name]
            return max(min_val, min(max_val, value))
        
        return value
    
    def _calculate_risk_score(self, metrics: Dict[str, float]) -> float:
        """
        Calculate overall risk score from metrics.
        
        Args:
            metrics: Dictionary of metric values
            
        Returns:
            Risk score between 0 and 1
        """
        risk_factors = []
        
        # Cognitive scores (lower is worse)
        if 'mmse_score' in metrics:
            mmse_risk = 1.0 - (metrics['mmse_score'] / 30.0)
            risk_factors.append(mmse_risk)
        
        if 'moca_score' in metrics:
            moca_risk = 1.0 - (metrics['moca_score'] / 30.0)
            risk_factors.append(moca_risk)
        
        if 'cdr_score' in metrics:
            cdr_risk = metrics['cdr_score'] / 3.0
            risk_factors.append(cdr_risk)
        
        # Biomarkers
        if 'csf_abeta42' in metrics:
            # Lower Abeta42 indicates higher risk
            abeta_risk = 1.0 - (metrics['csf_abeta42'] / 1000.0)
            abeta_risk = max(0, min(1, abeta_risk))
            risk_factors.append(abeta_risk)
        
        if 'csf_tau' in metrics:
            # Higher tau indicates higher risk
            tau_risk = metrics['csf_tau'] / 800.0
            tau_risk = max(0, min(1, tau_risk))
            risk_factors.append(tau_risk)
        
        # Imaging
        if 'hippocampal_volume' in metrics:
            # Lower volume indicates higher risk
            hipp_risk = 1.0 - (metrics['hippocampal_volume'] / 4000.0)
            hipp_risk = max(0, min(1, hipp_risk))
            risk_factors.append(hipp_risk)
        
        if risk_factors:
            return float(np.mean(risk_factors))
        
        return 0.5  # Default moderate risk
    
    def _predict_stage(self, metrics: Dict[str, float]) -> str:
        """
        Predict disease stage from metrics.
        
        Args:
            metrics: Dictionary of metric values
            
        Returns:
            Predicted stage string
        """
        # Use CDR score if available
        if 'cdr_score' in metrics:
            cdr = metrics['cdr_score']
            if cdr == 0:
                return 'normal'
            elif cdr == 0.5:
                return 'very_mild'
            elif cdr == 1:
                return 'mild'
            elif cdr == 2:
                return 'moderate'
            else:
                return 'severe'
        
        # Use MMSE score
        if 'mmse_score' in metrics:
            mmse = metrics['mmse_score']
            if mmse >= 24:
                return 'normal_or_mild'
            elif mmse >= 18:
                return 'mild'
            elif mmse >= 10:
                return 'moderate'
            else:
                return 'severe'
        
        return 'unknown'
    
    def _calculate_confidence(
        self,
        historical_data: Optional[List[Dict]]
    ) -> float:
        """
        Calculate confidence level for forecasts.
        
        Args:
            historical_data: Historical data points
            
        Returns:
            Confidence score between 0 and 1
        """
        if not historical_data:
            return 0.5  # Moderate confidence with no history
        
        # More data points = higher confidence
        n_points = len(historical_data)
        
        if n_points >= 5:
            return 0.9
        elif n_points >= 3:
            return 0.75
        elif n_points >= 2:
            return 0.6
        else:
            return 0.5
    
    def generate_progression_trajectory(
        self,
        current_metrics: Dict[str, float],
        historical_data: Optional[List[Dict]] = None,
        months_ahead: int = 24,
        interval_months: int = 3
    ) -> Dict:
        """
        Generate detailed progression trajectory with multiple time points.
        
        Args:
            current_metrics: Current health metrics
            historical_data: Optional historical data
            months_ahead: Total months to forecast
            interval_months: Interval between forecast points
            
        Returns:
            Dictionary with trajectory data
        """
        trajectory = {
            'time_points': [],
            'forecasts': []
        }
        
        # Generate forecasts at regular intervals
        for months in range(interval_months, months_ahead + 1, interval_months):
            forecast_result = self.forecast_progression(
                current_metrics,
                historical_data,
                forecast_months=[months]
            )
            
            trajectory['time_points'].append(months)
            trajectory['forecasts'].append(
                forecast_result['forecasts'][f'{months}_months']
            )
        
        return trajectory
    
    def compare_trajectories(
        self,
        baseline_metrics: Dict[str, float],
        intervention_metrics: Dict[str, float],
        months: int = 12
    ) -> Dict:
        """
        Compare progression trajectories with and without intervention.
        
        Args:
            baseline_metrics: Metrics without intervention
            intervention_metrics: Metrics with intervention
            months: Forecast period in months
            
        Returns:
            Dictionary comparing trajectories
        """
        baseline_forecast = self.forecast_progression(
            baseline_metrics,
            forecast_months=[months]
        )
        
        intervention_forecast = self.forecast_progression(
            intervention_metrics,
            forecast_months=[months]
        )
        
        comparison = {
            'baseline': baseline_forecast['forecasts'][f'{months}_months'],
            'intervention': intervention_forecast['forecasts'][f'{months}_months'],
            'improvement': {}
        }
        
        # Calculate improvements
        baseline_risk = comparison['baseline']['risk_score']
        intervention_risk = comparison['intervention']['risk_score']
        
        comparison['improvement'] = {
            'risk_reduction': baseline_risk - intervention_risk,
            'relative_improvement': (
                (baseline_risk - intervention_risk) / baseline_risk * 100
                if baseline_risk > 0 else 0
            )
        }
        
        return comparison
