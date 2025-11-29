"""
Feature Importance Report Generator

Generates comprehensive reports on extracted features including:
- Feature statistics
- Feature distributions
- Feature correlations
- Feature documentation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FeatureReportGenerator:
    """Generate comprehensive feature reports and documentation"""
    
    def __init__(self):
        """Initialize feature report generator"""
        pass
    
    def generate_report(
        self,
        features: pd.DataFrame,
        output_path: Optional[Path] = None
    ) -> Dict:
        """
        Generate comprehensive feature report
        
        Args:
            features: DataFrame with extracted features
            output_path: Optional path to save report
            
        Returns:
            Dictionary with report data
        """
        logger.info("Generating feature report")
        
        report = {
            'summary': self.generate_summary(features),
            'statistics': self.calculate_feature_statistics(features),
            'distributions': self.analyze_distributions(features),
            'correlations': self.calculate_correlations(features),
            'missing_data': self.analyze_missing_data(features),
            'feature_types': self.classify_feature_types(features)
        }
        
        # Save report if path provided
        if output_path:
            self.save_report(report, output_path)
        
        logger.info("Feature report generation complete")
        return report
    
    def generate_summary(self, features: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for the feature set
        
        Args:
            features: DataFrame with features
            
        Returns:
            Dictionary with summary information
        """
        summary = {
            'total_features': len(features.columns),
            'total_samples': len(features),
            'memory_usage_mb': features.memory_usage(deep=True).sum() / 1024**2,
            'feature_categories': self._categorize_features(features)
        }
        
        return summary
    
    def calculate_feature_statistics(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive statistics for each feature
        
        Args:
            features: DataFrame with features
            
        Returns:
            DataFrame with feature statistics
        """
        stats = pd.DataFrame({
            'feature': features.columns,
            'dtype': features.dtypes.values,
            'count': features.count().values,
            'missing': features.isnull().sum().values,
            'missing_pct': (features.isnull().sum() / len(features) * 100).values,
            'unique': features.nunique().values,
            'mean': features.mean(numeric_only=True).reindex(features.columns).values,
            'std': features.std(numeric_only=True).reindex(features.columns).values,
            'min': features.min(numeric_only=True).reindex(features.columns).values,
            'q25': features.quantile(0.25, numeric_only=True).reindex(features.columns).values,
            'median': features.median(numeric_only=True).reindex(features.columns).values,
            'q75': features.quantile(0.75, numeric_only=True).reindex(features.columns).values,
            'max': features.max(numeric_only=True).reindex(features.columns).values,
        })
        
        return stats
    
    def analyze_distributions(self, features: pd.DataFrame) -> Dict[str, Dict]:
        """
        Analyze feature distributions
        
        Args:
            features: DataFrame with features
            
        Returns:
            Dictionary with distribution information
        """
        distributions = {}
        
        for col in features.columns:
            if features[col].dtype in ['float64', 'int64']:
                distributions[col] = {
                    'skewness': features[col].skew(),
                    'kurtosis': features[col].kurtosis(),
                    'is_normal': self._test_normality(features[col]),
                    'outliers_count': self._count_outliers(features[col])
                }
        
        return distributions
    
    def calculate_correlations(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate feature correlations
        
        Args:
            features: DataFrame with features
            
        Returns:
            DataFrame with correlation matrix
        """
        # Calculate correlation matrix for numeric features
        numeric_features = features.select_dtypes(include=[np.number])
        
        if len(numeric_features.columns) > 0:
            correlations = numeric_features.corr()
            return correlations
        else:
            return pd.DataFrame()
    
    def analyze_missing_data(self, features: pd.DataFrame) -> Dict:
        """
        Analyze missing data patterns
        
        Args:
            features: DataFrame with features
            
        Returns:
            Dictionary with missing data analysis
        """
        missing_analysis = {
            'total_missing': features.isnull().sum().sum(),
            'missing_by_feature': features.isnull().sum().to_dict(),
            'features_with_missing': features.columns[features.isnull().any()].tolist(),
            'samples_with_missing': features.isnull().any(axis=1).sum(),
            'complete_samples': (~features.isnull().any(axis=1)).sum()
        }
        
        return missing_analysis
    
    def classify_feature_types(self, features: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Classify features by type
        
        Args:
            features: DataFrame with features
            
        Returns:
            Dictionary mapping feature types to feature names
        """
        feature_types = {
            'cognitive': [],
            'biomarker': [],
            'imaging': [],
            'genetic': [],
            'demographic': [],
            'temporal': [],
            'derived': [],
            'binary': [],
            'continuous': []
        }
        
        for col in features.columns:
            # Classify by name patterns
            col_lower = col.lower()
            
            if any(x in col_lower for x in ['mmse', 'moca', 'cdr', 'adas']):
                feature_types['cognitive'].append(col)
            
            if any(x in col_lower for x in ['csf', 'ab42', 'tau', 'ptau', 'biomarker']):
                feature_types['biomarker'].append(col)
            
            if any(x in col_lower for x in ['hippocampus', 'cortex', 'volume', 'thickness', 'ventricle']):
                feature_types['imaging'].append(col)
            
            if any(x in col_lower for x in ['apoe', 'genetic', 'e4', 'family_history']):
                feature_types['genetic'].append(col)
            
            if any(x in col_lower for x in ['age', 'sex', 'education', 'race', 'bmi']):
                feature_types['demographic'].append(col)
            
            if any(x in col_lower for x in ['time', 'visit', 'rate', 'change', 'trajectory']):
                feature_types['temporal'].append(col)
            
            if any(x in col_lower for x in ['ratio', 'normalized', 'derived', 'score']):
                feature_types['derived'].append(col)
            
            # Classify by data type
            unique_values = features[col].dropna().unique()
            if len(unique_values) <= 2 and set(unique_values).issubset({0, 1, 0.0, 1.0}):
                feature_types['binary'].append(col)
            elif features[col].dtype in ['float64', 'int64']:
                feature_types['continuous'].append(col)
        
        return feature_types
    
    def generate_feature_documentation(
        self,
        features: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Generate markdown documentation for all features
        
        Args:
            features: DataFrame with features
            output_path: Path to save documentation
        """
        logger.info(f"Generating feature documentation at {output_path}")
        
        stats = self.calculate_feature_statistics(features)
        feature_types = self.classify_feature_types(features)
        
        # Create markdown documentation
        doc = ["# Feature Documentation\n\n"]
        doc.append(f"**Total Features:** {len(features.columns)}\n\n")
        doc.append(f"**Total Samples:** {len(features)}\n\n")
        
        # Document by category
        for category, feature_list in feature_types.items():
            if feature_list:
                doc.append(f"## {category.title()} Features\n\n")
                
                for feature in feature_list:
                    feature_stats = stats[stats['feature'] == feature].iloc[0]
                    
                    doc.append(f"### {feature}\n\n")
                    doc.append(f"- **Type:** {feature_stats['dtype']}\n")
                    doc.append(f"- **Missing:** {feature_stats['missing']} ({feature_stats['missing_pct']:.2f}%)\n")
                    doc.append(f"- **Unique Values:** {feature_stats['unique']}\n")
                    
                    if pd.notna(feature_stats['mean']):
                        doc.append(f"- **Mean:** {feature_stats['mean']:.4f}\n")
                        doc.append(f"- **Std:** {feature_stats['std']:.4f}\n")
                        doc.append(f"- **Range:** [{feature_stats['min']:.4f}, {feature_stats['max']:.4f}]\n")
                    
                    doc.append("\n")
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.writelines(doc)
        
        logger.info("Feature documentation generated")
    
    def save_report(self, report: Dict, output_path: Path) -> None:
        """
        Save report to file
        
        Args:
            report: Report dictionary
            output_path: Path to save report
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save statistics as CSV
        if 'statistics' in report:
            stats_path = output_path.parent / f"{output_path.stem}_statistics.csv"
            report['statistics'].to_csv(stats_path, index=False)
            logger.info(f"Statistics saved to {stats_path}")
        
        # Save correlations as CSV
        if 'correlations' in report and not report['correlations'].empty:
            corr_path = output_path.parent / f"{output_path.stem}_correlations.csv"
            report['correlations'].to_csv(corr_path)
            logger.info(f"Correlations saved to {corr_path}")
        
        # Save summary as JSON
        import json
        summary_path = output_path.parent / f"{output_path.stem}_summary.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj
        
        summary_data = {
            'summary': convert_types(report['summary']),
            'missing_data': convert_types(report['missing_data']),
            'feature_types': convert_types(report['feature_types'])
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"Summary saved to {summary_path}")
    
    def _categorize_features(self, features: pd.DataFrame) -> Dict[str, int]:
        """
        Categorize features and count them
        
        Args:
            features: DataFrame with features
            
        Returns:
            Dictionary with feature category counts
        """
        feature_types = self.classify_feature_types(features)
        
        return {
            category: len(feature_list)
            for category, feature_list in feature_types.items()
            if feature_list
        }
    
    def _test_normality(self, series: pd.Series) -> bool:
        """
        Test if a series is normally distributed
        
        Args:
            series: Series to test
            
        Returns:
            True if approximately normal, False otherwise
        """
        from scipy import stats
        
        # Remove NaN values
        clean_series = series.dropna()
        
        if len(clean_series) < 8:
            return False
        
        # Shapiro-Wilk test
        try:
            _, p_value = stats.shapiro(clean_series)
            return p_value > 0.05
        except:
            return False
    
    def _count_outliers(self, series: pd.Series) -> int:
        """
        Count outliers using IQR method
        
        Args:
            series: Series to analyze
            
        Returns:
            Number of outliers
        """
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return 0
        
        q1 = clean_series.quantile(0.25)
        q3 = clean_series.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = (clean_series < lower_bound) | (clean_series > upper_bound)
        
        return outliers.sum()
