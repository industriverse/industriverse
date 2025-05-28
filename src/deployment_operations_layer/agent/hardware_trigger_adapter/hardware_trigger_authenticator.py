"""
Hardware Trigger Authenticator - Authenticates hardware trigger signals

This module authenticates hardware trigger signals to ensure they come from
authorized sources before processing them.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hmac
import hashlib
import base64
import time

logger = logging.getLogger(__name__)

class HardwareTriggerAuthenticator:
    """
    Authenticates hardware trigger signals.
    
    This component is responsible for authenticating hardware trigger signals
    to ensure they come from authorized sources before processing them.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Hardware Trigger Authenticator.
        
        Args:
            config: Configuration dictionary for the authenticator
        """
        self.config = config or {}
        self.auth_keys = {}  # Trigger ID -> Auth key
        self.auth_history = {}  # Trigger ID -> List of auth events
        self.max_history_length = self.config.get("max_history_length", 100)
        self.max_timestamp_skew = self.config.get("max_timestamp_skew", 300)  # 5 minutes
        
        logger.info("Initializing Hardware Trigger Authenticator")
    
    def initialize(self):
        """Initialize the authenticator and load authentication keys."""
        logger.info("Initializing Hardware Trigger Authenticator")
        
        # Load authentication keys
        self._load_auth_keys()
        
        logger.info(f"Loaded {len(self.auth_keys)} authentication keys")
        return True
    
    def authenticate_trigger(self, trigger_id: str, trigger_config: Dict[str, Any], 
                           signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a trigger signal.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with authentication result
        """
        logger.info(f"Authenticating trigger signal for {trigger_id}")
        
        # Check if authentication is required
        auth_required = trigger_config.get("auth_required", True)
        
        if not auth_required:
            logger.info(f"Authentication not required for trigger {trigger_id}")
            return {"authenticated": True, "method": "none"}
        
        # Check if auth key exists
        if trigger_id not in self.auth_keys:
            logger.error(f"No authentication key found for trigger {trigger_id}")
            return {"authenticated": False, "reason": "No authentication key found"}
        
        # Get authentication method
        auth_method = trigger_config.get("auth_method", "hmac")
        
        # Authenticate based on method
        if auth_method == "hmac":
            return self._authenticate_hmac(trigger_id, signal_data)
        elif auth_method == "token":
            return self._authenticate_token(trigger_id, signal_data)
        elif auth_method == "certificate":
            return self._authenticate_certificate(trigger_id, signal_data)
        else:
            logger.error(f"Unsupported authentication method: {auth_method}")
            return {"authenticated": False, "reason": f"Unsupported authentication method: {auth_method}"}
    
    def register_auth_key(self, trigger_id: str, auth_key: Dict[str, Any]) -> bool:
        """
        Register an authentication key for a trigger.
        
        Args:
            trigger_id: ID of the trigger
            auth_key: Authentication key data
            
        Returns:
            True if successful, False otherwise
        """
        if trigger_id in self.auth_keys:
            logger.warning(f"Authentication key for trigger {trigger_id} is already registered")
            return False
        
        # Validate auth key
        if not self._validate_auth_key(auth_key):
            logger.error(f"Invalid authentication key for trigger {trigger_id}")
            return False
        
        # Register auth key
        self.auth_keys[trigger_id] = auth_key
        
        # Save auth keys
        self._save_auth_keys()
        
        logger.info(f"Registered authentication key for trigger {trigger_id}")
        return True
    
    def unregister_auth_key(self, trigger_id: str) -> bool:
        """
        Unregister an authentication key for a trigger.
        
        Args:
            trigger_id: ID of the trigger
            
        Returns:
            True if successful, False otherwise
        """
        if trigger_id not in self.auth_keys:
            logger.warning(f"No authentication key registered for trigger {trigger_id}")
            return False
        
        # Unregister auth key
        del self.auth_keys[trigger_id]
        
        # Save auth keys
        self._save_auth_keys()
        
        logger.info(f"Unregistered authentication key for trigger {trigger_id}")
        return True
    
    def rotate_auth_key(self, trigger_id: str) -> Dict[str, Any]:
        """
        Rotate the authentication key for a trigger.
        
        Args:
            trigger_id: ID of the trigger
            
        Returns:
            Dictionary with rotation result
        """
        if trigger_id not in self.auth_keys:
            logger.warning(f"No authentication key registered for trigger {trigger_id}")
            return {"success": False, "error": "No authentication key registered"}
        
        # Get current auth key
        current_key = self.auth_keys[trigger_id]
        
        # Generate new auth key
        new_key = self._generate_auth_key(current_key.get("method", "hmac"))
        
        # Register new auth key
        self.auth_keys[trigger_id] = new_key
        
        # Save auth keys
        self._save_auth_keys()
        
        logger.info(f"Rotated authentication key for trigger {trigger_id}")
        
        return {
            "success": True,
            "trigger_id": trigger_id,
            "new_key": new_key
        }
    
    def get_auth_history(self, trigger_id: str) -> List[Dict[str, Any]]:
        """
        Get the authentication history for a trigger.
        
        Args:
            trigger_id: ID of the trigger
            
        Returns:
            List of authentication event dictionaries
        """
        return self.auth_history.get(trigger_id, [])
    
    def _authenticate_hmac(self, trigger_id: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a trigger signal using HMAC.
        
        Args:
            trigger_id: ID of the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with authentication result
        """
        # Extract signature and timestamp
        signature = signal_data.get("signature")
        timestamp = signal_data.get("timestamp")
        
        if not signature:
            logger.error("No signature in signal data")
            return {"authenticated": False, "reason": "No signature in signal data"}
        
        if not timestamp:
            logger.error("No timestamp in signal data")
            return {"authenticated": False, "reason": "No timestamp in signal data"}
        
        # Check timestamp to prevent replay attacks
        try:
            signal_time = datetime.fromisoformat(timestamp)
            current_time = datetime.now()
            time_diff = abs((current_time - signal_time).total_seconds())
            
            if time_diff > self.max_timestamp_skew:
                logger.error(f"Timestamp skew too large: {time_diff} seconds")
                return {"authenticated": False, "reason": "Timestamp skew too large"}
        except Exception as e:
            logger.error(f"Invalid timestamp format: {str(e)}")
            return {"authenticated": False, "reason": "Invalid timestamp format"}
        
        # Get auth key
        auth_key = self.auth_keys[trigger_id]
        
        # Get secret key
        secret_key = auth_key.get("secret")
        
        if not secret_key:
            logger.error("No secret key found")
            return {"authenticated": False, "reason": "No secret key found"}
        
        # Create message to sign
        # Remove signature from data to create message
        message_data = signal_data.copy()
        message_data.pop("signature", None)
        
        # Sort keys to ensure consistent order
        message = json.dumps(message_data, sort_keys=True)
        
        # Compute HMAC
        try:
            computed_signature = self._compute_hmac(message, secret_key)
            
            # Compare signatures
            if signature == computed_signature:
                # Record successful authentication
                self._record_auth_event(trigger_id, True, "hmac")
                
                logger.info(f"Successfully authenticated trigger {trigger_id} using HMAC")
                return {"authenticated": True, "method": "hmac"}
            else:
                # Record failed authentication
                self._record_auth_event(trigger_id, False, "hmac", "Invalid signature")
                
                logger.error("Invalid signature")
                return {"authenticated": False, "reason": "Invalid signature"}
        except Exception as e:
            # Record failed authentication
            self._record_auth_event(trigger_id, False, "hmac", f"Error computing HMAC: {str(e)}")
            
            logger.error(f"Error computing HMAC: {str(e)}")
            return {"authenticated": False, "reason": f"Error computing HMAC: {str(e)}"}
    
    def _authenticate_token(self, trigger_id: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a trigger signal using a token.
        
        Args:
            trigger_id: ID of the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with authentication result
        """
        # Extract token
        token = signal_data.get("token")
        
        if not token:
            logger.error("No token in signal data")
            return {"authenticated": False, "reason": "No token in signal data"}
        
        # Get auth key
        auth_key = self.auth_keys[trigger_id]
        
        # Get valid tokens
        valid_tokens = auth_key.get("tokens", [])
        
        if not valid_tokens:
            logger.error("No valid tokens found")
            return {"authenticated": False, "reason": "No valid tokens found"}
        
        # Check if token is valid
        if token in valid_tokens:
            # Record successful authentication
            self._record_auth_event(trigger_id, True, "token")
            
            logger.info(f"Successfully authenticated trigger {trigger_id} using token")
            return {"authenticated": True, "method": "token"}
        else:
            # Record failed authentication
            self._record_auth_event(trigger_id, False, "token", "Invalid token")
            
            logger.error("Invalid token")
            return {"authenticated": False, "reason": "Invalid token"}
    
    def _authenticate_certificate(self, trigger_id: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a trigger signal using a certificate.
        
        Args:
            trigger_id: ID of the trigger
            signal_data: Data from the trigger signal
            
        Returns:
            Dictionary with authentication result
        """
        # This is a placeholder for certificate-based authentication
        # In a real implementation, this would validate a certificate
        
        # Record authentication attempt
        self._record_auth_event(trigger_id, False, "certificate", "Certificate authentication not implemented")
        
        logger.error("Certificate authentication not implemented")
        return {"authenticated": False, "reason": "Certificate authentication not implemented"}
    
    def _compute_hmac(self, message: str, secret_key: str) -> str:
        """
        Compute HMAC for a message.
        
        Args:
            message: Message to sign
            secret_key: Secret key for HMAC
            
        Returns:
            HMAC signature
        """
        # Convert message and key to bytes
        message_bytes = message.encode('utf-8')
        key_bytes = secret_key.encode('utf-8')
        
        # Compute HMAC
        hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
        
        # Get digest and encode as base64
        digest = hmac_obj.digest()
        signature = base64.b64encode(digest).decode('utf-8')
        
        return signature
    
    def _validate_auth_key(self, auth_key: Dict[str, Any]) -> bool:
        """
        Validate an authentication key.
        
        Args:
            auth_key: Authentication key to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "method" not in auth_key:
            logger.error("Missing method in authentication key")
            return False
        
        # Check method-specific fields
        method = auth_key.get("method")
        
        if method == "hmac":
            if "secret" not in auth_key:
                logger.error("Missing secret in HMAC authentication key")
                return False
        elif method == "token":
            if "tokens" not in auth_key or not isinstance(auth_key["tokens"], list):
                logger.error("Missing or invalid tokens in token authentication key")
                return False
        elif method == "certificate":
            if "certificate" not in auth_key:
                logger.error("Missing certificate in certificate authentication key")
                return False
        else:
            logger.error(f"Unsupported authentication method: {method}")
            return False
        
        return True
    
    def _generate_auth_key(self, method: str) -> Dict[str, Any]:
        """
        Generate a new authentication key.
        
        Args:
            method: Authentication method
            
        Returns:
            Generated authentication key
        """
        if method == "hmac":
            # Generate random secret
            secret = base64.b64encode(os.urandom(32)).decode('utf-8')
            
            return {
                "method": "hmac",
                "secret": secret,
                "created": datetime.now().isoformat()
            }
        elif method == "token":
            # Generate random token
            token = base64.b64encode(os.urandom(16)).decode('utf-8')
            
            return {
                "method": "token",
                "tokens": [token],
                "created": datetime.now().isoformat()
            }
        elif method == "certificate":
            # This is a placeholder for certificate generation
            # In a real implementation, this would generate a certificate
            
            return {
                "method": "certificate",
                "certificate": "placeholder",
                "created": datetime.now().isoformat()
            }
        else:
            logger.error(f"Unsupported authentication method: {method}")
            return {}
    
    def _record_auth_event(self, trigger_id: str, success: bool, method: str, reason: str = None):
        """
        Record an authentication event.
        
        Args:
            trigger_id: ID of the trigger
            success: Whether authentication was successful
            method: Authentication method
            reason: Reason for failure (if applicable)
        """
        # Create event
        event = {
            "trigger_id": trigger_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "method": method
        }
        
        if not success and reason:
            event["reason"] = reason
        
        # Initialize history for this trigger if it doesn't exist
        if trigger_id not in self.auth_history:
            self.auth_history[trigger_id] = []
        
        # Add event to history
        self.auth_history[trigger_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.auth_history[trigger_id]) > self.max_history_length:
            self.auth_history[trigger_id] = self.auth_history[trigger_id][-self.max_history_length:]
        
        logger.info(f"Recorded authentication event for trigger {trigger_id}: {'success' if success else 'failure'}")
    
    def _load_auth_keys(self):
        """Load authentication keys from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.auth_keys = {}
            logger.info("Loaded authentication keys")
        except Exception as e:
            logger.error(f"Failed to load authentication keys: {str(e)}")
    
    def _save_auth_keys(self):
        """Save authentication keys to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.auth_keys)} authentication keys")
        except Exception as e:
            logger.error(f"Failed to save authentication keys: {str(e)}")
