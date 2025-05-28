"""
Chaos Test Suite - Tests for resilience and fault tolerance in the UI/UX Layer.

This module provides comprehensive chaos tests for the UI/UX Layer,
ensuring that all components can handle unexpected failures, network issues,
and other chaotic conditions gracefully.
"""

import os
import sys
import json
import time
import random
import logging
import unittest
import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UIUXLayerChaosTest(unittest.TestCase):
    """Chaos test case for the UI/UX Layer."""
    
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
    
    def test_network_disconnection_resilience(self):
        """Test resilience to network disconnection."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Simulate network disconnection
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': True,
            'latency': 0,
            'downloadThroughput': 0,
            'uploadThroughput': 0
        })
        
        # Wait for offline indicator to appear
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'offline-indicator'))
        )
        
        # Verify offline indicator is visible
        offline_indicator = self.driver.find_element(By.ID, 'offline-indicator')
        self.assertTrue(offline_indicator.is_displayed(), "Offline indicator not displayed")
        
        # Verify cached content is still accessible
        dashboard_content = self.driver.find_element(By.ID, 'dashboard-content')
        self.assertTrue(dashboard_content.is_displayed(), "Dashboard content not displayed in offline mode")
        
        # Simulate network reconnection
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'latency': 0,
            'downloadThroughput': -1,
            'uploadThroughput': -1
        })
        
        # Wait for offline indicator to disappear
        WebDriverWait(self.driver, self.wait_time).until_not(
            EC.presence_of_element_located((By.ID, 'offline-indicator'))
        )
        
        # Verify application recovers and syncs data
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'sync-complete-indicator'))
        )
        
        # Verify sync complete indicator is visible
        sync_complete_indicator = self.driver.find_element(By.ID, 'sync-complete-indicator')
        self.assertTrue(sync_complete_indicator.is_displayed(), "Sync complete indicator not displayed")
    
    def test_slow_network_resilience(self):
        """Test resilience to slow network conditions."""
        # Navigate to welcome page
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Simulate slow network
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'latency': 2000,  # 2000ms latency
            'downloadThroughput': 5 * 1024,  # 5 KB/s download speed
            'uploadThroughput': 5 * 1024  # 5 KB/s upload speed
        })
        
        # Navigate to digital twin explorer page
        self.driver.get(f"{self.base_url}/digital-twin-explorer")
        
        # Verify loading indicator is displayed
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'loading-indicator'))
        )
        
        loading_indicator = self.driver.find_element(By.ID, 'loading-indicator')
        self.assertTrue(loading_indicator.is_displayed(), "Loading indicator not displayed")
        
        # Wait for page to load (with extended timeout)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, 'digital-twin-explorer-page'))
        )
        
        # Verify page loaded successfully
        digital_twin_explorer_page = self.driver.find_element(By.ID, 'digital-twin-explorer-page')
        self.assertTrue(digital_twin_explorer_page.is_displayed(), "Digital Twin Explorer page not displayed")
        
        # Reset network conditions
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'latency': 0,
            'downloadThroughput': -1,
            'uploadThroughput': -1
        })
    
    def test_api_failure_resilience(self):
        """Test resilience to API failures."""
        # Navigate to agent explorer page
        self.driver.get(f"{self.base_url}/agent-explorer")
        
        # Wait for agent explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'agent-explorer-page'))
        )
        
        # Simulate API failure by blocking requests to agent API
        self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
            'urls': [f"{self.api_base_url}/agents"]
        })
        
        # Refresh page to trigger API calls
        self.driver.refresh()
        
        # Wait for error indicator to appear
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'api-error-indicator'))
        )
        
        # Verify error indicator is visible
        error_indicator = self.driver.find_element(By.ID, 'api-error-indicator')
        self.assertTrue(error_indicator.is_displayed(), "API error indicator not displayed")
        
        # Verify fallback content is displayed
        fallback_content = self.driver.find_element(By.ID, 'fallback-content')
        self.assertTrue(fallback_content.is_displayed(), "Fallback content not displayed")
        
        # Verify retry button is available
        retry_button = self.driver.find_element(By.ID, 'retry-button')
        self.assertTrue(retry_button.is_displayed(), "Retry button not displayed")
        
        # Unblock API requests
        self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
            'urls': []
        })
        
        # Click retry button
        retry_button.click()
        
        # Wait for content to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'agent-list'))
        )
        
        # Verify content loaded successfully
        agent_list = self.driver.find_element(By.ID, 'agent-list')
        self.assertTrue(agent_list.is_displayed(), "Agent list not displayed after retry")
    
    def test_random_api_latency_resilience(self):
        """Test resilience to random API latency."""
        # Navigate to workflow explorer page
        self.driver.get(f"{self.base_url}/workflow-explorer")
        
        # Wait for workflow explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'workflow-explorer-page'))
        )
        
        # Set up request interception to add random latency
        self.driver.execute_cdp_cmd('Network.enable', {})
        
        # Define request interception function
        def add_random_latency(request):
            # Only add latency to API requests
            if self.api_base_url in request['request']['url']:
                # Add random latency between 1-10 seconds
                time.sleep(random.uniform(1, 10))
            
            # Continue with the request
            self.driver.execute_cdp_cmd('Network.continueInterceptedRequest', {
                'interceptionId': request['interceptionId']
            })
        
        # Set up interception
        self.driver.execute_cdp_cmd('Network.setRequestInterception', {
            'patterns': [{'urlPattern': '*'}]
        })
        
        # Start interception thread
        interception_thread = threading.Thread(target=lambda: self.driver.execute_cdp_cmd('Network.requestIntercepted', add_random_latency))
        interception_thread.daemon = True
        interception_thread.start()
        
        # Refresh page to trigger API calls with random latency
        self.driver.refresh()
        
        # Verify loading indicators appear
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator'))
        )
        
        # Wait for content to load (with extended timeout)
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, 'workflow-list'))
        )
        
        # Verify content loaded successfully
        workflow_list = self.driver.find_element(By.ID, 'workflow-list')
        self.assertTrue(workflow_list.is_displayed(), "Workflow list not displayed after random latency")
        
        # Disable request interception
        self.driver.execute_cdp_cmd('Network.setRequestInterception', {
            'patterns': []
        })
    
    def test_memory_pressure_resilience(self):
        """Test resilience to memory pressure."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Simulate memory pressure
        self.driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': 1920,
            'height': 1080,
            'deviceScaleFactor': 1,
            'mobile': False
        })
        
        # Create memory pressure by allocating large arrays
        self.driver.execute_script("""
            // Allocate memory until pressure is detected
            const arrays = [];
            try {
                for (let i = 0; i < 100; i++) {
                    arrays.push(new Array(1000000).fill('x'));
                }
            } catch (e) {
                console.error('Memory allocation failed:', e);
            }
            
            // Trigger garbage collection
            if (window.gc) {
                window.gc();
            }
            
            // Return allocated memory size
            return arrays.length * 1000000;
        """)
        
        # Navigate to different pages to test memory management
        pages = [
            '/digital-twin-explorer',
            '/workflow-explorer',
            '/agent-explorer',
            '/settings',
            '/dashboard'
        ]
        
        for page in pages:
            # Navigate to page
            self.driver.get(f"{self.base_url}{page}")
            
            # Wait for page to load (with extended timeout)
            page_id = page.strip('/') + '-page'
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, page_id))
            )
            
            # Verify page loaded successfully
            page_element = self.driver.find_element(By.ID, page_id)
            self.assertTrue(page_element.is_displayed(), f"{page} not displayed under memory pressure")
    
    def test_cpu_pressure_resilience(self):
        """Test resilience to CPU pressure."""
        # Navigate to welcome page
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Create CPU pressure by running intensive calculation
        self.driver.execute_script("""
            // Function to create CPU pressure
            function createCPUPressure() {
                const start = Date.now();
                while (Date.now() - start < 5000) {
                    // Intensive calculation
                    Math.random() * Math.random();
                }
            }
            
            // Run CPU pressure in background
            setTimeout(createCPUPressure, 0);
            
            return true;
        """)
        
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load (with extended timeout)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Verify page loaded successfully
        dashboard_page = self.driver.find_element(By.ID, 'dashboard-page')
        self.assertTrue(dashboard_page.is_displayed(), "Dashboard page not displayed under CPU pressure")
        
        # Interact with page elements
        capsule_dock = self.driver.find_element(By.ID, 'capsule-dock')
        capsule = capsule_dock.find_element(By.CLASS_NAME, 'capsule')
        
        # Click capsule
        capsule.click()
        
        # Wait for capsule to expand (with extended timeout)
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'capsule-expanded'))
        )
        
        # Verify capsule expanded successfully
        expanded_capsule = self.driver.find_element(By.CLASS_NAME, 'capsule-expanded')
        self.assertTrue(expanded_capsule.is_displayed(), "Capsule not expanded under CPU pressure")
    
    def test_random_dom_mutation_resilience(self):
        """Test resilience to random DOM mutations."""
        # Navigate to agent explorer page
        self.driver.get(f"{self.base_url}/agent-explorer")
        
        # Wait for agent explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'agent-explorer-page'))
        )
        
        # Inject script to randomly mutate DOM
        self.driver.execute_script("""
            // Function to randomly mutate DOM
            function randomDOMMutation() {
                // Get all elements
                const elements = document.querySelectorAll('*');
                
                // Skip if no elements
                if (elements.length === 0) return;
                
                // Select random element
                const randomElement = elements[Math.floor(Math.random() * elements.length)];
                
                // Skip body and html elements
                if (randomElement.tagName === 'BODY' || randomElement.tagName === 'HTML') return;
                
                // Random mutation type
                const mutationType = Math.floor(Math.random() * 3);
                
                try {
                    switch (mutationType) {
                        case 0: // Add class
                            randomElement.classList.add('random-class-' + Math.floor(Math.random() * 1000));
                            break;
                        case 1: // Change style
                            randomElement.style.opacity = Math.random().toFixed(2);
                            break;
                        case 2: // Add attribute
                            randomElement.setAttribute('data-random', 'random-value-' + Math.floor(Math.random() * 1000));
                            break;
                    }
                } catch (e) {
                    console.error('DOM mutation failed:', e);
                }
            }
            
            // Perform random mutations
            for (let i = 0; i < 50; i++) {
                setTimeout(randomDOMMutation, i * 100);
            }
            
            return true;
        """)
        
        # Wait for mutations to complete
        time.sleep(6)
        
        # Interact with page elements
        try:
            # Find agent list
            agent_list = self.driver.find_element(By.ID, 'agent-list')
            
            # Verify agent list is displayed
            self.assertTrue(agent_list.is_displayed(), "Agent list not displayed after DOM mutations")
            
            # Find and click first agent
            agent = agent_list.find_element(By.CLASS_NAME, 'agent-item')
            agent.click()
            
            # Wait for agent details to load
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.ID, 'agent-details'))
            )
            
            # Verify agent details are displayed
            agent_details = self.driver.find_element(By.ID, 'agent-details')
            self.assertTrue(agent_details.is_displayed(), "Agent details not displayed after DOM mutations")
        except Exception as e:
            self.fail(f"Interaction failed after DOM mutations: {str(e)}")
    
    def test_local_storage_corruption_resilience(self):
        """Test resilience to local storage corruption."""
        # Navigate to settings page
        self.driver.get(f"{self.base_url}/settings")
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Save settings
        theme_toggle = self.driver.find_element(By.ID, 'theme-toggle')
        theme_toggle.click()
        
        save_button = self.driver.find_element(By.ID, 'save-settings')
        save_button.click()
        
        # Wait for settings to save
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-saved'))
        )
        
        # Corrupt local storage
        self.driver.execute_script("""
            // Get all local storage keys
            const keys = Object.keys(localStorage);
            
            // Corrupt each key
            for (const key of keys) {
                try {
                    // Get current value
                    const value = localStorage.getItem(key);
                    
                    // Corrupt value
                    localStorage.setItem(key, value.substring(0, value.length / 2) + '{"corrupt": true');
                } catch (e) {
                    console.error('Local storage corruption failed:', e);
                }
            }
            
            return keys.length;
        """)
        
        # Refresh page
        self.driver.refresh()
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Verify error recovery message is displayed
        error_recovery = self.driver.find_element(By.ID, 'storage-error-recovery')
        self.assertTrue(error_recovery.is_displayed(), "Storage error recovery message not displayed")
        
        # Verify default settings are restored
        default_settings_restored = self.driver.find_element(By.ID, 'default-settings-restored')
        self.assertTrue(default_settings_restored.is_displayed(), "Default settings restored message not displayed")
        
        # Save settings again
        theme_toggle = self.driver.find_element(By.ID, 'theme-toggle')
        theme_toggle.click()
        
        save_button = self.driver.find_element(By.ID, 'save-settings')
        save_button.click()
        
        # Wait for settings to save
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-saved'))
        )
        
        # Verify settings are saved
        settings_saved = self.driver.find_element(By.ID, 'settings-saved')
        self.assertTrue(settings_saved.is_displayed(), "Settings saved message not displayed after recovery")
    
    def test_websocket_disconnection_resilience(self):
        """Test resilience to WebSocket disconnection."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Wait for WebSocket connection to establish
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'websocket-connected'))
        )
        
        # Verify WebSocket connection is established
        websocket_connected = self.driver.find_element(By.ID, 'websocket-connected')
        self.assertTrue(websocket_connected.is_displayed(), "WebSocket connected indicator not displayed")
        
        # Disconnect WebSocket
        self.driver.execute_script("""
            // Get all WebSocket instances
            const sockets = window._websockets || [];
            
            // Close each socket
            for (const socket of sockets) {
                try {
                    socket.close();
                } catch (e) {
                    console.error('WebSocket close failed:', e);
                }
            }
            
            return sockets.length;
        """)
        
        # Wait for WebSocket disconnection indicator
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'websocket-disconnected'))
        )
        
        # Verify WebSocket disconnection indicator is displayed
        websocket_disconnected = self.driver.find_element(By.ID, 'websocket-disconnected')
        self.assertTrue(websocket_disconnected.is_displayed(), "WebSocket disconnected indicator not displayed")
        
        # Verify reconnect button is available
        reconnect_button = self.driver.find_element(By.ID, 'websocket-reconnect')
        self.assertTrue(reconnect_button.is_displayed(), "WebSocket reconnect button not displayed")
        
        # Click reconnect button
        reconnect_button.click()
        
        # Wait for WebSocket connection to reestablish
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'websocket-connected'))
        )
        
        # Verify WebSocket connection is reestablished
        websocket_connected = self.driver.find_element(By.ID, 'websocket-connected')
        self.assertTrue(websocket_connected.is_displayed(), "WebSocket connected indicator not displayed after reconnect")
    
    def test_random_browser_resize_resilience(self):
        """Test resilience to random browser resizing."""
        # Navigate to welcome page
        self.driver.get(self.base_url)
        
        # Wait for page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Define common screen sizes
        screen_sizes = [
            (320, 568),   # iPhone SE
            (375, 667),   # iPhone 8
            (414, 896),   # iPhone 11 Pro Max
            (768, 1024),  # iPad
            (1024, 768),  # iPad landscape
            (1280, 800),  # Small laptop
            (1366, 768),  # Laptop
            (1440, 900),  # Larger laptop
            (1920, 1080), # Full HD
            (2560, 1440)  # 2K
        ]
        
        # Randomly resize browser multiple times
        for _ in range(5):
            # Select random screen size
            width, height = random.choice(screen_sizes)
            
            # Resize browser
            self.driver.set_window_size(width, height)
            
            # Wait for responsive layout to adjust
            time.sleep(1)
            
            # Verify universal skin shell is still visible
            universal_skin_shell = self.driver.find_element(By.ID, 'universal-skin-shell')
            self.assertTrue(universal_skin_shell.is_displayed(), f"Universal Skin Shell not displayed at {width}x{height}")
            
            # Verify capsule dock is visible
            capsule_dock = self.driver.find_element(By.ID, 'capsule-dock')
            self.assertTrue(capsule_dock.is_displayed(), f"Capsule Dock not displayed at {width}x{height}")
        
        # Reset to full HD
        self.driver.set_window_size(1920, 1080)
    
    def test_rapid_navigation_resilience(self):
        """Test resilience to rapid navigation between pages."""
        # Define pages to navigate
        pages = [
            '/',
            '/dashboard',
            '/digital-twin-explorer',
            '/workflow-explorer',
            '/agent-explorer',
            '/settings'
        ]
        
        # Navigate rapidly between pages
        for _ in range(3):  # Do 3 rounds of rapid navigation
            for page in pages:
                # Navigate to page
                self.driver.get(f"{self.base_url}{page}")
                
                # Don't wait for page to fully load before navigating to next page
                time.sleep(0.2)
        
        # Navigate to dashboard page and wait for it to load
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Verify dashboard page loaded successfully
        dashboard_page = self.driver.find_element(By.ID, 'dashboard-page')
        self.assertTrue(dashboard_page.is_displayed(), "Dashboard page not displayed after rapid navigation")
    
    def test_concurrent_api_requests_resilience(self):
        """Test resilience to concurrent API requests."""
        # Navigate to dashboard page
        self.driver.get(f"{self.base_url}/dashboard")
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Make concurrent API requests
        self.driver.execute_script("""
            // API endpoints to request
            const endpoints = [
                '/api/agents',
                '/api/workflows',
                '/api/digital-twins',
                '/api/metrics',
                '/api/events',
                '/api/alerts',
                '/api/settings',
                '/api/user'
            ];
            
            // Make concurrent requests
            const requests = endpoints.map(endpoint => 
                fetch(endpoint)
                    .then(response => response.ok ? response.json() : Promise.reject(response))
                    .catch(error => console.error(`Error fetching ${endpoint}:`, error))
            );
            
            // Return when all requests complete
            return Promise.allSettled(requests)
                .then(results => {
                    return {
                        fulfilled: results.filter(r => r.status === 'fulfilled').length,
                        rejected: results.filter(r => r.status === 'rejected').length
                    };
                });
        """)
        
        # Wait for concurrent requests to complete
        time.sleep(5)
        
        # Verify dashboard still functions
        try:
            # Find and click on a dashboard widget
            dashboard_widget = self.driver.find_element(By.CLASS_NAME, 'dashboard-widget')
            dashboard_widget.click()
            
            # Wait for widget details to load
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'widget-details'))
            )
            
            # Verify widget details are displayed
            widget_details = self.driver.find_element(By.CLASS_NAME, 'widget-details')
            self.assertTrue(widget_details.is_displayed(), "Widget details not displayed after concurrent API requests")
        except Exception as e:
            self.fail(f"Dashboard interaction failed after concurrent API requests: {str(e)}")

def run_tests():
    """Run the chaos tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UIUXLayerChaosTest))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
