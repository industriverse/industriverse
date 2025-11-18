"""
Week 17 Day 5: Error Handling Improvements Tests
Tests to verify that all bare except clauses have been replaced with specific exceptions
"""

import pytest
import ast
import re
from pathlib import Path


class TestBareExceptClauses:
    """Test that all bare except clauses have been fixed"""

    @pytest.fixture
    def codebase_files(self):
        """Get all Python files in src directory"""
        src_dir = Path("src")
        if not src_dir.exists():
            pytest.skip("src directory not found")

        return list(src_dir.rglob("*.py"))

    def test_no_bare_except_in_data_layer(self, codebase_files):
        """Test that data layer files have no bare except clauses"""
        data_layer_files = [
            f for f in codebase_files
            if "data_layer" in str(f)
        ]

        bare_except_pattern = re.compile(r'^\s*except:\s*$', re.MULTILINE)

        files_with_bare_except = []

        for file in data_layer_files:
            if file.name.startswith("test_"):
                continue

            content = file.read_text()

            if bare_except_pattern.search(content):
                files_with_bare_except.append(file)

        assert len(files_with_bare_except) == 0, \
            f"Found bare except clauses in: {[str(f) for f in files_with_bare_except]}"

    def test_no_bare_except_in_protocol_layer(self, codebase_files):
        """Test that protocol layer files have no bare except clauses"""
        protocol_files = [
            f for f in codebase_files
            if "protocol_layer" in str(f)
        ]

        bare_except_pattern = re.compile(r'^\s*except:\s*$', re.MULTILINE)

        files_with_bare_except = []

        for file in protocol_files:
            if file.name.startswith("test_"):
                continue

            content = file.read_text()

            if bare_except_pattern.search(content):
                files_with_bare_except.append(file)

        assert len(files_with_bare_except) == 0, \
            f"Found bare except clauses in: {[str(f) for f in files_with_bare_except]}"

    def test_specific_files_fixed(self):
        """Test that specific files known to have had bare except are now fixed"""
        fixed_files = [
            "src/data_layer/src/processing_engine/data_processing_engine.py",
            "src/data_layer/src/storage_management/storage_management_system.py",
            "src/data_layer/src/catalog/data_catalog_system.py",
            "src/protocol_layer/industrial/adapters/opcua/opcua_adapter.py",
            "src/protocol_layer/industrial/adapters/modbus/modbus_adapter.py",
            "src/protocol_layer/industrial/adapters/mqtt/mqtt_adapter.py",
            "src/deployment_operations_layer/cloud_provider/aws_provider.py",
            "src/deployment_operations_layer/cloud_provider/azure_provider.py",
            "src/deployment_operations_layer/cloud_provider/gcp_provider.py"
        ]

        bare_except_pattern = re.compile(r'^\s*except:\s*$', re.MULTILINE)

        for file_path in fixed_files:
            file = Path(file_path)

            if not file.exists():
                pytest.skip(f"File not found: {file_path}")

            content = file.read_text()

            assert not bare_except_pattern.search(content), \
                f"File {file_path} still contains bare except clauses"

    def test_specific_exceptions_used(self):
        """Test that specific exception types are being used"""
        test_file = Path("src/data_layer/src/processing_engine/data_processing_engine.py")

        if not test_file.exists():
            pytest.skip("Test file not found")

        content = test_file.read_text()

        # Should contain specific exception types
        assert "except (ValueError, TypeError, KeyError):" in content
        assert "except (json.JSONDecodeError" in content

    def test_exception_comments_present(self):
        """Test that exception handling includes explanatory comments"""
        test_file = Path("src/data_layer/src/storage_management/storage_management_system.py")

        if not test_file.exists():
            pytest.skip("Test file not found")

        content = test_file.read_text()

        # Should have comments explaining exceptions
        assert "# ValueError:" in content
        assert "# TypeError:" in content
        assert "# JSONDecodeError:" in content


class TestExceptionCoverage:
    """Test that common exception types are properly handled"""

    def test_pandas_exceptions(self):
        """Test that Pandas-related exceptions are handled"""
        from pathlib import Path

        files_with_pandas = [
            "src/data_layer/src/processing_engine/data_processing_engine.py",
            "src/data_layer/src/catalog/data_catalog_system.py"
        ]

        for file_path in files_with_pandas:
            file = Path(file_path)
            if not file.exists():
                continue

            content = file.read_text()

            # Should handle Pandas exceptions
            assert "pd.errors.ParserError" in content or "ValueError" in content

    def test_json_exceptions(self):
        """Test that JSON-related exceptions are handled"""
        from pathlib import Path

        files_with_json = [
            "src/data_layer/src/processing_engine/data_processing_engine.py",
            "src/deployment_operations_layer/agent/agent_utils.py"
        ]

        for file_path in files_with_json:
            file = Path(file_path)
            if not file.exists():
                continue

            content = file.read_text()

            # Should handle JSON exceptions
            assert "json.JSONDecodeError" in content or "JSONDecodeError" in content

    def test_database_exceptions(self):
        """Test that database exceptions are handled"""
        from pathlib import Path

        file = Path("src/data_layer/src/storage_management/storage_management_system.py")

        if not file.exists():
            pytest.skip("File not found")

        content = file.read_text()

        # Should handle database exceptions
        assert "sqlite3.Error" in content


class TestErrorHandlingDocumentation:
    """Test error handling documentation"""

    def test_error_handling_doc_exists(self):
        """Test that error handling improvement doc exists"""
        doc = Path("ERROR_HANDLING_IMPROVEMENTS.md")
        assert doc.exists(), "Error handling documentation not found"

    def test_error_handling_doc_content(self):
        """Test that doc has required sections"""
        doc = Path("ERROR_HANDLING_IMPROVEMENTS.md")

        if not doc.exists():
            pytest.skip("Documentation not found")

        content = doc.read_text()

        required_sections = [
            "Overview",
            "Files Modified",
            "Exception Type Categories",
            "Summary of Changes",
            "Benefits",
            "Testing"
        ]

        for section in required_sections:
            assert section in content, f"Section '{section}' not found in documentation"

    def test_all_fixed_files_documented(self):
        """Test that all fixed files are documented"""
        doc = Path("ERROR_HANDLING_IMPROVEMENTS.md")

        if not doc.exists():
            pytest.skip("Documentation not found")

        content = doc.read_text()

        fixed_files = [
            "data_processing_engine.py",
            "storage_management_system.py",
            "data_catalog_system.py",
            "opcua_adapter.py",
            "modbus_adapter.py",
            "mqtt_adapter.py",
            "aws_provider.py",
            "azure_provider.py",
            "gcp_provider.py",
            "agent_utils.py"
        ]

        for filename in fixed_files:
            assert filename in content, f"File '{filename}' not documented"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
