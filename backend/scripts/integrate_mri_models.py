"""
Script to train and integrate MRI imaging models
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from datetime import datetime
from PIL import Image
import io

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal

# ML imports
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.decomposition import PCA

# Paths
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
ai4a_dir = backend_dir.parent

# Find Datasets folder
possible_paths = [
    Path("/Users/abbhivadhan/Downloads/Datasets"),
    ai4a_dir.parent / "Datasets",
]

DATASETS_PATH = None
for path in possible_paths:
    if path.exists():
        DATASETS_PATH = path
        break

MODELS_PATH = backend_dir / "ml_models"
MODELS_PATH.mkdir(exist_ok=True)


class MRIModelTrainer:
    """Train models on MRI imaging data"""
    
    def __init__(self):
        self.train_df = None
        self.test_df = None
        self.models = {}
        self.scaler = None
        self.pca = None
        
    def load_mri_data(self):
        """Load MRI dataset"""
        print("Loading MRI dataset...")
        train_path = DATASETS_PATH / "MRI Dataset" / "train.parquet"
        test_path = DATASETS_PATH / "MRI Dataset" / "test.parquet"
        
        if not train_path.exists():
            print(f"Error: MRI dataset not found at {train_path}")
            return False
        
        self.train_df = pd.read_parquet(train_path)
        if test_path.exists():
            self.test_df = pd.read_parquet(test_path)
        else:
            # Split train data
            from sklearn.model_selection import train_test_split
            self.train_df, self.test_df = train_test_split(
                self.train_df, test_size=0.2, random_state=42
            )
        
        print(f"Training samples: {len(self.train_df)}")
        print(f"Test samples: {len(self.test_df)}")
        print(f"Label distribution:\n{self.train_df['label'].value_counts()}")
        
        return True
    
    def extract_image_features(self, image_data, target_size=(64, 64)):
        """Extract features from image bytes"""
        try:
            # Load image from bytes
            img = Image.open(io.BytesIO(image_data['bytes']))
            
            # Convert to grayscale and resize
            img = img.convert('L').resize(target_size)
            
            # Convert to array and flatten
            features = np.array(img).flatten()
            
            return features
        except Exception as e:
            print(f"Error extracting features: {e}")
            return np.zeros(target_size[0] * target_size[1])
    
    def prepare_features(self, df, max_samples=1000):
        """Prepare features from MRI images"""
        print(f"\nExtracting features from {min(len(df), max_samples)} images...")
        
        features_list = []
        labels_list = []
        
        # Limit samples for faster training
        sample_df = df.sample(n=min(len(df), max_samples), random_state=42)
        
        for idx, row in sample_df.iterrows():
            features = self.extract_image_features(row['image'])
            features_list.append(features)
            labels_list.append(row['label'])
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1} images...")
        
        X = np.array(features_list)
        y = np.array(labels_list)
        
        print(f"Feature matrix shape: {X.shape}")
        return X, y
    
    def train_models(self):
        """Train MRI classification models"""
        print("\n" + "="*60)
        print("Training MRI Classification Models")
        print("="*60)
        
        # Prepare features
        X_train, y_train = self.prepare_features(self.train_df, max_samples=1000)
        X_test, y_test = self.prepare_features(self.test_df, max_samples=200)
        
        # Scale features
        print("\nScaling features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Apply PCA for dimensionality reduction
        print("Applying PCA...")
        self.pca = PCA(n_components=50, random_state=42)
        X_train_pca = self.pca.fit_transform(X_train_scaled)
        X_test_pca = self.pca.transform(X_test_scaled)
        
        print(f"Reduced to {X_train_pca.shape[1]} components")
        
        # Train Random Forest
        print("\nTraining Random Forest classifier...")
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_pca, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test_pca)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nModel Performance:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.models['random_forest'] = {
            'model': rf_model,
            'accuracy': accuracy
        }
        
        # Save models
        print("\nSaving models...")
        joblib.dump(rf_model, MODELS_PATH / "mri_random_forest.joblib")
        joblib.dump(self.scaler, MODELS_PATH / "mri_scaler.joblib")
        joblib.dump(self.pca, MODELS_PATH / "mri_pca.joblib")
        
        print("Models saved successfully!")
        
        return True
    
    def update_registry(self):
        """Update model registry"""
        import json
        
        registry_path = MODELS_PATH / "model_registry.json"
        
        # Load existing registry
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {'models': {}, 'scalers': {}}
        
        # Add MRI models
        registry['models']['mri_classifier'] = {
            'path': str(MODELS_PATH / "mri_random_forest.joblib"),
            'type': 'random_forest',
            'version': 'v1',
            'accuracy': self.models['random_forest']['accuracy'],
            'description': 'MRI brain scan classifier'
        }
        
        registry['scalers']['mri'] = str(MODELS_PATH / "mri_scaler.joblib")
        registry['scalers']['mri_pca'] = str(MODELS_PATH / "mri_pca.joblib")
        registry['last_updated'] = datetime.now().isoformat()
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"\nModel registry updated at {registry_path}")


def main():
    """Main training workflow"""
    print("="*60)
    print("MRI MODEL TRAINING")
    print("="*60)
    
    if not DATASETS_PATH or not DATASETS_PATH.exists():
        print("\nError: Datasets folder not found")
        return
    
    trainer = MRIModelTrainer()
    
    # Load data
    if not trainer.load_mri_data():
        return
    
    # Train models
    trainer.train_models()
    
    # Update registry
    trainer.update_registry()
    
    print("\n" + "="*60)
    print("MRI MODEL TRAINING COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update imaging_service.py to use trained models")
    print("2. Test MRI predictions via imaging API")
    print("3. Frontend will display real MRI analysis")


if __name__ == "__main__":
    main()
