"""
User Service for the Industriverse Application Layer.

This module provides user management functionality for the Application Layer.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    """
    User management service for the Application Layer.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the User Service.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.users = {}
        self.user_sessions = {}
        self.user_preferences = {}
        
        logger.info("User Service initialized")
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            user_data: User data
            
        Returns:
            Created user data
        """
        # Validate required fields
        required_fields = ["username", "email", "role"]
        for field in required_fields:
            if field not in user_data:
                return {"error": f"Missing required field: {field}"}
        
        # Check if username already exists
        if user_data["username"] in self.users:
            return {"error": f"Username already exists: {user_data['username']}"}
        
        # Generate user ID
        user_id = f"user-{int(time.time())}-{len(self.users) + 1}"
        
        # Create user
        user = {
            "id": user_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "active",
            **user_data
        }
        
        # Store user
        self.users[user_id] = user
        
        # Initialize user preferences
        self.user_preferences[user_id] = {
            "theme": "default",
            "language": "en",
            "notifications_enabled": True,
            "dashboard_layout": "default"
        }
        
        logger.info(f"Created user: {user_id}")
        
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data or None if not found
        """
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User data or None if not found
        """
        for user_id, user in self.users.items():
            if user.get("username") == username:
                return user
        
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user.
        
        Args:
            user_id: User ID
            updates: Updates to apply
            
        Returns:
            Updated user data or error
        """
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User not found: {user_id}"}
        
        # Get user
        user = self.users[user_id]
        
        # Apply updates
        for key, value in updates.items():
            if key not in ["id", "created_at"]:
                user[key] = value
        
        # Update timestamp
        user["updated_at"] = time.time()
        
        logger.info(f"Updated user: {user_id}")
        
        return user
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            Success message or error
        """
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User not found: {user_id}"}
        
        # Delete user
        del self.users[user_id]
        
        # Delete user preferences
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
        
        # Delete user sessions
        sessions_to_delete = []
        for session_id, session in self.user_sessions.items():
            if session.get("user_id") == user_id:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self.user_sessions[session_id]
        
        logger.info(f"Deleted user: {user_id}")
        
        return {"success": True, "message": f"User deleted: {user_id}"}
    
    def create_session(self, user_id: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user session.
        
        Args:
            user_id: User ID
            device_info: Device information
            
        Returns:
            Session data or error
        """
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User not found: {user_id}"}
        
        # Generate session ID
        session_id = f"session-{int(time.time())}-{len(self.user_sessions) + 1}"
        
        # Create session
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": time.time(),
            "last_activity": time.time(),
            "expires_at": time.time() + 86400,  # 24 hours
            "device_info": device_info,
            "status": "active"
        }
        
        # Store session
        self.user_sessions[session_id] = session
        
        logger.info(f"Created session for user {user_id}: {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        return self.user_sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update session.
        
        Args:
            session_id: Session ID
            updates: Updates to apply
            
        Returns:
            Updated session data or error
        """
        # Check if session exists
        if session_id not in self.user_sessions:
            return {"error": f"Session not found: {session_id}"}
        
        # Get session
        session = self.user_sessions[session_id]
        
        # Apply updates
        for key, value in updates.items():
            if key not in ["id", "user_id", "created_at"]:
                session[key] = value
        
        # Update last activity
        session["last_activity"] = time.time()
        
        logger.info(f"Updated session: {session_id}")
        
        return session
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Success message or error
        """
        # Check if session exists
        if session_id not in self.user_sessions:
            return {"error": f"Session not found: {session_id}"}
        
        # Update session status
        self.user_sessions[session_id]["status"] = "ended"
        self.user_sessions[session_id]["ended_at"] = time.time()
        
        logger.info(f"Ended session: {session_id}")
        
        return {"success": True, "message": f"Session ended: {session_id}"}
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            User preferences or error
        """
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User not found: {user_id}"}
        
        # Get user preferences
        preferences = self.user_preferences.get(user_id, {})
        
        return preferences
    
    def update_user_preferences(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            updates: Updates to apply
            
        Returns:
            Updated user preferences or error
        """
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User not found: {user_id}"}
        
        # Initialize user preferences if not exists
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        # Apply updates
        for key, value in updates.items():
            self.user_preferences[user_id][key] = value
        
        logger.info(f"Updated preferences for user: {user_id}")
        
        return self.user_preferences[user_id]
    
    def get_user_roles(self) -> List[str]:
        """
        Get available user roles.
        
        Returns:
            List of user roles
        """
        return [
            "admin",
            "manager",
            "operator",
            "viewer",
            "developer",
            "analyst"
        ]
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get users by role.
        
        Args:
            role: User role
            
        Returns:
            List of users with the specified role
        """
        return [user for user in self.users.values() if user.get("role") == role]
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """
        Get active users.
        
        Returns:
            List of active users
        """
        return [user for user in self.users.values() if user.get("status") == "active"]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get active sessions.
        
        Returns:
            List of active sessions
        """
        return [session for session in self.user_sessions.values() if session.get("status") == "active"]
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of sessions for the user
        """
        return [session for session in self.user_sessions.values() if session.get("user_id") == user_id]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        sessions_to_cleanup = []
        
        for session_id, session in self.user_sessions.items():
            if session.get("status") == "active" and session.get("expires_at", 0) < current_time:
                sessions_to_cleanup.append(session_id)
        
        for session_id in sessions_to_cleanup:
            self.user_sessions[session_id]["status"] = "expired"
        
        logger.info(f"Cleaned up {len(sessions_to_cleanup)} expired sessions")
        
        return len(sessions_to_cleanup)
    
    def get_observation_data(self) -> Dict[str, Any]:
        """
        Get observation data for the service.
        
        Returns:
            Observation data
        """
        active_users = len(self.get_active_users())
        active_sessions = len(self.get_active_sessions())
        
        return {
            "active_users": active_users,
            "active_sessions": active_sessions,
            "total_users": len(self.users),
            "total_sessions": len(self.user_sessions),
            "users_by_role": {role: len(self.get_users_by_role(role)) for role in self.get_user_roles()}
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get service status.
        
        Returns:
            Service status
        """
        return {
            "status": "operational",
            "active_users": len(self.get_active_users()),
            "active_sessions": len(self.get_active_sessions())
        }
