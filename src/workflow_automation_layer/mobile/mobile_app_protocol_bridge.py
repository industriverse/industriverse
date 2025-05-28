"""
Mobile App Protocol Bridge Module for Workflow Automation Layer

This module provides the bridge between mobile applications and the Workflow Automation Layer,
enabling workflow capsule export to mobile devices and seamless integration with mobile workflows.

Key features:
- Workflow capsule export to mobile devices
- Mobile-optimized protocol communication
- Offline workflow execution support
- Synchronization with central workflow engine
- Trust-aware execution on mobile devices
- Mobile-specific UI adaptations for Dynamic Agent Capsules
"""

import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union

from workflow_automation_layer.workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_automation_layer.workflow_engine.task_contract_manager import TaskContractManager
from workflow_automation_layer.workflow_engine.execution_mode_manager import ExecutionModeManager
from workflow_automation_layer.workflow_engine.mesh_topology_manager import MeshTopologyManager
from workflow_automation_layer.workflow_engine.capsule_debug_trace_manager import CapsuleDebugTraceManager
from workflow_automation_layer.agents.capsule_workflow_controller import CapsuleWorkflowController
from workflow_automation_layer.agents.capsule_memory_manager import CapsuleMemoryManager
from workflow_automation_layer.security.multi_tenant_isolation import MultiTenantIsolation
from workflow_automation_layer.security.trust_pathway_manager import TrustPathwayManager

logger = logging.getLogger(__name__)

