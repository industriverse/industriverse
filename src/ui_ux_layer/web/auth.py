"""
Authentication Manager for Web Frontend

This module handles user authentication, session management, and authorization
for the Industriverse UI/UX Layer web frontend.

It integrates with backend authentication services and manages user sessions
within the web application.

The Auth Manager:
1. Handles user login and logout
2. Manages session tokens (e.g., JWT)
3. Performs token validation and refresh
4. Provides user context and role information
5. Implements route protection and authorization checks

Author: Manus
"""

import logging
import time
import uuid
from typing import Dict, Optional, Any
import requests
import jwt
from flask import request, session, redirect, url_for, flash, current_app
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class AuthManager:
    """
    Manages user authentication and session handling for the Flask web frontend.
    """
    
    def __init__(self, app, config: Dict = None):
        """
        Initialize the Auth Manager.
        
        Args:
            app: The Flask application instance
            config: Optional configuration dictionary
        """
        self.app = app
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "auth_backend_url": "http://localhost:8000/api/auth",
            "jwt_secret_key": "default-secret-key",  # Replace with a strong, configured key
            "jwt_algorithm": "HS256",
            "session_timeout": 3600,  # seconds (1 hour)
            "token_refresh_margin": 300,  # seconds (5 minutes)
            "login_route": "/login",
            "logout_route": "/logout",
            "token_verify_route": "/verify_token",
            "token_refresh_route": "/refresh_token",
            "user_info_route": "/user_info",
            "session_cookie_name": "industriverse_session",
            "session_cookie_secure": True,
            "session_cookie_httponly": True,
            "session_cookie_samesite": "Lax",
        }
        
        # Merge provided config with defaults
        self._merge_config()
        
        # Set Flask app config for session management
        self.app.config["SECRET_KEY"] = self.config["jwt_secret_key"]
        self.app.config["SESSION_COOKIE_NAME"] = self.config["session_cookie_name"]
        self.app.config["SESSION_COOKIE_SECURE"] = self.config["session_cookie_secure"]
        self.app.config["SESSION_COOKIE_HTTPONLY"] = self.config["session_cookie_httponly"]
        self.app.config["SESSION_COOKIE_SAMESITE"] = self.config["session_cookie_samesite"]
        self.app.config["PERMANENT_SESSION_LIFETIME"] = self.config["session_timeout"]
        
        logger.info("Auth Manager initialized")

    def _merge_config(self) -> None:
        """Merge provided configuration with defaults."""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                # Merge nested dictionaries
                for nested_key, nested_value in value.items():
                    if nested_key not in self.config[key]:
                        self.config[key][nested_key] = nested_value

    def login(self, username: str, password: str) -> bool:
        """
        Attempt to log in a user.
        
        Args:
            username: User identifier (e.g., email)
            password: User password
            
        Returns:
            Boolean indicating login success
        """
        try:
            login_url = f"{self.config["auth_backend_url"]}{self.config["login_route"]}"
            response = requests.post(login_url, json={"username": username, "password": password}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")
                user_info = data.get("user_info")
                
                if access_token and user_info:
                    # Store tokens and user info in session
                    session["access_token"] = access_token
                    session["refresh_token"] = refresh_token
                    session["user_info"] = user_info
                    session["token_expiry"] = self._get_token_expiry(access_token)
                    session.permanent = True  # Use configured session lifetime
                    
                    logger.info(f"User {username} logged in successfully")
                    return True
                else:
                    logger.error("Login failed: Missing token or user info in backend response")
                    return False
            else:
                logger.warning(f"Login failed for user {username}: Backend status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return False

    def logout(self) -> None:
        """
        Log out the current user.
        """
        user_id = self.get_current_user_id()
        
        # Clear session data
        session.pop("access_token", None)
        session.pop("refresh_token", None)
        session.pop("user_info", None)
        session.pop("token_expiry", None)
        session.clear()
        
        if user_id:
            logger.info(f"User {user_id} logged out")
        else:
            logger.info("User logged out (no user info found in session)")
            
        # Optionally, notify the backend about logout
        # This depends on the backend API design
        # Example:
        # try:
        #     logout_url = f"{self.config["auth_backend_url"]}{self.config["logout_route"]}"
        #     # Send request with appropriate token if needed
        #     requests.post(logout_url, timeout=5)
        # except requests.exceptions.RequestException as e:
        #     logger.warning(f"Failed to notify backend of logout: {str(e)}")

    def is_authenticated(self) -> bool:
        """
        Check if the current user is authenticated.
        
        Returns:
            Boolean indicating authentication status
        """
        access_token = session.get("access_token")
        token_expiry = session.get("token_expiry")
        
        if not access_token or not token_expiry:
            return False
        
        # Check if token is expired
        if time.time() >= token_expiry:
            # Attempt to refresh token
            if not self.refresh_token():
                logger.info("Token expired and refresh failed")
                self.logout()  # Clear invalid session
                return False
            # If refresh succeeded, the token is now valid
        
        # Verify token integrity (optional, if backend verification is not used frequently)
        # try:
        #     jwt.decode(
        #         access_token, 
        #         self.config["jwt_secret_key"], 
        #         algorithms=[self.config["jwt_algorithm"]]
        #     )
        # except jwt.ExpiredSignatureError:
        #     # Should have been caught by expiry check, but handle just in case
        #     if not self.refresh_token():
        #         self.logout()
        #         return False
        # except jwt.InvalidTokenError:
        #     logger.warning("Invalid token found in session")
        #     self.logout()
        #     return False
            
        return True

    def refresh_token(self) -> bool:
        """
        Attempt to refresh the access token using the refresh token.
        
        Returns:
            Boolean indicating refresh success
        """
        refresh_token_val = session.get("refresh_token")
        if not refresh_token_val:
            logger.warning("Cannot refresh token: No refresh token in session")
            return False
            
        try:
            refresh_url = f"{self.config["auth_backend_url"]}{self.config["token_refresh_route"]}"
            response = requests.post(refresh_url, json={"refresh_token": refresh_token_val}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access_token")
                
                if new_access_token:
                    session["access_token"] = new_access_token
                    session["token_expiry"] = self._get_token_expiry(new_access_token)
                    logger.info("Access token refreshed successfully")
                    return True
                else:
                    logger.error("Token refresh failed: No new access token in backend response")
                    return False
            elif response.status_code in [401, 403]:
                logger.warning("Token refresh failed: Invalid or expired refresh token")
                return False
            else:
                logger.error(f"Token refresh failed: Backend status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            return False

    def _get_token_expiry(self, token: str) -> Optional[float]:
        """
        Decode the token to get its expiry time.
        
        Args:
            token: The JWT token string
            
        Returns:
            Expiry timestamp (float) or None if invalid
        """
        try:
            # Decode without verification to get expiry claim
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("exp")
        except jwt.DecodeError:
            logger.error("Failed to decode token to get expiry")
            return None

    def get_current_user_info(self) -> Optional[Dict]:
        """
        Get information about the currently logged-in user.
        
        Returns:
            Dictionary containing user information or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        return session.get("user_info")

    def get_current_user_id(self) -> Optional[str]:
        """
        Get the ID of the currently logged-in user.
        
        Returns:
            User ID string or None if not authenticated
        """
        user_info = self.get_current_user_info()
        return user_info.get("id") if user_info else None

    def get_current_user_roles(self) -> List[str]:
        """
        Get the roles of the currently logged-in user.
        
        Returns:
            List of role strings or an empty list if not authenticated or no roles
        """
        user_info = self.get_current_user_info()
        return user_info.get("roles", []) if user_info else []

    def has_role(self, role: str) -> bool:
        """
        Check if the current user has a specific role.
        
        Args:
            role: The role string to check for
            
        Returns:
            Boolean indicating if the user has the role
        """
        return role in self.get_current_user_roles()

    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token.
        Automatically handles refresh if needed and possible.
        
        Returns:
            Access token string or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        return session.get("access_token")

    def login_required(self, role: Optional[str] = None):
        """
        Decorator to protect routes, requiring login and optionally a specific role.
        
        Args:
            role: Optional role string required to access the route
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    flash("Please log in to access this page.", "warning")
                    # Store the intended URL in the session
                    session["next_url"] = request.url
                    return redirect(url_for("web_frontend.login_page"))  # Assuming login page route name
                
                if role and not self.has_role(role):
                    flash(f"You do not have permission (required role: {role}) to access this page.", "danger")
                    # Redirect to a suitable page, e.g., dashboard or unauthorized page
                    return redirect(url_for("web_frontend.dashboard")) # Assuming dashboard route name
                    
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for making requests to backend services.
        
        Returns:
            Dictionary containing Authorization header or empty dict if not authenticated.
        """
        token = self.get_access_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        else:
            return {}

# Example usage within a Flask app (in web_frontend_core.py or similar):
# from .auth import AuthManager
# 
# app = Flask(__name__)
# # Load config...
# auth_manager = AuthManager(app, app.config.get("AUTH_CONFIG"))
# 
# @app.route("/protected")
# @auth_manager.login_required(role="admin")
# def protected_route():
#     user_info = auth_manager.get_current_user_info()
#     return f"Welcome, {user_info["name"]}! You are an admin."
# 
# @app.route("/login", methods=["GET", "POST"])
# def login_page():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         if auth_manager.login(username, password):
#             next_url = session.pop("next_url", url_for("dashboard"))
#             flash("Login successful!", "success")
#             return redirect(next_url)
#         else:
#             flash("Invalid credentials.", "danger")
#     return render_template("login.html")
# 
# @app.route("/logout")
# def logout_route():
#     auth_manager.logout()
#     flash("You have been logged out.", "info")
#     return redirect(url_for("login_page"))

