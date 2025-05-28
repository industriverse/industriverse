"""
Settings Page Component - The settings page for the Industriverse UI/UX Layer

This module implements the settings page component for the Industriverse UI/UX Layer,
providing user configuration options for the Universal Skin experience.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Set, Union, Tuple
import json
import os
import time
import uuid
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)

class SettingsPage:
    """
    Settings Page Component for the Industriverse UI/UX Layer.
    
    This class implements the settings page component, providing user configuration
    options for the Universal Skin experience, including theme, accessibility,
    notification preferences, and device-specific settings.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Settings Page Component with optional configuration."""
        self.config = config or {}
        self.universal_skin_shell = None
        self.theme_manager = None
        self.accessibility_manager = None
        self.device_adapter = None
        self.event_subscribers = {}
        self.settings_categories = []
        self.user_preferences = {}
        self.device_settings = {}
        self.notification_settings = {}
        self.accessibility_settings = {}
        self.security_settings = {}
        self.avatar_settings = {}
        self.capsule_settings = {}
        
        logger.info("Settings Page Component initialized")
    
    def initialize(self, universal_skin_shell=None, theme_manager=None, accessibility_manager=None, device_adapter=None):
        """Initialize the Settings Page Component and connect to required services."""
        logger.info("Initializing Settings Page Component")
        
        # Store references to required services
        self.universal_skin_shell = universal_skin_shell
        self.theme_manager = theme_manager
        self.accessibility_manager = accessibility_manager
        self.device_adapter = device_adapter
        
        # Initialize settings categories
        self._initialize_settings_categories()
        
        # Initialize user preferences
        self._initialize_user_preferences()
        
        # Initialize device settings
        self._initialize_device_settings()
        
        # Initialize notification settings
        self._initialize_notification_settings()
        
        # Initialize accessibility settings
        self._initialize_accessibility_settings()
        
        # Initialize security settings
        self._initialize_security_settings()
        
        # Initialize avatar settings
        self._initialize_avatar_settings()
        
        # Initialize capsule settings
        self._initialize_capsule_settings()
        
        logger.info("Settings Page Component initialization complete")
        return True
    
    def _initialize_settings_categories(self):
        """Initialize settings categories."""
        logger.info("Initializing settings categories")
        
        # Define default settings categories
        self.settings_categories = [
            {
                "id": "appearance",
                "name": "Appearance",
                "icon": "appearance_icon",
                "description": "Customize the look and feel of the Universal Skin",
                "order": 1
            },
            {
                "id": "accessibility",
                "name": "Accessibility",
                "icon": "accessibility_icon",
                "description": "Configure accessibility features for the Universal Skin",
                "order": 2
            },
            {
                "id": "notifications",
                "name": "Notifications",
                "icon": "notifications_icon",
                "description": "Manage notification preferences for the Universal Skin",
                "order": 3
            },
            {
                "id": "devices",
                "name": "Devices & Adaptation",
                "icon": "devices_icon",
                "description": "Configure device-specific settings for the Universal Skin",
                "order": 4
            },
            {
                "id": "security",
                "name": "Security & Privacy",
                "icon": "security_icon",
                "description": "Manage security and privacy settings for the Universal Skin",
                "order": 5
            },
            {
                "id": "avatars",
                "name": "Layer Avatars",
                "icon": "avatars_icon",
                "description": "Customize layer avatar appearance and behavior",
                "order": 6
            },
            {
                "id": "capsules",
                "name": "Agent Capsules",
                "icon": "capsules_icon",
                "description": "Configure agent capsule behavior and appearance",
                "order": 7
            },
            {
                "id": "advanced",
                "name": "Advanced",
                "icon": "advanced_icon",
                "description": "Configure advanced settings for the Universal Skin",
                "order": 8
            }
        ]
        
        # Add custom settings categories from config
        config_categories = self.config.get("settings_categories", [])
        for category in config_categories:
            # Check if category with same ID already exists
            existing_category_index = next((i for i, c in enumerate(self.settings_categories) if c["id"] == category["id"]), None)
            
            if existing_category_index is not None:
                # Update existing category
                self.settings_categories[existing_category_index].update(category)
            else:
                # Add new category
                self.settings_categories.append(category)
        
        # Sort categories by order
        self.settings_categories.sort(key=lambda c: c.get("order", 999))
        
        logger.info("Settings categories initialized: %d categories defined", len(self.settings_categories))
    
    def _initialize_user_preferences(self):
        """Initialize user preferences."""
        logger.info("Initializing user preferences")
        
        # Define default user preferences
        self.user_preferences = {
            "theme": {
                "color_scheme": {
                    "value": "system",
                    "options": [
                        {"id": "system", "name": "System Default"},
                        {"id": "light", "name": "Light"},
                        {"id": "dark", "name": "Dark"},
                        {"id": "high_contrast", "name": "High Contrast"}
                    ],
                    "type": "select",
                    "label": "Color Scheme",
                    "description": "Choose the color scheme for the Universal Skin",
                    "category": "appearance"
                },
                "accent_color": {
                    "value": "blue",
                    "options": [
                        {"id": "blue", "name": "Blue", "color": "#0066cc"},
                        {"id": "green", "name": "Green", "color": "#00cc66"},
                        {"id": "purple", "name": "Purple", "color": "#6600cc"},
                        {"id": "orange", "name": "Orange", "color": "#cc6600"},
                        {"id": "red", "name": "Red", "color": "#cc0000"}
                    ],
                    "type": "color",
                    "label": "Accent Color",
                    "description": "Choose the accent color for the Universal Skin",
                    "category": "appearance"
                },
                "font_family": {
                    "value": "system",
                    "options": [
                        {"id": "system", "name": "System Default"},
                        {"id": "sans_serif", "name": "Sans Serif"},
                        {"id": "serif", "name": "Serif"},
                        {"id": "monospace", "name": "Monospace"}
                    ],
                    "type": "select",
                    "label": "Font Family",
                    "description": "Choose the font family for the Universal Skin",
                    "category": "appearance"
                },
                "font_size": {
                    "value": "medium",
                    "options": [
                        {"id": "small", "name": "Small"},
                        {"id": "medium", "name": "Medium"},
                        {"id": "large", "name": "Large"},
                        {"id": "x_large", "name": "Extra Large"}
                    ],
                    "type": "select",
                    "label": "Font Size",
                    "description": "Choose the font size for the Universal Skin",
                    "category": "appearance"
                },
                "animation_level": {
                    "value": "medium",
                    "options": [
                        {"id": "none", "name": "None"},
                        {"id": "minimal", "name": "Minimal"},
                        {"id": "medium", "name": "Medium"},
                        {"id": "full", "name": "Full"}
                    ],
                    "type": "select",
                    "label": "Animation Level",
                    "description": "Choose the animation level for the Universal Skin",
                    "category": "appearance"
                },
                "density": {
                    "value": "medium",
                    "options": [
                        {"id": "compact", "name": "Compact"},
                        {"id": "medium", "name": "Medium"},
                        {"id": "comfortable", "name": "Comfortable"}
                    ],
                    "type": "select",
                    "label": "Interface Density",
                    "description": "Choose the interface density for the Universal Skin",
                    "category": "appearance"
                }
            },
            "layout": {
                "dashboard_layout": {
                    "value": "grid",
                    "options": [
                        {"id": "grid", "name": "Grid"},
                        {"id": "list", "name": "List"},
                        {"id": "cards", "name": "Cards"}
                    ],
                    "type": "select",
                    "label": "Dashboard Layout",
                    "description": "Choose the layout for the dashboard",
                    "category": "appearance"
                },
                "sidebar_position": {
                    "value": "left",
                    "options": [
                        {"id": "left", "name": "Left"},
                        {"id": "right", "name": "Right"}
                    ],
                    "type": "select",
                    "label": "Sidebar Position",
                    "description": "Choose the position for the sidebar",
                    "category": "appearance"
                },
                "show_welcome_message": {
                    "value": True,
                    "type": "boolean",
                    "label": "Show Welcome Message",
                    "description": "Show welcome message on startup",
                    "category": "appearance"
                },
                "show_tips": {
                    "value": True,
                    "type": "boolean",
                    "label": "Show Tips",
                    "description": "Show tips and hints throughout the interface",
                    "category": "appearance"
                },
                "show_metrics": {
                    "value": True,
                    "type": "boolean",
                    "label": "Show Metrics",
                    "description": "Show metrics and statistics throughout the interface",
                    "category": "appearance"
                }
            },
            "behavior": {
                "auto_refresh": {
                    "value": "60",
                    "options": [
                        {"id": "0", "name": "Never"},
                        {"id": "30", "name": "Every 30 seconds"},
                        {"id": "60", "name": "Every minute"},
                        {"id": "300", "name": "Every 5 minutes"},
                        {"id": "600", "name": "Every 10 minutes"}
                    ],
                    "type": "select",
                    "label": "Auto Refresh",
                    "description": "Automatically refresh data",
                    "category": "advanced"
                },
                "default_view": {
                    "value": "dashboard",
                    "options": [
                        {"id": "dashboard", "name": "Dashboard"},
                        {"id": "workflows", "name": "Workflows"},
                        {"id": "digital_twins", "name": "Digital Twins"},
                        {"id": "capsules", "name": "Agent Capsules"}
                    ],
                    "type": "select",
                    "label": "Default View",
                    "description": "Choose the default view when opening the application",
                    "category": "advanced"
                },
                "confirm_actions": {
                    "value": True,
                    "type": "boolean",
                    "label": "Confirm Actions",
                    "description": "Confirm before performing potentially destructive actions",
                    "category": "advanced"
                },
                "save_session": {
                    "value": True,
                    "type": "boolean",
                    "label": "Save Session",
                    "description": "Save session state between visits",
                    "category": "advanced"
                }
            }
        }
        
        # Update user preferences from config
        config_preferences = self.config.get("user_preferences", {})
        for category, settings in config_preferences.items():
            if category in self.user_preferences and isinstance(settings, dict) and isinstance(self.user_preferences[category], dict):
                for setting_id, setting_value in settings.items():
                    if setting_id in self.user_preferences[category]:
                        if isinstance(setting_value, dict) and isinstance(self.user_preferences[category][setting_id], dict):
                            self.user_preferences[category][setting_id].update(setting_value)
                        else:
                            self.user_preferences[category][setting_id] = setting_value
                    else:
                        self.user_preferences[category][setting_id] = setting_value
            else:
                self.user_preferences[category] = settings
        
        logger.info("User preferences initialized")
    
    def _initialize_device_settings(self):
        """Initialize device settings."""
        logger.info("Initializing device settings")
        
        # Define default device settings
        self.device_settings = {
            "device_type": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "desktop", "name": "Desktop"},
                    {"id": "tablet", "name": "Tablet"},
                    {"id": "mobile", "name": "Mobile"},
                    {"id": "ar_vr", "name": "AR/VR"}
                ],
                "type": "select",
                "label": "Device Type",
                "description": "Choose the device type for the Universal Skin",
                "category": "devices"
            },
            "orientation": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "portrait", "name": "Portrait"},
                    {"id": "landscape", "name": "Landscape"}
                ],
                "type": "select",
                "label": "Orientation",
                "description": "Choose the orientation for the Universal Skin",
                "category": "devices"
            },
            "touch_optimization": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Touch Optimization",
                "description": "Optimize the interface for touch input",
                "category": "devices"
            },
            "offline_mode": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Offline Mode",
                "description": "Enable offline mode for the Universal Skin",
                "category": "devices"
            },
            "sync_settings": {
                "value": True,
                "type": "boolean",
                "label": "Sync Settings",
                "description": "Synchronize settings across devices",
                "category": "devices"
            },
            "enable_gestures": {
                "value": True,
                "type": "boolean",
                "label": "Enable Gestures",
                "description": "Enable gesture controls for the Universal Skin",
                "category": "devices"
            },
            "enable_voice": {
                "value": True,
                "type": "boolean",
                "label": "Enable Voice",
                "description": "Enable voice controls for the Universal Skin",
                "category": "devices"
            },
            "enable_haptics": {
                "value": True,
                "type": "boolean",
                "label": "Enable Haptics",
                "description": "Enable haptic feedback for the Universal Skin",
                "category": "devices"
            },
            "bitnet_ui_pack": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "BitNet UI Pack",
                "description": "Enable BitNet UI Pack for edge devices",
                "category": "devices"
            },
            "ar_vr_mode": {
                "value": "auto",
                "options": [
                    {"id": "auto", "name": "Auto-detect"},
                    {"id": "ar", "name": "Augmented Reality"},
                    {"id": "vr", "name": "Virtual Reality"},
                    {"id": "mr", "name": "Mixed Reality"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "AR/VR Mode",
                "description": "Configure AR/VR mode for the Universal Skin",
                "category": "devices"
            }
        }
        
        # Update device settings from config
        config_device_settings = self.config.get("device_settings", {})
        for setting_id, setting_value in config_device_settings.items():
            if setting_id in self.device_settings and isinstance(setting_value, dict) and isinstance(self.device_settings[setting_id], dict):
                self.device_settings[setting_id].update(setting_value)
            else:
                self.device_settings[setting_id] = setting_value
        
        logger.info("Device settings initialized")
    
    def _initialize_notification_settings(self):
        """Initialize notification settings."""
        logger.info("Initializing notification settings")
        
        # Define default notification settings
        self.notification_settings = {
            "alert_notifications": {
                "value": True,
                "type": "boolean",
                "label": "Alert Notifications",
                "description": "Receive notifications for alerts",
                "category": "notifications"
            },
            "workflow_notifications": {
                "value": True,
                "type": "boolean",
                "label": "Workflow Notifications",
                "description": "Receive notifications for workflow events",
                "category": "notifications"
            },
            "insight_notifications": {
                "value": True,
                "type": "boolean",
                "label": "Insight Notifications",
                "description": "Receive notifications for new insights",
                "category": "notifications"
            },
            "system_notifications": {
                "value": True,
                "type": "boolean",
                "label": "System Notifications",
                "description": "Receive notifications for system events",
                "category": "notifications"
            },
            "capsule_notifications": {
                "value": True,
                "type": "boolean",
                "label": "Capsule Notifications",
                "description": "Receive notifications for agent capsule events",
                "category": "notifications"
            },
            "notification_sound": {
                "value": True,
                "type": "boolean",
                "label": "Notification Sound",
                "description": "Play sound for notifications",
                "category": "notifications"
            },
            "notification_vibration": {
                "value": True,
                "type": "boolean",
                "label": "Notification Vibration",
                "description": "Enable vibration for notifications",
                "category": "notifications"
            },
            "notification_priority": {
                "value": "medium",
                "options": [
                    {"id": "low", "name": "Low"},
                    {"id": "medium", "name": "Medium"},
                    {"id": "high", "name": "High"}
                ],
                "type": "select",
                "label": "Notification Priority",
                "description": "Set the priority level for notifications",
                "category": "notifications"
            },
            "do_not_disturb": {
                "value": False,
                "type": "boolean",
                "label": "Do Not Disturb",
                "description": "Disable all notifications",
                "category": "notifications"
            },
            "do_not_disturb_schedule": {
                "value": {
                    "enabled": False,
                    "start_time": "22:00",
                    "end_time": "08:00"
                },
                "type": "schedule",
                "label": "Do Not Disturb Schedule",
                "description": "Schedule when Do Not Disturb is active",
                "category": "notifications"
            },
            "notification_channels": {
                "value": {
                    "in_app": True,
                    "email": False,
                    "sms": False,
                    "push": True
                },
                "type": "channels",
                "label": "Notification Channels",
                "description": "Configure notification channels",
                "category": "notifications"
            }
        }
        
        # Update notification settings from config
        config_notification_settings = self.config.get("notification_settings", {})
        for setting_id, setting_value in config_notification_settings.items():
            if setting_id in self.notification_settings and isinstance(setting_value, dict) and isinstance(self.notification_settings[setting_id], dict):
                self.notification_settings[setting_id].update(setting_value)
            else:
                self.notification_settings[setting_id] = setting_value
        
        logger.info("Notification settings initialized")
    
    def _initialize_accessibility_settings(self):
        """Initialize accessibility settings."""
        logger.info("Initializing accessibility settings")
        
        # Define default accessibility settings
        self.accessibility_settings = {
            "screen_reader": {
                "value": False,
                "type": "boolean",
                "label": "Screen Reader",
                "description": "Enable screen reader support",
                "category": "accessibility"
            },
            "high_contrast": {
                "value": False,
                "type": "boolean",
                "label": "High Contrast",
                "description": "Enable high contrast mode",
                "category": "accessibility"
            },
            "reduced_motion": {
                "value": False,
                "type": "boolean",
                "label": "Reduced Motion",
                "description": "Reduce or eliminate motion effects",
                "category": "accessibility"
            },
            "keyboard_navigation": {
                "value": True,
                "type": "boolean",
                "label": "Keyboard Navigation",
                "description": "Enable keyboard navigation",
                "category": "accessibility"
            },
            "text_to_speech": {
                "value": False,
                "type": "boolean",
                "label": "Text to Speech",
                "description": "Enable text to speech for content",
                "category": "accessibility"
            },
            "speech_to_text": {
                "value": False,
                "type": "boolean",
                "label": "Speech to Text",
                "description": "Enable speech to text for input",
                "category": "accessibility"
            },
            "color_blind_mode": {
                "value": "none",
                "options": [
                    {"id": "none", "name": "None"},
                    {"id": "protanopia", "name": "Protanopia (Red-Blind)"},
                    {"id": "deuteranopia", "name": "Deuteranopia (Green-Blind)"},
                    {"id": "tritanopia", "name": "Tritanopia (Blue-Blind)"},
                    {"id": "achromatopsia", "name": "Achromatopsia (Color-Blind)"}
                ],
                "type": "select",
                "label": "Color Blind Mode",
                "description": "Adjust colors for color blindness",
                "category": "accessibility"
            },
            "text_spacing": {
                "value": "normal",
                "options": [
                    {"id": "normal", "name": "Normal"},
                    {"id": "wide", "name": "Wide"},
                    {"id": "wider", "name": "Wider"}
                ],
                "type": "select",
                "label": "Text Spacing",
                "description": "Adjust spacing between text characters",
                "category": "accessibility"
            },
            "line_height": {
                "value": "normal",
                "options": [
                    {"id": "normal", "name": "Normal"},
                    {"id": "large", "name": "Large"},
                    {"id": "x_large", "name": "Extra Large"}
                ],
                "type": "select",
                "label": "Line Height",
                "description": "Adjust spacing between text lines",
                "category": "accessibility"
            },
            "focus_indicators": {
                "value": "normal",
                "options": [
                    {"id": "normal", "name": "Normal"},
                    {"id": "enhanced", "name": "Enhanced"},
                    {"id": "high_visibility", "name": "High Visibility"}
                ],
                "type": "select",
                "label": "Focus Indicators",
                "description": "Adjust visibility of focus indicators",
                "category": "accessibility"
            }
        }
        
        # Update accessibility settings from config
        config_accessibility_settings = self.config.get("accessibility_settings", {})
        for setting_id, setting_value in config_accessibility_settings.items():
            if setting_id in self.accessibility_settings and isinstance(setting_value, dict) and isinstance(self.accessibility_settings[setting_id], dict):
                self.accessibility_settings[setting_id].update(setting_value)
            else:
                self.accessibility_settings[setting_id] = setting_value
        
        logger.info("Accessibility settings initialized")
    
    def _initialize_security_settings(self):
        """Initialize security settings."""
        logger.info("Initializing security settings")
        
        # Define default security settings
        self.security_settings = {
            "trust_visualization": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Trust Visualization",
                "description": "Visualize trust scores and pathways",
                "category": "security"
            },
            "trust_threshold": {
                "value": "medium",
                "options": [
                    {"id": "low", "name": "Low"},
                    {"id": "medium", "name": "Medium"},
                    {"id": "high", "name": "High"},
                    {"id": "very_high", "name": "Very High"}
                ],
                "type": "select",
                "label": "Trust Threshold",
                "description": "Set the minimum trust threshold for agent actions",
                "category": "security"
            },
            "data_privacy": {
                "value": "standard",
                "options": [
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "standard", "name": "Standard"},
                    {"id": "enhanced", "name": "Enhanced"},
                    {"id": "maximum", "name": "Maximum"}
                ],
                "type": "select",
                "label": "Data Privacy",
                "description": "Configure data privacy settings",
                "category": "security"
            },
            "telemetry": {
                "value": "anonymous",
                "options": [
                    {"id": "full", "name": "Full"},
                    {"id": "anonymous", "name": "Anonymous"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Telemetry",
                "description": "Configure telemetry data collection",
                "category": "security"
            },
            "action_confirmation": {
                "value": "medium",
                "options": [
                    {"id": "low", "name": "Low"},
                    {"id": "medium", "name": "Medium"},
                    {"id": "high", "name": "High"}
                ],
                "type": "select",
                "label": "Action Confirmation",
                "description": "Configure confirmation level for agent actions",
                "category": "security"
            },
            "session_timeout": {
                "value": "30",
                "options": [
                    {"id": "5", "name": "5 minutes"},
                    {"id": "15", "name": "15 minutes"},
                    {"id": "30", "name": "30 minutes"},
                    {"id": "60", "name": "1 hour"},
                    {"id": "never", "name": "Never"}
                ],
                "type": "select",
                "label": "Session Timeout",
                "description": "Set the session timeout period",
                "category": "security"
            },
            "audit_logging": {
                "value": "standard",
                "options": [
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "standard", "name": "Standard"},
                    {"id": "detailed", "name": "Detailed"}
                ],
                "type": "select",
                "label": "Audit Logging",
                "description": "Configure audit logging level",
                "category": "security"
            },
            "zk_attestation_visibility": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "ZK Attestation Visibility",
                "description": "Configure visibility of zero-knowledge attestations",
                "category": "security"
            }
        }
        
        # Update security settings from config
        config_security_settings = self.config.get("security_settings", {})
        for setting_id, setting_value in config_security_settings.items():
            if setting_id in self.security_settings and isinstance(setting_value, dict) and isinstance(self.security_settings[setting_id], dict):
                self.security_settings[setting_id].update(setting_value)
            else:
                self.security_settings[setting_id] = setting_value
        
        logger.info("Security settings initialized")
    
    def _initialize_avatar_settings(self):
        """Initialize avatar settings."""
        logger.info("Initializing avatar settings")
        
        # Define default avatar settings
        self.avatar_settings = {
            "avatar_visibility": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Avatar Visibility",
                "description": "Configure visibility of layer avatars",
                "category": "avatars"
            },
            "avatar_animation": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Avatar Animation",
                "description": "Configure animation level for layer avatars",
                "category": "avatars"
            },
            "avatar_interaction": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Avatar Interaction",
                "description": "Configure interaction level with layer avatars",
                "category": "avatars"
            },
            "avatar_personality": {
                "value": "standard",
                "options": [
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "standard", "name": "Standard"},
                    {"id": "enhanced", "name": "Enhanced"}
                ],
                "type": "select",
                "label": "Avatar Personality",
                "description": "Configure personality level for layer avatars",
                "category": "avatars"
            },
            "avatar_style": {
                "value": "default",
                "options": [
                    {"id": "default", "name": "Default"},
                    {"id": "abstract", "name": "Abstract"},
                    {"id": "realistic", "name": "Realistic"},
                    {"id": "stylized", "name": "Stylized"},
                    {"id": "minimal", "name": "Minimal"}
                ],
                "type": "select",
                "label": "Avatar Style",
                "description": "Configure visual style for layer avatars",
                "category": "avatars"
            },
            "data_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Data Layer Avatar",
                "description": "Configure the Data Layer avatar",
                "category": "avatars"
            },
            "core_ai_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Core AI Layer Avatar",
                "description": "Configure the Core AI Layer avatar",
                "category": "avatars"
            },
            "generative_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Generative Layer Avatar",
                "description": "Configure the Generative Layer avatar",
                "category": "avatars"
            },
            "application_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Application Layer Avatar",
                "description": "Configure the Application Layer avatar",
                "category": "avatars"
            },
            "protocol_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Protocol Layer Avatar",
                "description": "Configure the Protocol Layer avatar",
                "category": "avatars"
            },
            "workflow_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Workflow Layer Avatar",
                "description": "Configure the Workflow Layer avatar",
                "category": "avatars"
            },
            "ui_ux_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "UI/UX Layer Avatar",
                "description": "Configure the UI/UX Layer avatar",
                "category": "avatars"
            },
            "security_layer_avatar": {
                "value": {
                    "enabled": True,
                    "style": "default",
                    "personality": "standard"
                },
                "type": "avatar_config",
                "label": "Security Layer Avatar",
                "description": "Configure the Security Layer avatar",
                "category": "avatars"
            }
        }
        
        # Update avatar settings from config
        config_avatar_settings = self.config.get("avatar_settings", {})
        for setting_id, setting_value in config_avatar_settings.items():
            if setting_id in self.avatar_settings and isinstance(setting_value, dict) and isinstance(self.avatar_settings[setting_id], dict):
                self.avatar_settings[setting_id].update(setting_value)
            else:
                self.avatar_settings[setting_id] = setting_value
        
        logger.info("Avatar settings initialized")
    
    def _initialize_capsule_settings(self):
        """Initialize capsule settings."""
        logger.info("Initializing capsule settings")
        
        # Define default capsule settings
        self.capsule_settings = {
            "capsule_visibility": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Visibility",
                "description": "Configure visibility of agent capsules",
                "category": "capsules"
            },
            "capsule_animation": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Animation",
                "description": "Configure animation level for agent capsules",
                "category": "capsules"
            },
            "capsule_interaction": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Interaction",
                "description": "Configure interaction level with agent capsules",
                "category": "capsules"
            },
            "capsule_style": {
                "value": "default",
                "options": [
                    {"id": "default", "name": "Default"},
                    {"id": "abstract", "name": "Abstract"},
                    {"id": "realistic", "name": "Realistic"},
                    {"id": "stylized", "name": "Stylized"},
                    {"id": "minimal", "name": "Minimal"}
                ],
                "type": "select",
                "label": "Capsule Style",
                "description": "Configure visual style for agent capsules",
                "category": "capsules"
            },
            "capsule_dock": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "auto_hide", "name": "Auto-hide"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Dock",
                "description": "Configure the capsule dock behavior",
                "category": "capsules"
            },
            "capsule_notifications": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Notifications",
                "description": "Configure notifications from agent capsules",
                "category": "capsules"
            },
            "capsule_trust_visualization": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Trust Visualization",
                "description": "Configure trust visualization for agent capsules",
                "category": "capsules"
            },
            "capsule_context_awareness": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Context Awareness",
                "description": "Configure context awareness for agent capsules",
                "category": "capsules"
            },
            "capsule_export": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "restricted", "name": "Restricted"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Export",
                "description": "Configure export capabilities for agent capsules",
                "category": "capsules"
            },
            "capsule_memory": {
                "value": "enabled",
                "options": [
                    {"id": "enabled", "name": "Enabled"},
                    {"id": "minimal", "name": "Minimal"},
                    {"id": "disabled", "name": "Disabled"}
                ],
                "type": "select",
                "label": "Capsule Memory",
                "description": "Configure memory capabilities for agent capsules",
                "category": "capsules"
            }
        }
        
        # Update capsule settings from config
        config_capsule_settings = self.config.get("capsule_settings", {})
        for setting_id, setting_value in config_capsule_settings.items():
            if setting_id in self.capsule_settings and isinstance(setting_value, dict) and isinstance(self.capsule_settings[setting_id], dict):
                self.capsule_settings[setting_id].update(setting_value)
            else:
                self.capsule_settings[setting_id] = setting_value
        
        logger.info("Capsule settings initialized")
    
    def get_settings_categories(self) -> List[Dict[str, Any]]:
        """
        Get all settings categories.
        
        Returns:
            List[Dict[str, Any]]: List of settings categories
        """
        return self.settings_categories
    
    def get_settings_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific settings category by ID.
        
        Args:
            category_id: Category ID
        
        Returns:
            Optional[Dict[str, Any]]: Category data or None if not found
        """
        return next((category for category in self.settings_categories if category["id"] == category_id), None)
    
    def get_settings_by_category(self, category_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all settings for a specific category.
        
        Args:
            category_id: Category ID
        
        Returns:
            Dict[str, Dict[str, Any]]: Settings for the specified category
        """
        settings = {}
        
        # Collect settings from all setting types
        for setting_type in [self.user_preferences, self.device_settings, self.notification_settings, 
                            self.accessibility_settings, self.security_settings, self.avatar_settings, 
                            self.capsule_settings]:
            for setting_category, category_settings in setting_type.items():
                if isinstance(category_settings, dict):
                    for setting_id, setting in category_settings.items():
                        if isinstance(setting, dict) and setting.get("category") == category_id:
                            if setting_category not in settings:
                                settings[setting_category] = {}
                            settings[setting_category][setting_id] = setting
        
        return settings
    
    def get_setting(self, setting_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific setting by path.
        
        Args:
            setting_path: Setting path (e.g., "theme.color_scheme")
        
        Returns:
            Optional[Dict[str, Any]]: Setting data or None if not found
        """
        path_parts = setting_path.split(".")
        if len(path_parts) != 2:
            return None
        
        category, setting_id = path_parts
        
        # Check user preferences
        if category in self.user_preferences and setting_id in self.user_preferences[category]:
            return self.user_preferences[category][setting_id]
        
        # Check device settings
        if setting_id in self.device_settings:
            return self.device_settings[setting_id]
        
        # Check notification settings
        if setting_id in self.notification_settings:
            return self.notification_settings[setting_id]
        
        # Check accessibility settings
        if setting_id in self.accessibility_settings:
            return self.accessibility_settings[setting_id]
        
        # Check security settings
        if setting_id in self.security_settings:
            return self.security_settings[setting_id]
        
        # Check avatar settings
        if setting_id in self.avatar_settings:
            return self.avatar_settings[setting_id]
        
        # Check capsule settings
        if setting_id in self.capsule_settings:
            return self.capsule_settings[setting_id]
        
        return None
    
    def get_setting_value(self, setting_path: str) -> Any:
        """
        Get the value of a specific setting by path.
        
        Args:
            setting_path: Setting path (e.g., "theme.color_scheme")
        
        Returns:
            Any: Setting value or None if not found
        """
        setting = self.get_setting(setting_path)
        if setting is None:
            return None
        
        return setting.get("value")
    
    def update_setting(self, setting_path: str, value: Any) -> bool:
        """
        Update a specific setting by path.
        
        Args:
            setting_path: Setting path (e.g., "theme.color_scheme")
            value: New setting value
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        logger.info("Updating setting: %s", setting_path)
        
        path_parts = setting_path.split(".")
        if len(path_parts) != 2:
            logger.error("Invalid setting path: %s", setting_path)
            return False
        
        category, setting_id = path_parts
        
        try:
            # Update user preferences
            if category in self.user_preferences and setting_id in self.user_preferences[category]:
                self.user_preferences[category][setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update device settings
            if setting_id in self.device_settings:
                self.device_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update notification settings
            if setting_id in self.notification_settings:
                self.notification_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update accessibility settings
            if setting_id in self.accessibility_settings:
                self.accessibility_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update security settings
            if setting_id in self.security_settings:
                self.security_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update avatar settings
            if setting_id in self.avatar_settings:
                self.avatar_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            # Update capsule settings
            if setting_id in self.capsule_settings:
                self.capsule_settings[setting_id]["value"] = value
                logger.info("Setting updated successfully: %s", setting_path)
                
                # Apply setting if applicable
                self._apply_setting(category, setting_id, value)
                
                # Notify subscribers
                self._notify_subscribers("setting_updated", {
                    "setting_path": setting_path,
                    "value": value
                })
                
                return True
            
            logger.warning("Setting not found: %s", setting_path)
            return False
        except Exception as e:
            logger.error("Error updating setting: %s", e)
            return False
    
    def _apply_setting(self, category: str, setting_id: str, value: Any):
        """
        Apply a setting to the appropriate manager.
        
        Args:
            category: Setting category
            setting_id: Setting ID
            value: Setting value
        """
        logger.info("Applying setting: %s.%s", category, setting_id)
        
        try:
            # Apply theme settings
            if category == "theme":
                if self.theme_manager:
                    if setting_id == "color_scheme":
                        self.theme_manager.set_color_scheme(value)
                    elif setting_id == "accent_color":
                        self.theme_manager.set_accent_color(value)
                    elif setting_id == "font_family":
                        self.theme_manager.set_font_family(value)
                    elif setting_id == "font_size":
                        self.theme_manager.set_font_size(value)
                    elif setting_id == "animation_level":
                        self.theme_manager.set_animation_level(value)
                    elif setting_id == "density":
                        self.theme_manager.set_density(value)
            
            # Apply accessibility settings
            elif category == "accessibility":
                if self.accessibility_manager:
                    if setting_id == "screen_reader":
                        self.accessibility_manager.set_screen_reader(value)
                    elif setting_id == "high_contrast":
                        self.accessibility_manager.set_high_contrast(value)
                    elif setting_id == "reduced_motion":
                        self.accessibility_manager.set_reduced_motion(value)
                    elif setting_id == "keyboard_navigation":
                        self.accessibility_manager.set_keyboard_navigation(value)
                    elif setting_id == "text_to_speech":
                        self.accessibility_manager.set_text_to_speech(value)
                    elif setting_id == "speech_to_text":
                        self.accessibility_manager.set_speech_to_text(value)
                    elif setting_id == "color_blind_mode":
                        self.accessibility_manager.set_color_blind_mode(value)
                    elif setting_id == "text_spacing":
                        self.accessibility_manager.set_text_spacing(value)
                    elif setting_id == "line_height":
                        self.accessibility_manager.set_line_height(value)
                    elif setting_id == "focus_indicators":
                        self.accessibility_manager.set_focus_indicators(value)
            
            # Apply device settings
            elif category == "devices":
                if self.device_adapter:
                    if setting_id == "device_type":
                        self.device_adapter.set_device_type(value)
                    elif setting_id == "orientation":
                        self.device_adapter.set_orientation(value)
                    elif setting_id == "touch_optimization":
                        self.device_adapter.set_touch_optimization(value)
                    elif setting_id == "offline_mode":
                        self.device_adapter.set_offline_mode(value)
                    elif setting_id == "enable_gestures":
                        self.device_adapter.set_enable_gestures(value)
                    elif setting_id == "enable_voice":
                        self.device_adapter.set_enable_voice(value)
                    elif setting_id == "enable_haptics":
                        self.device_adapter.set_enable_haptics(value)
                    elif setting_id == "bitnet_ui_pack":
                        self.device_adapter.set_bitnet_ui_pack(value)
                    elif setting_id == "ar_vr_mode":
                        self.device_adapter.set_ar_vr_mode(value)
            
            # Apply universal skin settings
            elif self.universal_skin_shell:
                # Notification settings
                if category == "notifications":
                    self.universal_skin_shell.update_notification_settings(setting_id, value)
                
                # Security settings
                elif category == "security":
                    self.universal_skin_shell.update_security_settings(setting_id, value)
                
                # Avatar settings
                elif category == "avatars":
                    self.universal_skin_shell.update_avatar_settings(setting_id, value)
                
                # Capsule settings
                elif category == "capsules":
                    self.universal_skin_shell.update_capsule_settings(setting_id, value)
                
                # Layout settings
                elif category == "layout":
                    self.universal_skin_shell.update_layout_settings(setting_id, value)
                
                # Behavior settings
                elif category == "behavior":
                    self.universal_skin_shell.update_behavior_settings(setting_id, value)
        except Exception as e:
            logger.error("Error applying setting: %s", e)
    
    def reset_settings(self, category_id: Optional[str] = None) -> bool:
        """
        Reset settings to default values.
        
        Args:
            category_id: Optional category ID to reset only settings in that category
        
        Returns:
            bool: True if reset was successful, False otherwise
        """
        logger.info("Resetting settings: %s", category_id or "all")
        
        try:
            # Re-initialize settings
            if category_id is None or category_id == "appearance":
                self._initialize_user_preferences()
            
            if category_id is None or category_id == "devices":
                self._initialize_device_settings()
            
            if category_id is None or category_id == "notifications":
                self._initialize_notification_settings()
            
            if category_id is None or category_id == "accessibility":
                self._initialize_accessibility_settings()
            
            if category_id is None or category_id == "security":
                self._initialize_security_settings()
            
            if category_id is None or category_id == "avatars":
                self._initialize_avatar_settings()
            
            if category_id is None or category_id == "capsules":
                self._initialize_capsule_settings()
            
            # Apply settings
            self._apply_all_settings()
            
            # Notify subscribers
            self._notify_subscribers("settings_reset", {
                "category_id": category_id
            })
            
            logger.info("Settings reset successfully: %s", category_id or "all")
            return True
        except Exception as e:
            logger.error("Error resetting settings: %s", e)
            return False
    
    def _apply_all_settings(self):
        """Apply all settings to the appropriate managers."""
        logger.info("Applying all settings")
        
        try:
            # Apply theme settings
            if self.theme_manager:
                for setting_id, setting in self.user_preferences.get("theme", {}).items():
                    self._apply_setting("theme", setting_id, setting.get("value"))
            
            # Apply accessibility settings
            if self.accessibility_manager:
                for setting_id, setting in self.accessibility_settings.items():
                    self._apply_setting("accessibility", setting_id, setting.get("value"))
            
            # Apply device settings
            if self.device_adapter:
                for setting_id, setting in self.device_settings.items():
                    self._apply_setting("devices", setting_id, setting.get("value"))
            
            # Apply universal skin settings
            if self.universal_skin_shell:
                # Notification settings
                for setting_id, setting in self.notification_settings.items():
                    self._apply_setting("notifications", setting_id, setting.get("value"))
                
                # Security settings
                for setting_id, setting in self.security_settings.items():
                    self._apply_setting("security", setting_id, setting.get("value"))
                
                # Avatar settings
                for setting_id, setting in self.avatar_settings.items():
                    self._apply_setting("avatars", setting_id, setting.get("value"))
                
                # Capsule settings
                for setting_id, setting in self.capsule_settings.items():
                    self._apply_setting("capsules", setting_id, setting.get("value"))
                
                # Layout settings
                for setting_id, setting in self.user_preferences.get("layout", {}).items():
                    self._apply_setting("layout", setting_id, setting.get("value"))
                
                # Behavior settings
                for setting_id, setting in self.user_preferences.get("behavior", {}).items():
                    self._apply_setting("behavior", setting_id, setting.get("value"))
        except Exception as e:
            logger.error("Error applying all settings: %s", e)
    
    def export_settings(self) -> Dict[str, Any]:
        """
        Export all settings.
        
        Returns:
            Dict[str, Any]: All settings
        """
        logger.info("Exporting settings")
        
        # Prepare export data
        export_data = {
            "user_preferences": self.user_preferences,
            "device_settings": self.device_settings,
            "notification_settings": self.notification_settings,
            "accessibility_settings": self.accessibility_settings,
            "security_settings": self.security_settings,
            "avatar_settings": self.avatar_settings,
            "capsule_settings": self.capsule_settings
        }
        
        return export_data
    
    def import_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        Import settings.
        
        Args:
            settings_data: Settings data to import
        
        Returns:
            bool: True if import was successful, False otherwise
        """
        logger.info("Importing settings")
        
        try:
            # Update user preferences
            if "user_preferences" in settings_data and isinstance(settings_data["user_preferences"], dict):
                for category, settings in settings_data["user_preferences"].items():
                    if category in self.user_preferences and isinstance(settings, dict) and isinstance(self.user_preferences[category], dict):
                        for setting_id, setting_value in settings.items():
                            if setting_id in self.user_preferences[category] and isinstance(setting_value, dict) and isinstance(self.user_preferences[category][setting_id], dict):
                                if "value" in setting_value:
                                    self.user_preferences[category][setting_id]["value"] = setting_value["value"]
            
            # Update device settings
            if "device_settings" in settings_data and isinstance(settings_data["device_settings"], dict):
                for setting_id, setting_value in settings_data["device_settings"].items():
                    if setting_id in self.device_settings and isinstance(setting_value, dict) and isinstance(self.device_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.device_settings[setting_id]["value"] = setting_value["value"]
            
            # Update notification settings
            if "notification_settings" in settings_data and isinstance(settings_data["notification_settings"], dict):
                for setting_id, setting_value in settings_data["notification_settings"].items():
                    if setting_id in self.notification_settings and isinstance(setting_value, dict) and isinstance(self.notification_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.notification_settings[setting_id]["value"] = setting_value["value"]
            
            # Update accessibility settings
            if "accessibility_settings" in settings_data and isinstance(settings_data["accessibility_settings"], dict):
                for setting_id, setting_value in settings_data["accessibility_settings"].items():
                    if setting_id in self.accessibility_settings and isinstance(setting_value, dict) and isinstance(self.accessibility_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.accessibility_settings[setting_id]["value"] = setting_value["value"]
            
            # Update security settings
            if "security_settings" in settings_data and isinstance(settings_data["security_settings"], dict):
                for setting_id, setting_value in settings_data["security_settings"].items():
                    if setting_id in self.security_settings and isinstance(setting_value, dict) and isinstance(self.security_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.security_settings[setting_id]["value"] = setting_value["value"]
            
            # Update avatar settings
            if "avatar_settings" in settings_data and isinstance(settings_data["avatar_settings"], dict):
                for setting_id, setting_value in settings_data["avatar_settings"].items():
                    if setting_id in self.avatar_settings and isinstance(setting_value, dict) and isinstance(self.avatar_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.avatar_settings[setting_id]["value"] = setting_value["value"]
            
            # Update capsule settings
            if "capsule_settings" in settings_data and isinstance(settings_data["capsule_settings"], dict):
                for setting_id, setting_value in settings_data["capsule_settings"].items():
                    if setting_id in self.capsule_settings and isinstance(setting_value, dict) and isinstance(self.capsule_settings[setting_id], dict):
                        if "value" in setting_value:
                            self.capsule_settings[setting_id]["value"] = setting_value["value"]
            
            # Apply settings
            self._apply_all_settings()
            
            # Notify subscribers
            self._notify_subscribers("settings_imported", {})
            
            logger.info("Settings imported successfully")
            return True
        except Exception as e:
            logger.error("Error importing settings: %s", e)
            return False
    
    def _notify_subscribers(self, event_type: str, event_data: Dict[str, Any]):
        """
        Notify subscribers of an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error("Error in event subscriber callback: %s", e)
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to settings events.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to be called when event occurs
        
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = set()
        
        self.event_subscribers[event_type].add(callback)
        return True
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from settings events.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to be removed
        
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        if event_type in self.event_subscribers and callback in self.event_subscribers[event_type]:
            self.event_subscribers[event_type].remove(callback)
            return True
        
        return False
    
    def render(self) -> Dict[str, Any]:
        """
        Render the settings page.
        
        Returns:
            Dict[str, Any]: Rendered settings page data
        """
        logger.info("Rendering settings page")
        
        # Prepare render data
        render_data = {
            "page": "settings",
            "title": "Settings - Industriverse",
            "categories": self.settings_categories,
            "settings": {
                "user_preferences": self.user_preferences,
                "device_settings": self.device_settings,
                "notification_settings": self.notification_settings,
                "accessibility_settings": self.accessibility_settings,
                "security_settings": self.security_settings,
                "avatar_settings": self.avatar_settings,
                "capsule_settings": self.capsule_settings
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Notify subscribers
        self._notify_subscribers("settings_page_rendered", {
            "render_data": render_data
        })
        
        return render_data
