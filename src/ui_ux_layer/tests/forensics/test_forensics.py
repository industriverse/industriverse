"""
Forensics Test Suite - Tests for the forensics capabilities of the UI/UX Layer.

This module provides comprehensive forensics tests for the UI/UX Layer,
ensuring that all components properly log events, maintain audit trails,
and support debugging and troubleshooting.
"""

import os
import sys
import json
import time
import uuid
import logging
import unittest
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UIUXLayerForensicsTest(unittest.TestCase):
    """Forensics test case for the UI/UX Layer."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test case class."""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        # Set up WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.set_window_size(1920, 1080)
        
        # Set base URL
        cls.base_url = os.environ.get('UI_UX_LAYER_URL', 'http://localhost:8080')
        cls.api_base_url = os.environ.get('UI_UX_LAYER_API_URL', 'http://localhost:8080/api')
        
        # Set wait time
        cls.wait_time = 10
        
        # Generate unique test ID
        cls.test_id = str(uuid.uuid4())
        
        # Set up test user
        cls.test_user = f"forensics_test_user_{cls.test_id}"
    
    @classmethod
    def tearDownClass(cls):
        """Tear down the test case class."""
        # Close WebDriver
        cls.driver.quit()
    
    def setUp(self):
        """Set up the test case."""
        # Navigate to base URL
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
    
    def test_event_logging(self):
        """Test event logging for user interactions."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique action ID for this test
        action_id = f"test_action_{uuid.uuid4()}"
        
        # Perform a series of user interactions
        actions = [
            {'element_id': 'capsule-dock', 'action': 'click', 'description': 'Open Capsule Dock'},
            {'element_id': 'layer-avatars', 'action': 'click', 'description': 'Open Layer Avatars'},
            {'element_id': 'workflow-widget', 'action': 'click', 'description': 'Open Workflow Widget'},
            {'element_id': 'settings-button', 'action': 'click', 'description': 'Open Settings'}
        ]
        
        # Execute actions and tag them with our test ID
        for action in actions:
            # Find element
            element = self.driver.find_element(By.ID, action['element_id'])
            
            # Tag action with test ID
            self.driver.execute_script(
                f"arguments[0].setAttribute('data-test-id', '{self.test_id}');", 
                element
            )
            
            # Tag action with action ID
            self.driver.execute_script(
                f"arguments[0].setAttribute('data-action-id', '{action_id}');", 
                element
            )
            
            # Perform action
            if action['action'] == 'click':
                element.click()
            
            # Wait for action to register
            time.sleep(1)
        
        # Navigate to forensics page
        self.driver.get(f"{self.base_url}/forensics")
        
        # Wait for forensics page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'forensics-page'))
        )
        
        # Search for events by test ID
        search_input = self.driver.find_element(By.ID, 'forensics-search')
        search_input.send_keys(self.test_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'forensics-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'forensics-result')
        
        # Verify all actions were logged
        self.assertEqual(len(results), len(actions), f"Expected {len(actions)} logged events, found {len(results)}")
        
        # Verify action details were logged correctly
        for i, action in enumerate(actions):
            result = results[i]
            
            # Verify action ID
            action_id_element = result.find_element(By.CLASS_NAME, 'action-id')
            self.assertIn(action_id, action_id_element.text, f"Action ID not found in log entry {i+1}")
            
            # Verify element ID
            element_id_element = result.find_element(By.CLASS_NAME, 'element-id')
            self.assertIn(action['element_id'], element_id_element.text, f"Element ID not found in log entry {i+1}")
            
            # Verify action type
            action_type_element = result.find_element(By.CLASS_NAME, 'action-type')
            self.assertIn(action['action'], action_type_element.text, f"Action type not found in log entry {i+1}")
            
            # Verify timestamp exists
            timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), f"Timestamp missing in log entry {i+1}")
    
    def test_audit_trail(self):
        """Test audit trail for system changes."""
        # Navigate to settings page
        self.driver.get(f"{self.base_url}/settings")
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Generate unique setting name for this test
        setting_name = f"test_setting_{self.test_id}"
        
        # Make a series of system changes
        changes = [
            {'setting': 'theme', 'value': 'dark', 'description': 'Change theme to dark'},
            {'setting': 'notifications', 'value': 'enabled', 'description': 'Enable notifications'},
            {'setting': 'language', 'value': 'en-US', 'description': 'Set language to English'},
            {'setting': setting_name, 'value': 'test_value', 'description': 'Set custom test setting'}
        ]
        
        # Execute changes
        for change in changes:
            # Find setting element
            if change['setting'] == setting_name:
                # For custom setting, use the custom setting form
                custom_name_input = self.driver.find_element(By.ID, 'custom-setting-name')
                custom_value_input = self.driver.find_element(By.ID, 'custom-setting-value')
                custom_save_button = self.driver.find_element(By.ID, 'custom-setting-save')
                
                # Set custom setting
                custom_name_input.clear()
                custom_name_input.send_keys(change['setting'])
                custom_value_input.clear()
                custom_value_input.send_keys(change['value'])
                custom_save_button.click()
            else:
                # For standard settings, use the settings form
                setting_element = self.driver.find_element(By.ID, f"setting-{change['setting']}")
                
                # Tag element with test ID
                self.driver.execute_script(
                    f"arguments[0].setAttribute('data-test-id', '{self.test_id}');", 
                    setting_element
                )
                
                # Set value based on element type
                if setting_element.tag_name == 'select':
                    # For select elements, select by value
                    for option in setting_element.find_elements(By.TAG_NAME, 'option'):
                        if option.get_attribute('value') == change['value']:
                            option.click()
                            break
                elif setting_element.tag_name == 'input' and setting_element.get_attribute('type') == 'checkbox':
                    # For checkboxes, check or uncheck
                    if (change['value'] == 'enabled' and not setting_element.is_selected()) or \
                       (change['value'] == 'disabled' and setting_element.is_selected()):
                        setting_element.click()
                else:
                    # For other inputs, set value directly
                    setting_element.clear()
                    setting_element.send_keys(change['value'])
            
            # Wait for change to register
            time.sleep(1)
        
        # Save settings
        save_button = self.driver.find_element(By.ID, 'save-settings')
        save_button.click()
        
        # Wait for settings to save
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-saved'))
        )
        
        # Navigate to audit trail page
        self.driver.get(f"{self.base_url}/audit-trail")
        
        # Wait for audit trail page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'audit-trail-page'))
        )
        
        # Search for audit events by test ID
        search_input = self.driver.find_element(By.ID, 'audit-search')
        search_input.send_keys(self.test_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'audit-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'audit-result')
        
        # Verify all changes were logged
        self.assertGreaterEqual(len(results), len(changes), f"Expected at least {len(changes)} audit events, found {len(results)}")
        
        # Verify custom setting change was logged correctly
        custom_setting_found = False
        for result in results:
            # Get setting name
            setting_name_element = result.find_element(By.CLASS_NAME, 'setting-name')
            if setting_name in setting_name_element.text:
                custom_setting_found = True
                
                # Verify setting value
                setting_value_element = result.find_element(By.CLASS_NAME, 'setting-value')
                self.assertIn('test_value', setting_value_element.text, "Custom setting value not found in audit trail")
                
                # Verify timestamp exists
                timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
                self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in audit trail")
                
                # Verify user info exists
                user_element = result.find_element(By.CLASS_NAME, 'user-info')
                self.assertTrue(user_element.text.strip(), "User info missing in audit trail")
                
                break
        
        self.assertTrue(custom_setting_found, "Custom setting change not found in audit trail")
    
    def test_error_logging(self):
        """Test error logging for system errors."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique error ID for this test
        error_id = f"test_error_{self.test_id}"
        
        # Inject script to generate errors
        self.driver.execute_script(f"""
            // Log error with test ID
            console.error('Test error with ID: {error_id}');
            
            // Generate different types of errors
            try {{
                // Reference error
                nonExistentFunction();
            }} catch (e) {{
                console.error('Reference error with ID: {error_id}', e);
            }}
            
            try {{
                // Type error
                null.toString();
            }} catch (e) {{
                console.error('Type error with ID: {error_id}', e);
            }}
            
            try {{
                // Syntax error (eval)
                eval('if (true) {{');
            }} catch (e) {{
                console.error('Syntax error with ID: {error_id}', e);
            }}
            
            // Log to error tracking system
            if (window.errorTracker) {{
                window.errorTracker.logError({{
                    message: 'Test error with ID: {error_id}',
                    stack: new Error().stack,
                    timestamp: new Date().toISOString(),
                    testId: '{self.test_id}'
                }});
            }}
            
            return true;
        """)
        
        # Wait for errors to be logged
        time.sleep(2)
        
        # Navigate to error logs page
        self.driver.get(f"{self.base_url}/error-logs")
        
        # Wait for error logs page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'error-logs-page'))
        )
        
        # Search for errors by error ID
        search_input = self.driver.find_element(By.ID, 'error-search')
        search_input.send_keys(error_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'error-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'error-result')
        
        # Verify errors were logged
        self.assertGreaterEqual(len(results), 3, f"Expected at least 3 error logs, found {len(results)}")
        
        # Verify error details were logged correctly
        error_types = ['Reference error', 'Type error', 'Syntax error']
        found_error_types = []
        
        for result in results:
            # Get error message
            error_message_element = result.find_element(By.CLASS_NAME, 'error-message')
            error_message = error_message_element.text
            
            # Check for error types
            for error_type in error_types:
                if error_type in error_message and error_type not in found_error_types:
                    found_error_types.append(error_type)
            
            # Verify error ID
            self.assertIn(error_id, error_message, "Error ID not found in error log")
            
            # Verify timestamp exists
            timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in error log")
            
            # Verify stack trace exists
            stack_trace_element = result.find_element(By.CLASS_NAME, 'stack-trace')
            self.assertTrue(stack_trace_element.text.strip(), "Stack trace missing in error log")
        
        # Verify all error types were found
        for error_type in error_types:
            self.assertIn(error_type, found_error_types, f"{error_type} not found in error logs")
    
    def test_user_session_tracking(self):
        """Test user session tracking."""
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for login page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'login-page'))
        )
        
        # Log in with test user
        username_input = self.driver.find_element(By.ID, 'username')
        password_input = self.driver.find_element(By.ID, 'password')
        login_button = self.driver.find_element(By.ID, 'login-button')
        
        username_input.send_keys(self.test_user)
        password_input.send_keys('password')
        login_button.click()
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Perform a series of page navigations
        pages = [
            '/dashboard',
            '/digital-twin-explorer',
            '/workflow-explorer',
            '/agent-explorer',
            '/settings'
        ]
        
        for page in pages:
            # Navigate to page
            self.driver.get(f"{self.base_url}{page}")
            
            # Wait for page to load
            page_id = page.strip('/') + '-page'
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.ID, page_id))
            )
            
            # Wait for page view to register
            time.sleep(1)
        
        # Log out
        self.driver.get(f"{self.base_url}/logout")
        
        # Wait for login page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'login-page'))
        )
        
        # Log in as admin to view session data
        username_input = self.driver.find_element(By.ID, 'username')
        password_input = self.driver.find_element(By.ID, 'password')
        login_button = self.driver.find_element(By.ID, 'login-button')
        
        username_input.send_keys('admin')
        password_input.send_keys('admin')
        login_button.click()
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Navigate to user sessions page
        self.driver.get(f"{self.base_url}/user-sessions")
        
        # Wait for user sessions page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'user-sessions-page'))
        )
        
        # Search for sessions by test user
        search_input = self.driver.find_element(By.ID, 'session-search')
        search_input.send_keys(self.test_user)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'session-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'session-result')
        
        # Verify session was logged
        self.assertGreaterEqual(len(results), 1, f"Expected at least 1 session log, found {len(results)}")
        
        # Click on first session to view details
        results[0].click()
        
        # Wait for session details to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'session-details'))
        )
        
        # Get page views
        page_views = self.driver.find_elements(By.CLASS_NAME, 'page-view')
        
        # Verify all page views were logged
        self.assertGreaterEqual(len(page_views), len(pages), f"Expected at least {len(pages)} page views, found {len(page_views)}")
        
        # Verify page views were logged correctly
        found_pages = []
        for page_view in page_views:
            # Get page URL
            page_url_element = page_view.find_element(By.CLASS_NAME, 'page-url')
            page_url = page_url_element.text
            
            # Check for pages
            for page in pages:
                if page in page_url and page not in found_pages:
                    found_pages.append(page)
            
            # Verify timestamp exists
            timestamp_element = page_view.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in page view")
        
        # Verify all pages were found
        for page in pages:
            self.assertIn(page, found_pages, f"{page} not found in page views")
    
    def test_performance_metrics_logging(self):
        """Test logging of performance metrics."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique metric ID for this test
        metric_id = f"test_metric_{self.test_id}"
        
        # Inject script to log performance metrics
        self.driver.execute_script(f"""
            // Log performance metrics with test ID
            if (window.performanceTracker) {{
                // Log page load metrics
                window.performanceTracker.logMetric({{
                    name: 'page_load',
                    value: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    unit: 'ms',
                    tags: {{
                        test_id: '{self.test_id}',
                        metric_id: '{metric_id}',
                        page: 'dashboard'
                    }}
                }});
                
                // Log DOM content loaded metrics
                window.performanceTracker.logMetric({{
                    name: 'dom_content_loaded',
                    value: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    unit: 'ms',
                    tags: {{
                        test_id: '{self.test_id}',
                        metric_id: '{metric_id}',
                        page: 'dashboard'
                    }}
                }});
                
                // Log first paint metrics
                const paintMetrics = performance.getEntriesByType('paint');
                for (const paint of paintMetrics) {{
                    window.performanceTracker.logMetric({{
                        name: paint.name,
                        value: paint.startTime,
                        unit: 'ms',
                        tags: {{
                            test_id: '{self.test_id}',
                            metric_id: '{metric_id}',
                            page: 'dashboard'
                        }}
                    }});
                }}
                
                // Log resource load metrics
                const resources = performance.getEntriesByType('resource');
                for (const resource of resources) {{
                    window.performanceTracker.logMetric({{
                        name: 'resource_load',
                        value: resource.duration,
                        unit: 'ms',
                        tags: {{
                            test_id: '{self.test_id}',
                            metric_id: '{metric_id}',
                            page: 'dashboard',
                            resource_type: resource.initiatorType,
                            resource_name: resource.name
                        }}
                    }});
                }}
            }}
            
            return true;
        """)
        
        # Wait for metrics to be logged
        time.sleep(2)
        
        # Navigate to performance metrics page
        self.driver.get(f"{self.base_url}/performance-metrics")
        
        # Wait for performance metrics page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'performance-metrics-page'))
        )
        
        # Search for metrics by metric ID
        search_input = self.driver.find_element(By.ID, 'metrics-search')
        search_input.send_keys(metric_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'metric-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'metric-result')
        
        # Verify metrics were logged
        self.assertGreaterEqual(len(results), 3, f"Expected at least 3 performance metrics, found {len(results)}")
        
        # Verify metric types were logged correctly
        metric_types = ['page_load', 'dom_content_loaded', 'first-paint']
        found_metric_types = []
        
        for result in results:
            # Get metric name
            metric_name_element = result.find_element(By.CLASS_NAME, 'metric-name')
            metric_name = metric_name_element.text
            
            # Check for metric types
            for metric_type in metric_types:
                if metric_type in metric_name and metric_type not in found_metric_types:
                    found_metric_types.append(metric_type)
            
            # Verify metric ID
            tags_element = result.find_element(By.CLASS_NAME, 'metric-tags')
            self.assertIn(metric_id, tags_element.text, "Metric ID not found in metric tags")
            
            # Verify timestamp exists
            timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in metric log")
            
            # Verify value exists
            value_element = result.find_element(By.CLASS_NAME, 'metric-value')
            self.assertTrue(value_element.text.strip(), "Value missing in metric log")
        
        # Verify key metric types were found
        for metric_type in ['page_load', 'dom_content_loaded']:
            self.assertIn(metric_type, found_metric_types, f"{metric_type} not found in performance metrics")
    
    def test_capsule_lifecycle_tracking(self):
        """Test tracking of capsule lifecycle events."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique capsule ID for this test
        capsule_id = f"test_capsule_{self.test_id}"
        
        # Inject script to create and manipulate test capsule
        self.driver.execute_script(f"""
            // Create test capsule if capsule manager exists
            if (window.capsuleManager) {{
                // Create test capsule
                window.capsuleManager.createCapsule({{
                    id: '{capsule_id}',
                    name: 'Test Capsule',
                    type: 'test',
                    state: 'created',
                    metadata: {{
                        test_id: '{self.test_id}'
                    }}
                }});
                
                // Wait before activating
                setTimeout(() => {{
                    // Activate capsule
                    window.capsuleManager.activateCapsule('{capsule_id}');
                    
                    // Wait before updating
                    setTimeout(() => {{
                        // Update capsule
                        window.capsuleManager.updateCapsule('{capsule_id}', {{
                            state: 'updated',
                            metadata: {{
                                test_id: '{self.test_id}',
                                updated: true
                            }}
                        }});
                        
                        // Wait before suspending
                        setTimeout(() => {{
                            // Suspend capsule
                            window.capsuleManager.suspendCapsule('{capsule_id}');
                            
                            // Wait before resuming
                            setTimeout(() => {{
                                // Resume capsule
                                window.capsuleManager.resumeCapsule('{capsule_id}');
                                
                                // Wait before destroying
                                setTimeout(() => {{
                                    // Destroy capsule
                                    window.capsuleManager.destroyCapsule('{capsule_id}');
                                }}, 500);
                            }}, 500);
                        }}, 500);
                    }}, 500);
                }}, 500);
            }}
            
            return true;
        """)
        
        # Wait for capsule lifecycle events to complete
        time.sleep(4)
        
        # Navigate to capsule logs page
        self.driver.get(f"{self.base_url}/capsule-logs")
        
        # Wait for capsule logs page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'capsule-logs-page'))
        )
        
        # Search for capsule logs by capsule ID
        search_input = self.driver.find_element(By.ID, 'capsule-search')
        search_input.send_keys(capsule_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'capsule-log'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'capsule-log')
        
        # Verify capsule lifecycle events were logged
        self.assertGreaterEqual(len(results), 6, f"Expected at least 6 capsule lifecycle events, found {len(results)}")
        
        # Verify lifecycle events were logged correctly
        lifecycle_events = ['created', 'activated', 'updated', 'suspended', 'resumed', 'destroyed']
        found_events = []
        
        for result in results:
            # Get event type
            event_type_element = result.find_element(By.CLASS_NAME, 'event-type')
            event_type = event_type_element.text
            
            # Check for lifecycle events
            for lifecycle_event in lifecycle_events:
                if lifecycle_event in event_type.lower() and lifecycle_event not in found_events:
                    found_events.append(lifecycle_event)
            
            # Verify capsule ID
            capsule_id_element = result.find_element(By.CLASS_NAME, 'capsule-id')
            self.assertIn(capsule_id, capsule_id_element.text, "Capsule ID not found in capsule log")
            
            # Verify timestamp exists
            timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in capsule log")
        
        # Verify all lifecycle events were found
        for lifecycle_event in lifecycle_events:
            self.assertIn(lifecycle_event, found_events, f"{lifecycle_event} event not found in capsule logs")
    
    def test_cross_layer_communication_logging(self):
        """Test logging of cross-layer communication events."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique communication ID for this test
        communication_id = f"test_communication_{self.test_id}"
        
        # Inject script to simulate cross-layer communication
        self.driver.execute_script(f"""
            // Simulate cross-layer communication if context bus exists
            if (window.contextBus) {{
                // Simulate communication with Data Layer
                window.contextBus.send('DataLayer', {{
                    id: '{communication_id}',
                    action: 'query',
                    payload: {{
                        query: 'SELECT * FROM test_table',
                        parameters: []
                    }},
                    metadata: {{
                        test_id: '{self.test_id}'
                    }}
                }});
                
                // Simulate communication with Core AI Layer
                window.contextBus.send('CoreAILayer', {{
                    id: '{communication_id}',
                    action: 'predict',
                    payload: {{
                        model: 'test_model',
                        input: 'test_input'
                    }},
                    metadata: {{
                        test_id: '{self.test_id}'
                    }}
                }});
                
                // Simulate communication with Workflow Automation Layer
                window.contextBus.send('WorkflowAutomationLayer', {{
                    id: '{communication_id}',
                    action: 'execute',
                    payload: {{
                        workflow: 'test_workflow',
                        parameters: {{}}
                    }},
                    metadata: {{
                        test_id: '{self.test_id}'
                    }}
                }});
                
                // Simulate receiving response from Data Layer
                setTimeout(() => {{
                    window.contextBus.receive('DataLayer', {{
                        id: '{communication_id}',
                        action: 'query_response',
                        payload: {{
                            results: [],
                            status: 'success'
                        }},
                        metadata: {{
                            test_id: '{self.test_id}'
                        }}
                    }});
                }}, 500);
                
                // Simulate receiving response from Core AI Layer
                setTimeout(() => {{
                    window.contextBus.receive('CoreAILayer', {{
                        id: '{communication_id}',
                        action: 'predict_response',
                        payload: {{
                            prediction: 'test_prediction',
                            confidence: 0.95
                        }},
                        metadata: {{
                            test_id: '{self.test_id}'
                        }}
                    }});
                }}, 1000);
                
                // Simulate receiving response from Workflow Automation Layer
                setTimeout(() => {{
                    window.contextBus.receive('WorkflowAutomationLayer', {{
                        id: '{communication_id}',
                        action: 'execute_response',
                        payload: {{
                            result: 'test_result',
                            status: 'completed'
                        }},
                        metadata: {{
                            test_id: '{self.test_id}'
                        }}
                    }});
                }}, 1500);
            }}
            
            return true;
        """)
        
        # Wait for cross-layer communication events to complete
        time.sleep(3)
        
        # Navigate to communication logs page
        self.driver.get(f"{self.base_url}/communication-logs")
        
        # Wait for communication logs page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'communication-logs-page'))
        )
        
        # Search for communication logs by communication ID
        search_input = self.driver.find_element(By.ID, 'communication-search')
        search_input.send_keys(communication_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'communication-log'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'communication-log')
        
        # Verify cross-layer communication events were logged
        self.assertGreaterEqual(len(results), 6, f"Expected at least 6 cross-layer communication events, found {len(results)}")
        
        # Verify communication with each layer was logged
        layers = ['DataLayer', 'CoreAILayer', 'WorkflowAutomationLayer']
        actions = ['query', 'predict', 'execute', 'query_response', 'predict_response', 'execute_response']
        found_layer_actions = []
        
        for result in results:
            # Get layer and action
            layer_element = result.find_element(By.CLASS_NAME, 'layer-name')
            action_element = result.find_element(By.CLASS_NAME, 'action-name')
            
            layer = layer_element.text
            action = action_element.text
            
            # Check for layer-action combinations
            for l in layers:
                for a in actions:
                    if l in layer and a in action and f"{l}:{a}" not in found_layer_actions:
                        found_layer_actions.append(f"{l}:{a}")
            
            # Verify communication ID
            communication_id_element = result.find_element(By.CLASS_NAME, 'communication-id')
            self.assertIn(communication_id, communication_id_element.text, "Communication ID not found in communication log")
            
            # Verify timestamp exists
            timestamp_element = result.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in communication log")
            
            # Verify payload exists
            payload_element = result.find_element(By.CLASS_NAME, 'payload')
            self.assertTrue(payload_element.text.strip(), "Payload missing in communication log")
        
        # Verify key layer-action combinations were found
        key_combinations = ['DataLayer:query', 'CoreAILayer:predict', 'WorkflowAutomationLayer:execute']
        for combination in key_combinations:
            self.assertIn(combination, found_layer_actions, f"{combination} not found in communication logs")
    
    def test_debug_trace_export(self):
        """Test export of debug traces."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Generate unique trace ID for this test
        trace_id = f"test_trace_{self.test_id}"
        
        # Inject script to generate debug trace
        self.driver.execute_script(f"""
            // Generate debug trace if debug tracer exists
            if (window.debugTracer) {{
                // Start trace
                window.debugTracer.startTrace('{trace_id}', {{
                    test_id: '{self.test_id}'
                }});
                
                // Add trace events
                window.debugTracer.addTraceEvent('{trace_id}', {{
                    type: 'component_mount',
                    component: 'Dashboard',
                    timestamp: new Date().toISOString()
                }});
                
                window.debugTracer.addTraceEvent('{trace_id}', {{
                    type: 'data_fetch',
                    source: 'DataLayer',
                    timestamp: new Date().toISOString()
                }});
                
                window.debugTracer.addTraceEvent('{trace_id}', {{
                    type: 'render',
                    component: 'DashboardWidgets',
                    timestamp: new Date().toISOString()
                }});
                
                window.debugTracer.addTraceEvent('{trace_id}', {{
                    type: 'user_interaction',
                    element: 'RefreshButton',
                    timestamp: new Date().toISOString()
                }});
                
                window.debugTracer.addTraceEvent('{trace_id}', {{
                    type: 'error',
                    message: 'Test error',
                    stack: new Error('Test error').stack,
                    timestamp: new Date().toISOString()
                }});
                
                // End trace
                window.debugTracer.endTrace('{trace_id}');
            }}
            
            return true;
        """)
        
        # Wait for debug trace to be generated
        time.sleep(2)
        
        # Navigate to debug traces page
        self.driver.get(f"{self.base_url}/debug-traces")
        
        # Wait for debug traces page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'debug-traces-page'))
        )
        
        # Search for debug traces by trace ID
        search_input = self.driver.find_element(By.ID, 'trace-search')
        search_input.send_keys(trace_id)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'trace-result'))
        )
        
        # Get search results
        results = self.driver.find_elements(By.CLASS_NAME, 'trace-result')
        
        # Verify debug trace was logged
        self.assertGreaterEqual(len(results), 1, f"Expected at least 1 debug trace, found {len(results)}")
        
        # Click on first trace to view details
        results[0].click()
        
        # Wait for trace details to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'trace-details'))
        )
        
        # Get trace events
        trace_events = self.driver.find_elements(By.CLASS_NAME, 'trace-event')
        
        # Verify trace events were logged
        self.assertGreaterEqual(len(trace_events), 5, f"Expected at least 5 trace events, found {len(trace_events)}")
        
        # Verify trace event types were logged correctly
        event_types = ['component_mount', 'data_fetch', 'render', 'user_interaction', 'error']
        found_event_types = []
        
        for trace_event in trace_events:
            # Get event type
            event_type_element = trace_event.find_element(By.CLASS_NAME, 'event-type')
            event_type = event_type_element.text
            
            # Check for event types
            for type_name in event_types:
                if type_name in event_type.lower() and type_name not in found_event_types:
                    found_event_types.append(type_name)
            
            # Verify timestamp exists
            timestamp_element = trace_event.find_element(By.CLASS_NAME, 'timestamp')
            self.assertTrue(timestamp_element.text.strip(), "Timestamp missing in trace event")
        
        # Verify all event types were found
        for event_type in event_types:
            self.assertIn(event_type, found_event_types, f"{event_type} not found in trace events")
        
        # Click export button
        export_button = self.driver.find_element(By.ID, 'export-trace')
        export_button.click()
        
        # Wait for export to complete
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'export-complete'))
        )
        
        # Verify export completed successfully
        export_complete = self.driver.find_element(By.ID, 'export-complete')
        self.assertTrue(export_complete.is_displayed(), "Export complete indicator not displayed")
        
        # Verify download link is available
        download_link = self.driver.find_element(By.ID, 'download-trace')
        self.assertTrue(download_link.is_displayed(), "Download link not displayed")
        self.assertTrue(download_link.get_attribute('href'), "Download link has no href attribute")

def run_tests():
    """Run the forensics tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UIUXLayerForensicsTest))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
