# DTSL Schema Validation

**Week 17 Day 4: Schema Validation for Digital Twin Swarm Language**

This document describes the schema validation system for DTSL (Digital Twin Swarm Language), ensuring that twin definitions, swarm definitions, and DTSL files conform to standardized schemas before execution.

## 📋 Overview

The DTSL schema validation system provides:

1. **JSON Schema validation** for twin and swarm structures
2. **Semantic validation** beyond basic schema checks
3. **Detailed error reporting** for debugging
4. **Version compatibility** checking
5. **Extension mechanism** for custom validation rules

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  DTSL Handler (dtsl_handler.py)                                 │
│  ├─ load_twin_definition()     ─────┐                           │
│  ├─ load_swarm_definition()    ─────┼─→ Validates before load   │
│  └─ parse_dtsl_file()          ─────┘                           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│  DTSL Schema Validator (dtsl_schema_validator.py)               │
│  ├─ DTSL_TWIN_DEFINITION_SCHEMA (JSON Schema)                   │
│  ├─ DTSL_SWARM_DEFINITION_SCHEMA (JSON Schema)                  │
│  ├─ DTSL_FILE_SCHEMA (JSON Schema)                              │
│  │                                                               │
│  ├─ validate_twin_definition()    ──→ Schema + Semantic checks  │
│  ├─ validate_swarm_definition()   ──→ Schema + Semantic checks  │
│  └─ validate_dtsl_file()          ──→ Schema + Nested checks    │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Resolved TODOs

### 1. Line 153: Twin Definition Validation

**Original TODO:**
```python
# TODO: Add validation against a DTSL schema
```

**Solution:**
```python
from .dtsl_schema_validator import get_dtsl_schema_validator, DTSLValidationError

validator = get_dtsl_schema_validator()

# Ensure 'type' field matches the twin_type parameter
if "type" not in definition:
    definition["type"] = twin_type

# Validate the definition
is_valid, errors = validator.validate_twin_definition(definition, raise_on_error=False)

if not is_valid:
    self.logger.error(f"Twin definition validation failed for '{twin_type}':")
    for error in errors:
        self.logger.error(f"  - {error}")
    return False
```

### 2. Line 160: Swarm Definition Validation

**Original TODO:**
```python
# TODO: Add validation against a DTSL schema
```

**Solution:**
```python
from .dtsl_schema_validator import get_dtsl_schema_validator, DTSLValidationError

validator = get_dtsl_schema_validator()

# Ensure 'swarm_id' field matches the parameter
if "swarm_id" not in definition:
    definition["swarm_id"] = swarm_id

# Validate the definition
is_valid, errors = validator.validate_swarm_definition(definition, raise_on_error=False)

if not is_valid:
    self.logger.error(f"Swarm definition validation failed for '{swarm_id}':")
    for error in errors:
        self.logger.error(f"  - {error}")
    return False
```

### 3. Line 179: DTSL File Validation

**Original TODO:**
```python
# TODO: Validate content against DTSL schema
```

**Solution:**
```python
from .dtsl_schema_validator import get_dtsl_schema_validator, DTSLValidationError

validator = get_dtsl_schema_validator()

is_valid, errors = validator.validate_dtsl_file(content, raise_on_error=False)

if not is_valid:
    self.logger.error(f"DTSL file validation failed for '{file_path}':")
    for error in errors:
        self.logger.error(f"  - {error}")
    return None

self.logger.info(f"Successfully parsed and validated DTSL file: {file_path}")
```

## 📚 Schema Definitions

### Twin Definition Schema

**Required Fields:**
- `type`: Twin type identifier (pattern: `^[a-zA-Z][a-zA-Z0-9_]*$`)
- `version`: Semver version (pattern: `^[0-9]+\.[0-9]+\.[0-9]+$`)
- `config`: Configuration object

