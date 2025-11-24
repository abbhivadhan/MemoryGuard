"""Schema validation for biomedical datasets."""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class DataType(str, Enum):
    """Supported data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


class ColumnSchema(BaseModel):
    """Schema definition for a single column."""
    name: str
    data_type: DataType
    required: bool = False
    nullable: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    description: Optional[str] = None


class DatasetSchema(BaseModel):
    """Schema definition for a dataset."""
    name: str
    version: str
    columns: List[ColumnSchema]
    description: Optional[str] = None
    
    def get_column_names(self) -> List[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]
    
    def get_required_columns(self) -> List[str]:
        """Get list of required column names."""
        return [col.name for col in self.columns if col.required]


class ValidationError(BaseModel):
    """Validation error details."""
    column: str
    error_type: str
    message: str
    row_indices: Optional[List[int]] = None
    count: int = 0


class ValidationResult(BaseModel):
    """Result of schema validation."""
    valid: bool
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    total_rows: int
    valid_rows: int
    
    def add_error(self, error: ValidationError):
        """Add validation error."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: ValidationError):
        """Add validation warning."""
        self.warnings.append(warning)
    
    def get_summary(self) -> str:
        """Get validation summary."""
        summary = f"Validation Result: {'PASSED' if self.valid else 'FAILED'}\n"
        summary += f"Total rows: {self.total_rows}\n"
        summary += f"Valid rows: {self.valid_rows}\n"
        summary += f"Errors: {len(self.errors)}\n"
        summary += f"Warnings: {len(self.warnings)}\n"
        return summary


