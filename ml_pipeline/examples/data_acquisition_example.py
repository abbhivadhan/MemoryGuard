"""Example script demonstrating data acquisition functionality."""

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ml_pipeline.data_ingestion import DataAcquisitionService
from ml_pipeline.config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main example function."""
    logger.info("Starting data acquisition example")
    
    # Initialize settings
    settings = Settings()
    
    # Initialize data acquisition service
    service = DataAcquisitionService(settings)
    
    # Example 1: Acquire ADNI cognitive assessment data
    logger.info("\n=== Example 1: Acquire ADNI Cognitive Data ===")
    adni_data = service.acquire_adni_data(
        data_types=['cognitive'],
        validate=True
    )
    
    if adni_data['cognitive'].empty:
        logger.info("No ADNI cognitive data available (expected for demo)")
    else:
        logger.info(f"Loaded {len(adni_data['cognitive'])} ADNI cognitive records")
        logger.info(f"Columns: {list(adni_data['cognitive'].columns)}")
    
    # Example 2: Acquire OASIS data
    logger.info("\n=== Example 2: Acquire OASIS Data ===")
    oasis_data = service.acquire_oasis_data(
        version="OASIS-3",
        validate=True
    )
    
    for data_type, df in oasis_data.items():
        if df.empty:
            logger.info(f"No OASIS {data_type} data available (expected for demo)")
        else:
            logger.info(f"Loaded {len(df)} OASIS {data_type} records")
    
    # Example 3: Acquire NACC data
    logger.info("\n=== Example 3: Acquire NACC Data ===")
    nacc_data = service.acquire_nacc_data(
        modules=['clinical', 'medical_history'],
        validate=True
    )
    
    for module, df in nacc_data.items():
        if df.empty:
            logger.info(f"No NACC {module} data available (expected for demo)")
        else:
            logger.info(f"Loaded {len(df)} NACC {module} records")
    
    # Example 4: Get data summary
    logger.info("\n=== Example 4: Data Summary ===")
    all_data = {
        'adni': adni_data,
        'oasis': oasis_data,
        'nacc': nacc_data
    }
    
    summary = service.get_data_summary(all_data)
    logger.info(f"\nData Summary:\n{summary.to_string()}")
    
    # Example 5: List provenance records
    logger.info("\n=== Example 5: Provenance Records ===")
    provenance_records = service.provenance_tracker.list_records()
    logger.info(f"Found {len(provenance_records)} provenance records")
    
    for record in provenance_records[:5]:  # Show first 5
        logger.info(f"  - {record.record_id}: {record.dataset_name} ({record.data_source}) - {record.num_records} records")
    
    logger.info("\nData acquisition example completed successfully!")


if __name__ == "__main__":
    main()
