"""
Example usage of the Feature Store
Demonstrates writing, reading, and querying features
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from ml_pipeline.data_storage.feature_store import FeatureStore
from ml_pipeline.config.logging_config import main_logger


def generate_sample_features(n_patients: int = 100, n_visits_per_patient: int = 3) -> pd.DataFrame:
    """
    Generate sample feature data for testing
    
    Args:
        n_patients: Number of patients
        n_visits_per_patient: Number of visits per patient
        
    Returns:
        DataFrame with sample features
    """
    data = []
    
    for i in range(n_patients):
        patient_id = f"PATIENT_{i:04d}"
        base_date = datetime.now() - timedelta(days=365 * 2)
        
        for visit in range(n_visits_per_patient):
            visit_date = base_date + timedelta(days=visit * 180)
            
            # Generate features
            record = {
                'patient_id': patient_id,
                'visit_date': visit_date,
                
                # Cognitive features
                'mmse_score': np.random.randint(15, 30),
                'moca_score': np.random.randint(12, 28),
                'cdr_global': np.random.choice([0, 0.5, 1, 2]),
                'adas_cog_score': np.random.randint(5, 40),
                
                # Biomarker features
                'csf_ab42': np.random.uniform(200, 1500),
                'csf_tau': np.random.uniform(50, 500),
                'csf_ptau': np.random.uniform(10, 100),
                
                # Imaging features
                'hippocampus_left_volume': np.random.uniform(2000, 4000),
                'hippocampus_right_volume': np.random.uniform(2000, 4000),
                'entorhinal_cortex_thickness': np.random.uniform(2.0, 4.0),
                'ventricular_volume': np.random.uniform(20000, 50000),
                'whole_brain_volume': np.random.uniform(900000, 1200000),
                
                # Genetic features
                'apoe_genotype': np.random.choice(['e2/e3', 'e3/e3', 'e3/e4', 'e4/e4']),
                'apoe_e4_count': np.random.choice([0, 1, 2]),
                
                # Demographics
                'age': np.random.randint(55, 85),
                'sex': np.random.choice(['M', 'F']),
                'education_years': np.random.randint(8, 20),
                
                # Target
                'diagnosis': np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])  # 0: Normal, 1: MCI, 2: AD
            }
            
            # Calculate derived features
            record['ab42_tau_ratio'] = record['csf_ab42'] / record['csf_tau']
            record['ptau_tau_ratio'] = record['csf_ptau'] / record['csf_tau']
            record['hippocampus_total_volume'] = (
                record['hippocampus_left_volume'] + record['hippocampus_right_volume']
            )
            
            data.append(record)
    
    return pd.DataFrame(data)


def example_write_features():
    """Example: Write features to the feature store"""
    print("\n=== Example 1: Writing Features ===\n")
    
    # Initialize feature store
    feature_store = FeatureStore()
    
    # Generate sample data for different cohorts
    cohorts = ['ADNI', 'OASIS', 'NACC']
    
    for cohort in cohorts:
        print(f"Generating sample data for {cohort}...")
        df = generate_sample_features(n_patients=50, n_visits_per_patient=3)
        
        print(f"Writing {len(df)} records to feature store...")
        stats = feature_store.write_features(
            features_df=df,
            cohort=cohort,
            partition_by_date=True
        )
        
        print(f"✓ Wrote {stats['total_records']} records to {stats['partitions_written']} partitions")
        print(f"  Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB\n")


def example_read_features():
    """Example: Read features from the feature store"""
    print("\n=== Example 2: Reading Features ===\n")
    
    feature_store = FeatureStore()
    
    # Read all features from ADNI cohort
    print("Reading all ADNI features...")
    df = feature_store.read_features(cohorts=['ADNI'])
    print(f"✓ Retrieved {len(df)} records")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Date range: {df['visit_date'].min()} to {df['visit_date'].max()}\n")
    
    # Read features for specific patients
    print("Reading features for specific patients...")
    patient_ids = df['patient_id'].unique()[:5].tolist()
    df_patients = feature_store.read_features(patient_ids=patient_ids)
    print(f"✓ Retrieved {len(df_patients)} records for {len(patient_ids)} patients\n")
    
    # Read features with date range
    print("Reading features with date range...")
    from datetime import date
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    df_date = feature_store.read_features(date_range=(start_date, end_date))
    print(f"✓ Retrieved {len(df_date)} records in date range\n")


def example_patient_features():
    """Example: Get features for a specific patient"""
    print("\n=== Example 3: Patient Features ===\n")
    
    feature_store = FeatureStore()
    
    # Get all features
    df = feature_store.read_features(cohorts=['ADNI'], use_cache=False)
    
    if df.empty:
        print("No data available. Run example_write_features() first.")
        return
    
    patient_id = df['patient_id'].iloc[0]
    
    # Get all visits for patient
    print(f"Getting all features for patient {patient_id}...")
    patient_df = feature_store.get_patient_features(patient_id)
    print(f"✓ Retrieved {len(patient_df)} visits")
    print(f"  Visit dates: {patient_df['visit_date'].tolist()}\n")
    
    # Get latest features
    print(f"Getting latest features for patient {patient_id}...")
    latest = feature_store.get_latest_features(patient_id)
    print(f"✓ Latest visit: {latest['visit_date']}")
    print(f"  MMSE score: {latest['mmse_score']}")
    print(f"  Diagnosis: {latest['diagnosis']}\n")


def example_training_data():
    """Example: Get training data"""
    print("\n=== Example 4: Training Data ===\n")
    
    feature_store = FeatureStore()
    
    print("Loading training data...")
    features, labels = feature_store.get_training_data(
        cohorts=['ADNI', 'OASIS'],
        min_completeness=0.7
    )
    
    print(f"✓ Training data loaded:")
    print(f"  Samples: {len(features)}")
    print(f"  Features: {len(features.columns)}")
    print(f"  Label distribution: {labels.value_counts().to_dict()}\n")
    
    print("Feature names:")
    for i, col in enumerate(features.columns[:10], 1):
        print(f"  {i}. {col}")
    if len(features.columns) > 10:
        print(f"  ... and {len(features.columns) - 10} more\n")


def example_statistics():
    """Example: Get feature statistics"""
    print("\n=== Example 5: Feature Statistics ===\n")
    
    feature_store = FeatureStore()
    
    print("Calculating feature statistics...")
    stats = feature_store.get_feature_statistics(cohorts=['ADNI'])
    
    if stats.empty:
        print("No statistics available.")
        return
    
    print(f"✓ Statistics for {len(stats)} features:\n")
    
    # Show stats for a few features
    features_to_show = ['mmse_score', 'csf_ab42', 'hippocampus_total_volume']
    
    for feature in features_to_show:
        if feature in stats.index:
            print(f"{feature}:")
            print(f"  Mean: {stats.loc[feature, 'mean']:.2f}")
            print(f"  Std: {stats.loc[feature, 'std']:.2f}")
            print(f"  Range: [{stats.loc[feature, 'min']:.2f}, {stats.loc[feature, 'max']:.2f}]")
            print(f"  Completeness: {stats.loc[feature, 'completeness']:.1%}\n")


def example_storage_info():
    """Example: Get storage information"""
    print("\n=== Example 6: Storage Information ===\n")
    
    feature_store = FeatureStore()
    
    print("Getting storage information...")
    info = feature_store.get_storage_info()
    
    print(f"✓ Storage information:")
    print(f"  Path: {info['storage_path']}")
    print(f"  Total size: {info['total_size_mb']:.2f} MB ({info['total_size_gb']:.3f} GB)")
    print(f"  Files: {info['file_count']}")
    print(f"  Partitions: {info['partition_count']}\n")


def example_compression():
    """Example: Get compression statistics"""
    print("\n=== Example 7: Compression Statistics ===\n")
    
    feature_store = FeatureStore()
    
    print("Analyzing compression...")
    stats = feature_store.get_compression_statistics()
    
    if stats['file_count'] == 0:
        print("No files to analyze.")
        return
    
    print(f"✓ Compression statistics:")
    print(f"  Files analyzed: {stats['file_count']}")
    print(f"  Compressed size: {stats['total_compressed_mb']:.2f} MB")
    print(f"  Uncompressed size: {stats['total_uncompressed_mb']:.2f} MB")
    print(f"  Compression ratio: {stats['compression_ratio']:.3f}")
    print(f"  Storage savings: {stats['storage_savings_percent']:.1f}%")
    print(f"  Meets 50% target: {'✓ Yes' if stats['meets_target'] else '✗ No'}\n")


def example_index():
    """Example: Index operations"""
    print("\n=== Example 8: Index Operations ===\n")
    
    feature_store = FeatureStore()
    
    # Rebuild index
    print("Rebuilding index...")
    feature_store.rebuild_index()
    print("✓ Index rebuilt\n")
    
    # Get index statistics
    print("Getting index statistics...")
    stats = feature_store.get_index_statistics()
    
    print(f"✓ Index statistics:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  Total patients: {stats['total_patients']}")
    print(f"  Total cohorts: {stats['total_cohorts']}")
    print(f"  Date range: {stats['date_range']}")
    print(f"  Last updated: {stats['last_updated']}")
    
    if 'cohort_distribution' in stats:
        print(f"\n  Cohort distribution:")
        for cohort, count in stats['cohort_distribution'].items():
            print(f"    {cohort}: {count} patients")
    print()


def example_cache():
    """Example: Cache operations"""
    print("\n=== Example 9: Cache Operations ===\n")
    
    feature_store = FeatureStore()
    
    # Get all features
    df = feature_store.read_features(cohorts=['ADNI'], use_cache=False)
    
    if df.empty:
        print("No data available.")
        return
    
    patient_id = df['patient_id'].iloc[0]
    
    # First read (no cache)
    print(f"First read for patient {patient_id} (no cache)...")
    import time
    start = time.time()
    df1 = feature_store.get_patient_features(patient_id, use_cache=True)
    time1 = time.time() - start
    print(f"✓ Retrieved {len(df1)} records in {time1:.4f}s\n")
    
    # Second read (from cache)
    print(f"Second read for patient {patient_id} (from cache)...")
    start = time.time()
    df2 = feature_store.get_patient_features(patient_id, use_cache=True)
    time2 = time.time() - start
    print(f"✓ Retrieved {len(df2)} records in {time2:.4f}s")
    print(f"  Speedup: {time1/time2:.1f}x faster\n")
    
    # Clear cache
    print("Clearing cache...")
    feature_store.clear_cache(patient_id)
    print("✓ Cache cleared\n")


def example_optimize():
    """Example: Optimize storage"""
    print("\n=== Example 10: Optimize Storage ===\n")
    
    feature_store = FeatureStore()
    
    print("Optimizing storage...")
    stats = feature_store.optimize_storage()
    
    print(f"✓ Storage optimized:")
    print(f"  Files before: {stats['files_before']}")
    print(f"  Files after: {stats['files_after']}")
    print(f"  Size before: {stats['size_before'] / 1024 / 1024:.2f} MB")
    print(f"  Size after: {stats['size_after'] / 1024 / 1024:.2f} MB")
    
    if stats['size_before'] > 0:
        reduction = (stats['size_before'] - stats['size_after']) / stats['size_before'] * 100
        print(f"  Size reduction: {reduction:.1f}%\n")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Feature Store Examples")
    print("=" * 60)
    
    try:
        # Write sample data
        example_write_features()
        
        # Read operations
        example_read_features()
        example_patient_features()
        example_training_data()
        
        # Statistics and info
        example_statistics()
        example_storage_info()
        example_compression()
        example_index()
        
        # Performance
        example_cache()
        example_optimize()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
