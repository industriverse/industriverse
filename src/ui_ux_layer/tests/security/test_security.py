"""
Security Test Suite - Tests for security compliance in the UI/UX Layer.

This module provides comprehensive security tests for the UI/UX Layer,
ensuring that all components meet security standards and protect user data
and system integrity.
"""

import os
import sys
import json
import logging
import unittest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class UIUXLayerSecurityTest(unittest.TestCase):
    """Security test case for the UI/UX Layer."""
    
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
    
    def test_content_security_policy(self):
        """Test Content Security Policy headers."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify Content Security Policy header is present
        self.assertIn('Content-Security-Policy', response.headers, "Content Security Policy header not present")
        
        # Verify Content Security Policy header contains expected directives
        csp = response.headers['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp, "Content Security Policy missing default-src directive")
        self.assertIn("script-src", csp, "Content Security Policy missing script-src directive")
        self.assertIn("style-src", csp, "Content Security Policy missing style-src directive")
        self.assertIn("img-src", csp, "Content Security Policy missing img-src directive")
        self.assertIn("connect-src", csp, "Content Security Policy missing connect-src directive")
        self.assertIn("font-src", csp, "Content Security Policy missing font-src directive")
        self.assertIn("object-src", csp, "Content Security Policy missing object-src directive")
        self.assertIn("media-src", csp, "Content Security Policy missing media-src directive")
        self.assertIn("frame-src", csp, "Content Security Policy missing frame-src directive")
    
    def test_x_content_type_options(self):
        """Test X-Content-Type-Options header."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify X-Content-Type-Options header is present
        self.assertIn('X-Content-Type-Options', response.headers, "X-Content-Type-Options header not present")
        
        # Verify X-Content-Type-Options header is set to nosniff
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff', "X-Content-Type-Options header not set to nosniff")
    
    def test_x_frame_options(self):
        """Test X-Frame-Options header."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify X-Frame-Options header is present
        self.assertIn('X-Frame-Options', response.headers, "X-Frame-Options header not present")
        
        # Verify X-Frame-Options header is set to DENY or SAMEORIGIN
        self.assertIn(response.headers['X-Frame-Options'], ['DENY', 'SAMEORIGIN'], "X-Frame-Options header not set to DENY or SAMEORIGIN")
    
    def test_strict_transport_security(self):
        """Test Strict-Transport-Security header."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify Strict-Transport-Security header is present
        self.assertIn('Strict-Transport-Security', response.headers, "Strict-Transport-Security header not present")
        
        # Verify Strict-Transport-Security header contains max-age directive
        hsts = response.headers['Strict-Transport-Security']
        self.assertIn("max-age=", hsts, "Strict-Transport-Security header missing max-age directive")
        
        # Verify max-age is at least 1 year (31536000 seconds)
        max_age = int(hsts.split("max-age=")[1].split(";")[0])
        self.assertGreaterEqual(max_age, 31536000, "Strict-Transport-Security max-age is less than 1 year")
    
    def test_referrer_policy(self):
        """Test Referrer-Policy header."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify Referrer-Policy header is present
        self.assertIn('Referrer-Policy', response.headers, "Referrer-Policy header not present")
        
        # Verify Referrer-Policy header is set to a secure value
        secure_values = ['no-referrer', 'no-referrer-when-downgrade', 'origin', 'origin-when-cross-origin', 'same-origin', 'strict-origin', 'strict-origin-when-cross-origin']
        self.assertIn(response.headers['Referrer-Policy'], secure_values, "Referrer-Policy header not set to a secure value")
    
    def test_feature_policy(self):
        """Test Feature-Policy/Permissions-Policy header."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify Feature-Policy or Permissions-Policy header is present
        self.assertTrue('Feature-Policy' in response.headers or 'Permissions-Policy' in response.headers, "Neither Feature-Policy nor Permissions-Policy header is present")
    
    def test_xss_protection(self):
        """Test XSS protection."""
        # Make request to base URL
        response = requests.get(self.base_url)
        
        # Verify X-XSS-Protection header is present
        self.assertIn('X-XSS-Protection', response.headers, "X-XSS-Protection header not present")
        
        # Verify X-XSS-Protection header is set to 1; mode=block
        self.assertEqual(response.headers['X-XSS-Protection'], '1; mode=block', "X-XSS-Protection header not set to 1; mode=block")
    
    def test_no_sensitive_information_in_html(self):
        """Test that no sensitive information is present in HTML."""
        # Get page source
        page_source = self.driver.page_source
        
        # Parse HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Check for sensitive information in comments
        comments = soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--'))
        for comment in comments:
            self.assertNotIn('password', comment.lower(), "Password found in HTML comment")
            self.assertNotIn('secret', comment.lower(), "Secret found in HTML comment")
            self.assertNotIn('api key', comment.lower(), "API key found in HTML comment")
            self.assertNotIn('token', comment.lower(), "Token found in HTML comment")
        
        # Check for sensitive information in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                self.assertNotIn('password', script.string.lower(), "Password found in script tag")
                self.assertNotIn('secret', script.string.lower(), "Secret found in script tag")
                self.assertNotIn('api key', script.string.lower(), "API key found in script tag")
                self.assertNotIn('token', script.string.lower(), "Token found in script tag")
    
    def test_no_sensitive_information_in_local_storage(self):
        """Test that no sensitive information is stored in local storage."""
        # Get all items in local storage
        local_storage = self.driver.execute_script("return Object.keys(localStorage);")
        
        # Check each item
        for key in local_storage:
            value = self.driver.execute_script(f"return localStorage.getItem('{key}');")
            
            # Check for sensitive information
            self.assertNotIn('password', key.lower(), "Password found in local storage key")
            self.assertNotIn('secret', key.lower(), "Secret found in local storage key")
            self.assertNotIn('api key', key.lower(), "API key found in local storage key")
            self.assertNotIn('token', key.lower(), "Token found in local storage key")
            
            if value:
                self.assertNotIn('password', value.lower(), "Password found in local storage value")
                self.assertNotIn('secret', value.lower(), "Secret found in local storage value")
                self.assertNotIn('api key', value.lower(), "API key found in local storage value")
    
    def test_no_sensitive_information_in_session_storage(self):
        """Test that no sensitive information is stored in session storage."""
        # Get all items in session storage
        session_storage = self.driver.execute_script("return Object.keys(sessionStorage);")
        
        # Check each item
        for key in session_storage:
            value = self.driver.execute_script(f"return sessionStorage.getItem('{key}');")
            
            # Check for sensitive information
            self.assertNotIn('password', key.lower(), "Password found in session storage key")
            self.assertNotIn('secret', key.lower(), "Secret found in session storage key")
            self.assertNotIn('api key', key.lower(), "API key found in session storage key")
            self.assertNotIn('token', key.lower(), "Token found in session storage key")
            
            if value:
                self.assertNotIn('password', value.lower(), "Password found in session storage value")
                self.assertNotIn('secret', value.lower(), "Secret found in session storage value")
                self.assertNotIn('api key', value.lower(), "API key found in session storage value")
    
    def test_no_sensitive_information_in_cookies(self):
        """Test that no sensitive information is stored in cookies."""
        # Get all cookies
        cookies = self.driver.get_cookies()
        
        # Check each cookie
        for cookie in cookies:
            # Check for sensitive information in cookie name
            self.assertNotIn('password', cookie['name'].lower(), "Password found in cookie name")
            self.assertNotIn('secret', cookie['name'].lower(), "Secret found in cookie name")
            self.assertNotIn('api key', cookie['name'].lower(), "API key found in cookie name")
            self.assertNotIn('token', cookie['name'].lower(), "Token found in cookie name")
            
            # Check for sensitive information in cookie value
            if 'value' in cookie and cookie['value']:
                self.assertNotIn('password', cookie['value'].lower(), "Password found in cookie value")
                self.assertNotIn('secret', cookie['value'].lower(), "Secret found in cookie value")
                self.assertNotIn('api key', cookie['value'].lower(), "API key found in cookie value")
    
    def test_secure_cookies(self):
        """Test that cookies are secure."""
        # Get all cookies
        cookies = self.driver.get_cookies()
        
        # Check each cookie
        for cookie in cookies:
            # Check if cookie is secure
            self.assertTrue(cookie.get('secure', False), f"Cookie '{cookie['name']}' is not secure")
            
            # Check if cookie has HttpOnly flag
            self.assertTrue(cookie.get('httpOnly', False), f"Cookie '{cookie['name']}' does not have HttpOnly flag")
            
            # Check if cookie has SameSite attribute
            self.assertIn('sameSite', cookie, f"Cookie '{cookie['name']}' does not have SameSite attribute")
            
            # Check if SameSite attribute is set to a secure value
            self.assertIn(cookie['sameSite'], ['Strict', 'Lax'], f"Cookie '{cookie['name']}' SameSite attribute not set to a secure value")
    
    def test_api_authentication(self):
        """Test API authentication."""
        # Make request to API without authentication
        response = requests.get(f"{self.api_base_url}/user")
        
        # Verify response status code is 401 Unauthorized
        self.assertEqual(response.status_code, 401, "API request without authentication did not return 401 Unauthorized")
    
    def test_api_authorization(self):
        """Test API authorization."""
        # Make request to admin API endpoint with regular user authentication
        headers = {
            'Authorization': 'Bearer regular-user-token'
        }
        response = requests.get(f"{self.api_base_url}/admin", headers=headers)
        
        # Verify response status code is 403 Forbidden
        self.assertEqual(response.status_code, 403, "API request with insufficient authorization did not return 403 Forbidden")
    
    def test_csrf_protection(self):
        """Test CSRF protection."""
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for login page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'login-form'))
        )
        
        # Find CSRF token
        csrf_token = self.driver.find_element(By.NAME, 'csrf_token').get_attribute('value')
        
        # Verify CSRF token is present
        self.assertIsNotNone(csrf_token, "CSRF token not found in login form")
        self.assertNotEqual(csrf_token, '', "CSRF token is empty")
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection."""
        # Navigate to search page
        self.driver.get(f"{self.base_url}/search")
        
        # Wait for search page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'search-form'))
        )
        
        # Find search input
        search_input = self.driver.find_element(By.ID, 'search-input')
        
        # Enter SQL injection payload
        search_input.send_keys("' OR 1=1; --")
        
        # Submit search form
        search_input.send_keys(Keys.ENTER)
        
        # Wait for search results
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'search-results'))
        )
        
        # Verify search results do not contain all records
        search_results = self.driver.find_element(By.ID, 'search-results')
        self.assertNotIn('all records', search_results.text.lower(), "SQL injection protection failed")
    
    def test_xss_protection_in_forms(self):
        """Test XSS protection in forms."""
        # Navigate to profile page
        self.driver.get(f"{self.base_url}/profile")
        
        # Wait for profile page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'profile-form'))
        )
        
        # Find name input
        name_input = self.driver.find_element(By.ID, 'name-input')
        
        # Enter XSS payload
        xss_payload = "<script>alert('XSS')</script>"
        name_input.clear()
        name_input.send_keys(xss_payload)
        
        # Submit profile form
        name_input.send_keys(Keys.ENTER)
        
        # Wait for profile to update
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'profile-updated'))
        )
        
        # Navigate to profile page again to see the updated profile
        self.driver.get(f"{self.base_url}/profile")
        
        # Wait for profile page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'profile-form'))
        )
        
        # Find displayed name
        displayed_name = self.driver.find_element(By.ID, 'displayed-name')
        
        # Verify XSS payload is escaped
        self.assertNotIn('<script>', displayed_name.text, "XSS payload not escaped")
        self.assertIn('&lt;script&gt;', displayed_name.get_attribute('innerHTML'), "XSS payload not escaped")
    
    def test_secure_websocket_connection(self):
        """Test secure WebSocket connection."""
        # Execute JavaScript to check WebSocket connection
        websocket_protocol = self.driver.execute_script("""
            var socket = new WebSocket((window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws');
            return socket.url.split(':')[0];
        """)
        
        # Verify WebSocket connection uses secure protocol
        self.assertEqual(websocket_protocol, 'wss', "WebSocket connection not using secure protocol")

def run_tests():
    """Run the security tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UIUXLayerSecurityTest))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
