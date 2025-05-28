"""
Capsule Definitions Module for the Workflow Automation Layer.

This module implements the capsule definitions UI component that provides
configuration and management capabilities for Dynamic Agent Capsules.
It allows users to define, customize, and manage capsule templates and instances.

Key features:
- Capsule template definition and management
- Capsule instance configuration
- Visual appearance customization
- Behavior configuration
- Integration with Workflow Canvas and Dashboard
- Support for multiple capsule types and roles
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta

class CapsuleTemplate:
    """
    Represents a template for creating Dynamic Agent Capsules.
    
    A capsule template defines the base configuration for a type of capsule.
    """
    
    def __init__(self, 
                template_id: str,
                name: str,
                description: str,
                capsule_type: str,
                visual_config: Dict[str, Any],
                behavior_config: Dict[str, Any],
                workflow_config: Dict[str, Any],
                metadata: Dict[str, Any] = None):
        """
        Initialize a capsule template.
        
        Args:
            template_id: Unique identifier for the template
            name: Name of the template
            description: Description of the template
            capsule_type: Type of capsule (e.g., "workflow", "agent", "task", "monitor")
            visual_config: Visual configuration for the capsule
            behavior_config: Behavior configuration for the capsule
            workflow_config: Workflow integration configuration
            metadata: Optional metadata for the template
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.capsule_type = capsule_type
        self.visual_config = visual_config
        self.behavior_config = behavior_config
        self.workflow_config = workflow_config
        self.metadata = metadata or {
            "created": time.time(),
            "modified": time.time(),
            "version": "1.0",
            "tags": []
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the capsule template to a dictionary.
        
        Returns:
            Dictionary representation of the capsule template
        """
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "capsule_type": self.capsule_type,
            "visual_config": self.visual_config,
            "behavior_config": self.behavior_config,
            "workflow_config": self.workflow_config,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleTemplate':
        """
        Create a capsule template from a dictionary.
        
        Args:
            data: Dictionary representation of the capsule template
            
        Returns:
            CapsuleTemplate instance
        """
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            capsule_type=data["capsule_type"],
            visual_config=data["visual_config"],
            behavior_config=data["behavior_config"],
            workflow_config=data["workflow_config"],
            metadata=data.get("metadata")
        )
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update the capsule template with new values.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "name" in updates:
                self.name = updates["name"]
            
            if "description" in updates:
                self.description = updates["description"]
            
            if "capsule_type" in updates:
                self.capsule_type = updates["capsule_type"]
            
            if "visual_config" in updates:
                self.visual_config.update(updates["visual_config"])
            
            if "behavior_config" in updates:
                self.behavior_config.update(updates["behavior_config"])
            
            if "workflow_config" in updates:
                self.workflow_config.update(updates["workflow_config"])
            
            if "metadata" in updates:
                self.metadata.update(updates["metadata"])
            
            self.metadata["modified"] = time.time()
            
            return True
        except Exception as e:
            print(f"Error updating capsule template: {e}")
            return False


class CapsuleInstance:
    """
    Represents an instance of a Dynamic Agent Capsule.
    
    A capsule instance is created from a template and can be customized.
    """
    
    def __init__(self, 
                instance_id: str,
                template_id: str,
                name: str,
                description: str,
                capsule_type: str,
                visual_config: Dict[str, Any],
                behavior_config: Dict[str, Any],
                workflow_config: Dict[str, Any],
                state: Dict[str, Any] = None,
                metadata: Dict[str, Any] = None):
        """
        Initialize a capsule instance.
        
        Args:
            instance_id: Unique identifier for the instance
            template_id: ID of the template used to create this instance
            name: Name of the instance
            description: Description of the instance
            capsule_type: Type of capsule
            visual_config: Visual configuration for the capsule
            behavior_config: Behavior configuration for the capsule
            workflow_config: Workflow integration configuration
            state: Optional current state of the capsule
            metadata: Optional metadata for the instance
        """
        self.instance_id = instance_id
        self.template_id = template_id
        self.name = name
        self.description = description
        self.capsule_type = capsule_type
        self.visual_config = visual_config
        self.behavior_config = behavior_config
        self.workflow_config = workflow_config
        self.state = state or {
            "status": "inactive",
            "last_active": None,
            "data": {}
        }
        self.metadata = metadata or {
            "created": time.time(),
            "modified": time.time(),
            "version": "1.0",
            "tags": []
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the capsule instance to a dictionary.
        
        Returns:
            Dictionary representation of the capsule instance
        """
        return {
            "instance_id": self.instance_id,
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "capsule_type": self.capsule_type,
            "visual_config": self.visual_config,
            "behavior_config": self.behavior_config,
            "workflow_config": self.workflow_config,
            "state": self.state,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleInstance':
        """
        Create a capsule instance from a dictionary.
        
        Args:
            data: Dictionary representation of the capsule instance
            
        Returns:
            CapsuleInstance instance
        """
        return cls(
            instance_id=data["instance_id"],
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            capsule_type=data["capsule_type"],
            visual_config=data["visual_config"],
            behavior_config=data["behavior_config"],
            workflow_config=data["workflow_config"],
            state=data.get("state"),
            metadata=data.get("metadata")
        )
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Update the capsule instance with new values.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if "name" in updates:
                self.name = updates["name"]
            
            if "description" in updates:
                self.description = updates["description"]
            
            if "visual_config" in updates:
                self.visual_config.update(updates["visual_config"])
            
            if "behavior_config" in updates:
                self.behavior_config.update(updates["behavior_config"])
            
            if "workflow_config" in updates:
                self.workflow_config.update(updates["workflow_config"])
            
            if "state" in updates:
                self.state.update(updates["state"])
            
            if "metadata" in updates:
                self.metadata.update(updates["metadata"])
            
            self.metadata["modified"] = time.time()
            
            return True
        except Exception as e:
            print(f"Error updating capsule instance: {e}")
            return False
    
    def update_state(self, state_updates: Dict[str, Any]) -> bool:
        """
        Update the state of the capsule instance.
        
        Args:
            state_updates: Dictionary of state updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.state.update(state_updates)
            
            if "status" in state_updates:
                if state_updates["status"] in ["active", "processing", "waiting"]:
                    self.state["last_active"] = time.time()
            
            self.metadata["modified"] = time.time()
            
            return True
        except Exception as e:
            print(f"Error updating capsule state: {e}")
            return False
    
    @classmethod
    def from_template(cls, 
                     template: CapsuleTemplate,
                     instance_id: Optional[str] = None,
                     name: Optional[str] = None,
                     description: Optional[str] = None) -> 'CapsuleInstance':
        """
        Create a capsule instance from a template.
        
        Args:
            template: Template to create the instance from
            instance_id: Optional unique identifier for the instance
            name: Optional name for the instance
            description: Optional description for the instance
            
        Returns:
            CapsuleInstance instance
        """
        instance_id = instance_id or f"capsule-{uuid.uuid4()}"
        name = name or f"{template.name} Instance"
        description = description or template.description
        
        return cls(
            instance_id=instance_id,
            template_id=template.template_id,
            name=name,
            description=description,
            capsule_type=template.capsule_type,
            visual_config=dict(template.visual_config),
            behavior_config=dict(template.behavior_config),
            workflow_config=dict(template.workflow_config),
            metadata={
                "created": time.time(),
                "modified": time.time(),
                "version": "1.0",
                "tags": template.metadata.get("tags", [])[:]
            }
        )


class CapsuleDefinitionsManager:
    """
    Manages capsule templates and instances for the Workflow Automation Layer.
    
    This class provides methods for creating, managing, and persisting
    capsule templates and instances.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Capsule Definitions Manager.
        
        Args:
            storage_path: Optional path for storing capsule definitions
        """
        self.storage_path = storage_path or "/data/capsule_definitions"
        self.templates: Dict[str, CapsuleTemplate] = {}
        self.instances: Dict[str, CapsuleInstance] = {}
        self._load_definitions()
        
    def _load_definitions(self):
        """Load capsule definitions from persistent storage."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            self._create_default_templates()
            return
        
        templates_path = os.path.join(self.storage_path, "templates")
        instances_path = os.path.join(self.storage_path, "instances")
        
        # Load templates
        if os.path.exists(templates_path):
            for filename in os.listdir(templates_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(templates_path, filename), 'r') as f:
                            template_data = json.load(f)
                            template = CapsuleTemplate.from_dict(template_data)
                            self.templates[template.template_id] = template
                    except Exception as e:
                        print(f"Error loading template {filename}: {e}")
        else:
            os.makedirs(templates_path, exist_ok=True)
            self._create_default_templates()
        
        # Load instances
        if os.path.exists(instances_path):
            for filename in os.listdir(instances_path):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(instances_path, filename), 'r') as f:
                            instance_data = json.load(f)
                            instance = CapsuleInstance.from_dict(instance_data)
                            self.instances[instance.instance_id] = instance
                    except Exception as e:
                        print(f"Error loading instance {filename}: {e}")
        else:
            os.makedirs(instances_path, exist_ok=True)
    
    def _create_default_templates(self):
        """Create default capsule templates."""
        # Workflow Capsule Template
        workflow_template = CapsuleTemplate(
            template_id="template-workflow-default",
            name="Default Workflow Capsule",
            description="A default template for workflow capsules",
            capsule_type="workflow",
            visual_config={
                "icon": "workflow",
                "color": "#3498db",
                "size": "medium",
                "animation": "pulse",
                "badge": {
                    "enabled": True,
                    "position": "top-right"
                },
                "expanded_view": {
                    "width": 400,
                    "height": 300,
                    "components": ["header", "status", "controls", "timeline", "details"]
                }
            },
            behavior_config={
                "notification": {
                    "level": "medium",
                    "sound": False,
                    "vibration": False
                },
                "interaction": {
                    "click": "expand",
                    "double_click": "open_details",
                    "drag": "move"
                },
                "lifecycle": {
                    "auto_close": False,
                    "persistence": "session"
                },
                "trust_visualization": {
                    "enabled": True,
                    "style": "color_gradient"
                }
            },
            workflow_config={
                "status_mapping": {
                    "pending": {"icon": "clock", "color": "#f39c12"},
                    "running": {"icon": "play", "color": "#2ecc71"},
                    "paused": {"icon": "pause", "color": "#f39c12"},
                    "completed": {"icon": "check", "color": "#27ae60"},
                    "failed": {"icon": "times", "color": "#e74c3c"}
                },
                "controls": ["start", "pause", "stop", "details"],
                "data_display": ["progress", "duration", "status"],
                "execution_mode_indicators": {
                    "enabled": True,
                    "position": "top-left"
                }
            }
        )
        
        # Agent Capsule Template
        agent_template = CapsuleTemplate(
            template_id="template-agent-default",
            name="Default Agent Capsule",
            description="A default template for agent capsules",
            capsule_type="agent",
            visual_config={
                "icon": "user-robot",
                "color": "#9b59b6",
                "size": "medium",
                "animation": "bounce",
                "badge": {
                    "enabled": True,
                    "position": "top-right"
                },
                "expanded_view": {
                    "width": 350,
                    "height": 250,
                    "components": ["header", "status", "controls", "memory", "capabilities"]
                }
            },
            behavior_config={
                "notification": {
                    "level": "high",
                    "sound": True,
                    "vibration": False
                },
                "interaction": {
                    "click": "expand",
                    "double_click": "open_details",
                    "drag": "move"
                },
                "lifecycle": {
                    "auto_close": False,
                    "persistence": "permanent"
                },
                "trust_visualization": {
                    "enabled": True,
                    "style": "badge"
                }
            },
            workflow_config={
                "status_mapping": {
                    "idle": {"icon": "sleep", "color": "#95a5a6"},
                    "thinking": {"icon": "brain", "color": "#3498db"},
                    "working": {"icon": "cog", "color": "#2ecc71"},
                    "waiting": {"icon": "hourglass", "color": "#f39c12"},
                    "error": {"icon": "exclamation", "color": "#e74c3c"}
                },
                "controls": ["message", "assign", "details", "memory"],
                "data_display": ["status", "task_count", "memory_usage"],
                "capabilities_display": {
                    "enabled": True,
                    "style": "icons"
                }
            }
        )
        
        # Task Capsule Template
        task_template = CapsuleTemplate(
            template_id="template-task-default",
            name="Default Task Capsule",
            description="A default template for task capsules",
            capsule_type="task",
            visual_config={
                "icon": "tasks",
                "color": "#e67e22",
                "size": "small",
                "animation": "slide",
                "badge": {
                    "enabled": True,
                    "position": "top-right"
                },
                "expanded_view": {
                    "width": 300,
                    "height": 200,
                    "components": ["header", "status", "controls", "details", "dependencies"]
                }
            },
            behavior_config={
                "notification": {
                    "level": "low",
                    "sound": False,
                    "vibration": False
                },
                "interaction": {
                    "click": "expand",
                    "double_click": "open_details",
                    "drag": "move"
                },
                "lifecycle": {
                    "auto_close": True,
                    "persistence": "workflow"
                },
                "trust_visualization": {
                    "enabled": True,
                    "style": "border"
                }
            },
            workflow_config={
                "status_mapping": {
                    "pending": {"icon": "clock", "color": "#f39c12"},
                    "assigned": {"icon": "user-check", "color": "#3498db"},
                    "in_progress": {"icon": "spinner", "color": "#2ecc71"},
                    "blocked": {"icon": "ban", "color": "#e74c3c"},
                    "completed": {"icon": "check", "color": "#27ae60"},
                    "failed": {"icon": "times", "color": "#e74c3c"}
                },
                "controls": ["start", "complete", "reassign", "details"],
                "data_display": ["status", "assignee", "deadline"],
                "dependency_visualization": {
                    "enabled": True,
                    "style": "arrows"
                }
            }
        )
        
        # Monitor Capsule Template
        monitor_template = CapsuleTemplate(
            template_id="template-monitor-default",
            name="Default Monitor Capsule",
            description="A default template for monitoring capsules",
            capsule_type="monitor",
            visual_config={
                "icon": "chart-line",
                "color": "#1abc9c",
                "size": "medium",
                "animation": "none",
                "badge": {
                    "enabled": True,
                    "position": "top-right"
                },
                "expanded_view": {
                    "width": 500,
                    "height": 400,
                    "components": ["header", "controls", "chart", "metrics", "alerts"]
                }
            },
            behavior_config={
                "notification": {
                    "level": "dynamic",
                    "sound": True,
                    "vibration": False
                },
                "interaction": {
                    "click": "expand",
                    "double_click": "open_details",
                    "drag": "move"
                },
                "lifecycle": {
                    "auto_close": False,
                    "persistence": "permanent"
                },
                "trust_visualization": {
                    "enabled": False,
                    "style": "none"
                }
            },
            workflow_config={
                "status_mapping": {
                    "normal": {"icon": "check-circle", "color": "#2ecc71"},
                    "warning": {"icon": "exclamation-triangle", "color": "#f39c12"},
                    "critical": {"icon": "exclamation-circle", "color": "#e74c3c"},
                    "unknown": {"icon": "question-circle", "color": "#95a5a6"}
                },
                "controls": ["refresh", "settings", "alerts", "details"],
                "data_display": ["status", "last_updated", "trend"],
                "alert_configuration": {
                    "enabled": True,
                    "levels": ["warning", "critical"]
                }
            }
        )
        
        # Add templates
        self.templates[workflow_template.template_id] = workflow_template
        self.templates[agent_template.template_id] = agent_template
        self.templates[task_template.template_id] = task_template
        self.templates[monitor_template.template_id] = monitor_template
        
        # Store templates
        for template in self.templates.values():
            self._store_template(template)
    
    def _store_template(self, template: CapsuleTemplate):
        """
        Store a template to persistent storage.
        
        Args:
            template: The template to store
        """
        templates_path = os.path.join(self.storage_path, "templates")
        if not os.path.exists(templates_path):
            os.makedirs(templates_path, exist_ok=True)
        
        file_path = os.path.join(templates_path, f"{template.template_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error storing template: {e}")
    
    def _store_instance(self, instance: CapsuleInstance):
        """
        Store an instance to persistent storage.
        
        Args:
            instance: The instance to store
        """
        instances_path = os.path.join(self.storage_path, "instances")
        if not os.path.exists(instances_path):
            os.makedirs(instances_path, exist_ok=True)
        
        file_path = os.path.join(instances_path, f"{instance.instance_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(instance.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error storing instance: {e}")
    
    def create_template(self, 
                       name: str,
                       description: str,
                       capsule_type: str,
                       visual_config: Dict[str, Any],
                       behavior_config: Dict[str, Any],
                       workflow_config: Dict[str, Any],
                       metadata: Dict[str, Any] = None,
                       template_id: Optional[str] = None) -> CapsuleTemplate:
        """
        Create a new capsule template.
        
        Args:
            name: Name for the template
            description: Description for the template
            capsule_type: Type of capsule
            visual_config: Visual configuration for the capsule
            behavior_config: Behavior configuration for the capsule
            workflow_config: Workflow integration configuration
            metadata: Optional metadata for the template
            template_id: Optional unique identifier for the template
            
        Returns:
            The created template
        """
        template_id = template_id or f"template-{uuid.uuid4()}"
        
        template = CapsuleTemplate(
            template_id=template_id,
            name=name,
            description=description,
            capsule_type=capsule_type,
            visual_config=visual_config,
            behavior_config=behavior_config,
            workflow_config=workflow_config,
            metadata=metadata
        )
        
        self.templates[template.template_id] = template
        self._store_template(template)
        
        return template
    
    def get_template(self, template_id: str) -> Optional[CapsuleTemplate]:
        """
        Get a template by its identifier.
        
        Args:
            template_id: Identifier for the template
            
        Returns:
            The template if found, None otherwise
        """
        return self.templates.get(template_id)
    
    def list_templates(self, capsule_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available templates.
        
        Args:
            capsule_type: Optional type to filter by
            
        Returns:
            List of template metadata
        """
        templates = self.templates.values()
        
        if capsule_type:
            templates = [t for t in templates if t.capsule_type == capsule_type]
        
        return [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "capsule_type": t.capsule_type,
                "created": t.metadata.get("created", 0),
                "modified": t.metadata.get("modified", 0),
                "version": t.metadata.get("version", "1.0"),
                "tags": t.metadata.get("tags", [])
            }
            for t in templates
        ]
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[CapsuleTemplate]:
        """
        Update a template.
        
        Args:
            template_id: Identifier for the template
            updates: Updates to apply to the template
            
        Returns:
            The updated template if successful, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        if template.update(updates):
            self._store_template(template)
            return template
        
        return None
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Identifier for the template
            
        Returns:
            True if successful, False otherwise
        """
        if template_id not in self.templates:
            return False
        
        # Check if any instances use this template
        for instance in self.instances.values():
            if instance.template_id == template_id:
                return False
        
        # Remove from memory
        del self.templates[template_id]
        
        # Remove from storage
        templates_path = os.path.join(self.storage_path, "templates")
        file_path = os.path.join(templates_path, f"{template_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def create_instance(self, 
                       template_id: str,
                       name: Optional[str] = None,
                       description: Optional[str] = None,
                       instance_id: Optional[str] = None) -> Optional[CapsuleInstance]:
        """
        Create a new capsule instance from a template.
        
        Args:
            template_id: Identifier for the template
            name: Optional name for the instance
            description: Optional description for the instance
            instance_id: Optional unique identifier for the instance
            
        Returns:
            The created instance if successful, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        instance = CapsuleInstance.from_template(
            template=template,
            instance_id=instance_id,
            name=name,
            description=description
        )
        
        self.instances[instance.instance_id] = instance
        self._store_instance(instance)
        
        return instance
    
    def get_instance(self, instance_id: str) -> Optional[CapsuleInstance]:
        """
        Get an instance by its identifier.
        
        Args:
            instance_id: Identifier for the instance
            
        Returns:
            The instance if found, None otherwise
        """
        return self.instances.get(instance_id)
    
    def list_instances(self, 
                      capsule_type: Optional[str] = None,
                      template_id: Optional[str] = None,
                      status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available instances.
        
        Args:
            capsule_type: Optional type to filter by
            template_id: Optional template ID to filter by
            status: Optional status to filter by
            
        Returns:
            List of instance metadata
        """
        instances = self.instances.values()
        
        if capsule_type:
            instances = [i for i in instances if i.capsule_type == capsule_type]
        
        if template_id:
            instances = [i for i in instances if i.template_id == template_id]
        
        if status:
            instances = [i for i in instances if i.state.get("status") == status]
        
        return [
            {
                "instance_id": i.instance_id,
                "template_id": i.template_id,
                "name": i.name,
                "description": i.description,
                "capsule_type": i.capsule_type,
                "status": i.state.get("status", "inactive"),
                "created": i.metadata.get("created", 0),
                "modified": i.metadata.get("modified", 0),
                "last_active": i.state.get("last_active"),
                "tags": i.metadata.get("tags", [])
            }
            for i in instances
        ]
    
    def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> Optional[CapsuleInstance]:
        """
        Update an instance.
        
        Args:
            instance_id: Identifier for the instance
            updates: Updates to apply to the instance
            
        Returns:
            The updated instance if successful, None otherwise
        """
        instance = self.get_instance(instance_id)
        if not instance:
            return None
        
        if instance.update(updates):
            self._store_instance(instance)
            return instance
        
        return None
    
    def update_instance_state(self, instance_id: str, state_updates: Dict[str, Any]) -> Optional[CapsuleInstance]:
        """
        Update the state of an instance.
        
        Args:
            instance_id: Identifier for the instance
            state_updates: State updates to apply
            
        Returns:
            The updated instance if successful, None otherwise
        """
        instance = self.get_instance(instance_id)
        if not instance:
            return None
        
        if instance.update_state(state_updates):
            self._store_instance(instance)
            return instance
        
        return None
    
    def delete_instance(self, instance_id: str) -> bool:
        """
        Delete an instance.
        
        Args:
            instance_id: Identifier for the instance
            
        Returns:
            True if successful, False otherwise
        """
        if instance_id not in self.instances:
            return False
        
        # Remove from memory
        del self.instances[instance_id]
        
        # Remove from storage
        instances_path = os.path.join(self.storage_path, "instances")
        file_path = os.path.join(instances_path, f"{instance_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting instance: {e}")
            return False


class CapsuleDefinitionsService:
    """
    Service for integrating the capsule definitions with the Workflow Automation Layer.
    
    This class provides methods for managing capsule definitions and
    handling user interactions.
    """
    
    def __init__(self, definitions_manager: CapsuleDefinitionsManager):
        """
        Initialize the Capsule Definitions Service.
        
        Args:
            definitions_manager: Capsule Definitions Manager instance
        """
        self.definitions_manager = definitions_manager
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
    def register_update_callback(self, callback_id: str, callback: Callable):
        """
        Register a callback for definition updates.
        
        Args:
            callback_id: Identifier for the callback
            callback: Callback function
        """
        if callback_id not in self.update_callbacks:
            self.update_callbacks[callback_id] = []
            
        self.update_callbacks[callback_id].append(callback)
    
    def unregister_update_callback(self, callback_id: str, callback: Callable) -> bool:
        """
        Unregister a callback for definition updates.
        
        Args:
            callback_id: Identifier for the callback
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if callback_id not in self.update_callbacks:
            return False
        
        if callback in self.update_callbacks[callback_id]:
            self.update_callbacks[callback_id].remove(callback)
            return True
        
        return False
    
    def notify_update(self, 
                     update_type: str,
                     update_data: Dict[str, Any]):
        """
        Notify update callbacks of a definition update.
        
        Args:
            update_type: Type of the update
            update_data: Update data
        """
        for callback_id, callbacks in self.update_callbacks.items():
            for callback in callbacks:
                try:
                    callback(update_type, update_data)
                except Exception as e:
                    print(f"Error in update callback {callback_id}: {e}")
    
    def create_template(self, 
                       name: str,
                       description: str,
                       capsule_type: str,
                       visual_config: Dict[str, Any],
                       behavior_config: Dict[str, Any],
                       workflow_config: Dict[str, Any],
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new capsule template.
        
        Args:
            name: Name for the template
            description: Description for the template
            capsule_type: Type of capsule
            visual_config: Visual configuration for the capsule
            behavior_config: Behavior configuration for the capsule
            workflow_config: Workflow integration configuration
            metadata: Optional metadata for the template
            
        Returns:
            The created template as a dictionary if successful, error otherwise
        """
        try:
            template = self.definitions_manager.create_template(
                name=name,
                description=description,
                capsule_type=capsule_type,
                visual_config=visual_config,
                behavior_config=behavior_config,
                workflow_config=workflow_config,
                metadata=metadata
            )
            
            # Notify update
            self.notify_update(
                update_type="template_created",
                update_data={
                    "template_id": template.template_id,
                    "template": template.to_dict()
                }
            )
            
            return {
                "success": True,
                "template": template.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a capsule template.
        
        Args:
            template_id: Identifier for the template
            updates: Updates to apply to the template
            
        Returns:
            The updated template as a dictionary if successful, error otherwise
        """
        try:
            template = self.definitions_manager.update_template(template_id, updates)
            
            if template:
                # Notify update
                self.notify_update(
                    update_type="template_updated",
                    update_data={
                        "template_id": template.template_id,
                        "template": template.to_dict(),
                        "updates": updates
                    }
                )
                
                return {
                    "success": True,
                    "template": template.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found or update failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """
        Delete a capsule template.
        
        Args:
            template_id: Identifier for the template
            
        Returns:
            Success status and message
        """
        try:
            success = self.definitions_manager.delete_template(template_id)
            
            if success:
                # Notify update
                self.notify_update(
                    update_type="template_deleted",
                    update_data={
                        "template_id": template_id
                    }
                )
                
                return {
                    "success": True,
                    "message": f"Template {template_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found or in use by instances"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_instance(self, 
                       template_id: str,
                       name: Optional[str] = None,
                       description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new capsule instance from a template.
        
        Args:
            template_id: Identifier for the template
            name: Optional name for the instance
            description: Optional description for the instance
            
        Returns:
            The created instance as a dictionary if successful, error otherwise
        """
        try:
            instance = self.definitions_manager.create_instance(
                template_id=template_id,
                name=name,
                description=description
            )
            
            if instance:
                # Notify update
                self.notify_update(
                    update_type="instance_created",
                    update_data={
                        "instance_id": instance.instance_id,
                        "instance": instance.to_dict()
                    }
                )
                
                return {
                    "success": True,
                    "instance": instance.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a capsule instance.
        
        Args:
            instance_id: Identifier for the instance
            updates: Updates to apply to the instance
            
        Returns:
            The updated instance as a dictionary if successful, error otherwise
        """
        try:
            instance = self.definitions_manager.update_instance(instance_id, updates)
            
            if instance:
                # Notify update
                self.notify_update(
                    update_type="instance_updated",
                    update_data={
                        "instance_id": instance.instance_id,
                        "instance": instance.to_dict(),
                        "updates": updates
                    }
                )
                
                return {
                    "success": True,
                    "instance": instance.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instance {instance_id} not found or update failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_instance_state(self, instance_id: str, state_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state of a capsule instance.
        
        Args:
            instance_id: Identifier for the instance
            state_updates: State updates to apply
            
        Returns:
            The updated instance as a dictionary if successful, error otherwise
        """
        try:
            instance = self.definitions_manager.update_instance_state(instance_id, state_updates)
            
            if instance:
                # Notify update
                self.notify_update(
                    update_type="instance_state_updated",
                    update_data={
                        "instance_id": instance.instance_id,
                        "instance": instance.to_dict(),
                        "state_updates": state_updates
                    }
                )
                
                return {
                    "success": True,
                    "instance": instance.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instance {instance_id} not found or update failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Delete a capsule instance.
        
        Args:
            instance_id: Identifier for the instance
            
        Returns:
            Success status and message
        """
        try:
            success = self.definitions_manager.delete_instance(instance_id)
            
            if success:
                # Notify update
                self.notify_update(
                    update_type="instance_deleted",
                    update_data={
                        "instance_id": instance_id
                    }
                )
                
                return {
                    "success": True,
                    "message": f"Instance {instance_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Instance {instance_id} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_user_interaction(self, 
                              interaction_type: str,
                              interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user interaction with the capsule definitions.
        
        Args:
            interaction_type: Type of the interaction
            interaction_data: Interaction data
            
        Returns:
            Response data
        """
        if interaction_type == "list_templates":
            capsule_type = interaction_data.get("capsule_type")
            
            templates = self.definitions_manager.list_templates(capsule_type)
            
            return {
                "success": True,
                "templates": templates
            }
            
        elif interaction_type == "get_template":
            template_id = interaction_data.get("template_id")
            
            if not template_id:
                return {
                    "success": False,
                    "error": "Missing template_id parameter"
                }
            
            template = self.definitions_manager.get_template(template_id)
            
            if template:
                return {
                    "success": True,
                    "template": template.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Template {template_id} not found"
                }
                
        elif interaction_type == "list_instances":
            capsule_type = interaction_data.get("capsule_type")
            template_id = interaction_data.get("template_id")
            status = interaction_data.get("status")
            
            instances = self.definitions_manager.list_instances(
                capsule_type=capsule_type,
                template_id=template_id,
                status=status
            )
            
            return {
                "success": True,
                "instances": instances
            }
            
        elif interaction_type == "get_instance":
            instance_id = interaction_data.get("instance_id")
            
            if not instance_id:
                return {
                    "success": False,
                    "error": "Missing instance_id parameter"
                }
            
            instance = self.definitions_manager.get_instance(instance_id)
            
            if instance:
                return {
                    "success": True,
                    "instance": instance.to_dict()
                }
            else:
                return {
                    "success": False,
                    "error": f"Instance {instance_id} not found"
                }
                
        else:
            return {
                "success": False,
                "error": f"Unknown interaction type: {interaction_type}"
            }


# Example usage
if __name__ == "__main__":
    # Initialize the definitions manager
    definitions_manager = CapsuleDefinitionsManager()
    
    # Initialize the definitions service
    definitions_service = CapsuleDefinitionsService(definitions_manager)
    
    # Register an update callback
    def update_callback(update_type, update_data):
        print(f"Definition update: {update_type}")
        print(f"Update data: {update_data}")
    
    definitions_service.register_update_callback("example", update_callback)
    
    # Create a custom template
    custom_template = definitions_service.create_template(
        name="Custom Workflow Capsule",
        description="A custom template for specialized workflows",
        capsule_type="workflow",
        visual_config={
            "icon": "cogs",
            "color": "#e74c3c",
            "size": "large",
            "animation": "pulse",
            "badge": {
                "enabled": True,
                "position": "top-right"
            },
            "expanded_view": {
                "width": 500,
                "height": 400,
                "components": ["header", "status", "controls", "timeline", "details", "metrics"]
            }
        },
        behavior_config={
            "notification": {
                "level": "high",
                "sound": True,
                "vibration": True
            },
            "interaction": {
                "click": "expand",
                "double_click": "open_details",
                "drag": "move"
            },
            "lifecycle": {
                "auto_close": False,
                "persistence": "permanent"
            },
            "trust_visualization": {
                "enabled": True,
                "style": "glow"
            }
        },
        workflow_config={
            "status_mapping": {
                "pending": {"icon": "clock", "color": "#f39c12"},
                "running": {"icon": "play", "color": "#2ecc71"},
                "paused": {"icon": "pause", "color": "#f39c12"},
                "completed": {"icon": "check", "color": "#27ae60"},
                "failed": {"icon": "times", "color": "#e74c3c"}
            },
            "controls": ["start", "pause", "stop", "details", "debug"],
            "data_display": ["progress", "duration", "status", "metrics"],
            "execution_mode_indicators": {
                "enabled": True,
                "position": "top-left"
            }
        },
        metadata={
            "tags": ["custom", "specialized", "high-priority"],
            "version": "1.0"
        }
    )
    
    # Create an instance from the custom template
    if custom_template["success"]:
        template_id = custom_template["template"]["template_id"]
        
        instance = definitions_service.create_instance(
            template_id=template_id,
            name="Critical Process Workflow",
            description="Workflow for monitoring and managing critical processes"
        )
        
        if instance["success"]:
            instance_id = instance["instance"]["instance_id"]
            
            # Update the instance state
            definitions_service.update_instance_state(
                instance_id=instance_id,
                state_updates={
                    "status": "running",
                    "data": {
                        "progress": 25,
                        "start_time": time.time(),
                        "metrics": {
                            "cpu_usage": 45,
                            "memory_usage": 512,
                            "task_count": 8
                        }
                    }
                }
            )
            
            # List all instances
            response = definitions_service.handle_user_interaction(
                interaction_type="list_instances",
                interaction_data={}
            )
            
            print(f"All instances: {response['instances']}")
"""