class SchemaValidator:
    """Validator for dataset schemas."""
    
    def __init__(self):
        """Initialize schema validator."""
        self.schemas = self._load_schemas()
        logger.info("Schema validator initialized")
    
    def _load_schemas(self) -> Dict[str, DatasetSchema]:
        """Load predefined schemas for each dataset."""
        schemas = {}
        
        # ADNI Cognitive Assessment Schema
        schemas['adni_cognitive'] = DatasetSchema(
            name='adni_cognitive',
            version='1.0',
            description='ADNI cognitive assessment data schema',
            columns=[
                ColumnSchema(name='patient_id', data_type=DataType.STRING, required=True, nullable=False),
                ColumnSchema(name='visit_date', data_type=DataType.DATE, required=True, nullable=False),
                ColumnSchema(name='mmse_score', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=30),
                ColumnSchema(name='adas_cog_score', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=70),
                ColumnSchema(name='cdr_global', data_type=DataType.FLOAT, nullable=True, allowed_values=[0, 0.5, 1, 2, 3]),
                ColumnSchema(name='cdr_sob', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=18),
                ColumnSchema(name='moca_score', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=30),
                ColumnSchema(name='data_source', data_type=DataType.STRING, required=True),
                ColumnSchema(name='ingestion_timestamp', data_type=DataType.DATETIME, required=True)
            ]
        )
        
        # ADNI CSF Biomarker Schema
        schemas['adni_biomarker'] = DatasetSchema(
            name='adni_biomarker',
            version='1.0',
            description='ADNI CSF biomarker data schema',
            columns=[
                ColumnSchema(name='patient_id', data_type=DataType.STRING, required=True, nullable=False),
                ColumnSchema(name='visit_date', data_type=DataType.DATE, required=True, nullable=False),
                ColumnSchema(name='csf_ab42', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=2000),
                ColumnSchema(name='csf_tau', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=1500),
                ColumnSchema(name='csf_ptau', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=200),
                ColumnSchema(name='ab42_tau_ratio', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='ptau_tau_ratio', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=1),
                ColumnSchema(name='data_source', data_type=DataType.STRING, required=True),
                ColumnSchema(name='ingestion_timestamp', data_type=DataType.DATETIME, required=True)
            ]
        )
        
        # OASIS MRI Schema
        schemas['oasis_mri'] = DatasetSchema(
            name='oasis_mri',
            version='1.0',
            description='OASIS MRI volumetric data schema',
            columns=[
                ColumnSchema(name='patient_id', data_type=DataType.STRING, required=True, nullable=False),
                ColumnSchema(name='visit_date', data_type=DataType.DATE, nullable=True),
                ColumnSchema(name='hippocampus_left', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='hippocampus_right', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='hippocampus_total', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='ventricle_volume', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='whole_brain_volume', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='icv', data_type=DataType.FLOAT, nullable=True, min_value=0),
                ColumnSchema(name='data_source', data_type=DataType.STRING, required=True),
                ColumnSchema(name='ingestion_timestamp', data_type=DataType.DATETIME, required=True)
            ]
        )
        
        # NACC Clinical Schema
        schemas['nacc_clinical'] = DatasetSchema(
            name='nacc_clinical',
            version='1.0',
            description='NACC clinical assessment data schema',
            columns=[
                ColumnSchema(name='patient_id', data_type=DataType.STRING, required=True, nullable=False),
                ColumnSchema(name='visit_date', data_type=DataType.DATE, required=True, nullable=False),
                ColumnSchema(name='visit_number', data_type=DataType.INTEGER, nullable=True, min_value=1),
                ColumnSchema(name='mmse_score', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=30),
                ColumnSchema(name='moca_score', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=30),
                ColumnSchema(name='cdr_global', data_type=DataType.FLOAT, nullable=True, allowed_values=[0, 0.5, 1, 2, 3]),
                ColumnSchema(name='cdr_sob', data_type=DataType.FLOAT, nullable=True, min_value=0, max_value=18),
                ColumnSchema(name='data_source', data_type=DataType.STRING, required=True),
                ColumnSchema(name='ingestion_timestamp', data_type=DataType.DATETIME, required=True)
            ]
        )
        
        return schemas
    
    def validate(
        self,
        data: pd.DataFrame,
        schema_name: str,
        strict: bool = False
    ) -> ValidationResult:
        """
        Validate data against schema.
        
        Args:
            data: DataFrame to validate
            schema_name: Name of schema to validate against
            strict: If True, fail on warnings
        
        Returns:
            ValidationResult with errors and warnings
        
        Raises:
            ValueError: If schema_name is not found
        """
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found. Available schemas: {list(self.schemas.keys())}")
        
        schema = self.schemas[schema_name]
        logger.info(f"Validating data against schema: {schema_name}")
        
        result = ValidationResult(
            valid=True,
            total_rows=len(data),
            valid_rows=len(data)
        )
        
        # Check for required columns
        missing_required = set(schema.get_required_columns()) - set(data.columns)
        if missing_required:
            result.add_error(ValidationError(
                column='',
                error_type='missing_required_columns',
                message=f"Missing required columns: {missing_required}",
                count=len(missing_required)
            ))
        
        # Check for extra columns (warning only)
        extra_columns = set(data.columns) - set(schema.get_column_names())
        if extra_columns:
            result.add_warning(ValidationError(
                column='',
                error_type='extra_columns',
                message=f"Extra columns not in schema: {extra_columns}",
                count=len(extra_columns)
            ))
        
        # Validate each column
        for col_schema in schema.columns:
            if col_schema.name not in data.columns:
                continue
            
            col_data = data[col_schema.name]
            
            # Check nullability
            if not col_schema.nullable:
                null_count = col_data.isna().sum()
                if null_count > 0:
                    null_indices = data[col_data.isna()].index.tolist()[:10]  # First 10
                    result.add_error(ValidationError(
                        column=col_schema.name,
                        error_type='null_values',
                        message=f"Column '{col_schema.name}' contains {null_count} null values but is not nullable",
                        row_indices=null_indices,
                        count=null_count
                    ))
            
            # Skip further validation for null values
            non_null_data = col_data.dropna()
            if non_null_data.empty:
                continue
            
            # Validate data type
            type_errors = self._validate_data_type(non_null_data, col_schema)
            if type_errors:
                result.add_error(type_errors)
            
            # Validate range
            if col_schema.min_value is not None or col_schema.max_value is not None:
                range_errors = self._validate_range(non_null_data, col_schema)
                if range_errors:
                    result.add_error(range_errors)
            
            # Validate allowed values
            if col_schema.allowed_values is not None:
                value_errors = self._validate_allowed_values(non_null_data, col_schema)
                if value_errors:
                    result.add_error(value_errors)
        
        # Calculate valid rows (rows without errors)
        if result.errors:
            # Estimate valid rows (this is approximate)
            error_rows = sum(e.count for e in result.errors if e.count > 0)
            result.valid_rows = max(0, result.total_rows - error_rows)
        
        # In strict mode, warnings become errors
        if strict and result.warnings:
            result.errors.extend(result.warnings)
            result.warnings = []
            result.valid = False
        
        logger.info(f"Validation complete: {result.get_summary()}")
        return result
    
    def _validate_data_type(
        self,
        data: pd.Series,
        col_schema: ColumnSchema
    ) -> Optional[ValidationError]:
        """Validate data type of column."""
        expected_type = col_schema.data_type
        
        try:
            if expected_type == DataType.INTEGER:
                # Check if values can be converted to int
                pd.to_numeric(data, errors='raise', downcast='integer')
            elif expected_type == DataType.FLOAT:
                # Check if values can be converted to float
                pd.to_numeric(data, errors='raise')
            elif expected_type in [DataType.DATE, DataType.DATETIME]:
                # Check if values can be converted to datetime
                pd.to_datetime(data, errors='raise')
            elif expected_type == DataType.BOOLEAN:
                # Check if values are boolean-like
                if not data.isin([True, False, 0, 1]).all():
                    raise ValueError("Invalid boolean values")
            
            return None
            
        except Exception as e:
            invalid_count = len(data)
            return ValidationError(
                column=col_schema.name,
                error_type='invalid_data_type',
                message=f"Column '{col_schema.name}' has invalid {expected_type.value} values",
                count=invalid_count
            )
    
    def _validate_range(
        self,
        data: pd.Series,
        col_schema: ColumnSchema
    ) -> Optional[ValidationError]:
        """Validate value range of column."""
        numeric_data = pd.to_numeric(data, errors='coerce')
        
        out_of_range = pd.Series([False] * len(numeric_data), index=numeric_data.index)
        
        if col_schema.min_value is not None:
            out_of_range |= numeric_data < col_schema.min_value
        
        if col_schema.max_value is not None:
            out_of_range |= numeric_data > col_schema.max_value
        
        if out_of_range.any():
            count = out_of_range.sum()
            indices = data[out_of_range].index.tolist()[:10]  # First 10
            return ValidationError(
                column=col_schema.name,
                error_type='out_of_range',
                message=f"Column '{col_schema.name}' has {count} values outside range [{col_schema.min_value}, {col_schema.max_value}]",
                row_indices=indices,
                count=count
            )
        
        return None
    
    def _validate_allowed_values(
        self,
        data: pd.Series,
        col_schema: ColumnSchema
    ) -> Optional[ValidationError]:
        """Validate allowed values of column."""
        invalid = ~data.isin(col_schema.allowed_values)
        
        if invalid.any():
            count = invalid.sum()
            indices = data[invalid].index.tolist()[:10]  # First 10
            return ValidationError(
                column=col_schema.name,
                error_type='invalid_value',
                message=f"Column '{col_schema.name}' has {count} values not in allowed set: {col_schema.allowed_values}",
                row_indices=indices,
                count=count
            )
        
        return None
    
    def log_validation_errors(self, result: ValidationResult):
        """Log validation errors and warnings."""
        if result.errors:
            logger.error(f"Validation failed with {len(result.errors)} errors:")
            for error in result.errors:
                logger.error(f"  - {error.error_type}: {error.message}")
        
        if result.warnings:
            logger.warning(f"Validation completed with {len(result.warnings)} warnings:")
            for warning in result.warnings:
                logger.warning(f"  - {warning.error_type}: {warning.message}")
        
        if not result.errors and not result.warnings:
            logger.info("Validation passed with no errors or warnings")
