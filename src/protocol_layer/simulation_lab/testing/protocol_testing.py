"""
Protocol Testing Framework for Industriverse Protocol Layer

This module provides comprehensive testing capabilities for protocol components,
including simulation, validation, and performance testing.
"""

import asyncio
import json
import time
import random
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("protocol_testing")

class ProtocolTestCase:
    """
    Represents a test case for protocol testing.
    """
    
    def __init__(self, test_id: str, name: str, description: str = None):
        """
        Initialize a protocol test case.
        
        Args:
            test_id: Unique identifier for the test
            name: Name of the test
            description: Description of the test
        """
        self.test_id = test_id
        self.name = name
        self.description = description or ""
        self.steps = []
        self.assertions = []
        self.setup_actions = []
        self.teardown_actions = []
        self.timeout = 60  # Default timeout in seconds
        self.tags = []
        self.metadata = {}
        
        logger.info(f"Created test case: {name} (ID: {test_id})")
    
    def add_step(self, step_name: str, action: Callable, params: Dict[str, Any] = None):
        """
        Add a test step.
        
        Args:
            step_name: Name of the step
            action: Function to execute
            params: Parameters for the action
        """
        self.steps.append({
            "name": step_name,
            "action": action,
            "params": params or {}
        })
        logger.debug(f"Added step '{step_name}' to test case {self.name}")
    
    def add_assertion(self, assertion_name: str, condition: Callable, 
                     expected: Any, message: str = None):
        """
        Add an assertion to the test case.
        
        Args:
            assertion_name: Name of the assertion
            condition: Function that returns a value to compare
            expected: Expected value
            message: Message to display on failure
        """
        self.assertions.append({
            "name": assertion_name,
            "condition": condition,
            "expected": expected,
            "message": message or f"Assertion '{assertion_name}' failed"
        })
        logger.debug(f"Added assertion '{assertion_name}' to test case {self.name}")
    
    def add_setup(self, action: Callable, params: Dict[str, Any] = None):
        """
        Add a setup action to run before the test.
        
        Args:
            action: Function to execute
            params: Parameters for the action
        """
        self.setup_actions.append({
            "action": action,
            "params": params or {}
        })
    
    def add_teardown(self, action: Callable, params: Dict[str, Any] = None):
        """
        Add a teardown action to run after the test.
        
        Args:
            action: Function to execute
            params: Parameters for the action
        """
        self.teardown_actions.append({
            "action": action,
            "params": params or {}
        })
    
    def set_timeout(self, timeout: int):
        """
        Set the timeout for the test case.
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
    
    def add_tag(self, tag: str):
        """
        Add a tag to the test case.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def set_metadata(self, key: str, value: Any):
        """
        Set metadata for the test case.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

class ProtocolTestSuite:
    """
    A collection of related test cases.
    """
    
    def __init__(self, suite_id: str, name: str, description: str = None):
        """
        Initialize a test suite.
        
        Args:
            suite_id: Unique identifier for the suite
            name: Name of the suite
            description: Description of the suite
        """
        self.suite_id = suite_id
        self.name = name
        self.description = description or ""
        self.test_cases = []
        self.setup_actions = []
        self.teardown_actions = []
        self.tags = []
        self.metadata = {}
        
        logger.info(f"Created test suite: {name} (ID: {suite_id})")
    
    def add_test_case(self, test_case: ProtocolTestCase):
        """
        Add a test case to the suite.
        
        Args:
            test_case: Test case to add
        """
        self.test_cases.append(test_case)
        logger.debug(f"Added test case '{test_case.name}' to suite {self.name}")
    
    def add_setup(self, action: Callable, params: Dict[str, Any] = None):
        """
        Add a setup action to run before the suite.
        
        Args:
            action: Function to execute
            params: Parameters for the action
        """
        self.setup_actions.append({
            "action": action,
            "params": params or {}
        })
    
    def add_teardown(self, action: Callable, params: Dict[str, Any] = None):
        """
        Add a teardown action to run after the suite.
        
        Args:
            action: Function to execute
            params: Parameters for the action
        """
        self.teardown_actions.append({
            "action": action,
            "params": params or {}
        })
    
    def add_tag(self, tag: str):
        """
        Add a tag to the suite.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def set_metadata(self, key: str, value: Any):
        """
        Set metadata for the suite.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def get_test_cases_by_tag(self, tag: str) -> List[ProtocolTestCase]:
        """
        Get test cases with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List[ProtocolTestCase]: Matching test cases
        """
        return [tc for tc in self.test_cases if tag in tc.tags]

class ProtocolTestRunner:
    """
    Executes test cases and suites.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the test runner.
        
        Args:
            config: Configuration for the test runner
        """
        self.config = config or {
            "parallel_tests": 4,
            "default_timeout": 60,
            "stop_on_failure": False,
            "report_format": "json"
        }
        self.results = {}
        self.current_suite = None
        self.current_test = None
        
        logger.info("Initialized Protocol Test Runner")
    
    async def run_test_case(self, test_case: ProtocolTestCase) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_case: Test case to run
            
        Returns:
            Dict[str, Any]: Test results
        """
        self.current_test = test_case
        logger.info(f"Running test case: {test_case.name} (ID: {test_case.test_id})")
        
        start_time = time.time()
        result = {
            "test_id": test_case.test_id,
            "name": test_case.name,
            "status": "pending",
            "steps": [],
            "assertions": [],
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
            "error": None
        }
        
        # Run setup actions
        try:
            for setup in test_case.setup_actions:
                await self._run_action(setup["action"], setup["params"])
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Setup error: {str(e)}"
            result["end_time"] = time.time()
            result["duration"] = result["end_time"] - start_time
            logger.error(f"Setup error in test case {test_case.name}: {e}")
            return result
        
        # Run test steps
        try:
            for step in test_case.steps:
                step_result = await self._run_step(step)
                result["steps"].append(step_result)
                
                if step_result["status"] == "error":
                    result["status"] = "error"
                    result["error"] = step_result["error"]
                    break
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Step error: {str(e)}"
            logger.error(f"Step error in test case {test_case.name}: {e}")
        
        # Run assertions if no errors
        if result["status"] != "error":
            try:
                all_passed = True
                for assertion in test_case.assertions:
                    assertion_result = await self._run_assertion(assertion)
                    result["assertions"].append(assertion_result)
                    
                    if assertion_result["status"] == "failed":
                        all_passed = False
                
                result["status"] = "passed" if all_passed else "failed"
            except Exception as e:
                result["status"] = "error"
                result["error"] = f"Assertion error: {str(e)}"
                logger.error(f"Assertion error in test case {test_case.name}: {e}")
        
        # Run teardown actions
        try:
            for teardown in test_case.teardown_actions:
                await self._run_action(teardown["action"], teardown["params"])
        except Exception as e:
            logger.error(f"Teardown error in test case {test_case.name}: {e}")
            # Don't change test status for teardown errors, but log them
        
        # Finalize result
        result["end_time"] = time.time()
        result["duration"] = result["end_time"] - start_time
        
        logger.info(f"Test case {test_case.name} completed with status: {result['status']}")
        self.results[test_case.test_id] = result
        self.current_test = None
        
        return result
    
    async def _run_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a test step.
        
        Args:
            step: Step to run
            
        Returns:
            Dict[str, Any]: Step result
        """
        logger.debug(f"Running step: {step['name']}")
        start_time = time.time()
        
        step_result = {
            "name": step["name"],
            "status": "pending",
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
            "error": None,
            "output": None
        }
        
        try:
            output = await self._run_action(step["action"], step["params"])
            step_result["status"] = "completed"
            step_result["output"] = output
        except Exception as e:
            step_result["status"] = "error"
            step_result["error"] = str(e)
            logger.error(f"Error in step {step['name']}: {e}")
        
        step_result["end_time"] = time.time()
        step_result["duration"] = step_result["end_time"] - start_time
        
        return step_result
    
    async def _run_assertion(self, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an assertion.
        
        Args:
            assertion: Assertion to run
            
        Returns:
            Dict[str, Any]: Assertion result
        """
        logger.debug(f"Running assertion: {assertion['name']}")
        start_time = time.time()
        
        assertion_result = {
            "name": assertion["name"],
            "status": "pending",
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
            "expected": assertion["expected"],
            "actual": None,
            "message": assertion["message"]
        }
        
        try:
            actual = await self._run_action(assertion["condition"], {})
            assertion_result["actual"] = actual
            
            if actual == assertion["expected"]:
                assertion_result["status"] = "passed"
            else:
                assertion_result["status"] = "failed"
        except Exception as e:
            assertion_result["status"] = "error"
            assertion_result["message"] = f"Error: {str(e)}"
            logger.error(f"Error in assertion {assertion['name']}: {e}")
        
        assertion_result["end_time"] = time.time()
        assertion_result["duration"] = assertion_result["end_time"] - start_time
        
        return assertion_result
    
    async def _run_action(self, action: Callable, params: Dict[str, Any]) -> Any:
        """
        Run an action function.
        
        Args:
            action: Function to run
            params: Parameters for the function
            
        Returns:
            Any: Result of the action
        """
        if asyncio.iscoroutinefunction(action):
            return await action(**params)
        else:
            return action(**params)
    
    async def run_test_suite(self, test_suite: ProtocolTestSuite) -> Dict[str, Any]:
        """
        Run a test suite.
        
        Args:
            test_suite: Test suite to run
            
        Returns:
            Dict[str, Any]: Suite results
        """
        self.current_suite = test_suite
        logger.info(f"Running test suite: {test_suite.name} (ID: {test_suite.suite_id})")
        
        start_time = time.time()
        suite_result = {
            "suite_id": test_suite.suite_id,
            "name": test_suite.name,
            "status": "pending",
            "test_results": [],
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
            "error": None,
            "summary": {
                "total": len(test_suite.test_cases),
                "passed": 0,
                "failed": 0,
                "error": 0,
                "skipped": 0
            }
        }
        
        # Run suite setup actions
        try:
            for setup in test_suite.setup_actions:
                await self._run_action(setup["action"], setup["params"])
        except Exception as e:
            suite_result["status"] = "error"
            suite_result["error"] = f"Suite setup error: {str(e)}"
            suite_result["end_time"] = time.time()
            suite_result["duration"] = suite_result["end_time"] - start_time
            logger.error(f"Setup error in test suite {test_suite.name}: {e}")
            return suite_result
        
        # Run test cases
        parallel_tests = self.config["parallel_tests"]
        if parallel_tests > 1:
            # Run tests in parallel
            tasks = []
            for test_case in test_suite.test_cases:
                task = asyncio.create_task(self.run_test_case(test_case))
                tasks.append(task)
            
            # Wait for all tasks to complete
            test_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in test_results:
                if isinstance(result, Exception):
                    logger.error(f"Error running test case: {result}")
                    suite_result["summary"]["error"] += 1
                else:
                    suite_result["test_results"].append(result)
                    if result["status"] == "passed":
                        suite_result["summary"]["passed"] += 1
                    elif result["status"] == "failed":
                        suite_result["summary"]["failed"] += 1
                    elif result["status"] == "error":
                        suite_result["summary"]["error"] += 1
                    else:
                        suite_result["summary"]["skipped"] += 1
        else:
            # Run tests sequentially
            for test_case in test_suite.test_cases:
                test_result = await self.run_test_case(test_case)
                suite_result["test_results"].append(test_result)
                
                if test_result["status"] == "passed":
                    suite_result["summary"]["passed"] += 1
                elif test_result["status"] == "failed":
                    suite_result["summary"]["failed"] += 1
                    if self.config["stop_on_failure"]:
                        logger.warning("Stopping suite execution due to test failure")
                        break
                elif test_result["status"] == "error":
                    suite_result["summary"]["error"] += 1
                    if self.config["stop_on_failure"]:
                        logger.warning("Stopping suite execution due to test error")
                        break
                else:
                    suite_result["summary"]["skipped"] += 1
        
        # Run suite teardown actions
        try:
            for teardown in test_suite.teardown_actions:
                await self._run_action(teardown["action"], teardown["params"])
        except Exception as e:
            logger.error(f"Teardown error in test suite {test_suite.name}: {e}")
            # Don't change suite status for teardown errors, but log them
        
        # Determine suite status
        if suite_result["summary"]["error"] > 0:
            suite_result["status"] = "error"
        elif suite_result["summary"]["failed"] > 0:
            suite_result["status"] = "failed"
        else:
            suite_result["status"] = "passed"
        
        # Finalize result
        suite_result["end_time"] = time.time()
        suite_result["duration"] = suite_result["end_time"] - start_time
        
        logger.info(f"Test suite {test_suite.name} completed with status: {suite_result['status']}")
        logger.info(f"Summary: {suite_result['summary']}")
        
        self.current_suite = None
        return suite_result
    
    def generate_report(self, results: Dict[str, Any], format: str = None) -> str:
        """
        Generate a test report.
        
        Args:
            results: Test results
            format: Report format (json, html, text)
            
        Returns:
            str: Formatted report
        """
        report_format = format or self.config["report_format"]
        
        if report_format == "json":
            return json.dumps(results, indent=2)
        elif report_format == "html":
            return self._generate_html_report(results)
        else:  # text
            return self._generate_text_report(results)
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """
        Generate an HTML test report.
        
        Args:
            results: Test results
            
        Returns:
            str: HTML report
        """
        # Simple HTML report template
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Protocol Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .summary { margin: 20px 0; padding: 10px; background-color: #f5f5f5; }
                .passed { color: green; }
                .failed { color: red; }
                .error { color: darkred; }
                .test-case { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
                .details { margin-left: 20px; }
            </style>
        </head>
        <body>
            <h1>Protocol Test Report</h1>
        """
        
        # Add suite information
        html += f"""
            <div class="summary">
                <h2>{results['name']} (ID: {results['suite_id']})</h2>
                <p>Status: <span class="{results['status']}">{results['status'].upper()}</span></p>
                <p>Duration: {results['duration']:.2f} seconds</p>
                <p>Total Tests: {results['summary']['total']}</p>
                <p>Passed: <span class="passed">{results['summary']['passed']}</span></p>
                <p>Failed: <span class="failed">{results['summary']['failed']}</span></p>
                <p>Errors: <span class="error">{results['summary']['error']}</span></p>
                <p>Skipped: {results['summary']['skipped']}</p>
            </div>
        """
        
        # Add test case results
        html += "<h2>Test Cases</h2>"
        for test_result in results["test_results"]:
            html += f"""
                <div class="test-case">
                    <h3>{test_result['name']} (ID: {test_result['test_id']})</h3>
                    <p>Status: <span class="{test_result['status']}">{test_result['status'].upper()}</span></p>
                    <p>Duration: {test_result['duration']:.2f} seconds</p>
            """
            
            if test_result.get("error"):
                html += f'<p class="error">Error: {test_result["error"]}</p>'
            
            # Add steps
            if test_result.get("steps"):
                html += '<div class="details"><h4>Steps</h4><ul>'
                for step in test_result["steps"]:
                    html += f'<li>{step["name"]} - {step["status"]}'
                    if step.get("error"):
                        html += f' (Error: {step["error"]})'
                    html += '</li>'
                html += '</ul></div>'
            
            # Add assertions
            if test_result.get("assertions"):
                html += '<div class="details"><h4>Assertions</h4><ul>'
                for assertion in test_result["assertions"]:
                    html += f'<li>{assertion["name"]} - <span class="{assertion["status"]}">{assertion["status"].upper()}</span>'
                    if assertion["status"] == "failed":
                        html += f' (Expected: {assertion["expected"]}, Actual: {assertion["actual"]})'
                    if assertion.get("message") and assertion["status"] != "passed":
                        html += f' - {assertion["message"]}'
                    html += '</li>'
                html += '</ul></div>'
            
            html += '</div>'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a text test report.
        
        Args:
            results: Test results
            
        Returns:
            str: Text report
        """
        report = []
        
        # Add header
        report.append("=" * 80)
        report.append(f"PROTOCOL TEST REPORT: {results['name']} (ID: {results['suite_id']})")
        report.append("=" * 80)
        
        # Add summary
        report.append(f"Status: {results['status'].upper()}")
        report.append(f"Duration: {results['duration']:.2f} seconds")
        report.append(f"Total Tests: {results['summary']['total']}")
        report.append(f"Passed: {results['summary']['passed']}")
        report.append(f"Failed: {results['summary']['failed']}")
        report.append(f"Errors: {results['summary']['error']}")
        report.append(f"Skipped: {results['summary']['skipped']}")
        report.append("")
        
        # Add test case results
        report.append("TEST CASES")
        report.append("-" * 80)
        
        for test_result in results["test_results"]:
            report.append(f"Test: {test_result['name']} (ID: {test_result['test_id']})")
            report.append(f"Status: {test_result['status'].upper()}")
            report.append(f"Duration: {test_result['duration']:.2f} seconds")
            
            if test_result.get("error"):
                report.append(f"Error: {test_result['error']}")
            
            # Add steps
            if test_result.get("steps"):
                report.append("Steps:")
                for step in test_result["steps"]:
                    step_line = f"  - {step['name']} - {step['status']}"
                    if step.get("error"):
                        step_line += f" (Error: {step['error']})"
                    report.append(step_line)
            
            # Add assertions
            if test_result.get("assertions"):
                report.append("Assertions:")
                for assertion in test_result["assertions"]:
                    assertion_line = f"  - {assertion['name']} - {assertion['status'].upper()}"
                    if assertion["status"] == "failed":
                        assertion_line += f" (Expected: {assertion['expected']}, Actual: {assertion['actual']})"
                    if assertion.get("message") and assertion["status"] != "passed":
                        assertion_line += f" - {assertion['message']}"
                    report.append(assertion_line)
            
            report.append("-" * 80)
        
        return "\n".join(report)

class ProtocolPerformanceTester:
    """
    Specialized tester for protocol performance testing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the performance tester.
        
        Args:
            config: Configuration for the tester
        """
        self.config = config or {
            "iterations": 100,
            "warmup_iterations": 10,
            "concurrency": 1,
            "report_percentiles": [50, 90, 95, 99]
        }
        
        logger.info("Initialized Protocol Performance Tester")
    
    async def run_performance_test(self, test_func: Callable, 
                                  params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a performance test.
        
        Args:
            test_func: Function to test
            params: Parameters for the function
            
        Returns:
            Dict[str, Any]: Performance test results
        """
        params = params or {}
        iterations = self.config["iterations"]
        warmup = self.config["warmup_iterations"]
        concurrency = self.config["concurrency"]
        
        logger.info(f"Running performance test with {iterations} iterations (warmup: {warmup})")
        
        # Run warmup iterations
        if warmup > 0:
            logger.info(f"Running {warmup} warmup iterations")
            for _ in range(warmup):
                await self._run_test_iteration(test_func, params)
        
        # Run actual test iterations
        start_time = time.time()
        durations = []
        
        if concurrency > 1:
            # Run concurrent iterations
            tasks = []
            for _ in range(iterations):
                task = asyncio.create_task(self._run_test_iteration(test_func, params))
                tasks.append(task)
            
            # Wait for all tasks to complete
            iteration_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in iteration_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in test iteration: {result}")
                else:
                    durations.append(result)
        else:
            # Run sequential iterations
            for _ in range(iterations):
                duration = await self._run_test_iteration(test_func, params)
                durations.append(duration)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate statistics
        if durations:
            min_duration = min(durations)
            max_duration = max(durations)
            avg_duration = sum(durations) / len(durations)
            median_duration = statistics.median(durations)
            
            # Calculate percentiles
            percentiles = {}
            for p in self.config["report_percentiles"]:
                percentiles[f"p{p}"] = self._calculate_percentile(durations, p)
            
            # Calculate operations per second
            ops_per_second = len(durations) / total_duration
            
            result = {
                "iterations": len(durations),
                "total_duration": total_duration,
                "min": min_duration,
                "max": max_duration,
                "avg": avg_duration,
                "median": median_duration,
                "percentiles": percentiles,
                "ops_per_second": ops_per_second
            }
        else:
            result = {
                "iterations": 0,
                "total_duration": total_duration,
                "error": "No successful iterations"
            }
        
        logger.info(f"Performance test completed: {result}")
        return result
    
    async def _run_test_iteration(self, test_func: Callable, 
                                 params: Dict[str, Any]) -> float:
        """
        Run a single test iteration.
        
        Args:
            test_func: Function to test
            params: Parameters for the function
            
        Returns:
            float: Duration of the iteration in seconds
        """
        start_time = time.time()
        
        if asyncio.iscoroutinefunction(test_func):
            await test_func(**params)
        else:
            test_func(**params)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return duration
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate a percentile from a list of values.
        
        Args:
            values: List of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            float: Percentile value
        """
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1 if k > f else f
        
        if f == c:
            return sorted_values[f]
        else:
            d0 = sorted_values[f] * (c - k)
            d1 = sorted_values[c] * (k - f)
            return d0 + d1

class ProtocolFuzzTester:
    """
    Specialized tester for protocol fuzzing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the fuzz tester.
        
        Args:
            config: Configuration for the tester
        """
        self.config = config or {
            "iterations": 1000,
            "seed": None,
            "mutation_rate": 0.1,
            "max_mutations": 10
        }
        
        # Set random seed if provided
        if self.config["seed"] is not None:
            random.seed(self.config["seed"])
        
        logger.info("Initialized Protocol Fuzz Tester")
    
    async def fuzz_test(self, target_func: Callable, base_input: Any,
                       validator_func: Callable = None) -> Dict[str, Any]:
        """
        Run a fuzz test.
        
        Args:
            target_func: Function to test
            base_input: Base input to mutate
            validator_func: Function to validate results
            
        Returns:
            Dict[str, Any]: Fuzz test results
        """
        iterations = self.config["iterations"]
        logger.info(f"Running fuzz test with {iterations} iterations")
        
        results = {
            "iterations": iterations,
            "successful": 0,
            "failed": 0,
            "errors": 0,
            "failures": []
        }
        
        for i in range(iterations):
            # Generate mutated input
            mutated_input = self._mutate_input(base_input)
            
            try:
                # Run test with mutated input
                if asyncio.iscoroutinefunction(target_func):
                    output = await target_func(mutated_input)
                else:
                    output = target_func(mutated_input)
                
                # Validate output if validator provided
                if validator_func:
                    if asyncio.iscoroutinefunction(validator_func):
                        valid = await validator_func(output)
                    else:
                        valid = validator_func(output)
                    
                    if valid:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["failures"].append({
                            "iteration": i,
                            "input": mutated_input,
                            "output": output,
                            "error": "Validation failed"
                        })
                else:
                    # No validator, assume success
                    results["successful"] += 1
            except Exception as e:
                results["errors"] += 1
                results["failures"].append({
                    "iteration": i,
                    "input": mutated_input,
                    "error": str(e)
                })
                logger.warning(f"Error in fuzz test iteration {i}: {e}")
            
            # Log progress periodically
            if (i + 1) % 100 == 0:
                logger.info(f"Fuzz test progress: {i + 1}/{iterations} iterations")
        
        logger.info(f"Fuzz test completed: {results['successful']} successful, "
                   f"{results['failed']} failed, {results['errors']} errors")
        
        return results
    
    def _mutate_input(self, input_data: Any) -> Any:
        """
        Mutate input data for fuzzing.
        
        Args:
            input_data: Input data to mutate
            
        Returns:
            Any: Mutated input data
        """
        if isinstance(input_data, dict):
            return self._mutate_dict(input_data)
        elif isinstance(input_data, list):
            return self._mutate_list(input_data)
        elif isinstance(input_data, str):
            return self._mutate_string(input_data)
        elif isinstance(input_data, (int, float)):
            return self._mutate_number(input_data)
        elif isinstance(input_data, bool):
            return not input_data
        else:
            # Can't mutate, return as is
            return input_data
    
    def _mutate_dict(self, data: Dict) -> Dict:
        """
        Mutate a dictionary.
        
        Args:
            data: Dictionary to mutate
            
        Returns:
            Dict: Mutated dictionary
        """
        result = data.copy()
        
        # Determine number of mutations
        num_mutations = random.randint(1, min(len(data), self.config["max_mutations"]))
        
        for _ in range(num_mutations):
            mutation_type = random.choice(["modify", "add", "remove"])
            
            if mutation_type == "modify" and result:
                # Modify an existing key
                key = random.choice(list(result.keys()))
                result[key] = self._mutate_input(result[key])
            elif mutation_type == "add":
                # Add a new key
                key = f"fuzz_key_{random.randint(1000, 9999)}"
                result[key] = self._generate_random_value()
            elif mutation_type == "remove" and result:
                # Remove a key
                key = random.choice(list(result.keys()))
                del result[key]
        
        return result
    
    def _mutate_list(self, data: List) -> List:
        """
        Mutate a list.
        
        Args:
            data: List to mutate
            
        Returns:
            List: Mutated list
        """
        result = data.copy()
        
        # Determine number of mutations
        num_mutations = random.randint(1, min(len(data) + 2, self.config["max_mutations"]))
        
        for _ in range(num_mutations):
            mutation_type = random.choice(["modify", "add", "remove", "shuffle"])
            
            if mutation_type == "modify" and result:
                # Modify an existing item
                index = random.randint(0, len(result) - 1)
                result[index] = self._mutate_input(result[index])
            elif mutation_type == "add":
                # Add a new item
                result.append(self._generate_random_value())
            elif mutation_type == "remove" and result:
                # Remove an item
                index = random.randint(0, len(result) - 1)
                result.pop(index)
            elif mutation_type == "shuffle" and len(result) > 1:
                # Shuffle the list
                random.shuffle(result)
        
        return result
    
    def _mutate_string(self, data: str) -> str:
        """
        Mutate a string.
        
        Args:
            data: String to mutate
            
        Returns:
            str: Mutated string
        """
        if not data:
            return self._generate_random_string(random.randint(1, 10))
        
        mutation_type = random.choice(["modify", "append", "prepend", "replace"])
        
        if mutation_type == "modify":
            # Modify characters
            chars = list(data)
            num_mutations = random.randint(1, min(len(chars), self.config["max_mutations"]))
            
            for _ in range(num_mutations):
                index = random.randint(0, len(chars) - 1)
                chars[index] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?")
            
            return "".join(chars)
        elif mutation_type == "append":
            # Append random string
            return data + self._generate_random_string(random.randint(1, 5))
        elif mutation_type == "prepend":
            # Prepend random string
            return self._generate_random_string(random.randint(1, 5)) + data
        else:  # replace
            # Replace with random string
            return self._generate_random_string(len(data))
    
    def _mutate_number(self, data: Union[int, float]) -> Union[int, float]:
        """
        Mutate a number.
        
        Args:
            data: Number to mutate
            
        Returns:
            Union[int, float]: Mutated number
        """
        mutation_type = random.choice(["add", "multiply", "negate", "replace"])
        
        if mutation_type == "add":
            # Add a random value
            if isinstance(data, int):
                return data + random.randint(-100, 100)
            else:
                return data + random.uniform(-100.0, 100.0)
        elif mutation_type == "multiply":
            # Multiply by a random value
            if isinstance(data, int):
                return data * random.randint(-10, 10)
            else:
                return data * random.uniform(-10.0, 10.0)
        elif mutation_type == "negate":
            # Negate the value
            return -data
        else:  # replace
            # Replace with a random value
            if isinstance(data, int):
                return random.randint(-1000, 1000)
            else:
                return random.uniform(-1000.0, 1000.0)
    
    def _generate_random_value(self) -> Any:
        """
        Generate a random value for fuzzing.
        
        Returns:
            Any: Random value
        """
        value_type = random.choice(["string", "number", "boolean", "dict", "list", "null"])
        
        if value_type == "string":
            return self._generate_random_string(random.randint(1, 20))
        elif value_type == "number":
            if random.random() < 0.5:
                return random.randint(-1000, 1000)
            else:
                return random.uniform(-1000.0, 1000.0)
        elif value_type == "boolean":
            return random.choice([True, False])
        elif value_type == "dict":
            # Generate a small random dict
            result = {}
            for _ in range(random.randint(1, 3)):
                key = self._generate_random_string(random.randint(3, 8))
                result[key] = self._generate_random_value()
            return result
        elif value_type == "list":
            # Generate a small random list
            result = []
            for _ in range(random.randint(1, 3)):
                result.append(self._generate_random_value())
            return result
        else:  # null
            return None
    
    def _generate_random_string(self, length: int) -> str:
        """
        Generate a random string.
        
        Args:
            length: Length of the string
            
        Returns:
            str: Random string
        """
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(chars) for _ in range(length))

# Export the main classes
__all__ = [
    'ProtocolTestCase',
    'ProtocolTestSuite',
    'ProtocolTestRunner',
    'ProtocolPerformanceTester',
    'ProtocolFuzzTester'
]
