"""
Agent Capsule Integration for Industriverse Generative Layer

This module implements the agent capsule integration that enables direct user interaction
via the Universal Skin and Dynamic Capsule Panel, supporting UI capsules with
live preview and editable fields.
"""

import json
import logging
import time
import os
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCapsuleIntegration:
    """
    Implements agent capsule integration for the Generative Layer.
    Enables direct user interaction via the Universal Skin and Dynamic Capsule Panel.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the agent capsule integration.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.registered_capsules = {}
        self.active_capsule_sessions = {}
        self.capsule_templates = {}
        
        # Initialize capsule storage
        self.capsule_storage_path = os.path.join(os.getcwd(), "capsule_storage")
        os.makedirs(self.capsule_storage_path, exist_ok=True)
        
        logger.info("Agent Capsule Integration initialized")
    
    def register_capsule(self, 
                        capsule_id: str, 
                        capsule_type: str,
                        metadata: Dict[str, Any],
                        template: Dict[str, Any]) -> bool:
        """
        Register a new UI capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            capsule_type: Type of capsule (form, dashboard, editor, etc.)
            metadata: Metadata about the capsule
            template: Template definition for the capsule
            
        Returns:
            True if registration was successful, False otherwise
        """
        if capsule_id in self.registered_capsules:
            logger.warning(f"Capsule {capsule_id} already registered")
            return False
        
        timestamp = time.time()
        
        # Create capsule record
        capsule = {
            "id": capsule_id,
            "type": capsule_type,
            "metadata": metadata,
            "timestamp": timestamp,
            "status": "registered"
        }
        
        # Store capsule
        self.registered_capsules[capsule_id] = capsule
        
        # Store template
        self.capsule_templates[capsule_id] = template
        
        # Store template file
        template_path = os.path.join(self.capsule_storage_path, f"{capsule_id}_template.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"Registered capsule {capsule_id} of type {capsule_type}")
        
        # Emit MCP event for capsule registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/capsule/registered",
                {
                    "capsule_id": capsule_id,
                    "capsule_type": capsule_type
                }
            )
        
        return True
    
    def create_capsule_session(self, 
                              capsule_id: str, 
                              user_id: str,
                              initial_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a new capsule session for a user.
        
        Args:
            capsule_id: ID of the capsule to create a session for
            user_id: ID of the user
            initial_data: Initial data for the capsule (optional)
            
        Returns:
            Session ID if successful, None otherwise
        """
        if capsule_id not in self.registered_capsules:
            logger.warning(f"Capsule {capsule_id} not found")
            return None
        
        session_id = f"{capsule_id}_{user_id}_{int(time.time())}"
        timestamp = time.time()
        
        # Create session record
        session = {
            "id": session_id,
            "capsule_id": capsule_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "status": "active",
            "data": initial_data or {},
            "history": []
        }
        
        # Store session
        self.active_capsule_sessions[session_id] = session
        
        # Store session file
        session_path = os.path.join(self.capsule_storage_path, f"{session_id}_session.json")
        with open(session_path, 'w') as f:
            json.dump(session, f, indent=2)
        
        logger.info(f"Created capsule session {session_id} for user {user_id}")
        
        # Emit MCP event for session creation
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/capsule/session_created",
                {
                    "session_id": session_id,
                    "capsule_id": capsule_id,
                    "user_id": user_id
                }
            )
        
        return session_id
    
    def update_capsule_session(self, 
                              session_id: str, 
                              data_updates: Dict[str, Any],
                              event_type: str = "user_input") -> bool:
        """
        Update a capsule session with new data.
        
        Args:
            session_id: ID of the session to update
            data_updates: Updates to apply to the session data
            event_type: Type of event that triggered the update
            
        Returns:
            True if update was successful, False otherwise
        """
        if session_id not in self.active_capsule_sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        session = self.active_capsule_sessions[session_id]
        timestamp = time.time()
        
        # Create history record
        history_record = {
            "timestamp": timestamp,
            "event_type": event_type,
            "data_before": session["data"].copy(),
            "updates": data_updates
        }
        
        # Update session data
        session["data"].update(data_updates)
        session["history"].append(history_record)
        
        # Update session file
        session_path = os.path.join(self.capsule_storage_path, f"{session_id}_session.json")
        with open(session_path, 'w') as f:
            json.dump(session, f, indent=2)
        
        logger.info(f"Updated capsule session {session_id}")
        
        # Emit MCP event for session update
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/capsule/session_updated",
                {
                    "session_id": session_id,
                    "event_type": event_type
                }
            )
        
        return True
    
    def get_capsule_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data if found, None otherwise
        """
        if session_id not in self.active_capsule_sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        return self.active_capsule_sessions[session_id]
    
    def close_capsule_session(self, session_id: str, reason: str = "completed") -> bool:
        """
        Close a capsule session.
        
        Args:
            session_id: ID of the session to close
            reason: Reason for closing the session
            
        Returns:
            True if closure was successful, False otherwise
        """
        if session_id not in self.active_capsule_sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        session = self.active_capsule_sessions[session_id]
        timestamp = time.time()
        
        # Update session status
        session["status"] = "closed"
        session["close_reason"] = reason
        session["close_timestamp"] = timestamp
        
        # Update session file
        session_path = os.path.join(self.capsule_storage_path, f"{session_id}_session.json")
        with open(session_path, 'w') as f:
            json.dump(session, f, indent=2)
        
        logger.info(f"Closed capsule session {session_id}")
        
        # Emit MCP event for session closure
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/capsule/session_closed",
                {
                    "session_id": session_id,
                    "reason": reason
                }
            )
        
        return True
    
    def get_capsule_template(self, capsule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule template by ID.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Template data if found, None otherwise
        """
        if capsule_id not in self.capsule_templates:
            logger.warning(f"Capsule template {capsule_id} not found")
            return None
        
        return self.capsule_templates[capsule_id]
    
    def get_capsule_preview(self, 
                           capsule_id: str, 
                           preview_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a preview of a capsule with sample data.
        
        Args:
            capsule_id: ID of the capsule
            preview_data: Sample data for the preview (optional)
            
        Returns:
            Preview data structure
        """
        if capsule_id not in self.registered_capsules:
            logger.warning(f"Capsule {capsule_id} not found")
            return {"error": "Capsule not found"}
        
        capsule = self.registered_capsules[capsule_id]
        template = self.capsule_templates[capsule_id]
        
        # Generate preview
        preview = {
            "capsule_id": capsule_id,
            "capsule_type": capsule["type"],
            "template": template,
            "sample_data": preview_data or self._generate_sample_data(template)
        }
        
        logger.info(f"Generated preview for capsule {capsule_id}")
        
        return preview
    
    def _generate_sample_data(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sample data for a capsule template.
        
        Args:
            template: The capsule template
            
        Returns:
            Sample data
        """
        sample_data = {}
        
        # This is a simplified implementation
        # In a real system, this would generate appropriate sample data
        # based on the template structure and field types
        
        if "fields" in template:
            for field in template["fields"]:
                field_id = field.get("id", "")
                field_type = field.get("type", "text")
                
                if field_type == "text":
                    sample_data[field_id] = "Sample text"
                elif field_type == "number":
                    sample_data[field_id] = 42
                elif field_type == "boolean":
                    sample_data[field_id] = True
                elif field_type == "date":
                    sample_data[field_id] = "2025-05-21"
                elif field_type == "select":
                    options = field.get("options", [])
                    if options:
                        sample_data[field_id] = options[0].get("value", "")
                elif field_type == "multiselect":
                    options = field.get("options", [])
                    if options and len(options) > 1:
                        sample_data[field_id] = [options[0].get("value", ""), options[1].get("value", "")]
                else:
                    sample_data[field_id] = "Sample data"
        
        return sample_data
    
    def register_form_capsule(self, 
                             capsule_id: str, 
                             title: str,
                             description: str,
                             fields: List[Dict[str, Any]],
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a form capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            title: Title of the form
            description: Description of the form
            fields: List of field definitions
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Create form template
        template = {
            "title": title,
            "description": description,
            "fields": fields,
            "layout": "standard",
            "submit_label": "Submit"
        }
        
        # Register capsule
        return self.register_capsule(
            capsule_id=capsule_id,
            capsule_type="form",
            metadata=metadata or {},
            template=template
        )
    
    def register_dashboard_capsule(self, 
                                 capsule_id: str, 
                                 title: str,
                                 description: str,
                                 widgets: List[Dict[str, Any]],
                                 layout: Optional[Dict[str, Any]] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a dashboard capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            title: Title of the dashboard
            description: Description of the dashboard
            widgets: List of widget definitions
            layout: Layout configuration (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Create dashboard template
        template = {
            "title": title,
            "description": description,
            "widgets": widgets,
            "layout": layout or {"type": "grid", "columns": 12}
        }
        
        # Register capsule
        return self.register_capsule(
            capsule_id=capsule_id,
            capsule_type="dashboard",
            metadata=metadata or {},
            template=template
        )
    
    def register_editor_capsule(self, 
                              capsule_id: str, 
                              title: str,
                              description: str,
                              editor_type: str,
                              initial_content: str,
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register an editor capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            title: Title of the editor
            description: Description of the editor
            editor_type: Type of editor (code, text, rich, etc.)
            initial_content: Initial content for the editor
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Create editor template
        template = {
            "title": title,
            "description": description,
            "editor_type": editor_type,
            "initial_content": initial_content,
            "settings": {
                "line_numbers": True,
                "syntax_highlighting": True,
                "auto_save": True
            }
        }
        
        # Register capsule
        return self.register_capsule(
            capsule_id=capsule_id,
            capsule_type="editor",
            metadata=metadata or {},
            template=template
        )
    
    def register_wizard_capsule(self, 
                              capsule_id: str, 
                              title: str,
                              description: str,
                              steps: List[Dict[str, Any]],
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a wizard capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            title: Title of the wizard
            description: Description of the wizard
            steps: List of step definitions
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Create wizard template
        template = {
            "title": title,
            "description": description,
            "steps": steps,
            "settings": {
                "allow_back": True,
                "allow_skip": False,
                "show_progress": True
            }
        }
        
        # Register capsule
        return self.register_capsule(
            capsule_id=capsule_id,
            capsule_type="wizard",
            metadata=metadata or {},
            template=template
        )
    
    def export_capsule_data(self) -> Dict[str, Any]:
        """
        Export capsule data for persistence.
        
        Returns:
            Capsule data
        """
        return {
            "registered_capsules": self.registered_capsules,
            "capsule_templates": self.capsule_templates
        }
    
    def import_capsule_data(self, capsule_data: Dict[str, Any]) -> None:
        """
        Import capsule data from persistence.
        
        Args:
            capsule_data: Capsule data to import
        """
        if "registered_capsules" in capsule_data:
            self.registered_capsules = capsule_data["registered_capsules"]
        
        if "capsule_templates" in capsule_data:
            self.capsule_templates = capsule_data["capsule_templates"]
        
        logger.info("Imported capsule data")
    
    def get_active_sessions_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active capsule sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of active sessions
        """
        active_sessions = [
            session for session in self.active_capsule_sessions.values()
            if session["user_id"] == user_id and session["status"] == "active"
        ]
        
        return active_sessions
    
    def get_capsule_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a capsule session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session history
        """
        if session_id not in self.active_capsule_sessions:
            logger.warning(f"Session {session_id} not found")
            return []
        
        return self.active_capsule_sessions[session_id]["history"]
