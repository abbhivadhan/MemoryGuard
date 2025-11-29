"""Quality Reporter Module - Generates comprehensive data quality reports"""

import pandas as pd
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import logging

from .phi_detector import PHIDetector
from .deidentification_verifier import DeidentificationVerifier
from .completeness_checker import CompletenessChecker
from .outlier_detector import OutlierDetector
from .range_validator import RangeValidator
from .duplicate_detector import DuplicateDetector
from .temporal_validator import TemporalValidator

logger = logging.getLogger(__name__)


class QualityReporter:
    """Generate comprehensive data quality reports"""
    
    def __init__(self):
        """Initialize quality reporter with all validators"""
        self.phi_detector = PHIDetector()
        self.deidentification_verifier = DeidentificationVerifier()
        self.completeness_checker = CompletenessChecker()
        self.outlier_detector = OutlierDetector()
        self.range_validator = RangeValidator()
        self.duplicate_detector = DuplicateDetector()
        self.temporal_validator = TemporalValidator()
        
        logger.info("Initialized QualityReporter with all validators")
    
    def generate_comprehensive_report(self, data: pd.DataFrame,
                                     dataset_name: str = "Unknown",
                                     patient_id_col: Optional[str] = None,
                                     visit_date_col: Optional[str] = None) -> Dict:
        """
        Generate comprehensive data quality report
        
        Args:
            data: DataFrame to analyze
            dataset_name: Name of the dataset
            patient_id_col: Name of patient ID column (optional)
            visit_date_col: Name of visit date column (optional)
            
        Returns:
            Dictionary with complete quality analysis
        """
        logger.info(f"Generating comprehensive quality report for {dataset_name}")
        
        report = {
            'report_metadata': {
                'dataset_name': dataset_name,
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0'
            },
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'column_names': list(data.columns),
                'memory_usage_mb': float(data.memory_usage(deep=True).sum() / 1024 / 1024)
            }
        }
        
        # 1. PHI Detection
        logger.info("Running PHI detection...")
        phi_report = self.phi_detector.get_phi_report(data)
        report['phi_detection'] = phi_report
        
        # 2. De-identification Verification
        logger.info("Running de-identification verification...")
        deident_report = self.deidentification_verifier.comprehensive_verification(data)
        report['deidentification'] = deident_report
        
        # 3. Completeness Check
        logger.info("Running completeness check...")
        completeness_report = self.completeness_checker.generate_completeness_report(data)
        report['completeness'] = completeness_report
        
        # 4. Outlier Detection
        logger.info("Running outlier detection...")
        outlier_report = self.outlier_detector.generate_outlier_report(data, method='both')
        report['outliers'] = outlier_report
        
        # 5. Range Validation
        logger.info("Running range validation...")
        range_report = self.range_validator.generate_range_report(data)
        report['range_validation'] = range_report
        
        # 6. Duplicate Detection
        logger.info("Running duplicate detection...")
        duplicate_report = self.duplicate_detector.generate_duplicate_report(
            data, patient_id_col, visit_date_col
        )
        report['duplicates'] = duplicate_report
        
        # 7. Temporal Validation (if applicable)
        if patient_id_col and visit_date_col:
            logger.info("Running temporal validation...")
            temporal_report = self.temporal_validator.comprehensive_temporal_validation(
                data, patient_id_col, visit_date_col
            )
            report['temporal_consistency'] = temporal_report
        
        # Overall Quality Score
        quality_score = self._calculate_quality_score(report)
        report['quality_score'] = quality_score
        
        # Overall Assessment
        report['overall_assessment'] = self._generate_assessment(report)
        
        logger.info(f"Report generation complete. Quality score: {quality_score['overall_score']:.1f}/100")
        
        return report
    
    def _calculate_quality_score(self, report: Dict) -> Dict:
        """
        Calculate overall quality score based on all checks
        
        Args:
            report: Complete quality report
            
        Returns:
            Dictionary with quality scores
        """
        scores = {}
        weights = {}
        
        # PHI Detection (20 points)
        phi_passed = not report['phi_detection']['phi_detected']
        scores['phi_detection'] = 20 if phi_passed else 0
        weights['phi_detection'] = 20
        
        # De-identification (15 points)
        deident_passed = report['deidentification']['verification_passed']
        scores['deidentification'] = 15 if deident_passed else 0
        weights['deidentification'] = 15
        
        # Completeness (20 points)
        completeness_pct = report['completeness']['validation']['overall_completeness']
        scores['completeness'] = completeness_pct * 20
        weights['completeness'] = 20
        
        # Outliers (10 points) - score based on percentage of outliers
        outlier_summary = report['outliers']['summary']
        if 'total_outliers_iqr' in outlier_summary and outlier_summary['total_outliers_iqr'] is not None:
            total_cells = report['dataset_info']['rows'] * outlier_summary['columns_analyzed']
            outlier_pct = outlier_summary['total_outliers_iqr'] / total_cells if total_cells > 0 else 0
            scores['outliers'] = max(0, 10 * (1 - outlier_pct * 10))  # Penalize high outlier rates
        else:
            scores['outliers'] = 10
        weights['outliers'] = 10
        
        # Range Validation (15 points)
        range_passed = report['range_validation']['validation_summary']['validation_passed']
        if range_passed:
            scores['range_validation'] = 15
        else:
            # Partial credit based on percentage of columns passing
            validated = report['range_validation']['validation_summary']['validated_columns']
            violations = report['range_validation']['validation_summary']['columns_with_violations']
            if validated > 0:
                scores['range_validation'] = 15 * (1 - violations / validated)
            else:
                scores['range_validation'] = 15
        weights['range_validation'] = 15
        
        # Duplicates (10 points)
        duplicate_passed = report['duplicates']['validation_passed']
        scores['duplicates'] = 10 if duplicate_passed else 5  # Partial credit
        weights['duplicates'] = 10
        
        # Temporal Consistency (10 points) - if applicable
        if 'temporal_consistency' in report:
            temporal_passed = report['temporal_consistency']['validation_passed']
            scores['temporal_consistency'] = 10 if temporal_passed else 5
            weights['temporal_consistency'] = 10
        else:
            # Redistribute weight if temporal not applicable
            weights['completeness'] += 5
            weights['range_validation'] += 5
        
        # Calculate overall score
        total_score = sum(scores.values())
        max_score = sum(weights.values())
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'overall_score': round(overall_score, 1),
            'max_score': max_score,
            'component_scores': scores,
            'component_weights': weights,
            'grade': self._get_grade(overall_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_assessment(self, report: Dict) -> Dict:
        """
        Generate overall assessment and recommendations
        
        Args:
            report: Complete quality report
            
        Returns:
            Dictionary with assessment and recommendations
        """
        issues = []
        recommendations = []
        warnings = []
        
        # Check PHI
        if report['phi_detection']['phi_detected']:
            issues.append("PHI detected in dataset")
            recommendations.append("Remove or quarantine columns containing PHI before proceeding")
            warnings.append("CRITICAL: Dataset contains Protected Health Information")
        
        # Check de-identification
        if not report['deidentification']['verification_passed']:
            issues.append("De-identification verification failed")
            recommendations.append("Ensure all direct identifiers are removed and k-anonymity is satisfied")
        
        # Check completeness
        completeness_pct = report['completeness']['validation']['overall_completeness']
        if completeness_pct < 0.70:
            issues.append(f"Dataset completeness below threshold ({completeness_pct*100:.1f}% < 70%)")
            recommendations.append("Consider data imputation or additional data collection")
            warnings.append("Dataset may not be suitable for ML training due to low completeness")
        elif completeness_pct < 0.85:
            warnings.append(f"Dataset completeness is moderate ({completeness_pct*100:.1f}%)")
            recommendations.append("Review missing data patterns and consider imputation strategies")
        
        # Check outliers
        outlier_summary = report['outliers']['summary']
        if outlier_summary['columns_with_outliers'] > 0:
            warnings.append(f"{outlier_summary['columns_with_outliers']} columns contain outliers")
            recommendations.append("Review outliers to determine if they are errors or valid extreme values")
        
        # Check range violations
        if not report['range_validation']['validation_summary']['validation_passed']:
            violations_count = report['range_validation']['validation_summary']['columns_with_violations']
            issues.append(f"{violations_count} columns have values outside expected ranges")
            recommendations.append("Investigate and correct out-of-range values")
        
        # Check duplicates
        if not report['duplicates']['validation_passed']:
            issues.append("Duplicate records detected")
            recommendations.append("Remove or consolidate duplicate records")
        
        # Check temporal consistency
        if 'temporal_consistency' in report and not report['temporal_consistency']['validation_passed']:
            issues.append("Temporal consistency violations found")
            recommendations.append("Verify and correct date sequences in longitudinal data")
        
        # Overall recommendation
        quality_score = report['quality_score']['overall_score']
        
        if quality_score >= 90:
            overall_status = "EXCELLENT"
            overall_recommendation = "Dataset meets high quality standards and is ready for ML training"
        elif quality_score >= 80:
            overall_status = "GOOD"
            overall_recommendation = "Dataset quality is good. Address minor issues before ML training"
        elif quality_score >= 70:
            overall_status = "ACCEPTABLE"
            overall_recommendation = "Dataset quality is acceptable but improvements recommended"
        elif quality_score >= 60:
            overall_status = "POOR"
            overall_recommendation = "Dataset quality is poor. Significant improvements required before use"
        else:
            overall_status = "UNACCEPTABLE"
            overall_recommendation = "Dataset quality is unacceptable. Do not use for ML training"
        
        return {
            'overall_status': overall_status,
            'overall_recommendation': overall_recommendation,
            'issues_found': len(issues),
            'issues': issues,
            'warnings': warnings,
            'recommendations': recommendations,
            'ready_for_ml': quality_score >= 70 and not report['phi_detection']['phi_detected']
        }
    
    def save_report(self, report: Dict, output_path: Path, format: str = 'json'):
        """
        Save quality report to file
        
        Args:
            report: Quality report dictionary
            output_path: Path to save report
            format: Output format ('json' or 'html')
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {output_path}")
        
        elif format == 'html':
            html_content = self._generate_html_report(report)
            with open(output_path, 'w') as f:
                f.write(html_content)
            logger.info(f"HTML report saved to {output_path}")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, report: Dict) -> str:
        """Generate HTML version of the report"""
        quality_score = report['quality_score']
        assessment = report['overall_assessment']
        
        # Determine color based on score
        if quality_score['overall_score'] >= 80:
            score_color = '#28a745'  # Green
        elif quality_score['overall_score'] >= 60:
            score_color = '#ffc107'  # Yellow
        else:
            score_color = '#dc3545'  # Red
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Quality Report - {report['report_metadata']['dataset_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .score-box {{ background-color: {score_color}; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
        .score-box h2 {{ color: white; margin: 0; }}
        .score-box .score {{ font-size: 48px; font-weight: bold; }}
        .score-box .grade {{ font-size: 36px; }}
        .status-box {{ padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .status-excellent {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
        .status-good {{ background-color: #d1ecf1; border-left: 4px solid #17a2b8; }}
        .status-acceptable {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
        .status-poor {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .metric {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric-name {{ font-weight: bold; color: #555; }}
        .metric-value {{ font-size: 18px; color: #007bff; }}
        .issue {{ color: #dc3545; margin: 5px 0; }}
        .warning {{ color: #ffc107; margin: 5px 0; }}
        .recommendation {{ color: #17a2b8; margin: 5px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .pass {{ color: #28a745; font-weight: bold; }}
        .fail {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Quality Report</h1>
        <p><strong>Dataset:</strong> {report['report_metadata']['dataset_name']}</p>
        <p><strong>Generated:</strong> {report['report_metadata']['generated_at']}</p>
        <p><strong>Rows:</strong> {report['dataset_info']['rows']:,} | <strong>Columns:</strong> {report['dataset_info']['columns']}</p>
        
        <div class="score-box">
            <h2>Overall Quality Score</h2>
            <div class="score">{quality_score['overall_score']:.1f}/100</div>
            <div class="grade">Grade: {quality_score['grade']}</div>
        </div>
        
        <div class="status-box status-{assessment['overall_status'].lower()}">
            <h3>Status: {assessment['overall_status']}</h3>
            <p>{assessment['overall_recommendation']}</p>
            <p><strong>Ready for ML Training:</strong> {'✓ Yes' if assessment['ready_for_ml'] else '✗ No'}</p>
        </div>
        
        <h2>Issues and Recommendations</h2>
        <div class="metric">
            <p><strong>Issues Found:</strong> {assessment['issues_found']}</p>
            {''.join([f'<p class="issue">• {issue}</p>' for issue in assessment['issues']])}
            {''.join([f'<p class="warning">⚠ {warning}</p>' for warning in assessment['warnings']])}
            {''.join([f'<p class="recommendation">→ {rec}</p>' for rec in assessment['recommendations']])}
        </div>
        
        <h2>Validation Results</h2>
        <table>
            <tr>
                <th>Check</th>
                <th>Status</th>
                <th>Score</th>
                <th>Details</th>
            </tr>
            <tr>
                <td>PHI Detection</td>
                <td class="{'pass' if not report['phi_detection']['phi_detected'] else 'fail'}">
                    {'✓ PASS' if not report['phi_detection']['phi_detected'] else '✗ FAIL'}
                </td>
                <td>{quality_score['component_scores']['phi_detection']}/{quality_score['component_weights']['phi_detection']}</td>
                <td>{'No PHI detected' if not report['phi_detection']['phi_detected'] else f"PHI found in {len(report['phi_detection']['phi_columns'])} categories"}</td>
            </tr>
            <tr>
                <td>De-identification</td>
                <td class="{'pass' if report['deidentification']['verification_passed'] else 'fail'}">
                    {'✓ PASS' if report['deidentification']['verification_passed'] else '✗ FAIL'}
                </td>
                <td>{quality_score['component_scores']['deidentification']}/{quality_score['component_weights']['deidentification']}</td>
                <td>k-anonymity: {report['deidentification']['checks']['k_anonymity'].get('min_k', 'N/A')}</td>
            </tr>
            <tr>
                <td>Completeness</td>
                <td class="{'pass' if report['completeness']['validation']['validation_passed'] else 'fail'}">
                    {'✓ PASS' if report['completeness']['validation']['validation_passed'] else '✗ FAIL'}
                </td>
                <td>{quality_score['component_scores']['completeness']:.1f}/{quality_score['component_weights']['completeness']}</td>
                <td>{report['completeness']['validation']['overall_completeness']*100:.1f}% complete</td>
            </tr>
            <tr>
                <td>Range Validation</td>
                <td class="{'pass' if report['range_validation']['validation_summary']['validation_passed'] else 'fail'}">
                    {'✓ PASS' if report['range_validation']['validation_summary']['validation_passed'] else '✗ FAIL'}
                </td>
                <td>{quality_score['component_scores']['range_validation']:.1f}/{quality_score['component_weights']['range_validation']}</td>
                <td>{report['range_validation']['validation_summary']['columns_with_violations']} columns with violations</td>
            </tr>
            <tr>
                <td>Duplicates</td>
                <td class="{'pass' if report['duplicates']['validation_passed'] else 'fail'}">
                    {'✓ PASS' if report['duplicates']['validation_passed'] else '✗ FAIL'}
                </td>
                <td>{quality_score['component_scores']['duplicates']}/{quality_score['component_weights']['duplicates']}</td>
                <td>{report['duplicates']['exact_duplicates']['duplicate_rows']} duplicate rows</td>
            </tr>
        </table>
        
        <p style="text-align: center; color: #888; margin-top: 40px;">
            Generated by ML Pipeline Data Validation Engine v{report['report_metadata']['report_version']}
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def get_summary_text(self, report: Dict) -> str:
        """
        Get human-readable text summary of the report
        
        Args:
            report: Quality report dictionary
            
        Returns:
            Formatted string summary
        """
        quality_score = report['quality_score']
        assessment = report['overall_assessment']
        
        summary = f"""
{'='*70}
DATA QUALITY REPORT
{'='*70}

Dataset: {report['report_metadata']['dataset_name']}
Generated: {report['report_metadata']['generated_at']}
Rows: {report['dataset_info']['rows']:,} | Columns: {report['dataset_info']['columns']}

{'='*70}
OVERALL QUALITY SCORE: {quality_score['overall_score']:.1f}/100 (Grade: {quality_score['grade']})
{'='*70}

Status: {assessment['overall_status']}
{assessment['overall_recommendation']}

Ready for ML Training: {'✓ YES' if assessment['ready_for_ml'] else '✗ NO'}

{'='*70}
VALIDATION RESULTS
{'='*70}

PHI Detection:        {'✓ PASS' if not report['phi_detection']['phi_detected'] else '✗ FAIL'}
De-identification:    {'✓ PASS' if report['deidentification']['verification_passed'] else '✗ FAIL'}
Completeness:         {'✓ PASS' if report['completeness']['validation']['validation_passed'] else '✗ FAIL'} ({report['completeness']['validation']['overall_completeness']*100:.1f}%)
Range Validation:     {'✓ PASS' if report['range_validation']['validation_summary']['validation_passed'] else '✗ FAIL'}
Duplicates:           {'✓ PASS' if report['duplicates']['validation_passed'] else '✗ FAIL'}

{'='*70}
ISSUES AND RECOMMENDATIONS
{'='*70}

Issues Found: {assessment['issues_found']}
"""
        
        if assessment['issues']:
            summary += "\nIssues:\n"
            for issue in assessment['issues']:
                summary += f"  ✗ {issue}\n"
        
        if assessment['warnings']:
            summary += "\nWarnings:\n"
            for warning in assessment['warnings']:
                summary += f"  ⚠ {warning}\n"
        
        if assessment['recommendations']:
            summary += "\nRecommendations:\n"
            for rec in assessment['recommendations']:
                summary += f"  → {rec}\n"
        
        summary += "\n" + "="*70
        
        return summary
