"""
Accessibility Test Suite - Tests for accessibility compliance in the UI/UX Layer.

This module provides comprehensive accessibility tests for the UI/UX Layer,
ensuring that all components meet accessibility standards and provide an
inclusive experience for all users.
"""

import os
import sys
import json
import logging
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from axe_selenium_python import Axe

class UIUXLayerAccessibilityTest(unittest.TestCase):
    """Accessibility test case for the UI/UX Layer."""
    
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
        
        # Initialize axe
        self.axe = Axe(self.driver)
        
        # Inject axe-core javascript into page
        self.axe.inject()
    
    def test_welcome_page_accessibility(self):
        """Test accessibility of the welcome page."""
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_dashboard_page_accessibility(self):
        """Test accessibility of the dashboard page."""
        # Navigate to dashboard page
        dashboard_link = self.driver.find_element(By.ID, 'dashboard-link')
        dashboard_link.click()
        
        # Wait for dashboard page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'dashboard-page'))
        )
        
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_digital_twin_explorer_accessibility(self):
        """Test accessibility of the digital twin explorer page."""
        # Navigate to digital twin explorer page
        digital_twin_explorer_link = self.driver.find_element(By.ID, 'digital-twin-explorer-link')
        digital_twin_explorer_link.click()
        
        # Wait for digital twin explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'digital-twin-explorer-page'))
        )
        
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_workflow_explorer_accessibility(self):
        """Test accessibility of the workflow explorer page."""
        # Navigate to workflow explorer page
        workflow_explorer_link = self.driver.find_element(By.ID, 'workflow-explorer-link')
        workflow_explorer_link.click()
        
        # Wait for workflow explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'workflow-explorer-page'))
        )
        
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_agent_explorer_accessibility(self):
        """Test accessibility of the agent explorer page."""
        # Navigate to agent explorer page
        agent_explorer_link = self.driver.find_element(By.ID, 'agent-explorer-link')
        agent_explorer_link.click()
        
        # Wait for agent explorer page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'agent-explorer-page'))
        )
        
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_settings_page_accessibility(self):
        """Test accessibility of the settings page."""
        # Navigate to settings page
        settings_link = self.driver.find_element(By.ID, 'settings-link')
        settings_link.click()
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Run axe against the page
        results = self.axe.run()
        
        # Check for violations
        violations = results["violations"]
        
        # Log violations for debugging
        if violations:
            for violation in violations:
                logging.error(f"Accessibility violation: {violation['id']} - {violation['description']}")
                logging.error(f"Impact: {violation['impact']}")
                logging.error(f"Help: {violation['help']}")
                logging.error(f"Help URL: {violation['helpUrl']}")
                logging.error("Affected elements:")
                for node in violation["nodes"]:
                    logging.error(f"  {node['html']}")
                    logging.error(f"  {node['target']}")
        
        # Assert no violations
        self.assertEqual(len(violations), 0, f"Found {len(violations)} accessibility violations")
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation."""
        # Focus on first focusable element
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.TAB)
        
        # Get all focusable elements
        focusable_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')
        
        # Verify at least one element is focusable
        self.assertGreater(len(focusable_elements), 0, "No focusable elements found")
        
        # Navigate through all focusable elements using Tab key
        for _ in range(len(focusable_elements)):
            # Get currently focused element
            active_element = self.driver.switch_to.active_element
            
            # Verify element is focused
            self.assertIsNotNone(active_element, "No element is focused")
            
            # Press Tab key to move to next focusable element
            active_element.send_keys(Keys.TAB)
    
    def test_screen_reader_compatibility(self):
        """Test screen reader compatibility."""
        # Check for ARIA attributes on key elements
        
        # Universal Skin Shell
        universal_skin_shell = self.driver.find_element(By.ID, 'universal-skin-shell')
        self.assertIsNotNone(universal_skin_shell.get_attribute('role'), "Universal Skin Shell missing role attribute")
        
        # Layer Avatars
        layer_avatars = self.driver.find_elements(By.CLASS_NAME, 'layer-avatar')
        for avatar in layer_avatars:
            self.assertIsNotNone(avatar.get_attribute('aria-label'), "Layer Avatar missing aria-label attribute")
        
        # Capsule Dock
        capsule_dock = self.driver.find_element(By.ID, 'capsule-dock')
        self.assertIsNotNone(capsule_dock.get_attribute('role'), "Capsule Dock missing role attribute")
        self.assertIsNotNone(capsule_dock.get_attribute('aria-label'), "Capsule Dock missing aria-label attribute")
        
        # Timeline View
        timeline_view = self.driver.find_element(By.ID, 'timeline-view')
        self.assertIsNotNone(timeline_view.get_attribute('role'), "Timeline View missing role attribute")
        self.assertIsNotNone(timeline_view.get_attribute('aria-label'), "Timeline View missing aria-label attribute")
        
        # Mission Deck
        mission_deck = self.driver.find_element(By.ID, 'mission-deck')
        self.assertIsNotNone(mission_deck.get_attribute('role'), "Mission Deck missing role attribute")
        self.assertIsNotNone(mission_deck.get_attribute('aria-label'), "Mission Deck missing aria-label attribute")
    
    def test_high_contrast_mode(self):
        """Test high contrast mode."""
        # Navigate to settings page
        settings_link = self.driver.find_element(By.ID, 'settings-link')
        settings_link.click()
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Find accessibility settings
        accessibility_settings = self.driver.find_element(By.ID, 'accessibility-settings')
        
        # Find high contrast toggle
        high_contrast_toggle = accessibility_settings.find_element(By.ID, 'high-contrast-toggle')
        
        # Enable high contrast mode
        if not high_contrast_toggle.is_selected():
            high_contrast_toggle.click()
        
        # Wait for high contrast mode to be applied
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body.high-contrast'))
        )
        
        # Verify high contrast mode is applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('high-contrast', body.get_attribute('class'), "High contrast mode not applied")
        
        # Navigate back to welcome page
        welcome_link = self.driver.find_element(By.ID, 'welcome-link')
        welcome_link.click()
        
        # Wait for welcome page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Verify high contrast mode is still applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('high-contrast', body.get_attribute('class'), "High contrast mode not persisted")
    
    def test_reduced_motion_mode(self):
        """Test reduced motion mode."""
        # Navigate to settings page
        settings_link = self.driver.find_element(By.ID, 'settings-link')
        settings_link.click()
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Find accessibility settings
        accessibility_settings = self.driver.find_element(By.ID, 'accessibility-settings')
        
        # Find reduced motion toggle
        reduced_motion_toggle = accessibility_settings.find_element(By.ID, 'reduced-motion-toggle')
        
        # Enable reduced motion mode
        if not reduced_motion_toggle.is_selected():
            reduced_motion_toggle.click()
        
        # Wait for reduced motion mode to be applied
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body.reduced-motion'))
        )
        
        # Verify reduced motion mode is applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('reduced-motion', body.get_attribute('class'), "Reduced motion mode not applied")
        
        # Navigate back to welcome page
        welcome_link = self.driver.find_element(By.ID, 'welcome-link')
        welcome_link.click()
        
        # Wait for welcome page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Verify reduced motion mode is still applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('reduced-motion', body.get_attribute('class'), "Reduced motion mode not persisted")
    
    def test_text_scaling(self):
        """Test text scaling."""
        # Navigate to settings page
        settings_link = self.driver.find_element(By.ID, 'settings-link')
        settings_link.click()
        
        # Wait for settings page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'settings-page'))
        )
        
        # Find accessibility settings
        accessibility_settings = self.driver.find_element(By.ID, 'accessibility-settings')
        
        # Find text size slider
        text_size_slider = accessibility_settings.find_element(By.ID, 'text-size-slider')
        
        # Set text size to large
        self.driver.execute_script("arguments[0].value = 2;", text_size_slider)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { 'bubbles': true }));", text_size_slider)
        
        # Wait for text size to be applied
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body.text-size-large'))
        )
        
        # Verify text size is applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('text-size-large', body.get_attribute('class'), "Large text size not applied")
        
        # Navigate back to welcome page
        welcome_link = self.driver.find_element(By.ID, 'welcome-link')
        welcome_link.click()
        
        # Wait for welcome page to load
        WebDriverWait(self.driver, self.wait_time).until(
            EC.presence_of_element_located((By.ID, 'universal-skin-shell'))
        )
        
        # Verify text size is still applied
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.assertIn('text-size-large', body.get_attribute('class'), "Large text size not persisted")

def run_tests():
    """Run the accessibility tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(UIUXLayerAccessibilityTest))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests
    run_tests()
