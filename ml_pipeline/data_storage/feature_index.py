"""
Feature indexing system for fast lookups by patient_id and timestamp
Maintains indexes in memory and on disk for efficient queries
"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, date
import json
import pickle
from collections import defaultdict
import pandas as pd

from ml_pipeline.config.settings import settings
from ml_pipeline.config.logging_config import main_logger


class FeatureIndex:
    """
    Index system for fast feature lookups
    
    Maintains two primary indexes:
    1. Patient ID index: Maps patient_id -> list of (file_path, row_group)
    2. Timestamp index: Maps date -> list of (file_path, row_group)
    
    Indexes are persisted to disk and loaded on startup
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize feature index
        
        Args:
            storage_path: Path to feature store
        """
        self.storage_path = storage_path or settings.FEATURES_PATH
        self.index_path = self.storage_path / "_indexes"
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory indexes
        self.patient_index: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.date_index: Dict[date, List[Tuple[str, int]]] = defaultdict(list)
        self.cohort_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Metadata
        self.index_metadata = {
            'last_updated': None,
            'total_records': 0,
            'total_patients': 0,
            'date_range': (None, None)
        }
        
        # Load existing indexes
        self._load_indexes()
        
        main_logger.info(
            f"Feature index initialized with {self.index_metadata['total_records']} records",
            extra={'operation': 'index_init', 'user_id': 'system'}
        )
    
    def build_index(self, force_rebuild: bool = False):
        """
        Build or rebuild indexes from Parquet files
        
        Args:
            force_rebuild: Force rebuild even if indexes exist
        """
        if not force_rebuild and self.index_metadata['last_updated']:
            main_logger.info(
                "Indexes already exist, use force_rebuild=True to rebuild",
                extra={'operation': 'build_index', 'user_id': 'system'}
            )
            return
        
        start_time = datetime.now()
        
        # Clear existing indexes
        self.patient_index.clear()
        self.date_index.clear()
        self.cohort_index.clear()
        
        total_records = 0
        min_date = None
        max_date = None
        
        # Scan all Parquet files
        for cohort_dir in self.storage_path.glob("cohort=*"):
            cohort = cohort_dir.name.split('=')[1]
            
            for parquet_file in cohort_dir.rglob("*.parquet"):
                # Read file metadata
                try:
                    df = pd.read_parquet(
                        parquet_file,
                        columns=['patient_id', 'visit_date']
                    )
                    
                    if df.empty:
                        continue
                    
                    # Ensure visit_date is datetime
                    if not pd.api.types.is_datetime64_any_dtype(df['visit_date']):
                        df['visit_date'] = pd.to_datetime(df['visit_date'])
                    
                    # Build indexes
                    file_path_str = str(parquet_file.relative_to(self.storage_path))
                    
                    for idx, row in df.iterrows():
                        patient_id = row['patient_id']
                        visit_date = row['visit_date'].date()
                        
                        # Patient index
                        self.patient_index[patient_id].append((file_path_str, idx))
                        
                        # Date index
                        self.date_index[visit_date].append((file_path_str, idx))
                        
                        # Cohort index
                        self.cohort_index[cohort].add(patient_id)
                        
                        total_records += 1
                        
                        # Track date range
                        if min_date is None or visit_date < min_date:
                            min_date = visit_date
                        if max_date is None or visit_date > max_date:
                            max_date = visit_date
                    
                    main_logger.debug(
                        f"Indexed {len(df)} records from {parquet_file.name}",
                        extra={'operation': 'build_index', 'user_id': 'system'}
                    )
                    
                except Exception as e:
                    main_logger.error(
                        f"Failed to index {parquet_file}: {str(e)}",
                        extra={'operation': 'build_index', 'user_id': 'system'}
                    )
        
        # Update metadata
        self.index_metadata = {
            'last_updated': datetime.now(),
            'total_records': total_records,
            'total_patients': len(self.patient_index),
            'date_range': (min_date, max_date)
        }
        
        # Persist indexes
        self._save_indexes()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        main_logger.info(
            f"Built indexes for {total_records} records from {len(self.patient_index)} patients "
            f"in {duration:.2f}s",
            extra={
                'operation': 'build_index',
                'user_id': 'system',
                'records': total_records,
                'patients': len(self.patient_index)
            }
        )
    
    def get_patient_locations(self, patient_id: str) -> List[Tuple[Path, int]]:
        """
        Get file locations for a patient's features
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of (file_path, row_index) tuples
        """
        locations = self.patient_index.get(patient_id, [])
        
        # Convert relative paths to absolute
        return [
            (self.storage_path / file_path, row_idx)
            for file_path, row_idx in locations
        ]
    
    def get_date_locations(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[Tuple[Path, int]]:
        """
        Get file locations for features in date range
        
        Args:
            start_date: Start date
            end_date: End date (defaults to start_date)
            
        Returns:
            List of (file_path, row_index) tuples
        """
        if end_date is None:
            end_date = start_date
        
        locations = []
        
        for visit_date, locs in self.date_index.items():
            if start_date <= visit_date <= end_date:
                locations.extend(locs)
        
        # Convert relative paths to absolute
        return [
            (self.storage_path / file_path, row_idx)
            for file_path, row_idx in locations
        ]
    
    def get_cohort_patients(self, cohort: str) -> Set[str]:
        """
        Get all patient IDs in a cohort
        
        Args:
            cohort: Cohort name (ADNI, OASIS, NACC)
            
        Returns:
            Set of patient IDs
        """
        return self.cohort_index.get(cohort, set())
    
    def patient_exists(self, patient_id: str) -> bool:
        """
        Check if patient exists in index
        
        Args:
            patient_id: Patient ID
            
        Returns:
            True if patient exists
        """
        return patient_id in self.patient_index
    
    def get_patient_visit_dates(self, patient_id: str) -> List[date]:
        """
        Get all visit dates for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of visit dates
        """
        visit_dates = []
        
        for visit_date, locations in self.date_index.items():
            for file_path, row_idx in locations:
                # Check if this location belongs to the patient
                patient_locations = self.patient_index.get(patient_id, [])
                if (file_path, row_idx) in patient_locations:
                    visit_dates.append(visit_date)
        
        return sorted(visit_dates)
    
    def get_statistics(self) -> Dict:
        """
        Get index statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_records': self.index_metadata['total_records'],
            'total_patients': self.index_metadata['total_patients'],
            'total_cohorts': len(self.cohort_index),
            'date_range': self.index_metadata['date_range'],
            'last_updated': self.index_metadata['last_updated'],
            'cohort_distribution': {
                cohort: len(patients)
                for cohort, patients in self.cohort_index.items()
            }
        }
    
    def update_index(
        self,
        patient_id: str,
        visit_date: date,
        file_path: Path,
        row_idx: int,
        cohort: str
    ):
        """
        Update index with new record
        
        Args:
            patient_id: Patient ID
            visit_date: Visit date
            file_path: File path
            row_idx: Row index
            cohort: Cohort name
        """
        file_path_str = str(file_path.relative_to(self.storage_path))
        
        # Update indexes
        self.patient_index[patient_id].append((file_path_str, row_idx))
        self.date_index[visit_date].append((file_path_str, row_idx))
        self.cohort_index[cohort].add(patient_id)
        
        # Update metadata
        self.index_metadata['total_records'] += 1
        self.index_metadata['total_patients'] = len(self.patient_index)
        
        # Update date range
        min_date, max_date = self.index_metadata['date_range']
        if min_date is None or visit_date < min_date:
            min_date = visit_date
        if max_date is None or visit_date > max_date:
            max_date = visit_date
        self.index_metadata['date_range'] = (min_date, max_date)
        
        self.index_metadata['last_updated'] = datetime.now()
    
    def remove_from_index(
        self,
        patient_id: str,
        visit_date: Optional[date] = None
    ):
        """
        Remove patient from index
        
        Args:
            patient_id: Patient ID
            visit_date: Specific visit date to remove, or None for all
        """
        if patient_id not in self.patient_index:
            return
        
        if visit_date is None:
            # Remove all records for patient
            locations = self.patient_index[patient_id]
            
            # Remove from date index
            for file_path, row_idx in locations:
                for date_key in list(self.date_index.keys()):
                    self.date_index[date_key] = [
                        loc for loc in self.date_index[date_key]
                        if loc != (file_path, row_idx)
                    ]
                    if not self.date_index[date_key]:
                        del self.date_index[date_key]
            
            # Remove from patient index
            del self.patient_index[patient_id]
            
            # Remove from cohort indexes
            for cohort in self.cohort_index:
                self.cohort_index[cohort].discard(patient_id)
            
            self.index_metadata['total_records'] -= len(locations)
        else:
            # Remove specific visit
            locations = self.patient_index[patient_id]
            
            # Find and remove the specific visit
            for file_path, row_idx in locations:
                if (file_path, row_idx) in self.date_index.get(visit_date, []):
                    self.patient_index[patient_id].remove((file_path, row_idx))
                    self.date_index[visit_date].remove((file_path, row_idx))
                    self.index_metadata['total_records'] -= 1
                    break
            
            # If no more records for patient, remove from patient index
            if not self.patient_index[patient_id]:
                del self.patient_index[patient_id]
                for cohort in self.cohort_index:
                    self.cohort_index[cohort].discard(patient_id)
        
        self.index_metadata['total_patients'] = len(self.patient_index)
        self.index_metadata['last_updated'] = datetime.now()
    
    def _save_indexes(self):
        """Save indexes to disk"""
        try:
            # Save patient index
            with open(self.index_path / "patient_index.pkl", 'wb') as f:
                pickle.dump(dict(self.patient_index), f)
            
            # Save date index (convert dates to strings for JSON)
            date_index_serializable = {
                str(date_key): locations
                for date_key, locations in self.date_index.items()
            }
            with open(self.index_path / "date_index.json", 'w') as f:
                json.dump(date_index_serializable, f)
            
            # Save cohort index (convert sets to lists)
            cohort_index_serializable = {
                cohort: list(patients)
                for cohort, patients in self.cohort_index.items()
            }
            with open(self.index_path / "cohort_index.json", 'w') as f:
                json.dump(cohort_index_serializable, f)
            
            # Save metadata (convert dates to strings)
            metadata_serializable = self.index_metadata.copy()
            if metadata_serializable['last_updated']:
                metadata_serializable['last_updated'] = metadata_serializable['last_updated'].isoformat()
            if metadata_serializable['date_range'][0]:
                metadata_serializable['date_range'] = (
                    str(metadata_serializable['date_range'][0]),
                    str(metadata_serializable['date_range'][1])
                )
            
            with open(self.index_path / "metadata.json", 'w') as f:
                json.dump(metadata_serializable, f)
            
            main_logger.debug(
                "Indexes saved to disk",
                extra={'operation': 'save_indexes', 'user_id': 'system'}
            )
            
        except Exception as e:
            main_logger.error(
                f"Failed to save indexes: {str(e)}",
                extra={'operation': 'save_indexes', 'user_id': 'system'}
            )
    
    def _load_indexes(self):
        """Load indexes from disk"""
        try:
            # Load patient index
            patient_index_file = self.index_path / "patient_index.pkl"
            if patient_index_file.exists():
                with open(patient_index_file, 'rb') as f:
                    self.patient_index = defaultdict(list, pickle.load(f))
            
            # Load date index
            date_index_file = self.index_path / "date_index.json"
            if date_index_file.exists():
                with open(date_index_file, 'r') as f:
                    date_index_data = json.load(f)
                    # Convert string dates back to date objects
                    self.date_index = defaultdict(list, {
                        datetime.fromisoformat(date_str).date(): locations
                        for date_str, locations in date_index_data.items()
                    })
            
            # Load cohort index
            cohort_index_file = self.index_path / "cohort_index.json"
            if cohort_index_file.exists():
                with open(cohort_index_file, 'r') as f:
                    cohort_index_data = json.load(f)
                    # Convert lists back to sets
                    self.cohort_index = defaultdict(set, {
                        cohort: set(patients)
                        for cohort, patients in cohort_index_data.items()
                    })
            
            # Load metadata
            metadata_file = self.index_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                    # Convert strings back to appropriate types
                    if metadata['last_updated']:
                        metadata['last_updated'] = datetime.fromisoformat(metadata['last_updated'])
                    
                    if metadata['date_range'][0]:
                        metadata['date_range'] = (
                            datetime.fromisoformat(metadata['date_range'][0]).date(),
                            datetime.fromisoformat(metadata['date_range'][1]).date()
                        )
                    
                    self.index_metadata = metadata
            
            main_logger.debug(
                "Indexes loaded from disk",
                extra={'operation': 'load_indexes', 'user_id': 'system'}
            )
            
        except Exception as e:
            main_logger.warning(
                f"Failed to load indexes: {str(e)}. Will rebuild on first use.",
                extra={'operation': 'load_indexes', 'user_id': 'system'}
            )
