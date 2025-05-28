"""
Authentication Service

This module provides a comprehensive authentication service for the Deployment Operations Layer.
It handles user authentication, token management, and integration with various identity providers.

The Authentication Service is a critical security component that ensures only authorized users
and systems can access and manage deployment operations.
"""

import logging
import json
import time
import uuid
import hashlib
import base64
import os
import jwt
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AuthenticationService:
    """
    Authentication Service for the Deployment Operations Layer.
    
    This service handles user authentication, token management, and integration with
    various identity providers to ensure secure access to deployment operations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Authentication Service.
        
        Args:
            config: Configuration dictionary for the service
        """
        self.config = config or {}
        
        # Initialize service ID and version
        self.service_id = self.config.get("service_id", "auth-service")
        self.service_version = self.config.get("service_version", "1.0.0")
        
        # Initialize secret key for token signing
        self.secret_key = self.config.get("secret_key", os.urandom(32).hex())
        
        # Initialize token settings
        self.token_settings = self.config.get("token_settings", {
            "access_token_expiry": 3600,  # 1 hour
            "refresh_token_expiry": 86400 * 7,  # 7 days
            "token_algorithm": "HS256"
        })
        
        # Initialize identity providers
        self.identity_providers = self.config.get("identity_providers", {})
        
        # Initialize user store (in a real implementation, this would be a database)
        self.user_store = {}
        
        # Initialize token store (in a real implementation, this would be a database)
        self.token_store = {}
        
        # Initialize session store (in a real implementation, this would be a database)
        self.session_store = {}
        
        logger.info(f"Authentication Service initialized: {self.service_id}")
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Authentication result dictionary
        """
        logger.info(f"Authenticating user: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "Invalid username or password",
                "authenticated": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Verify password
        password_hash = self._hash_password(password, user_data.get("salt", ""))
        if password_hash != user_data.get("password_hash"):
            logger.warning(f"Invalid password for user: {username}")
            return {
                "status": "error",
                "message": "Invalid username or password",
                "authenticated": False
            }
        
        # Generate tokens
        tokens = self._generate_tokens(username, user_data)
        
        # Create session
        session_id = self._create_session(username, tokens)
        
        logger.info(f"User authenticated successfully: {username}")
        
        return {
            "status": "success",
            "message": "Authentication successful",
            "authenticated": True,
            "user_id": user_data.get("user_id"),
            "username": username,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "session_id": session_id,
            "expires_in": self.token_settings["access_token_expiry"]
        }
    
    def authenticate_with_provider(self, provider: str, token: str) -> Dict[str, Any]:
        """
        Authenticate a user with an external identity provider.
        
        Args:
            provider: Identity provider name
            token: Provider-specific token
            
        Returns:
            Authentication result dictionary
        """
        logger.info(f"Authenticating with provider: {provider}")
        
        # Check if provider is configured
        if provider not in self.identity_providers:
            logger.warning(f"Identity provider not configured: {provider}")
            return {
                "status": "error",
                "message": f"Identity provider not configured: {provider}",
                "authenticated": False
            }
        
        # Get provider configuration
        provider_config = self.identity_providers[provider]
        
        # Validate token with provider (in a real implementation, this would call the provider's API)
        # For this example, we'll simulate a successful validation
        user_info = self._validate_provider_token(provider, token, provider_config)
        
        if not user_info:
            logger.warning(f"Invalid token for provider: {provider}")
            return {
                "status": "error",
                "message": "Invalid token",
                "authenticated": False
            }
        
        # Get or create user
        username = user_info.get("email", user_info.get("username", f"{provider}_{user_info.get('id')}")
        
        if username not in self.user_store:
            # Create user
            user_data = {
                "user_id": str(uuid.uuid4()),
                "username": username,
                "email": user_info.get("email"),
                "provider": provider,
                "provider_user_id": user_info.get("id"),
                "created_at": time.time(),
                "roles": ["user"],
                "metadata": {
                    "provider_data": user_info
                }
            }
            
            self.user_store[username] = user_data
        else:
            # Update user data
            user_data = self.user_store[username]
            user_data["metadata"]["provider_data"] = user_info
            user_data["last_login"] = time.time()
            
            self.user_store[username] = user_data
        
        # Generate tokens
        tokens = self._generate_tokens(username, user_data)
        
        # Create session
        session_id = self._create_session(username, tokens)
        
        logger.info(f"User authenticated successfully with provider {provider}: {username}")
        
        return {
            "status": "success",
            "message": "Authentication successful",
            "authenticated": True,
            "user_id": user_data.get("user_id"),
            "username": username,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "session_id": session_id,
            "expires_in": self.token_settings["access_token_expiry"],
            "provider": provider
        }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate an access token.
        
        Args:
            token: Access token
            
        Returns:
            Validation result dictionary
        """
        logger.info("Validating access token")
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.token_settings["token_algorithm"]]
            )
            
            # Check if token is in token store
            token_id = payload.get("jti")
            if token_id not in self.token_store:
                logger.warning(f"Token not found in token store: {token_id}")
                return {
                    "status": "error",
                    "message": "Invalid token",
                    "valid": False
                }
            
            # Check if token is revoked
            token_data = self.token_store[token_id]
            if token_data.get("revoked", False):
                logger.warning(f"Token has been revoked: {token_id}")
                return {
                    "status": "error",
                    "message": "Token has been revoked",
                    "valid": False
                }
            
            # Get user data
            username = payload.get("sub")
            if username not in self.user_store:
                logger.warning(f"User not found for token: {username}")
                return {
                    "status": "error",
                    "message": "User not found",
                    "valid": False
                }
            
            user_data = self.user_store[username]
            
            logger.info(f"Token validated successfully for user: {username}")
            
            return {
                "status": "success",
                "message": "Token is valid",
                "valid": True,
                "user_id": user_data.get("user_id"),
                "username": username,
                "roles": user_data.get("roles", []),
                "expires_at": payload.get("exp")
            }
        
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return {
                "status": "error",
                "message": "Token has expired",
                "valid": False,
                "error_code": "token_expired"
            }
        
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return {
                "status": "error",
                "message": "Invalid token",
                "valid": False,
                "error_code": "invalid_token"
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Refresh result dictionary
        """
        logger.info("Refreshing access token")
        
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=[self.token_settings["token_algorithm"]]
            )
            
            # Check if token is in token store
            token_id = payload.get("jti")
            if token_id not in self.token_store:
                logger.warning(f"Refresh token not found in token store: {token_id}")
                return {
                    "status": "error",
                    "message": "Invalid refresh token",
                    "refreshed": False
                }
            
            # Check if token is revoked
            token_data = self.token_store[token_id]
            if token_data.get("revoked", False):
                logger.warning(f"Refresh token has been revoked: {token_id}")
                return {
                    "status": "error",
                    "message": "Refresh token has been revoked",
                    "refreshed": False
                }
            
            # Check token type
            if token_data.get("token_type") != "refresh":
                logger.warning(f"Invalid token type for refresh: {token_data.get('token_type')}")
                return {
                    "status": "error",
                    "message": "Invalid token type",
                    "refreshed": False
                }
            
            # Get user data
            username = payload.get("sub")
            if username not in self.user_store:
                logger.warning(f"User not found for refresh token: {username}")
                return {
                    "status": "error",
                    "message": "User not found",
                    "refreshed": False
                }
            
            user_data = self.user_store[username]
            
            # Generate new access token
            access_token = self._generate_access_token(username, user_data)
            
            logger.info(f"Access token refreshed successfully for user: {username}")
            
            return {
                "status": "success",
                "message": "Token refreshed successfully",
                "refreshed": True,
                "access_token": access_token,
                "expires_in": self.token_settings["access_token_expiry"]
            }
        
        except jwt.ExpiredSignatureError:
            logger.warning("Refresh token has expired")
            return {
                "status": "error",
                "message": "Refresh token has expired",
                "refreshed": False,
                "error_code": "token_expired"
            }
        
        except jwt.InvalidTokenError:
            logger.warning("Invalid refresh token")
            return {
                "status": "error",
                "message": "Invalid refresh token",
                "refreshed": False,
                "error_code": "invalid_token"
            }
    
    def revoke_token(self, token: str) -> Dict[str, Any]:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
            
        Returns:
            Revocation result dictionary
        """
        logger.info("Revoking token")
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.token_settings["token_algorithm"]],
                options={"verify_exp": False}
            )
            
            # Check if token is in token store
            token_id = payload.get("jti")
            if token_id not in self.token_store:
                logger.warning(f"Token not found in token store: {token_id}")
                return {
                    "status": "error",
                    "message": "Invalid token",
                    "revoked": False
                }
            
            # Revoke token
            token_data = self.token_store[token_id]
            token_data["revoked"] = True
            token_data["revoked_at"] = time.time()
            
            self.token_store[token_id] = token_data
            
            # If this is an access token, also revoke the associated refresh token
            if token_data.get("token_type") == "access" and "refresh_token_id" in token_data:
                refresh_token_id = token_data["refresh_token_id"]
                if refresh_token_id in self.token_store:
                    refresh_token_data = self.token_store[refresh_token_id]
                    refresh_token_data["revoked"] = True
                    refresh_token_data["revoked_at"] = time.time()
                    
                    self.token_store[refresh_token_id] = refresh_token_data
            
            # Get user data
            username = payload.get("sub")
            
            logger.info(f"Token revoked successfully for user: {username}")
            
            return {
                "status": "success",
                "message": "Token revoked successfully",
                "revoked": True,
                "token_id": token_id,
                "username": username
            }
        
        except jwt.InvalidTokenError:
            logger.warning("Invalid token for revocation")
            return {
                "status": "error",
                "message": "Invalid token",
                "revoked": False,
                "error_code": "invalid_token"
            }
    
    def create_user(self, username: str, password: str, email: str = None, roles: List[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: User's username
            password: User's password
            email: User's email
            roles: User's roles
            metadata: Additional user metadata
            
        Returns:
            User creation result dictionary
        """
        logger.info(f"Creating user: {username}")
        
        # Check if user already exists
        if username in self.user_store:
            logger.warning(f"User already exists: {username}")
            return {
                "status": "error",
                "message": "User already exists",
                "created": False
            }
        
        # Generate salt and hash password
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(password, salt)
        
        # Create user data
        user_data = {
            "user_id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": time.time(),
            "roles": roles or ["user"],
            "metadata": metadata or {}
        }
        
        # Store user
        self.user_store[username] = user_data
        
        logger.info(f"User created successfully: {username}")
        
        return {
            "status": "success",
            "message": "User created successfully",
            "created": True,
            "user_id": user_data["user_id"],
            "username": username,
            "roles": user_data["roles"]
        }
    
    def update_user(self, username: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user.
        
        Args:
            username: User's username
            updates: Dictionary of updates to apply
            
        Returns:
            User update result dictionary
        """
        logger.info(f"Updating user: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "User not found",
                "updated": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Apply updates
        for key, value in updates.items():
            # Handle password update separately
            if key == "password":
                salt = os.urandom(16).hex()
                password_hash = self._hash_password(value, salt)
                user_data["password_hash"] = password_hash
                user_data["salt"] = salt
            elif key in ["user_id", "created_at"]:
                # Don't allow updating these fields
                continue
            else:
                user_data[key] = value
        
        # Update last modified timestamp
        user_data["last_modified"] = time.time()
        
        # Store updated user
        self.user_store[username] = user_data
        
        logger.info(f"User updated successfully: {username}")
        
        return {
            "status": "success",
            "message": "User updated successfully",
            "updated": True,
            "user_id": user_data["user_id"],
            "username": username
        }
    
    def delete_user(self, username: str) -> Dict[str, Any]:
        """
        Delete a user.
        
        Args:
            username: User's username
            
        Returns:
            User deletion result dictionary
        """
        logger.info(f"Deleting user: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "User not found",
                "deleted": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Delete user
        del self.user_store[username]
        
        # Revoke all tokens for user
        for token_id, token_data in list(self.token_store.items()):
            if token_data.get("username") == username:
                token_data["revoked"] = True
                token_data["revoked_at"] = time.time()
                
                self.token_store[token_id] = token_data
        
        # Delete all sessions for user
        for session_id, session_data in list(self.session_store.items()):
            if session_data.get("username") == username:
                del self.session_store[session_id]
        
        logger.info(f"User deleted successfully: {username}")
        
        return {
            "status": "success",
            "message": "User deleted successfully",
            "deleted": True,
            "user_id": user_data["user_id"],
            "username": username
        }
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user data.
        
        Args:
            username: User's username
            
        Returns:
            User data dictionary
        """
        logger.info(f"Getting user data: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "User not found",
                "found": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Create safe user data (without sensitive information)
        safe_user_data = {
            "user_id": user_data["user_id"],
            "username": username,
            "email": user_data.get("email"),
            "created_at": user_data.get("created_at"),
            "last_modified": user_data.get("last_modified"),
            "roles": user_data.get("roles", []),
            "provider": user_data.get("provider"),
            "metadata": user_data.get("metadata", {})
        }
        
        logger.info(f"User data retrieved successfully: {username}")
        
        return {
            "status": "success",
            "message": "User data retrieved successfully",
            "found": True,
            "user": safe_user_data
        }
    
    def list_users(self, filters: Dict[str, Any] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        List users.
        
        Args:
            filters: Filters to apply
            page: Page number
            page_size: Page size
            
        Returns:
            User list dictionary
        """
        logger.info("Listing users")
        
        filters = filters or {}
        
        # Apply filters
        filtered_users = []
        for username, user_data in self.user_store.items():
            include = True
            
            for key, value in filters.items():
                if key == "role" and value not in user_data.get("roles", []):
                    include = False
                    break
                elif key == "provider" and value != user_data.get("provider"):
                    include = False
                    break
                elif key == "email" and value != user_data.get("email"):
                    include = False
                    break
            
            if include:
                # Create safe user data (without sensitive information)
                safe_user_data = {
                    "user_id": user_data["user_id"],
                    "username": username,
                    "email": user_data.get("email"),
                    "created_at": user_data.get("created_at"),
                    "roles": user_data.get("roles", []),
                    "provider": user_data.get("provider")
                }
                
                filtered_users.append(safe_user_data)
        
        # Sort users by username
        filtered_users.sort(key=lambda u: u["username"])
        
        # Paginate
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_users = filtered_users[start_index:end_index]
        
        logger.info(f"Listed {len(paginated_users)} users (page {page}, total {len(filtered_users)})")
        
        return {
            "status": "success",
            "message": "Users listed successfully",
            "users": paginated_users,
            "page": page,
            "page_size": page_size,
            "total": len(filtered_users),
            "total_pages": (len(filtered_users) + page_size - 1) // page_size
        }
    
    def add_user_role(self, username: str, role: str) -> Dict[str, Any]:
        """
        Add a role to a user.
        
        Args:
            username: User's username
            role: Role to add
            
        Returns:
            Role addition result dictionary
        """
        logger.info(f"Adding role {role} to user: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "User not found",
                "added": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Check if user already has the role
        if "roles" in user_data and role in user_data["roles"]:
            logger.info(f"User {username} already has role: {role}")
            return {
                "status": "success",
                "message": "User already has the role",
                "added": False,
                "roles": user_data["roles"]
            }
        
        # Add role
        if "roles" not in user_data:
            user_data["roles"] = []
        
        user_data["roles"].append(role)
        
        # Update last modified timestamp
        user_data["last_modified"] = time.time()
        
        # Store updated user
        self.user_store[username] = user_data
        
        logger.info(f"Role {role} added to user {username}")
        
        return {
            "status": "success",
            "message": "Role added successfully",
            "added": True,
            "roles": user_data["roles"]
        }
    
    def remove_user_role(self, username: str, role: str) -> Dict[str, Any]:
        """
        Remove a role from a user.
        
        Args:
            username: User's username
            role: Role to remove
            
        Returns:
            Role removal result dictionary
        """
        logger.info(f"Removing role {role} from user: {username}")
        
        # Check if user exists
        if username not in self.user_store:
            logger.warning(f"User not found: {username}")
            return {
                "status": "error",
                "message": "User not found",
                "removed": False
            }
        
        # Get user data
        user_data = self.user_store[username]
        
        # Check if user has the role
        if "roles" not in user_data or role not in user_data["roles"]:
            logger.info(f"User {username} does not have role: {role}")
            return {
                "status": "success",
                "message": "User does not have the role",
                "removed": False,
                "roles": user_data.get("roles", [])
            }
        
        # Remove role
        user_data["roles"].remove(role)
        
        # Update last modified timestamp
        user_data["last_modified"] = time.time()
        
        # Store updated user
        self.user_store[username] = user_data
        
        logger.info(f"Role {role} removed from user {username}")
        
        return {
            "status": "success",
            "message": "Role removed successfully",
            "removed": True,
            "roles": user_data["roles"]
        }
    
    def _hash_password(self, password: str, salt: str) -> str:
        """
        Hash a password with a salt.
        
        Args:
            password: Password to hash
            salt: Salt to use
            
        Returns:
            Hashed password
        """
        # Combine password and salt
        salted_password = password + salt
        
        # Hash the salted password
        hasher = hashlib.sha256()
        hasher.update(salted_password.encode())
        
        return hasher.hexdigest()
    
    def _generate_tokens(self, username: str, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate access and refresh tokens for a user.
        
        Args:
            username: User's username
            user_data: User data
            
        Returns:
            Dictionary containing access and refresh tokens
        """
        # Generate access token
        access_token = self._generate_access_token(username, user_data)
        
        # Generate refresh token
        refresh_token = self._generate_refresh_token(username, user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def _generate_access_token(self, username: str, user_data: Dict[str, Any]) -> str:
        """
        Generate an access token for a user.
        
        Args:
            username: User's username
            user_data: User data
            
        Returns:
            Access token
        """
        # Generate token ID
        token_id = str(uuid.uuid4())
        
        # Set expiry time
        expiry = int(time.time()) + self.token_settings["access_token_expiry"]
        
        # Create token payload
        payload = {
            "iss": self.service_id,
            "sub": username,
            "iat": int(time.time()),
            "exp": expiry,
            "jti": token_id,
            "user_id": user_data.get("user_id"),
            "roles": user_data.get("roles", [])
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.token_settings["token_algorithm"]
        )
        
        # Store token
        self.token_store[token_id] = {
            "token_id": token_id,
            "username": username,
            "user_id": user_data.get("user_id"),
            "token_type": "access",
            "created_at": time.time(),
            "expires_at": expiry,
            "revoked": False
        }
        
        return token
    
    def _generate_refresh_token(self, username: str, user_data: Dict[str, Any]) -> str:
        """
        Generate a refresh token for a user.
        
        Args:
            username: User's username
            user_data: User data
            
        Returns:
            Refresh token
        """
        # Generate token ID
        token_id = str(uuid.uuid4())
        
        # Set expiry time
        expiry = int(time.time()) + self.token_settings["refresh_token_expiry"]
        
        # Create token payload
        payload = {
            "iss": self.service_id,
            "sub": username,
            "iat": int(time.time()),
            "exp": expiry,
            "jti": token_id,
            "user_id": user_data.get("user_id"),
            "token_type": "refresh"
        }
        
        # Generate token
        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.token_settings["token_algorithm"]
        )
        
        # Store token
        self.token_store[token_id] = {
            "token_id": token_id,
            "username": username,
            "user_id": user_data.get("user_id"),
            "token_type": "refresh",
            "created_at": time.time(),
            "expires_at": expiry,
            "revoked": False
        }
        
        return token
    
    def _create_session(self, username: str, tokens: Dict[str, str]) -> str:
        """
        Create a session for a user.
        
        Args:
            username: User's username
            tokens: Dictionary containing access and refresh tokens
            
        Returns:
            Session ID
        """
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session data
        session_data = {
            "session_id": session_id,
            "username": username,
            "created_at": time.time(),
            "last_activity": time.time(),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "active": True
        }
        
        # Store session
        self.session_store[session_id] = session_data
        
        return session_id
    
    def _validate_provider_token(self, provider: str, token: str, provider_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate a token from an external identity provider.
        
        Args:
            provider: Identity provider name
            token: Provider-specific token
            provider_config: Provider configuration
            
        Returns:
            User information dictionary or None if validation fails
        """
        # In a real implementation, this would call the provider's API to validate the token
        # For this example, we'll simulate a successful validation
        
        # Simulate user info
        user_info = {
            "id": f"provider_user_{int(time.time())}",
            "email": f"user_{int(time.time())}@example.com",
            "name": f"User {int(time.time())}",
            "provider": provider
        }
        
        return user_info
