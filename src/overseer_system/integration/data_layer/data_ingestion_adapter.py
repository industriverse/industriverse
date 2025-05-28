"""
Data Ingestion Adapter for the Overseer System.

This module provides the integration adapter for data ingestion components
of the Industriverse Data Layer, enabling seamless data ingestion from
various sources into the Overseer System.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

from src.integration.base_integration_adapter import BaseIntegrationAdapter
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService
from src.config.config_service import ConfigService
from src.auth.auth_service import AuthService

class DataIngestionAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for Data Ingestion components of the Industriverse Data Layer.
    
    This class provides integration with data ingestion components, enabling
    seamless data ingestion from various sources into the Overseer System.
    """
    
    def __init__(
        self,
        adapter_id: str,
        manager: Any,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        config_service: ConfigService,
        auth_service: AuthService,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Data Ingestion Adapter.
        
        Args:
            adapter_id: Unique identifier for this adapter
            manager: Parent integration manager
            mcp_bridge: MCP protocol bridge for internal communication
            a2a_bridge: A2A protocol bridge for external communication
            event_bus: Event bus client for event-driven communication
            data_access: Data access service for persistence
            config_service: Configuration service for settings
            auth_service: Authentication service for security
            config: Adapter-specific configuration
            logger: Optional logger instance
        """
        super().__init__(
            adapter_id=adapter_id,
            manager=manager,
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            config_service=config_service,
            auth_service=auth_service,
            config=config,
            logger=logger or logging.getLogger(__name__)
        )
        
        # Initialize data ingestion specific resources
        self._source_connectors = {}
        self._ingestion_pipelines = {}
        self._active_ingestion_jobs = {}
        
        # Initialize metrics
        self._metrics = {
            "total_ingested_records": 0,
            "total_ingestion_errors": 0,
            "active_ingestion_jobs": 0,
            "last_ingestion_timestamp": None
        }
        
        self.logger.info(f"Data Ingestion Adapter {adapter_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this adapter.
        
        Returns:
            List of supported context types
        """
        return [
            "data_layer.ingestion",
            "data_layer.ingestion.source",
            "data_layer.ingestion.pipeline",
            "data_layer.ingestion.job"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this adapter.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "data_ingestion",
                "description": "Ingest data from various sources",
                "parameters": {
                    "source_type": {
                        "type": "string",
                        "description": "Type of data source (e.g., file, database, api, stream)"
                    },
                    "source_config": {
                        "type": "object",
                        "description": "Configuration for the data source"
                    },
                    "pipeline_id": {
                        "type": "string",
                        "description": "ID of the ingestion pipeline to use"
                    }
                }
            },
            {
                "type": "data_source_management",
                "description": "Manage data sources for ingestion",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "source_id": {
                        "type": "string",
                        "description": "ID of the data source"
                    },
                    "source_config": {
                        "type": "object",
                        "description": "Configuration for the data source"
                    }
                }
            },
            {
                "type": "ingestion_pipeline_management",
                "description": "Manage data ingestion pipelines",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "pipeline_id": {
                        "type": "string",
                        "description": "ID of the ingestion pipeline"
                    },
                    "pipeline_config": {
                        "type": "object",
                        "description": "Configuration for the ingestion pipeline"
                    }
                }
            }
        ]
    
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        try:
            # Load source connectors from configuration
            source_connectors_config = self.config.get("source_connectors", {})
            for source_id, source_config in source_connectors_config.items():
                self._create_source_connector(source_id, source_config)
            
            # Load ingestion pipelines from configuration
            ingestion_pipelines_config = self.config.get("ingestion_pipelines", {})
            for pipeline_id, pipeline_config in ingestion_pipelines_config.items():
                self._create_ingestion_pipeline(pipeline_id, pipeline_config)
            
            self.logger.info(f"Initialized resources for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        try:
            # Start auto-start ingestion pipelines
            for pipeline_id, pipeline in self._ingestion_pipelines.items():
                if pipeline.get("auto_start", False):
                    self._start_ingestion_pipeline(pipeline_id)
            
            self.logger.info(f"Started resources for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        try:
            # Stop all active ingestion jobs
            for job_id in list(self._active_ingestion_jobs.keys()):
                self._stop_ingestion_job(job_id)
            
            self.logger.info(f"Stopped resources for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        try:
            # Clear all resources
            self._source_connectors = {}
            self._ingestion_pipelines = {}
            self._active_ingestion_jobs = {}
            
            self.logger.info(f"Released resources for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Check source connectors
            unhealthy_connectors = 0
            for source_id, source in self._source_connectors.items():
                if source.get("status") == "error":
                    unhealthy_connectors += 1
            
            # Check ingestion pipelines
            unhealthy_pipelines = 0
            for pipeline_id, pipeline in self._ingestion_pipelines.items():
                if pipeline.get("status") == "error":
                    unhealthy_pipelines += 1
            
            # Check active ingestion jobs
            unhealthy_jobs = 0
            for job_id, job in self._active_ingestion_jobs.items():
                if job.get("status") == "error":
                    unhealthy_jobs += 1
            
            # Determine overall health
            total_connectors = len(self._source_connectors)
            total_pipelines = len(self._ingestion_pipelines)
            total_jobs = len(self._active_ingestion_jobs)
            
            if unhealthy_connectors > 0 or unhealthy_pipelines > 0 or unhealthy_jobs > 0:
                # At least one component is unhealthy
                if (unhealthy_connectors / max(total_connectors, 1) > 0.5 or
                    unhealthy_pipelines / max(total_pipelines, 1) > 0.5 or
                    unhealthy_jobs / max(total_jobs, 1) > 0.5):
                    # More than 50% of components are unhealthy
                    return "unhealthy"
                else:
                    # Less than 50% of components are unhealthy
                    return "degraded"
            else:
                # All components are healthy
                return "healthy"
        except Exception as e:
            self.logger.error(f"Error checking resource health for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply source connector configuration changes
            source_connectors_config = self.config.get("source_connectors", {})
            
            # Remove deleted source connectors
            for source_id in list(self._source_connectors.keys()):
                if source_id not in source_connectors_config:
                    self._delete_source_connector(source_id)
            
            # Add or update source connectors
            for source_id, source_config in source_connectors_config.items():
                if source_id in self._source_connectors:
                    self._update_source_connector(source_id, source_config)
                else:
                    self._create_source_connector(source_id, source_config)
            
            # Apply ingestion pipeline configuration changes
            ingestion_pipelines_config = self.config.get("ingestion_pipelines", {})
            
            # Remove deleted ingestion pipelines
            for pipeline_id in list(self._ingestion_pipelines.keys()):
                if pipeline_id not in ingestion_pipelines_config:
                    self._delete_ingestion_pipeline(pipeline_id)
            
            # Add or update ingestion pipelines
            for pipeline_id, pipeline_config in ingestion_pipelines_config.items():
                if pipeline_id in self._ingestion_pipelines:
                    self._update_ingestion_pipeline(pipeline_id, pipeline_config)
                else:
                    self._create_ingestion_pipeline(pipeline_id, pipeline_config)
            
            self.logger.info(f"Applied configuration changes for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        return {
            "source_connectors": {
                source_id: {
                    "type": source.get("type"),
                    "status": source.get("status")
                }
                for source_id, source in self._source_connectors.items()
            },
            "ingestion_pipelines": {
                pipeline_id: {
                    "status": pipeline.get("status"),
                    "source_id": pipeline.get("source_id")
                }
                for pipeline_id, pipeline in self._ingestion_pipelines.items()
            },
            "active_ingestion_jobs": {
                job_id: {
                    "pipeline_id": job.get("pipeline_id"),
                    "status": job.get("status"),
                    "start_time": job.get("start_time"),
                    "records_processed": job.get("records_processed", 0),
                    "errors": job.get("errors", 0)
                }
                for job_id, job in self._active_ingestion_jobs.items()
            },
            "metrics": self._metrics
        }
    
    def _handle_custom_command(self, command: str, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle a custom command event.
        
        Args:
            command: Command to handle
            event: Command event data
        
        Returns:
            Optional result data
        """
        if command == "create_source_connector":
            source_id = event.get("source_id", str(uuid.uuid4()))
            source_config = event.get("source_config", {})
            self._create_source_connector(source_id, source_config)
            return {"source_id": source_id}
        
        elif command == "update_source_connector":
            source_id = event.get("source_id")
            source_config = event.get("source_config", {})
            if not source_id:
                raise ValueError("source_id is required")
            self._update_source_connector(source_id, source_config)
            return {"source_id": source_id}
        
        elif command == "delete_source_connector":
            source_id = event.get("source_id")
            if not source_id:
                raise ValueError("source_id is required")
            self._delete_source_connector(source_id)
            return {"source_id": source_id}
        
        elif command == "list_source_connectors":
            return {
                "source_connectors": {
                    source_id: {
                        "type": source.get("type"),
                        "status": source.get("status")
                    }
                    for source_id, source in self._source_connectors.items()
                }
            }
        
        elif command == "create_ingestion_pipeline":
            pipeline_id = event.get("pipeline_id", str(uuid.uuid4()))
            pipeline_config = event.get("pipeline_config", {})
            self._create_ingestion_pipeline(pipeline_id, pipeline_config)
            return {"pipeline_id": pipeline_id}
        
        elif command == "update_ingestion_pipeline":
            pipeline_id = event.get("pipeline_id")
            pipeline_config = event.get("pipeline_config", {})
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            self._update_ingestion_pipeline(pipeline_id, pipeline_config)
            return {"pipeline_id": pipeline_id}
        
        elif command == "delete_ingestion_pipeline":
            pipeline_id = event.get("pipeline_id")
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            self._delete_ingestion_pipeline(pipeline_id)
            return {"pipeline_id": pipeline_id}
        
        elif command == "list_ingestion_pipelines":
            return {
                "ingestion_pipelines": {
                    pipeline_id: {
                        "status": pipeline.get("status"),
                        "source_id": pipeline.get("source_id")
                    }
                    for pipeline_id, pipeline in self._ingestion_pipelines.items()
                }
            }
        
        elif command == "start_ingestion_pipeline":
            pipeline_id = event.get("pipeline_id")
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            job_id = self._start_ingestion_pipeline(pipeline_id)
            return {"job_id": job_id, "pipeline_id": pipeline_id}
        
        elif command == "stop_ingestion_job":
            job_id = event.get("job_id")
            if not job_id:
                raise ValueError("job_id is required")
            self._stop_ingestion_job(job_id)
            return {"job_id": job_id}
        
        elif command == "list_ingestion_jobs":
            return {
                "active_ingestion_jobs": {
                    job_id: {
                        "pipeline_id": job.get("pipeline_id"),
                        "status": job.get("status"),
                        "start_time": job.get("start_time"),
                        "records_processed": job.get("records_processed", 0),
                        "errors": job.get("errors", 0)
                    }
                    for job_id, job in self._active_ingestion_jobs.items()
                }
            }
        
        elif command == "get_metrics":
            return {"metrics": self._metrics}
        
        elif command == "reset_metrics":
            self._metrics = {
                "total_ingested_records": 0,
                "total_ingestion_errors": 0,
                "active_ingestion_jobs": 0,
                "last_ingestion_timestamp": None
            }
            return {"metrics": self._metrics}
        
        else:
            raise ValueError(f"Unsupported command: {command}")
    
    def _subscribe_to_additional_events(self) -> None:
        """Subscribe to additional events specific to this adapter."""
        try:
            # Subscribe to data ingestion events
            self.event_bus.subscribe(
                topic="data_layer.ingestion.event",
                group_id=f"{self.adapter_id}-ingestion-event-handler",
                callback=self._handle_ingestion_event
            )
            
            self.logger.info(f"Subscribed to additional events for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error subscribing to additional events for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _unsubscribe_from_additional_events(self) -> None:
        """Unsubscribe from additional events specific to this adapter."""
        try:
            # Unsubscribe from data ingestion events
            self.event_bus.unsubscribe(
                topic="data_layer.ingestion.event",
                group_id=f"{self.adapter_id}-ingestion-event-handler"
            )
            
            self.logger.info(f"Unsubscribed from additional events for Data Ingestion Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from additional events for Data Ingestion Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _handle_ingestion_event(self, event: Dict[str, Any]) -> None:
        """
        Handle data ingestion events.
        
        Args:
            event: Event data
        """
        try:
            event_type = event.get("event_type")
            
            if event_type == "ingestion_complete":
                job_id = event.get("job_id")
                records_processed = event.get("records_processed", 0)
                errors = event.get("errors", 0)
                
                # Update metrics
                self._metrics["total_ingested_records"] += records_processed
                self._metrics["total_ingestion_errors"] += errors
                self._metrics["last_ingestion_timestamp"] = self.data_access.get_current_timestamp()
                
                # Update job status
                if job_id in self._active_ingestion_jobs:
                    job = self._active_ingestion_jobs[job_id]
                    job["status"] = "completed"
                    job["records_processed"] = records_processed
                    job["errors"] = errors
                    job["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active jobs
                    del self._active_ingestion_jobs[job_id]
                    self._metrics["active_ingestion_jobs"] = len(self._active_ingestion_jobs)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("data_ingestion_count", records_processed)
                
                self.logger.info(f"Ingestion job {job_id} completed: {records_processed} records processed, {errors} errors")
            
            elif event_type == "ingestion_error":
                job_id = event.get("job_id")
                error = event.get("error")
                
                # Update metrics
                self._metrics["total_ingestion_errors"] += 1
                
                # Update job status
                if job_id in self._active_ingestion_jobs:
                    job = self._active_ingestion_jobs[job_id]
                    job["status"] = "error"
                    job["error"] = error
                    job["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active jobs
                    del self._active_ingestion_jobs[job_id]
                    self._metrics["active_ingestion_jobs"] = len(self._active_ingestion_jobs)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("error_count", 1)
                
                self.logger.error(f"Ingestion job {job_id} error: {error}")
            
            elif event_type == "ingestion_progress":
                job_id = event.get("job_id")
                records_processed = event.get("records_processed", 0)
                errors = event.get("errors", 0)
                
                # Update job status
                if job_id in self._active_ingestion_jobs:
                    job = self._active_ingestion_jobs[job_id]
                    job["records_processed"] = records_processed
                    job["errors"] = errors
                
                self.logger.debug(f"Ingestion job {job_id} progress: {records_processed} records processed, {errors} errors")
        except Exception as e:
            self.logger.error(f"Error handling ingestion event: {str(e)}")
    
    def _create_source_connector(self, source_id: str, source_config: Dict[str, Any]) -> None:
        """
        Create a new source connector.
        
        Args:
            source_id: Source connector ID
            source_config: Source connector configuration
        """
        try:
            # Validate source configuration
            source_type = source_config.get("type")
            if not source_type:
                raise ValueError("Source type is required")
            
            # Create source connector
            self._source_connectors[source_id] = {
                "id": source_id,
                "type": source_type,
                "config": source_config,
                "status": "initialized"
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.source.{source_id}",
                provider_name=f"Data Source: {source_id}",
                provider_type="data_source",
                context_types=[
                    "data_layer.ingestion.source",
                    f"data_layer.ingestion.source.{source_type}"
                ]
            )
            
            # Save to configuration
            self.config["source_connectors"] = self.config.get("source_connectors", {})
            self.config["source_connectors"][source_id] = source_config
            
            self.logger.info(f"Created source connector {source_id} of type {source_type}")
        except Exception as e:
            self.logger.error(f"Error creating source connector {source_id}: {str(e)}")
            raise
    
    def _update_source_connector(self, source_id: str, source_config: Dict[str, Any]) -> None:
        """
        Update an existing source connector.
        
        Args:
            source_id: Source connector ID
            source_config: Source connector configuration
        """
        try:
            # Check if source connector exists
            if source_id not in self._source_connectors:
                raise ValueError(f"Source connector {source_id} does not exist")
            
            # Validate source configuration
            source_type = source_config.get("type")
            if not source_type:
                raise ValueError("Source type is required")
            
            # Update source connector
            self._source_connectors[source_id]["type"] = source_type
            self._source_connectors[source_id]["config"] = source_config
            self._source_connectors[source_id]["status"] = "initialized"
            
            # Update MCP registration if type changed
            if self._source_connectors[source_id]["type"] != source_type:
                # Unregister old context provider
                self.mcp_bridge.unregister_context_provider(
                    provider_id=f"{self.adapter_id}.source.{source_id}"
                )
                
                # Register new context provider
                self.mcp_bridge.register_context_provider(
                    provider_id=f"{self.adapter_id}.source.{source_id}",
                    provider_name=f"Data Source: {source_id}",
                    provider_type="data_source",
                    context_types=[
                        "data_layer.ingestion.source",
                        f"data_layer.ingestion.source.{source_type}"
                    ]
                )
            
            # Save to configuration
            self.config["source_connectors"] = self.config.get("source_connectors", {})
            self.config["source_connectors"][source_id] = source_config
            
            self.logger.info(f"Updated source connector {source_id} of type {source_type}")
        except Exception as e:
            self.logger.error(f"Error updating source connector {source_id}: {str(e)}")
            raise
    
    def _delete_source_connector(self, source_id: str) -> None:
        """
        Delete a source connector.
        
        Args:
            source_id: Source connector ID
        """
        try:
            # Check if source connector exists
            if source_id not in self._source_connectors:
                raise ValueError(f"Source connector {source_id} does not exist")
            
            # Check if source connector is used by any pipeline
            for pipeline_id, pipeline in self._ingestion_pipelines.items():
                if pipeline.get("source_id") == source_id:
                    raise ValueError(f"Source connector {source_id} is used by pipeline {pipeline_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.source.{source_id}"
            )
            
            # Delete source connector
            del self._source_connectors[source_id]
            
            # Remove from configuration
            if "source_connectors" in self.config and source_id in self.config["source_connectors"]:
                del self.config["source_connectors"][source_id]
            
            self.logger.info(f"Deleted source connector {source_id}")
        except Exception as e:
            self.logger.error(f"Error deleting source connector {source_id}: {str(e)}")
            raise
    
    def _create_ingestion_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> None:
        """
        Create a new ingestion pipeline.
        
        Args:
            pipeline_id: Ingestion pipeline ID
            pipeline_config: Ingestion pipeline configuration
        """
        try:
            # Validate pipeline configuration
            source_id = pipeline_config.get("source_id")
            if not source_id:
                raise ValueError("Source ID is required")
            
            # Check if source connector exists
            if source_id not in self._source_connectors:
                raise ValueError(f"Source connector {source_id} does not exist")
            
            # Create ingestion pipeline
            self._ingestion_pipelines[pipeline_id] = {
                "id": pipeline_id,
                "source_id": source_id,
                "config": pipeline_config,
                "status": "initialized",
                "auto_start": pipeline_config.get("auto_start", False)
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.pipeline.{pipeline_id}",
                provider_name=f"Ingestion Pipeline: {pipeline_id}",
                provider_type="ingestion_pipeline",
                context_types=[
                    "data_layer.ingestion.pipeline"
                ]
            )
            
            # Save to configuration
            self.config["ingestion_pipelines"] = self.config.get("ingestion_pipelines", {})
            self.config["ingestion_pipelines"][pipeline_id] = pipeline_config
            
            self.logger.info(f"Created ingestion pipeline {pipeline_id} for source {source_id}")
        except Exception as e:
            self.logger.error(f"Error creating ingestion pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _update_ingestion_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> None:
        """
        Update an existing ingestion pipeline.
        
        Args:
            pipeline_id: Ingestion pipeline ID
            pipeline_config: Ingestion pipeline configuration
        """
        try:
            # Check if ingestion pipeline exists
            if pipeline_id not in self._ingestion_pipelines:
                raise ValueError(f"Ingestion pipeline {pipeline_id} does not exist")
            
            # Validate pipeline configuration
            source_id = pipeline_config.get("source_id")
            if not source_id:
                raise ValueError("Source ID is required")
            
            # Check if source connector exists
            if source_id not in self._source_connectors:
                raise ValueError(f"Source connector {source_id} does not exist")
            
            # Update ingestion pipeline
            self._ingestion_pipelines[pipeline_id]["source_id"] = source_id
            self._ingestion_pipelines[pipeline_id]["config"] = pipeline_config
            self._ingestion_pipelines[pipeline_id]["status"] = "initialized"
            self._ingestion_pipelines[pipeline_id]["auto_start"] = pipeline_config.get("auto_start", False)
            
            # Save to configuration
            self.config["ingestion_pipelines"] = self.config.get("ingestion_pipelines", {})
            self.config["ingestion_pipelines"][pipeline_id] = pipeline_config
            
            self.logger.info(f"Updated ingestion pipeline {pipeline_id} for source {source_id}")
        except Exception as e:
            self.logger.error(f"Error updating ingestion pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _delete_ingestion_pipeline(self, pipeline_id: str) -> None:
        """
        Delete an ingestion pipeline.
        
        Args:
            pipeline_id: Ingestion pipeline ID
        """
        try:
            # Check if ingestion pipeline exists
            if pipeline_id not in self._ingestion_pipelines:
                raise ValueError(f"Ingestion pipeline {pipeline_id} does not exist")
            
            # Check if ingestion pipeline is running
            for job_id, job in self._active_ingestion_jobs.items():
                if job.get("pipeline_id") == pipeline_id:
                    raise ValueError(f"Ingestion pipeline {pipeline_id} has active job {job_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.pipeline.{pipeline_id}"
            )
            
            # Delete ingestion pipeline
            del self._ingestion_pipelines[pipeline_id]
            
            # Remove from configuration
            if "ingestion_pipelines" in self.config and pipeline_id in self.config["ingestion_pipelines"]:
                del self.config["ingestion_pipelines"][pipeline_id]
            
            self.logger.info(f"Deleted ingestion pipeline {pipeline_id}")
        except Exception as e:
            self.logger.error(f"Error deleting ingestion pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _start_ingestion_pipeline(self, pipeline_id: str) -> str:
        """
        Start an ingestion pipeline.
        
        Args:
            pipeline_id: Ingestion pipeline ID
        
        Returns:
            Job ID
        """
        try:
            # Check if ingestion pipeline exists
            if pipeline_id not in self._ingestion_pipelines:
                raise ValueError(f"Ingestion pipeline {pipeline_id} does not exist")
            
            # Create job ID
            job_id = str(uuid.uuid4())
            
            # Get pipeline and source
            pipeline = self._ingestion_pipelines[pipeline_id]
            source_id = pipeline.get("source_id")
            source = self._source_connectors.get(source_id)
            
            if not source:
                raise ValueError(f"Source connector {source_id} does not exist")
            
            # Create ingestion job
            self._active_ingestion_jobs[job_id] = {
                "id": job_id,
                "pipeline_id": pipeline_id,
                "source_id": source_id,
                "status": "running",
                "start_time": self.data_access.get_current_timestamp(),
                "records_processed": 0,
                "errors": 0
            }
            
            # Update metrics
            self._metrics["active_ingestion_jobs"] = len(self._active_ingestion_jobs)
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.job.{job_id}",
                provider_name=f"Ingestion Job: {job_id}",
                provider_type="ingestion_job",
                context_types=[
                    "data_layer.ingestion.job"
                ]
            )
            
            # Publish job start event
            self.event_bus.publish(
                topic="data_layer.ingestion.job",
                key=job_id,
                value={
                    "job_id": job_id,
                    "pipeline_id": pipeline_id,
                    "source_id": source_id,
                    "event_type": "job_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start ingestion job (simulated for now)
            # In a real implementation, this would start an actual ingestion process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.ingestion.event",
                key=job_id,
                value={
                    "event_type": "ingestion_complete",
                    "job_id": job_id,
                    "records_processed": 100,  # Simulated value
                    "errors": 0,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started ingestion pipeline {pipeline_id} with job {job_id}")
            
            return job_id
        except Exception as e:
            self.logger.error(f"Error starting ingestion pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _stop_ingestion_job(self, job_id: str) -> None:
        """
        Stop an ingestion job.
        
        Args:
            job_id: Ingestion job ID
        """
        try:
            # Check if ingestion job exists
            if job_id not in self._active_ingestion_jobs:
                raise ValueError(f"Ingestion job {job_id} does not exist")
            
            # Get job
            job = self._active_ingestion_jobs[job_id]
            
            # Update job status
            job["status"] = "stopped"
            job["end_time"] = self.data_access.get_current_timestamp()
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.job.{job_id}"
            )
            
            # Publish job stop event
            self.event_bus.publish(
                topic="data_layer.ingestion.job",
                key=job_id,
                value={
                    "job_id": job_id,
                    "pipeline_id": job.get("pipeline_id"),
                    "source_id": job.get("source_id"),
                    "event_type": "job_stop",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Remove from active jobs
            del self._active_ingestion_jobs[job_id]
            
            # Update metrics
            self._metrics["active_ingestion_jobs"] = len(self._active_ingestion_jobs)
            
            self.logger.info(f"Stopped ingestion job {job_id}")
        except Exception as e:
            self.logger.error(f"Error stopping ingestion job {job_id}: {str(e)}")
            raise
