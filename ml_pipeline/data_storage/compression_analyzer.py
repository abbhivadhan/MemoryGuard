"""
Compression analysis utilities for feature store
Analyzes compression ratios and storage efficiency
"""
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import pyarrow.parquet as pq
import numpy as np

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger


class CompressionAnalyzer:
    """
    Analyze compression efficiency of Parquet files
    
    Measures:
    - Compression ratio
    - Storage savings
    - Read/write performance
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize compression analyzer
        
        Args:
            storage_path: Path to feature store
        """
        self.storage_path = storage_path or settings.FEATURES_PATH
    
    def analyze_compression(self) -> Dict:
        """
        Analyze compression across all Parquet files
        
        Returns:
            Dictionary with compression statistics
        """
        total_compressed_size = 0
        total_uncompressed_size = 0
        file_count = 0
        compression_ratios = []
        
        # Scan all Parquet files
        for parquet_file in self.storage_path.rglob("*.parquet"):
            try:
                # Get file metadata
                parquet_metadata = pq.read_metadata(parquet_file)
                
                compressed_size = parquet_file.stat().st_size
                
                # Calculate uncompressed size from metadata
                uncompressed_size = 0
                for i in range(parquet_metadata.num_row_groups):
                    row_group = parquet_metadata.row_group(i)
                    for j in range(row_group.num_columns):
                        column = row_group.column(j)
                        uncompressed_size += column.total_uncompressed_size
                
                if uncompressed_size > 0:
                    ratio = compressed_size / uncompressed_size
                    compression_ratios.append(ratio)
                    
                    total_compressed_size += compressed_size
                    total_uncompressed_size += uncompressed_size
                    file_count += 1
                    
            except Exception as e:
                main_logger.warning(
                    f"Failed to analyze {parquet_file}: {str(e)}",
                    extra={'operation': 'analyze_compression', 'user_id': 'system'}
                )
        
        if file_count == 0:
            return {
                'file_count': 0,
                'total_compressed_mb': 0,
                'total_uncompressed_mb': 0,
                'compression_ratio': 0,
                'storage_savings_percent': 0,
                'average_compression_ratio': 0
            }
        
        overall_ratio = total_compressed_size / total_uncompressed_size
        storage_savings = (1 - overall_ratio) * 100
        
        stats = {
            'file_count': file_count,
            'total_compressed_mb': total_compressed_size / 1024 / 1024,
            'total_uncompressed_mb': total_uncompressed_size / 1024 / 1024,
            'compression_ratio': overall_ratio,
            'storage_savings_percent': storage_savings,
            'average_compression_ratio': np.mean(compression_ratios),
            'min_compression_ratio': np.min(compression_ratios),
            'max_compression_ratio': np.max(compression_ratios),
            'meets_target': storage_savings >= 50.0
        }
        
        main_logger.info(
            f"Compression analysis: {storage_savings:.1f}% storage savings "
            f"({total_compressed_size / 1024 / 1024:.2f} MB compressed from "
            f"{total_uncompressed_size / 1024 / 1024:.2f} MB uncompressed)",
            extra={
                'operation': 'analyze_compression',
                'user_id': 'system',
                'savings_percent': storage_savings
            }
        )
        
        return stats
    
    def compare_compression_methods(
        self,
        sample_df: pd.DataFrame,
        methods: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compare different compression methods
        
        Args:
            sample_df: Sample DataFrame to test
            methods: List of compression methods to test
            
        Returns:
            DataFrame with comparison results
        """
        if methods is None:
            methods = ['snappy', 'gzip', 'brotli', 'zstd', 'lz4']
        
        results = []
        temp_dir = self.storage_path / "_compression_test"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            for method in methods:
                try:
                    test_file = temp_dir / f"test_{method}.parquet"
                    
                    # Write with compression
                    import time
                    start_time = time.time()
                    sample_df.to_parquet(
                        test_file,
                        compression=method,
                        index=False
                    )
                    write_time = time.time() - start_time
                    
                    # Get file size
                    compressed_size = test_file.stat().st_size
                    
                    # Read back
                    start_time = time.time()
                    _ = pd.read_parquet(test_file)
                    read_time = time.time() - start_time
                    
                    # Calculate uncompressed size (approximate)
                    uncompressed_size = sample_df.memory_usage(deep=True).sum()
                    
                    ratio = compressed_size / uncompressed_size
                    savings = (1 - ratio) * 100
                    
                    results.append({
                        'method': method,
                        'compressed_mb': compressed_size / 1024 / 1024,
                        'uncompressed_mb': uncompressed_size / 1024 / 1024,
                        'compression_ratio': ratio,
                        'savings_percent': savings,
                        'write_time_sec': write_time,
                        'read_time_sec': read_time,
                        'total_time_sec': write_time + read_time
                    })
                    
                    # Clean up
                    test_file.unlink()
                    
                except Exception as e:
                    main_logger.warning(
                        f"Failed to test {method} compression: {str(e)}",
                        extra={'operation': 'compare_compression', 'user_id': 'system'}
                    )
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
        
        results_df = pd.DataFrame(results)
        
        if not results_df.empty:
            # Sort by best compression ratio
            results_df = results_df.sort_values('compression_ratio')
            
            main_logger.info(
                f"Compression comparison complete. Best method: "
                f"{results_df.iloc[0]['method']} "
                f"({results_df.iloc[0]['savings_percent']:.1f}% savings)",
                extra={'operation': 'compare_compression', 'user_id': 'system'}
            )
        
        return results_df
    
    def get_file_compression_details(self, file_path: Path) -> Dict:
        """
        Get detailed compression info for a specific file
        
        Args:
            file_path: Path to Parquet file
            
        Returns:
            Dictionary with compression details
        """
        try:
            metadata = pq.read_metadata(file_path)
            
            compressed_size = file_path.stat().st_size
            uncompressed_size = 0
            
            column_details = []
            
            for i in range(metadata.num_row_groups):
                row_group = metadata.row_group(i)
                
                for j in range(row_group.num_columns):
                    column = row_group.column(j)
                    
                    col_compressed = column.total_compressed_size
                    col_uncompressed = column.total_uncompressed_size
                    
                    uncompressed_size += col_uncompressed
                    
                    column_details.append({
                        'column_name': column.path_in_schema,
                        'compressed_bytes': col_compressed,
                        'uncompressed_bytes': col_uncompressed,
                        'compression_ratio': col_compressed / col_uncompressed if col_uncompressed > 0 else 0,
                        'compression': column.compression
                    })
            
            return {
                'file_path': str(file_path),
                'total_compressed_mb': compressed_size / 1024 / 1024,
                'total_uncompressed_mb': uncompressed_size / 1024 / 1024,
                'compression_ratio': compressed_size / uncompressed_size if uncompressed_size > 0 else 0,
                'storage_savings_percent': (1 - compressed_size / uncompressed_size) * 100 if uncompressed_size > 0 else 0,
                'num_rows': metadata.num_rows,
                'num_row_groups': metadata.num_row_groups,
                'num_columns': metadata.num_columns,
                'column_details': column_details
            }
            
        except Exception as e:
            main_logger.error(
                f"Failed to get compression details for {file_path}: {str(e)}",
                extra={'operation': 'get_file_compression_details', 'user_id': 'system'}
            )
            return {}
    
    def optimize_compression_settings(
        self,
        sample_df: pd.DataFrame
    ) -> Dict:
        """
        Find optimal compression settings for the data
        
        Args:
            sample_df: Sample DataFrame
            
        Returns:
            Dictionary with recommended settings
        """
        # Test different compression levels for snappy
        best_settings = {
            'compression': 'snappy',
            'compression_level': None,
            'use_dictionary': True,
            'data_page_size': 1024 * 1024
        }
        
        # Test with and without dictionary encoding
        temp_dir = self.storage_path / "_optimization_test"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            results = []
            
            for use_dict in [True, False]:
                for page_size in [512 * 1024, 1024 * 1024, 2048 * 1024]:
                    test_file = temp_dir / f"test_dict{use_dict}_page{page_size}.parquet"
                    
                    try:
                        import time
                        start_time = time.time()
                        
                        sample_df.to_parquet(
                            test_file,
                            compression='snappy',
                            use_dictionary=use_dict,
                            index=False
                        )
                        
                        write_time = time.time() - start_time
                        
                        compressed_size = test_file.stat().st_size
                        
                        start_time = time.time()
                        _ = pd.read_parquet(test_file)
                        read_time = time.time() - start_time
                        
                        uncompressed_size = sample_df.memory_usage(deep=True).sum()
                        
                        results.append({
                            'use_dictionary': use_dict,
                            'data_page_size': page_size,
                            'compressed_size': compressed_size,
                            'compression_ratio': compressed_size / uncompressed_size,
                            'write_time': write_time,
                            'read_time': read_time,
                            'total_time': write_time + read_time
                        })
                        
                        test_file.unlink()
                        
                    except Exception as e:
                        main_logger.warning(
                            f"Failed optimization test: {str(e)}",
                            extra={'operation': 'optimize_compression', 'user_id': 'system'}
                        )
            
            if results:
                # Find best balance of compression and speed
                results_df = pd.DataFrame(results)
                
                # Normalize metrics
                results_df['compression_score'] = 1 - results_df['compression_ratio']
                results_df['speed_score'] = 1 / (results_df['total_time'] + 0.001)
                
                # Combined score (70% compression, 30% speed)
                results_df['combined_score'] = (
                    0.7 * results_df['compression_score'] +
                    0.3 * results_df['speed_score']
                )
                
                best_idx = results_df['combined_score'].idxmax()
                best_result = results_df.loc[best_idx]
                
                best_settings['use_dictionary'] = bool(best_result['use_dictionary'])
                best_settings['data_page_size'] = int(best_result['data_page_size'])
                
                main_logger.info(
                    f"Optimal compression settings: dictionary={best_settings['use_dictionary']}, "
                    f"page_size={best_settings['data_page_size']}",
                    extra={'operation': 'optimize_compression', 'user_id': 'system'}
                )
        
        finally:
            # Clean up
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
        
        return best_settings
