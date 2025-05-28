"""
Testing Framework for Industriverse Generative Layer

This module implements the testing framework for the Generative Layer with
protocol-native architecture and MCP/A2A integration.
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestingFramework:
    """
    Implements the testing framework for the Generative Layer.
    Provides functionality for testing generated artifacts.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the testing framework.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.test_suites = {}
        self.test_results = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "testing_framework_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Register default test suites
        self._register_default_test_suites()
        
        logger.info("Testing Framework initialized")
    
    def _register_default_test_suites(self):
        """Register default test suites."""
        # Web UI test suite
        self.register_test_suite(
            suite_id="web_ui",
            name="Web UI Test Suite",
            description="Test suite for web UI artifacts",
            target_types=["html", "css", "javascript"],
            test_cases={
                "html": ["structure", "links", "forms", "accessibility"],
                "css": ["responsive", "cross_browser", "print"],
                "javascript": ["functionality", "performance", "compatibility"]
            },
            settings={
                "structure": {
                    "validate_html": True,
                    "check_semantic_elements": True
                },
                "links": {
                    "check_broken_links": True,
                    "validate_external_links": True
                },
                "forms": {
                    "validate_inputs": True,
                    "check_submission": True
                },
                "accessibility": {
                    "wcag_level": "AA",
                    "check_screen_readers": True
                },
                "responsive": {
                    "breakpoints": ["320px", "768px", "1024px", "1440px"],
                    "check_mobile_first": True
                },
                "cross_browser": {
                    "browsers": ["chrome", "firefox", "safari", "edge"],
                    "check_vendor_prefixes": True
                },
                "print": {
                    "check_print_styles": True
                },
                "functionality": {
                    "unit_tests": True,
                    "integration_tests": True
                },
                "performance": {
                    "benchmark_rendering": True,
                    "check_memory_leaks": True
                },
                "compatibility": {
                    "es_version": "ES6",
                    "check_polyfills": True
                }
            }
        )
        
        # Industrial dashboard test suite
        self.register_test_suite(
            suite_id="industrial_dashboard",
            name="Industrial Dashboard Test Suite",
            description="Test suite for industrial dashboard artifacts",
            target_types=["dashboard", "visualization", "control_panel"],
            test_cases={
                "dashboard": ["data_accuracy", "refresh_rate", "alerts", "user_roles"],
                "visualization": ["chart_accuracy", "responsiveness", "data_density"],
                "control_panel": ["control_functionality", "safety_features", "permissions"]
            },
            settings={
                "data_accuracy": {
                    "validate_calculations": True,
                    "check_data_sources": True
                },
                "refresh_rate": {
                    "minimum_rate": "1s",
                    "check_performance_impact": True
                },
                "alerts": {
                    "validate_thresholds": True,
                    "check_notification_delivery": True
                },
                "user_roles": {
                    "test_permissions": True,
                    "validate_role_separation": True
                },
                "chart_accuracy": {
                    "validate_rendering": True,
                    "check_data_mapping": True
                },
                "responsiveness": {
                    "test_resize_behavior": True,
                    "check_mobile_view": True
                },
                "data_density": {
                    "validate_information_hierarchy": True,
                    "check_cognitive_load": True
                },
                "control_functionality": {
                    "test_all_controls": True,
                    "validate_feedback": True
                },
                "safety_features": {
                    "test_confirmation_dialogs": True,
                    "validate_emergency_stops": True
                },
                "permissions": {
                    "test_access_controls": True,
                    "validate_audit_logging": True
                }
            }
        )
        
        # API test suite
        self.register_test_suite(
            suite_id="api",
            name="API Test Suite",
            description="Test suite for API artifacts",
            target_types=["rest_api", "graphql", "websocket"],
            test_cases={
                "rest_api": ["endpoints", "authentication", "rate_limiting", "error_handling"],
                "graphql": ["queries", "mutations", "subscriptions", "validation"],
                "websocket": ["connection", "messaging", "reconnection", "security"]
            },
            settings={
                "endpoints": {
                    "test_all_methods": True,
                    "validate_responses": True
                },
                "authentication": {
                    "test_auth_methods": True,
                    "validate_token_handling": True
                },
                "rate_limiting": {
                    "test_limits": True,
                    "validate_headers": True
                },
                "error_handling": {
                    "test_error_codes": True,
                    "validate_error_messages": True
                },
                "queries": {
                    "test_all_queries": True,
                    "validate_responses": True
                },
                "mutations": {
                    "test_all_mutations": True,
                    "validate_side_effects": True
                },
                "subscriptions": {
                    "test_event_delivery": True,
                    "validate_real_time_updates": True
                },
                "validation": {
                    "test_input_validation": True,
                    "validate_schema": True
                },
                "connection": {
                    "test_connection_establishment": True,
                    "validate_handshake": True
                },
                "messaging": {
                    "test_message_delivery": True,
                    "validate_message_format": True
                },
                "reconnection": {
                    "test_reconnection_behavior": True,
                    "validate_state_recovery": True
                },
                "security": {
                    "test_origin_validation": True,
                    "validate_message_authentication": True
                }
            }
        )
        
        # Low ticket offer test suite
        self.register_test_suite(
            suite_id="low_ticket_offer",
            name="Low Ticket Offer Test Suite",
            description="Test suite for low ticket offer artifacts",
            target_types=["web_app", "dashboard", "documentation", "api"],
            test_cases={
                "web_app": ["functionality", "usability", "performance", "accessibility"],
                "dashboard": ["data_accuracy", "responsiveness", "user_roles"],
                "documentation": ["completeness", "accuracy", "readability"],
                "api": ["endpoints", "authentication", "error_handling"]
            },
            settings={
                "functionality": {
                    "test_core_features": True,
                    "validate_business_logic": True
                },
                "usability": {
                    "test_user_flows": True,
                    "validate_intuitive_design": True
                },
                "performance": {
                    "test_load_time": True,
                    "maximum_load_time": "3s"
                },
                "accessibility": {
                    "wcag_level": "AA",
                    "test_keyboard_navigation": True
                },
                "data_accuracy": {
                    "validate_calculations": True,
                    "check_data_sources": True
                },
                "responsiveness": {
                    "test_resize_behavior": True,
                    "check_mobile_view": True
                },
                "user_roles": {
                    "test_permissions": True,
                    "validate_role_separation": True
                },
                "completeness": {
                    "check_all_features_documented": True,
                    "validate_examples": True
                },
                "accuracy": {
                    "verify_technical_accuracy": True,
                    "check_version_match": True
                },
                "readability": {
                    "validate_clarity": True,
                    "check_structure": True
                },
                "endpoints": {
                    "test_all_methods": True,
                    "validate_responses": True
                },
                "authentication": {
                    "test_auth_methods": True,
                    "validate_token_handling": True
                },
                "error_handling": {
                    "test_error_codes": True,
                    "validate_error_messages": True
                }
            }
        )
    
    def register_test_suite(self, 
                          suite_id: str, 
                          name: str,
                          description: str,
                          target_types: List[str],
                          test_cases: Dict[str, List[str]],
                          settings: Dict[str, Dict[str, Any]],
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new test suite.
        
        Args:
            suite_id: Unique identifier for the test suite
            name: Name of the test suite
            description: Description of the test suite
            target_types: List of target types this test suite can test
            test_cases: Dictionary mapping target types to lists of test cases
            settings: Dictionary of test case settings
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if suite_id in self.test_suites:
            logger.warning(f"Test suite {suite_id} already registered")
            return False
        
        timestamp = time.time()
        
        # Create test suite record
        suite = {
            "id": suite_id,
            "name": name,
            "description": description,
            "target_types": target_types,
            "test_cases": test_cases,
            "settings": settings,
            "metadata": metadata or {},
            "timestamp": timestamp
        }
        
        # Store test suite
        self.test_suites[suite_id] = suite
        
        # Store test suite file
        suite_path = os.path.join(self.storage_path, f"{suite_id}_test_suite.json")
        with open(suite_path, 'w') as f:
            json.dump(suite, f, indent=2)
        
        logger.info(f"Registered test suite {suite_id}: {name}")
        
        # Emit MCP event for test suite registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/testing/suite_registered",
                {
                    "suite_id": suite_id,
                    "name": name,
                    "target_types": target_types
                }
            )
        
        return True
    
    def run_tests(self, 
                artifact_id: str, 
                artifact_type: str,
                content: Any,
                test_suite_id: Optional[str] = None,
                test_run_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Run tests on an artifact.
        
        Args:
            artifact_id: ID of the artifact to test
            artifact_type: Type of the artifact
            content: Content of the artifact
            test_suite_id: ID of the test suite to use (optional)
            test_run_id: Optional ID for the test run (generated if not provided)
            
        Returns:
            Test result if successful, None otherwise
        """
        # Select appropriate test suite if not specified
        if test_suite_id is None:
            test_suite_id = self._select_test_suite_for_type(artifact_type)
            
        # Check if a test suite is available
        if test_suite_id is None:
            logger.warning(f"No suitable test suite found for type: {artifact_type}")
            return None
            
        # Generate test run ID if not provided
        if test_run_id is None:
            test_run_id = f"run_{uuid.uuid4().hex[:8]}"
        
        timestamp = time.time()
        
        try:
            # Get test suite
            test_suite = self.test_suites[test_suite_id]
            
            # Initialize test result
            result = {
                "id": test_run_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "test_suite_id": test_suite_id,
                "test_suite_name": test_suite["name"],
                "timestamp": timestamp,
                "status": "success",
                "test_cases": [],
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "total": 0
            }
            
            # Get test cases for this artifact type
            test_cases = test_suite["test_cases"].get(artifact_type, [])
            
            if not test_cases:
                logger.warning(f"No test cases defined for artifact type: {artifact_type}")
                result["status"] = "warning"
                
                # Store test result
                self.test_results[test_run_id] = result
                
                # Store test result file
                result_path = os.path.join(self.storage_path, f"{test_run_id}_result.json")
                with open(result_path, 'w') as f:
                    json.dump(result, f, indent=2)
                
                return result
            
            # Run test cases
            for test_case in test_cases:
                # Get test case settings
                settings = test_suite["settings"].get(test_case, {})
                
                # Run test case
                test_case_result = self._run_test_case(test_case, content, settings)
                
                # Add test case result
                result["test_cases"].append(test_case_result)
                
                # Update counts
                result["total"] += 1
                if test_case_result["status"] == "pass":
                    result["passed"] += 1
                elif test_case_result["status"] == "fail":
                    result["failed"] += 1
                elif test_case_result["status"] == "warning":
                    result["warnings"] += 1
            
            # Determine overall status
            if result["failed"] > 0:
                result["status"] = "fail"
            elif result["warnings"] > 0:
                result["status"] = "warning"
            
            # Store test result
            self.test_results[test_run_id] = result
            
            # Store test result file
            result_path = os.path.join(self.storage_path, f"{test_run_id}_result.json")
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Tested artifact {artifact_id} with result: {result['status']} (passed: {result['passed']}, failed: {result['failed']}, warnings: {result['warnings']})")
            
            # Emit MCP event for test completion
            if self.agent_core:
                self.agent_core.send_mcp_event(
                    "generative_layer/testing/artifact_tested",
                    {
                        "test_run_id": test_run_id,
                        "artifact_id": artifact_id,
                        "status": result["status"],
                        "passed": result["passed"],
                        "failed": result["failed"],
                        "warnings": result["warnings"]
                    }
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing artifact {artifact_id}: {str(e)}")
            
            # Create failure result
            result = {
                "id": test_run_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "test_suite_id": test_suite_id,
                "timestamp": timestamp,
                "status": "error",
                "reason": f"Test error: {str(e)}"
            }
            
            # Store test result
            self.test_results[test_run_id] = result
            
            return result
    
    def get_test_result(self, test_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a test result by ID.
        
        Args:
            test_run_id: ID of the test result to retrieve
            
        Returns:
            Test result if found, None otherwise
        """
        if test_run_id not in self.test_results:
            logger.warning(f"Test result {test_run_id} not found")
            return None
        
        return self.test_results[test_run_id]
    
    def get_test_suite(self, suite_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a test suite by ID.
        
        Args:
            suite_id: ID of the test suite to retrieve
            
        Returns:
            Test suite if found, None otherwise
        """
        if suite_id not in self.test_suites:
            logger.warning(f"Test suite {suite_id} not found")
            return None
        
        return self.test_suites[suite_id]
    
    def _select_test_suite_for_type(self, artifact_type: str) -> Optional[str]:
        """
        Select an appropriate test suite for an artifact type.
        
        Args:
            artifact_type: Type of artifact
            
        Returns:
            Test suite ID if found, None otherwise
        """
        # Find test suites that support this artifact type
        suitable_suites = []
        
        for suite_id, suite in self.test_suites.items():
            if artifact_type in suite["target_types"]:
                suitable_suites.append(suite_id)
        
        if not suitable_suites:
            return None
        
        # For now, just return the first suitable test suite
        # In the future, this could be more sophisticated
        return suitable_suites[0]
    
    def _run_test_case(self, test_case: str, content: Any, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a test case on content.
        
        Args:
            test_case: Name of the test case
            content: Content to test
            settings: Test case settings
            
        Returns:
            Test case result
        """
        # Initialize result
        result = {
            "test_case": test_case,
            "status": "pass",
            "issues": [],
            "details": {}
        }
        
        # In a real implementation, this would perform actual tests
        # For this example, we'll simulate the process with some common test cases
        
        if test_case == "structure":
            # Test HTML structure
            if isinstance(content, str):
                # Check for doctype
                if "<!doctype html>" not in content.lower() and settings.get("validate_html", True):
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": "Missing DOCTYPE declaration"
                    })
                
                # Check for semantic elements
                if settings.get("check_semantic_elements", True):
                    semantic_elements = ["header", "nav", "main", "article", "section", "aside", "footer"]
                    found_elements = [elem for elem in semantic_elements if f"<{elem}" in content.lower()]
                    
                    if len(found_elements) < 3:  # Arbitrary threshold
                        result["status"] = "warning"
                        result["issues"].append({
                            "severity": "medium",
                            "message": f"Limited use of semantic elements. Found: {', '.join(found_elements)}"
                        })
                
                result["details"]["semantic_elements_found"] = found_elements if 'found_elements' in locals() else []
        
        elif test_case == "links":
            # Test links
            if isinstance(content, str):
                # Check for broken links (simplified)
                if settings.get("check_broken_links", True):
                    import re
                    links = re.findall(r'href=["\'](.*?)["\']', content)
                    empty_links = [link for link in links if not link or link == "#"]
                    
                    if empty_links:
                        result["status"] = "warning"
                        result["issues"].append({
                            "severity": "medium",
                            "message": f"Found {len(empty_links)} empty or placeholder links"
                        })
                
                result["details"]["total_links"] = len(links) if 'links' in locals() else 0
                result["details"]["empty_links"] = len(empty_links) if 'empty_links' in locals() else 0
        
        elif test_case == "responsive":
            # Test responsiveness
            if isinstance(content, str):
                # Check for viewport meta tag
                if '<meta name="viewport"' not in content.lower():
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": "Missing viewport meta tag for responsive design"
                    })
                
                # Check for media queries
                if "@media" not in content.lower():
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": "No media queries found for responsive breakpoints"
                    })
                
                # Check for mobile-first approach
                if settings.get("check_mobile_first", True) and "@media (min-width:" not in content.lower():
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": "No min-width media queries found, may not be using mobile-first approach"
                    })
        
        elif test_case == "functionality":
            # Test functionality
            if settings.get("unit_tests", True):
                # Simulate unit tests
                result["details"]["unit_tests"] = {
                    "total": 10,
                    "passed": 9,
                    "failed": 1
                }
                
                if result["details"]["unit_tests"]["failed"] > 0:
                    result["status"] = "fail"
                    result["issues"].append({
                        "severity": "high",
                        "message": f"Unit tests failed: {result['details']['unit_tests']['failed']} of {result['details']['unit_tests']['total']}"
                    })
            
            if settings.get("integration_tests", True):
                # Simulate integration tests
                result["details"]["integration_tests"] = {
                    "total": 5,
                    "passed": 5,
                    "failed": 0
                }
        
        elif test_case == "data_accuracy":
            # Test data accuracy
            if settings.get("validate_calculations", True):
                # Simulate calculation validation
                result["details"]["calculations"] = {
                    "total": 8,
                    "accurate": 8,
                    "inaccurate": 0
                }
            
            if settings.get("check_data_sources", True):
                # Simulate data source checking
                result["details"]["data_sources"] = {
                    "total": 3,
                    "valid": 3,
                    "invalid": 0
                }
        
        elif test_case == "endpoints":
            # Test API endpoints
            if settings.get("test_all_methods", True):
                # Simulate endpoint testing
                result["details"]["endpoints"] = {
                    "total": 12,
                    "passed": 11,
                    "failed": 1
                }
                
                if result["details"]["endpoints"]["failed"] > 0:
                    result["status"] = "fail"
                    result["issues"].append({
                        "severity": "high",
                        "message": f"Endpoint tests failed: {result['details']['endpoints']['failed']} of {result['details']['endpoints']['total']}"
                    })
            
            if settings.get("validate_responses", True):
                # Simulate response validation
                result["details"]["responses"] = {
                    "total": 12,
                    "valid": 10,
                    "invalid": 2
                }
                
                if result["details"]["responses"]["invalid"] > 0:
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": f"Invalid responses: {result['details']['responses']['invalid']} of {result['details']['responses']['total']}"
                    })
        
        elif test_case == "completeness":
            # Test documentation completeness
            if settings.get("check_all_features_documented", True):
                # Simulate feature documentation checking
                result["details"]["features"] = {
                    "total": 15,
                    "documented": 13,
                    "undocumented": 2
                }
                
                if result["details"]["features"]["undocumented"] > 0:
                    result["status"] = "warning"
                    result["issues"].append({
                        "severity": "medium",
                        "message": f"Undocumented features: {result['details']['features']['undocumented']} of {result['details']['features']['total']}"
                    })
            
            if settings.get("validate_examples", True):
                # Simulate example validation
                result["details"]["examples"] = {
                    "total": 10,
                    "valid": 10,
                    "invalid": 0
                }
        
        # For other test cases, just return a pass result
        else:
            result["details"]["note"] = f"Test case '{test_case}' simulated successfully"
        
        return result
    
    def export_test_data(self) -> Dict[str, Any]:
        """
        Export test data for persistence.
        
        Returns:
            Test data
        """
        return {
            "test_suites": self.test_suites,
            "test_results": self.test_results
        }
    
    def import_test_data(self, test_data: Dict[str, Any]) -> None:
        """
        Import test data from persistence.
        
        Args:
            test_data: Test data to import
        """
        if "test_suites" in test_data:
            self.test_suites = test_data["test_suites"]
        
        if "test_results" in test_data:
            self.test_results = test_data["test_results"]
        
        logger.info("Imported test data")
