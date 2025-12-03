"""
Script to integrate real Alzheimer's datasets and train ML models
Datasets:
1. ALZ_Variant Dataset: Genetic variant data (preprocessed)
2. MRI Dataset: Brain imaging data
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.prediction import Prediction
from app.models.health_metric import HealthMetric
from app.ml.ensemble_predictor import EnsemblePredictor
from sqlalchemy import text

# ML imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import xgboost as xgb

# Paths - handle multi-workspace setup
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
ai4a_dir = backend_dir.parent

# Try to find Datasets folder (it's a sibling workspace in multi-root setup)
possible_paths = [
    ai4a_dir.parent / "Datasets",  # Sibling to AI4A
    ai4a_dir / "Datasets",  # Inside AI4A
    Path.cwd().parent / "Datasets",  # Relative to current directory
    Path("/Users/abbhivadhan/Downloads/Datasets"),  # Absolute path (Downloads)
    Path("/Users/abbhivadhan/Desktop/Datasets"),  # Absolute path (Desktop)
]

DATASETS_PATH = None
for path in possible_paths:
    if path.exists():
        DATASETS_PATH = path
        print(f"Found Datasets at: {path}")
        break

if DATASETS_PATH is None:
    print("Warning: Datasets folder not found. Checked:")
    for path in possible_paths:
        print(f"  - {path}")
    # Try to get from environment or use default
    import os
    datasets_env = os.getenv('DATASETS_PATH')
    if datasets_env:
        DATASETS_PATH = Path(datasets_env)
    else:
        DATASETS_PATH = ai4a_dir.parent / "Datasets"  # Default

MODELS_PATH = backend_dir / "ml_models"
MODELS_PATH.mkdir(exist_ok=True)
print(f"Models will be saved to: {MODELS_PATH}")


class DatasetIntegrator:
    """Integrates real datasets and trains ML models"""
    
    def __init__(self):
        self.genetic_data = None
        self.mri_data = None
        self.models = {}
        self.scalers = {}
        
    def load_genetic_data(self):
        """Load preprocessed genetic variant data"""
        print("Loading genetic variant dataset...")
        genetic_path = DATASETS_PATH / "ALZ_Variant Datset" / "preprocessed_alz_data.npz"
        
        if not genetic_path.exists():
            print(f"Warning: Genetic dataset not found at {genetic_path}")
            return False
            
        data = np.load(genetic_path)
        self.genetic_data = {
            'X_train': data['X_train'],
            'X_test': data['X_test'],
            'y_train': data['y_train'],
            'y_test': data['y_test']
        }
        
        print(f"Genetic data loaded:")
        print(f"  Training samples: {self.genetic_data['X_train'].shape[0]}")
        print(f"  Test samples: {self.genetic_data['X_test'].shape[0]}")
        print(f"  Features: {self.genetic_data['X_train'].shape[1]}")
        print(f"  Output classes: {self.genetic_data['y_train'].shape[1]}")
        
        return True
    
    def load_mri_data(self):
        """Load MRI imaging dataset"""
        print("\nLoading MRI dataset...")
        mri_train_path = DATASETS_PATH / "MRI Dataset" / "train.parquet"
        mri_test_path = DATASETS_PATH / "MRI Dataset" / "test.parquet"
        
        if not mri_train_path.exists():
            print(f"Warning: MRI dataset not found at {mri_train_path}")
            return False
            
        train_df = pd.read_parquet(mri_train_path)
        test_df = pd.read_parquet(mri_test_path) if mri_test_path.exists() else None
        
        self.mri_data = {
            'train': train_df,
            'test': test_df
        }
        
        print(f"MRI data loaded:")
        print(f"  Training samples: {len(train_df)}")
        if test_df is not None:
            print(f"  Test samples: {len(test_df)}")
        print(f"  Label distribution:\n{train_df['label'].value_counts()}")
        
        return True
    
    def train_genetic_models(self):
        """Train models on genetic variant data"""
        if self.genetic_data is None:
            print("No genetic data loaded")
            return
            
        print("\n" + "="*60)
        print("Training models on genetic variant data...")
        print("="*60)
        
        X_train = self.genetic_data['X_train']
        X_test = self.genetic_data['X_test']
        # Use first column of y as primary target (binary classification)
        y_train = self.genetic_data['y_train'][:, 0]
        y_test = self.genetic_data['y_test'][:, 0]
        
        # Clean data: replace inf and nan values, clip extreme values
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
        X_test = np.nan_to_num(X_test, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Clip extreme values to prevent overflow
        X_train = np.clip(X_train, -1e10, 1e10)
        X_test = np.clip(X_test, -1e10, 1e10)
        
        # Scale features with robust scaler to handle outliers
        from sklearn.preprocessing import RobustScaler
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['genetic'] = scaler
        
        # Train multiple models
        models_to_train = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            ),
            'neural_net': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                max_iter=200,
                random_state=42,
                early_stopping=True
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        }
        
        results = {}
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...")
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
            
            accuracy = accuracy_score(y_test, y_pred)
            results[name] = {
                'accuracy': accuracy,
                'model': model
            }
            
            print(f"  Accuracy: {accuracy:.4f}")
            if y_pred_proba is not None:
                try:
                    auc = roc_auc_score(y_test, y_pred_proba)
                    results[name]['auc'] = auc
                    print(f"  AUC-ROC: {auc:.4f}")
                except:
                    pass
            
            # Save model
            model_path = MODELS_PATH / f"genetic_{name}.joblib"
            joblib.dump(model, model_path)
            print(f"  Saved to {model_path}")
        
        # Save scaler
        scaler_path = MODELS_PATH / "genetic_scaler.joblib"
        joblib.dump(scaler, scaler_path)
        
        self.models['genetic'] = results
        
        # Select best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
        print(f"\nBest genetic model: {best_model_name} (Accuracy: {results[best_model_name]['accuracy']:.4f})")
        
        return results
    
    def create_ensemble_predictor(self):
        """Create an ensemble predictor combining multiple models"""
        print("\n" + "="*60)
        print("Creating ensemble predictor...")
        print("="*60)
        
        if not self.models.get('genetic'):
            print("No models trained yet")
            return
        
        ensemble = EnsemblePredictor(self.models['genetic'], self.scalers['genetic'])
        
        # Save ensemble
        ensemble_path = MODELS_PATH / "ensemble_predictor.joblib"
        joblib.dump(ensemble, ensemble_path)
        print(f"Ensemble predictor saved to {ensemble_path}")
        
        return ensemble
    
    def generate_sample_predictions(self, user_id: int = 1, num_samples: int = 10):
        """Generate sample predictions using trained models"""
        print("\n" + "="*60)
        print(f"Generating {num_samples} sample predictions for user {user_id}...")
        print("="*60)
        
        if not self.genetic_data:
            print("No data available for predictions")
            return
        
        # Use test data samples
        X_test = self.genetic_data['X_test']
        indices = np.random.choice(len(X_test), min(num_samples, len(X_test)), replace=False)
        
        ensemble_path = MODELS_PATH / "ensemble_predictor.joblib"
        if not ensemble_path.exists():
            print("Ensemble predictor not found")
            return
        
        ensemble = joblib.load(ensemble_path)
        
        db = SessionLocal()
        try:
            predictions_created = 0
            for idx in indices:
                features = X_test[idx]
                result = ensemble.predict_risk(features)
                
                # Create prediction record
                from app.models.prediction import RiskCategory
                
                risk_category_map = {
                    'low': RiskCategory.LOW,
                    'moderate': RiskCategory.MODERATE,
                    'high': RiskCategory.HIGH
                }
                
                prediction = Prediction(
                    user_id=user_id,
                    risk_score=result['risk_score'],
                    risk_category=risk_category_map.get(result['risk_level'], RiskCategory.MODERATE),
                    confidence_interval_lower=max(0, result['risk_score'] - result['confidence']),
                    confidence_interval_upper=min(1, result['risk_score'] + result['confidence']),
                    feature_importance={},
                    model_version="ensemble_v1",
                    model_type="ensemble",
                    input_features={"genetic_features": features[:10].tolist()},
                    prediction_date=datetime.utcnow()
                )
                db.add(prediction)
                predictions_created += 1
            
            db.commit()
            print(f"Created {predictions_created} predictions in database")
            
        except Exception as e:
            print(f"Error creating predictions: {e}")
            db.rollback()
        finally:
            db.close()
    
    def update_model_registry(self):
        """Update model registry with trained models"""
        print("\n" + "="*60)
        print("Updating model registry...")
        print("="*60)
        
        registry_path = MODELS_PATH / "model_registry.json"
        
        import json
        registry = {
            'last_updated': datetime.now().isoformat(),
            'models': {
                'genetic_ensemble': {
                    'path': str(MODELS_PATH / "ensemble_predictor.joblib"),
                    'type': 'ensemble',
                    'version': 'v1',
                    'accuracy': max(m['accuracy'] for m in self.models.get('genetic', {}).values()) if self.models.get('genetic') else 0,
                    'features': 130,
                    'description': 'Ensemble model trained on genetic variant data'
                }
            },
            'scalers': {
                'genetic': str(MODELS_PATH / "genetic_scaler.joblib")
            }
        }
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"Model registry updated at {registry_path}")


def main():
    """Main integration workflow"""
    print("="*60)
    print("ALZHEIMER'S DATASET INTEGRATION")
    print("="*60)
    
    integrator = DatasetIntegrator()
    
    # Load datasets
    genetic_loaded = integrator.load_genetic_data()
    mri_loaded = integrator.load_mri_data()
    
    if not genetic_loaded and not mri_loaded:
        print("\nError: No datasets could be loaded")
        return
    
    # Train models on genetic data
    if genetic_loaded:
        integrator.train_genetic_models()
        integrator.create_ensemble_predictor()
        integrator.update_model_registry()
        
        # Generate sample predictions
        print("\nDo you want to generate sample predictions? (y/n)")
        # For automated run, default to yes
        integrator.generate_sample_predictions(user_id=1, num_samples=10)
    
    print("\n" + "="*60)
    print("INTEGRATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Models are saved in:", MODELS_PATH)
    print("2. Update backend ML service to use these models")
    print("3. Test predictions via API endpoints")
    print("4. Frontend will automatically display real predictions")


if __name__ == "__main__":
    main()
