"""
Feature Store implementation using Parquet for efficient storage and retrieval
Implements partitioning, indexing, compression, and caching
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, date
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
from sqlalchemy.orm import Session

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger
from ml_pipeline.data_storage.cache import RedisCache
from ml_pipeline.data_storage.database import get_db_context
from ml_pipeline.data_storage.models import ProcessedFeature
from ml_pipeline.data_storage.feature_index import FeatureIndex
from ml_pipeline.data_storage.compression_analyzer import CompressionAnalyzer


class FeatureStore:
    """
    Feature store for efficient storage and retrieval of processed features
    
    Features:
    - Parquet columnar storage for efficient I/O
    - Partitioning by date and cohort for fast queries
    - Compression to reduce storage by 50%+
    - Indexing by patient_id and timestamp
    - Redis caching for frequently accessed features
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        cache_manager: Optional[RedisCache] = None,
        use_index: bool = True
    ):
        """
        Initialize feature store
        
        Args:
            storage_path: Path to store Parquet files
            cache_manager: Cache manager for Redis caching
            use_index: Whether to use indexing for fast lookups
        """
        self.storage_path = storage_path or settings.FEATURES_PATH
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.cache_manager = cache_manager or RedisCache()
        
        # Initialize index
        self.use_index = use_index
        self.index = FeatureIndex(self.storage_path) if use_index else None
        
        # Parquet write options for compression
        self.write_options = {
            'compression': 'snappy',  # Fast compression with good ratio
            'compression_level': 9,
            'use_dictionary': True,
            'write_statistics': True,
            'data_page_size': 1024 * 1024,  # 1MB pages
        }
        
        main_logger.info(
            f"Feature store initialized at {self.storage_path}",
            extra={'operation': 'feature_store_init', 'user_id': 'system'}
        )
    
    def _get_partition_path(
        self,
        cohort: str,
        year: int,
        month: int
    ) -> Path:
        """
        Get partition path for data
        
        Args:
            cohort: Data cohort (e.g., 'ADNI', 'OASIS', 'NACC')
            year: Year
            month: Month
            
        Returns:
            Path to partition directory
        """
        partition_path = (
            self.storage_path / 
            f"cohort={cohort}" / 
            f"year={year}" / 
            f"month={month:02d}"
        )
        partition_path.mkdir(parents=True, exist_ok=True)
        return partition_path
    
    def write_features(
        self,
        features_df: pd.DataFrame,
        cohort: str,
        partition_by_date: bool = True,
        overwrite: bool = False
    ) -> Dict[str, int]:
        """
        Write features to Parquet with partitioning and compression
        
        Args:
            features_df: DataFrame with processed features
            cohort: Data cohort (ADNI, OASIS, NACC)
            partition_by_date: Whether to partition by date
            overwrite: Whether to overwrite existing data
            
        Returns:
            Dictionary with write statistics
        """
        start_time = datetime.now()
        
        # Validate required columns
        required_cols = ['patient_id', 'visit_date']
        missing_cols = [col for col in required_cols if col not in features_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure visit_date is datetime
        if not pd.api.types.is_datetime64_any_dtype(features_df['visit_date']):
            features_df['visit_date'] = pd.to_datetime(features_df['visit_date'])
        
        # Add metadata columns
        features_df['cohort'] = cohort
        features_df['ingestion_timestamp'] = datetime.now()
        
        stats = {
            'total_records': len(features_df),
            'partitions_written': 0,
            'total_size_bytes': 0
        }
        
        if partition_by_date:
            # Partition by year and month
            features_df['year'] = features_df['visit_date'].dt.year
            features_df['month'] = features_df['visit_date'].dt.month
            
            # Group by partition
            for (year, month), group_df in features_df.groupby(['year', 'month']):
                partition_path = self._get_partition_path(cohort, year, month)
                file_path = partition_path / f"features_{cohort}_{year}_{month:02d}.parquet"
                
                # Drop partition columns before writing
                write_df = group_df.drop(columns=['year', 'month'])
                
                # Write to Parquet
                self._write_parquet_file(
                    write_df,
                    file_path,
                    overwrite=overwrite
                )
                
                stats['partitions_written'] += 1
                stats['total_size_bytes'] += file_path.stat().st_size
        else:
            # Write without partitioning
            file_path = self.storage_path / f"features_{cohort}.parquet"
            self._write_parquet_file(
                features_df,
                file_path,
                overwrite=overwrite
            )
            stats['partitions_written'] = 1
            stats['total_size_bytes'] = file_path.stat().st_size
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Rebuild index after writing
        if self.use_index and self.index:
            self.index.build_index(force_rebuild=True)
        
        main_logger.info(
            f"Wrote {stats['total_records']} features to {stats['partitions_written']} partitions "
            f"({stats['total_size_bytes'] / 1024 / 1024:.2f} MB) in {duration:.2f}s",
            extra={
                'operation': 'write_features',
                'user_id': 'system',
                'cohort': cohort,
                'records': stats['total_records']
            }
        )
        
        return stats
    
    def _write_parquet_file(
        self,
        df: pd.DataFrame,
        file_path: Path,
        overwrite: bool = False
    ):
        """
        Write DataFrame to Parquet file with compression
        
        Args:
            df: DataFrame to write
            file_path: Output file path
            overwrite: Whether to overwrite existing file
        """
        if file_path.exists() and not overwrite:
            # Append mode - read existing and concatenate
            existing_df = pd.read_parquet(file_path)
            df = pd.concat([existing_df, df], ignore_index=True)
            
            # Remove duplicates based on patient_id and visit_date
            df = df.drop_duplicates(subset=['patient_id', 'visit_date'], keep='last')
        
        # Convert to PyArrow table for better control
        table = pa.Table.from_pandas(df)
        
        # Write with compression
        pq.write_table(
            table,
            file_path,
            compression=self.write_options['compression'],
            compression_level=self.write_options['compression_level'],
            use_dictionary=self.write_options['use_dictionary'],
            write_statistics=self.write_options['write_statistics'],
            data_page_size=self.write_options['data_page_size']
        )
    
    def read_features(
        self,
        patient_ids: Optional[List[str]] = None,
        cohorts: Optional[List[str]] = None,
        date_range: Optional[Tuple[date, date]] = None,
        columns: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Read features from Parquet with filtering
        
        Args:
            patient_ids: List of patient IDs to filter
            cohorts: List of cohorts to include
            date_range: Tuple of (start_date, end_date)
            columns: Specific columns to read
            use_cache: Whether to use Redis cache
            
        Returns:
            DataFrame with features
        """
        start_time = datetime.now()
        
        # Try cache first for single patient queries
        if use_cache and patient_ids and len(patient_ids) == 1:
            cache_key = f"features:{patient_ids[0]}"
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                main_logger.debug(
                    f"Cache hit for patient {patient_ids[0]}",
                    extra={'operation': 'read_features_cache', 'user_id': 'system'}
                )
                return pd.DataFrame(cached_data)
        
        # Use index for faster lookups if available
        if self.use_index and self.index and patient_ids:
            return self._read_features_indexed(
                patient_ids, cohorts, date_range, columns, use_cache
            )
        
        # Read from Parquet files
        dfs = []
        
        # Determine which partitions to read
        cohorts_to_read = cohorts or ['ADNI', 'OASIS', 'NACC']
        
        for cohort in cohorts_to_read:
            cohort_path = self.storage_path / f"cohort={cohort}"
            
            if not cohort_path.exists():
                continue
            
            # Find all Parquet files in cohort
            parquet_files = list(cohort_path.rglob("*.parquet"))
            
            for file_path in parquet_files:
                # Read with filters if possible
                filters = []
                
                if patient_ids:
                    filters.append(('patient_id', 'in', patient_ids))
                
                if date_range:
                    start_date, end_date = date_range
                    filters.append(('visit_date', '>=', pd.Timestamp(start_date)))
                    filters.append(('visit_date', '<=', pd.Timestamp(end_date)))
                
                try:
                    df = pd.read_parquet(
                        file_path,
                        columns=columns,
                        filters=filters if filters else None
                    )
                    
                    if len(df) > 0:
                        dfs.append(df)
                        
                except Exception as e:
                    main_logger.warning(
                        f"Failed to read {file_path}: {str(e)}",
                        extra={'operation': 'read_features', 'user_id': 'system'}
                    )
        
        if not dfs:
            main_logger.warning(
                "No features found matching criteria",
                extra={'operation': 'read_features', 'user_id': 'system'}
            )
            return pd.DataFrame()
        
        # Combine all DataFrames
        result_df = pd.concat(dfs, ignore_index=True)
        
        # Apply additional filters if needed
        if patient_ids:
            result_df = result_df[result_df['patient_id'].isin(patient_ids)]
        
        if date_range:
            start_date, end_date = date_range
            result_df = result_df[
                (result_df['visit_date'] >= pd.Timestamp(start_date)) &
                (result_df['visit_date'] <= pd.Timestamp(end_date))
            ]
        
        # Cache single patient results
        if use_cache and patient_ids and len(patient_ids) == 1 and len(result_df) > 0:
            cache_key = f"features:{patient_ids[0]}"
            self.cache_manager.set(
                cache_key,
                result_df.to_dict('records'),
                ttl=settings.CACHE_TTL
            )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        main_logger.info(
            f"Read {len(result_df)} features in {duration:.2f}s",
            extra={
                'operation': 'read_features',
                'user_id': 'system',
                'records': len(result_df)
            }
        )
        
        return result_df
    
    def _read_features_indexed(
        self,
        patient_ids: List[str],
        cohorts: Optional[List[str]],
        date_range: Optional[Tuple[date, date]],
        columns: Optional[List[str]],
        use_cache: bool
    ) -> pd.DataFrame:
        """
        Read features using index for faster lookups
        
        Args:
            patient_ids: List of patient IDs
            cohorts: Cohorts to filter
            date_range: Date range filter
            columns: Columns to read
            use_cache: Whether to use cache
            
        Returns:
            DataFrame with features
        """
        dfs = []
        
        for patient_id in patient_ids:
            # Get file locations from index
            locations = self.index.get_patient_locations(patient_id)
            
            if not locations:
                continue
            
            # Group by file to minimize I/O
            files_to_read = {}
            for file_path, row_idx in locations:
                if file_path not in files_to_read:
                    files_to_read[file_path] = []
                files_to_read[file_path].append(row_idx)
            
            # Read each file
            for file_path, row_indices in files_to_read.items():
                try:
                    df = pd.read_parquet(file_path, columns=columns)
                    
                    # Filter by row indices
                    df = df.iloc[row_indices]
                    
                    # Apply additional filters
                    if cohorts and 'cohort' in df.columns:
                        df = df[df['cohort'].isin(cohorts)]
                    
                    if date_range and 'visit_date' in df.columns:
                        start_date, end_date = date_range
                        df = df[
                            (df['visit_date'] >= pd.Timestamp(start_date)) &
                            (df['visit_date'] <= pd.Timestamp(end_date))
                        ]
                    
                    if len(df) > 0:
                        dfs.append(df)
                        
                except Exception as e:
                    main_logger.warning(
                        f"Failed to read {file_path}: {str(e)}",
                        extra={'operation': 'read_features_indexed', 'user_id': 'system'}
                    )
        
        if not dfs:
            return pd.DataFrame()
        
        result_df = pd.concat(dfs, ignore_index=True)
        
        # Cache single patient results
        if use_cache and len(patient_ids) == 1 and len(result_df) > 0:
            cache_key = f"features:{patient_ids[0]}"
            self.cache_manager.set(
                cache_key,
                result_df.to_dict('records'),
                ttl=settings.CACHE_TTL
            )
        
        return result_df
    
    def rebuild_index(self):
        """Rebuild feature index"""
        if self.use_index and self.index:
            self.index.build_index(force_rebuild=True)
            main_logger.info(
                "Feature index rebuilt",
                extra={'operation': 'rebuild_index', 'user_id': 'system'}
            )
    
    def get_index_statistics(self) -> Dict:
        """Get index statistics"""
        if self.use_index and self.index:
            return self.index.get_statistics()
        return {}
    
    def get_compression_statistics(self) -> Dict:
        """
        Get compression statistics for stored features
        
        Returns:
            Dictionary with compression stats
        """
        analyzer = CompressionAnalyzer(self.storage_path)
        return analyzer.analyze_compression()

    
    def get_patient_features(
        self,
        patient_id: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get all features for a specific patient
        
        Args:
            patient_id: Patient ID
            use_cache: Whether to use cache
            
        Returns:
            DataFrame with patient features
        """
        return self.read_features(
            patient_ids=[patient_id],
            use_cache=use_cache
        )
    
    def get_latest_features(
        self,
        patient_id: str,
        use_cache: bool = True
    ) -> Optional[pd.Series]:
        """
        Get most recent features for a patient
        
        Args:
            patient_id: Patient ID
            use_cache: Whether to use cache
            
        Returns:
            Series with latest features or None
        """
        df = self.get_patient_features(patient_id, use_cache=use_cache)
        
        if df.empty:
            return None
        
        # Sort by visit_date and get latest
        df = df.sort_values('visit_date', ascending=False)
        return df.iloc[0]
    
    def get_training_data(
        self,
        cohorts: Optional[List[str]] = None,
        date_range: Optional[Tuple[date, date]] = None,
        min_completeness: float = 0.7
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Get training data with features and labels
        
        Args:
            cohorts: Cohorts to include
            date_range: Date range filter
            min_completeness: Minimum completeness threshold
            
        Returns:
            Tuple of (features DataFrame, labels Series)
        """
        # Read all features
        df = self.read_features(
            cohorts=cohorts,
            date_range=date_range,
            use_cache=False
        )
        
        if df.empty:
            raise ValueError("No training data found")
        
        # Check completeness
        completeness = df.notna().mean()
        low_completeness_cols = completeness[completeness < min_completeness].index.tolist()
        
        if low_completeness_cols:
            main_logger.warning(
                f"Dropping columns with low completeness: {low_completeness_cols}",
                extra={'operation': 'get_training_data', 'user_id': 'system'}
            )
            df = df.drop(columns=low_completeness_cols)
        
        # Separate features and labels
        if 'diagnosis' not in df.columns:
            raise ValueError("No diagnosis column found for labels")
        
        labels = df['diagnosis']
        
        # Drop non-feature columns
        drop_cols = [
            'diagnosis', 'patient_id', 'visit_date', 'cohort',
            'ingestion_timestamp', 'data_source', 'feature_version',
            'created_at', 'updated_at'
        ]
        features = df.drop(columns=[col for col in drop_cols if col in df.columns])
        
        main_logger.info(
            f"Loaded training data: {len(features)} samples, {len(features.columns)} features",
            extra={
                'operation': 'get_training_data',
                'user_id': 'system',
                'samples': len(features),
                'features': len(features.columns)
            }
        )
        
        return features, labels
    
    def get_feature_statistics(
        self,
        cohorts: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get statistics for all features
        
        Args:
            cohorts: Cohorts to include
            
        Returns:
            DataFrame with feature statistics
        """
        df = self.read_features(cohorts=cohorts, use_cache=False)
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats = pd.DataFrame({
            'count': df[numeric_cols].count(),
            'mean': df[numeric_cols].mean(),
            'std': df[numeric_cols].std(),
            'min': df[numeric_cols].min(),
            '25%': df[numeric_cols].quantile(0.25),
            '50%': df[numeric_cols].quantile(0.50),
            '75%': df[numeric_cols].quantile(0.75),
            'max': df[numeric_cols].max(),
            'completeness': df[numeric_cols].notna().mean()
        })
        
        return stats
    
    def get_storage_info(self) -> Dict[str, Union[int, float, str]]:
        """
        Get storage information and statistics
        
        Returns:
            Dictionary with storage info
        """
        total_size = 0
        file_count = 0
        partition_count = 0
        
        # Count files and sizes
        for cohort_dir in self.storage_path.glob("cohort=*"):
            partition_count += 1
            for parquet_file in cohort_dir.rglob("*.parquet"):
                file_count += 1
                total_size += parquet_file.stat().st_size
        
        return {
            'storage_path': str(self.storage_path),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024,
            'total_size_gb': total_size / 1024 / 1024 / 1024,
            'file_count': file_count,
            'partition_count': partition_count
        }
    
    def optimize_storage(self) -> Dict[str, int]:
        """
        Optimize storage by compacting small files
        
        Returns:
            Dictionary with optimization statistics
        """
        stats = {
            'files_before': 0,
            'files_after': 0,
            'size_before': 0,
            'size_after': 0
        }
        
        # Get initial stats
        info = self.get_storage_info()
        stats['files_before'] = info['file_count']
        stats['size_before'] = info['total_size_bytes']
        
        # Compact files by partition
        for cohort_dir in self.storage_path.glob("cohort=*"):
            for year_dir in cohort_dir.glob("year=*"):
                for month_dir in year_dir.glob("month=*"):
                    parquet_files = list(month_dir.glob("*.parquet"))
                    
                    if len(parquet_files) > 1:
                        # Read all files in partition
                        dfs = [pd.read_parquet(f) for f in parquet_files]
                        combined_df = pd.concat(dfs, ignore_index=True)
                        
                        # Remove duplicates
                        combined_df = combined_df.drop_duplicates(
                            subset=['patient_id', 'visit_date'],
                            keep='last'
                        )
                        
                        # Delete old files
                        for f in parquet_files:
                            f.unlink()
                        
                        # Write compacted file
                        cohort = cohort_dir.name.split('=')[1]
                        year = int(year_dir.name.split('=')[1])
                        month = int(month_dir.name.split('=')[1])
                        
                        new_file = month_dir / f"features_{cohort}_{year}_{month:02d}.parquet"
                        self._write_parquet_file(combined_df, new_file, overwrite=True)
        
        # Get final stats
        info = self.get_storage_info()
        stats['files_after'] = info['file_count']
        stats['size_after'] = info['total_size_bytes']
        
        compression_ratio = (
            (stats['size_before'] - stats['size_after']) / stats['size_before'] * 100
            if stats['size_before'] > 0 else 0
        )
        
        main_logger.info(
            f"Storage optimized: {stats['files_before']} -> {stats['files_after']} files, "
            f"{compression_ratio:.1f}% size reduction",
            extra={'operation': 'optimize_storage', 'user_id': 'system'}
        )
        
        return stats
    
    def clear_cache(self, patient_id: Optional[str] = None):
        """
        Clear cached features
        
        Args:
            patient_id: Specific patient ID to clear, or None for all
        """
        if patient_id:
            cache_key = f"features:{patient_id}"
            self.cache_manager.delete(cache_key)
        else:
            # Clear all feature cache keys
            self.cache_manager.clear_pattern("features:*")
        
        main_logger.info(
            f"Cache cleared for {'patient ' + patient_id if patient_id else 'all patients'}",
            extra={'operation': 'clear_cache', 'user_id': 'system'}
        )
    
    def delete_features(
        self,
        patient_ids: Optional[List[str]] = None,
        cohorts: Optional[List[str]] = None,
        date_range: Optional[Tuple[date, date]] = None
    ) -> int:
        """
        Delete features matching criteria
        
        Args:
            patient_ids: Patient IDs to delete
            cohorts: Cohorts to delete
            date_range: Date range to delete
            
        Returns:
            Number of records deleted
        """
        # Read matching features
        df = self.read_features(
            patient_ids=patient_ids,
            cohorts=cohorts,
            date_range=date_range,
            use_cache=False
        )
        
        if df.empty:
            return 0
        
        deleted_count = len(df)
        
        # For each partition, rewrite without deleted records
        for cohort in df['cohort'].unique():
            cohort_df = df[df['cohort'] == cohort]
            
            for (year, month), group_df in cohort_df.groupby([
                cohort_df['visit_date'].dt.year,
                cohort_df['visit_date'].dt.month
            ]):
                partition_path = self._get_partition_path(cohort, year, month)
                file_path = partition_path / f"features_{cohort}_{year}_{month:02d}.parquet"
                
                if file_path.exists():
                    # Read existing data
                    existing_df = pd.read_parquet(file_path)
                    
                    # Remove records to delete
                    mask = ~(
                        existing_df['patient_id'].isin(group_df['patient_id']) &
                        existing_df['visit_date'].isin(group_df['visit_date'])
                    )
                    remaining_df = existing_df[mask]
                    
                    if len(remaining_df) > 0:
                        # Rewrite file
                        self._write_parquet_file(remaining_df, file_path, overwrite=True)
                    else:
                        # Delete empty file
                        file_path.unlink()
        
        # Clear cache for deleted patients
        if patient_ids:
            for patient_id in patient_ids:
                self.clear_cache(patient_id)
        
        main_logger.info(
            f"Deleted {deleted_count} feature records",
            extra={
                'operation': 'delete_features',
                'user_id': 'system',
                'deleted_count': deleted_count
            }
        )
        
        return deleted_count
