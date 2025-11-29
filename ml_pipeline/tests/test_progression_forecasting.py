"""
Tests for Progression Forecasting Module

Basic tests to verify the forecasting components work correctly.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasting import (
    ProgressionForecaster,
    SequenceBuilder,
    UncertaintyQuantifier,
    ProgressionForecastingTrainer,
    ForecastEvaluator
)


def generate_test_data(n_patients=20, n_visits=6):
    """Generate small test dataset."""
    data = []
    
    for patient_id in range(n_patients):
        baseline_mmse = np.random.uniform(20, 28)
        decline_rate = np.random.uniform(0.3, 0.8)
        
        for visit_num in range(n_visits):
            months = visit_num * 6
            mmse = baseline_mmse - (decline_rate * months / 12)
            mmse = np.clip(mmse + np.random.normal(0, 0.5), 10, 30)
            
            data.append({
                'patient_id': f'P{patient_id:03d}',
                'visit_date': pd.Timestamp('2020-01-01') + pd.DateOffset(months=months),
                'mmse_score': mmse,
                'age': 70 + (months / 12),
                'sex': np.random.choice([0, 1]),
                'education': np.random.randint(12, 18),
                'apoe_e4_count': np.random.choice([0, 1, 2]),
                'csf_ab42': np.random.normal(800, 100),
                'hippocampus_volume': 3500 - (months * 5)
            })
    
    return pd.DataFrame(data)


class TestSequenceBuilder:
    """Test SequenceBuilder functionality."""
    
    def test_initialization(self):
        """Test SequenceBuilder initialization."""
        builder = SequenceBuilder(
            sequence_length=4,
            forecast_horizons=[6, 12, 24]
        )
        
        assert builder.sequence_length == 4
        assert builder.forecast_horizons == [6, 12, 24]
    
    def test_prepare_sequences(self):
        """Test sequence preparation."""
        data = generate_test_data(n_patients=20, n_visits=6)
        
        builder = SequenceBuilder(sequence_length=3, forecast_horizons=[6])
        
        X, y, patient_ids = builder.prepare_sequences(
            data,
            patient_id_col='patient_id',
            visit_date_col='visit_date',
            target_col='mmse_score'
        )
        
        # Check shapes
        assert X.ndim == 3  # (n_samples, sequence_length, n_features)
        assert y.ndim == 2  # (n_samples, n_horizons)
        assert X.shape[0] == y.shape[0]
        assert X.shape[1] == 3  # sequence_length
        assert y.shape[1] == 1  # 1 horizon
        
        # Check no NaN values
        assert not np.isnan(X).any()
        assert not np.isnan(y).any()
    
    def test_temporal_features(self):
        """Test temporal feature creation."""
        data = generate_test_data(n_patients=10, n_visits=5)
        
        builder = SequenceBuilder()
        data_with_temporal = builder.create_temporal_features(data)
        
        assert 'months_since_baseline' in data_with_temporal.columns
        assert 'visit_number' in data_with_temporal.columns


class TestProgressionForecaster:
    """Test ProgressionForecaster functionality."""
    
    def test_initialization(self):
        """Test forecaster initialization."""
        forecaster = ProgressionForecaster(
            sequence_length=4,
            n_features=10,
            lstm_units=[64, 32],
            dropout_rate=0.3
        )
        
        assert forecaster.sequence_length == 4
        assert forecaster.n_features == 10
        assert forecaster.lstm_units == [64, 32]
    
    def test_build_model(self):
        """Test model building."""
        forecaster = ProgressionForecaster(
            sequence_length=4,
            n_features=10,
            lstm_units=[64, 32]
        )
        
        model = forecaster.build_model()
        
        assert model is not None
        assert forecaster.model is not None
        
        # Check input/output shapes
        assert model.input_shape == (None, 4, 10)
        assert model.output_shape == (None, 3)  # 3 horizons


class TestUncertaintyQuantifier:
    """Test UncertaintyQuantifier functionality."""
    
    def test_initialization(self):
        """Test quantifier initialization."""
        quantifier = UncertaintyQuantifier(
            n_mc_samples=50,
            confidence_level=0.95
        )
        
        assert quantifier.n_mc_samples == 50
        assert quantifier.confidence_level == 0.95
    
    def test_prediction_intervals(self):
        """Test prediction interval calculation."""
        quantifier = UncertaintyQuantifier(confidence_level=0.95)
        
        predictions = np.array([[25.0, 24.0, 23.0]])
        std_predictions = np.array([[1.0, 1.5, 2.0]])
        
        lower, upper = quantifier.calculate_prediction_intervals(
            predictions,
            std_predictions,
            method='gaussian'
        )
        
        assert lower.shape == predictions.shape
        assert upper.shape == predictions.shape
        assert np.all(lower < predictions)
        assert np.all(upper > predictions)


class TestForecastEvaluator:
    """Test ForecastEvaluator functionality."""
    
    def test_initialization(self):
        """Test evaluator initialization."""
        evaluator = ForecastEvaluator(
            mae_threshold=3.0,
            forecast_horizons=[6, 12, 24]
        )
        
        assert evaluator.mae_threshold == 3.0
        assert evaluator.forecast_horizons == [6, 12, 24]
    
    def test_evaluate_accuracy(self):
        """Test accuracy evaluation."""
        evaluator = ForecastEvaluator(
            mae_threshold=3.0,
            forecast_horizons=[6, 12, 24]
        )
        
        # Create test data
        y_true = np.array([
            [25.0, 24.0, 23.0],
            [26.0, 25.0, 24.0],
            [24.0, 23.0, 22.0]
        ])
        
        y_pred = np.array([
            [24.5, 23.5, 22.5],
            [25.5, 24.5, 23.5],
            [24.5, 23.5, 22.5]
        ])
        
        metrics = evaluator.evaluate_accuracy(y_true, y_pred)
        
        # Check metrics exist
        assert 'overall_mae' in metrics
        assert 'overall_rmse' in metrics
        assert 'overall_r2' in metrics
        assert '6_month_mae' in metrics
        assert '12_month_mae' in metrics
        assert '24_month_mae' in metrics
        
        # Check MAE is reasonable
        assert metrics['overall_mae'] < 3.0
    
    def test_validate_requirements(self):
        """Test requirement validation."""
        evaluator = ForecastEvaluator(mae_threshold=3.0)
        
        # Good metrics
        good_metrics = {
            'overall_mae': 2.5,
            'overall_r2': 0.8,
            '6_month_mae': 2.3,
            '12_month_mae': 2.5,
            '24_month_mae': 2.7
        }
        
        passes, issues = evaluator.validate_requirements(good_metrics)
        assert passes
        assert len(issues) == 0
        
        # Bad metrics
        bad_metrics = {
            'overall_mae': 3.5,
            'overall_r2': 0.8,
            '6_month_mae': 3.2,
            '12_month_mae': 3.5,
            '24_month_mae': 3.8
        }
        
        passes, issues = evaluator.validate_requirements(bad_metrics)
        assert not passes
        assert len(issues) > 0


def test_integration():
    """Integration test of the full pipeline."""
    # Generate test data
    data = generate_test_data(n_patients=30, n_visits=6)
    
    # Initialize trainer
    trainer = ProgressionForecastingTrainer(
        sequence_length=3,
        forecast_horizons=[6, 12],
        lstm_units=[32, 16],
        output_dir=Path('ml_pipeline/models/test_forecasting')
    )
    
    # Prepare data
    feature_cols = ['age', 'sex', 'education', 'apoe_e4_count', 'csf_ab42', 'hippocampus_volume']
    
    data_splits = trainer.prepare_data(
        data,
        feature_cols=feature_cols,
        add_temporal_features=False,
        add_rate_features=False
    )
    
    # Check data splits
    assert 'X_train' in data_splits
    assert 'y_train' in data_splits
    assert 'X_val' in data_splits
    assert 'y_val' in data_splits
    assert 'X_test' in data_splits
    assert 'y_test' in data_splits
    
    # Check shapes
    assert data_splits['X_train'].shape[1] == 3  # sequence_length
    assert data_splits['y_train'].shape[1] == 2  # 2 horizons
    
    print("✓ All tests passed!")


if __name__ == '__main__':
    # Run tests
    print("Running Progression Forecasting Tests...")
    print()
    
    # Test SequenceBuilder
    print("Testing SequenceBuilder...")
    test_sb = TestSequenceBuilder()
    test_sb.test_initialization()
    test_sb.test_prepare_sequences()
    test_sb.test_temporal_features()
    print("✓ SequenceBuilder tests passed")
    print()
    
    # Test ProgressionForecaster
    print("Testing ProgressionForecaster...")
    test_pf = TestProgressionForecaster()
    test_pf.test_initialization()
    test_pf.test_build_model()
    print("✓ ProgressionForecaster tests passed")
    print()
    
    # Test UncertaintyQuantifier
    print("Testing UncertaintyQuantifier...")
    test_uq = TestUncertaintyQuantifier()
    test_uq.test_initialization()
    test_uq.test_prediction_intervals()
    print("✓ UncertaintyQuantifier tests passed")
    print()
    
    # Test ForecastEvaluator
    print("Testing ForecastEvaluator...")
    test_fe = TestForecastEvaluator()
    test_fe.test_initialization()
    test_fe.test_evaluate_accuracy()
    test_fe.test_validate_requirements()
    print("✓ ForecastEvaluator tests passed")
    print()
    
    # Integration test
    print("Running integration test...")
    test_integration()
    print()
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
