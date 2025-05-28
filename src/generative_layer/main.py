"""
Main application entry point for Industriverse Generative Layer

This module serves as the main entry point for the Generative Layer with
protocol-native architecture and MCP/A2A integration.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core components
from protocols.agent_core import AgentCore
from protocols.protocol_translator import ProtocolTranslator
from protocols.well_known_endpoint import WellKnownEndpoint
from protocols.mesh_boot_lifecycle import MeshBootLifecycle
from protocols.mesh_agent_intent_graph import MeshAgentIntentGraph
from protocols.consensus_resolver_agent import ConsensusResolverAgent
from protocols.protocol_conflict_resolver_agent import ProtocolConflictResolverAgent

# Import distributed intelligence components
from distributed_intelligence.prompt_mutator_agent import PromptMutatorAgent
from distributed_intelligence.artifact_registry_agent import ArtifactRegistryAgent
from distributed_intelligence.agent_capsule_integration import AgentCapsuleIntegration
from distributed_intelligence.agent_lineage_manager import AgentLineageManager
from distributed_intelligence.collaborative_workflow_agent import CollaborativeWorkflowAgent
from distributed_intelligence.zk_artifact_traceability import ZKArtifactTraceability

# Import generative layer components
from template_system import TemplateSystem
from ui_component_system import UIComponentSystem
from variability_management import VariabilityManagement
from performance_optimization import PerformanceOptimization
from documentation_generation import DocumentationGeneration
from security_accessibility import SecurityAccessibility
from testing_framework import TestingFramework

class GenerativeLayer:
    """
    Main class for the Industriverse Generative Layer.
    Orchestrates all components and provides the main API.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Generative Layer.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.start_time = time.time()
        logger.info("Initializing Generative Layer...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize protocol components
        self.agent_core = AgentCore(self.config.get("agent_core", {}))
        self.protocol_translator = ProtocolTranslator(self.agent_core)
        self.well_known_endpoint = WellKnownEndpoint(self.agent_core)
        self.mesh_boot_lifecycle = MeshBootLifecycle(self.agent_core)
        self.mesh_agent_intent_graph = MeshAgentIntentGraph(self.agent_core)
        self.consensus_resolver = ConsensusResolverAgent(self.agent_core)
        self.protocol_conflict_resolver = ProtocolConflictResolverAgent(self.agent_core)
        
        # Initialize distributed intelligence components
        self.prompt_mutator = PromptMutatorAgent(self.agent_core)
        self.artifact_registry = ArtifactRegistryAgent(self.agent_core)
        self.agent_capsule_integration = AgentCapsuleIntegration(self.agent_core)
        self.agent_lineage_manager = AgentLineageManager(self.agent_core)
        self.collaborative_workflow = CollaborativeWorkflowAgent(self.agent_core)
        self.zk_artifact_traceability = ZKArtifactTraceability(self.agent_core)
        
        # Initialize generative layer components
        self.template_system = TemplateSystem(self.agent_core)
        self.ui_component_system = UIComponentSystem(self.agent_core)
        self.variability_management = VariabilityManagement(self.agent_core)
        self.performance_optimization = PerformanceOptimization(self.agent_core)
        self.documentation_generation = DocumentationGeneration(self.agent_core)
        self.security_accessibility = SecurityAccessibility(self.agent_core)
        self.testing_framework = TestingFramework(self.agent_core)
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "generative_layer_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Register with mesh
        self._register_with_mesh()
        
        # Register MCP/A2A event handlers
        self._register_event_handlers()
        
        # Load offer templates
        self._load_offer_templates()
        
        logger.info(f"Generative Layer initialized in {time.time() - self.start_time:.2f} seconds")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "agent_core": {
                "agent_id": "generative_layer_agent",
                "agent_name": "Industriverse Generative Layer",
                "agent_version": "1.0.0",
                "agent_description": "Generative Layer for Industriverse with protocol-native architecture",
                "mcp_enabled": True,
                "a2a_enabled": True,
                "mesh_coordination_role": "follower",
                "intelligence_role": "generator",
                "resilience_mode": "active"
            },
            "mesh": {
                "bootstrap_nodes": ["core_ai_layer_agent", "data_layer_agent"],
                "discovery_interval": 30,
                "heartbeat_interval": 10
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8082,
                "enable_http": True,
                "enable_grpc": True
            },
            "storage": {
                "path": "generative_layer_storage",
                "persistence_enabled": True,
                "backup_interval": 3600
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "logs/generative_layer.log",
                "rotation": "daily"
            },
            "security": {
                "authentication_required": True,
                "authorization_required": True,
                "encryption_enabled": True
            },
            "performance": {
                "cache_enabled": True,
                "cache_size": 1000,
                "cache_ttl": 3600,
                "parallel_generation": True,
                "max_parallel_jobs": 10
            },
            "edge_behavior_profile": {
                "compute_fallback_mode": "approximate",
                "stream_input_window": 128,
                "latency_threshold_ms": 250
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                
                # Merge user config with default config
                self._deep_merge(default_config, user_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_path}: {str(e)}")
        else:
            logger.info("Using default configuration")
        
        return default_config
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries.
        
        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _register_with_mesh(self) -> None:
        """Register with the mesh network."""
        logger.info("Registering with mesh network...")
        
        # Initialize mesh boot lifecycle
        self.mesh_boot_lifecycle.initialize()
        
        # Register agent with mesh
        bootstrap_nodes = self.config.get("mesh", {}).get("bootstrap_nodes", [])
        for node in bootstrap_nodes:
            self.mesh_boot_lifecycle.register_with_node(node)
        
        # Start mesh agent intent graph
        self.mesh_agent_intent_graph.initialize()
        
        logger.info("Registered with mesh network")
    
    def _register_event_handlers(self) -> None:
        """Register MCP/A2A event handlers."""
        logger.info("Registering event handlers...")
        
        # Register MCP event handlers
        self.agent_core.register_mcp_event_handler(
            "generative_layer/template/generate",
            self._handle_template_generate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/ui_component/generate",
            self._handle_ui_component_generate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/documentation/generate",
            self._handle_documentation_generate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/workflow/collaborate",
            self._handle_workflow_collaborate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/prompt/mutate",
            self._handle_prompt_mutate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/artifact/register",
            self._handle_artifact_register
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/artifact/validate",
            self._handle_artifact_validate
        )
        
        self.agent_core.register_mcp_event_handler(
            "generative_layer/artifact/test",
            self._handle_artifact_test
        )
        
        # Register A2A event handlers
        self.agent_core.register_a2a_event_handler(
            "generative_layer/offer/generate",
            self._handle_offer_generate
        )
        
        logger.info("Event handlers registered")
    
    def _load_offer_templates(self) -> None:
        """Load offer templates for low ticket offers."""
        logger.info("Loading offer templates...")
        
        # Define template categories based on the 500 low ticket offers
        template_categories = [
            "industrial_dashboard",
            "predictive_maintenance",
            "quality_control",
            "inventory_management",
            "energy_optimization",
            "safety_compliance",
            "production_scheduling",
            "equipment_monitoring",
            "supply_chain_visibility",
            "workforce_management"
        ]
        
        # Load templates for each category
        for category in template_categories:
            template_path = os.path.join("offer_templates", f"{category}_template.json")
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r') as f:
                        template = json.load(f)
                    
                    self.template_system.register_template(
                        template_id=f"{category}_template",
                        name=template.get("name", f"{category.replace('_', ' ').title()} Template"),
                        template_content=template.get("content", {}),
                        metadata=template.get("metadata", {})
                    )
                    
                    logger.info(f"Loaded template: {category}_template")
                except Exception as e:
                    logger.error(f"Error loading template {category}_template: {str(e)}")
            else:
                # Create default template if not exists
                default_template = self._create_default_template(category)
                
                self.template_system.register_template(
                    template_id=f"{category}_template",
                    name=f"{category.replace('_', ' ').title()} Template",
                    template_content=default_template,
                    metadata={"auto_generated": True}
                )
                
                logger.info(f"Created default template: {category}_template")
        
        logger.info(f"Loaded {len(template_categories)} offer templates")
    
    def _create_default_template(self, category: str) -> Dict[str, Any]:
        """
        Create a default template for a category.
        
        Args:
            category: Template category
            
        Returns:
            Default template
        """
        # Create default template based on category
        if category == "industrial_dashboard":
            return {
                "type": "dashboard",
                "components": [
                    {"type": "header", "title": "{{title}}", "subtitle": "{{subtitle}}"},
                    {"type": "kpi_panel", "kpis": "{{kpis}}"},
                    {"type": "chart_grid", "charts": "{{charts}}"},
                    {"type": "alert_panel", "alerts": "{{alerts}}"},
                    {"type": "control_panel", "controls": "{{controls}}"}
                ],
                "layout": {
                    "type": "responsive_grid",
                    "breakpoints": ["sm", "md", "lg", "xl"]
                },
                "theme": {
                    "primary_color": "{{primary_color|#1976d2}}",
                    "secondary_color": "{{secondary_color|#424242}}",
                    "background_color": "{{background_color|#f5f5f5}}",
                    "text_color": "{{text_color|#212121}}",
                    "font_family": "{{font_family|Roboto, sans-serif}}"
                }
            }
        elif category == "predictive_maintenance":
            return {
                "type": "application",
                "modules": [
                    {"type": "equipment_registry", "equipment": "{{equipment}}"},
                    {"type": "sensor_data_viewer", "sensors": "{{sensors}}"},
                    {"type": "maintenance_scheduler", "schedule": "{{schedule}}"},
                    {"type": "prediction_engine", "models": "{{models}}"},
                    {"type": "alert_system", "alerts": "{{alerts}}"}
                ],
                "workflows": [
                    {"type": "data_collection", "steps": "{{data_collection_steps}}"},
                    {"type": "analysis", "steps": "{{analysis_steps}}"},
                    {"type": "prediction", "steps": "{{prediction_steps}}"},
                    {"type": "notification", "steps": "{{notification_steps}}"},
                    {"type": "maintenance", "steps": "{{maintenance_steps}}"}
                ]
            }
        elif category == "quality_control":
            return {
                "type": "application",
                "modules": [
                    {"type": "inspection_station", "stations": "{{stations}}"},
                    {"type": "defect_classifier", "defects": "{{defects}}"},
                    {"type": "quality_metrics", "metrics": "{{metrics}}"},
                    {"type": "reporting_system", "reports": "{{reports}}"}
                ],
                "workflows": [
                    {"type": "inspection", "steps": "{{inspection_steps}}"},
                    {"type": "classification", "steps": "{{classification_steps}}"},
                    {"type": "remediation", "steps": "{{remediation_steps}}"},
                    {"type": "reporting", "steps": "{{reporting_steps}}"}
                ]
            }
        else:
            # Generic template for other categories
            return {
                "type": "application",
                "name": "{{name}}",
                "description": "{{description}}",
                "modules": "{{modules}}",
                "components": "{{components}}",
                "workflows": "{{workflows}}",
                "integrations": "{{integrations}}",
                "theme": {
                    "primary_color": "{{primary_color|#1976d2}}",
                    "secondary_color": "{{secondary_color|#424242}}",
                    "background_color": "{{background_color|#f5f5f5}}",
                    "text_color": "{{text_color|#212121}}",
                    "font_family": "{{font_family|Roboto, sans-serif}}"
                }
            }
    
    def _handle_template_generate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle template generation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling template generation event: {event.get('template_id', 'unknown')}")
        
        try:
            # Extract event data
            template_id = event.get("template_id")
            template_params = event.get("params", {})
            options = event.get("options", {})
            
            # Generate from template
            result = self.template_system.generate_from_template(
                template_id=template_id,
                params=template_params,
                options=options
            )
            
            # Apply variability management if enabled
            if options.get("apply_variability", False):
                result = self.variability_management.apply_variability(
                    content=result,
                    variability_config=options.get("variability_config", {})
                )
            
            # Apply performance optimization if enabled
            if options.get("optimize_performance", False):
                result = self.performance_optimization.optimize(
                    content=result,
                    optimization_config=options.get("optimization_config", {})
                )
            
            # Generate ZK proof hash for traceability
            zk_proof_hash = self.zk_artifact_traceability.generate_proof(
                content=result,
                metadata={
                    "template_id": template_id,
                    "params": template_params,
                    "options": options
                }
            )
            
            # Return result
            return {
                "status": "success",
                "template_id": template_id,
                "result": result,
                "zk_proof_hash": zk_proof_hash
            }
            
        except Exception as e:
            logger.error(f"Error handling template generation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_ui_component_generate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle UI component generation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling UI component generation event: {event.get('component_type', 'unknown')}")
        
        try:
            # Extract event data
            component_type = event.get("component_type")
            component_params = event.get("params", {})
            options = event.get("options", {})
            
            # Generate UI component
            result = self.ui_component_system.generate_component(
                component_type=component_type,
                params=component_params,
                options=options
            )
            
            # Apply variability management if enabled
            if options.get("apply_variability", False):
                result = self.variability_management.apply_variability(
                    content=result,
                    variability_config=options.get("variability_config", {})
                )
            
            # Apply performance optimization if enabled
            if options.get("optimize_performance", False):
                result = self.performance_optimization.optimize(
                    content=result,
                    optimization_config=options.get("optimization_config", {})
                )
            
            # Generate ZK proof hash for traceability
            zk_proof_hash = self.zk_artifact_traceability.generate_proof(
                content=result,
                metadata={
                    "component_type": component_type,
                    "params": component_params,
                    "options": options
                }
            )
            
            # Return result
            return {
                "status": "success",
                "component_type": component_type,
                "result": result,
                "zk_proof_hash": zk_proof_hash
            }
            
        except Exception as e:
            logger.error(f"Error handling UI component generation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_documentation_generate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle documentation generation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling documentation generation event: {event.get('doc_type', 'unknown')}")
        
        try:
            # Extract event data
            doc_type = event.get("doc_type")
            content = event.get("content", {})
            options = event.get("options", {})
            
            # Generate documentation
            result = self.documentation_generation.generate_documentation(
                doc_type=doc_type,
                content=content,
                options=options
            )
            
            # Generate ZK proof hash for traceability
            zk_proof_hash = self.zk_artifact_traceability.generate_proof(
                content=result,
                metadata={
                    "doc_type": doc_type,
                    "options": options
                }
            )
            
            # Return result
            return {
                "status": "success",
                "doc_type": doc_type,
                "result": result,
                "zk_proof_hash": zk_proof_hash
            }
            
        except Exception as e:
            logger.error(f"Error handling documentation generation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_workflow_collaborate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow collaboration event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling workflow collaboration event: {event.get('workflow_id', 'unknown')}")
        
        try:
            # Extract event data
            workflow_id = event.get("workflow_id")
            workflow_type = event.get("workflow_type")
            participants = event.get("participants", [])
            workflow_data = event.get("workflow_data", {})
            options = event.get("options", {})
            
            # Execute collaborative workflow
            result = self.collaborative_workflow.execute_workflow(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                participants=participants,
                workflow_data=workflow_data,
                options=options
            )
            
            # Generate ZK proof hash for traceability
            zk_proof_hash = self.zk_artifact_traceability.generate_proof(
                content=result,
                metadata={
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "participants": participants,
                    "options": options
                }
            )
            
            # Return result
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "result": result,
                "zk_proof_hash": zk_proof_hash
            }
            
        except Exception as e:
            logger.error(f"Error handling workflow collaboration event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_prompt_mutate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle prompt mutation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling prompt mutation event: {event.get('prompt_id', 'unknown')}")
        
        try:
            # Extract event data
            prompt_id = event.get("prompt_id")
            original_prompt = event.get("prompt")
            context = event.get("context", {})
            feedback = event.get("feedback", {})
            options = event.get("options", {})
            
            # Mutate prompt
            result = self.prompt_mutator.mutate_prompt(
                prompt_id=prompt_id,
                original_prompt=original_prompt,
                context=context,
                feedback=feedback,
                options=options
            )
            
            # Return result
            return {
                "status": "success",
                "prompt_id": prompt_id,
                "original_prompt": original_prompt,
                "mutated_prompt": result["prompt"],
                "mutation_steps": result["steps"],
                "confidence": result["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Error handling prompt mutation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_artifact_register(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle artifact registration event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling artifact registration event: {event.get('artifact_id', 'unknown')}")
        
        try:
            # Extract event data
            artifact_id = event.get("artifact_id")
            artifact_type = event.get("artifact_type")
            content = event.get("content")
            metadata = event.get("metadata", {})
            options = event.get("options", {})
            
            # Register artifact
            result = self.artifact_registry.register_artifact(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content=content,
                metadata=metadata,
                options=options
            )
            
            # Return result
            return {
                "status": "success",
                "artifact_id": artifact_id,
                "registry_id": result["registry_id"],
                "timestamp": result["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error handling artifact registration event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_artifact_validate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle artifact validation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling artifact validation event: {event.get('artifact_id', 'unknown')}")
        
        try:
            # Extract event data
            artifact_id = event.get("artifact_id")
            artifact_type = event.get("artifact_type")
            content = event.get("content")
            security_profile_id = event.get("security_profile_id")
            accessibility_profile_id = event.get("accessibility_profile_id")
            options = event.get("options", {})
            
            # Validate artifact
            result = self.security_accessibility.validate_artifact(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content=content,
                security_profile_id=security_profile_id,
                accessibility_profile_id=accessibility_profile_id
            )
            
            # Return result
            return {
                "status": "success",
                "artifact_id": artifact_id,
                "validation_id": result["id"],
                "overall_status": result["overall_status"],
                "security": result.get("security"),
                "accessibility": result.get("accessibility")
            }
            
        except Exception as e:
            logger.error(f"Error handling artifact validation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_artifact_test(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle artifact testing event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling artifact testing event: {event.get('artifact_id', 'unknown')}")
        
        try:
            # Extract event data
            artifact_id = event.get("artifact_id")
            artifact_type = event.get("artifact_type")
            content = event.get("content")
            test_suite_id = event.get("test_suite_id")
            options = event.get("options", {})
            
            # Test artifact
            result = self.testing_framework.run_tests(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content=content,
                test_suite_id=test_suite_id
            )
            
            # Return result
            return {
                "status": "success",
                "artifact_id": artifact_id,
                "test_run_id": result["id"],
                "test_status": result["status"],
                "passed": result["passed"],
                "failed": result["failed"],
                "warnings": result["warnings"],
                "total": result["total"]
            }
            
        except Exception as e:
            logger.error(f"Error handling artifact testing event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _handle_offer_generate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle offer generation event.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        logger.info(f"Handling offer generation event: {event.get('offer_id', 'unknown')}")
        
        try:
            # Extract event data
            offer_id = event.get("offer_id")
            offer_type = event.get("offer_type")
            offer_params = event.get("params", {})
            options = event.get("options", {})
            
            # Determine template ID based on offer type
            template_id = f"{offer_type}_template"
            if not self.template_system.has_template(template_id):
                template_id = "generic_template"
            
            # Generate from template
            template_result = self.template_system.generate_from_template(
                template_id=template_id,
                params=offer_params,
                options=options
            )
            
            # Generate UI components if needed
            ui_components = {}
            if options.get("generate_ui", False):
                ui_component_types = options.get("ui_component_types", ["dashboard", "form", "report"])
                for component_type in ui_component_types:
                    ui_components[component_type] = self.ui_component_system.generate_component(
                        component_type=component_type,
                        params=offer_params,
                        options=options
                    )
            
            # Generate documentation if needed
            documentation = None
            if options.get("generate_documentation", False):
                documentation = self.documentation_generation.generate_documentation(
                    doc_type="offer",
                    content={
                        "offer_id": offer_id,
                        "offer_type": offer_type,
                        "offer_params": offer_params,
                        "template_result": template_result,
                        "ui_components": ui_components
                    },
                    options=options
                )
            
            # Apply variability management if enabled
            if options.get("apply_variability", False):
                template_result = self.variability_management.apply_variability(
                    content=template_result,
                    variability_config=options.get("variability_config", {})
                )
            
            # Apply performance optimization if enabled
            if options.get("optimize_performance", False):
                template_result = self.performance_optimization.optimize(
                    content=template_result,
                    optimization_config=options.get("optimization_config", {})
                )
            
            # Generate ZK proof hash for traceability
            zk_proof_hash = self.zk_artifact_traceability.generate_proof(
                content={
                    "template_result": template_result,
                    "ui_components": ui_components,
                    "documentation": documentation
                },
                metadata={
                    "offer_id": offer_id,
                    "offer_type": offer_type,
                    "params": offer_params,
                    "options": options
                }
            )
            
            # Register artifact
            artifact_id = f"offer_{offer_id}"
            self.artifact_registry.register_artifact(
                artifact_id=artifact_id,
                artifact_type="offer",
                content={
                    "template_result": template_result,
                    "ui_components": ui_components,
                    "documentation": documentation
                },
                metadata={
                    "offer_id": offer_id,
                    "offer_type": offer_type,
                    "params": offer_params,
                    "options": options,
                    "zk_proof_hash": zk_proof_hash
                }
            )
            
            # Return result
            return {
                "status": "success",
                "offer_id": offer_id,
                "artifact_id": artifact_id,
                "template_result": template_result,
                "ui_components": ui_components if ui_components else None,
                "documentation": documentation,
                "zk_proof_hash": zk_proof_hash
            }
            
        except Exception as e:
            logger.error(f"Error handling offer generation event: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def start(self) -> None:
        """Start the Generative Layer."""
        logger.info("Starting Generative Layer...")
        
        # Start mesh boot lifecycle
        self.mesh_boot_lifecycle.start()
        
        # Start well-known endpoint
        self.well_known_endpoint.start()
        
        # Emit MCP event for layer startup
        self.agent_core.send_mcp_event(
            "generative_layer/lifecycle/started",
            {
                "agent_id": self.config["agent_core"]["agent_id"],
                "timestamp": time.time(),
                "version": self.config["agent_core"]["agent_version"]
            }
        )
        
        logger.info("Generative Layer started")
    
    def stop(self) -> None:
        """Stop the Generative Layer."""
        logger.info("Stopping Generative Layer...")
        
        # Emit MCP event for layer shutdown
        self.agent_core.send_mcp_event(
            "generative_layer/lifecycle/stopping",
            {
                "agent_id": self.config["agent_core"]["agent_id"],
                "timestamp": time.time()
            }
        )
        
        # Stop well-known endpoint
        self.well_known_endpoint.stop()
        
        # Stop mesh boot lifecycle
        self.mesh_boot_lifecycle.stop()
        
        logger.info("Generative Layer stopped")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Industriverse Generative Layer")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    try:
        # Initialize and start Generative Layer
        generative_layer = GenerativeLayer(config_path=args.config)
        generative_layer.start()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        if 'generative_layer' in locals():
            generative_layer.stop()
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        if 'generative_layer' in locals():
            generative_layer.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
