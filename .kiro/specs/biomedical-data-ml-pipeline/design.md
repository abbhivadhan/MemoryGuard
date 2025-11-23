# Biomedical Data ML Pipeline Design Document

## Overview

The Biomedical Data ML Pipeline is a production-grade system for acquiring, processing, and utilizing real de-identified biomedical datasets to train and deploy machine learning models for Alzheimer's Disease detection and progression forecasting. The system integrates multiple public datasets (ADNI, OASIS, NACC), implements comprehensive data quality controls, and provides automated ML training with interpretability.

### Core Components

1. **Data Acquisition Layer**: Interfaces with public biomedical datasets
2. **Data Validation & Quality Engine**: Ensures data integrity and HIPAA compliance
3. **Feature Engineering Pipeline**: Transforms raw data into ML-ready features
4. **ML Training System**: Trains, validates, and versions models
5. **Model Registry**: Centralized model storage with versioning
6. **Monitoring & Drift Detection**: Tracks data and model performance
7. **Inference Service**: Serves predictions with interpretability

### Technology Stack

**Data Processing:**
- Python 3.11+
- Pandas for data manipulation
- NumPy for numerical operations
- PyDICOM and NiBabel for medical imaging
- Scikit-learn for preprocessing

**Machine Learning:**
- Scikit-learn for Random Forest
- XGBoost for gradient boosting
- TensorFlow/Keras for neural networks
- SHAP for model interpretability
- Optuna for hyperparameter tuning
- MLflow for experiment tracking

**Data Storage:**
- PostgreSQL for metadata and structured data
- MinIO or S3 for object storage (DICOM files, models)
- Parquet files for processed features
- Redis for caching

**Orchestration:**
- Apache Airflow for pipeline scheduling
- Celery for async task processing
- Docker for containerization

**Monitoring:**
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for logging


## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Sources (External)                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │   ADNI   │    │  OASIS   │    │   NACC   │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Data Acquisition Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Loaders (CSV, JSON, DICOM)                         │  │
│  │  De-identification Validator                             │  │
│  │  Schema Validator                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Data Validation & Quality Engine                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PHI Detection                                           │  │
│  │  Completeness Checker                                    │  │
│  │  Outlier Detection                                       │  │
│  │  Duplicate Detection                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Feature Engineering Pipeline                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Cognitive Score Extraction                              │  │
│  │  Biomarker Processing                                    │  │
│  │  Imaging Feature Extraction                              │  │
│  │  Genetic Feature Encoding                                │  │
│  │  Missing Data Imputation                                 │  │
│  │  Feature Normalization                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Feature Store (Parquet)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Partitioned by Date & Cohort                            │  │
│  │  Indexed for Fast Retrieval                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML Training System                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Random Forest Trainer                                   │  │
│  │  XGBoost Trainer                                         │  │
│  │  Neural Network Trainer                                  │  │
│  │  Ensemble Combiner                                       │  │
│  │  SHAP Explainer                                          │  │
│  │  Hyperparameter Tuner                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Model Registry                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Artifacts (Pickle, ONNX)                          │  │
│  │  Model Metadata & Metrics                                │  │
│  │  Version Control                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Inference Service (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Model Loading & Caching                                 │  │
│  │  Prediction Endpoint                                     │  │
│  │  SHAP Explanation Endpoint                               │  │
│  │  Progression Forecast Endpoint                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Monitoring & Drift Detection                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Drift Monitor                                      │  │
│  │  Model Performance Tracker                               │  │
│  │  Retraining Trigger                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Data Acquisition Layer

**Purpose:** Download and ingest data from public biomedical datasets

**Supported Datasets:**

**ADNI (Alzheimer's Disease Neuroimaging Initiative):**
- Cognitive assessments (MMSE, ADAS-Cog, CDR)
- CSF biomarkers (Aβ42, t-Tau, p-Tau)
- MRI scans (T1-weighted, volumetric)
- PET imaging (FDG-PET, Amyloid-PET)
- APOE genotype
- Demographics and medical history

**OASIS (Open Access Series of Imaging Studies):**
- MRI scans with volumetric data
- CDR scores
- Demographics
- Longitudinal data (OASIS-3)

**NACC (National Alzheimer's Coordinating Center):**
- Clinical assessments
- Neuropathology data
- Cognitive test batteries
- Medical history

**Implementation:**

```python
class DataAcquisitionService:
    """Service for downloading and ingesting biomedical datasets"""
    
    def download_adni_data(self, data_type: str, date_range: tuple) -> Path:
        """Download ADNI data for specified type and date range"""
        pass
    
    def download_oasis_data(self, version: str) -> Path:
        """Download OASIS dataset version"""
        pass
    
    def download_nacc_data(self, modules: List[str]) -> Path:
        """Download NACC data modules"""
        pass
    
    def validate_schema(self, data: pd.DataFrame, dataset: str) -> bool:
        """Validate data schema matches expected format"""
        pass
```

### 2. Data Validation & Quality Engine

**Purpose:** Ensure data quality, completeness, and HIPAA compliance

**PHI Detection:**
- Scan for 18 HIPAA identifiers (names, dates, SSN, etc.)
- Use regex patterns and NLP for detection
- Quarantine any data with PHI

**Quality Checks:**
- Completeness: % of non-null values per column
- Range validation: Biomarkers and scores within valid ranges
- Outlier detection: Statistical methods (IQR, Z-score)
- Duplicate detection: Check for duplicate patient records
- Temporal consistency: Validate date sequences in longitudinal data

**Implementation:**

```python
class DataValidationEngine:
    """Engine for comprehensive data quality validation"""
    
    def detect_phi(self, data: pd.DataFrame) -> List[str]:
        """Detect potential PHI in dataset"""
        phi_patterns = {
            'ssn': r'\d{3}-\d{2}-\d{4}',
            'phone': r'\d{3}-\d{3}-\d{4}',
            'email': r'[\w\.-]+@[\w\.-]+',
            # ... more patterns
        }
        return detected_columns
    
    def check_completeness(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate completeness percentage for each column"""
        return {col: data[col].notna().mean() for col in data.columns}
    
    def detect_outliers(self, data: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Detect outliers using specified method"""
        pass
    
    def validate_ranges(self, data: pd.DataFrame) -> Dict[str, List[int]]:
        """Validate that values are within expected ranges"""
        ranges = {
            'MMSE': (0, 30),
            'MoCA': (0, 30),
            'CDR': (0, 3),
            'CSF_AB42': (0, 2000),  # pg/mL
            # ... more ranges
        }
        return violations
```

### 3. Feature Engineering Pipeline

**Purpose:** Transform raw biomedical data into ML-ready features

**Feature Categories:**

**Cognitive Features:**
- MMSE score (0-30)
- MoCA score (0-30)
- CDR global score (0-3)
- ADAS-Cog score
- Individual test component scores

**Biomarker Features:**
- CSF Aβ42 level
- CSF Total Tau level
- CSF Phosphorylated Tau level
- Aβ42/Tau ratio
- p-Tau/Tau ratio

**Imaging Features:**
- Hippocampal volume (left, right, total)
- Entorhinal cortex thickness
- Ventricular volume
- Whole brain volume
- Cortical thickness (multiple regions)
- White matter hyperintensity volume
- Normalized by intracranial volume

**Genetic Features:**
- APOE genotype (one-hot encoded)
- APOE e4 allele count (0, 1, 2)
- APOE risk category

**Demographic Features:**
- Age
- Sex (binary)
- Education years
- Race/ethnicity (one-hot encoded)

**Lifestyle Features:**
- BMI
- Smoking status
- Alcohol consumption
- Physical activity level
- Social engagement score

**Temporal Features:**
- Time since baseline
- Rate of cognitive decline
- Biomarker change rate

**Implementation:**

```python
class FeatureEngineeringPipeline:
    """Pipeline for transforming raw data into ML features"""
    
    def extract_cognitive_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract and normalize cognitive assessment scores"""
        features = pd.DataFrame()
        features['mmse_score'] = data['MMSE']
        features['moca_score'] = data['MoCA']
        features['cdr_global'] = data['CDR_GLOBAL']
        return features
    
    def extract_biomarker_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract and process CSF biomarker values"""
        features = pd.DataFrame()
        features['csf_ab42'] = data['CSF_AB42']
        features['csf_tau'] = data['CSF_TAU']
        features['csf_ptau'] = data['CSF_PTAU']
        features['ab42_tau_ratio'] = data['CSF_AB42'] / data['CSF_TAU']
        features['ptau_tau_ratio'] = data['CSF_PTAU'] / data['CSF_TAU']
        return features
    
    def extract_imaging_features(self, dicom_path: Path) -> Dict[str, float]:
        """Extract volumetric features from MRI DICOM"""
        # Use FreeSurfer or similar for segmentation
        volumes = {
            'hippocampus_left': 0.0,
            'hippocampus_right': 0.0,
            'entorhinal_cortex': 0.0,
            'ventricles': 0.0,
            # ... more regions
        }
        return volumes
    
    def encode_genetic_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode APOE genotype as features"""
        features = pd.DataFrame()
        # One-hot encode genotype
        features = pd.get_dummies(data['APOE_GENOTYPE'], prefix='apoe')
        # Count e4 alleles
        features['apoe_e4_count'] = data['APOE_GENOTYPE'].apply(
            lambda x: x.count('e4')
        )
        return features
    
    def impute_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values using multiple imputation"""
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer
        
        imputer = IterativeImputer(random_state=42)
        return pd.DataFrame(
            imputer.fit_transform(data),
            columns=data.columns
        )
    
    def normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normalize continuous features using standardization"""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        return pd.DataFrame(
            scaler.fit_transform(data),
            columns=data.columns
        )
```


### 4. ML Training System

**Purpose:** Train, validate, and optimize machine learning models

**Model Architecture:**

**Random Forest Classifier:**
```python
from sklearn.ensemble import RandomForestClassifier

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)
```

**XGBoost Classifier:**
```python
import xgboost as xgb

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=1.5,  # Handle class imbalance
    random_state=42
)
```

**Deep Neural Network:**
```python
from tensorflow import keras

def create_neural_network(input_dim: int) -> keras.Model:
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_dim=input_dim),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )
    
    return model
```

**Ensemble Predictor:**
```python
class EnsemblePredictor:
    """Ensemble model combining RF, XGBoost, and Neural Network"""
    
    def __init__(self, models: List, weights: List[float] = None):
        self.models = models
        self.weights = weights or [1/len(models)] * len(models)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Generate ensemble predictions using weighted averaging"""
        predictions = np.array([
            model.predict_proba(X)[:, 1] for model in self.models
        ])
        return np.average(predictions, axis=0, weights=self.weights)
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Generate binary predictions"""
        return (self.predict_proba(X) >= threshold).astype(int)
```

**Training Pipeline:**

```python
class MLTrainingPipeline:
    """Complete ML training pipeline"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.mlflow_client = mlflow.tracking.MlflowClient()
    
    def load_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Load processed features from feature store"""
        features = pd.read_parquet('feature_store/train_features.parquet')
        labels = features.pop('diagnosis')  # 0: Normal, 1: AD
        return features, labels
    
    def split_data(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """Stratified train-validation-test split"""
        from sklearn.model_selection import train_test_split
        
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=0.15, stratify=y, random_state=42
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=0.18, stratify=y_temp, random_state=42
        )
        
        return {
            'X_train': X_train, 'y_train': y_train,
            'X_val': X_val, 'y_val': y_val,
            'X_test': X_test, 'y_test': y_test
        }
    
    def handle_class_imbalance(self, X: pd.DataFrame, y: pd.Series) -> Tuple:
        """Apply SMOTE if class imbalance detected"""
        from imblearn.over_sampling import SMOTE
        
        class_ratio = y.value_counts()[0] / y.value_counts()[1]
        
        if class_ratio > 3:
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)
            return X_resampled, y_resampled
        
        return X, y
    
    def train_random_forest(self, X_train, y_train, X_val, y_val) -> Dict:
        """Train Random Forest with cross-validation"""
        with mlflow.start_run(run_name="random_forest"):
            model = RandomForestClassifier(**self.config['rf_params'])
            model.fit(X_train, y_train)
            
            # Evaluate
            metrics = self.evaluate_model(model, X_val, y_val)
            
            # Log to MLflow
            mlflow.log_params(self.config['rf_params'])
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, "model")
            
            return {'model': model, 'metrics': metrics}
    
    def train_xgboost(self, X_train, y_train, X_val, y_val) -> Dict:
        """Train XGBoost with early stopping"""
        with mlflow.start_run(run_name="xgboost"):
            model = xgb.XGBClassifier(**self.config['xgb_params'])
            
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=20,
                verbose=False
            )
            
            metrics = self.evaluate_model(model, X_val, y_val)
            
            mlflow.log_params(self.config['xgb_params'])
            mlflow.log_metrics(metrics)
            mlflow.xgboost.log_model(model, "model")
            
            return {'model': model, 'metrics': metrics}
    
    def train_neural_network(self, X_train, y_train, X_val, y_val) -> Dict:
        """Train deep neural network"""
        with mlflow.start_run(run_name="neural_network"):
            model = create_neural_network(X_train.shape[1])
            
            early_stop = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            )
            
            history = model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=100,
                batch_size=32,
                callbacks=[early_stop],
                verbose=0
            )
            
            metrics = self.evaluate_model(model, X_val, y_val)
            
            mlflow.log_params(self.config['nn_params'])
            mlflow.log_metrics(metrics)
            mlflow.keras.log_model(model, "model")
            
            return {'model': model, 'metrics': metrics}
    
    def evaluate_model(self, model, X_val, y_val) -> Dict[str, float]:
        """Comprehensive model evaluation"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, average_precision_score, confusion_matrix,
            balanced_accuracy_score
        )
        
        y_pred = model.predict(X_val)
        y_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'balanced_accuracy': balanced_accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred),
            'recall': recall_score(y_val, y_pred),
            'f1_score': f1_score(y_val, y_pred),
            'roc_auc': roc_auc_score(y_val, y_proba),
            'pr_auc': average_precision_score(y_val, y_proba)
        }
        
        return metrics
    
    def optimize_hyperparameters(self, model_type: str, X_train, y_train) -> Dict:
        """Hyperparameter optimization using Optuna"""
        import optuna
        
        def objective(trial):
            if model_type == 'random_forest':
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 100, 300),
                    'max_depth': trial.suggest_int('max_depth', 10, 30),
                    'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                }
                model = RandomForestClassifier(**params, random_state=42)
            
            # Cross-validation score
            from sklearn.model_selection import cross_val_score
            scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=50)
        
        return study.best_params
```

### 5. Model Interpretability

**SHAP (SHapley Additive exPlanations):**

```python
import shap

class ModelInterpreter:
    """Generate interpretable explanations for model predictions"""
    
    def __init__(self, model, X_train: pd.DataFrame):
        self.model = model
        self.explainer = shap.TreeExplainer(model)  # For tree-based models
        self.X_train = X_train
    
    def explain_prediction(self, X: pd.DataFrame) -> Dict:
        """Generate SHAP explanation for a single prediction"""
        shap_values = self.explainer.shap_values(X)
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'shap_value': shap_values[0],
            'feature_value': X.iloc[0].values
        }).sort_values('shap_value', key=abs, ascending=False)
        
        return {
            'shap_values': shap_values,
            'feature_importance': feature_importance.head(10).to_dict('records'),
            'base_value': self.explainer.expected_value
        }
    
    def generate_global_importance(self) -> pd.DataFrame:
        """Generate global feature importance across all training data"""
        shap_values = self.explainer.shap_values(self.X_train)
        
        importance = pd.DataFrame({
            'feature': self.X_train.columns,
            'importance': np.abs(shap_values).mean(axis=0)
        }).sort_values('importance', ascending=False)
        
        return importance
    
    def generate_summary_plot(self, X: pd.DataFrame, output_path: Path):
        """Generate SHAP summary plot"""
        shap_values = self.explainer.shap_values(X)
        shap.summary_plot(shap_values, X, show=False)
        plt.savefig(output_path)
        plt.close()
```

### 6. Progression Forecasting

**Time-Series Model for Progression:**

```python
from tensorflow.keras.layers import LSTM, Dense, Dropout

class ProgressionForecaster:
    """Forecast disease progression using longitudinal data"""
    
    def __init__(self):
        self.model = None
    
    def build_lstm_model(self, sequence_length: int, n_features: int):
        """Build LSTM model for time-series forecasting"""
        model = keras.Sequential([
            LSTM(64, return_sequences=True, input_shape=(sequence_length, n_features)),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(3)  # Predict 6, 12, 24 month MMSE scores
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def prepare_sequences(self, data: pd.DataFrame, sequence_length: int = 4):
        """Prepare time-series sequences from longitudinal data"""
        sequences = []
        targets = []
        
        for patient_id in data['patient_id'].unique():
            patient_data = data[data['patient_id'] == patient_id].sort_values('visit_date')
            
            if len(patient_data) >= sequence_length + 1:
                for i in range(len(patient_data) - sequence_length):
                    seq = patient_data.iloc[i:i+sequence_length][self.feature_cols].values
                    target = patient_data.iloc[i+sequence_length]['mmse_score']
                    sequences.append(seq)
                    targets.append(target)
        
        return np.array(sequences), np.array(targets)
    
    def forecast(self, patient_history: pd.DataFrame) -> Dict[str, float]:
        """Generate 6, 12, 24 month forecasts"""
        sequence = patient_history[self.feature_cols].values[-4:]  # Last 4 visits
        sequence = sequence.reshape(1, 4, -1)
        
        predictions = self.model.predict(sequence)[0]
        
        return {
            '6_month_mmse': predictions[0],
            '12_month_mmse': predictions[1],
            '24_month_mmse': predictions[2]
        }
```


### 7. Model Registry

**Purpose:** Version control and management for trained models

```python
class ModelRegistry:
    """Centralized registry for model versioning and deployment"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.metadata_db = self._init_metadata_db()
    
    def register_model(
        self,
        model,
        model_name: str,
        metrics: Dict[str, float],
        dataset_version: str,
        hyperparameters: Dict
    ) -> str:
        """Register a new model version"""
        version_id = self._generate_version_id()
        
        # Save model artifact
        model_path = self.storage_path / model_name / version_id
        model_path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(model, model_path / 'model.pkl')
        
        # Save metadata
        metadata = {
            'version_id': version_id,
            'model_name': model_name,
            'created_at': datetime.now().isoformat(),
            'metrics': metrics,
            'dataset_version': dataset_version,
            'hyperparameters': hyperparameters,
            'status': 'registered'
        }
        
        self._save_metadata(metadata)
        
        return version_id
    
    def promote_to_production(self, model_name: str, version_id: str):
        """Promote a model version to production"""
        # Update metadata
        self._update_status(model_name, version_id, 'production')
        
        # Demote current production model
        current_prod = self.get_production_model(model_name)
        if current_prod:
            self._update_status(model_name, current_prod['version_id'], 'archived')
    
    def get_production_model(self, model_name: str) -> Dict:
        """Get currently deployed production model"""
        query = """
            SELECT * FROM models 
            WHERE model_name = ? AND status = 'production'
        """
        return self.metadata_db.execute(query, (model_name,)).fetchone()
    
    def load_model(self, model_name: str, version_id: str = None):
        """Load a specific model version"""
        if version_id is None:
            # Load production model
            metadata = self.get_production_model(model_name)
            version_id = metadata['version_id']
        
        model_path = self.storage_path / model_name / version_id / 'model.pkl'
        return joblib.load(model_path)
    
    def compare_versions(self, model_name: str, version_ids: List[str]) -> pd.DataFrame:
        """Compare metrics across model versions"""
        query = """
            SELECT version_id, metrics, created_at 
            FROM models 
            WHERE model_name = ? AND version_id IN ({})
        """.format(','.join('?' * len(version_ids)))
        
        results = self.metadata_db.execute(
            query, [model_name] + version_ids
        ).fetchall()
        
        return pd.DataFrame(results)
```

### 8. Data Drift Detection

**Purpose:** Monitor data distribution changes and trigger retraining

```python
from scipy import stats

class DataDriftMonitor:
    """Monitor for data drift and model performance degradation"""
    
    def __init__(self, reference_data: pd.DataFrame):
        self.reference_data = reference_data
        self.reference_distributions = self._compute_distributions(reference_data)
    
    def _compute_distributions(self, data: pd.DataFrame) -> Dict:
        """Compute distribution statistics for each feature"""
        distributions = {}
        for col in data.columns:
            distributions[col] = {
                'mean': data[col].mean(),
                'std': data[col].std(),
                'quantiles': data[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        return distributions
    
    def detect_drift(self, new_data: pd.DataFrame, threshold: float = 0.05) -> Dict:
        """Detect drift using Kolmogorov-Smirnov test"""
        drift_results = {}
        
        for col in new_data.columns:
            if col in self.reference_data.columns:
                # KS test
                statistic, p_value = stats.ks_2samp(
                    self.reference_data[col],
                    new_data[col]
                )
                
                drift_results[col] = {
                    'ks_statistic': statistic,
                    'p_value': p_value,
                    'drift_detected': p_value < threshold
                }
        
        return drift_results
    
    def calculate_psi(self, new_data: pd.DataFrame, n_bins: int = 10) -> Dict[str, float]:
        """Calculate Population Stability Index for each feature"""
        psi_scores = {}
        
        for col in new_data.columns:
            if col not in self.reference_data.columns:
                continue
            
            # Bin the data
            bins = np.histogram_bin_edges(self.reference_data[col], bins=n_bins)
            
            ref_counts, _ = np.histogram(self.reference_data[col], bins=bins)
            new_counts, _ = np.histogram(new_data[col], bins=bins)
            
            # Calculate proportions
            ref_props = ref_counts / len(self.reference_data)
            new_props = new_counts / len(new_data)
            
            # Avoid division by zero
            ref_props = np.where(ref_props == 0, 0.0001, ref_props)
            new_props = np.where(new_props == 0, 0.0001, new_props)
            
            # Calculate PSI
            psi = np.sum((new_props - ref_props) * np.log(new_props / ref_props))
            psi_scores[col] = psi
        
        return psi_scores
    
    def should_retrain(self, drift_results: Dict, psi_scores: Dict) -> bool:
        """Determine if model retraining is needed"""
        # Check if any feature has significant drift
        significant_drift = any(
            result['drift_detected'] for result in drift_results.values()
        )
        
        # Check if any PSI score exceeds threshold
        high_psi = any(psi > 0.2 for psi in psi_scores.values())
        
        return significant_drift or high_psi
```

### 9. Automated Retraining Pipeline

**Purpose:** Automatically retrain models when drift is detected

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

class AutomatedRetrainingPipeline:
    """Orchestrate automated model retraining"""
    
    def create_retraining_dag(self) -> DAG:
        """Create Airflow DAG for automated retraining"""
        
        default_args = {
            'owner': 'ml-team',
            'depends_on_past': False,
            'start_date': datetime(2025, 1, 1),
            'email_on_failure': True,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        }
        
        dag = DAG(
            'model_retraining',
            default_args=default_args,
            description='Automated ML model retraining pipeline',
            schedule_interval='@monthly',  # Run monthly
            catchup=False
        )
        
        # Task 1: Check for data drift
        check_drift = PythonOperator(
            task_id='check_data_drift',
            python_callable=self.check_drift_task,
            dag=dag
        )
        
        # Task 2: Load new data
        load_data = PythonOperator(
            task_id='load_new_data',
            python_callable=self.load_data_task,
            dag=dag
        )
        
        # Task 3: Retrain models
        retrain = PythonOperator(
            task_id='retrain_models',
            python_callable=self.retrain_task,
            dag=dag
        )
        
        # Task 4: Evaluate new models
        evaluate = PythonOperator(
            task_id='evaluate_models',
            python_callable=self.evaluate_task,
            dag=dag
        )
        
        # Task 5: Deploy if better
        deploy = PythonOperator(
            task_id='deploy_if_better',
            python_callable=self.deploy_task,
            dag=dag
        )
        
        # Define task dependencies
        check_drift >> load_data >> retrain >> evaluate >> deploy
        
        return dag
    
    def check_drift_task(self, **context):
        """Check for data drift"""
        monitor = DataDriftMonitor(reference_data)
        new_data = load_recent_data()
        
        drift_results = monitor.detect_drift(new_data)
        psi_scores = monitor.calculate_psi(new_data)
        
        should_retrain = monitor.should_retrain(drift_results, psi_scores)
        
        # Push to XCom for next task
        context['task_instance'].xcom_push(key='should_retrain', value=should_retrain)
        
        return should_retrain
    
    def retrain_task(self, **context):
        """Retrain all models"""
        should_retrain = context['task_instance'].xcom_pull(
            task_ids='check_data_drift',
            key='should_retrain'
        )
        
        if not should_retrain:
            return "Skipping retraining - no drift detected"
        
        pipeline = MLTrainingPipeline(config)
        X, y = pipeline.load_training_data()
        data_splits = pipeline.split_data(X, y)
        
        # Train all models
        rf_result = pipeline.train_random_forest(**data_splits)
        xgb_result = pipeline.train_xgboost(**data_splits)
        nn_result = pipeline.train_neural_network(**data_splits)
        
        # Store results
        context['task_instance'].xcom_push(key='new_models', value={
            'rf': rf_result,
            'xgb': xgb_result,
            'nn': nn_result
        })
        
        return "Retraining complete"
    
    def deploy_task(self, **context):
        """Deploy new models if they perform better"""
        new_models = context['task_instance'].xcom_pull(
            task_ids='retrain_models',
            key='new_models'
        )
        
        registry = ModelRegistry(storage_path)
        
        for model_name, result in new_models.items():
            current_prod = registry.get_production_model(model_name)
            
            # Compare performance
            if result['metrics']['roc_auc'] > current_prod['metrics']['roc_auc'] * 1.05:
                # New model is 5% better, promote it
                version_id = registry.register_model(
                    result['model'],
                    model_name,
                    result['metrics'],
                    dataset_version='latest',
                    hyperparameters={}
                )
                registry.promote_to_production(model_name, version_id)
                
                # Send notification
                send_notification(f"New {model_name} model deployed: {version_id}")
```

## Data Models

### Feature Store Schema

```sql
CREATE TABLE processed_features (
    patient_id VARCHAR(50) PRIMARY KEY,
    visit_date DATE,
    
    -- Cognitive features
    mmse_score FLOAT,
    moca_score FLOAT,
    cdr_global FLOAT,
    
    -- Biomarker features
    csf_ab42 FLOAT,
    csf_tau FLOAT,
    csf_ptau FLOAT,
    ab42_tau_ratio FLOAT,
    
    -- Imaging features
    hippocampus_volume FLOAT,
    entorhinal_cortex_thickness FLOAT,
    ventricular_volume FLOAT,
    
    -- Genetic features
    apoe_e4_count INT,
    
    -- Demographics
    age INT,
    sex VARCHAR(1),
    education_years INT,
    
    -- Target
    diagnosis INT,  -- 0: Normal, 1: MCI, 2: AD
    
    -- Metadata
    data_source VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_patient_date ON processed_features(patient_id, visit_date);
CREATE INDEX idx_diagnosis ON processed_features(diagnosis);
```

### Model Registry Schema

```sql
CREATE TABLE models (
    version_id VARCHAR(50) PRIMARY KEY,
    model_name VARCHAR(100),
    model_type VARCHAR(50),
    created_at TIMESTAMP,
    
    -- Performance metrics
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    
    -- Training info
    dataset_version VARCHAR(50),
    n_training_samples INT,
    hyperparameters JSON,
    
    -- Deployment
    status VARCHAR(20),  -- registered, production, archived
    deployed_at TIMESTAMP,
    
    -- Storage
    artifact_path VARCHAR(255)
);

CREATE INDEX idx_model_status ON models(model_name, status);
```

## API Endpoints

### Data Ingestion
- `POST /api/v1/data/ingest` - Ingest new dataset
- `GET /api/v1/data/sources` - List available data sources
- `GET /api/v1/data/quality/:dataset_id` - Get quality report

### Feature Engineering
- `POST /api/v1/features/extract` - Extract features from raw data
- `GET /api/v1/features/:patient_id` - Get patient features
- `GET /api/v1/features/statistics` - Get feature statistics

### Model Training
- `POST /api/v1/training/start` - Start training job
- `GET /api/v1/training/status/:job_id` - Get training status
- `GET /api/v1/training/results/:job_id` - Get training results

### Model Registry
- `GET /api/v1/models` - List all models
- `GET /api/v1/models/:model_name/versions` - List model versions
- `POST /api/v1/models/:model_name/promote/:version_id` - Promote to production
- `GET /api/v1/models/:model_name/production` - Get production model

### Monitoring
- `GET /api/v1/monitoring/drift` - Get drift detection results
- `GET /api/v1/monitoring/performance` - Get model performance metrics
- `POST /api/v1/monitoring/trigger-retrain` - Manually trigger retraining

## Testing Strategy

### Data Quality Tests
- Validate PHI removal
- Check data completeness
- Verify feature ranges
- Test duplicate detection

### Model Tests
- Unit tests for preprocessing functions
- Integration tests for training pipeline
- Validate model predictions on test set
- Test SHAP explanation generation

### Performance Tests
- Benchmark feature extraction speed
- Test training time on large datasets
- Measure inference latency

## Deployment

### Docker Containers
- `data-pipeline`: Data ingestion and processing
- `ml-training`: Model training service
- `model-registry`: Model storage and versioning
- `inference-api`: Prediction service
- `monitoring`: Drift detection and monitoring

### Environment Variables
```bash
# Data sources
ADNI_API_KEY=xxx
OASIS_DATA_PATH=/data/oasis
NACC_DATA_PATH=/data/nacc

# Storage
FEATURE_STORE_PATH=/data/features
MODEL_REGISTRY_PATH=/models
S3_BUCKET=alzheimer-ml-models

# ML Configuration
MLFLOW_TRACKING_URI=http://mlflow:5000
TRAINING_BATCH_SIZE=32
RETRAINING_SCHEDULE=monthly

# Monitoring
DRIFT_THRESHOLD=0.2
PERFORMANCE_ALERT_EMAIL=ml-team@example.com
```

## Performance Optimization

- Use Parquet for efficient columnar storage
- Implement feature caching in Redis
- Parallelize feature extraction across patients
- Use GPU for neural network training
- Batch predictions for efficiency
- Implement model quantization for faster inference

## Security & Compliance

- All data encrypted at rest (AES-256)
- TLS 1.3 for data in transit
- PHI detection and removal
- Audit logging for all operations
- Role-based access control
- HIPAA compliance measures
- Regular security audits

This design provides a comprehensive, production-ready architecture for integrating real biomedical data and training ML models for Alzheimer's detection and progression forecasting.
