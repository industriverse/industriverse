"""
Edge Device Manager for the Deployment Operations Layer.

This module provides capabilities for managing edge devices and deploying
capsules to edge environments across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EdgeDeviceManager:
    """
    Manager for edge devices and edge deployments.
    
    This class provides methods for registering, managing, and deploying to
    edge devices across the Industriverse ecosystem.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Edge Device Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.manager_id = config.get("manager_id", f"edge-manager-{uuid.uuid4().hex[:8]}")
        self.registry_path = config.get("registry_path", "/tmp/edge_registry")
        self.device_timeout = config.get("device_timeout", 300)  # seconds
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        self.offline_mode_enabled = config.get("offline_mode_enabled", True)
        self.compression_enabled = config.get("compression_enabled", True)
        
        # Initialize blockchain integration for device verification
        from ..blockchain.blockchain_integration import BlockchainIntegration
        self.blockchain = BlockchainIntegration(config.get("blockchain", {}))
        
        # Initialize security integration
        from ..security.security_integration import SecurityIntegration
        self.security = SecurityIntegration(config.get("security", {}))
        
        # Initialize analytics manager for edge metrics
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Initialize AI optimization for edge resource allocation
        from ..ai_optimization.ai_optimization_manager import AIOptimizationManager
        self.ai_optimization = AIOptimizationManager(config.get("ai_optimization", {}))
        
        # Create registry directory if it doesn't exist
        os.makedirs(self.registry_path, exist_ok=True)
        
        logger.info(f"Edge Device Manager {self.manager_id} initialized")
    
    def register_device(self, device_data: Dict) -> Dict:
        """
        Register an edge device.
        
        Args:
            device_data: Device data
            
        Returns:
            Dict: Registration results
        """
        try:
            # Generate device ID if not provided
            device_id = device_data.get("device_id")
            if not device_id:
                device_id = f"edge-device-{uuid.uuid4().hex}"
                device_data["device_id"] = device_id
            
            # Add timestamp if not provided
            if "registration_timestamp" not in device_data:
                device_data["registration_timestamp"] = datetime.now().isoformat()
            
            # Add manager ID
            device_data["manager_id"] = self.manager_id
            
            # Add device status if not provided
            if "status" not in device_data:
                device_data["status"] = "registered"
            
            # Add security context if available
            security_context = self.security.get_current_context()
            if security_context:
                device_data["security_context"] = security_context
            
            # Validate device data
            validation_result = self._validate_device_data(device_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Save device to registry
            self._save_device(device_id, device_data)
            
            # Record device in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_device",
                    "device_id": device_id,
                    "timestamp": device_data["registration_timestamp"],
                    "hash": self._calculate_device_hash(device_data)
                })
            
            # Track edge metrics
            self._track_edge_metrics("register", device_data)
            
            return {
                "status": "success",
                "message": "Edge device registered successfully",
                "device_id": device_id,
                "timestamp": device_data["registration_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error registering edge device: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """
        Get an edge device by ID.
        
        Args:
            device_id: Device ID
            
        Returns:
            Optional[Dict]: Device data or None if not found
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            
            # Track edge metrics
            if device_data:
                self._track_edge_metrics("get", {"device_id": device_id})
            
            return device_data
        except Exception as e:
            logger.error(f"Error getting edge device: {e}")
            return None
    
    def update_device(self, device_id: str, update_data: Dict) -> Dict:
        """
        Update an edge device.
        
        Args:
            device_id: Device ID
            update_data: Update data
            
        Returns:
            Dict: Update results
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Add update timestamp
            update_data["update_timestamp"] = datetime.now().isoformat()
            
            # Update device data
            for key, value in update_data.items():
                if key not in ["device_id", "registration_timestamp", "manager_id"]:
                    device_data[key] = value
            
            # Validate updated device data
            validation_result = self._validate_device_data(device_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Save updated device to registry
            self._save_device(device_id, device_data)
            
            # Record update in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_device_update",
                    "device_id": device_id,
                    "timestamp": update_data["update_timestamp"],
                    "hash": self._calculate_device_hash(device_data)
                })
            
            # Track edge metrics
            self._track_edge_metrics("update", {
                "device_id": device_id,
                "update_data": update_data
            })
            
            return {
                "status": "success",
                "message": "Edge device updated successfully",
                "device_id": device_id,
                "timestamp": update_data["update_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error updating edge device: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_device(self, device_id: str) -> Dict:
        """
        Delete an edge device.
        
        Args:
            device_id: Device ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Delete device from registry
            self._delete_device(device_id)
            
            # Record deletion in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_device_deletion",
                    "device_id": device_id,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Track edge metrics
            self._track_edge_metrics("delete", {"device_id": device_id})
            
            return {
                "status": "success",
                "message": "Edge device deleted successfully",
                "device_id": device_id,
                "timestamp": datetime.now().isoformat(),
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error deleting edge device: {e}")
            return {"status": "error", "message": str(e)}
    
    def search_devices(self, filters: Dict = None, sort_by: str = "registration_timestamp", sort_order: str = "desc", limit: int = 100, offset: int = 0) -> Dict:
        """
        Search edge devices.
        
        Args:
            filters: Filter criteria
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum number of devices to return
            offset: Offset for pagination
            
        Returns:
            Dict: Search results
        """
        try:
            # Initialize filters
            if not filters:
                filters = {}
            
            # Get all device IDs
            device_ids = self._get_all_device_ids()
            
            # Load devices
            devices = []
            for device_id in device_ids:
                device_data = self._load_device(device_id)
                if device_data:
                    # Apply filters
                    match = True
                    for key, value in filters.items():
                        if key not in device_data or device_data[key] != value:
                            match = False
                            break
                    
                    if match:
                        devices.append(device_data)
            
            # Sort devices
            if sort_by in ["registration_timestamp", "status", "device_id", "type"]:
                reverse = sort_order.lower() == "desc"
                devices.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
            
            # Apply pagination
            total_devices = len(devices)
            devices = devices[offset:offset + limit]
            
            # Track edge metrics
            self._track_edge_metrics("search", {
                "filters": filters,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "limit": limit,
                "offset": offset,
                "total_devices": total_devices,
                "returned_devices": len(devices)
            })
            
            return {
                "status": "success",
                "message": "Edge devices retrieved successfully",
                "total_devices": total_devices,
                "returned_devices": len(devices),
                "devices": devices
            }
        except Exception as e:
            logger.error(f"Error searching edge devices: {e}")
            return {"status": "error", "message": str(e)}
    
    def deploy_to_device(self, device_id: str, deployment_data: Dict) -> Dict:
        """
        Deploy a capsule to an edge device.
        
        Args:
            device_id: Device ID
            deployment_data: Deployment data
            
        Returns:
            Dict: Deployment results
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Check device status
            if device_data.get("status") not in ["online", "registered"]:
                return {
                    "status": "error",
                    "message": f"Edge device is not available for deployment: {device_id}, status: {device_data.get('status')}"
                }
            
            # Generate deployment ID if not provided
            deployment_id = deployment_data.get("deployment_id")
            if not deployment_id:
                deployment_id = f"edge-deployment-{uuid.uuid4().hex}"
                deployment_data["deployment_id"] = deployment_id
            
            # Add timestamp if not provided
            if "timestamp" not in deployment_data:
                deployment_data["timestamp"] = datetime.now().isoformat()
            
            # Add device ID
            deployment_data["device_id"] = device_id
            
            # Add manager ID
            deployment_data["manager_id"] = self.manager_id
            
            # Add deployment status if not provided
            if "status" not in deployment_data:
                deployment_data["status"] = "pending"
            
            # Validate deployment data
            validation_result = self._validate_deployment_data(deployment_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Optimize deployment for edge resources
            optimization_result = self.ai_optimization.optimize_edge_deployment(device_data, deployment_data)
            if optimization_result.get("status") == "success":
                deployment_data["optimization"] = optimization_result.get("optimization", {})
            
            # Save deployment to registry
            self._save_deployment(deployment_id, deployment_data)
            
            # Execute deployment
            execution_result = self._execute_deployment(device_data, deployment_data)
            
            # Update deployment status
            deployment_data["status"] = execution_result.get("status", "failed")
            deployment_data["execution_result"] = execution_result
            
            # Save updated deployment to registry
            self._save_deployment(deployment_id, deployment_data)
            
            # Record deployment in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_deployment",
                    "deployment_id": deployment_id,
                    "device_id": device_id,
                    "timestamp": deployment_data["timestamp"],
                    "hash": self._calculate_deployment_hash(deployment_data)
                })
            
            # Track edge metrics
            self._track_edge_metrics("deploy", {
                "device_id": device_id,
                "deployment_id": deployment_id,
                "status": deployment_data["status"]
            })
            
            return {
                "status": execution_result.get("status", "failed"),
                "message": execution_result.get("message", "Deployment execution failed"),
                "device_id": device_id,
                "deployment_id": deployment_id,
                "timestamp": deployment_data["timestamp"],
                "execution_result": execution_result,
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error deploying to edge device: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_deployment(self, deployment_id: str) -> Optional[Dict]:
        """
        Get an edge deployment by ID.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Optional[Dict]: Deployment data or None if not found
        """
        try:
            # Load deployment from registry
            deployment_data = self._load_deployment(deployment_id)
            
            # Track edge metrics
            if deployment_data:
                self._track_edge_metrics("get_deployment", {"deployment_id": deployment_id})
            
            return deployment_data
        except Exception as e:
            logger.error(f"Error getting edge deployment: {e}")
            return None
    
    def search_deployments(self, filters: Dict = None, sort_by: str = "timestamp", sort_order: str = "desc", limit: int = 100, offset: int = 0) -> Dict:
        """
        Search edge deployments.
        
        Args:
            filters: Filter criteria
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum number of deployments to return
            offset: Offset for pagination
            
        Returns:
            Dict: Search results
        """
        try:
            # Initialize filters
            if not filters:
                filters = {}
            
            # Get all deployment IDs
            deployment_ids = self._get_all_deployment_ids()
            
            # Load deployments
            deployments = []
            for deployment_id in deployment_ids:
                deployment_data = self._load_deployment(deployment_id)
                if deployment_data:
                    # Apply filters
                    match = True
                    for key, value in filters.items():
                        if key not in deployment_data or deployment_data[key] != value:
                            match = False
                            break
                    
                    if match:
                        deployments.append(deployment_data)
            
            # Sort deployments
            if sort_by in ["timestamp", "status", "deployment_id", "device_id"]:
                reverse = sort_order.lower() == "desc"
                deployments.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
            
            # Apply pagination
            total_deployments = len(deployments)
            deployments = deployments[offset:offset + limit]
            
            # Track edge metrics
            self._track_edge_metrics("search_deployments", {
                "filters": filters,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "limit": limit,
                "offset": offset,
                "total_deployments": total_deployments,
                "returned_deployments": len(deployments)
            })
            
            return {
                "status": "success",
                "message": "Edge deployments retrieved successfully",
                "total_deployments": total_deployments,
                "returned_deployments": len(deployments),
                "deployments": deployments
            }
        except Exception as e:
            logger.error(f"Error searching edge deployments: {e}")
            return {"status": "error", "message": str(e)}
    
    def cancel_deployment(self, deployment_id: str) -> Dict:
        """
        Cancel an edge deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Dict: Cancellation results
        """
        try:
            # Load deployment from registry
            deployment_data = self._load_deployment(deployment_id)
            if not deployment_data:
                return {
                    "status": "error",
                    "message": f"Edge deployment not found: {deployment_id}"
                }
            
            # Check if deployment can be cancelled
            if deployment_data.get("status") not in ["pending", "in_progress"]:
                return {
                    "status": "error",
                    "message": f"Edge deployment cannot be cancelled: {deployment_id}, status: {deployment_data.get('status')}"
                }
            
            # Load device from registry
            device_id = deployment_data.get("device_id")
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Execute cancellation
            cancellation_result = self._execute_cancellation(device_data, deployment_data)
            
            # Update deployment status
            deployment_data["status"] = "cancelled"
            deployment_data["cancellation_timestamp"] = datetime.now().isoformat()
            deployment_data["cancellation_result"] = cancellation_result
            
            # Save updated deployment to registry
            self._save_deployment(deployment_id, deployment_data)
            
            # Record cancellation in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_deployment_cancellation",
                    "deployment_id": deployment_id,
                    "device_id": device_id,
                    "timestamp": deployment_data["cancellation_timestamp"],
                    "hash": self._calculate_deployment_hash(deployment_data)
                })
            
            # Track edge metrics
            self._track_edge_metrics("cancel_deployment", {
                "device_id": device_id,
                "deployment_id": deployment_id
            })
            
            return {
                "status": "success",
                "message": "Edge deployment cancelled successfully",
                "device_id": device_id,
                "deployment_id": deployment_id,
                "timestamp": deployment_data["cancellation_timestamp"],
                "cancellation_result": cancellation_result,
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error cancelling edge deployment: {e}")
            return {"status": "error", "message": str(e)}
    
    def sync_device(self, device_id: str) -> Dict:
        """
        Synchronize an edge device.
        
        Args:
            device_id: Device ID
            
        Returns:
            Dict: Synchronization results
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Check device status
            if device_data.get("status") not in ["online", "offline", "registered"]:
                return {
                    "status": "error",
                    "message": f"Edge device is not available for synchronization: {device_id}, status: {device_data.get('status')}"
                }
            
            # Execute synchronization
            sync_result = self._execute_synchronization(device_data)
            
            # Update device status
            device_data["status"] = sync_result.get("device_status", device_data.get("status"))
            device_data["last_sync_timestamp"] = datetime.now().isoformat()
            device_data["last_sync_result"] = sync_result
            
            # Save updated device to registry
            self._save_device(device_id, device_data)
            
            # Record synchronization in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "edge_device_sync",
                    "device_id": device_id,
                    "timestamp": device_data["last_sync_timestamp"],
                    "hash": self._calculate_device_hash(device_data)
                })
            
            # Track edge metrics
            self._track_edge_metrics("sync", {
                "device_id": device_id,
                "status": device_data["status"]
            })
            
            return {
                "status": "success",
                "message": "Edge device synchronized successfully",
                "device_id": device_id,
                "timestamp": device_data["last_sync_timestamp"],
                "sync_result": sync_result,
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error synchronizing edge device: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_device_status(self, device_id: str) -> Dict:
        """
        Get the status of an edge device.
        
        Args:
            device_id: Device ID
            
        Returns:
            Dict: Status results
        """
        try:
            # Load device from registry
            device_data = self._load_device(device_id)
            if not device_data:
                return {
                    "status": "error",
                    "message": f"Edge device not found: {device_id}"
                }
            
            # Check device status
            current_status = device_data.get("status", "unknown")
            
            # Check if status is stale
            last_sync_timestamp = device_data.get("last_sync_timestamp")
            if last_sync_timestamp:
                last_sync_time = datetime.fromisoformat(last_sync_timestamp)
                current_time = datetime.now()
                time_diff = (current_time - last_sync_time).total_seconds()
                
                # If device was online but hasn't synced recently, mark as offline
                if current_status == "online" and time_diff > self.device_timeout:
                    current_status = "offline"
                    
                    # Update device status
                    device_data["status"] = current_status
                    device_data["status_update_timestamp"] = current_time.isoformat()
                    device_data["status_update_reason"] = "timeout"
                    
                    # Save updated device to registry
                    self._save_device(device_id, device_data)
            
            # Track edge metrics
            self._track_edge_metrics("get_status", {
                "device_id": device_id,
                "status": current_status
            })
            
            return {
                "status": "success",
                "message": "Edge device status retrieved successfully",
                "device_id": device_id,
                "device_status": current_status,
                "last_sync_timestamp": last_sync_timestamp
            }
        except Exception as e:
            logger.error(f"Error getting edge device status: {e}")
            return {"status": "error", "message": str(e)}
    
    def analyze_devices(self, filters: Dict = None, metrics: List[str] = None) -> Dict:
        """
        Analyze edge devices.
        
        Args:
            filters: Filter criteria
            metrics: Metrics to calculate
            
        Returns:
            Dict: Analysis results
        """
        try:
            # Initialize metrics
            if not metrics:
                metrics = ["count", "status", "types", "regions"]
            
            # Search devices
            search_result = self.search_devices(filters, limit=1000)
            
            if search_result.get("status") != "success":
                return search_result
            
            devices = search_result.get("devices", [])
            
            # Initialize results
            results = {
                "total_devices": len(devices)
            }
            
            # Calculate metrics
            if "count" in metrics:
                results["count"] = len(devices)
            
            if "status" in metrics:
                # Count devices by status
                status_counts = {}
                for device in devices:
                    status = device.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                results["status"] = status_counts
            
            if "types" in metrics:
                # Count devices by type
                type_counts = {}
                for device in devices:
                    device_type = device.get("type", "unknown")
                    type_counts[device_type] = type_counts.get(device_type, 0) + 1
                
                results["types"] = type_counts
            
            if "regions" in metrics:
                # Count devices by region
                region_counts = {}
                for device in devices:
                    region = device.get("region", "unknown")
                    region_counts[region] = region_counts.get(region, 0) + 1
                
                results["regions"] = region_counts
            
            if "capabilities" in metrics:
                # Analyze device capabilities
                capability_counts = {}
                for device in devices:
                    capabilities = device.get("capabilities", [])
                    for capability in capabilities:
                        capability_counts[capability] = capability_counts.get(capability, 0) + 1
                
                results["capabilities"] = capability_counts
            
            if "resources" in metrics:
                # Analyze device resources
                resource_stats = {
                    "cpu": {"min": None, "max": None, "avg": 0, "total": 0},
                    "memory": {"min": None, "max": None, "avg": 0, "total": 0},
                    "storage": {"min": None, "max": None, "avg": 0, "total": 0}
                }
                
                for device in devices:
                    resources = device.get("resources", {})
                    for resource_type in ["cpu", "memory", "storage"]:
                        resource_value = resources.get(resource_type, 0)
                        
                        # Update min
                        if resource_stats[resource_type]["min"] is None or resource_value < resource_stats[resource_type]["min"]:
                            resource_stats[resource_type]["min"] = resource_value
                        
                        # Update max
                        if resource_stats[resource_type]["max"] is None or resource_value > resource_stats[resource_type]["max"]:
                            resource_stats[resource_type]["max"] = resource_value
                        
                        # Update total
                        resource_stats[resource_type]["total"] += resource_value
                
                # Calculate averages
                for resource_type in ["cpu", "memory", "storage"]:
                    if len(devices) > 0:
                        resource_stats[resource_type]["avg"] = resource_stats[resource_type]["total"] / len(devices)
                
                results["resources"] = resource_stats
            
            # Track edge metrics
            self._track_edge_metrics("analyze", {
                "filters": filters,
                "metrics": metrics,
                "devices": len(devices)
            })
            
            return {
                "status": "success",
                "message": "Edge devices analyzed successfully",
                "devices": len(devices),
                "metrics": metrics,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error analyzing edge devices: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_device_data(self, device_data: Dict) -> Dict:
        """
        Validate edge device data.
        
        Args:
            device_data: Device data
            
        Returns:
            Dict: Validation results
        """
        try:
            # Check required fields
            required_fields = ["device_id", "type"]
            for field in required_fields:
                if field not in device_data:
                    return {
                        "status": "error",
                        "message": f"Missing required field: {field}"
                    }
            
            # Validate device type
            valid_types = ["sensor", "gateway", "controller", "compute", "storage", "hybrid"]
            if device_data.get("type") not in valid_types:
                return {
                    "status": "error",
                    "message": f"Invalid device type: {device_data.get('type')}, valid types: {valid_types}"
                }
            
            # Validate device status
            valid_statuses = ["registered", "online", "offline", "maintenance", "decommissioned"]
            if "status" in device_data and device_data.get("status") not in valid_statuses:
                return {
                    "status": "error",
                    "message": f"Invalid device status: {device_data.get('status')}, valid statuses: {valid_statuses}"
                }
            
            return {
                "status": "success",
                "message": "Device data validation successful"
            }
        except Exception as e:
            logger.error(f"Error validating device data: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_deployment_data(self, deployment_data: Dict) -> Dict:
        """
        Validate edge deployment data.
        
        Args:
            deployment_data: Deployment data
            
        Returns:
            Dict: Validation results
        """
        try:
            # Check required fields
            required_fields = ["deployment_id", "device_id", "capsule_id"]
            for field in required_fields:
                if field not in deployment_data:
                    return {
                        "status": "error",
                        "message": f"Missing required field: {field}"
                    }
            
            # Validate deployment status
            valid_statuses = ["pending", "in_progress", "completed", "failed", "cancelled"]
            if "status" in deployment_data and deployment_data.get("status") not in valid_statuses:
                return {
                    "status": "error",
                    "message": f"Invalid deployment status: {deployment_data.get('status')}, valid statuses: {valid_statuses}"
                }
            
            return {
                "status": "success",
                "message": "Deployment data validation successful"
            }
        except Exception as e:
            logger.error(f"Error validating deployment data: {e}")
            return {"status": "error", "message": str(e)}
    
    def _save_device(self, device_id: str, device_data: Dict) -> None:
        """
        Save an edge device to registry.
        
        Args:
            device_id: Device ID
            device_data: Device data
        """
        try:
            # Save device to file
            device_file = os.path.join(self.registry_path, f"device-{device_id}.json")
            
            # Compress if enabled
            if self.compression_enabled:
                import gzip
                with gzip.open(f"{device_file}.gz", "wt") as f:
                    json.dump(device_data, f)
            else:
                with open(device_file, "w") as f:
                    json.dump(device_data, f)
        except Exception as e:
            logger.error(f"Error saving edge device: {e}")
            raise
    
    def _load_device(self, device_id: str) -> Optional[Dict]:
        """
        Load an edge device from registry.
        
        Args:
            device_id: Device ID
            
        Returns:
            Optional[Dict]: Device data or None if not found
        """
        try:
            # Check for compressed file first
            device_file_gz = os.path.join(self.registry_path, f"device-{device_id}.json.gz")
            if os.path.exists(device_file_gz):
                # Load from compressed file
                import gzip
                with gzip.open(device_file_gz, "rt") as f:
                    return json.load(f)
            
            # Check for uncompressed file
            device_file = os.path.join(self.registry_path, f"device-{device_id}.json")
            if os.path.exists(device_file):
                # Load from uncompressed file
                with open(device_file, "r") as f:
                    return json.load(f)
            
            return None
        except Exception as e:
            logger.error(f"Error loading edge device: {e}")
            return None
    
    def _delete_device(self, device_id: str) -> None:
        """
        Delete an edge device from registry.
        
        Args:
            device_id: Device ID
        """
        try:
            # Check for compressed file
            device_file_gz = os.path.join(self.registry_path, f"device-{device_id}.json.gz")
            if os.path.exists(device_file_gz):
                os.remove(device_file_gz)
            
            # Check for uncompressed file
            device_file = os.path.join(self.registry_path, f"device-{device_id}.json")
            if os.path.exists(device_file):
                os.remove(device_file)
        except Exception as e:
            logger.error(f"Error deleting edge device: {e}")
            raise
    
    def _get_all_device_ids(self) -> List[str]:
        """
        Get all edge device IDs.
        
        Returns:
            List[str]: List of device IDs
        """
        try:
            device_ids = []
            
            # Get all files in registry directory
            for file in os.listdir(self.registry_path):
                # Check if file is a device file
                if file.startswith("device-") and (file.endswith(".json") or file.endswith(".json.gz")):
                    # Extract device ID
                    device_id = file.replace("device-", "").replace(".json", "").replace(".gz", "")
                    device_ids.append(device_id)
            
            return device_ids
        except Exception as e:
            logger.error(f"Error getting all device IDs: {e}")
            return []
    
    def _save_deployment(self, deployment_id: str, deployment_data: Dict) -> None:
        """
        Save an edge deployment to registry.
        
        Args:
            deployment_id: Deployment ID
            deployment_data: Deployment data
        """
        try:
            # Save deployment to file
            deployment_file = os.path.join(self.registry_path, f"deployment-{deployment_id}.json")
            
            # Compress if enabled
            if self.compression_enabled:
                import gzip
                with gzip.open(f"{deployment_file}.gz", "wt") as f:
                    json.dump(deployment_data, f)
            else:
                with open(deployment_file, "w") as f:
                    json.dump(deployment_data, f)
        except Exception as e:
            logger.error(f"Error saving edge deployment: {e}")
            raise
    
    def _load_deployment(self, deployment_id: str) -> Optional[Dict]:
        """
        Load an edge deployment from registry.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Optional[Dict]: Deployment data or None if not found
        """
        try:
            # Check for compressed file first
            deployment_file_gz = os.path.join(self.registry_path, f"deployment-{deployment_id}.json.gz")
            if os.path.exists(deployment_file_gz):
                # Load from compressed file
                import gzip
                with gzip.open(deployment_file_gz, "rt") as f:
                    return json.load(f)
            
            # Check for uncompressed file
            deployment_file = os.path.join(self.registry_path, f"deployment-{deployment_id}.json")
            if os.path.exists(deployment_file):
                # Load from uncompressed file
                with open(deployment_file, "r") as f:
                    return json.load(f)
            
            return None
        except Exception as e:
            logger.error(f"Error loading edge deployment: {e}")
            return None
    
    def _get_all_deployment_ids(self) -> List[str]:
        """
        Get all edge deployment IDs.
        
        Returns:
            List[str]: List of deployment IDs
        """
        try:
            deployment_ids = []
            
            # Get all files in registry directory
            for file in os.listdir(self.registry_path):
                # Check if file is a deployment file
                if file.startswith("deployment-") and (file.endswith(".json") or file.endswith(".json.gz")):
                    # Extract deployment ID
                    deployment_id = file.replace("deployment-", "").replace(".json", "").replace(".gz", "")
                    deployment_ids.append(deployment_id)
            
            return deployment_ids
        except Exception as e:
            logger.error(f"Error getting all deployment IDs: {e}")
            return []
    
    def _calculate_device_hash(self, device_data: Dict) -> str:
        """
        Calculate hash for an edge device.
        
        Args:
            device_data: Device data
            
        Returns:
            str: Device hash
        """
        try:
            # Convert device data to JSON string
            device_json = json.dumps(device_data, sort_keys=True)
            
            # Calculate SHA-256 hash
            import hashlib
            device_hash = hashlib.sha256(device_json.encode()).hexdigest()
            
            return device_hash
        except Exception as e:
            logger.error(f"Error calculating device hash: {e}")
            raise
    
    def _calculate_deployment_hash(self, deployment_data: Dict) -> str:
        """
        Calculate hash for an edge deployment.
        
        Args:
            deployment_data: Deployment data
            
        Returns:
            str: Deployment hash
        """
        try:
            # Convert deployment data to JSON string
            deployment_json = json.dumps(deployment_data, sort_keys=True)
            
            # Calculate SHA-256 hash
            import hashlib
            deployment_hash = hashlib.sha256(deployment_json.encode()).hexdigest()
            
            return deployment_hash
        except Exception as e:
            logger.error(f"Error calculating deployment hash: {e}")
            raise
    
    def _execute_deployment(self, device_data: Dict, deployment_data: Dict) -> Dict:
        """
        Execute an edge deployment.
        
        Args:
            device_data: Device data
            deployment_data: Deployment data
            
        Returns:
            Dict: Execution results
        """
        try:
            # Get device connection info
            connection_info = device_data.get("connection_info", {})
            device_type = device_data.get("type")
            device_id = device_data.get("device_id")
            
            # Get deployment info
            capsule_id = deployment_data.get("capsule_id")
            deployment_id = deployment_data.get("deployment_id")
            
            # Check if device is online
            if device_data.get("status") != "online":
                # If offline mode is enabled, queue deployment for later
                if self.offline_mode_enabled:
                    logger.info(f"Device {device_id} is offline, queueing deployment {deployment_id} for later")
                    return {
                        "status": "queued",
                        "message": f"Device is offline, deployment queued for later execution",
                        "device_id": device_id,
                        "deployment_id": deployment_id
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Device is offline and offline mode is disabled",
                        "device_id": device_id,
                        "deployment_id": deployment_id
                    }
            
            # Simulate deployment execution
            logger.info(f"Executing deployment {deployment_id} to device {device_id}")
            
            # In a real implementation, this would connect to the device and deploy the capsule
            # For simulation purposes, we'll just return success
            
            return {
                "status": "success",
                "message": f"Deployment executed successfully",
                "device_id": device_id,
                "deployment_id": deployment_id,
                "capsule_id": capsule_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing deployment: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "device_id": device_data.get("device_id"),
                "deployment_id": deployment_data.get("deployment_id"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _execute_cancellation(self, device_data: Dict, deployment_data: Dict) -> Dict:
        """
        Execute an edge deployment cancellation.
        
        Args:
            device_data: Device data
            deployment_data: Deployment data
            
        Returns:
            Dict: Cancellation results
        """
        try:
            # Get device connection info
            connection_info = device_data.get("connection_info", {})
            device_type = device_data.get("type")
            device_id = device_data.get("device_id")
            
            # Get deployment info
            deployment_id = deployment_data.get("deployment_id")
            
            # Check if device is online
            if device_data.get("status") != "online":
                return {
                    "status": "failed",
                    "message": f"Device is offline, cannot cancel deployment",
                    "device_id": device_id,
                    "deployment_id": deployment_id
                }
            
            # Simulate cancellation execution
            logger.info(f"Cancelling deployment {deployment_id} on device {device_id}")
            
            # In a real implementation, this would connect to the device and cancel the deployment
            # For simulation purposes, we'll just return success
            
            return {
                "status": "success",
                "message": f"Deployment cancelled successfully",
                "device_id": device_id,
                "deployment_id": deployment_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error cancelling deployment: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "device_id": device_data.get("device_id"),
                "deployment_id": deployment_data.get("deployment_id"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _execute_synchronization(self, device_data: Dict) -> Dict:
        """
        Execute an edge device synchronization.
        
        Args:
            device_data: Device data
            
        Returns:
            Dict: Synchronization results
        """
        try:
            # Get device connection info
            connection_info = device_data.get("connection_info", {})
            device_type = device_data.get("type")
            device_id = device_data.get("device_id")
            
            # Simulate synchronization
            logger.info(f"Synchronizing device {device_id}")
            
            # In a real implementation, this would connect to the device and synchronize state
            # For simulation purposes, we'll just return success and simulate device status
            
            # Simulate device status (online/offline)
            import random
            device_status = "online" if random.random() > 0.2 else "offline"
            
            # Simulate device metrics
            device_metrics = {
                "cpu_usage": random.uniform(0, 100),
                "memory_usage": random.uniform(0, 100),
                "storage_usage": random.uniform(0, 100),
                "temperature": random.uniform(20, 80),
                "battery_level": random.uniform(0, 100) if device_data.get("has_battery", False) else None
            }
            
            # Simulate deployed capsules
            deployed_capsules = []
            for deployment_id in self._get_all_deployment_ids():
                deployment_data = self._load_deployment(deployment_id)
                if deployment_data and deployment_data.get("device_id") == device_id and deployment_data.get("status") == "success":
                    deployed_capsules.append({
                        "capsule_id": deployment_data.get("capsule_id"),
                        "deployment_id": deployment_id,
                        "status": "running" if random.random() > 0.1 else "stopped",
                        "metrics": {
                            "cpu_usage": random.uniform(0, 50),
                            "memory_usage": random.uniform(0, 50),
                            "storage_usage": random.uniform(0, 50)
                        }
                    })
            
            return {
                "status": "success",
                "message": f"Device synchronized successfully",
                "device_id": device_id,
                "device_status": device_status,
                "device_metrics": device_metrics,
                "deployed_capsules": deployed_capsules,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error synchronizing device: {e}")
            return {
                "status": "failed",
                "message": str(e),
                "device_id": device_data.get("device_id"),
                "timestamp": datetime.now().isoformat()
            }
    
    def _track_edge_metrics(self, operation: str, data: Dict) -> None:
        """
        Track edge metrics.
        
        Args:
            operation: Operation name
            data: Operation data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"edge_{operation}",
                "timestamp": datetime.now().isoformat(),
                "manager_id": self.manager_id
            }
            
            # Add operation data
            metrics.update(data)
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking edge metrics: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Edge Device Manager.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "device_timeout" in config:
                self.device_timeout = config["device_timeout"]
            
            if "max_retry_attempts" in config:
                self.max_retry_attempts = config["max_retry_attempts"]
            
            if "offline_mode_enabled" in config:
                self.offline_mode_enabled = config["offline_mode_enabled"]
            
            if "compression_enabled" in config:
                self.compression_enabled = config["compression_enabled"]
            
            if "registry_path" in config:
                self.registry_path = config["registry_path"]
                
                # Create registry directory if it doesn't exist
                os.makedirs(self.registry_path, exist_ok=True)
            
            # Configure blockchain integration
            blockchain_result = None
            if "blockchain" in config:
                blockchain_result = self.blockchain.configure(config["blockchain"])
            
            # Configure security integration
            security_result = None
            if "security" in config:
                security_result = self.security.configure(config["security"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Configure AI optimization
            ai_optimization_result = None
            if "ai_optimization" in config:
                ai_optimization_result = self.ai_optimization.configure(config["ai_optimization"])
            
            return {
                "status": "success",
                "message": "Edge Device Manager configured successfully",
                "manager_id": self.manager_id,
                "blockchain_result": blockchain_result,
                "security_result": security_result,
                "analytics_result": analytics_result,
                "ai_optimization_result": ai_optimization_result
            }
        except Exception as e:
            logger.error(f"Error configuring Edge Device Manager: {e}")
            return {"status": "error", "message": str(e)}
