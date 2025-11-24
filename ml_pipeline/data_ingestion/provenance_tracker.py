"""Data provenance tracking for biomedical datasets."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import hashlib
import pandas as pd
from pydantic import BaseModel, Field

from ml_pipeline.config.settings import Settings
from ml_pipeline.data_storage.database import get_db_session

logger = logging.getLogger(__name__)


class DataSource(str, Enum):
    """Supported data sources."""
    ADNI = "ADNI"
    OASIS = "OASIS"
    NACC = "NACC"
    MANUAL = "MANUAL"
    DERIVED = "DERIVED"


class ProcessingStage(str, Enum):
    """Data processing stages."""
    RAW = "raw"
    VALIDATED = "validated"
    CLEANED = "cleaned"
    TRANSFORMED = "transformed"
    FEATURE_ENGINEERED = "feature_engineered"
    TRAINING_READY = "training_ready"


class ProvenanceRecord(BaseModel):
    """Record of data provenance."""
    record_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    dataset_name: str
    data_source: DataSource
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    ingestion_timestamp: datetime = Field(default_factory=datetime.now)
    processing_stage: ProcessingStage = ProcessingStage.RAW
    
    # Data characteristics
    num_records: int = 0
    num_columns: int = 0
    file_size_bytes: Optional[int] = None
    data_hash: Optional[str] = None
    
    # Processing information
    processing_steps: List[str] = []
    parent_records: List[str] = []  # IDs of parent provenance records
    
    # Metadata
    version: str = "1.0"
    user: Optional[str] = None
    notes: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True


class LineageNode(BaseModel):
    """Node in data lineage graph."""
    record_id: str
    dataset_name: str
    data_source: str
    processing_stage: str
    timestamp: datetime
    children: List[str] = []  # IDs of child records


class ProvenanceTracker:
    """Tracker for data provenance and lineage."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize provenance tracker.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        self.metadata_dir = Path(self.settings.METADATA_PATH) / "provenance"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Provenance tracker initialized")
    
    def track_ingestion(
        self,
        dataset_name: str,
        data_source: DataSource,
        data: pd.DataFrame,
        source_file: Optional[Path] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProvenanceRecord:
        """
        Track data ingestion.
        
        Args:
            dataset_name: Name of the dataset
            data_source: Source of the data
            data: DataFrame being ingested
            source_file: Optional source file path
            source_url: Optional source URL
            metadata: Optional additional metadata
        
        Returns:
            ProvenanceRecord for the ingestion
        """
        logger.info(f"Tracking ingestion for {dataset_name} from {data_source}")
        
        # Calculate data hash
        data_hash = self._calculate_dataframe_hash(data)
        
        # Get file size if source file provided
        file_size = None
        if source_file and source_file.exists():
            file_size = source_file.stat().st_size
        
        # Create provenance record
        record = ProvenanceRecord(
            dataset_name=dataset_name,
            data_source=data_source,
            source_file=str(source_file) if source_file else None,
            source_url=source_url,
            processing_stage=ProcessingStage.RAW,
            num_records=len(data),
            num_columns=len(data.columns),
            file_size_bytes=file_size,
            data_hash=data_hash,
            metadata=metadata or {}
        )
        
        # Save record
        self._save_record(record)
        
        logger.info(f"Created provenance record: {record.record_id}")
        return record
    
    def track_processing(
        self,
        parent_record_id: str,
        dataset_name: str,
        processing_stage: ProcessingStage,
        data: pd.DataFrame,
        processing_steps: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProvenanceRecord:
        """
        Track data processing step.
        
        Args:
            parent_record_id: ID of parent provenance record
            dataset_name: Name of the dataset
            processing_stage: Current processing stage
            data: Processed DataFrame
            processing_steps: List of processing steps applied
            metadata: Optional additional metadata
        
        Returns:
            ProvenanceRecord for the processing step
        """
        logger.info(f"Tracking processing for {dataset_name} at stage {processing_stage}")
        
        # Load parent record to get data source
        parent_record = self._load_record(parent_record_id)
        if not parent_record:
            logger.warning(f"Parent record {parent_record_id} not found")
            data_source = DataSource.DERIVED
        else:
            data_source = DataSource(parent_record.data_source)
        
        # Calculate data hash
        data_hash = self._calculate_dataframe_hash(data)
        
        # Create provenance record
        record = ProvenanceRecord(
            dataset_name=dataset_name,
            data_source=data_source,
            processing_stage=processing_stage,
            num_records=len(data),
            num_columns=len(data.columns),
            data_hash=data_hash,
            processing_steps=processing_steps,
            parent_records=[parent_record_id],
            metadata=metadata or {}
        )
        
        # Save record
        self._save_record(record)
        
        logger.info(f"Created provenance record: {record.record_id}")
        return record
    
    def track_merge(
        self,
        parent_record_ids: List[str],
        dataset_name: str,
        data: pd.DataFrame,
        merge_description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProvenanceRecord:
        """
        Track data merge operation.
        
        Args:
            parent_record_ids: IDs of parent provenance records being merged
            dataset_name: Name of the merged dataset
            data: Merged DataFrame
            merge_description: Description of merge operation
            metadata: Optional additional metadata
        
        Returns:
            ProvenanceRecord for the merge
        """
        logger.info(f"Tracking merge for {dataset_name} from {len(parent_record_ids)} sources")
        
        # Calculate data hash
        data_hash = self._calculate_dataframe_hash(data)
        
        # Create provenance record
        record = ProvenanceRecord(
            dataset_name=dataset_name,
            data_source=DataSource.DERIVED,
            processing_stage=ProcessingStage.TRANSFORMED,
            num_records=len(data),
            num_columns=len(data.columns),
            data_hash=data_hash,
            processing_steps=[merge_description],
            parent_records=parent_record_ids,
            metadata=metadata or {}
        )
        
        # Save record
        self._save_record(record)
        
        logger.info(f"Created provenance record: {record.record_id}")
        return record
    
    def get_lineage(self, record_id: str) -> Dict[str, LineageNode]:
        """
        Get complete lineage for a provenance record.
        
        Args:
            record_id: ID of provenance record
        
        Returns:
            Dictionary mapping record IDs to LineageNodes
        """
        logger.info(f"Getting lineage for record {record_id}")
        
        lineage = {}
        self._build_lineage_recursive(record_id, lineage)
        
        logger.info(f"Built lineage with {len(lineage)} nodes")
        return lineage
    
    def _build_lineage_recursive(
        self,
        record_id: str,
        lineage: Dict[str, LineageNode]
    ):
        """Recursively build lineage graph."""
        if record_id in lineage:
            return  # Already processed
        
        # Load record
        record = self._load_record(record_id)
        if not record:
            logger.warning(f"Record {record_id} not found")
            return
        
        # Create lineage node
        node = LineageNode(
            record_id=record.record_id,
            dataset_name=record.dataset_name,
            data_source=record.data_source,
            processing_stage=record.processing_stage,
            timestamp=record.ingestion_timestamp
        )
        
        # Process parent records
        for parent_id in record.parent_records:
            node.children.append(parent_id)
            self._build_lineage_recursive(parent_id, lineage)
        
        lineage[record_id] = node
    
    def get_record(self, record_id: str) -> Optional[ProvenanceRecord]:
        """
        Get provenance record by ID.
        
        Args:
            record_id: ID of provenance record
        
        Returns:
            ProvenanceRecord or None if not found
        """
        return self._load_record(record_id)
    
    def list_records(
        self,
        data_source: Optional[DataSource] = None,
        processing_stage: Optional[ProcessingStage] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ProvenanceRecord]:
        """
        List provenance records with optional filters.
        
        Args:
            data_source: Optional filter by data source
            processing_stage: Optional filter by processing stage
            start_date: Optional filter by start date
            end_date: Optional filter by end date
        
        Returns:
            List of ProvenanceRecords matching filters
        """
        logger.info("Listing provenance records")
        
        records = []
        
        # Load all records
        for record_file in self.metadata_dir.glob("*.json"):
            try:
                record = self._load_record_from_file(record_file)
                
                # Apply filters
                if data_source and record.data_source != data_source:
                    continue
                if processing_stage and record.processing_stage != processing_stage:
                    continue
                if start_date and record.ingestion_timestamp < start_date:
                    continue
                if end_date and record.ingestion_timestamp > end_date:
                    continue
                
                records.append(record)
                
            except Exception as e:
                logger.error(f"Failed to load record from {record_file}: {e}")
        
        logger.info(f"Found {len(records)} matching records")
        return records
    
    def _calculate_dataframe_hash(self, data: pd.DataFrame) -> str:
        """Calculate hash of DataFrame for data integrity."""
        # Convert DataFrame to string representation and hash
        data_str = data.to_json(orient='records', date_format='iso')
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _save_record(self, record: ProvenanceRecord):
        """Save provenance record to file."""
        record_file = self.metadata_dir / f"{record.record_id}.json"
        
        with open(record_file, 'w') as f:
            json.dump(record.dict(), f, indent=2, default=str)
        
        logger.debug(f"Saved provenance record to {record_file}")
    
    def _load_record(self, record_id: str) -> Optional[ProvenanceRecord]:
        """Load provenance record from file."""
        record_file = self.metadata_dir / f"{record_id}.json"
        
        if not record_file.exists():
            return None
        
        return self._load_record_from_file(record_file)
    
    def _load_record_from_file(self, record_file: Path) -> ProvenanceRecord:
        """Load provenance record from file path."""
        with open(record_file, 'r') as f:
            data = json.load(f)
        
        # Convert timestamp strings back to datetime
        if 'ingestion_timestamp' in data:
            data['ingestion_timestamp'] = datetime.fromisoformat(data['ingestion_timestamp'])
        
        return ProvenanceRecord(**data)
    
    def export_lineage_graph(
        self,
        record_id: str,
        output_file: Path,
        format: str = 'json'
    ):
        """
        Export lineage graph to file.
        
        Args:
            record_id: ID of provenance record
            output_file: Output file path
            format: Export format ('json' or 'dot')
        """
        lineage = self.get_lineage(record_id)
        
        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(
                    {k: v.dict() for k, v in lineage.items()},
                    f,
                    indent=2,
                    default=str
                )
        elif format == 'dot':
            # Export as Graphviz DOT format
            with open(output_file, 'w') as f:
                f.write("digraph lineage {\n")
                f.write("  rankdir=LR;\n")
                
                for node_id, node in lineage.items():
                    label = f"{node.dataset_name}\\n{node.processing_stage}"
                    f.write(f'  "{node_id}" [label="{label}"];\n')
                    
                    for child_id in node.children:
                        f.write(f'  "{node_id}" -> "{child_id}";\n')
                
                f.write("}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported lineage graph to {output_file}")
