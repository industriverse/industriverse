"""
Context Rules Engine for Context Engine

This module provides rule-based context processing capabilities for the Industriverse UI/UX Layer.
It defines, manages, and executes rules for context interpretation, inference, and adaptation.

The Context Rules Engine:
1. Defines and manages context rules
2. Processes context data through rule evaluation
3. Infers higher-level context from lower-level data
4. Triggers actions based on context conditions
5. Adapts to changing context patterns

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import time
import re

# Local imports
from .context_awareness_engine import ContextType, ContextPriority

# Configure logging
logger = logging.getLogger(__name__)

class RuleType(Enum):
    """Enumeration of context rule types."""
    INFERENCE = "inference"       # Rules that infer new context from existing context
    TRIGGER = "trigger"           # Rules that trigger actions based on context conditions
    ADAPTATION = "adaptation"     # Rules that adapt the system based on context
    VALIDATION = "validation"     # Rules that validate context consistency
    TRANSFORMATION = "transformation"  # Rules that transform context data

class RulePriority(Enum):
    """Enumeration of rule priority levels."""
    CRITICAL = "critical"         # Highest priority, evaluated first
    HIGH = "high"                 # High priority
    MEDIUM = "medium"             # Medium priority
    LOW = "low"                   # Low priority
    BACKGROUND = "background"     # Lowest priority, evaluated last

class ContextRule:
    """
    Represents a single context rule.
    
    A context rule consists of conditions, actions, and metadata.
    When conditions are met, the rule's actions are executed.
    """
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        rule_type: str,
        priority: str,
        conditions: List[Dict],
        actions: List[Dict],
        enabled: bool = True
    ):
        """
        Initialize a context rule.
        
        Args:
            rule_id: Unique identifier for the rule
            name: Human-readable name for the rule
            description: Description of the rule's purpose
            rule_type: Type of rule (from RuleType enum)
            priority: Priority level (from RulePriority enum)
            conditions: List of condition dictionaries
            actions: List of action dictionaries
            enabled: Whether the rule is enabled
        """
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.rule_type = rule_type
        self.priority = priority
        self.conditions = conditions
        self.actions = actions
        self.enabled = enabled
        
        # Rule statistics
        self.evaluation_count = 0
        self.match_count = 0
        self.last_match_time = None
        self.last_evaluation_time = None
        self.average_evaluation_time = 0
        
        logger.debug(f"Initialized context rule: {name} ({rule_id})")
    
    def evaluate(self, context_data: Dict) -> bool:
        """
        Evaluate the rule against context data.
        
        Args:
            context_data: The context data to evaluate against
            
        Returns:
            Boolean indicating whether all conditions were met
        """
        if not self.enabled:
            return False
        
        start_time = time.time()
        self.evaluation_count += 1
        
        # Check each condition
        all_conditions_met = True
        for condition in self.conditions:
            if not self._evaluate_condition(condition, context_data):
                all_conditions_met = False
                break
        
        # Update statistics
        self.last_evaluation_time = time.time()
        evaluation_time = self.last_evaluation_time - start_time
        
        # Update average evaluation time
        if self.average_evaluation_time == 0:
            self.average_evaluation_time = evaluation_time
        else:
            self.average_evaluation_time = (self.average_evaluation_time * (self.evaluation_count - 1) + evaluation_time) / self.evaluation_count
        
        # If all conditions met, update match statistics
        if all_conditions_met:
            self.match_count += 1
            self.last_match_time = time.time()
        
        return all_conditions_met
    
    def _evaluate_condition(self, condition: Dict, context_data: Dict) -> bool:
        """
        Evaluate a single condition against context data.
        
        Args:
            condition: The condition to evaluate
            context_data: The context data to evaluate against
            
        Returns:
            Boolean indicating whether the condition was met
        """
        # Get condition parameters
        context_type = condition.get("context_type")
        path = condition.get("path")
        operator = condition.get("operator")
        value = condition.get("value")
        
        # Get context value
        context_value = self._get_context_value(context_data, context_type, path)
        
        # If context value not found, condition not met
        if context_value is None:
            return False
        
        # Evaluate based on operator
        if operator == "equals":
            return context_value == value
        elif operator == "not_equals":
            return context_value != value
        elif operator == "greater_than":
            return context_value > value
        elif operator == "less_than":
            return context_value < value
        elif operator == "contains":
            return value in context_value
        elif operator == "not_contains":
            return value not in context_value
        elif operator == "starts_with":
            return str(context_value).startswith(str(value))
        elif operator == "ends_with":
            return str(context_value).endswith(str(value))
        elif operator == "matches":
            return bool(re.match(value, str(context_value)))
        elif operator == "exists":
            return True  # We already checked that context_value is not None
        elif operator == "not_exists":
            return False  # We already checked that context_value is not None
        elif operator == "in":
            return context_value in value
        elif operator == "not_in":
            return context_value not in value
        elif operator == "is_true":
            return bool(context_value)
        elif operator == "is_false":
            return not bool(context_value)
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _get_context_value(self, context_data: Dict, context_type: str, path: str) -> Any:
        """
        Get a value from context data using dot notation path.
        
        Args:
            context_data: The context data to get value from
            context_type: The type of context to get value from
            path: Dot notation path to the value
            
        Returns:
            The context value or None if not found
        """
        # Get context type data
        if context_type not in context_data:
            return None
        
        type_data = context_data[context_type]
        
        # If no path, return entire type data
        if not path:
            return type_data
        
        # Split path into parts
        parts = path.split(".")
        
        # Navigate through path
        current = type_data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
    
    def execute(self, context_data: Dict) -> Dict:
        """
        Execute the rule's actions.
        
        Args:
            context_data: The context data to use for action execution
            
        Returns:
            Dictionary of action results
        """
        if not self.enabled:
            return {}
        
        results = {}
        
        # Execute each action
        for action in self.actions:
            action_type = action.get("type")
            action_params = action.get("parameters", {})
            
            result = self._execute_action(action_type, action_params, context_data)
            
            if result:
                results[action_type] = result
        
        return results
    
    def _execute_action(self, action_type: str, action_params: Dict, context_data: Dict) -> Any:
        """
        Execute a single action.
        
        Args:
            action_type: The type of action to execute
            action_params: Parameters for the action
            context_data: The context data to use for action execution
            
        Returns:
            Result of the action execution
        """
        # Infer context action
        if action_type == "infer_context":
            context_type = action_params.get("context_type")
            inferences = action_params.get("inferences", {})
            
            result = {}
            for key, value_template in inferences.items():
                # Replace template variables with context values
                value = self._process_template(value_template, context_data)
                result[key] = value
            
            return {
                "context_type": context_type,
                "inferred_data": result
            }
        
        # Set context value action
        elif action_type == "set_context_value":
            context_type = action_params.get("context_type")
            path = action_params.get("path")
            value_template = action_params.get("value")
            
            # Replace template variables with context values
            value = self._process_template(value_template, context_data)
            
            return {
                "context_type": context_type,
                "path": path,
                "value": value
            }
        
        # Trigger notification action
        elif action_type == "trigger_notification":
            notification_type = action_params.get("notification_type")
            message_template = action_params.get("message")
            priority = action_params.get("priority", "medium")
            
            # Replace template variables with context values
            message = self._process_template(message_template, context_data)
            
            return {
                "notification_type": notification_type,
                "message": message,
                "priority": priority
            }
        
        # Log action
        elif action_type == "log":
            level = action_params.get("level", "info")
            message_template = action_params.get("message")
            
            # Replace template variables with context values
            message = self._process_template(message_template, context_data)
            
            # Log message
            if level == "debug":
                logger.debug(message)
            elif level == "info":
                logger.info(message)
            elif level == "warning":
                logger.warning(message)
            elif level == "error":
                logger.error(message)
            
            return {
                "level": level,
                "message": message
            }
        
        # Unknown action type
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return None
    
    def _process_template(self, template: Any, context_data: Dict) -> Any:
        """
        Process a template by replacing variables with context values.
        
        Args:
            template: The template to process
            context_data: The context data to use for variable replacement
            
        Returns:
            Processed template
        """
        # If template is not a string, return as is
        if not isinstance(template, str):
            return template
        
        # Find all variables in template
        variables = re.findall(r'\${([^}]+)}', template)
        
        # Replace each variable with context value
        result = template
        for var in variables:
            # Split variable into context type and path
            parts = var.split(":", 1)
            
            if len(parts) == 2:
                context_type = parts[0]
                path = parts[1]
                
                # Get context value
                value = self._get_context_value(context_data, context_type, path)
                
                # Replace variable with value
                if value is not None:
                    result = result.replace(f"${{{var}}}", str(value))
        
        return result
    
    def to_dict(self) -> Dict:
        """
        Convert rule to dictionary representation.
        
        Returns:
            Dictionary representation of the rule
        """
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "priority": self.priority,
            "conditions": self.conditions,
            "actions": self.actions,
            "enabled": self.enabled,
            "statistics": {
                "evaluation_count": self.evaluation_count,
                "match_count": self.match_count,
                "last_match_time": self.last_match_time,
                "last_evaluation_time": self.last_evaluation_time,
                "average_evaluation_time": self.average_evaluation_time
            }
        }
    
    @classmethod
    def from_dict(cls, rule_dict: Dict) -> 'ContextRule':
        """
        Create rule from dictionary representation.
        
        Args:
            rule_dict: Dictionary representation of the rule
            
        Returns:
            ContextRule instance
        """
        rule = cls(
            rule_id=rule_dict["rule_id"],
            name=rule_dict["name"],
            description=rule_dict["description"],
            rule_type=rule_dict["rule_type"],
            priority=rule_dict["priority"],
            conditions=rule_dict["conditions"],
            actions=rule_dict["actions"],
            enabled=rule_dict.get("enabled", True)
        )
        
        # Set statistics if available
        if "statistics" in rule_dict:
            stats = rule_dict["statistics"]
            rule.evaluation_count = stats.get("evaluation_count", 0)
            rule.match_count = stats.get("match_count", 0)
            rule.last_match_time = stats.get("last_match_time")
            rule.last_evaluation_time = stats.get("last_evaluation_time")
            rule.average_evaluation_time = stats.get("average_evaluation_time", 0)
        
        return rule

class ContextRulesEngine:
    """
    Provides rule-based context processing capabilities.
    
    This class is responsible for defining, managing, and executing rules
    for context interpretation, inference, and adaptation within the
    Industriverse UI/UX Layer.
    """
    
    def __init__(self, rules_path: str = None):
        """
        Initialize the Context Rules Engine.
        
        Args:
            rules_path: Optional path to rules configuration file
        """
        # Rules storage
        self.rules = {}
        
        # Rule execution listeners
        self.rule_listeners = []
        
        # Load rules from configuration if provided
        if rules_path:
            self.load_rules(rules_path)
        else:
            # Initialize with default rules
            self._initialize_default_rules()
        
        logger.info("Context Rules Engine initialized")
    
    def _initialize_default_rules(self) -> None:
        """Initialize with default context rules."""
        # Device type inference rule
        self.add_rule(ContextRule(
            rule_id="device_type_inference",
            name="Device Type Inference",
            description="Infers device type based on screen size and input methods",
            rule_type=RuleType.INFERENCE.value,
            priority=RulePriority.HIGH.value,
            conditions=[
                {
                    "context_type": ContextType.DEVICE.value,
                    "path": "screen_size",
                    "operator": "exists",
                    "value": None
                }
            ],
            actions=[
                {
                    "type": "infer_context",
                    "parameters": {
                        "context_type": ContextType.DEVICE.value,
                        "inferences": {
                            "device_type": "${device:screen_size.width} < 768 ? 'mobile' : (${device:screen_size.width} < 1024 ? 'tablet' : 'desktop')"
                        }
                    }
                }
            ]
        ))
        
        # User focus level inference rule
        self.add_rule(ContextRule(
            rule_id="user_focus_inference",
            name="User Focus Level Inference",
            description="Infers user focus level based on activity and task priority",
            rule_type=RuleType.INFERENCE.value,
            priority=RulePriority.MEDIUM.value,
            conditions=[
                {
                    "context_type": ContextType.USER.value,
                    "path": "last_activity",
                    "operator": "exists",
                    "value": None
                },
                {
                    "context_type": ContextType.TASK.value,
                    "path": "task_priority",
                    "operator": "exists",
                    "value": None
                }
            ],
            actions=[
                {
                    "type": "infer_context",
                    "parameters": {
                        "context_type": ContextType.USER.value,
                        "inferences": {
                            "focus_level": "${task:task_priority} == 'high' ? 'focused' : (${task:interruption_level} == 'high' ? 'distracted' : 'normal')"
                        }
                    }
                }
            ]
        ))
        
        # Critical system status notification rule
        self.add_rule(ContextRule(
            rule_id="critical_system_notification",
            name="Critical System Status Notification",
            description="Triggers notification when system status is critical",
            rule_type=RuleType.TRIGGER.value,
            priority=RulePriority.CRITICAL.value,
            conditions=[
                {
                    "context_type": ContextType.SYSTEM.value,
                    "path": "system_status",
                    "operator": "equals",
                    "value": "critical"
                }
            ],
            actions=[
                {
                    "type": "trigger_notification",
                    "parameters": {
                        "notification_type": "alert",
                        "message": "System status is critical: ${system:system_status}",
                        "priority": "critical"
                    }
                },
                {
                    "type": "log",
                    "parameters": {
                        "level": "error",
                        "message": "Critical system status detected: ${system:system_status}"
                    }
                }
            ]
        ))
        
        # Mobile device adaptation rule
        self.add_rule(ContextRule(
            rule_id="mobile_device_adaptation",
            name="Mobile Device Adaptation",
            description="Adapts UI for mobile devices",
            rule_type=RuleType.ADAPTATION.value,
            priority=RulePriority.HIGH.value,
            conditions=[
                {
                    "context_type": ContextType.DEVICE.value,
                    "path": "device_type",
                    "operator": "equals",
                    "value": "mobile"
                }
            ],
            actions=[
                {
                    "type": "set_context_value",
                    "parameters": {
                        "context_type": ContextType.DEVICE.value,
                        "path": "ui_mode",
                        "value": "compact"
                    }
                },
                {
                    "type": "log",
                    "parameters": {
                        "level": "info",
                        "message": "Adapted UI for mobile device: ${device:device_id}"
                    }
                }
            ]
        ))
    
    def add_rule(self, rule: ContextRule) -> bool:
        """
        Add a rule to the engine.
        
        Args:
            rule: The rule to add
            
        Returns:
            Boolean indicating success
        """
        if rule.rule_id in self.rules:
            logger.warning(f"Rule with ID {rule.rule_id} already exists")
            return False
        
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rule: {rule.name} ({rule.rule_id})")
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule from the engine.
        
        Args:
            rule_id: The ID of the rule to remove
            
        Returns:
            Boolean indicating success
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed rule: {rule_id}")
            return True
        
        logger.warning(f"Rule with ID {rule_id} not found")
        return False
    
    def get_rule(self, rule_id: str) -> Optional[ContextRule]:
        """
        Get a rule by ID.
        
        Args:
            rule_id: The ID of the rule to get
            
        Returns:
            The rule or None if not found
        """
        return self.rules.get(rule_id)
    
    def get_rules(self, rule_type: str = None, enabled_only: bool = False) -> List[ContextRule]:
        """
        Get rules, optionally filtered by type and enabled status.
        
        Args:
            rule_type: Optional rule type to filter by
            enabled_only: Whether to return only enabled rules
            
        Returns:
            List of rules
        """
        result = []
        
        for rule in self.rules.values():
            # Filter by type if specified
            if rule_type and rule.rule_type != rule_type:
                continue
            
            # Filter by enabled status if specified
            if enabled_only and not rule.enabled:
                continue
            
            result.append(rule)
        
        return result
    
    def enable_rule(self, rule_id: str) -> bool:
        """
        Enable a rule.
        
        Args:
            rule_id: The ID of the rule to enable
            
        Returns:
            Boolean indicating success
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Enabled rule: {rule_id}")
            return True
        
        logger.warning(f"Rule with ID {rule_id} not found")
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """
        Disable a rule.
        
        Args:
            rule_id: The ID of the rule to disable
            
        Returns:
            Boolean indicating success
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Disabled rule: {rule_id}")
            return True
        
        logger.warning(f"Rule with ID {rule_id} not found")
        return False
    
    def evaluate_rules(self, context_data: Dict, rule_type: str = None) -> List[Dict]:
        """
        Evaluate rules against context data.
        
        Args:
            context_data: The context data to evaluate against
            rule_type: Optional rule type to filter by
            
        Returns:
            List of evaluation results
        """
        results = []
        
        # Get rules to evaluate
        rules_to_evaluate = self.get_rules(rule_type, enabled_only=True)
        
        # Sort rules by priority
        rules_to_evaluate.sort(key=lambda r: self._get_priority_value(r.priority))
        
        # Evaluate each rule
        for rule in rules_to_evaluate:
            # Evaluate rule
            match = rule.evaluate(context_data)
            
            # If rule matches, execute actions
            if match:
                action_results = rule.execute(context_data)
                
                # Add result
                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "match": True,
                    "actions": action_results
                })
                
                # Notify listeners
                self._notify_rule_execution(rule, action_results)
            else:
                # Add result
                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "match": False,
                    "actions": {}
                })
        
        return results
    
    def _get_priority_value(self, priority: str) -> int:
        """
        Get numeric value for priority level.
        
        Args:
            priority: Priority level string
            
        Returns:
            Numeric priority value (lower is higher priority)
        """
        if priority == RulePriority.CRITICAL.value:
            return 0
        elif priority == RulePriority.HIGH.value:
            return 1
        elif priority == RulePriority.MEDIUM.value:
            return 2
        elif priority == RulePriority.LOW.value:
            return 3
        elif priority == RulePriority.BACKGROUND.value:
            return 4
        else:
            return 5
    
    def register_rule_listener(self, listener_function: Callable) -> bool:
        """
        Register a function to be called when rules are executed.
        
        Args:
            listener_function: Function to call with rule execution results
            
        Returns:
            Boolean indicating success
        """
        if listener_function not in self.rule_listeners:
            self.rule_listeners.append(listener_function)
            logger.info(f"Registered rule listener: {listener_function.__name__}")
            return True
        return False
    
    def unregister_rule_listener(self, listener_function: Callable) -> bool:
        """
        Unregister a rule execution listener.
        
        Args:
            listener_function: Function to unregister
            
        Returns:
            Boolean indicating success
        """
        if listener_function in self.rule_listeners:
            self.rule_listeners.remove(listener_function)
            logger.info(f"Unregistered rule listener: {listener_function.__name__}")
            return True
        return False
    
    def _notify_rule_execution(self, rule: ContextRule, action_results: Dict) -> None:
        """
        Notify listeners of rule execution.
        
        Args:
            rule: The rule that was executed
            action_results: Results of the rule's actions
        """
        # Create rule execution event
        event = {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "rule_type": rule.rule_type,
            "priority": rule.priority,
            "timestamp": time.time(),
            "action_results": action_results
        }
        
        # Notify each listener
        for listener in self.rule_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying rule listener: {str(e)}")
    
    def save_rules(self, file_path: str) -> bool:
        """
        Save rules to a file.
        
        Args:
            file_path: Path to save rules to
            
        Returns:
            Boolean indicating success
        """
        try:
            # Convert rules to dictionaries
            rules_dict = {rule_id: rule.to_dict() for rule_id, rule in self.rules.items()}
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(rules_dict, f, indent=2)
            
            logger.info(f"Saved {len(rules_dict)} rules to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save rules: {str(e)}")
            return False
    
    def load_rules(self, file_path: str) -> bool:
        """
        Load rules from a file.
        
        Args:
            file_path: Path to load rules from
            
        Returns:
            Boolean indicating success
        """
        try:
            # Read from file
            with open(file_path, 'r') as f:
                rules_dict = json.load(f)
            
            # Clear existing rules
            self.rules = {}
            
            # Convert dictionaries to rules
            for rule_id, rule_dict in rules_dict.items():
                rule = ContextRule.from_dict(rule_dict)
                self.rules[rule_id] = rule
            
            logger.info(f"Loaded {len(self.rules)} rules from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load rules: {str(e)}")
            return False
    
    def get_rule_statistics(self, rule_id: str = None) -> Dict:
        """
        Get statistics for rules.
        
        Args:
            rule_id: Optional ID of the rule to get statistics for
            
        Returns:
            Dictionary of rule statistics
        """
        if rule_id:
            # Get statistics for specific rule
            rule = self.get_rule(rule_id)
            if not rule:
                return {}
            
            return {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "evaluation_count": rule.evaluation_count,
                "match_count": rule.match_count,
                "match_rate": rule.match_count / rule.evaluation_count if rule.evaluation_count > 0 else 0,
                "last_match_time": rule.last_match_time,
                "last_evaluation_time": rule.last_evaluation_time,
                "average_evaluation_time": rule.average_evaluation_time
            }
        else:
            # Get statistics for all rules
            stats = {
                "total_rules": len(self.rules),
                "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
                "rules_by_type": {},
                "rules_by_priority": {},
                "total_evaluations": 0,
                "total_matches": 0,
                "overall_match_rate": 0
            }
            
            # Count rules by type
            for rule in self.rules.values():
                # Count by type
                if rule.rule_type not in stats["rules_by_type"]:
                    stats["rules_by_type"][rule.rule_type] = 0
                stats["rules_by_type"][rule.rule_type] += 1
                
                # Count by priority
                if rule.priority not in stats["rules_by_priority"]:
                    stats["rules_by_priority"][rule.priority] = 0
                stats["rules_by_priority"][rule.priority] += 1
                
                # Add to totals
                stats["total_evaluations"] += rule.evaluation_count
                stats["total_matches"] += rule.match_count
            
            # Calculate overall match rate
            if stats["total_evaluations"] > 0:
                stats["overall_match_rate"] = stats["total_matches"] / stats["total_evaluations"]
            
            return stats
    
    def create_rule_from_template(
        self,
        template_id: str,
        parameters: Dict
    ) -> Optional[ContextRule]:
        """
        Create a rule from a template.
        
        Args:
            template_id: ID of the template to use
            parameters: Parameters to fill in the template
            
        Returns:
            Created rule or None if template not found
        """
        # In a real implementation, this would load templates from a configuration
        # For now, we'll define a few simple templates inline
        
        templates = {
            "device_type_detection": {
                "name": "Device Type Detection",
                "description": "Detects device type based on screen size",
                "rule_type": RuleType.INFERENCE.value,
                "priority": RulePriority.HIGH.value,
                "conditions_template": [
                    {
                        "context_type": ContextType.DEVICE.value,
                        "path": "screen_size.width",
                        "operator": "exists",
                        "value": None
                    }
                ],
                "actions_template": [
                    {
                        "type": "infer_context",
                        "parameters": {
                            "context_type": ContextType.DEVICE.value,
                            "inferences": {
                                "device_type": "${device:screen_size.width} < {mobile_threshold} ? 'mobile' : (${device:screen_size.width} < {tablet_threshold} ? 'tablet' : 'desktop')"
                            }
                        }
                    }
                ],
                "required_parameters": ["mobile_threshold", "tablet_threshold"]
            },
            "notification_trigger": {
                "name": "Notification Trigger",
                "description": "Triggers a notification based on a condition",
                "rule_type": RuleType.TRIGGER.value,
                "priority": RulePriority.MEDIUM.value,
                "conditions_template": [
                    {
                        "context_type": "{context_type}",
                        "path": "{context_path}",
                        "operator": "{operator}",
                        "value": "{value}"
                    }
                ],
                "actions_template": [
                    {
                        "type": "trigger_notification",
                        "parameters": {
                            "notification_type": "{notification_type}",
                            "message": "{message}",
                            "priority": "{priority}"
                        }
                    }
                ],
                "required_parameters": [
                    "context_type", "context_path", "operator", "value",
                    "notification_type", "message", "priority"
                ]
            }
        }
        
        # Check if template exists
        if template_id not in templates:
            logger.warning(f"Template with ID {template_id} not found")
            return None
        
        template = templates[template_id]
        
        # Check if all required parameters are provided
        for param in template["required_parameters"]:
            if param not in parameters:
                logger.warning(f"Missing required parameter: {param}")
                return None
        
        # Generate rule ID
        rule_id = f"{template_id}_{int(time.time())}"
        
        # Fill in name and description
        name = template["name"]
        description = template["description"]
        
        # Fill in conditions
        conditions = []
        for condition_template in template["conditions_template"]:
            condition = condition_template.copy()
            
            # Replace template parameters in condition
            for key, value in condition.items():
                if isinstance(value, str):
                    for param, param_value in parameters.items():
                        placeholder = "{" + param + "}"
                        if placeholder in value:
                            condition[key] = value.replace(placeholder, str(param_value))
            
            conditions.append(condition)
        
        # Fill in actions
        actions = []
        for action_template in template["actions_template"]:
            action = {
                "type": action_template["type"],
                "parameters": {}
            }
            
            # Replace template parameters in action parameters
            for key, value in action_template["parameters"].items():
                if isinstance(value, str):
                    for param, param_value in parameters.items():
                        placeholder = "{" + param + "}"
                        if placeholder in value:
                            value = value.replace(placeholder, str(param_value))
                    action["parameters"][key] = value
                elif isinstance(value, dict):
                    action["parameters"][key] = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            for param, param_value in parameters.items():
                                placeholder = "{" + param + "}"
                                if placeholder in sub_value:
                                    sub_value = sub_value.replace(placeholder, str(param_value))
                            action["parameters"][key][sub_key] = sub_value
                        else:
                            action["parameters"][key][sub_key] = sub_value
                else:
                    action["parameters"][key] = value
            
            actions.append(action)
        
        # Create rule
        rule = ContextRule(
            rule_id=rule_id,
            name=name,
            description=description,
            rule_type=template["rule_type"],
            priority=template["priority"],
            conditions=conditions,
            actions=actions,
            enabled=True
        )
        
        return rule
    
    def infer_context(self, context_data: Dict) -> Dict:
        """
        Infer context data using inference rules.
        
        Args:
            context_data: The current context data
            
        Returns:
            Dictionary of inferred context data
        """
        # Evaluate inference rules
        results = self.evaluate_rules(context_data, RuleType.INFERENCE.value)
        
        # Collect inferred data
        inferred_data = {}
        
        for result in results:
            if result["match"]:
                for action_type, action_result in result["actions"].items():
                    if action_type == "infer_context":
                        context_type = action_result["context_type"]
                        
                        if context_type not in inferred_data:
                            inferred_data[context_type] = {}
                        
                        inferred_data[context_type].update(action_result["inferred_data"])
        
        return inferred_data
    
    def adapt_to_context(self, context_data: Dict) -> Dict:
        """
        Adapt system based on context using adaptation rules.
        
        Args:
            context_data: The current context data
            
        Returns:
            Dictionary of adaptation results
        """
        # Evaluate adaptation rules
        results = self.evaluate_rules(context_data, RuleType.ADAPTATION.value)
        
        # Collect adaptation results
        adaptation_results = {}
        
        for result in results:
            if result["match"]:
                adaptation_results[result["rule_id"]] = result["actions"]
        
        return adaptation_results
    
    def validate_context(self, context_data: Dict) -> Dict:
        """
        Validate context data using validation rules.
        
        Args:
            context_data: The context data to validate
            
        Returns:
            Dictionary of validation results
        """
        # Evaluate validation rules
        results = self.evaluate_rules(context_data, RuleType.VALIDATION.value)
        
        # Collect validation results
        validation_results = {
            "valid": True,
            "issues": []
        }
        
        for result in results:
            if result["match"]:
                # If validation rule matched, it found an issue
                validation_results["valid"] = False
                
                # Add issue details
                for action_type, action_result in result["actions"].items():
                    if action_type == "log":
                        validation_results["issues"].append({
                            "rule_id": result["rule_id"],
                            "message": action_result["message"]
                        })
        
        return validation_results
"""
