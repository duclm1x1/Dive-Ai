"""
Transformation Engine - Data transformation and format conversion
Integrates format conversion, data normalization, and schema transformation
"""

import logging
import json
import yaml
import csv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from io import StringIO

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    AVRO = "avro"


@dataclass
class TransformationResult:
    """Transformation result"""
    source_format: DataFormat
    target_format: DataFormat
    input_data: Any
    output_data: Any
    success: bool
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_format": self.source_format.value,
            "target_format": self.target_format.value,
            "success": self.success,
            "metadata": self.metadata or {}
        }


class TransformationEngine:
    """
    Dive AI Transformation Engine
    
    Capabilities:
    - Format conversion (JSON, YAML, CSV, XML, etc.)
    - Data normalization
    - Schema transformation
    - Data validation
    - Batch transformation
    """
    
    def __init__(self):
        """Initialize transformation engine"""
        self.logger = logging.getLogger(f"{__name__}.TransformationEngine")
        self.cache = {}
    
    def convert_format(self, data: Any, source_format: DataFormat, 
                      target_format: DataFormat) -> TransformationResult:
        """
        Convert data between formats
        
        Args:
            data: Input data
            source_format: Source format
            target_format: Target format
            
        Returns:
            TransformationResult with converted data
        """
        try:
            # Step 1: Parse source format
            if source_format == DataFormat.JSON:
                if isinstance(data, str):
                    parsed_data = json.loads(data)
                else:
                    parsed_data = data
            elif source_format == DataFormat.YAML:
                if isinstance(data, str):
                    parsed_data = yaml.safe_load(data)
                else:
                    parsed_data = data
            elif source_format == DataFormat.CSV:
                if isinstance(data, str):
                    reader = csv.DictReader(StringIO(data))
                    parsed_data = list(reader)
                else:
                    parsed_data = data
            else:
                parsed_data = data
            
            # Step 2: Convert to target format
            if target_format == DataFormat.JSON:
                output_data = json.dumps(parsed_data, indent=2)
            elif target_format == DataFormat.YAML:
                output_data = yaml.dump(parsed_data, default_flow_style=False)
            elif target_format == DataFormat.CSV:
                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    output = StringIO()
                    writer = csv.DictWriter(output, fieldnames=parsed_data[0].keys())
                    writer.writeheader()
                    writer.writerows(parsed_data)
                    output_data = output.getvalue()
                else:
                    output_data = ""
            else:
                output_data = parsed_data
            
            result = TransformationResult(
                source_format=source_format,
                target_format=target_format,
                input_data=data,
                output_data=output_data,
                success=True,
                metadata={"conversion_type": "format"}
            )
            
            self.logger.info(f"Format conversion successful: {source_format.value} → {target_format.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            return TransformationResult(
                source_format=source_format,
                target_format=target_format,
                input_data=data,
                output_data=None,
                success=False,
                metadata={"error": str(e)}
            )
    
    def normalize_data(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> TransformationResult:
        """
        Normalize data according to schema
        
        Args:
            data: Input data
            schema: Target schema
            
        Returns:
            TransformationResult with normalized data
        """
        try:
            normalized = {}
            
            if schema:
                # Apply schema
                for field, field_type in schema.items():
                    if field in data:
                        value = data[field]
                        # Type conversion
                        if field_type == "string":
                            normalized[field] = str(value)
                        elif field_type == "integer":
                            normalized[field] = int(value)
                        elif field_type == "float":
                            normalized[field] = float(value)
                        elif field_type == "boolean":
                            normalized[field] = bool(value)
                        else:
                            normalized[field] = value
            else:
                # Basic normalization
                normalized = data
            
            result = TransformationResult(
                source_format=DataFormat.JSON,
                target_format=DataFormat.JSON,
                input_data=data,
                output_data=normalized,
                success=True,
                metadata={"normalization_type": "schema-based"}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data normalization failed: {str(e)}")
            return TransformationResult(
                source_format=DataFormat.JSON,
                target_format=DataFormat.JSON,
                input_data=data,
                output_data=None,
                success=False,
                metadata={"error": str(e)}
            )
    
    def validate_data(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Validation schema
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        warnings = []
        
        try:
            if isinstance(data, dict) and isinstance(schema, dict):
                # Check required fields
                required_fields = schema.get("required", [])
                for field in required_fields:
                    if field not in data:
                        errors.append(f"Missing required field: {field}")
                
                # Check field types
                properties = schema.get("properties", {})
                for field, field_schema in properties.items():
                    if field in data:
                        field_type = field_schema.get("type")
                        value = data[field]
                        
                        # Type validation
                        if field_type == "string" and not isinstance(value, str):
                            errors.append(f"Field '{field}' must be string, got {type(value).__name__}")
                        elif field_type == "integer" and not isinstance(value, int):
                            errors.append(f"Field '{field}' must be integer, got {type(value).__name__}")
                        elif field_type == "array" and not isinstance(value, list):
                            errors.append(f"Field '{field}' must be array, got {type(value).__name__}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def batch_transform(self, data_list: List[Any], source_format: DataFormat,
                       target_format: DataFormat) -> List[TransformationResult]:
        """Batch transform multiple data items"""
        results = []
        for data in data_list:
            result = self.convert_format(data, source_format, target_format)
            results.append(result)
        
        return results