**Optional Fields:**
- `description`: Human-readable description
- `capabilities`: Array of capability strings
- `initial_state`: Initial state object
- `sensors`: Array of sensor definitions
- `actuators`: Array of actuator definitions
- `relationships`: Relationship definitions (parent, children, peers)
- `metadata`: Additional metadata

**Example:**
```yaml
type: sensor_twin
version: 1.0.0
description: Temperature sensor digital twin
config:
  update_interval: 1.0
  sync_mode: real-time
capabilities:
  - temperature_monitoring
  - alert_generation
sensors:
  - sensor_id: temp_01
    sensor_type: temperature
    unit: celsius
    min_value: -40.0
    max_value: 125.0
    sample_rate_hz: 1.0
initial_state:
  temperature: 20.0
  status: active
```

### Swarm Definition Schema

**Required Fields:**
- `swarm_id`: Unique swarm identifier (pattern: `^[a-zA-Z][a-zA-Z0-9_-]*$`)
- `version`: Semver version (pattern: `^[0-9]+\.[0-9]+\.[0-9]+$`)
- `twins`: Array of twin instances (minimum 1)

**Optional Fields:**
- `description`: Human-readable description
- `coordination`: Coordination configuration (strategy, leader election, consensus)
- `networking`: Network configuration (topology, protocol, security)
- `scaling`: Auto-scaling configuration
- `metadata`: Additional metadata

**Example:**
```yaml
swarm_id: factory_floor_swarm
version: 1.0.0
description: Digital twin swarm for factory floor monitoring
twins:
  - id: temp_sensor_01
    type: sensor_twin
    initial_state:
      location: zone_a
  - id: temp_sensor_02
    type: sensor_twin
    initial_state:
      location: zone_b
    relationships:
      - target_twin_id: temp_sensor_01
        relationship_type: peer
coordination:
  strategy: distributed
  consensus_threshold: 0.67
networking:
  topology: mesh
  protocol: mcp
  security:
    encryption: true
    authentication: true
scaling:
  enabled: true
  min_twins: 2
  max_twins: 10
```

### DTSL File Schema

**Optional Fields:**
- `dtsl_version`: DTSL language version (pattern: `^[0-9]+\.[0-9]+$`)
- `twin_definitions`: Array of twin definitions
- `swarm_definitions`: Array of swarm definitions
- `imports`: Array of file paths/URLs to import

**At least one of these required:**
- `twin_definitions`
- `swarm_definitions`
- `imports`

**Example:**
```yaml
dtsl_version: "1.0"
twin_definitions:
  - type: sensor_twin
    version: 1.0.0
    config: {...}
swarm_definitions:
  - swarm_id: factory_swarm
    version: 1.0.0
    twins: [...]
imports:
  - ./common_twins.yaml
  - ./network_config.yaml
```

## 🔍 Validation Types

### 1. Schema Validation

**JSON Schema (Draft 7)** validates:
- Required fields
- Field types (string, number, object, array, etc.)
- String patterns (regex)
- Number ranges (minimum, maximum)
- Array constraints (minItems, uniqueItems)
- Enum values

### 2. Semantic Validation

**Beyond schema**, semantic validation checks:

**For Twin Definitions:**
- Sensor ID uniqueness
- Actuator ID uniqueness
- Sensor value ranges (min < max)

**For Swarm Definitions:**
- Twin ID uniqueness
- Relationship target validation (must reference existing twin)
- Scaling configuration (min_twins ≤ max_twins)
- Twin count vs. min_twins requirement

**Example Semantic Error:**
```python
# Invalid: min_value >= max_value
sensors:
  - sensor_id: temp_01
    sensor_type: temperature
    min_value: 100.0
    max_value: 50.0  # ERROR: min must be < max
```

### 3. Nested Validation

**DTSL files** are validated recursively:
1. File schema validation
2. Each twin definition validated
3. Each swarm definition validated
4. Nested errors reported with context

**Example Error Output:**
```
DTSL file validation failed for 'factory.yaml':
  - Twin 'sensor_twin': Schema validation error: 'version' is a required property at type
  - Swarm 'factory_swarm': Duplicate twin IDs found in swarm definition
  - Twin 'motor_twin': Sensor 'vibration_01': min_value must be less than max_value
```