class MobileAppProtocolBridge:
    """
    Bridge for exporting workflow capsules to mobile devices and managing mobile workflow execution.
    """
    
    def __init__(
        self,
        workflow_runtime: WorkflowRuntime,
        task_contract_manager: TaskContractManager,
        execution_mode_manager: ExecutionModeManager,
        mesh_topology_manager: MeshTopologyManager,
        capsule_debug_trace_manager: CapsuleDebugTraceManager,
        capsule_workflow_controller: CapsuleWorkflowController,
        capsule_memory_manager: CapsuleMemoryManager,
        multi_tenant_isolation: MultiTenantIsolation,
        trust_pathway_manager: TrustPathwayManager,
        config: Dict[str, Any] = None
    ):
        """
        Initialize the Mobile App Protocol Bridge.
        
        Args:
            workflow_runtime: The workflow runtime instance
            task_contract_manager: The task contract manager instance
            execution_mode_manager: The execution mode manager instance
            mesh_topology_manager: The mesh topology manager instance
            capsule_debug_trace_manager: The capsule debug trace manager instance
            capsule_workflow_controller: The capsule workflow controller instance
            capsule_memory_manager: The capsule memory manager instance
            multi_tenant_isolation: The multi-tenant isolation instance
            trust_pathway_manager: The trust pathway manager instance
            config: Configuration parameters for the bridge
        """
        self.workflow_runtime = workflow_runtime
        self.task_contract_manager = task_contract_manager
        self.execution_mode_manager = execution_mode_manager
        self.mesh_topology_manager = mesh_topology_manager
        self.capsule_debug_trace_manager = capsule_debug_trace_manager
        self.capsule_workflow_controller = capsule_workflow_controller
        self.capsule_memory_manager = capsule_memory_manager
        self.multi_tenant_isolation = multi_tenant_isolation
        self.trust_pathway_manager = trust_pathway_manager
        
        self.config = config or {}
        self.mobile_capsules = {}
        self.sync_status = {}
        
        logger.info("Mobile App Protocol Bridge initialized")
    
    def export_workflow_capsule(
        self,
        workflow_id: str,
        device_id: str,
        user_id: str,
        tenant_id: str,
        execution_mode_config: Dict[str, Any] = None,
        offline_capabilities: Dict[str, Any] = None,
        ui_customization: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Export a workflow capsule to a mobile device.
        
        Args:
            workflow_id: ID of the workflow to export
            device_id: ID of the target mobile device
            user_id: ID of the user
            tenant_id: ID of the tenant
            execution_mode_config: Configuration for execution modes on the mobile device
            offline_capabilities: Configuration for offline execution capabilities
            ui_customization: Customization parameters for the mobile UI
            
        Returns:
            Dictionary containing the exported capsule information
        """
        logger.info(f"Exporting workflow capsule {workflow_id} to device {device_id}")
        
        # Verify permissions
        self.multi_tenant_isolation.verify_access(user_id, tenant_id, workflow_id)
        
        # Get workflow manifest
        workflow_manifest = self.workflow_runtime.get_workflow_manifest(workflow_id)
        if not workflow_manifest:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Get task contracts
        task_contracts = self.task_contract_manager.get_task_contracts_for_workflow(workflow_id)
        
        # Configure execution modes for mobile
        mobile_execution_modes = self._configure_mobile_execution_modes(
            workflow_id, execution_mode_config or {}
        )
        
        # Configure offline capabilities
        offline_config = self._configure_offline_capabilities(
            workflow_id, offline_capabilities or {}
        )
        
        # Configure mobile UI
        mobile_ui = self._configure_mobile_ui(
            workflow_id, ui_customization or {}
        )
        
        # Create capsule memory snapshot
        memory_snapshot = self.capsule_memory_manager.create_memory_snapshot(workflow_id)
        
        # Generate capsule ID
        capsule_id = f"mobile-{workflow_id}-{device_id}-{uuid.uuid4()}"
        
        # Create mobile capsule
        mobile_capsule = {
            "capsule_id": capsule_id,
            "workflow_id": workflow_id,
            "device_id": device_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "workflow_manifest": workflow_manifest,
            "task_contracts": task_contracts,
            "execution_modes": mobile_execution_modes,
            "offline_capabilities": offline_config,
            "ui_configuration": mobile_ui,
            "memory_snapshot": memory_snapshot,
            "mesh_configuration": self.mesh_topology_manager.get_mobile_mesh_config(device_id),
            "trust_pathway": self.trust_pathway_manager.get_trust_pathway(workflow_id),
            "debug_trace_config": self.capsule_debug_trace_manager.get_mobile_trace_config(),
            "export_timestamp": self._get_current_timestamp(),
            "version": "1.0"
        }
        
        # Store mobile capsule
        self.mobile_capsules[capsule_id] = mobile_capsule
        
        # Initialize sync status
        self.sync_status[capsule_id] = {
            "last_sync": self._get_current_timestamp(),
            "sync_status": "initial_export",
            "pending_updates": []
        }
        
        logger.info(f"Workflow capsule {workflow_id} exported as {capsule_id}")
        
        # Return the mobile capsule (without sensitive information)
        return self._sanitize_capsule_for_export(mobile_capsule)
    
    def sync_workflow_capsule(
        self,
        capsule_id: str,
        device_id: str,
        user_id: str,
        local_execution_data: Dict[str, Any] = None,
        local_memory_updates: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Synchronize a workflow capsule between mobile device and central system.
        
        Args:
            capsule_id: ID of the capsule to synchronize
            device_id: ID of the mobile device
            user_id: ID of the user
            local_execution_data: Execution data from the mobile device
            local_memory_updates: Memory updates from the mobile device
            
        Returns:
            Dictionary containing synchronization results and updates
        """
        logger.info(f"Synchronizing workflow capsule {capsule_id} from device {device_id}")
        
        # Verify capsule exists
        if capsule_id not in self.mobile_capsules:
            raise ValueError(f"Capsule {capsule_id} not found")
        
        # Verify device and user
        capsule = self.mobile_capsules[capsule_id]
        if capsule["device_id"] != device_id:
            raise ValueError(f"Device ID mismatch for capsule {capsule_id}")
        if capsule["user_id"] != user_id:
            raise ValueError(f"User ID mismatch for capsule {capsule_id}")
        
        # Process local execution data
        if local_execution_data:
            self._process_local_execution_data(capsule_id, local_execution_data)
        
        # Process local memory updates
        if local_memory_updates:
            self._process_local_memory_updates(capsule_id, local_memory_updates)
        
        # Get central updates
        central_updates = self._get_central_updates(capsule_id)
        
        # Update sync status
        self.sync_status[capsule_id].update({
            "last_sync": self._get_current_timestamp(),
            "sync_status": "synchronized",
            "pending_updates": []
        })
        
        logger.info(f"Workflow capsule {capsule_id} synchronized")
        
        # Return updates for the mobile device
        return {
            "capsule_id": capsule_id,
            "sync_timestamp": self._get_current_timestamp(),
            "updates": central_updates
        }
    
    def deactivate_workflow_capsule(
        self,
        capsule_id: str,
        device_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Deactivate a workflow capsule on a mobile device.
        
        Args:
            capsule_id: ID of the capsule to deactivate
            device_id: ID of the mobile device
            user_id: ID of the user
            
        Returns:
            Dictionary containing deactivation status
        """
        logger.info(f"Deactivating workflow capsule {capsule_id} on device {device_id}")
        
        # Verify capsule exists
        if capsule_id not in self.mobile_capsules:
            raise ValueError(f"Capsule {capsule_id} not found")
        
        # Verify device and user
        capsule = self.mobile_capsules[capsule_id]
        if capsule["device_id"] != device_id:
            raise ValueError(f"Device ID mismatch for capsule {capsule_id}")
        if capsule["user_id"] != user_id:
            raise ValueError(f"User ID mismatch for capsule {capsule_id}")
        
        # Perform final sync
        final_sync = self._perform_final_sync(capsule_id)
        
        # Update status
        self.sync_status[capsule_id].update({
            "last_sync": self._get_current_timestamp(),
            "sync_status": "deactivated",
            "deactivation_timestamp": self._get_current_timestamp()
        })
        
        logger.info(f"Workflow capsule {capsule_id} deactivated")
        
        # Return deactivation status
        return {
            "capsule_id": capsule_id,
            "deactivation_timestamp": self._get_current_timestamp(),
            "final_sync_status": final_sync
        }
    
    def get_mobile_capsule_status(
        self,
        capsule_id: str,
        device_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get the status of a mobile workflow capsule.
        
        Args:
            capsule_id: ID of the capsule
            device_id: ID of the mobile device
            user_id: ID of the user
            
        Returns:
            Dictionary containing capsule status
        """
        logger.info(f"Getting status for workflow capsule {capsule_id}")
        
        # Verify capsule exists
        if capsule_id not in self.mobile_capsules:
            raise ValueError(f"Capsule {capsule_id} not found")
        
        # Verify device and user
        capsule = self.mobile_capsules[capsule_id]
        if capsule["device_id"] != device_id:
            raise ValueError(f"Device ID mismatch for capsule {capsule_id}")
        if capsule["user_id"] != user_id:
            raise ValueError(f"User ID mismatch for capsule {capsule_id}")
        
        # Get workflow status
        workflow_status = self.workflow_runtime.get_workflow_status(capsule["workflow_id"])
        
        # Get sync status
        sync_info = self.sync_status.get(capsule_id, {})
        
        # Get trust status
        trust_status = self.trust_pathway_manager.get_trust_status(capsule["workflow_id"])
        
        # Return status
        return {
            "capsule_id": capsule_id,
            "workflow_id": capsule["workflow_id"],
            "workflow_status": workflow_status,
            "sync_status": sync_info,
            "trust_status": trust_status,
            "timestamp": self._get_current_timestamp()
        }
    
    def _configure_mobile_execution_modes(
        self,
        workflow_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure execution modes for mobile device.
        
        Args:
            workflow_id: ID of the workflow
            config: Configuration parameters
            
        Returns:
            Dictionary containing mobile execution mode configuration
        """
        # Get base execution modes
        base_modes = self.execution_mode_manager.get_execution_modes(workflow_id)
        
        # Apply mobile-specific adjustments
        mobile_modes = {
            "autonomous": {
                "enabled": config.get("autonomous_enabled", base_modes["autonomous"]["enabled"]),
                "trust_threshold": config.get("autonomous_trust_threshold", base_modes["autonomous"]["trust_threshold"]),
                "offline_allowed": config.get("autonomous_offline_allowed", True),
                "requires_confirmation": config.get("autonomous_requires_confirmation", False)
            },
            "supervised": {
                "enabled": config.get("supervised_enabled", base_modes["supervised"]["enabled"]),
                "trust_threshold": config.get("supervised_trust_threshold", base_modes["supervised"]["trust_threshold"]),
                "offline_allowed": config.get("supervised_offline_allowed", True),
                "requires_confirmation": config.get("supervised_requires_confirmation", True)
            },
            "collaborative": {
                "enabled": config.get("collaborative_enabled", base_modes["collaborative"]["enabled"]),
                "trust_threshold": config.get("collaborative_trust_threshold", base_modes["collaborative"]["trust_threshold"]),
                "offline_allowed": config.get("collaborative_offline_allowed", False),
                "requires_confirmation": config.get("collaborative_requires_confirmation", True)
            },
            "assistive": {
                "enabled": config.get("assistive_enabled", base_modes["assistive"]["enabled"]),
                "trust_threshold": config.get("assistive_trust_threshold", base_modes["assistive"]["trust_threshold"]),
                "offline_allowed": config.get("assistive_offline_allowed", True),
                "requires_confirmation": config.get("assistive_requires_confirmation", True)
            },
            "manual": {
                "enabled": config.get("manual_enabled", base_modes["manual"]["enabled"]),
                "trust_threshold": config.get("manual_trust_threshold", base_modes["manual"]["trust_threshold"]),
                "offline_allowed": config.get("manual_offline_allowed", True),
                "requires_confirmation": config.get("manual_requires_confirmation", True)
            }
        }
        
        # Add mobile-specific settings
        mobile_modes["default_offline_mode"] = config.get("default_offline_mode", "assistive")
        mobile_modes["low_battery_mode"] = config.get("low_battery_mode", "manual")
        mobile_modes["poor_connectivity_mode"] = config.get("poor_connectivity_mode", "autonomous")
        
        return mobile_modes
    
    def _configure_offline_capabilities(
        self,
        workflow_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure offline capabilities for mobile device.
        
        Args:
            workflow_id: ID of the workflow
            config: Configuration parameters
            
        Returns:
            Dictionary containing offline capabilities configuration
        """
        # Default offline configuration
        default_config = {
            "enabled": True,
            "max_offline_duration_hours": 24,
            "required_data_sources": [],
            "cached_data_sources": [],
            "offline_execution_modes": ["autonomous", "assistive", "manual"],
            "sync_policy": {
                "auto_sync_on_connection": True,
                "sync_interval_minutes": 60,
                "priority_sync_items": ["completed_tasks", "critical_updates"]
            },
            "conflict_resolution": {
                "strategy": "mobile_wins",  # Options: mobile_wins, server_wins, timestamp_wins, merge
                "requires_user_resolution": False
            }
        }
        
        # Merge with provided configuration
        offline_config = {**default_config, **config}
        
        # Get workflow-specific data sources
        workflow_data_sources = self.workflow_runtime.get_workflow_data_sources(workflow_id)
        
        # Determine which data sources can be cached
        cacheable_sources = []
        for source in workflow_data_sources:
            if source.get("cacheable", False):
                cacheable_sources.append(source["id"])
        
        # Update cached data sources if not explicitly provided
        if not config.get("cached_data_sources"):
            offline_config["cached_data_sources"] = cacheable_sources
        
        return offline_config
    
    def _configure_mobile_ui(
        self,
        workflow_id: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure mobile UI for workflow capsule.
        
        Args:
            workflow_id: ID of the workflow
            config: Configuration parameters
            
        Returns:
            Dictionary containing mobile UI configuration
        """
        # Default UI configuration
        default_config = {
            "capsule_style": "dynamic_island",  # Options: dynamic_island, floating_bubble, status_bar, full_screen
            "theme": "system",  # Options: system, light, dark, custom
            "color_scheme": "default",
            "notification_level": "standard",  # Options: minimal, standard, verbose
            "interaction_mode": "touch",  # Options: touch, voice, gesture
            "accessibility": {
                "high_contrast": False,
                "large_text": False,
                "screen_reader_optimized": False
            },
            "compact_view": True,
            "show_trust_indicators": True,
            "show_execution_mode": True,
            "show_sync_status": True,
            "animation_level": "standard"  # Options: none, minimal, standard, rich
        }
        
        # Merge with provided configuration
        ui_config = {**default_config, **config}
        
        # Get workflow-specific UI elements
        workflow_ui = self.workflow_runtime.get_workflow_ui_elements(workflow_id)
        if workflow_ui:
            ui_config["workflow_specific_elements"] = workflow_ui
        
        return ui_config
    
    def _process_local_execution_data(
        self,
        capsule_id: str,
        execution_data: Dict[str, Any]
    ) -> None:
        """
        Process execution data from mobile device.
        
        Args:
            capsule_id: ID of the capsule
            execution_data: Execution data from mobile device
        """
        capsule = self.mobile_capsules[capsule_id]
        workflow_id = capsule["workflow_id"]
        
        # Process completed tasks
        if "completed_tasks" in execution_data:
            for task in execution_data["completed_tasks"]:
                self.workflow_runtime.register_mobile_task_completion(
                    workflow_id=workflow_id,
                    task_id=task["task_id"],
                    result=task["result"],
                    execution_context=task["execution_context"],
                    execution_mode=task["execution_mode"],
                    trust_score=task["trust_score"],
                    device_id=capsule["device_id"],
                    timestamp=task["timestamp"]
                )
        
        # Process execution metrics
        if "execution_metrics" in execution_data:
            self.workflow_runtime.register_mobile_execution_metrics(
                workflow_id=workflow_id,
                metrics=execution_data["execution_metrics"],
                device_id=capsule["device_id"]
            )
        
        # Process debug traces
        if "debug_traces" in execution_data:
            self.capsule_debug_trace_manager.register_mobile_traces(
                workflow_id=workflow_id,
                traces=execution_data["debug_traces"],
                device_id=capsule["device_id"]
            )
        
        # Process trust updates
        if "trust_updates" in execution_data:
            self.trust_pathway_manager.register_mobile_trust_updates(
                workflow_id=workflow_id,
                updates=execution_data["trust_updates"],
                device_id=capsule["device_id"]
            )
    
    def _process_local_memory_updates(
        self,
        capsule_id: str,
        memory_updates: Dict[str, Any]
    ) -> None:
        """
        Process memory updates from mobile device.
        
        Args:
            capsule_id: ID of the capsule
            memory_updates: Memory updates from mobile device
        """
        capsule = self.mobile_capsules[capsule_id]
        workflow_id = capsule["workflow_id"]
        
        # Apply memory updates
        self.capsule_memory_manager.apply_mobile_memory_updates(
            workflow_id=workflow_id,
            updates=memory_updates,
            device_id=capsule["device_id"]
        )
    
    def _get_central_updates(
        self,
        capsule_id: str
    ) -> Dict[str, Any]:
        """
        Get updates from central system for mobile device.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Dictionary containing updates for mobile device
        """
        capsule = self.mobile_capsules[capsule_id]
        workflow_id = capsule["workflow_id"]
        last_sync = self.sync_status[capsule_id]["last_sync"]
        
        # Get workflow updates
        workflow_updates = self.workflow_runtime.get_workflow_updates(
            workflow_id=workflow_id,
            since_timestamp=last_sync
        )
        
        # Get task updates
        task_updates = self.task_contract_manager.get_task_updates(
            workflow_id=workflow_id,
            since_timestamp=last_sync
        )
        
        # Get memory updates
        memory_updates = self.capsule_memory_manager.get_memory_updates(
            workflow_id=workflow_id,
            since_timestamp=last_sync
        )
        
        # Get execution mode updates
        execution_mode_updates = self.execution_mode_manager.get_execution_mode_updates(
            workflow_id=workflow_id,
            since_timestamp=last_sync
        )
        
        # Get mesh updates
        mesh_updates = self.mesh_topology_manager.get_mesh_updates(
            workflow_id=workflow_id,
            device_id=capsule["device_id"],
            since_timestamp=last_sync
        )
        
        # Get trust updates
        trust_updates = self.trust_pathway_manager.get_trust_updates(
            workflow_id=workflow_id,
            since_timestamp=last_sync
        )
        
        # Compile all updates
        return {
            "workflow_updates": workflow_updates,
            "task_updates": task_updates,
            "memory_updates": memory_updates,
            "execution_mode_updates": execution_mode_updates,
            "mesh_updates": mesh_updates,
            "trust_updates": trust_updates,
            "timestamp": self._get_current_timestamp()
        }
    
    def _perform_final_sync(
        self,
        capsule_id: str
    ) -> Dict[str, Any]:
        """
        Perform final synchronization before deactivation.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Dictionary containing final sync status
        """
        capsule = self.mobile_capsules[capsule_id]
        workflow_id = capsule["workflow_id"]
        
        # Notify workflow runtime of capsule deactivation
        self.workflow_runtime.deactivate_mobile_capsule(
            workflow_id=workflow_id,
            capsule_id=capsule_id,
            device_id=capsule["device_id"]
        )
        
        # Notify capsule memory manager
        self.capsule_memory_manager.finalize_mobile_memory(
            workflow_id=workflow_id,
            capsule_id=capsule_id,
            device_id=capsule["device_id"]
        )
        
        # Notify mesh topology manager
        self.mesh_topology_manager.remove_mobile_device(
            workflow_id=workflow_id,
            device_id=capsule["device_id"]
        )
        
        return {
            "status": "completed",
            "timestamp": self._get_current_timestamp()
        }
    
    def _sanitize_capsule_for_export(
        self,
        capsule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sanitize capsule data for export to mobile device.
        
        Args:
            capsule: Capsule data
            
        Returns:
            Sanitized capsule data
        """
        # Create a copy to avoid modifying the original
        export_capsule = capsule.copy()
        
        # Remove sensitive information
        if "internal_config" in export_capsule:
            del export_capsule["internal_config"]
        
        # Add export-specific information
        export_capsule["exported_for_device"] = capsule["device_id"]
        export_capsule["exported_for_user"] = capsule["user_id"]
        
        return export_capsule
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
