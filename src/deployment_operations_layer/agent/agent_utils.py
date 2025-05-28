"""
Agent Utilities for the Deployment Operations Layer.

This module provides utility functions for agent operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentUtils:
    """
    Utilities for agent operations.
    
    This class provides utility functions for agent operations,
    including authentication, communication, and data processing.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Agent Utilities.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.utils_id = config.get("utils_id", f"utils-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9007")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize utility configuration
        self.encryption_enabled = config.get("encryption_enabled", True)
        self.compression_enabled = config.get("compression_enabled", True)
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
        
        # Initialize cache
        self.cache = {}
        
        logger.info(f"Agent Utilities {self.utils_id} initialized")
    
    def generate_id(self, prefix: str = "") -> str:
        """
        Generate a unique ID.
        
        Args:
            prefix: ID prefix
            
        Returns:
            str: Unique ID
        """
        return f"{prefix}{uuid.uuid4().hex}"
    
    def generate_timestamp(self) -> str:
        """
        Generate a timestamp.
        
        Returns:
            str: ISO format timestamp
        """
        return datetime.now().isoformat()
    
    def calculate_hash(self, data: Any) -> str:
        """
        Calculate a hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            str: Hash value
        """
        # Convert data to JSON string if not already a string
        if not isinstance(data, str):
            data = json.dumps(data, sort_keys=True)
        
        # Calculate SHA-256 hash
        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()
    
    def encrypt_data(self, data: Any, key: str = None) -> Dict:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Dict: Encrypted data
        """
        if not self.encryption_enabled:
            return {"encrypted": False, "data": data}
        
        try:
            # In a real implementation, this would use proper encryption
            # For now, just simulate encryption with base64 encoding
            
            # Convert data to JSON string if not already a string
            if not isinstance(data, str):
                data = json.dumps(data)
            
            # Encode data
            encoded_data = base64.b64encode(data.encode()).decode()
            
            return {
                "encrypted": True,
                "data": encoded_data,
                "algorithm": "simulated",
                "timestamp": self.generate_timestamp()
            }
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return {"encrypted": False, "data": data, "error": str(e)}
    
    def decrypt_data(self, encrypted_data: Dict, key: str = None) -> Any:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data
            key: Encryption key
            
        Returns:
            Any: Decrypted data
        """
        if not encrypted_data.get("encrypted", False):
            return encrypted_data.get("data")
        
        try:
            # In a real implementation, this would use proper decryption
            # For now, just simulate decryption with base64 decoding
            
            # Decode data
            encoded_data = encrypted_data.get("data", "")
            decoded_data = base64.b64decode(encoded_data.encode()).decode()
            
            # Parse JSON if possible
            try:
                return json.loads(decoded_data)
            except:
                return decoded_data
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None
    
    def compress_data(self, data: Any) -> Dict:
        """
        Compress data.
        
        Args:
            data: Data to compress
            
        Returns:
            Dict: Compressed data
        """
        if not self.compression_enabled:
            return {"compressed": False, "data": data}
        
        try:
            # In a real implementation, this would use proper compression
            # For now, just simulate compression
            
            # Convert data to JSON string if not already a string
            if not isinstance(data, str):
                data = json.dumps(data)
            
            # Simulate compression (no actual compression)
            compressed_data = data
            
            return {
                "compressed": True,
                "data": compressed_data,
                "algorithm": "simulated",
                "original_size": len(data),
                "compressed_size": len(compressed_data),
                "timestamp": self.generate_timestamp()
            }
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            return {"compressed": False, "data": data, "error": str(e)}
    
    def decompress_data(self, compressed_data: Dict) -> Any:
        """
        Decompress data.
        
        Args:
            compressed_data: Compressed data
            
        Returns:
            Any: Decompressed data
        """
        if not compressed_data.get("compressed", False):
            return compressed_data.get("data")
        
        try:
            # In a real implementation, this would use proper decompression
            # For now, just simulate decompression
            
            # Get compressed data
            data = compressed_data.get("data", "")
            
            # Parse JSON if possible
            try:
                return json.loads(data)
            except:
                return data
        except Exception as e:
            logger.error(f"Error decompressing data: {e}")
            return None
    
    def cache_data(self, key: str, data: Any, ttl: int = None) -> bool:
        """
        Cache data.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            
        Returns:
            bool: Success flag
        """
        if not self.cache_enabled:
            return False
        
        try:
            # Set TTL
            if ttl is None:
                ttl = self.cache_ttl
            
            # Calculate expiration time
            expiration = datetime.now() + timedelta(seconds=ttl)
            
            # Store in cache
            self.cache[key] = {
                "data": data,
                "expiration": expiration,
                "timestamp": self.generate_timestamp()
            }
            
            return True
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Tuple[bool, Any]:
        """
        Get cached data.
        
        Args:
            key: Cache key
            
        Returns:
            Tuple[bool, Any]: Success flag and data
        """
        if not self.cache_enabled or key not in self.cache:
            return False, None
        
        try:
            # Get cache entry
            cache_entry = self.cache[key]
            
            # Check expiration
            if datetime.now() > cache_entry["expiration"]:
                # Remove expired entry
                del self.cache[key]
                return False, None
            
            return True, cache_entry["data"]
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return False, None
    
    def clear_cache(self, key: str = None) -> bool:
        """
        Clear cache.
        
        Args:
            key: Cache key to clear (None for all)
            
        Returns:
            bool: Success flag
        """
        try:
            if key is None:
                # Clear all cache
                self.cache = {}
            elif key in self.cache:
                # Clear specific key
                del self.cache[key]
            
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def validate_json(self, json_data: str) -> Tuple[bool, Any, str]:
        """
        Validate JSON data.
        
        Args:
            json_data: JSON data
            
        Returns:
            Tuple[bool, Any, str]: Success flag, parsed data, and error message
        """
        try:
            # Parse JSON
            parsed_data = json.loads(json_data)
            return True, parsed_data, ""
        except Exception as e:
            return False, None, str(e)
    
    def validate_schema(self, data: Dict, schema: Dict) -> Tuple[bool, List[str]]:
        """
        Validate data against a schema.
        
        Args:
            data: Data to validate
            schema: Schema to validate against
            
        Returns:
            Tuple[bool, List[str]]: Success flag and error messages
        """
        try:
            # In a real implementation, this would use a proper schema validator
            # For now, just check required fields
            
            errors = []
            
            # Check required fields
            for field in schema.get("required", []):
                if field not in data:
                    errors.append(f"Missing required field: {field}")
            
            # Check field types
            for field, field_schema in schema.get("properties", {}).items():
                if field in data:
                    field_type = field_schema.get("type")
                    
                    if field_type == "string" and not isinstance(data[field], str):
                        errors.append(f"Field {field} must be a string")
                    elif field_type == "number" and not isinstance(data[field], (int, float)):
                        errors.append(f"Field {field} must be a number")
                    elif field_type == "integer" and not isinstance(data[field], int):
                        errors.append(f"Field {field} must be an integer")
                    elif field_type == "boolean" and not isinstance(data[field], bool):
                        errors.append(f"Field {field} must be a boolean")
                    elif field_type == "array" and not isinstance(data[field], list):
                        errors.append(f"Field {field} must be an array")
                    elif field_type == "object" and not isinstance(data[field], dict):
                        errors.append(f"Field {field} must be an object")
            
            return len(errors) == 0, errors
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return False, [str(e)]
    
    def format_error(self, error: str, context: str = None) -> Dict:
        """
        Format an error.
        
        Args:
            error: Error message
            context: Error context
            
        Returns:
            Dict: Formatted error
        """
        return {
            "status": "error",
            "message": error,
            "context": context,
            "timestamp": self.generate_timestamp()
        }
    
    def format_success(self, message: str, data: Any = None) -> Dict:
        """
        Format a success response.
        
        Args:
            message: Success message
            data: Response data
            
        Returns:
            Dict: Formatted success response
        """
        response = {
            "status": "success",
            "message": message,
            "timestamp": self.generate_timestamp()
        }
        
        if data is not None:
            response["data"] = data
        
        return response
    
    def retry_operation(self, operation_func, *args, max_attempts: int = None, delay: int = None, **kwargs) -> Any:
        """
        Retry an operation.
        
        Args:
            operation_func: Operation function
            *args: Function arguments
            max_attempts: Maximum retry attempts
            delay: Delay between retries in seconds
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Operation result
        """
        # Set defaults
        if max_attempts is None:
            max_attempts = self.retry_attempts
        
        if delay is None:
            delay = 1
        
        # Initialize variables
        attempts = 0
        last_error = None
        
        # Retry loop
        while attempts < max_attempts:
            try:
                # Increment attempts
                attempts += 1
                
                # Execute operation
                result = operation_func(*args, **kwargs)
                
                # Return result on success
                return result
            except Exception as e:
                # Store error
                last_error = e
                
                # Log error
                logger.warning(f"Retry {attempts}/{max_attempts} failed: {e}")
                
                # Delay before next attempt
                if attempts < max_attempts:
                    time.sleep(delay)
        
        # Raise last error after all attempts
        if last_error:
            raise last_error
        
        return None
    
    def parse_duration(self, duration_str: str) -> int:
        """
        Parse a duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., "1h", "30m", "45s")
            
        Returns:
            int: Duration in seconds
        """
        try:
            # Check if already a number
            try:
                return int(duration_str)
            except:
                pass
            
            # Parse duration string
            duration_str = duration_str.lower()
            
            if duration_str.endswith("s"):
                return int(duration_str[:-1])
            elif duration_str.endswith("m"):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith("h"):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith("d"):
                return int(duration_str[:-1]) * 86400
            else:
                return int(duration_str)
        except Exception as e:
            logger.error(f"Error parsing duration: {e}")
            return 0
    
    def format_duration(self, seconds: int) -> str:
        """
        Format a duration in seconds to a human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            str: Formatted duration
        """
        try:
            # Handle negative durations
            if seconds < 0:
                return f"-{self.format_duration(-seconds)}"
            
            # Handle zero duration
            if seconds == 0:
                return "0s"
            
            # Calculate components
            days = seconds // 86400
            seconds %= 86400
            
            hours = seconds // 3600
            seconds %= 3600
            
            minutes = seconds // 60
            seconds %= 60
            
            # Build formatted string
            parts = []
            
            if days > 0:
                parts.append(f"{days}d")
            
            if hours > 0:
                parts.append(f"{hours}h")
            
            if minutes > 0:
                parts.append(f"{minutes}m")
            
            if seconds > 0:
                parts.append(f"{seconds}s")
            
            return " ".join(parts)
        except Exception as e:
            logger.error(f"Error formatting duration: {e}")
            return f"{seconds}s"
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Agent Utilities.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "encryption_enabled" in config:
                self.encryption_enabled = config["encryption_enabled"]
            
            if "compression_enabled" in config:
                self.compression_enabled = config["compression_enabled"]
            
            if "cache_enabled" in config:
                self.cache_enabled = config["cache_enabled"]
            
            if "cache_ttl" in config:
                self.cache_ttl = config["cache_ttl"]
            
            return {
                "status": "success",
                "message": "Agent Utilities configured successfully",
                "utils_id": self.utils_id
            }
        except Exception as e:
            logger.error(f"Error configuring Agent Utilities: {e}")
            return {"status": "error", "message": str(e)}
