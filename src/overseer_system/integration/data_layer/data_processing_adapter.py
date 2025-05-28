"""
Data Processing Adapter for the Overseer System.

This module provides the integration adapter for data processing components
of the Industriverse Data Layer, enabling seamless data processing and
transformation within the Overseer System.

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

class DataProcessingAdapter(BaseIntegrationAdapter):
    """
    Integration Adapter for Data Processing components of the Industriverse Data Layer.
    
    This class provides integration with data processing components, enabling
    seamless data processing and transformation within the Overseer System.
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
        Initialize the Data Processing Adapter.
        
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
        
        # Initialize data processing specific resources
        self._processors = {}
        self._processing_pipelines = {}
        self._active_processing_jobs = {}
        
        # Initialize metrics
        self._metrics = {
            "total_processed_records": 0,
            "total_processing_errors": 0,
            "active_processing_jobs": 0,
            "last_processing_timestamp": None
        }
        
        self.logger.info(f"Data Processing Adapter {adapter_id} initialized")
    
    def _get_supported_context_types(self) -> List[str]:
        """
        Get the MCP context types supported by this adapter.
        
        Returns:
            List of supported context types
        """
        return [
            "data_layer.processing",
            "data_layer.processing.processor",
            "data_layer.processing.pipeline",
            "data_layer.processing.job"
        ]
    
    def _get_supported_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the A2A capabilities supported by this adapter.
        
        Returns:
            List of supported capabilities
        """
        return [
            {
                "type": "data_processing",
                "description": "Process data using various transformations",
                "parameters": {
                    "processing_type": {
                        "type": "string",
                        "description": "Type of data processing (e.g., transform, filter, aggregate, enrich)"
                    },
                    "processing_config": {
                        "type": "object",
                        "description": "Configuration for the data processing"
                    },
                    "pipeline_id": {
                        "type": "string",
                        "description": "ID of the processing pipeline to use"
                    }
                }
            },
            {
                "type": "processor_management",
                "description": "Manage data processors",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "processor_id": {
                        "type": "string",
                        "description": "ID of the data processor"
                    },
                    "processor_config": {
                        "type": "object",
                        "description": "Configuration for the data processor"
                    }
                }
            },
            {
                "type": "processing_pipeline_management",
                "description": "Manage data processing pipelines",
                "parameters": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform (create, update, delete, list)"
                    },
                    "pipeline_id": {
                        "type": "string",
                        "description": "ID of the processing pipeline"
                    },
                    "pipeline_config": {
                        "type": "object",
                        "description": "Configuration for the processing pipeline"
                    }
                }
            }
        ]
    
    def _initialize_resources(self) -> None:
        """Initialize adapter-specific resources."""
        try:
            # Load processors from configuration
            processors_config = self.config.get("processors", {})
            for processor_id, processor_config in processors_config.items():
                self._create_processor(processor_id, processor_config)
            
            # Load processing pipelines from configuration
            processing_pipelines_config = self.config.get("processing_pipelines", {})
            for pipeline_id, pipeline_config in processing_pipelines_config.items():
                self._create_processing_pipeline(pipeline_id, pipeline_config)
            
            self.logger.info(f"Initialized resources for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error initializing resources for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _start_resources(self) -> None:
        """Start adapter-specific resources."""
        try:
            # Start auto-start processing pipelines
            for pipeline_id, pipeline in self._processing_pipelines.items():
                if pipeline.get("auto_start", False):
                    self._start_processing_pipeline(pipeline_id)
            
            self.logger.info(f"Started resources for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error starting resources for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _stop_resources(self) -> None:
        """Stop adapter-specific resources."""
        try:
            # Stop all active processing jobs
            for job_id in list(self._active_processing_jobs.keys()):
                self._stop_processing_job(job_id)
            
            self.logger.info(f"Stopped resources for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error stopping resources for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _release_resources(self) -> None:
        """Release adapter-specific resources."""
        try:
            # Clear all resources
            self._processors = {}
            self._processing_pipelines = {}
            self._active_processing_jobs = {}
            
            self.logger.info(f"Released resources for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error releasing resources for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _check_resource_health(self) -> str:
        """
        Check the health of adapter-specific resources.
        
        Returns:
            Health status string: "healthy", "degraded", or "unhealthy"
        """
        try:
            # Check processors
            unhealthy_processors = 0
            for processor_id, processor in self._processors.items():
                if processor.get("status") == "error":
                    unhealthy_processors += 1
            
            # Check processing pipelines
            unhealthy_pipelines = 0
            for pipeline_id, pipeline in self._processing_pipelines.items():
                if pipeline.get("status") == "error":
                    unhealthy_pipelines += 1
            
            # Check active processing jobs
            unhealthy_jobs = 0
            for job_id, job in self._active_processing_jobs.items():
                if job.get("status") == "error":
                    unhealthy_jobs += 1
            
            # Determine overall health
            total_processors = len(self._processors)
            total_pipelines = len(self._processing_pipelines)
            total_jobs = len(self._active_processing_jobs)
            
            if unhealthy_processors > 0 or unhealthy_pipelines > 0 or unhealthy_jobs > 0:
                # At least one component is unhealthy
                if (unhealthy_processors / max(total_processors, 1) > 0.5 or
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
            self.logger.error(f"Error checking resource health for Data Processing Adapter {self.adapter_id}: {str(e)}")
            return "unhealthy"
    
    def _apply_configuration(self) -> None:
        """Apply configuration changes."""
        try:
            # Apply processor configuration changes
            processors_config = self.config.get("processors", {})
            
            # Remove deleted processors
            for processor_id in list(self._processors.keys()):
                if processor_id not in processors_config:
                    self._delete_processor(processor_id)
            
            # Add or update processors
            for processor_id, processor_config in processors_config.items():
                if processor_id in self._processors:
                    self._update_processor(processor_id, processor_config)
                else:
                    self._create_processor(processor_id, processor_config)
            
            # Apply processing pipeline configuration changes
            processing_pipelines_config = self.config.get("processing_pipelines", {})
            
            # Remove deleted processing pipelines
            for pipeline_id in list(self._processing_pipelines.keys()):
                if pipeline_id not in processing_pipelines_config:
                    self._delete_processing_pipeline(pipeline_id)
            
            # Add or update processing pipelines
            for pipeline_id, pipeline_config in processing_pipelines_config.items():
                if pipeline_id in self._processing_pipelines:
                    self._update_processing_pipeline(pipeline_id, pipeline_config)
                else:
                    self._create_processing_pipeline(pipeline_id, pipeline_config)
            
            self.logger.info(f"Applied configuration changes for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error applying configuration changes for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _get_status_data(self) -> Dict[str, Any]:
        """
        Get adapter-specific status data.
        
        Returns:
            Adapter-specific status data
        """
        return {
            "processors": {
                processor_id: {
                    "type": processor.get("type"),
                    "status": processor.get("status")
                }
                for processor_id, processor in self._processors.items()
            },
            "processing_pipelines": {
                pipeline_id: {
                    "status": pipeline.get("status"),
                    "processor_ids": pipeline.get("processor_ids", [])
                }
                for pipeline_id, pipeline in self._processing_pipelines.items()
            },
            "active_processing_jobs": {
                job_id: {
                    "pipeline_id": job.get("pipeline_id"),
                    "status": job.get("status"),
                    "start_time": job.get("start_time"),
                    "records_processed": job.get("records_processed", 0),
                    "errors": job.get("errors", 0)
                }
                for job_id, job in self._active_processing_jobs.items()
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
        if command == "create_processor":
            processor_id = event.get("processor_id", str(uuid.uuid4()))
            processor_config = event.get("processor_config", {})
            self._create_processor(processor_id, processor_config)
            return {"processor_id": processor_id}
        
        elif command == "update_processor":
            processor_id = event.get("processor_id")
            processor_config = event.get("processor_config", {})
            if not processor_id:
                raise ValueError("processor_id is required")
            self._update_processor(processor_id, processor_config)
            return {"processor_id": processor_id}
        
        elif command == "delete_processor":
            processor_id = event.get("processor_id")
            if not processor_id:
                raise ValueError("processor_id is required")
            self._delete_processor(processor_id)
            return {"processor_id": processor_id}
        
        elif command == "list_processors":
            return {
                "processors": {
                    processor_id: {
                        "type": processor.get("type"),
                        "status": processor.get("status")
                    }
                    for processor_id, processor in self._processors.items()
                }
            }
        
        elif command == "create_processing_pipeline":
            pipeline_id = event.get("pipeline_id", str(uuid.uuid4()))
            pipeline_config = event.get("pipeline_config", {})
            self._create_processing_pipeline(pipeline_id, pipeline_config)
            return {"pipeline_id": pipeline_id}
        
        elif command == "update_processing_pipeline":
            pipeline_id = event.get("pipeline_id")
            pipeline_config = event.get("pipeline_config", {})
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            self._update_processing_pipeline(pipeline_id, pipeline_config)
            return {"pipeline_id": pipeline_id}
        
        elif command == "delete_processing_pipeline":
            pipeline_id = event.get("pipeline_id")
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            self._delete_processing_pipeline(pipeline_id)
            return {"pipeline_id": pipeline_id}
        
        elif command == "list_processing_pipelines":
            return {
                "processing_pipelines": {
                    pipeline_id: {
                        "status": pipeline.get("status"),
                        "processor_ids": pipeline.get("processor_ids", [])
                    }
                    for pipeline_id, pipeline in self._processing_pipelines.items()
                }
            }
        
        elif command == "start_processing_pipeline":
            pipeline_id = event.get("pipeline_id")
            input_data = event.get("input_data")
            if not pipeline_id:
                raise ValueError("pipeline_id is required")
            job_id = self._start_processing_pipeline(pipeline_id, input_data)
            return {"job_id": job_id, "pipeline_id": pipeline_id}
        
        elif command == "stop_processing_job":
            job_id = event.get("job_id")
            if not job_id:
                raise ValueError("job_id is required")
            self._stop_processing_job(job_id)
            return {"job_id": job_id}
        
        elif command == "list_processing_jobs":
            return {
                "active_processing_jobs": {
                    job_id: {
                        "pipeline_id": job.get("pipeline_id"),
                        "status": job.get("status"),
                        "start_time": job.get("start_time"),
                        "records_processed": job.get("records_processed", 0),
                        "errors": job.get("errors", 0)
                    }
                    for job_id, job in self._active_processing_jobs.items()
                }
            }
        
        elif command == "get_metrics":
            return {"metrics": self._metrics}
        
        elif command == "reset_metrics":
            self._metrics = {
                "total_processed_records": 0,
                "total_processing_errors": 0,
                "active_processing_jobs": 0,
                "last_processing_timestamp": None
            }
            return {"metrics": self._metrics}
        
        else:
            raise ValueError(f"Unsupported command: {command}")
    
    def _subscribe_to_additional_events(self) -> None:
        """Subscribe to additional events specific to this adapter."""
        try:
            # Subscribe to data processing events
            self.event_bus.subscribe(
                topic="data_layer.processing.event",
                group_id=f"{self.adapter_id}-processing-event-handler",
                callback=self._handle_processing_event
            )
            
            self.logger.info(f"Subscribed to additional events for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error subscribing to additional events for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _unsubscribe_from_additional_events(self) -> None:
        """Unsubscribe from additional events specific to this adapter."""
        try:
            # Unsubscribe from data processing events
            self.event_bus.unsubscribe(
                topic="data_layer.processing.event",
                group_id=f"{self.adapter_id}-processing-event-handler"
            )
            
            self.logger.info(f"Unsubscribed from additional events for Data Processing Adapter {self.adapter_id}")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from additional events for Data Processing Adapter {self.adapter_id}: {str(e)}")
            raise
    
    def _handle_processing_event(self, event: Dict[str, Any]) -> None:
        """
        Handle data processing events.
        
        Args:
            event: Event data
        """
        try:
            event_type = event.get("event_type")
            
            if event_type == "processing_complete":
                job_id = event.get("job_id")
                records_processed = event.get("records_processed", 0)
                errors = event.get("errors", 0)
                
                # Update metrics
                self._metrics["total_processed_records"] += records_processed
                self._metrics["total_processing_errors"] += errors
                self._metrics["last_processing_timestamp"] = self.data_access.get_current_timestamp()
                
                # Update job status
                if job_id in self._active_processing_jobs:
                    job = self._active_processing_jobs[job_id]
                    job["status"] = "completed"
                    job["records_processed"] = records_processed
                    job["errors"] = errors
                    job["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active jobs
                    del self._active_processing_jobs[job_id]
                    self._metrics["active_processing_jobs"] = len(self._active_processing_jobs)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("data_processing_count", records_processed)
                
                self.logger.info(f"Processing job {job_id} completed: {records_processed} records processed, {errors} errors")
            
            elif event_type == "processing_error":
                job_id = event.get("job_id")
                error = event.get("error")
                
                # Update metrics
                self._metrics["total_processing_errors"] += 1
                
                # Update job status
                if job_id in self._active_processing_jobs:
                    job = self._active_processing_jobs[job_id]
                    job["status"] = "error"
                    job["error"] = error
                    job["end_time"] = self.data_access.get_current_timestamp()
                    
                    # Remove from active jobs
                    del self._active_processing_jobs[job_id]
                    self._metrics["active_processing_jobs"] = len(self._active_processing_jobs)
                
                # Notify manager
                if hasattr(self.manager, "update_metrics"):
                    self.manager.update_metrics("error_count", 1)
                
                self.logger.error(f"Processing job {job_id} error: {error}")
            
            elif event_type == "processing_progress":
                job_id = event.get("job_id")
                records_processed = event.get("records_processed", 0)
                errors = event.get("errors", 0)
                
                # Update job status
                if job_id in self._active_processing_jobs:
                    job = self._active_processing_jobs[job_id]
                    job["records_processed"] = records_processed
                    job["errors"] = errors
                
                self.logger.debug(f"Processing job {job_id} progress: {records_processed} records processed, {errors} errors")
        except Exception as e:
            self.logger.error(f"Error handling processing event: {str(e)}")
    
    def _create_processor(self, processor_id: str, processor_config: Dict[str, Any]) -> None:
        """
        Create a new processor.
        
        Args:
            processor_id: Processor ID
            processor_config: Processor configuration
        """
        try:
            # Validate processor configuration
            processor_type = processor_config.get("type")
            if not processor_type:
                raise ValueError("Processor type is required")
            
            # Create processor
            self._processors[processor_id] = {
                "id": processor_id,
                "type": processor_type,
                "config": processor_config,
                "status": "initialized"
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.processor.{processor_id}",
                provider_name=f"Data Processor: {processor_id}",
                provider_type="data_processor",
                context_types=[
                    "data_layer.processing.processor",
                    f"data_layer.processing.processor.{processor_type}"
                ]
            )
            
            # Save to configuration
            self.config["processors"] = self.config.get("processors", {})
            self.config["processors"][processor_id] = processor_config
            
            self.logger.info(f"Created processor {processor_id} of type {processor_type}")
        except Exception as e:
            self.logger.error(f"Error creating processor {processor_id}: {str(e)}")
            raise
    
    def _update_processor(self, processor_id: str, processor_config: Dict[str, Any]) -> None:
        """
        Update an existing processor.
        
        Args:
            processor_id: Processor ID
            processor_config: Processor configuration
        """
        try:
            # Check if processor exists
            if processor_id not in self._processors:
                raise ValueError(f"Processor {processor_id} does not exist")
            
            # Validate processor configuration
            processor_type = processor_config.get("type")
            if not processor_type:
                raise ValueError("Processor type is required")
            
            # Update processor
            self._processors[processor_id]["type"] = processor_type
            self._processors[processor_id]["config"] = processor_config
            self._processors[processor_id]["status"] = "initialized"
            
            # Update MCP registration if type changed
            if self._processors[processor_id]["type"] != processor_type:
                # Unregister old context provider
                self.mcp_bridge.unregister_context_provider(
                    provider_id=f"{self.adapter_id}.processor.{processor_id}"
                )
                
                # Register new context provider
                self.mcp_bridge.register_context_provider(
                    provider_id=f"{self.adapter_id}.processor.{processor_id}",
                    provider_name=f"Data Processor: {processor_id}",
                    provider_type="data_processor",
                    context_types=[
                        "data_layer.processing.processor",
                        f"data_layer.processing.processor.{processor_type}"
                    ]
                )
            
            # Save to configuration
            self.config["processors"] = self.config.get("processors", {})
            self.config["processors"][processor_id] = processor_config
            
            self.logger.info(f"Updated processor {processor_id} of type {processor_type}")
        except Exception as e:
            self.logger.error(f"Error updating processor {processor_id}: {str(e)}")
            raise
    
    def _delete_processor(self, processor_id: str) -> None:
        """
        Delete a processor.
        
        Args:
            processor_id: Processor ID
        """
        try:
            # Check if processor exists
            if processor_id not in self._processors:
                raise ValueError(f"Processor {processor_id} does not exist")
            
            # Check if processor is used by any pipeline
            for pipeline_id, pipeline in self._processing_pipelines.items():
                if processor_id in pipeline.get("processor_ids", []):
                    raise ValueError(f"Processor {processor_id} is used by pipeline {pipeline_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.processor.{processor_id}"
            )
            
            # Delete processor
            del self._processors[processor_id]
            
            # Remove from configuration
            if "processors" in self.config and processor_id in self.config["processors"]:
                del self.config["processors"][processor_id]
            
            self.logger.info(f"Deleted processor {processor_id}")
        except Exception as e:
            self.logger.error(f"Error deleting processor {processor_id}: {str(e)}")
            raise
    
    def _create_processing_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> None:
        """
        Create a new processing pipeline.
        
        Args:
            pipeline_id: Processing pipeline ID
            pipeline_config: Processing pipeline configuration
        """
        try:
            # Validate pipeline configuration
            processor_ids = pipeline_config.get("processor_ids", [])
            if not processor_ids:
                raise ValueError("At least one processor ID is required")
            
            # Check if processors exist
            for processor_id in processor_ids:
                if processor_id not in self._processors:
                    raise ValueError(f"Processor {processor_id} does not exist")
            
            # Create processing pipeline
            self._processing_pipelines[pipeline_id] = {
                "id": pipeline_id,
                "processor_ids": processor_ids,
                "config": pipeline_config,
                "status": "initialized",
                "auto_start": pipeline_config.get("auto_start", False)
            }
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.pipeline.{pipeline_id}",
                provider_name=f"Processing Pipeline: {pipeline_id}",
                provider_type="processing_pipeline",
                context_types=[
                    "data_layer.processing.pipeline"
                ]
            )
            
            # Save to configuration
            self.config["processing_pipelines"] = self.config.get("processing_pipelines", {})
            self.config["processing_pipelines"][pipeline_id] = pipeline_config
            
            self.logger.info(f"Created processing pipeline {pipeline_id} with processors {processor_ids}")
        except Exception as e:
            self.logger.error(f"Error creating processing pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _update_processing_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> None:
        """
        Update an existing processing pipeline.
        
        Args:
            pipeline_id: Processing pipeline ID
            pipeline_config: Processing pipeline configuration
        """
        try:
            # Check if processing pipeline exists
            if pipeline_id not in self._processing_pipelines:
                raise ValueError(f"Processing pipeline {pipeline_id} does not exist")
            
            # Validate pipeline configuration
            processor_ids = pipeline_config.get("processor_ids", [])
            if not processor_ids:
                raise ValueError("At least one processor ID is required")
            
            # Check if processors exist
            for processor_id in processor_ids:
                if processor_id not in self._processors:
                    raise ValueError(f"Processor {processor_id} does not exist")
            
            # Update processing pipeline
            self._processing_pipelines[pipeline_id]["processor_ids"] = processor_ids
            self._processing_pipelines[pipeline_id]["config"] = pipeline_config
            self._processing_pipelines[pipeline_id]["status"] = "initialized"
            self._processing_pipelines[pipeline_id]["auto_start"] = pipeline_config.get("auto_start", False)
            
            # Save to configuration
            self.config["processing_pipelines"] = self.config.get("processing_pipelines", {})
            self.config["processing_pipelines"][pipeline_id] = pipeline_config
            
            self.logger.info(f"Updated processing pipeline {pipeline_id} with processors {processor_ids}")
        except Exception as e:
            self.logger.error(f"Error updating processing pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _delete_processing_pipeline(self, pipeline_id: str) -> None:
        """
        Delete a processing pipeline.
        
        Args:
            pipeline_id: Processing pipeline ID
        """
        try:
            # Check if processing pipeline exists
            if pipeline_id not in self._processing_pipelines:
                raise ValueError(f"Processing pipeline {pipeline_id} does not exist")
            
            # Check if processing pipeline is running
            for job_id, job in self._active_processing_jobs.items():
                if job.get("pipeline_id") == pipeline_id:
                    raise ValueError(f"Processing pipeline {pipeline_id} has active job {job_id}")
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.pipeline.{pipeline_id}"
            )
            
            # Delete processing pipeline
            del self._processing_pipelines[pipeline_id]
            
            # Remove from configuration
            if "processing_pipelines" in self.config and pipeline_id in self.config["processing_pipelines"]:
                del self.config["processing_pipelines"][pipeline_id]
            
            self.logger.info(f"Deleted processing pipeline {pipeline_id}")
        except Exception as e:
            self.logger.error(f"Error deleting processing pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _start_processing_pipeline(self, pipeline_id: str, input_data: Optional[Any] = None) -> str:
        """
        Start a processing pipeline.
        
        Args:
            pipeline_id: Processing pipeline ID
            input_data: Optional input data for the pipeline
        
        Returns:
            Job ID
        """
        try:
            # Check if processing pipeline exists
            if pipeline_id not in self._processing_pipelines:
                raise ValueError(f"Processing pipeline {pipeline_id} does not exist")
            
            # Create job ID
            job_id = str(uuid.uuid4())
            
            # Get pipeline
            pipeline = self._processing_pipelines[pipeline_id]
            processor_ids = pipeline.get("processor_ids", [])
            
            # Create processing job
            self._active_processing_jobs[job_id] = {
                "id": job_id,
                "pipeline_id": pipeline_id,
                "processor_ids": processor_ids,
                "status": "running",
                "start_time": self.data_access.get_current_timestamp(),
                "records_processed": 0,
                "errors": 0,
                "input_data": input_data
            }
            
            # Update metrics
            self._metrics["active_processing_jobs"] = len(self._active_processing_jobs)
            
            # Register with MCP
            self.mcp_bridge.register_context_provider(
                provider_id=f"{self.adapter_id}.job.{job_id}",
                provider_name=f"Processing Job: {job_id}",
                provider_type="processing_job",
                context_types=[
                    "data_layer.processing.job"
                ]
            )
            
            # Publish job start event
            self.event_bus.publish(
                topic="data_layer.processing.job",
                key=job_id,
                value={
                    "job_id": job_id,
                    "pipeline_id": pipeline_id,
                    "processor_ids": processor_ids,
                    "event_type": "job_start",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Start processing job (simulated for now)
            # In a real implementation, this would start an actual processing process
            # For now, we'll simulate it with a simple event
            self.event_bus.publish(
                topic="data_layer.processing.event",
                key=job_id,
                value={
                    "event_type": "processing_complete",
                    "job_id": job_id,
                    "records_processed": 100,  # Simulated value
                    "errors": 0,
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            self.logger.info(f"Started processing pipeline {pipeline_id} with job {job_id}")
            
            return job_id
        except Exception as e:
            self.logger.error(f"Error starting processing pipeline {pipeline_id}: {str(e)}")
            raise
    
    def _stop_processing_job(self, job_id: str) -> None:
        """
        Stop a processing job.
        
        Args:
            job_id: Processing job ID
        """
        try:
            # Check if processing job exists
            if job_id not in self._active_processing_jobs:
                raise ValueError(f"Processing job {job_id} does not exist")
            
            # Get job
            job = self._active_processing_jobs[job_id]
            
            # Update job status
            job["status"] = "stopped"
            job["end_time"] = self.data_access.get_current_timestamp()
            
            # Unregister from MCP
            self.mcp_bridge.unregister_context_provider(
                provider_id=f"{self.adapter_id}.job.{job_id}"
            )
            
            # Publish job stop event
            self.event_bus.publish(
                topic="data_layer.processing.job",
                key=job_id,
                value={
                    "job_id": job_id,
                    "pipeline_id": job.get("pipeline_id"),
                    "processor_ids": job.get("processor_ids", []),
                    "event_type": "job_stop",
                    "timestamp": self.data_access.get_current_timestamp()
                }
            )
            
            # Remove from active jobs
            del self._active_processing_jobs[job_id]
            
            # Update metrics
            self._metrics["active_processing_jobs"] = len(self._active_processing_jobs)
            
            self.logger.info(f"Stopped processing job {job_id}")
        except Exception as e:
            self.logger.error(f"Error stopping processing job {job_id}: {str(e)}")
            raise
