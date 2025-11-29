"""
Drift reporting system
Generates comprehensive weekly drift reports
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Optional visualization dependencies
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

from ml_pipeline.config.settings import settings
from ml_pipeline.monitoring.distribution_monitor import DistributionMonitor
from ml_pipeline.monitoring.drift_detector import DriftDetector
from ml_pipeline.monitoring.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class DriftReporter:
    """
    Generate comprehensive drift reports
    Combines distribution monitoring, drift detection, and performance tracking
    """
    
    def __init__(
        self,
        report_storage_path: Optional[Path] = None
    ):
        """
        Initialize drift reporter
        
        Args:
            report_storage_path: Path to store reports
        """
        if report_storage_path is None:
            report_storage_path = settings.METADATA_PATH / "reports"
        self.report_storage_path = report_storage_path
        self.report_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized DriftReporter with storage: {report_storage_path}")
    
    def generate_weekly_report(
        self,
        distribution_monitor: DistributionMonitor,
        drift_detector: DriftDetector,
        performance_tracker: Optional[PerformanceTracker] = None,
        current_data: Optional[pd.DataFrame] = None,
        report_name: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive weekly drift report
        
        Args:
            distribution_monitor: Distribution monitor instance
            drift_detector: Drift detector instance
            performance_tracker: Performance tracker instance (optional)
            current_data: Current data for drift detection (optional)
            report_name: Custom report name (optional)
            
        Returns:
            Report dictionary
        """
        if report_name is None:
            report_name = f"weekly_drift_report_{datetime.now().strftime('%Y%m%d')}"
        
        logger.info(f"Generating weekly drift report: {report_name}")
        
        # Initialize report
        report = {
            'report_name': report_name,
            'report_type': 'weekly_drift',
            'generated_at': datetime.now().isoformat(),
            'period_start': (datetime.now() - timedelta(days=7)).isoformat(),
            'period_end': datetime.now().isoformat()
        }
        
        # 1. Distribution summary
        logger.info("Generating distribution summary...")
        report['distribution_summary'] = self._generate_distribution_summary(
            distribution_monitor
        )
        
        # 2. Drift detection results
        if current_data is not None:
            logger.info("Running drift detection...")
            drift_results = drift_detector.detect_drift(current_data)
            report['drift_detection'] = drift_results
            
            # Drift summary
            report['drift_summary'] = {
                'drift_detected': drift_results['drift_detected'],
                'retraining_recommended': drift_results['retraining_recommended'],
                'n_features_with_ks_drift': len(drift_results.get('features_with_ks_drift', [])),
                'n_features_with_high_psi': len(drift_results.get('features_with_high_psi', []))
            }
        
        # 3. Performance tracking
        if performance_tracker is not None:
            logger.info("Generating performance summary...")
            report['performance_summary'] = self._generate_performance_summary(
                performance_tracker
            )
        
        # 4. Recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        # Save report
        self._save_report(report)
        
        # Generate visualizations
        if current_data is not None:
            self._generate_visualizations(report, distribution_monitor, drift_detector)
        
        logger.info(f"Weekly drift report generated: {report_name}")
        
        return report
    
    def _generate_distribution_summary(
        self,
        distribution_monitor: DistributionMonitor
    ) -> Dict:
        """
        Generate distribution summary
        
        Args:
            distribution_monitor: Distribution monitor instance
            
        Returns:
            Distribution summary
        """
        summary = {
            'reference_distributions_available': distribution_monitor.reference_distributions is not None,
            'n_tracked_distributions': len(distribution_monitor.distribution_history)
        }
        
        if distribution_monitor.reference_distributions:
            summary['n_features'] = len(distribution_monitor.reference_distributions)
            
            # Get feature names
            summary['features'] = list(distribution_monitor.reference_distributions.keys())
        
        # Recent distribution changes
        if distribution_monitor.distribution_history:
            recent_history = distribution_monitor.distribution_history[-7:]  # Last 7 entries
            summary['recent_tracking_count'] = len(recent_history)
        
        return summary
    
    def _generate_performance_summary(
        self,
        performance_tracker: PerformanceTracker
    ) -> Dict:
        """
        Generate performance summary
        
        Args:
            performance_tracker: Performance tracker instance
            
        Returns:
            Performance summary
        """
        # Load recent performance
        performance_tracker.load_performance_history(days=7)
        
        summary = {
            'model_name': performance_tracker.model_name,
            'n_tracking_entries': len(performance_tracker.performance_history)
        }
        
        if performance_tracker.performance_history:
            # Most recent performance
            recent = performance_tracker.performance_history[-1]
            summary['most_recent_metrics'] = recent['metrics']
            summary['most_recent_timestamp'] = recent['timestamp']
            
            # Performance degradation check
            degraded, details = performance_tracker.detect_performance_degradation()
            summary['degradation_detected'] = degraded
            summary['degradation_details'] = details
            
            # Trend analysis
            df = performance_tracker.get_performance_summary()
            if not df.empty and 'accuracy' in df.columns:
                summary['accuracy_trend'] = {
                    'mean': float(df['accuracy'].mean()),
                    'std': float(df['accuracy'].std()),
                    'min': float(df['accuracy'].min()),
                    'max': float(df['accuracy'].max())
                }
        
        return summary
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """
        Generate recommendations based on report findings
        
        Args:
            report: Report dictionary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check drift detection
        if 'drift_summary' in report:
            drift_summary = report['drift_summary']
            
            if drift_summary['drift_detected']:
                recommendations.append(
                    f"⚠️ Data drift detected in {drift_summary['n_features_with_high_psi']} "
                    f"features. Review drift analysis and consider retraining."
                )
            
            if drift_summary['retraining_recommended']:
                recommendations.append(
                    "🔄 Model retraining is recommended based on drift analysis."
                )
        
        # Check performance
        if 'performance_summary' in report:
            perf_summary = report['performance_summary']
            
            if perf_summary.get('degradation_detected', False):
                recommendations.append(
                    "📉 Model performance degradation detected. "
                    "Investigate root causes and consider retraining."
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ No significant drift or performance issues detected. "
                "Continue monitoring."
            )
        
        recommendations.append(
            "📊 Review detailed metrics and visualizations for deeper insights."
        )
        
        return recommendations
    
    def _save_report(self, report: Dict) -> None:
        """
        Save report to storage
        
        Args:
            report: Report dictionary
        """
        filepath = self.report_storage_path / f"{report['report_name']}.json"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved: {filepath}")
    
    def _generate_visualizations(
        self,
        report: Dict,
        distribution_monitor: DistributionMonitor,
        drift_detector: DriftDetector
    ) -> None:
        """
        Generate visualization plots for the report
        
        Args:
            report: Report dictionary
            distribution_monitor: Distribution monitor instance
            drift_detector: Drift detector instance
        """
        if not VISUALIZATION_AVAILABLE:
            logger.warning("Visualization libraries not available, skipping plots")
            return
        
        try:
            viz_dir = self.report_storage_path / f"{report['report_name']}_visualizations"
            viz_dir.mkdir(exist_ok=True)
            
            # 1. PSI scores plot
            if 'drift_detection' in report and 'psi_scores' in report['drift_detection']:
                self._plot_psi_scores(
                    report['drift_detection']['psi_scores'],
                    viz_dir / "psi_scores.png"
                )
            
            # 2. Distribution comparison plots (top drifted features)
            if 'drift_detection' in report:
                drift_results = report['drift_detection']
                high_psi_features = drift_results.get('features_with_high_psi', [])[:5]
                
                for feature in high_psi_features:
                    self._plot_distribution_comparison(
                        distribution_monitor,
                        feature,
                        viz_dir / f"distribution_{feature}.png"
                    )
            
            logger.info(f"Visualizations saved to {viz_dir}")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    def _plot_psi_scores(self, psi_scores: Dict[str, float], filepath: Path) -> None:
        """
        Plot PSI scores
        
        Args:
            psi_scores: Dictionary of PSI scores
            filepath: Output file path
        """
        if not psi_scores:
            return
        
        # Sort by PSI score
        sorted_scores = sorted(psi_scores.items(), key=lambda x: x[1], reverse=True)
        features = [f for f, _ in sorted_scores[:20]]  # Top 20
        scores = [s for _, s in sorted_scores[:20]]
        
        plt.figure(figsize=(12, 6))
        colors = ['red' if s >= 0.2 else 'orange' if s >= 0.1 else 'green' for s in scores]
        plt.barh(features, scores, color=colors)
        plt.xlabel('PSI Score')
        plt.ylabel('Feature')
        plt.title('Population Stability Index (PSI) by Feature')
        plt.axvline(x=0.2, color='red', linestyle='--', label='High drift threshold (0.2)')
        plt.axvline(x=0.1, color='orange', linestyle='--', label='Moderate drift threshold (0.1)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
    
    def _plot_distribution_comparison(
        self,
        distribution_monitor: DistributionMonitor,
        feature: str,
        filepath: Path
    ) -> None:
        """
        Plot distribution comparison for a feature
        
        Args:
            distribution_monitor: Distribution monitor instance
            feature: Feature name
            filepath: Output file path
        """
        try:
            summary = distribution_monitor.get_distribution_summary(feature)
            
            if summary.empty:
                return
            
            plt.figure(figsize=(12, 6))
            
            # Plot mean over time
            plt.subplot(1, 2, 1)
            plt.plot(summary['timestamp'], summary['mean'], marker='o')
            plt.xlabel('Time')
            plt.ylabel('Mean')
            plt.title(f'{feature} - Mean Over Time')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Plot std over time
            plt.subplot(1, 2, 2)
            plt.plot(summary['timestamp'], summary['std'], marker='o', color='orange')
            plt.xlabel('Time')
            plt.ylabel('Standard Deviation')
            plt.title(f'{feature} - Std Dev Over Time')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting distribution for {feature}: {e}")
    
    def load_report(self, report_name: str) -> Dict:
        """
        Load a saved report
        
        Args:
            report_name: Name of the report
            
        Returns:
            Report dictionary
        """
        filepath = self.report_storage_path / f"{report_name}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Report not found: {filepath}")
        
        with open(filepath, 'r') as f:
            report = json.load(f)
        
        logger.info(f"Loaded report: {report_name}")
        return report
    
    def list_reports(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[str]:
        """
        List available reports
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of report names
        """
        reports = []
        
        for filepath in sorted(self.report_storage_path.glob("*.json")):
            report_name = filepath.stem
            
            # Filter by date if specified
            if start_date or end_date:
                try:
                    with open(filepath, 'r') as f:
                        report = json.load(f)
                    
                    report_time = datetime.fromisoformat(report['generated_at'])
                    
                    if start_date and report_time < start_date:
                        continue
                    if end_date and report_time > end_date:
                        continue
                except Exception:
                    continue
            
            reports.append(report_name)
        
        return reports
    
    def generate_summary_report(
        self,
        days: int = 30
    ) -> Dict:
        """
        Generate summary report for the last N days
        
        Args:
            days: Number of days to summarize
            
        Returns:
            Summary report dictionary
        """
        start_date = datetime.now() - timedelta(days=days)
        report_names = self.list_reports(start_date=start_date)
        
        summary = {
            'summary_type': f'{days}_day_summary',
            'generated_at': datetime.now().isoformat(),
            'period_start': start_date.isoformat(),
            'period_end': datetime.now().isoformat(),
            'n_reports': len(report_names),
            'reports': []
        }
        
        # Aggregate statistics
        total_drift_detected = 0
        total_retraining_recommended = 0
        
        for report_name in report_names:
            try:
                report = self.load_report(report_name)
                
                summary['reports'].append({
                    'name': report_name,
                    'generated_at': report['generated_at'],
                    'drift_detected': report.get('drift_summary', {}).get('drift_detected', False),
                    'retraining_recommended': report.get('drift_summary', {}).get('retraining_recommended', False)
                })
                
                if report.get('drift_summary', {}).get('drift_detected', False):
                    total_drift_detected += 1
                if report.get('drift_summary', {}).get('retraining_recommended', False):
                    total_retraining_recommended += 1
                    
            except Exception as e:
                logger.error(f"Error loading report {report_name}: {e}")
        
        summary['statistics'] = {
            'drift_detected_count': total_drift_detected,
            'retraining_recommended_count': total_retraining_recommended,
            'drift_rate': total_drift_detected / len(report_names) if report_names else 0
        }
        
        return summary
