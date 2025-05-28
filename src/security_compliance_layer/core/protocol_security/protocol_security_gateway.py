"""
Protocol Security Gateway Module for the Security & Compliance Layer of Industriverse.

This module implements a comprehensive Protocol Security Gateway that provides:
- Protocol validation and sanitization
- Protocol-level access control
- Protocol transformation and normalization
- Protocol anomaly detection
- Protocol-level audit logging
- Integration with MCP and A2A protocols

The Protocol Security Gateway is a critical component of the Protocol Security System,
ensuring that all protocol communications within Industriverse are secure, compliant,
and properly authorized.
"""

import os
import time
import uuid
import json
import logging
import hashlib
import base64
import re
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProtocolSecurityGateway:
    """
    Protocol Security Gateway for the Security & Compliance Layer.
    
    This class provides comprehensive protocol security services including:
    - Protocol validation and sanitization
    - Protocol-level access control
    - Protocol transformation and normalization
    - Protocol anomaly detection
    - Protocol-level audit logging
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Protocol Security Gateway with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.protocol_validators = {}
        self.protocol_transformers = {}
        self.protocol_acl = {}
        self.anomaly_detectors = {}
        self.audit_log = []
        
        # Initialize protocol handlers
        self._initialize_protocol_handlers()
        
        logger.info("Protocol Security Gateway initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "protocols": {
                "mcp": {
                    "enabled": True,
                    "validation_level": "strict",  # strict, standard, permissive
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                },
                "a2a": {
                    "enabled": True,
                    "validation_level": "strict",
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                },
                "http": {
                    "enabled": True,
                    "validation_level": "standard",
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                },
                "mqtt": {
                    "enabled": True,
                    "validation_level": "standard",
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                },
                "opc_ua": {
                    "enabled": True,
                    "validation_level": "standard",
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                },
                "modbus": {
                    "enabled": True,
                    "validation_level": "standard",
                    "sanitization_enabled": True,
                    "transformation_enabled": True,
                    "anomaly_detection_enabled": True
                }
            },
            "access_control": {
                "enabled": True,
                "default_policy": "deny",  # allow, deny
                "trust_based": True
            },
            "audit": {
                "enabled": True,
                "log_level": "info",  # debug, info, warning, error
                "retention_days": 90,
                "tamper_proof": True
            },
            "anomaly_detection": {
                "sensitivity": "medium",  # low, medium, high
                "learning_mode": False,
                "alert_threshold": 0.8,
                "baseline_period_days": 30
            },
            "performance": {
                "max_message_size_mb": 10,
                "rate_limiting_enabled": True,
                "max_requests_per_minute": 1000
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        return default_config
    
    def _initialize_protocol_handlers(self):
        """Initialize protocol handlers based on configuration."""
        # Initialize validators
        self._initialize_validators()
        
        # Initialize transformers
        self._initialize_transformers()
        
        # Initialize access control
        self._initialize_access_control()
        
        # Initialize anomaly detectors
        self._initialize_anomaly_detectors()
    
    def _initialize_validators(self):
        """Initialize protocol validators based on configuration."""
        for protocol, config in self.config["protocols"].items():
            if config["enabled"]:
                if protocol == "mcp":
                    self.protocol_validators[protocol] = self._create_mcp_validator(config["validation_level"])
                elif protocol == "a2a":
                    self.protocol_validators[protocol] = self._create_a2a_validator(config["validation_level"])
                elif protocol == "http":
                    self.protocol_validators[protocol] = self._create_http_validator(config["validation_level"])
                elif protocol == "mqtt":
                    self.protocol_validators[protocol] = self._create_mqtt_validator(config["validation_level"])
                elif protocol == "opc_ua":
                    self.protocol_validators[protocol] = self._create_opc_ua_validator(config["validation_level"])
                elif protocol == "modbus":
                    self.protocol_validators[protocol] = self._create_modbus_validator(config["validation_level"])
    
    def _initialize_transformers(self):
        """Initialize protocol transformers based on configuration."""
        for protocol, config in self.config["protocols"].items():
            if config["enabled"] and config["transformation_enabled"]:
                if protocol == "mcp":
                    self.protocol_transformers[protocol] = self._create_mcp_transformer()
                elif protocol == "a2a":
                    self.protocol_transformers[protocol] = self._create_a2a_transformer()
                elif protocol == "http":
                    self.protocol_transformers[protocol] = self._create_http_transformer()
                elif protocol == "mqtt":
                    self.protocol_transformers[protocol] = self._create_mqtt_transformer()
                elif protocol == "opc_ua":
                    self.protocol_transformers[protocol] = self._create_opc_ua_transformer()
                elif protocol == "modbus":
                    self.protocol_transformers[protocol] = self._create_modbus_transformer()
    
    def _initialize_access_control(self):
        """Initialize protocol access control based on configuration."""
        if self.config["access_control"]["enabled"]:
            # In a production environment, this would load ACL rules from a database or file
            # For this implementation, we'll use a simple in-memory structure
            
            # Initialize with default policy
            default_policy = self.config["access_control"]["default_policy"]
            
            # Create ACL for each protocol
            for protocol in self.config["protocols"]:
                if self.config["protocols"][protocol]["enabled"]:
                    self.protocol_acl[protocol] = {
                        "default_policy": default_policy,
                        "rules": []
                    }
            
            # Add some example rules
            self._add_acl_rule("mcp", "source:core_ai_layer", "destination:generative_layer", "allow")
            self._add_acl_rule("a2a", "agent:trust_score_agent", "agent:*", "allow")
    
    def _initialize_anomaly_detectors(self):
        """Initialize protocol anomaly detectors based on configuration."""
        for protocol, config in self.config["protocols"].items():
            if config["enabled"] and config["anomaly_detection_enabled"]:
                sensitivity = self.config["anomaly_detection"]["sensitivity"]
                learning_mode = self.config["anomaly_detection"]["learning_mode"]
                
                self.anomaly_detectors[protocol] = self._create_anomaly_detector(
                    protocol, sensitivity, learning_mode
                )
    
    def process_message(self, protocol: str, message: Dict, context: Dict = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Process a protocol message through the security gateway.
        
        Args:
            protocol: Protocol identifier (mcp, a2a, http, mqtt, opc_ua, modbus)
            message: Protocol message to process
            context: Optional context information (source, destination, etc.)
            
        Returns:
            Tuple containing (success, processed_message, error_message)
        """
        # Check if protocol is supported
        if protocol not in self.config["protocols"] or not self.config["protocols"][protocol]["enabled"]:
            error = f"Protocol {protocol} is not supported or not enabled"
            self._audit_log("error", protocol, "process_message", error, context)
            return False, None, error
        
        # Create default context if not provided
        if context is None:
            context = {}
        
        # Add timestamp to context
        context["timestamp"] = datetime.utcnow().isoformat()
        
        # Generate message ID if not in context
        if "message_id" not in context:
            context["message_id"] = str(uuid.uuid4())
        
        # Audit log the message receipt
        self._audit_log("info", protocol, "message_received", "Message received", context)
        
        # Check rate limiting
        if self.config["performance"]["rate_limiting_enabled"]:
            # In a production environment, this would use a rate limiting service
            # For this implementation, we'll assume rate limiting is not exceeded
            pass
        
        # Check message size
        max_size = self.config["performance"]["max_message_size_mb"] * 1024 * 1024
        message_size = len(json.dumps(message).encode())
        if message_size > max_size:
            error = f"Message size ({message_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
            self._audit_log("error", protocol, "process_message", error, context)
            return False, None, error
        
        # Validate message
        valid, validation_error = self._validate_message(protocol, message, context)
        if not valid:
            self._audit_log("error", protocol, "validation", validation_error, context)
            return False, None, validation_error
        
        # Check access control
        allowed, acl_error = self._check_access_control(protocol, message, context)
        if not allowed:
            self._audit_log("error", protocol, "access_control", acl_error, context)
            return False, None, acl_error
        
        # Transform message if needed
        transformed_message = self._transform_message(protocol, message, context)
        
        # Check for anomalies
        anomaly, anomaly_score, anomaly_details = self._detect_anomalies(protocol, transformed_message, context)
        if anomaly:
            # Log the anomaly
            self._audit_log("warning", protocol, "anomaly_detection", 
                          f"Anomaly detected (score: {anomaly_score}): {anomaly_details}", context)
            
            # If anomaly score is above threshold, block the message
            if anomaly_score > self.config["anomaly_detection"]["alert_threshold"]:
                error = f"Message blocked due to high anomaly score: {anomaly_score}"
                self._audit_log("error", protocol, "anomaly_detection", error, context)
                return False, None, error
        
        # Audit log the successful processing
        self._audit_log("info", protocol, "process_message", "Message processed successfully", context)
        
        return True, transformed_message, None
    
    def _validate_message(self, protocol: str, message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate a protocol message.
        
        Args:
            protocol: Protocol identifier
            message: Protocol message to validate
            context: Context information
            
        Returns:
            Tuple containing (valid, error_message)
        """
        if protocol not in self.protocol_validators:
            return False, f"No validator available for protocol {protocol}"
        
        validator = self.protocol_validators[protocol]
        return validator(message, context)
    
    def _check_access_control(self, protocol: str, message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check access control for a protocol message.
        
        Args:
            protocol: Protocol identifier
            message: Protocol message to check
            context: Context information
            
        Returns:
            Tuple containing (allowed, error_message)
        """
        if not self.config["access_control"]["enabled"]:
            return True, None
        
        if protocol not in self.protocol_acl:
            # If no ACL is defined for the protocol, use the default policy
            default_policy = self.config["access_control"]["default_policy"]
            return default_policy == "allow", f"No ACL defined for protocol {protocol}, using default policy: {default_policy}"
        
        # Get source and destination from context
        source = context.get("source", "unknown")
        destination = context.get("destination", "unknown")
        
        # Check if there's a specific rule for this source and destination
        acl = self.protocol_acl[protocol]
        for rule in acl["rules"]:
            source_pattern = rule["source"]
            destination_pattern = rule["destination"]
            
            # Check if the rule matches
            source_match = self._match_pattern(source, source_pattern)
            destination_match = self._match_pattern(destination, destination_pattern)
            
            if source_match and destination_match:
                # Rule matches, return the action
                return rule["action"] == "allow", f"ACL rule matched: {rule['action']}"
        
        # No rule matched, use the default policy
        default_policy = acl["default_policy"]
        return default_policy == "allow", f"No ACL rule matched, using default policy: {default_policy}"
    
    def _transform_message(self, protocol: str, message: Dict, context: Dict) -> Dict:
        """
        Transform a protocol message.
        
        Args:
            protocol: Protocol identifier
            message: Protocol message to transform
            context: Context information
            
        Returns:
            Transformed message
        """
        if not self.config["protocols"][protocol]["transformation_enabled"]:
            return message
        
        if protocol not in self.protocol_transformers:
            return message
        
        transformer = self.protocol_transformers[protocol]
        return transformer(message, context)
    
    def _detect_anomalies(self, protocol: str, message: Dict, context: Dict) -> Tuple[bool, float, Optional[str]]:
        """
        Detect anomalies in a protocol message.
        
        Args:
            protocol: Protocol identifier
            message: Protocol message to check
            context: Context information
            
        Returns:
            Tuple containing (anomaly_detected, anomaly_score, anomaly_details)
        """
        if not self.config["protocols"][protocol]["anomaly_detection_enabled"]:
            return False, 0.0, None
        
        if protocol not in self.anomaly_detectors:
            return False, 0.0, None
        
        detector = self.anomaly_detectors[protocol]
        return detector(message, context)
    
    def _audit_log(self, level: str, protocol: str, operation: str, message: str, context: Dict):
        """
        Add an entry to the audit log.
        
        Args:
            level: Log level (debug, info, warning, error)
            protocol: Protocol identifier
            operation: Operation being performed
            message: Log message
            context: Context information
        """
        if not self.config["audit"]["enabled"]:
            return
        
        # Check if log level is sufficient
        log_levels = ["debug", "info", "warning", "error"]
        config_level = self.config["audit"]["log_level"]
        
        if log_levels.index(level) < log_levels.index(config_level):
            return
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "protocol": protocol,
            "operation": operation,
            "message": message,
            "context": context
        }
        
        # In a production environment, this would write to a secure, tamper-proof log store
        # For this implementation, we'll just append to an in-memory list
        self.audit_log.append(log_entry)
        
        # Log to the logger as well
        log_method = getattr(logger, level)
        log_method(f"[{protocol}] {operation}: {message}")
    
    def add_acl_rule(self, protocol: str, source: str, destination: str, action: str) -> bool:
        """
        Add an access control rule.
        
        Args:
            protocol: Protocol identifier
            source: Source pattern
            destination: Destination pattern
            action: Action (allow, deny)
            
        Returns:
            True if rule was added successfully, False otherwise
        """
        return self._add_acl_rule(protocol, source, destination, action)
    
    def _add_acl_rule(self, protocol: str, source: str, destination: str, action: str) -> bool:
        """
        Add an access control rule (internal implementation).
        
        Args:
            protocol: Protocol identifier
            source: Source pattern
            destination: Destination pattern
            action: Action (allow, deny)
            
        Returns:
            True if rule was added successfully, False otherwise
        """
        if not self.config["access_control"]["enabled"]:
            return False
        
        if protocol not in self.protocol_acl:
            return False
        
        if action not in ["allow", "deny"]:
            return False
        
        # Create rule
        rule = {
            "source": source,
            "destination": destination,
            "action": action,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add rule to ACL
        self.protocol_acl[protocol]["rules"].append(rule)
        
        logger.info(f"Added ACL rule for {protocol}: {source} -> {destination} = {action}")
        
        return True
    
    def get_audit_log(self, start_time: str = None, end_time: str = None, 
                     level: str = None, protocol: str = None, limit: int = 100) -> List[Dict]:
        """
        Get entries from the audit log.
        
        Args:
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            level: Optional log level filter
            protocol: Optional protocol filter
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        if not self.config["audit"]["enabled"]:
            return []
        
        # Filter log entries
        filtered_log = self.audit_log
        
        if start_time:
            filtered_log = [entry for entry in filtered_log if entry["timestamp"] >= start_time]
        
        if end_time:
            filtered_log = [entry for entry in filtered_log if entry["timestamp"] <= end_time]
        
        if level:
            filtered_log = [entry for entry in filtered_log if entry["level"] == level]
        
        if protocol:
            filtered_log = [entry for entry in filtered_log if entry["protocol"] == protocol]
        
        # Sort by timestamp (newest first)
        filtered_log.sort(key=lambda entry: entry["timestamp"], reverse=True)
        
        # Apply limit
        return filtered_log[:limit]
    
    def _match_pattern(self, value: str, pattern: str) -> bool:
        """
        Match a value against a pattern.
        
        Args:
            value: Value to match
            pattern: Pattern to match against (supports * wildcard)
            
        Returns:
            True if the value matches the pattern, False otherwise
        """
        # Convert pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", value))
    
    # Protocol validator implementations
    
    def _create_mcp_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for MCP protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_mcp(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate an MCP protocol message.
            
            Args:
                message: MCP message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["id", "type", "content"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["timestamp", "source", "destination"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Validate message type
            valid_types = ["request", "response", "event", "error"]
            if message["type"] not in valid_types:
                return False, f"Invalid message type: {message['type']}"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate timestamp format
                try:
                    datetime.fromisoformat(message["timestamp"])
                except ValueError:
                    return False, "Invalid timestamp format"
                
                # Validate content structure based on message type
                if message["type"] == "request":
                    if "action" not in message["content"]:
                        return False, "Request message must have an action in content"
                
                elif message["type"] == "response":
                    if "request_id" not in message:
                        return False, "Response message must have a request_id"
                
                elif message["type"] == "error":
                    if "error_code" not in message["content"] or "error_message" not in message["content"]:
                        return False, "Error message must have error_code and error_message in content"
            
            return True, None
        
        return validate_mcp
    
    def _create_a2a_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for A2A protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_a2a(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate an A2A protocol message.
            
            Args:
                message: A2A message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["agent_id", "message_type", "payload"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["timestamp", "conversation_id", "trace_id"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Validate message type
            valid_types = ["request", "response", "notification", "error"]
            if message["message_type"] not in valid_types:
                return False, f"Invalid message type: {message['message_type']}"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate timestamp format
                if "timestamp" in message:
                    try:
                        datetime.fromisoformat(message["timestamp"])
                    except ValueError:
                        return False, "Invalid timestamp format"
                
                # Validate payload structure based on message type
                if message["message_type"] == "request":
                    if "action" not in message["payload"]:
                        return False, "Request message must have an action in payload"
                
                elif message["message_type"] == "response":
                    if "request_id" not in message:
                        return False, "Response message must have a request_id"
                
                elif message["message_type"] == "error":
                    if "error_code" not in message["payload"] or "error_message" not in message["payload"]:
                        return False, "Error message must have error_code and error_message in payload"
                
                # Validate industry-specific metadata if present
                if "industryTags" in message:
                    if not isinstance(message["industryTags"], list):
                        return False, "industryTags must be a list"
                
                # Validate priority if present
                if "priority" in message:
                    if not isinstance(message["priority"], int) or message["priority"] < 1 or message["priority"] > 5:
                        return False, "priority must be an integer between 1 and 5"
            
            return True, None
        
        return validate_a2a
    
    def _create_http_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for HTTP protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_http(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate an HTTP protocol message.
            
            Args:
                message: HTTP message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["method", "url"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["headers", "version"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Validate HTTP method
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
            if message["method"] not in valid_methods:
                return False, f"Invalid HTTP method: {message['method']}"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate URL format
                if not message["url"].startswith("http://") and not message["url"].startswith("https://"):
                    return False, "URL must start with http:// or https://"
                
                # Validate headers
                if not isinstance(message["headers"], dict):
                    return False, "Headers must be a dictionary"
                
                # Validate HTTP version
                valid_versions = ["HTTP/1.0", "HTTP/1.1", "HTTP/2", "HTTP/3"]
                if message["version"] not in valid_versions:
                    return False, f"Invalid HTTP version: {message['version']}"
            
            return True, None
        
        return validate_http
    
    def _create_mqtt_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for MQTT protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_mqtt(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate an MQTT protocol message.
            
            Args:
                message: MQTT message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["topic", "payload"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["qos", "retain"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate QoS
                valid_qos = [0, 1, 2]
                if message["qos"] not in valid_qos:
                    return False, f"Invalid QoS value: {message['qos']}"
                
                # Validate retain flag
                if not isinstance(message["retain"], bool):
                    return False, "Retain flag must be a boolean"
                
                # Validate topic format
                if not isinstance(message["topic"], str) or len(message["topic"]) == 0:
                    return False, "Topic must be a non-empty string"
                
                # Check for invalid characters in topic
                invalid_chars = ["\0", "+", "#"]
                for char in invalid_chars:
                    if char in message["topic"]:
                        return False, f"Topic contains invalid character: {char}"
            
            return True, None
        
        return validate_mqtt
    
    def _create_opc_ua_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for OPC UA protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_opc_ua(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate an OPC UA protocol message.
            
            Args:
                message: OPC UA message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["message_type", "node_id"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["timestamp", "security_mode"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Validate message type
            valid_types = ["read", "write", "subscribe", "unsubscribe", "method_call", "browse"]
            if message["message_type"] not in valid_types:
                return False, f"Invalid message type: {message['message_type']}"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate timestamp format
                try:
                    datetime.fromisoformat(message["timestamp"])
                except ValueError:
                    return False, "Invalid timestamp format"
                
                # Validate security mode
                valid_modes = ["None", "Sign", "SignAndEncrypt"]
                if message["security_mode"] not in valid_modes:
                    return False, f"Invalid security mode: {message['security_mode']}"
                
                # Validate node ID format
                if not isinstance(message["node_id"], str) or len(message["node_id"]) == 0:
                    return False, "Node ID must be a non-empty string"
                
                # Validate message-specific fields
                if message["message_type"] == "write":
                    if "value" not in message:
                        return False, "Write message must have a value field"
                
                elif message["message_type"] == "method_call":
                    if "method_name" not in message or "arguments" not in message:
                        return False, "Method call message must have method_name and arguments fields"
            
            return True, None
        
        return validate_opc_ua
    
    def _create_modbus_validator(self, validation_level: str) -> Callable:
        """
        Create a validator for Modbus protocol messages.
        
        Args:
            validation_level: Validation level (strict, standard, permissive)
            
        Returns:
            Validator function
        """
        def validate_modbus(message: Dict, context: Dict) -> Tuple[bool, Optional[str]]:
            """
            Validate a Modbus protocol message.
            
            Args:
                message: Modbus message to validate
                context: Context information
                
            Returns:
                Tuple containing (valid, error_message)
            """
            # Check required fields
            required_fields = ["function_code", "unit_id"]
            
            if validation_level == "strict":
                # Add more required fields for strict validation
                required_fields.extend(["address", "transport"])
            
            for field in required_fields:
                if field not in message:
                    return False, f"Missing required field: {field}"
            
            # Validate function code
            valid_function_codes = [1, 2, 3, 4, 5, 6, 15, 16]
            if message["function_code"] not in valid_function_codes:
                return False, f"Invalid function code: {message['function_code']}"
            
            # Validate unit ID
            if not isinstance(message["unit_id"], int) or message["unit_id"] < 0 or message["unit_id"] > 255:
                return False, "Unit ID must be an integer between 0 and 255"
            
            # Additional validation for strict level
            if validation_level == "strict":
                # Validate address
                if not isinstance(message["address"], int) or message["address"] < 0:
                    return False, "Address must be a non-negative integer"
                
                # Validate transport
                valid_transports = ["tcp", "rtu", "ascii"]
                if message["transport"] not in valid_transports:
                    return False, f"Invalid transport: {message['transport']}"
                
                # Validate function-specific fields
                if message["function_code"] in [1, 2, 3, 4]:  # Read functions
                    if "count" not in message:
                        return False, "Read function must have a count field"
                    
                    if not isinstance(message["count"], int) or message["count"] <= 0:
                        return False, "Count must be a positive integer"
                
                elif message["function_code"] in [5, 6]:  # Single write functions
                    if "value" not in message:
                        return False, "Write function must have a value field"
                
                elif message["function_code"] in [15, 16]:  # Multiple write functions
                    if "values" not in message:
                        return False, "Multiple write function must have a values field"
                    
                    if not isinstance(message["values"], list) or len(message["values"]) == 0:
                        return False, "Values must be a non-empty list"
            
            return True, None
        
        return validate_modbus
    
    # Protocol transformer implementations
    
    def _create_mcp_transformer(self) -> Callable:
        """
        Create a transformer for MCP protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_mcp(message: Dict, context: Dict) -> Dict:
            """
            Transform an MCP protocol message.
            
            Args:
                message: MCP message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Add timestamp if missing
            if "timestamp" not in transformed:
                transformed["timestamp"] = datetime.utcnow().isoformat()
            
            # Add source and destination if available in context
            if "source" in context and "source" not in transformed:
                transformed["source"] = context["source"]
            
            if "destination" in context and "destination" not in transformed:
                transformed["destination"] = context["destination"]
            
            # Add message ID if missing
            if "id" not in transformed:
                transformed["id"] = context.get("message_id", str(uuid.uuid4()))
            
            # Add security metadata
            transformed["_security"] = {
                "processed_by": "protocol_security_gateway",
                "processed_at": datetime.utcnow().isoformat(),
                "trace_id": context.get("trace_id", str(uuid.uuid4()))
            }
            
            return transformed
        
        return transform_mcp
    
    def _create_a2a_transformer(self) -> Callable:
        """
        Create a transformer for A2A protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_a2a(message: Dict, context: Dict) -> Dict:
            """
            Transform an A2A protocol message.
            
            Args:
                message: A2A message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Add timestamp if missing
            if "timestamp" not in transformed:
                transformed["timestamp"] = datetime.utcnow().isoformat()
            
            # Add conversation ID if missing
            if "conversation_id" not in transformed:
                transformed["conversation_id"] = context.get("conversation_id", str(uuid.uuid4()))
            
            # Add trace ID if missing
            if "trace_id" not in transformed:
                transformed["trace_id"] = context.get("trace_id", str(uuid.uuid4()))
            
            # Add security metadata
            transformed["_security"] = {
                "processed_by": "protocol_security_gateway",
                "processed_at": datetime.utcnow().isoformat(),
                "trace_id": transformed["trace_id"]
            }
            
            return transformed
        
        return transform_a2a
    
    def _create_http_transformer(self) -> Callable:
        """
        Create a transformer for HTTP protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_http(message: Dict, context: Dict) -> Dict:
            """
            Transform an HTTP protocol message.
            
            Args:
                message: HTTP message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Ensure headers exist
            if "headers" not in transformed:
                transformed["headers"] = {}
            
            # Add security headers
            transformed["headers"]["X-Security-Trace-ID"] = context.get("trace_id", str(uuid.uuid4()))
            transformed["headers"]["X-Security-Processed-At"] = datetime.utcnow().isoformat()
            
            # Add version if missing
            if "version" not in transformed:
                transformed["version"] = "HTTP/1.1"
            
            return transformed
        
        return transform_http
    
    def _create_mqtt_transformer(self) -> Callable:
        """
        Create a transformer for MQTT protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_mqtt(message: Dict, context: Dict) -> Dict:
            """
            Transform an MQTT protocol message.
            
            Args:
                message: MQTT message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Add QoS if missing
            if "qos" not in transformed:
                transformed["qos"] = 1
            
            # Add retain flag if missing
            if "retain" not in transformed:
                transformed["retain"] = False
            
            # Add security metadata to payload if it's a dictionary
            if isinstance(transformed["payload"], dict):
                if "_security" not in transformed["payload"]:
                    transformed["payload"]["_security"] = {}
                
                transformed["payload"]["_security"].update({
                    "processed_by": "protocol_security_gateway",
                    "processed_at": datetime.utcnow().isoformat(),
                    "trace_id": context.get("trace_id", str(uuid.uuid4()))
                })
            
            return transformed
        
        return transform_mqtt
    
    def _create_opc_ua_transformer(self) -> Callable:
        """
        Create a transformer for OPC UA protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_opc_ua(message: Dict, context: Dict) -> Dict:
            """
            Transform an OPC UA protocol message.
            
            Args:
                message: OPC UA message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Add timestamp if missing
            if "timestamp" not in transformed:
                transformed["timestamp"] = datetime.utcnow().isoformat()
            
            # Add security mode if missing
            if "security_mode" not in transformed:
                transformed["security_mode"] = "SignAndEncrypt"
            
            # Add security metadata
            transformed["_security"] = {
                "processed_by": "protocol_security_gateway",
                "processed_at": datetime.utcnow().isoformat(),
                "trace_id": context.get("trace_id", str(uuid.uuid4()))
            }
            
            return transformed
        
        return transform_opc_ua
    
    def _create_modbus_transformer(self) -> Callable:
        """
        Create a transformer for Modbus protocol messages.
        
        Returns:
            Transformer function
        """
        def transform_modbus(message: Dict, context: Dict) -> Dict:
            """
            Transform a Modbus protocol message.
            
            Args:
                message: Modbus message to transform
                context: Context information
                
            Returns:
                Transformed message
            """
            # Create a copy of the message to avoid modifying the original
            transformed = message.copy()
            
            # Add address if missing
            if "address" not in transformed:
                transformed["address"] = 0
            
            # Add transport if missing
            if "transport" not in transformed:
                transformed["transport"] = "tcp"
            
            # Add security metadata
            transformed["_security"] = {
                "processed_by": "protocol_security_gateway",
                "processed_at": datetime.utcnow().isoformat(),
                "trace_id": context.get("trace_id", str(uuid.uuid4()))
            }
            
            return transformed
        
        return transform_modbus
    
    # Anomaly detector implementation
    
    def _create_anomaly_detector(self, protocol: str, sensitivity: str, learning_mode: bool) -> Callable:
        """
        Create an anomaly detector for a protocol.
        
        Args:
            protocol: Protocol identifier
            sensitivity: Sensitivity level (low, medium, high)
            learning_mode: Whether the detector is in learning mode
            
        Returns:
            Anomaly detector function
        """
        # Set sensitivity threshold based on sensitivity level
        if sensitivity == "low":
            threshold = 0.8
        elif sensitivity == "medium":
            threshold = 0.6
        else:  # high
            threshold = 0.4
        
        def detect_anomalies(message: Dict, context: Dict) -> Tuple[bool, float, Optional[str]]:
            """
            Detect anomalies in a protocol message.
            
            Args:
                message: Protocol message to check
                context: Context information
                
            Returns:
                Tuple containing (anomaly_detected, anomaly_score, anomaly_details)
            """
            # In a production environment, this would use a real anomaly detection algorithm
            # For this implementation, we'll use a simple simulation
            
            # Simulate anomaly detection
            anomaly_score = 0.0
            anomaly_details = None
            
            # Check for unusual message structure
            if protocol == "mcp":
                if message["type"] == "request" and "action" not in message.get("content", {}):
                    anomaly_score += 0.3
                    anomaly_details = "Request message missing action in content"
                
                if "source" in message and "destination" in message and message["source"] == message["destination"]:
                    anomaly_score += 0.4
                    anomaly_details = "Source and destination are the same"
            
            elif protocol == "a2a":
                if message["message_type"] == "request" and "action" not in message.get("payload", {}):
                    anomaly_score += 0.3
                    anomaly_details = "Request message missing action in payload"
                
                if "priority" in message and message["priority"] > 4:
                    anomaly_score += 0.2
                    anomaly_details = "Unusually high priority"
            
            # Check for unusual timing
            if "timestamp" in message:
                try:
                    msg_time = datetime.fromisoformat(message["timestamp"])
                    now = datetime.utcnow()
                    
                    # Check if message is from the future
                    if msg_time > now:
                        time_diff = (msg_time - now).total_seconds()
                        if time_diff > 60:  # More than a minute in the future
                            anomaly_score += 0.5
                            anomaly_details = f"Message timestamp is {time_diff} seconds in the future"
                    
                    # Check if message is too old
                    elif now - msg_time > timedelta(days=1):  # More than a day old
                        anomaly_score += 0.3
                        anomaly_details = "Message is more than a day old"
                except ValueError:
                    pass
            
            # In learning mode, just record the anomaly but don't flag it
            if learning_mode:
                return False, anomaly_score, anomaly_details
            
            # Check if anomaly score exceeds threshold
            return anomaly_score > threshold, anomaly_score, anomaly_details
        
        return detect_anomalies


# Example usage
if __name__ == "__main__":
    # Initialize Protocol Security Gateway
    gateway = ProtocolSecurityGateway()
    
    # Add some ACL rules
    gateway.add_acl_rule("mcp", "source:data_layer", "destination:core_ai_layer", "allow")
    gateway.add_acl_rule("a2a", "agent:zk_attestation_agent", "agent:trust_score_agent", "allow")
    
    # Process an MCP message
    mcp_message = {
        "id": "msg123",
        "type": "request",
        "content": {
            "action": "get_model_context",
            "parameters": {
                "model_id": "model123",
                "context_type": "full"
            }
        }
    }
    
    mcp_context = {
        "source": "data_layer",
        "destination": "core_ai_layer",
        "trace_id": "trace123"
    }
    
    success, processed_message, error = gateway.process_message("mcp", mcp_message, mcp_context)
    
    if success:
        print("MCP message processed successfully:")
        print(json.dumps(processed_message, indent=2))
    else:
        print(f"Error processing MCP message: {error}")
    
    # Process an A2A message
    a2a_message = {
        "agent_id": "zk_attestation_agent",
        "message_type": "request",
        "payload": {
            "action": "verify_attestation",
            "parameters": {
                "attestation_id": "att123",
                "verification_level": "full"
            }
        }
    }
    
    a2a_context = {
        "source": "agent:zk_attestation_agent",
        "destination": "agent:trust_score_agent",
        "conversation_id": "conv123",
        "trace_id": "trace456"
    }
    
    success, processed_message, error = gateway.process_message("a2a", a2a_message, a2a_context)
    
    if success:
        print("\nA2A message processed successfully:")
        print(json.dumps(processed_message, indent=2))
    else:
        print(f"Error processing A2A message: {error}")
    
    # Get audit log
    audit_log = gateway.get_audit_log(level="info", limit=5)
    
    print("\nAudit log entries:")
    for entry in audit_log:
        print(f"{entry['timestamp']} [{entry['level']}] {entry['protocol']} - {entry['operation']}: {entry['message']}")
