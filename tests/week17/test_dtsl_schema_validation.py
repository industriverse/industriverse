"""
Week 17 Day 4: DTSL Schema Validation Tests
Tests for twin/swarm/file schema validation
"""

import pytest
import json


class TestDTSLSchemaValidator:
    """Test DTSL schema validator"""

    @pytest.fixture
    def validator(self):
        """Create DTSL schema validator"""
        try:
            from src.protocol_layer.protocols.dtsl.dtsl_schema_validator import (
                get_dtsl_schema_validator
            )
            return get_dtsl_schema_validator()
        except ImportError:
            pytest.skip("DTSL schema validator not available")

    def test_validator_module_imports(self):
        """Test that validator module can be imported"""
        try:
            from src.protocol_layer.protocols.dtsl.dtsl_schema_validator import (
                DTSLSchemaValidator,
                DTSLValidationError,
                get_dtsl_schema_validator
            )

            assert DTSLSchemaValidator is not None
            assert DTSLValidationError is not None
            assert get_dtsl_schema_validator is not None

        except ImportError as e:
            pytest.fail(f"Failed to import DTSL schema validator: {e}")

    def test_valid_twin_definition(self, validator):
        """Test validation of valid twin definition"""
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
                    "min_value": -40.0,
                    "max_value": 125.0
                }
            ]
        }

        is_valid, errors = validator.validate_twin_definition(twin_def, raise_on_error=False)
        assert is_valid, f"Valid twin definition failed: {errors}"
        assert len(errors) == 0

    def test_invalid_twin_missing_type(self, validator):
        """Test validation of twin definition missing type"""
        twin_def = {
            "version": "1.0.0",
            "config": {}
        }

        is_valid, errors = validator.validate_twin_definition(twin_def, raise_on_error=False)
        assert not is_valid
        assert len(errors) > 0

    def test_invalid_twin_bad_version(self, validator):
        """Test validation of twin definition with invalid version"""
        twin_def = {
            "type": "sensor_twin",
            "version": "1.0",  # Should be semver (1.0.0)
            "config": {}
        }

        is_valid, errors = validator.validate_twin_definition(twin_def, raise_on_error=False)
        assert not is_valid
        assert any("version" in str(e).lower() for e in errors)

    def test_semantic_validation_sensor_ranges(self, validator):
        """Test semantic validation of sensor min/max values"""
        twin_def = {
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

        is_valid, errors = validator.validate_twin_definition(twin_def, raise_on_error=False)
        assert not is_valid
        assert any("min_value must be less than max_value" in str(e) for e in errors)

    def test_semantic_validation_duplicate_sensors(self, validator):
        """Test semantic validation for duplicate sensor IDs"""
        twin_def = {
            "type": "sensor_twin",
            "version": "1.0.0",
            "config": {},
            "sensors": [
                {"sensor_id": "temp_01", "sensor_type": "temperature"},
                {"sensor_id": "temp_01", "sensor_type": "temperature"}  # Duplicate
            ]
        }

        is_valid, errors = validator.validate_twin_definition(twin_def, raise_on_error=False)
        assert not is_valid
        assert any("duplicate" in str(e).lower() for e in errors)

    def test_valid_swarm_definition(self, validator):
        """Test validation of valid swarm definition"""
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
                    "config": {}
                }
            ]
        }

        is_valid, errors = validator.validate_swarm_definition(swarm_def, raise_on_error=False)
        assert is_valid, f"Valid swarm definition failed: {errors}"
        assert len(errors) == 0

    def test_invalid_swarm_no_twins(self, validator):
        """Test validation of swarm definition without twins"""
        swarm_def = {
            "swarm_id": "test_swarm",
            "version": "1.0.0",
            "twins": []  # Empty twins list
        }

        is_valid, errors = validator.validate_swarm_definition(swarm_def, raise_on_error=False)
        assert not is_valid

    def test_semantic_validation_invalid_relationships(self, validator):
        """Test semantic validation for invalid relationship targets"""
        swarm_def = {
            "swarm_id": "test_swarm",
            "version": "1.0.0",
            "twins": [
                {
                    "id": "twin_01",
                    "type": "sensor_twin",
                    "config": {},
                    "relationships": [
                        {
                            "target_twin_id": "nonexistent_twin",  # Invalid
                            "relationship_type": "peer"
                        }
                    ]
                }
            ]
        }

        is_valid, errors = validator.validate_swarm_definition(swarm_def, raise_on_error=False)
        assert not is_valid
        assert any("unknown twin" in str(e).lower() for e in errors)

    def test_valid_dtsl_file(self, validator):
        """Test validation of valid DTSL file"""
        dtsl_file = {
            "dtsl_version": "1.0",
            "twin_definitions": [
                {
                    "type": "sensor_twin",
                    "version": "1.0.0",
                    "config": {}
                }
            ],
            "swarm_definitions": [
                {
                    "swarm_id": "test_swarm",
                    "version": "1.0.0",
                    "twins": [
                        {
                            "type": "sensor_twin",
                            "config": {}
                        }
                    ]
                }
            ]
        }

        is_valid, errors = validator.validate_dtsl_file(dtsl_file, raise_on_error=False)
        assert is_valid, f"Valid DTSL file failed: {errors}"
        assert len(errors) == 0


class TestDTSLHandlerIntegration:
    """Test DTSL handler integration with schema validation"""

    def test_handler_validates_twin_definitions(self):
        """Test that DTSLHandler validates twin definitions"""
        # Note: This would require full handler setup
        # For now, we test that the methods exist
        from pathlib import Path

        handler_file = Path("src/protocol_layer/protocols/dtsl/dtsl_handler.py")
        assert handler_file.exists()

        content = handler_file.read_text()

        # Check that validation code is present
        assert "from .dtsl_schema_validator import" in content
        assert "validator.validate_twin_definition" in content
        assert "validator.validate_swarm_definition" in content
        assert "validator.validate_dtsl_file" in content


class TestDTSLDocumentation:
    """Test DTSL schema validation documentation"""

    def test_validation_doc_exists(self):
        """Test that schema validation documentation exists"""
        from pathlib import Path

        doc = Path(
            "src/protocol_layer/protocols/dtsl/DTSL_SCHEMA_VALIDATION.md"
        )

        assert doc.exists(), "DTSL schema validation doc not found"

    def test_validation_doc_content(self):
        """Test validation doc has required sections"""
        from pathlib import Path

        doc = Path(
            "src/protocol_layer/protocols/dtsl/DTSL_SCHEMA_VALIDATION.md"
        )

        if not doc.exists():
            pytest.skip("Validation doc not found")

        content = doc.read_text()

        required_sections = [
            "Overview",
            "Resolved TODOs",
            "Schema Definitions",
            "Validation Types",
            "Usage Examples",
            "Testing"
        ]

        for section in required_sections:
            assert section in content, f"Section '{section}' not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