## 🚀 Usage Examples

### Example 1: Validate Twin Definition

```python
from dtsl_schema_validator import get_dtsl_schema_validator, DTSLValidationError

validator = get_dtsl_schema_validator()

twin_def = {
    "type": "sensor_twin",
    "version": "1.0.0",
    "config": {
        "update_interval": 1.0
    },
    "sensors": [
        {
            "sensor_id": "temp_01",
            "sensor_type": "temperature",
            "unit": "celsius",
            "min_value": -40.0,
            "max_value": 125.0
        }
    ]
}

try:
    is_valid, errors = validator.validate_twin_definition(twin_def)
    if is_valid:
        print("Twin definition is valid!")
    else:
        print(f"Validation errors: {errors}")
except DTSLValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

### Example 2: Validate Swarm Definition

```python
swarm_def = {
    "swarm_id": "test_swarm",
    "version": "1.0.0",
    "twins": [
        {
            "id": "twin_01",
            "type": "sensor_twin",
            "config": {}
        },
        {
            "id": "twin_02",
            "type": "sensor_twin",
            "config": {},
            "relationships": [
                {
                    "target_twin_id": "twin_01",
                    "relationship_type": "peer"
                }
            ]
        }
    ],
    "coordination": {
        "strategy": "distributed"
    }
}

is_valid, errors = validator.validate_swarm_definition(swarm_def, raise_on_error=False)
print(f"Valid: {is_valid}")
if errors:
    print(f"Errors: {errors}")
```

### Example 3: Validate DTSL File

```python
from dtsl_handler import DTSLHandler

handler = DTSLHandler()

# Parse and validate in one step
content = handler.parse_dtsl_file("factory_twins.yaml")

if content:
    print("File is valid and loaded!")
    # Load twin definitions
    for twin_def in content.get("twin_definitions", []):
        handler.load_twin_definition(twin_def["type"], twin_def)
    # Load swarm definitions
    for swarm_def in content.get("swarm_definitions", []):
        handler.load_swarm_definition(swarm_def["swarm_id"], swarm_def)
else:
    print("File validation failed - check logs for details")
```

### Example 4: Handle Validation Errors

```python
try:
    validator.validate_twin_definition(
        invalid_twin_def,
        raise_on_error=True  # Raise exception on error
    )
except DTSLValidationError as e:
    # Custom error handling
    log_validation_error(e.message, e.errors)
    send_alert_to_admin(e)
    # Optionally: attempt auto-fix
    fixed_def = auto_fix_twin_definition(invalid_twin_def, e.errors)
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from dtsl_schema_validator import DTSLSchemaValidator, DTSLValidationError

@pytest.fixture
def validator():
    return DTSLSchemaValidator()

def test_valid_twin_definition(validator):
    valid_twin = {
        "type": "test_twin",
        "version": "1.0.0",
        "config": {}
    }
    is_valid, errors = validator.validate_twin_definition(valid_twin)
    assert is_valid
    assert len(errors) == 0

def test_invalid_twin_missing_type(validator):
    invalid_twin = {
        "version": "1.0.0",
        "config": {}
    }
    is_valid, errors = validator.validate_twin_definition(
        invalid_twin,
        raise_on_error=False
    )
    assert not is_valid
    assert any("'type' is a required property" in e for e in errors)

def test_sensor_range_validation(validator):
    twin_with_invalid_sensor = {
        "type": "sensor_twin",
        "version": "1.0.0",
        "config": {},
        "sensors": [
            {
                "sensor_id": "temp_01",
                "sensor_type": "temperature",
                "min_value": 100.0,
                "max_value": 50.0  # Invalid: min > max
            }
        ]
    }
    is_valid, errors = validator.validate_twin_definition(twin_with_invalid_sensor)
    assert not is_valid
    assert any("min_value must be less than max_value" in e for e in errors)

