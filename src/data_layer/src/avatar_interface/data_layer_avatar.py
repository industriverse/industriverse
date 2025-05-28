"""
Data Layer Avatar Interface for Industriverse

This module implements the protocol-native Avatar Interface for the Industriverse Data Layer,
providing a unified interface for agent-based interaction with the data layer components
through MCP/A2A protocols and AG-UI feedback loop.

Key Features:
- Protocol-native avatar interface with MCP/A2A integration
- AG-UI feedback loop for user interaction
- Digital Twin synchronization
- Intent-based data operations
- Mesh intent graph integration
- Universal Skin / Dynamic Agent Capsules integration

Classes:
- DataLayerAvatar: Main avatar interface implementation
- IntentProcessor: Processes user and agent intents
- DataOperationExecutor: Executes data operations
- FeedbackLoopManager: Manages AG-UI feedback loop
- DigitalTwinSynchronizer: Synchronizes with digital twins
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from ..protocols.agent_core import AgentCore
from ..protocols.protocol_translator import ProtocolTranslator
from ..protocols.mesh_boot_lifecycle import MeshBootLifecycle
from ..protocols.mesh_agent_intent_graph import MeshAgentIntentGraph
from ..protocols.well_known_endpoint import WellKnownEndpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLayerAvatar(AgentCore):
    """
    Protocol-native Avatar Interface for Industriverse Data Layer.
    
    Implements a unified interface for agent-based interaction with data layer
    components through MCP/A2A protocols and AG-UI feedback loop.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Data Layer Avatar with protocol-native capabilities.
        
        Args:
            config_path: Path to avatar configuration file
        """
        super().__init__(
            agent_id="data_layer_avatar",
            agent_type="interface",
            intelligence_type="interactive",
            description="Protocol-native avatar interface for industrial data layer"
        )
        
        self.config = self._load_config(config_path)
        
        # Initialize avatar components
        self.intent_processor = IntentProcessor(self)
        self.operation_executor = DataOperationExecutor(self)
        self.feedback_loop = FeedbackLoopManager(self)
        self.twin_synchronizer = DigitalTwinSynchronizer(self)
        
        # Register with mesh boot lifecycle
        self.mesh_boot = MeshBootLifecycle()
        self.mesh_boot.register_agent(self)
        
        # Initialize protocol translator for MCP/A2A communication
        self.protocol_translator = ProtocolTranslator()
        
        # Initialize mesh agent intent graph
        self.mesh_intent = MeshAgentIntentGraph()
        
        # Initialize well-known endpoint
        self.well_known = WellKnownEndpoint(self)
        
        # Register avatar capabilities
        self._register_capabilities()
        
        logger.info("Data Layer Avatar initialized with protocol-native capabilities")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load avatar configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "avatar": {
                "name": "Data Layer Avatar",
                "description": "Industrial data layer interface avatar",
                "icon": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgMThjLTQuNDEgMC04LTMuNTktOC04czMuNTktOCA4LTggOCAzLjU5IDggOC0zLjU5IDgtOCA4eiIvPjxwYXRoIGQ9Ik0xMiA2Yy0zLjMxIDAtNiAyLjY5LTYgNnMyLjY5IDYgNiA2IDYtMi42OSA2LTYtMi42OS02LTYtNnptMCAxMGMtMi4yMSAwLTQtMS43OS00LTRzMS43OS00IDQtNCA0IDEuNzkgNCA0LTEuNzkgNC00IDR6Ii8+PC9zdmc+",
                "appearance": {
                    "primary_color": "#2196F3",
                    "secondary_color": "#1565C0",
                    "accent_color": "#FFC107"
                }
            },
            "interface": {
                "capsule_enabled": True,
                "desktop_companion": True,
                "mobile_bar": True,
                "ar_hud": True,
                "web_popover": True
            },
            "capabilities": {
                "data_exploration": True,
                "data_visualization": True,
                "data_processing": True,
                "anomaly_detection": True,
                "predictive_analytics": True
            },
            "feedback_loop": {
                "user_feedback_enabled": True,
                "ambient_awareness": True,
                "notification_level": "medium"
            },
            "digital_twin": {
                "sync_enabled": True,
                "sync_interval": 60,  # seconds
                "state_streaming": True
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                logger.error(f"Error loading avatar config: {e}")
                return default_config
        return default_config
    
    def _register_capabilities(self):
        """Register avatar capabilities with the mesh intent graph."""
        capabilities = {
            "data_exploration": {
                "description": "Explore industrial datasets",
                "parameters": {
                    "dataset_id": "string",
                    "filters": "object",
                    "limit": "integer"
                },
                "returns": "object"
            },
            "data_visualization": {
                "description": "Visualize industrial data",
                "parameters": {
                    "dataset_id": "string",
                    "visualization_type": "string",
                    "parameters": "object"
                },
                "returns": "object"
            },
            "data_processing": {
                "description": "Process industrial data",
                "parameters": {
                    "dataset_id": "string",
                    "operation": "string",
                    "parameters": "object"
                },
                "returns": "object"
            },
            "anomaly_detection": {
                "description": "Detect anomalies in industrial data",
                "parameters": {
                    "dataset_id": "string",
                    "sensitivity": "number",
                    "parameters": "object"
                },
                "returns": "object"
            },
            "predictive_analytics": {
                "description": "Perform predictive analytics on industrial data",
                "parameters": {
                    "dataset_id": "string",
                    "target_variable": "string",
                    "horizon": "integer",
                    "parameters": "object"
                },
                "returns": "object"
            }
        }
        
        for capability_id, capability_spec in capabilities.items():
            if self.config["capabilities"].get(capability_id, False):
                self.mesh_intent.register_capability(
                    agent_id=self.agent_id,
                    capability_id=capability_id,
                    capability_spec=capability_spec
                )
    
    def process_user_intent(self, intent: Dict) -> Dict:
        """
        Process user intent.
        
        Args:
            intent: User intent payload
            
        Returns:
            Processing result
        """
        logger.info(f"Processing user intent: {intent.get('intent_type')}")
        
        # Add intent to mesh intent graph
        self.mesh_intent.add_intent(
            source_id="user",
            target_id=self.agent_id,
            intent_type=intent.get("intent_type"),
            intent_payload=intent
        )
        
        # Process intent
        result = self.intent_processor.process(intent)
        
        # Update feedback loop
        self.feedback_loop.update_feedback(
            intent=intent,
            result=result
        )
        
        # Synchronize with digital twin if needed
        if intent.get("sync_twin", False):
            self.twin_synchronizer.sync_state(result)
        
        return result
    
    def execute_data_operation(self, operation: Dict) -> Dict:
        """
        Execute a data operation.
        
        Args:
            operation: Data operation payload
            
        Returns:
            Operation result
        """
        logger.info(f"Executing data operation: {operation.get('operation_type')}")
        
        # Add operation to mesh intent graph
        self.mesh_intent.add_intent(
            source_id=operation.get("source_id", self.agent_id),
            target_id="data_layer",
            intent_type=operation.get("operation_type"),
            intent_payload=operation
        )
        
        # Execute operation
        result = self.operation_executor.execute(operation)
        
        # Update feedback loop
        self.feedback_loop.update_feedback(
            intent=operation,
            result=result
        )
        
        return result
    
    def get_avatar_state(self) -> Dict:
        """
        Get current avatar state.
        
        Returns:
            Avatar state
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "intelligence_type": self.intelligence_type,
            "avatar": self.config["avatar"],
            "capabilities": self.config["capabilities"],
            "feedback": self.feedback_loop.get_current_feedback(),
            "twin_sync_status": self.twin_synchronizer.get_sync_status(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_capsule_state(self) -> Dict:
        """
        Get current capsule state for Universal Skin integration.
        
        Returns:
            Capsule state
        """
        return {
            "capsule_id": f"data_layer_avatar_{self.agent_id}",
            "name": self.config["avatar"]["name"],
            "description": self.config["avatar"]["description"],
            "icon": self.config["avatar"]["icon"],
            "appearance": self.config["avatar"]["appearance"],
            "state": {
                "status": "active",
                "context": self.mesh_intent.get_recent_intents(limit=5),
                "feedback": self.feedback_loop.get_current_feedback(),
                "notifications": self.feedback_loop.get_pending_notifications()
            },
            "actions": [
                {
                    "id": "explore",
                    "name": "Explore Data",
                    "description": "Explore industrial datasets"
                },
                {
                    "id": "visualize",
                    "name": "Visualize Data",
                    "description": "Create visualizations from industrial data"
                },
                {
                    "id": "process",
                    "name": "Process Data",
                    "description": "Run processing operations on industrial data"
                },
                {
                    "id": "detect",
                    "name": "Detect Anomalies",
                    "description": "Detect anomalies in industrial data"
                },
                {
                    "id": "predict",
                    "name": "Predict Trends",
                    "description": "Perform predictive analytics on industrial data"
                }
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def handle_mcp_request(self, request: Dict) -> Dict:
        """
        Handle an incoming MCP protocol request.
        
        Args:
            request: MCP request payload
            
        Returns:
            MCP response payload
        """
        request_type = request.get("type")
        
        if request_type == "avatar.intent":
            return self.process_user_intent(request.get("intent", {}))
        elif request_type == "avatar.operation":
            return self.execute_data_operation(request.get("operation", {}))
        elif request_type == "avatar.state":
            return self.get_avatar_state()
        elif request_type == "avatar.capsule":
            return self.get_capsule_state()
        else:
            return {
                "error": "Unsupported avatar request type",
                "requestType": request_type
            }
    
    def handle_a2a_request(self, request: Dict) -> Dict:
        """
        Handle an incoming A2A protocol request.
        
        Args:
            request: A2A request payload
            
        Returns:
            A2A response payload
        """
        # Translate A2A request to internal format
        internal_request = self.protocol_translator.translate_request(request, "A2A")
        
        # Process using internal methods
        result = self.handle_mcp_request(internal_request)
        
        # Translate response back to A2A format
        return self.protocol_translator.translate_response(result, "A2A")


class IntentProcessor:
    """
    Processes user and agent intents.
    """
    
    def __init__(self, avatar):
        """
        Initialize the Intent Processor.
        
        Args:
            avatar: Parent avatar
        """
        self.avatar = avatar
    
    def process(self, intent: Dict) -> Dict:
        """
        Process an intent.
        
        Args:
            intent: Intent payload
            
        Returns:
            Processing result
        """
        intent_type = intent.get("intent_type")
        
        if intent_type == "explore":
            return self._process_explore_intent(intent)
        elif intent_type == "visualize":
            return self._process_visualize_intent(intent)
        elif intent_type == "process":
            return self._process_process_intent(intent)
        elif intent_type == "detect":
            return self._process_detect_intent(intent)
        elif intent_type == "predict":
            return self._process_predict_intent(intent)
        else:
            return {
                "status": "error",
                "error": f"Unsupported intent type: {intent_type}"
            }
    
    def _process_explore_intent(self, intent: Dict) -> Dict:
        """
        Process explore intent.
        
        Args:
            intent: Explore intent payload
            
        Returns:
            Exploration result
        """
        dataset_id = intent.get("dataset_id")
        filters = intent.get("filters", {})
        limit = intent.get("limit", 100)
        
        # Convert to data operation
        operation = {
            "operation_type": "explore",
            "dataset_id": dataset_id,
            "filters": filters,
            "limit": limit,
            "source_id": intent.get("source_id", "user")
        }
        
        # Execute operation
        return self.avatar.execute_data_operation(operation)
    
    def _process_visualize_intent(self, intent: Dict) -> Dict:
        """
        Process visualize intent.
        
        Args:
            intent: Visualize intent payload
            
        Returns:
            Visualization result
        """
        dataset_id = intent.get("dataset_id")
        visualization_type = intent.get("visualization_type")
        parameters = intent.get("parameters", {})
        
        # Convert to data operation
        operation = {
            "operation_type": "visualize",
            "dataset_id": dataset_id,
            "visualization_type": visualization_type,
            "parameters": parameters,
            "source_id": intent.get("source_id", "user")
        }
        
        # Execute operation
        return self.avatar.execute_data_operation(operation)
    
    def _process_process_intent(self, intent: Dict) -> Dict:
        """
        Process process intent.
        
        Args:
            intent: Process intent payload
            
        Returns:
            Processing result
        """
        dataset_id = intent.get("dataset_id")
        operation = intent.get("operation")
        parameters = intent.get("parameters", {})
        
        # Convert to data operation
        operation = {
            "operation_type": "process",
            "dataset_id": dataset_id,
            "process_operation": operation,
            "parameters": parameters,
            "source_id": intent.get("source_id", "user")
        }
        
        # Execute operation
        return self.avatar.execute_data_operation(operation)
    
    def _process_detect_intent(self, intent: Dict) -> Dict:
        """
        Process detect intent.
        
        Args:
            intent: Detect intent payload
            
        Returns:
            Detection result
        """
        dataset_id = intent.get("dataset_id")
        sensitivity = intent.get("sensitivity", 0.8)
        parameters = intent.get("parameters", {})
        
        # Convert to data operation
        operation = {
            "operation_type": "detect",
            "dataset_id": dataset_id,
            "sensitivity": sensitivity,
            "parameters": parameters,
            "source_id": intent.get("source_id", "user")
        }
        
        # Execute operation
        return self.avatar.execute_data_operation(operation)
    
    def _process_predict_intent(self, intent: Dict) -> Dict:
        """
        Process predict intent.
        
        Args:
            intent: Predict intent payload
            
        Returns:
            Prediction result
        """
        dataset_id = intent.get("dataset_id")
        target_variable = intent.get("target_variable")
        horizon = intent.get("horizon", 24)
        parameters = intent.get("parameters", {})
        
        # Convert to data operation
        operation = {
            "operation_type": "predict",
            "dataset_id": dataset_id,
            "target_variable": target_variable,
            "horizon": horizon,
            "parameters": parameters,
            "source_id": intent.get("source_id", "user")
        }
        
        # Execute operation
        return self.avatar.execute_data_operation(operation)


class DataOperationExecutor:
    """
    Executes data operations.
    """
    
    def __init__(self, avatar):
        """
        Initialize the Data Operation Executor.
        
        Args:
            avatar: Parent avatar
        """
        self.avatar = avatar
    
    def execute(self, operation: Dict) -> Dict:
        """
        Execute a data operation.
        
        Args:
            operation: Data operation payload
            
        Returns:
            Operation result
        """
        operation_type = operation.get("operation_type")
        
        if operation_type == "explore":
            return self._execute_explore(operation)
        elif operation_type == "visualize":
            return self._execute_visualize(operation)
        elif operation_type == "process":
            return self._execute_process(operation)
        elif operation_type == "detect":
            return self._execute_detect(operation)
        elif operation_type == "predict":
            return self._execute_predict(operation)
        else:
            return {
                "status": "error",
                "error": f"Unsupported operation type: {operation_type}"
            }
    
    def _execute_explore(self, operation: Dict) -> Dict:
        """
        Execute explore operation.
        
        Args:
            operation: Explore operation payload
            
        Returns:
            Exploration result
        """
        # In a real implementation, this would interact with the data layer
        # components to explore the dataset
        
        # For demonstration, we'll return a simulated result
        return {
            "status": "success",
            "operation_id": str(uuid.uuid4()),
            "operation_type": "explore",
            "dataset_id": operation.get("dataset_id"),
            "result": {
                "total_records": 1000,
                "filtered_records": 100,
                "sample_data": [
                    {"id": 1, "value": 10.5, "timestamp": "2025-05-01T12:00:00Z"},
                    {"id": 2, "value": 11.2, "timestamp": "2025-05-01T12:01:00Z"},
                    {"id": 3, "value": 10.8, "timestamp": "2025-05-01T12:02:00Z"}
                ],
                "schema": {
                    "id": "integer",
                    "value": "float",
                    "timestamp": "datetime"
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_visualize(self, operation: Dict) -> Dict:
        """
        Execute visualize operation.
        
        Args:
            operation: Visualize operation payload
            
        Returns:
            Visualization result
        """
        # In a real implementation, this would interact with the data layer
        # components to visualize the dataset
        
        # For demonstration, we'll return a simulated result
        return {
            "status": "success",
            "operation_id": str(uuid.uuid4()),
            "operation_type": "visualize",
            "dataset_id": operation.get("dataset_id"),
            "visualization_type": operation.get("visualization_type"),
            "result": {
                "visualization_url": f"https://example.com/visualizations/{uuid.uuid4()}.png",
                "visualization_data": {
                    "type": operation.get("visualization_type"),
                    "data": {
                        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                        "datasets": [
                            {
                                "label": "Dataset 1",
                                "data": [10, 20, 15, 25, 30]
                            }
                        ]
                    }
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_process(self, operation: Dict) -> Dict:
        """
        Execute process operation.
        
        Args:
            operation: Process operation payload
            
        Returns:
            Processing result
        """
        # In a real implementation, this would interact with the data layer
        # components to process the dataset
        
        # For demonstration, we'll return a simulated result
        return {
            "status": "success",
            "operation_id": str(uuid.uuid4()),
            "operation_type": "process",
            "dataset_id": operation.get("dataset_id"),
            "process_operation": operation.get("process_operation"),
            "result": {
                "records_processed": 1000,
                "processing_time": 2.5,  # seconds
                "output_dataset_id": f"processed_{operation.get('dataset_id')}_{uuid.uuid4().hex[:8]}"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_detect(self, operation: Dict) -> Dict:
        """
        Execute detect operation.
        
        Args:
            operation: Detect operation payload
            
        Returns:
            Detection result
        """
        # In a real implementation, this would interact with the data layer
        # components to detect anomalies in the dataset
        
        # For demonstration, we'll return a simulated result
        return {
            "status": "success",
            "operation_id": str(uuid.uuid4()),
            "operation_type": "detect",
            "dataset_id": operation.get("dataset_id"),
            "sensitivity": operation.get("sensitivity"),
            "result": {
                "anomalies_detected": 5,
                "records_analyzed": 1000,
                "anomaly_details": [
                    {
                        "id": 42,
                        "value": 35.7,
                        "timestamp": "2025-05-01T14:23:00Z",
                        "score": 0.92,
                        "reason": "Value spike"
                    },
                    {
                        "id": 157,
                        "value": 2.1,
                        "timestamp": "2025-05-01T18:45:00Z",
                        "score": 0.87,
                        "reason": "Value drop"
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _execute_predict(self, operation: Dict) -> Dict:
        """
        Execute predict operation.
        
        Args:
            operation: Predict operation payload
            
        Returns:
            Prediction result
        """
        # In a real implementation, this would interact with the data layer
        # components to perform predictive analytics on the dataset
        
        # For demonstration, we'll return a simulated result
        return {
            "status": "success",
            "operation_id": str(uuid.uuid4()),
            "operation_type": "predict",
            "dataset_id": operation.get("dataset_id"),
            "target_variable": operation.get("target_variable"),
            "horizon": operation.get("horizon"),
            "result": {
                "predictions": [
                    {"timestamp": "2025-05-02T00:00:00Z", "value": 12.3, "confidence": 0.85},
                    {"timestamp": "2025-05-02T01:00:00Z", "value": 12.5, "confidence": 0.82},
                    {"timestamp": "2025-05-02T02:00:00Z", "value": 12.8, "confidence": 0.79}
                ],
                "model_metrics": {
                    "mape": 5.2,
                    "rmse": 0.8,
                    "r2": 0.92
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }


class FeedbackLoopManager:
    """
    Manages AG-UI feedback loop.
    """
    
    def __init__(self, avatar):
        """
        Initialize the Feedback Loop Manager.
        
        Args:
            avatar: Parent avatar
        """
        self.avatar = avatar
        self.feedback_history = []
        self.pending_notifications = []
    
    def update_feedback(self, intent: Dict, result: Dict) -> None:
        """
        Update feedback based on intent and result.
        
        Args:
            intent: Intent or operation payload
            result: Processing result
        """
        feedback_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "intent": intent,
            "result": result,
            "feedback_id": str(uuid.uuid4())
        }
        
        # Add to history
        self.feedback_history.append(feedback_entry)
        
        # Limit history size
        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]
        
        # Generate notifications if needed
        self._generate_notifications(feedback_entry)
    
    def _generate_notifications(self, feedback_entry: Dict) -> None:
        """
        Generate notifications based on feedback.
        
        Args:
            feedback_entry: Feedback entry
        """
        result = feedback_entry.get("result", {})
        
        # Check for errors
        if result.get("status") == "error":
            self.pending_notifications.append({
                "notification_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "level": "error",
                "title": "Operation Error",
                "message": result.get("error", "Unknown error occurred"),
                "source": feedback_entry.get("intent", {}).get("intent_type", "unknown"),
                "feedback_id": feedback_entry.get("feedback_id")
            })
        
        # Check for anomalies
        if result.get("operation_type") == "detect" and result.get("result", {}).get("anomalies_detected", 0) > 0:
            self.pending_notifications.append({
                "notification_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "level": "warning",
                "title": "Anomalies Detected",
                "message": f"Detected {result.get('result', {}).get('anomalies_detected', 0)} anomalies in dataset {result.get('dataset_id')}",
                "source": "anomaly_detection",
                "feedback_id": feedback_entry.get("feedback_id")
            })
    
    def get_current_feedback(self) -> Dict:
        """
        Get current feedback state.
        
        Returns:
            Current feedback state
        """
        return {
            "last_updated": datetime.utcnow().isoformat(),
            "recent_feedback": self.feedback_history[-5:] if self.feedback_history else [],
            "notification_count": len(self.pending_notifications)
        }
    
    def get_pending_notifications(self) -> List[Dict]:
        """
        Get pending notifications.
        
        Returns:
            List of pending notifications
        """
        notifications = self.pending_notifications.copy()
        self.pending_notifications = []
        return notifications


class DigitalTwinSynchronizer:
    """
    Synchronizes with digital twins.
    """
    
    def __init__(self, avatar):
        """
        Initialize the Digital Twin Synchronizer.
        
        Args:
            avatar: Parent avatar
        """
        self.avatar = avatar
        self.last_sync = None
        self.sync_status = "idle"
    
    def sync_state(self, state: Dict) -> Dict:
        """
        Synchronize state with digital twin.
        
        Args:
            state: State to synchronize
            
        Returns:
            Synchronization result
        """
        logger.info("Synchronizing state with digital twin")
        
        try:
            # In a real implementation, this would synchronize the state
            # with a digital twin
            
            # For demonstration, we'll simulate synchronization
            self.last_sync = datetime.utcnow()
            self.sync_status = "synced"
            
            return {
                "status": "success",
                "sync_id": str(uuid.uuid4()),
                "timestamp": self.last_sync.isoformat(),
                "message": "State synchronized with digital twin"
            }
        except Exception as e:
            logger.error(f"Digital twin synchronization failed: {e}")
            self.sync_status = "error"
            
            return {
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def get_sync_status(self) -> Dict:
        """
        Get synchronization status.
        
        Returns:
            Synchronization status
        """
        return {
            "status": self.sync_status,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_interval": self.avatar.config["digital_twin"]["sync_interval"],
            "sync_enabled": self.avatar.config["digital_twin"]["sync_enabled"],
            "state_streaming": self.avatar.config["digital_twin"]["state_streaming"]
        }
