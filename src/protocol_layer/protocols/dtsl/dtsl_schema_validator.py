"""
DTSL Schema Validator
Week 17 Day 4: Schema Validation for Digital Twin Swarm Language

This module provides JSON schema validation for DTSL definitions, ensuring
that twin definitions, swarm definitions, and DTSL files conform to the
standardized schema before execution.

Features:
1. JSON schema definitions for twin and swarm structures
2. Comprehensive validation with detailed error messages
3. Version compatibility checking
4. Extension mechanism for custom validation rules
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError

logger = logging.getLogger(__name__)


# =============================================================================
# DTSL Schema Definitions
# =============================================================================

DTSL_TWIN_DEFINITION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "DTSL Twin Definition Schema",
    "description": "Schema for defining a digital twin type in DTSL",
    "required": ["type", "version", "config"],
    "properties": {
        "type": {
            "type": "string",
            "description": "Type identifier for this twin (e.g., 'sensor_twin', 'machine_twin')",
            "minLength": 1,
            "maxLength": 100,
            "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$"
        },
        "version": {
            "type": "string",
            "description": "Version of the twin definition (semver format)",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        },
        "description": {
            "type": "string",
            "description": "Human-readable description of the twin type"
        },
        "config": {
            "type": "object",
            "description": "Configuration parameters for the twin",
            "properties": {
                "update_interval": {
                    "type": "number",
                    "description": "Update interval in seconds",
                    "minimum": 0
                },
                "data_retention_days": {
                    "type": "integer",
                    "description": "How long to retain twin data (days)",
                    "minimum": 1
                },
                "sync_mode": {
                    "type": "string",
                    "description": "Synchronization mode with physical twin",
                    "enum": ["real-time", "periodic", "on-demand", "event-driven"]
                }
            }
        },
        "capabilities": {
            "type": "array",
            "description": "Capabilities this twin type provides",
            "items": {
                "type": "string",
                "minLength": 1
            },
            "uniqueItems": True
        },
        "initial_state": {
            "type": "object",
            "description": "Initial state values for new twin instances"
        },
        "sensors": {
            "type": "array",
            "description": "Sensor definitions for this twin",
            "items": {
                "type": "object",
                "required": ["sensor_id", "sensor_type"],
                "properties": {
                    "sensor_id": {"type": "string"},
                    "sensor_type": {"type": "string"},
                    "unit": {"type": "string"},
                    "min_value": {"type": "number"},
                    "max_value": {"type": "number"},
                    "sample_rate_hz": {"type": "number", "minimum": 0}
                }
            }
        },
        "actuators": {
            "type": "array",
            "description": "Actuator definitions for this twin",
            "items": {
                "type": "object",
                "required": ["actuator_id", "actuator_type"],
                "properties": {
                    "actuator_id": {"type": "string"},
                    "actuator_type": {"type": "string"},
                    "command_types": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "relationships": {
            "type": "object",
            "description": "Relationship definitions with other twins",
            "properties": {
                "parent": {
                    "type": "object",
                    "properties": {
                        "twin_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "cardinality": {
                            "type": "string",
                            "enum": ["one", "many"]
                        }
                    }
                },
                "children": {
                    "type": "object",
                    "properties": {
                        "twin_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "cardinality": {
                            "type": "string",
                            "enum": ["one", "many"]
                        }
                    }
                },
                "peers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "twin_type": {"type": "string"},
                            "relationship_type": {"type": "string"}
                        }
                    }
                }
            }
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata for the twin definition"
        }
    }
}


DTSL_SWARM_DEFINITION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "DTSL Swarm Definition Schema",
    "description": "Schema for defining a digital twin swarm in DTSL",
    "required": ["swarm_id", "version", "twins"],
    "properties": {
        "swarm_id": {
            "type": "string",
            "description": "Unique identifier for this swarm",
            "minLength": 1,
            "maxLength": 100,
            "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$"
        },
        "version": {
            "type": "string",
            "description": "Version of the swarm definition (semver format)",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
        },
        "description": {
            "type": "string",
            "description": "Human-readable description of the swarm"
        },
        "twins": {
            "type": "array",
            "description": "Twin instances in this swarm",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique ID for this twin instance (auto-generated if not provided)"
                    },
                    "type": {
                        "type": "string",
                        "description": "Twin type (must reference a loaded twin definition)"
                    },
                    "config": {
                        "type": "object",
                        "description": "Instance-specific configuration overrides"
                    },
                    "initial_state": {
                        "type": "object",
                        "description": "Instance-specific initial state overrides"
                    },
                    "capabilities": {
                        "type": "array",
                        "description": "Additional capabilities for this instance",
                        "items": {"type": "string"}
                    },
                    "relationships": {
                        "type": "array",
                        "description": "Relationships with other twins in the swarm",
                        "items": {
                            "type": "object",
                            "required": ["target_twin_id", "relationship_type"],
                            "properties": {
                                "target_twin_id": {"type": "string"},
                                "relationship_type": {
                                    "type": "string",
                                    "enum": ["parent", "child", "peer", "depends_on", "controls"]
                                },
                                "metadata": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "coordination": {
            "type": "object",
            "description": "Swarm coordination configuration",
            "properties": {
                "strategy": {
                    "type": "string",
                    "description": "Coordination strategy",
                    "enum": ["centralized", "distributed", "hierarchical", "consensus"]
                },
                "leader_election": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "algorithm": {
                            "type": "string",
                            "enum": ["bully", "ring", "raft", "paxos"]
                        }
                    }
                },
                "consensus_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Threshold for consensus decisions (0.0-1.0)"
                }
            }
        },
        "networking": {
            "type": "object",
            "description": "Network configuration for swarm communication",
            "properties": {
                "topology": {
                    "type": "string",
                    "enum": ["mesh", "star", "ring", "tree", "hybrid"]
                },
                "protocol": {
                    "type": "string",
                    "enum": ["mcp", "a2a", "custom"]
                },
                "security": {
                    "type": "object",
                    "properties": {
                        "encryption": {"type": "boolean"},
                        "authentication": {"type": "boolean"},
                        "authorization": {"type": "boolean"}
                    }
                }
            }
        },
        "scaling": {
            "type": "object",
            "description": "Auto-scaling configuration",
            "properties": {
                "enabled": {"type": "boolean"},
                "min_twins": {
                    "type": "integer",
                    "minimum": 1
                },
                "max_twins": {
                    "type": "integer",
                    "minimum": 1
                },
                "scale_up_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "scale_down_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            }
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata for the swarm"
        }
    }
}


DTSL_FILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "DTSL File Schema",
    "description": "Schema for DTSL configuration files (YAML or JSON)",
    "properties": {
        "dtsl_version": {
            "type": "string",
            "description": "DTSL language version",
            "pattern": "^[0-9]+\\.[0-9]+$"
        },
        "twin_definitions": {
            "type": "array",
            "description": "Array of twin type definitions",
            "items": DTSL_TWIN_DEFINITION_SCHEMA
        },
        "swarm_definitions": {
            "type": "array",
            "description": "Array of swarm definitions",
            "items": DTSL_SWARM_DEFINITION_SCHEMA
        },
        "imports": {
            "type": "array",
            "description": "External DTSL files to import",
            "items": {
                "type": "string",
                "description": "File path or URL to import"
            }
        }
    },
    "anyOf": [
        {"required": ["twin_definitions"]},
        {"required": ["swarm_definitions"]},
        {"required": ["imports"]}
    ]
}


# =============================================================================
# Validation Functions
# =============================================================================

class DTSLValidationError(Exception):
    """Exception raised when DTSL validation fails."""
    def __init__(self, message: str, errors: List[str]):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class DTSLSchemaValidator:
    """
    Validates DTSL definitions against JSON schemas.
    """

    def __init__(self):
        """Initialize the DTSL schema validator."""
        self.twin_validator = Draft7Validator(DTSL_TWIN_DEFINITION_SCHEMA)
        self.swarm_validator = Draft7Validator(DTSL_SWARM_DEFINITION_SCHEMA)
        self.file_validator = Draft7Validator(DTSL_FILE_SCHEMA)

        logger.info("DTSL Schema Validator initialized")

    def validate_twin_definition(
        self,
        definition: Dict[str, Any],
        raise_on_error: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate a twin definition against the DTSL twin schema.

        Args:
            definition: Twin definition to validate
            raise_on_error: If True, raise DTSLValidationError on validation failure

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            DTSLValidationError: If validation fails and raise_on_error is True
        """
        errors = []

        try:
            # Validate against JSON schema
            self.twin_validator.validate(definition)

            # Additional semantic validations
            errors.extend(self._validate_twin_semantics(definition))

            if errors and raise_on_error:
                raise DTSLValidationError(
                    f"Twin definition validation failed for type '{definition.get('type', 'unknown')}'",
                    errors
                )

            return len(errors) == 0, errors

        except ValidationError as e:
            error_msg = f"Schema validation error: {e.message} at {'.'.join(str(p) for p in e.path)}"
            errors.append(error_msg)

            if raise_on_error:
                raise DTSLValidationError(
                    f"Twin definition validation failed",
                    errors
                )

            return False, errors

    def validate_swarm_definition(
        self,
        definition: Dict[str, Any],
        raise_on_error: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate a swarm definition against the DTSL swarm schema.

        Args:
            definition: Swarm definition to validate
            raise_on_error: If True, raise DTSLValidationError on validation failure

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            DTSLValidationError: If validation fails and raise_on_error is True
        """
        errors = []

        try:
            # Validate against JSON schema
            self.swarm_validator.validate(definition)

            # Additional semantic validations
            errors.extend(self._validate_swarm_semantics(definition))

            if errors and raise_on_error:
                raise DTSLValidationError(
                    f"Swarm definition validation failed for swarm '{definition.get('swarm_id', 'unknown')}'",
                    errors
                )

            return len(errors) == 0, errors

        except ValidationError as e:
            error_msg = f"Schema validation error: {e.message} at {'.'.join(str(p) for p in e.path)}"
            errors.append(error_msg)

            if raise_on_error:
                raise DTSLValidationError(
                    f"Swarm definition validation failed",
                    errors
                )

            return False, errors

    def validate_dtsl_file(
        self,
        content: Dict[str, Any],
        raise_on_error: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate a DTSL file content against the DTSL file schema.

        Args:
            content: Parsed DTSL file content
            raise_on_error: If True, raise DTSLValidationError on validation failure

        Returns:
            Tuple of (is_valid, error_messages)

        Raises:
            DTSLValidationError: If validation fails and raise_on_error is True
        """
        errors = []

        try:
            # Validate against JSON schema
            self.file_validator.validate(content)

            # Validate nested twin definitions
            for twin_def in content.get("twin_definitions", []):
                is_valid, twin_errors = self.validate_twin_definition(
                    twin_def,
                    raise_on_error=False
                )
                if not is_valid:
                    errors.extend([f"Twin '{twin_def.get('type')}': {err}" for err in twin_errors])

            # Validate nested swarm definitions
            for swarm_def in content.get("swarm_definitions", []):
                is_valid, swarm_errors = self.validate_swarm_definition(
                    swarm_def,
                    raise_on_error=False
                )
                if not is_valid:
                    errors.extend([f"Swarm '{swarm_def.get('swarm_id')}': {err}" for err in swarm_errors])

            if errors and raise_on_error:
                raise DTSLValidationError(
                    "DTSL file validation failed",
                    errors
                )

            return len(errors) == 0, errors

        except ValidationError as e:
            error_msg = f"Schema validation error: {e.message} at {'.'.join(str(p) for p in e.path)}"
            errors.append(error_msg)

            if raise_on_error:
                raise DTSLValidationError(
                    "DTSL file validation failed",
                    errors
                )

            return False, errors

    def _validate_twin_semantics(self, definition: Dict[str, Any]) -> List[str]:
        """
        Perform semantic validation on twin definition beyond schema validation.

        Args:
            definition: Twin definition to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check for sensor ID uniqueness
        sensors = definition.get("sensors", [])
        sensor_ids = [s.get("sensor_id") for s in sensors]
        if len(sensor_ids) != len(set(sensor_ids)):
            errors.append("Duplicate sensor IDs found in twin definition")

        # Check for actuator ID uniqueness
        actuators = definition.get("actuators", [])
        actuator_ids = [a.get("actuator_id") for a in actuators]
        if len(actuator_ids) != len(set(actuator_ids)):
            errors.append("Duplicate actuator IDs found in twin definition")

        # Validate sensor ranges
        for sensor in sensors:
            if "min_value" in sensor and "max_value" in sensor:
                if sensor["min_value"] >= sensor["max_value"]:
                    errors.append(
                        f"Sensor '{sensor.get('sensor_id')}': min_value must be less than max_value"
                    )

        return errors

    def _validate_swarm_semantics(self, definition: Dict[str, Any]) -> List[str]:
        """
        Perform semantic validation on swarm definition beyond schema validation.

        Args:
            definition: Swarm definition to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        twins = definition.get("twins", [])

        # Check for twin ID uniqueness
        twin_ids = [t.get("id") for t in twins if "id" in t]
        if len(twin_ids) != len(set(twin_ids)):
            errors.append("Duplicate twin IDs found in swarm definition")

        # Validate relationship references
        all_twin_ids = set(twin_ids)
        for i, twin in enumerate(twins):
            relationships = twin.get("relationships", [])
            for rel in relationships:
                target_id = rel.get("target_twin_id")
                if target_id and target_id not in all_twin_ids:
                    errors.append(
                        f"Twin at index {i}: relationship references unknown twin '{target_id}'"
                    )

        # Validate scaling configuration
        scaling = definition.get("scaling", {})
        if scaling.get("enabled"):
            min_twins = scaling.get("min_twins", 1)
            max_twins = scaling.get("max_twins", 1)

            if min_twins > max_twins:
                errors.append("Scaling: min_twins cannot be greater than max_twins")

            if len(twins) < min_twins:
                errors.append(
                    f"Scaling: current twin count ({len(twins)}) is less than min_twins ({min_twins})"
                )

        return errors


# =============================================================================
# Singleton Instance
# =============================================================================

_dtsl_schema_validator: Optional[DTSLSchemaValidator] = None


def get_dtsl_schema_validator() -> DTSLSchemaValidator:
    """Get singleton instance of DTSL schema validator."""
    global _dtsl_schema_validator

    if _dtsl_schema_validator is None:
        _dtsl_schema_validator = DTSLSchemaValidator()

    return _dtsl_schema_validator