def test_duplicate_sensor_ids(validator):
    twin_with_duplicate_sensors = {
        "type": "sensor_twin",
        "version": "1.0.0",
        "config": {},
        "sensors": [
            {"sensor_id": "temp_01", "sensor_type": "temperature"},
            {"sensor_id": "temp_01", "sensor_type": "temperature"}  # Duplicate
        ]
    }
    is_valid, errors = validator.validate_twin_definition(twin_with_duplicate_sensors)
    assert not is_valid
    assert any("Duplicate sensor IDs" in e for e in errors)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_dtsl_handler_with_validation():
    from dtsl_handler import DTSLHandler

    handler = DTSLHandler()

    # Valid twin definition
    valid_twin = {
        "type": "test_twin",
        "version": "1.0.0",
        "config": {"update_interval": 1.0}
    }

    # Should succeed
    result = handler.load_twin_definition("test_twin", valid_twin)
    assert result == True
    assert "test_twin" in handler.twin_definitions

    # Invalid twin definition
    invalid_twin = {
        # Missing 'version' field
        "type": "invalid_twin",
        "config": {}
    }

    # Should fail
    result = handler.load_twin_definition("invalid_twin", invalid_twin)
    assert result == False
    assert "invalid_twin" not in handler.twin_definitions
```

## 📊 Error Messages

### Schema Validation Errors

```
Schema validation error: 'version' is a required property at type
```

```
Schema validation error: '1.0' does not match '^[0-9]+\\.[0-9]+\\.[0-9]+$' at version
```

```
Schema validation error: 'unknown_strategy' is not one of ['centralized', 'distributed', 'hierarchical', 'consensus'] at coordination.strategy
```

### Semantic Validation Errors

```
Duplicate sensor IDs found in twin definition
```

```
Sensor 'temp_01': min_value must be less than max_value
```

```
Twin at index 2: relationship references unknown twin 'nonexistent_twin'
```

```
Scaling: min_twins cannot be greater than max_twins
```

## 🔐 Security Considerations

1. **Schema Injection**: Validate that user-provided schemas don't override core schemas
2. **DoS via Complexity**: Limit recursion depth for nested definitions
3. **File Path Traversal**: Sanitize file paths in `imports` field
4. **Resource Exhaustion**: Limit max size of DTSL files
5. **Type Confusion**: Strict type checking in schema validation

## 🚧 Future Enhancements

### Phase 2 (Week 18+)

- [ ] Custom validation rules via plugins
- [ ] Schema versioning and migration
- [ ] Performance optimization for large swarms
- [ ] Validation caching for repeated definitions
- [ ] Auto-fix suggestions for common errors

### Phase 3 (Week 20+)

- [ ] Visual schema editor
- [ ] Schema generation from existing twins
- [ ] Validation metrics and analytics
- [ ] Integration with CI/CD pipelines
- [ ] Real-time validation during editing

## 📝 Changelog

### Week 17 Day 4 (2025-11-18)
- ✅ Created `dtsl_schema_validator.py` (650+ LOC)
- ✅ Implemented JSON Schema validation (Draft 7)
- ✅ Added semantic validation for twins and swarms
- ✅ Resolved 3 TODOs in `dtsl_handler.py`
- ✅ Added detailed error reporting
- ✅ Created comprehensive documentation
- ✅ Added validation examples

## 🤝 Contributing

When extending DTSL schemas:

1. Update schema definitions in `dtsl_schema_validator.py`
2. Add corresponding semantic validation in `_validate_*_semantics()` methods
3. Update this documentation with new fields
4. Add test cases for new validation rules
5. Update example DTSL files

## 📧 Support

For questions about DTSL schema validation:
- Review [COMPREHENSIVE_ENHANCEMENT_ANALYSIS.md](../../../../COMPREHENSIVE_ENHANCEMENT_ANALYSIS.md)
- Check [DTSL Protocol Documentation](../README.md)
- See Week 17 development log
