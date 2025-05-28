"""
Disaster Recovery Framework for the Deployment Operations Layer

This module provides comprehensive disaster recovery capabilities for the
Deployment Operations Layer, implementing self-healing infrastructure with
automated backup, recovery, and resilient deployment strategies to ensure
business continuity.

The disaster recovery framework supports automated backup, point-in-time recovery,
failover mechanisms, and self-healing capabilities for deployment infrastructure.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from ..analytics.analytics_manager import AnalyticsManager
from ..agent.agent_utils import AgentUtils
from ..security.security_framework_manager import SecurityFrameworkManager
from ..orchestration.deployment_orchestration_service import get_deployment_orchestration_service

# Configure logging
logger = logging.getLogger(__name__)

class DisasterRecoveryManager:
    """Disaster recovery manager for self-healing infrastructure"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the disaster recovery manager
        
        Args:
            config: Configuration for the disaster recovery manager
        """
        self.config = config
        self.analytics_manager = AnalyticsManager()
        self.agent_utils = AgentUtils()
        self.security_manager = SecurityFrameworkManager()
        self.orchestration_service = get_deployment_orchestration_service()
        self.backup_schedule = config.get("backup_schedule", {})
        self.recovery_points = {}
        self.active_recoveries = {}
        self.health_checks = {}
        self.status = "initialized"
        
        logger.info("Initialized disaster recovery manager")
    
    async def initialize(self):
        """Initialize the disaster recovery manager"""
        try:
            # Load existing recovery points
            await self._load_recovery_points()
            
            # Initialize health checks
            await self._initialize_health_checks()
            
            # Start backup scheduler
            await self._start_backup_scheduler()
            
            self.status = "ready"
            logger.info("Disaster recovery manager initialized successfully")
            
            return {
                "status": "success",
                "recovery_points": len(self.recovery_points),
                "health_checks": len(self.health_checks)
            }
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize disaster recovery manager: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _load_recovery_points(self):
        """Load existing recovery points"""
        try:
            # In a real implementation, this would load recovery points from storage
            # For demonstration, we'll create sample recovery points
            self.recovery_points = {
                "rp-20250101-000000": {
                    "id": "rp-20250101-000000",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "type": "scheduled",
                    "status": "available",
                    "layers": ["data", "core_ai", "generative", "application", "protocol", "workflow", "ui_ux", "security"],
                    "size_mb": 1024,
                    "metadata": {
                        "created_by": "system"
                    }
                },
                "rp-20250201-000000": {
                    "id": "rp-20250201-000000",
                    "timestamp": "2025-02-01T00:00:00Z",
                    "type": "scheduled",
                    "status": "available",
                    "layers": ["data", "core_ai", "generative", "application", "protocol", "workflow", "ui_ux", "security"],
                    "size_mb": 1024,
                    "metadata": {
                        "created_by": "system"
                    }
                },
                "rp-20250301-000000": {
                    "id": "rp-20250301-000000",
                    "timestamp": "2025-03-01T00:00:00Z",
                    "type": "scheduled",
                    "status": "available",
                    "layers": ["data", "core_ai", "generative", "application", "protocol", "workflow", "ui_ux", "security"],
                    "size_mb": 1024,
                    "metadata": {
                        "created_by": "system"
                    }
                }
            }
            
            logger.info(f"Loaded {len(self.recovery_points)} recovery points")
        except Exception as e:
            logger.error(f"Failed to load recovery points: {str(e)}")
            raise
    
    async def _initialize_health_checks(self):
        """Initialize health checks"""
        try:
            # In a real implementation, this would set up health checks for various components
            # For demonstration, we'll create sample health checks
            self.health_checks = {
                "deployment_engine": {
                    "id": "deployment_engine",
                    "name": "Deployment Engine",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "mission_planner": {
                    "id": "mission_planner",
                    "name": "Mission Planner",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "mission_executor": {
                    "id": "mission_executor",
                    "name": "Mission Executor",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "template_manager": {
                    "id": "template_manager",
                    "name": "Template Manager",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "manifest_manager": {
                    "id": "manifest_manager",
                    "name": "Manifest Manager",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "protocol_bridge": {
                    "id": "protocol_bridge",
                    "name": "Protocol Bridge",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "kubernetes_integration": {
                    "id": "kubernetes_integration",
                    "name": "Kubernetes Integration",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                },
                "edge_device_manager": {
                    "id": "edge_device_manager",
                    "name": "Edge Device Manager",
                    "status": "healthy",
                    "last_checked": self.agent_utils.get_current_timestamp(),
                    "check_interval_seconds": 60,
                    "recovery_action": "restart_service",
                    "auto_recover": True
                }
            }
            
            # Start health check tasks
            for component_id, health_check in self.health_checks.items():
                asyncio.create_task(self._run_health_check_loop(component_id))
            
            logger.info(f"Initialized {len(self.health_checks)} health checks")
        except Exception as e:
            logger.error(f"Failed to initialize health checks: {str(e)}")
            raise
    
    async def _run_health_check_loop(self, component_id: str):
        """
        Run health check loop for a component
        
        Args:
            component_id: ID of the component to check
        """
        if component_id not in self.health_checks:
            logger.error(f"Health check for component {component_id} not found")
            return
        
        health_check = self.health_checks[component_id]
        check_interval = health_check.get("check_interval_seconds", 60)
        
        logger.info(f"Starting health check loop for {component_id} with interval {check_interval}s")
        
        while True:
            try:
                # Run health check
                await self._check_component_health(component_id)
                
                # Wait for next check
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                logger.info(f"Health check loop for {component_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health check loop for {component_id}: {str(e)}")
                await asyncio.sleep(check_interval)
    
    async def _check_component_health(self, component_id: str):
        """
        Check health of a component
        
        Args:
            component_id: ID of the component to check
        """
        if component_id not in self.health_checks:
            logger.error(f"Health check for component {component_id} not found")
            return
        
        health_check = self.health_checks[component_id]
        
        try:
            # In a real implementation, this would check the actual health of the component
            # For demonstration, we'll simulate health checks with random failures
            
            # Update last checked timestamp
            health_check["last_checked"] = self.agent_utils.get_current_timestamp()
            
            # Simulate health check (90% healthy, 10% unhealthy)
            import random
            is_healthy = random.random() < 0.9
            
            if is_healthy:
                # Component is healthy
                if health_check["status"] != "healthy":
                    logger.info(f"Component {component_id} is now healthy")
                
                health_check["status"] = "healthy"
                health_check["last_healthy"] = self.agent_utils.get_current_timestamp()
                
                # Record health check in analytics
                self.analytics_manager.record_component_health_check(
                    component_id=component_id,
                    status="healthy",
                    timestamp=health_check["last_checked"]
                )
            else:
                # Component is unhealthy
                logger.warning(f"Component {component_id} is unhealthy")
                
                health_check["status"] = "unhealthy"
                health_check["last_unhealthy"] = self.agent_utils.get_current_timestamp()
                
                # Record health check in analytics
                self.analytics_manager.record_component_health_check(
                    component_id=component_id,
                    status="unhealthy",
                    timestamp=health_check["last_checked"]
                )
                
                # Attempt recovery if auto-recover is enabled
                if health_check.get("auto_recover", False):
                    await self._recover_component(component_id)
        except Exception as e:
            logger.error(f"Error checking health of component {component_id}: {str(e)}")
            
            # Update health check status
            health_check["status"] = "error"
            health_check["last_error"] = self.agent_utils.get_current_timestamp()
            health_check["last_error_message"] = str(e)
            
            # Record health check in analytics
            self.analytics_manager.record_component_health_check(
                component_id=component_id,
                status="error",
                timestamp=health_check["last_checked"],
                error=str(e)
            )
    
    async def _recover_component(self, component_id: str):
        """
        Recover a component
        
        Args:
            component_id: ID of the component to recover
        """
        if component_id not in self.health_checks:
            logger.error(f"Health check for component {component_id} not found")
            return
        
        health_check = self.health_checks[component_id]
        recovery_action = health_check.get("recovery_action")
        
        logger.info(f"Recovering component {component_id} with action {recovery_action}")
        
        try:
            # Record recovery start
            recovery_id = f"recovery-{component_id}-{self.agent_utils.generate_id()}"
            
            self.active_recoveries[recovery_id] = {
                "id": recovery_id,
                "component_id": component_id,
                "recovery_action": recovery_action,
                "status": "in_progress",
                "started_at": self.agent_utils.get_current_timestamp()
            }
            
            # Perform recovery action
            if recovery_action == "restart_service":
                # In a real implementation, this would restart the service
                # For demonstration, we'll simulate a restart
                logger.info(f"Restarting service for component {component_id}")
                
                # Simulate restart time
                await asyncio.sleep(2)
                
                # Update health check status
                health_check["status"] = "recovering"
                
                # Record recovery in analytics
                self.analytics_manager.record_component_recovery(
                    component_id=component_id,
                    recovery_id=recovery_id,
                    recovery_action=recovery_action,
                    timestamp=self.agent_utils.get_current_timestamp()
                )
                
                # Update recovery status
                self.active_recoveries[recovery_id]["status"] = "completed"
                self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
                
                logger.info(f"Recovery {recovery_id} for component {component_id} completed")
            elif recovery_action == "failover":
                # In a real implementation, this would perform a failover
                # For demonstration, we'll simulate a failover
                logger.info(f"Performing failover for component {component_id}")
                
                # Simulate failover time
                await asyncio.sleep(5)
                
                # Update health check status
                health_check["status"] = "recovering"
                
                # Record recovery in analytics
                self.analytics_manager.record_component_recovery(
                    component_id=component_id,
                    recovery_id=recovery_id,
                    recovery_action=recovery_action,
                    timestamp=self.agent_utils.get_current_timestamp()
                )
                
                # Update recovery status
                self.active_recoveries[recovery_id]["status"] = "completed"
                self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
                
                logger.info(f"Recovery {recovery_id} for component {component_id} completed")
            elif recovery_action == "restore_from_backup":
                # In a real implementation, this would restore from backup
                # For demonstration, we'll simulate a restore
                logger.info(f"Restoring component {component_id} from backup")
                
                # Find latest recovery point
                latest_recovery_point = self._find_latest_recovery_point()
                
                if latest_recovery_point:
                    # Simulate restore time
                    await asyncio.sleep(10)
                    
                    # Update health check status
                    health_check["status"] = "recovering"
                    
                    # Record recovery in analytics
                    self.analytics_manager.record_component_recovery(
                        component_id=component_id,
                        recovery_id=recovery_id,
                        recovery_action=recovery_action,
                        recovery_point_id=latest_recovery_point["id"],
                        timestamp=self.agent_utils.get_current_timestamp()
                    )
                    
                    # Update recovery status
                    self.active_recoveries[recovery_id]["status"] = "completed"
                    self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
                    self.active_recoveries[recovery_id]["recovery_point_id"] = latest_recovery_point["id"]
                    
                    logger.info(f"Recovery {recovery_id} for component {component_id} completed using recovery point {latest_recovery_point['id']}")
                else:
                    logger.error(f"No recovery points available for component {component_id}")
                    
                    # Update recovery status
                    self.active_recoveries[recovery_id]["status"] = "failed"
                    self.active_recoveries[recovery_id]["error"] = "No recovery points available"
                    self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
            else:
                logger.error(f"Unknown recovery action {recovery_action} for component {component_id}")
                
                # Update recovery status
                self.active_recoveries[recovery_id]["status"] = "failed"
                self.active_recoveries[recovery_id]["error"] = f"Unknown recovery action {recovery_action}"
                self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
        except Exception as e:
            logger.error(f"Error recovering component {component_id}: {str(e)}")
            
            # Update recovery status if it exists
            if recovery_id in self.active_recoveries:
                self.active_recoveries[recovery_id]["status"] = "failed"
                self.active_recoveries[recovery_id]["error"] = str(e)
                self.active_recoveries[recovery_id]["completed_at"] = self.agent_utils.get_current_timestamp()
    
    def _find_latest_recovery_point(self) -> Optional[Dict[str, Any]]:
        """
        Find the latest recovery point
        
        Returns:
            Latest recovery point, or None if no recovery points are available
        """
        if not self.recovery_points:
            return None
        
        # Sort recovery points by timestamp (newest first)
        sorted_recovery_points = sorted(
            self.recovery_points.values(),
            key=lambda rp: rp["timestamp"],
            reverse=True
        )
        
        # Return the newest recovery point
        return sorted_recovery_points[0] if sorted_recovery_points else None
    
    async def _start_backup_scheduler(self):
        """Start the backup scheduler"""
        try:
            # In a real implementation, this would set up scheduled backups
            # For demonstration, we'll just log that the scheduler is started
            logger.info("Started backup scheduler")
            
            # Start backup scheduler task
            asyncio.create_task(self._run_backup_scheduler())
        except Exception as e:
            logger.error(f"Failed to start backup scheduler: {str(e)}")
            raise
    
    async def _run_backup_scheduler(self):
        """Run the backup scheduler"""
        logger.info("Running backup scheduler")
        
        while True:
            try:
                # Check if it's time for a scheduled backup
                # In a real implementation, this would check the schedule and trigger backups
                # For demonstration, we'll just sleep
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                logger.info("Backup scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Error in backup scheduler: {str(e)}")
                await asyncio.sleep(60)
    
    async def create_recovery_point(self, layers: Optional[List[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a recovery point
        
        Args:
            layers: List of layers to include in the recovery point, or None for all layers
            metadata: Additional metadata for the recovery point
            
        Returns:
            Dict containing recovery point creation results
        """
        try:
            # Generate recovery point ID
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            recovery_point_id = f"rp-{timestamp}"
            
            logger.info(f"Creating recovery point {recovery_point_id}")
            
            # Determine layers to include
            if layers is None:
                # Include all layers
                layers = ["data", "core_ai", "generative", "application", "protocol", "workflow", "ui_ux", "security"]
            
            # Create recovery point record
            recovery_point = {
                "id": recovery_point_id,
                "timestamp": self.agent_utils.get_current_timestamp(),
                "type": "manual",
                "status": "creating",
                "layers": layers,
                "size_mb": 0,
                "metadata": metadata or {}
            }
            
            # Store recovery point record
            self.recovery_points[recovery_point_id] = recovery_point
            
            # In a real implementation, this would create the actual recovery point
            # For demonstration, we'll simulate the creation process
            
            # Simulate creation time (1 second per layer)
            await asyncio.sleep(len(layers))
            
            # Update recovery point status
            recovery_point["status"] = "available"
            recovery_point["size_mb"] = len(layers) * 128  # 128 MB per layer
            
            logger.info(f"Recovery point {recovery_point_id} created successfully")
            
            # Record recovery point creation in analytics
            self.analytics_manager.record_recovery_point_creation(
                recovery_point_id=recovery_point_id,
                layers=layers,
                size_mb=recovery_point["size_mb"],
                timestamp=recovery_point["timestamp"]
            )
            
            return {
                "status": "success",
                "recovery_point_id": recovery_point_id,
                "recovery_point": recovery_point
            }
        except Exception as e:
            logger.error(f"Failed to create recovery point: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_recovery_points(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List recovery points
        
        Args:
            status: Filter by status, or None for all
            
        Returns:
            List of recovery points
        """
        recovery_points = []
        
        for recovery_point_id, recovery_point in self.recovery_points.items():
            if status is None or recovery_point["status"] == status:
                recovery_points.append(recovery_point)
        
        # Sort by timestamp (newest first)
        recovery_points.sort(key=lambda rp: rp["timestamp"], reverse=True)
        
        return recovery_points
    
    async def get_recovery_point(self, recovery_point_id: str) -> Dict[str, Any]:
        """
        Get a recovery point
        
        Args:
            recovery_point_id: ID of the recovery point
            
        Returns:
            Dict containing recovery point details
        """
        if recovery_point_id not in self.recovery_points:
            return {
                "status": "not_found",
                "recovery_point_id": recovery_point_id
            }
        
        return {
            "status": "success",
            "recovery_point": self.recovery_points[recovery_point_id]
        }
    
    async def delete_recovery_point(self, recovery_point_id: str) -> Dict[str, Any]:
        """
        Delete a recovery point
        
        Args:
            recovery_point_id: ID of the recovery point to delete
            
        Returns:
            Dict containing deletion results
        """
        if recovery_point_id not in self.recovery_points:
            return {
                "status": "not_found",
                "recovery_point_id": recovery_point_id
            }
        
        recovery_point = self.recovery_points[recovery_point_id]
        
        if recovery_point["status"] == "creating":
            return {
                "status": "invalid_state",
                "recovery_point_id": recovery_point_id,
                "current_status": recovery_point["status"]
            }
        
        logger.info(f"Deleting recovery point {recovery_point_id}")
        
        # In a real implementation, this would delete the actual recovery point
        # For demonstration, we'll just remove it from our records
        
        # Remove recovery point
        del self.recovery_points[recovery_point_id]
        
        # Record recovery point deletion in analytics
        self.analytics_manager.record_recovery_point_deletion(
            recovery_point_id=recovery_point_id,
            timestamp=self.agent_utils.get_current_timestamp()
        )
        
        return {
            "status": "success",
            "recovery_point_id": recovery_point_id
        }
    
    async def restore_from_recovery_point(self, recovery_point_id: str, layers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Restore from a recovery point
        
        Args:
            recovery_point_id: ID of the recovery point to restore from
            layers: List of layers to restore, or None for all layers in the recovery point
            
        Returns:
            Dict containing restoration results
        """
        if recovery_point_id not in self.recovery_points:
            return {
                "status": "not_found",
                "recovery_point_id": recovery_point_id
            }
        
        recovery_point = self.recovery_points[recovery_point_id]
        
        if recovery_point["status"] != "available":
            return {
                "status": "invalid_state",
                "recovery_point_id": recovery_point_id,
                "current_status": recovery_point["status"]
            }
        
        # Determine layers to restore
        if layers is None:
            # Restore all layers in the recovery point
            layers = recovery_point["layers"]
        else:
            # Validate that all requested layers are in the recovery point
            for layer in layers:
                if layer not in recovery_point["layers"]:
                    return {
                        "status": "invalid_layer",
                        "recovery_point_id": recovery_point_id,
                        "invalid_layer": layer,
                        "available_layers": recovery_point["layers"]
                    }
        
        logger.info(f"Restoring from recovery point {recovery_point_id} for layers {layers}")
        
        # Generate restoration ID
        restoration_id = f"restore-{recovery_point_id}-{self.agent_utils.generate_id()}"
        
        # Create restoration record
        restoration = {
            "id": restoration_id,
            "recovery_point_id": recovery_point_id,
            "layers": layers,
            "status": "in_progress",
            "started_at": self.agent_utils.get_current_timestamp()
        }
        
        # In a real implementation, this would perform the actual restoration
        # For demonstration, we'll simulate the restoration process
        
        # Start restoration task
        asyncio.create_task(self._run_restoration(restoration_id, recovery_point_id, layers))
        
        return {
            "status": "started",
            "restoration_id": restoration_id,
            "recovery_point_id": recovery_point_id,
            "layers": layers
        }
    
    async def _run_restoration(self, restoration_id: str, recovery_point_id: str, layers: List[str]):
        """
        Run a restoration
        
        Args:
            restoration_id: ID of the restoration
            recovery_point_id: ID of the recovery point
            layers: List of layers to restore
        """
        logger.info(f"Running restoration {restoration_id} from recovery point {recovery_point_id} for layers {layers}")
        
        try:
            # Simulate restoration time (2 seconds per layer)
            await asyncio.sleep(len(layers) * 2)
            
            # Record restoration completion in analytics
            self.analytics_manager.record_restoration(
                restoration_id=restoration_id,
                recovery_point_id=recovery_point_id,
                layers=layers,
                status="completed",
                timestamp=self.agent_utils.get_current_timestamp()
            )
            
            logger.info(f"Restoration {restoration_id} completed successfully")
        except Exception as e:
            logger.error(f"Error in restoration {restoration_id}: {str(e)}")
            
            # Record restoration failure in analytics
            self.analytics_manager.record_restoration(
                restoration_id=restoration_id,
                recovery_point_id=recovery_point_id,
                layers=layers,
                status="failed",
                error=str(e),
                timestamp=self.agent_utils.get_current_timestamp()
            )
    
    async def get_component_health(self, component_id: str) -> Dict[str, Any]:
        """
        Get health status of a component
        
        Args:
            component_id: ID of the component
            
        Returns:
            Dict containing component health status
        """
        if component_id not in self.health_checks:
            return {
                "status": "not_found",
                "component_id": component_id
            }
        
        return {
            "status": "success",
            "component": self.health_checks[component_id]
        }
    
    async def list_component_health(self) -> List[Dict[str, Any]]:
        """
        List health status of all components
        
        Returns:
            List of component health statuses
        """
        return list(self.health_checks.values())
    
    async def trigger_component_recovery(self, component_id: str, recovery_action: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger recovery for a component
        
        Args:
            component_id: ID of the component
            recovery_action: Recovery action to perform, or None to use the default
            
        Returns:
            Dict containing recovery trigger results
        """
        if component_id not in self.health_checks:
            return {
                "status": "not_found",
                "component_id": component_id
            }
        
        health_check = self.health_checks[component_id]
        
        # Determine recovery action
        if recovery_action is None:
            recovery_action = health_check.get("recovery_action")
            
            if not recovery_action:
                return {
                    "status": "error",
                    "error": f"No recovery action specified for component {component_id}"
                }
        
        logger.info(f"Triggering recovery for component {component_id} with action {recovery_action}")
        
        # Perform recovery
        await self._recover_component(component_id)
        
        return {
            "status": "triggered",
            "component_id": component_id,
            "recovery_action": recovery_action
        }
    
    async def cleanup(self):
        """Clean up resources used by the disaster recovery manager"""
        logger.info("Cleaned up disaster recovery manager")


# Singleton instance
_instance = None

def get_disaster_recovery_manager(config: Optional[Dict[str, Any]] = None) -> DisasterRecoveryManager:
    """
    Get the singleton instance of the disaster recovery manager
    
    Args:
        config: Configuration for the disaster recovery manager (only used if creating a new instance)
        
    Returns:
        DisasterRecoveryManager instance
    """
    global _instance
    
    if _instance is None:
        if config is None:
            config = {}
        
        _instance = DisasterRecoveryManager(config)
    
    return _instance
