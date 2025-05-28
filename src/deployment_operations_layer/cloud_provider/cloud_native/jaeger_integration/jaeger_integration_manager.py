"""
Jaeger Integration Manager

This module provides integration with Jaeger for the Deployment Operations Layer.
It handles Jaeger tracing, service discovery, and query capabilities.

Classes:
    JaegerIntegrationManager: Manages Jaeger integration
    JaegerQueryManager: Manages Jaeger queries
    JaegerCollectorManager: Manages Jaeger collectors
    JaegerAgentManager: Manages Jaeger agents
    JaegerExecutor: Executes Jaeger API calls
"""

import json
import logging
import os
import subprocess
import tempfile
import yaml
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

from ....agent.agent_utils import AgentResponse
from ....protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class JaegerIntegrationManager:
    """
    Manages Jaeger integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Jaeger,
    handling tracing, service discovery, and query capabilities.
    """
    
    def __init__(self, jaeger_query_url: Optional[str] = None,
                jaeger_collector_url: Optional[str] = None,
                jaeger_agent_host: Optional[str] = None,
                jaeger_agent_port: Optional[int] = 6831,
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Jaeger Integration Manager.
        
        Args:
            jaeger_query_url: Jaeger Query URL (optional)
            jaeger_collector_url: Jaeger Collector URL (optional)
            jaeger_agent_host: Jaeger Agent host (optional)
            jaeger_agent_port: Jaeger Agent port (default: 6831)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Jaeger operations (optional)
        """
        self.jaeger_query_url = jaeger_query_url
        self.jaeger_collector_url = jaeger_collector_url
        self.jaeger_agent_host = jaeger_agent_host
        self.jaeger_agent_port = jaeger_agent_port
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="jaeger_")
        
        self.executor = JaegerExecutor(
            self.jaeger_query_url, 
            self.jaeger_collector_url,
            self.jaeger_agent_host,
            self.jaeger_agent_port,
            self.kubectl_binary, 
            self.working_dir
        )
        self.query_manager = JaegerQueryManager(self.executor)
        self.collector_manager = JaegerCollectorManager(self.executor)
        self.agent_manager = JaegerAgentManager(self.executor)
        
        # Verify Jaeger connectivity
        if self.jaeger_query_url:
            self._verify_jaeger_connectivity()
    
    def _verify_jaeger_connectivity(self):
        """
        Verify that Jaeger is accessible.
        
        Logs a warning if Jaeger is not accessible but does not raise an exception
        as Jaeger may be accessed via other means.
        """
        try:
            response = self.executor.make_jaeger_api_request("GET", "/api/services")
            if response.status_code == 200:
                logger.info("Jaeger server is accessible")
            else:
                logger.warning(f"Jaeger server returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Jaeger server is not accessible: {str(e)}")
    
    def get_services(self) -> AgentResponse:
        """
        Get all services registered with Jaeger.
        
        Returns:
            AgentResponse: Services response
        """
        try:
            if not self.jaeger_query_url:
                raise Exception("Jaeger Query URL not configured")
            
            result = self.query_manager.get_services()
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('data', []))} services from Jaeger",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get services from Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get services from Jaeger: {str(e)}",
                data={}
            )
    
    def get_operations(self, service: str) -> AgentResponse:
        """
        Get all operations for a service.
        
        Args:
            service: Service name
            
        Returns:
            AgentResponse: Operations response
        """
        try:
            if not self.jaeger_query_url:
                raise Exception("Jaeger Query URL not configured")
            
            result = self.query_manager.get_operations(service)
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('data', []))} operations for service {service} from Jaeger",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get operations for service {service} from Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get operations for service {service} from Jaeger: {str(e)}",
                data={}
            )
    
    def search_traces(self, service: str, 
                     operation: Optional[str] = None,
                     tags: Optional[Dict[str, str]] = None,
                     start_time: Optional[int] = None,
                     end_time: Optional[int] = None,
                     min_duration: Optional[str] = None,
                     max_duration: Optional[str] = None,
                     limit: int = 20) -> AgentResponse:
        """
        Search for traces.
        
        Args:
            service: Service name
            operation: Operation name (optional)
            tags: Tags to filter by (optional)
            start_time: Start time in microseconds (optional)
            end_time: End time in microseconds (optional)
            min_duration: Minimum duration (optional)
            max_duration: Maximum duration (optional)
            limit: Maximum number of traces to return (default: 20)
            
        Returns:
            AgentResponse: Traces response
        """
        try:
            if not self.jaeger_query_url:
                raise Exception("Jaeger Query URL not configured")
            
            result = self.query_manager.search_traces(
                service=service,
                operation=operation,
                tags=tags,
                start_time=start_time,
                end_time=end_time,
                min_duration=min_duration,
                max_duration=max_duration,
                limit=limit
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('data', []))} traces for service {service} from Jaeger",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to search traces for service {service} from Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to search traces for service {service} from Jaeger: {str(e)}",
                data={}
            )
    
    def get_trace(self, trace_id: str) -> AgentResponse:
        """
        Get a trace by ID.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            AgentResponse: Trace response
        """
        try:
            if not self.jaeger_query_url:
                raise Exception("Jaeger Query URL not configured")
            
            result = self.query_manager.get_trace(trace_id)
            
            return AgentResponse(
                success=True,
                message=f"Retrieved trace {trace_id} from Jaeger",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get trace {trace_id} from Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get trace {trace_id} from Jaeger: {str(e)}",
                data={}
            )
    
    def get_dependencies(self, start_time: Optional[int] = None,
                        end_time: Optional[int] = None) -> AgentResponse:
        """
        Get service dependencies.
        
        Args:
            start_time: Start time in microseconds (optional)
            end_time: End time in microseconds (optional)
            
        Returns:
            AgentResponse: Dependencies response
        """
        try:
            if not self.jaeger_query_url:
                raise Exception("Jaeger Query URL not configured")
            
            result = self.query_manager.get_dependencies(
                start_time=start_time,
                end_time=end_time
            )
            
            return AgentResponse(
                success=True,
                message=f"Retrieved service dependencies from Jaeger",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get service dependencies from Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get service dependencies from Jaeger: {str(e)}",
                data={}
            )
    
    def deploy_jaeger(self, namespace: str = "jaeger",
                     storage_type: str = "memory",
                     collector_replicas: int = 1,
                     query_replicas: int = 1,
                     agent_strategy: str = "daemonset") -> AgentResponse:
        """
        Deploy Jaeger to Kubernetes.
        
        Args:
            namespace: Kubernetes namespace (default: jaeger)
            storage_type: Storage type (default: memory)
            collector_replicas: Number of collector replicas (default: 1)
            query_replicas: Number of query replicas (default: 1)
            agent_strategy: Agent deployment strategy (default: daemonset)
            
        Returns:
            AgentResponse: Deployment response
        """
        try:
            # Create namespace if it doesn't exist
            try:
                self.executor.run_kubectl_command(["get", "namespace", namespace])
            except Exception:
                self.executor.run_kubectl_command(["create", "namespace", namespace])
            
            # Create Jaeger custom resource
            jaeger_cr = {
                "apiVersion": "jaegertracing.io/v1",
                "kind": "Jaeger",
                "metadata": {
                    "name": "jaeger",
                    "namespace": namespace
                },
                "spec": {
                    "strategy": "production",
                    "storage": {
                        "type": storage_type
                    },
                    "collector": {
                        "replicas": collector_replicas
                    },
                    "query": {
                        "replicas": query_replicas
                    },
                    "agent": {
                        "strategy": agent_strategy
                    }
                }
            }
            
            # Write Jaeger CR to file
            jaeger_cr_path = os.path.join(self.working_dir, "jaeger-cr.yaml")
            with open(jaeger_cr_path, "w") as f:
                yaml.dump(jaeger_cr, f)
            
            # Apply Jaeger CR
            self.executor.run_kubectl_command(["apply", "-f", jaeger_cr_path])
            
            # Wait for Jaeger to be ready
            self.executor.run_kubectl_command(["wait", "--for=condition=available", "deployment/jaeger-collector", "-n", namespace, "--timeout=300s"])
            self.executor.run_kubectl_command(["wait", "--for=condition=available", "deployment/jaeger-query", "-n", namespace, "--timeout=300s"])
            
            # Get Jaeger query service
            query_service = self.executor.run_kubectl_command(["get", "service", "jaeger-query", "-n", namespace, "-o", "jsonpath={.spec.clusterIP}"])
            
            return AgentResponse(
                success=True,
                message=f"Jaeger deployed successfully to namespace {namespace}",
                data={
                    "namespace": namespace,
                    "query_service": query_service.strip(),
                    "query_port": 16686,
                    "collector_port": 14268,
                    "agent_port": 6831
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to deploy Jaeger: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy Jaeger: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Jaeger integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Jaeger integration information
        """
        return MCPContext(
            context_type="jaeger_integration",
            jaeger_query_url=self.jaeger_query_url,
            jaeger_collector_url=self.jaeger_collector_url,
            jaeger_agent_host=self.jaeger_agent_host,
            jaeger_agent_port=self.jaeger_agent_port,
            working_dir=self.working_dir
        )


class JaegerQueryManager:
    """
    Manages Jaeger queries.
    
    This class provides methods for querying Jaeger for traces, services, and operations.
    """
    
    def __init__(self, executor: 'JaegerExecutor'):
        """
        Initialize the Jaeger Query Manager.
        
        Args:
            executor: Jaeger executor
        """
        self.executor = executor
    
    def get_services(self) -> Dict[str, Any]:
        """
        Get all services registered with Jaeger.
        
        Returns:
            Dict[str, Any]: Services information
        """
        # Get services
        response = self.executor.make_jaeger_api_request(
            "GET",
            "/api/services"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get services: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_operations(self, service: str) -> Dict[str, Any]:
        """
        Get all operations for a service.
        
        Args:
            service: Service name
            
        Returns:
            Dict[str, Any]: Operations information
        """
        # Get operations
        response = self.executor.make_jaeger_api_request(
            "GET",
            f"/api/services/{service}/operations"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get operations: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def search_traces(self, service: str, 
                     operation: Optional[str] = None,
                     tags: Optional[Dict[str, str]] = None,
                     start_time: Optional[int] = None,
                     end_time: Optional[int] = None,
                     min_duration: Optional[str] = None,
                     max_duration: Optional[str] = None,
                     limit: int = 20) -> Dict[str, Any]:
        """
        Search for traces.
        
        Args:
            service: Service name
            operation: Operation name (optional)
            tags: Tags to filter by (optional)
            start_time: Start time in microseconds (optional)
            end_time: End time in microseconds (optional)
            min_duration: Minimum duration (optional)
            max_duration: Maximum duration (optional)
            limit: Maximum number of traces to return (default: 20)
            
        Returns:
            Dict[str, Any]: Traces information
        """
        # Build query parameters
        params = {
            "service": service,
            "limit": limit
        }
        
        # Add optional parameters
        if operation:
            params["operation"] = operation
        
        if start_time:
            params["start"] = start_time
        
        if end_time:
            params["end"] = end_time
        
        if min_duration:
            params["minDuration"] = min_duration
        
        if max_duration:
            params["maxDuration"] = max_duration
        
        # Add tags
        if tags:
            for key, value in tags.items():
                params[f"tags[{key}]"] = value
        
        # Search traces
        response = self.executor.make_jaeger_api_request(
            "GET",
            "/api/traces",
            params=params
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to search traces: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """
        Get a trace by ID.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            Dict[str, Any]: Trace information
        """
        # Get trace
        response = self.executor.make_jaeger_api_request(
            "GET",
            f"/api/traces/{trace_id}"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get trace: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_dependencies(self, start_time: Optional[int] = None,
                        end_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Get service dependencies.
        
        Args:
            start_time: Start time in microseconds (optional)
            end_time: End time in microseconds (optional)
            
        Returns:
            Dict[str, Any]: Dependencies information
        """
        # Build query parameters
        params = {}
        
        # Add optional parameters
        if start_time:
            params["start"] = start_time
        
        if end_time:
            params["end"] = end_time
        
        # Get dependencies
        response = self.executor.make_jaeger_api_request(
            "GET",
            "/api/dependencies",
            params=params
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get dependencies: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class JaegerCollectorManager:
    """
    Manages Jaeger collectors.
    
    This class provides methods for managing Jaeger collectors,
    including sending spans and managing collector configuration.
    """
    
    def __init__(self, executor: 'JaegerExecutor'):
        """
        Initialize the Jaeger Collector Manager.
        
        Args:
            executor: Jaeger executor
        """
        self.executor = executor
    
    def send_spans(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send spans to the Jaeger collector.
        
        Args:
            spans: List of spans
            
        Returns:
            Dict[str, Any]: Span submission result
        """
        # Send spans
        response = self.executor.make_jaeger_collector_request(
            "POST",
            "/api/traces",
            json=spans
        )
        
        # Check response
        if response.status_code not in (200, 201, 202):
            raise Exception(f"Failed to send spans: {response.text}")
        
        # Parse response
        try:
            result = response.json()
        except Exception:
            result = {"status": "success"}
        
        return result
    
    def get_collector_status(self) -> Dict[str, Any]:
        """
        Get the status of the Jaeger collector.
        
        Returns:
            Dict[str, Any]: Collector status
        """
        # Get status
        response = self.executor.make_jaeger_collector_request(
            "GET",
            "/api/status"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get collector status: {response.text}")
        
        # Parse response
        try:
            result = response.json()
        except Exception:
            result = {"status": response.text}
        
        return result


class JaegerAgentManager:
    """
    Manages Jaeger agents.
    
    This class provides methods for managing Jaeger agents,
    including sending spans and managing agent configuration.
    """
    
    def __init__(self, executor: 'JaegerExecutor'):
        """
        Initialize the Jaeger Agent Manager.
        
        Args:
            executor: Jaeger executor
        """
        self.executor = executor
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of the Jaeger agent.
        
        Returns:
            Dict[str, Any]: Agent status
        """
        # Get status
        try:
            # Try to connect to agent's HTTP status endpoint
            response = requests.get(f"http://{self.executor.jaeger_agent_host}:14271/")
            
            # Check response
            if response.status_code != 200:
                return {"status": "error", "message": f"Agent returned status code {response.status_code}"}
            
            # Parse response
            try:
                result = response.json()
            except Exception:
                result = {"status": "success", "message": response.text}
            
            return result
        
        except Exception as e:
            return {"status": "error", "message": str(e)}


class JaegerExecutor:
    """
    Executes Jaeger API calls and kubectl commands.
    
    This class provides methods for executing Jaeger API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, jaeger_query_url: Optional[str],
                jaeger_collector_url: Optional[str],
                jaeger_agent_host: Optional[str],
                jaeger_agent_port: Optional[int],
                kubectl_binary: str,
                working_dir: str):
        """
        Initialize the Jaeger Executor.
        
        Args:
            jaeger_query_url: Jaeger Query URL
            jaeger_collector_url: Jaeger Collector URL
            jaeger_agent_host: Jaeger Agent host
            jaeger_agent_port: Jaeger Agent port
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Jaeger operations
        """
        self.jaeger_query_url = jaeger_query_url
        self.jaeger_collector_url = jaeger_collector_url
        self.jaeger_agent_host = jaeger_agent_host
        self.jaeger_agent_port = jaeger_agent_port
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def make_jaeger_api_request(self, method: str, 
                               endpoint: str,
                               params: Optional[Dict[str, Any]] = None,
                               json: Optional[Dict[str, Any]] = None,
                               data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a Jaeger Query API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters (optional)
            json: JSON body (optional)
            data: Form data (optional)
            
        Returns:
            requests.Response: API response
            
        Raises:
            Exception: If Jaeger Query URL is not configured
        """
        if not self.jaeger_query_url:
            raise Exception("Jaeger Query URL not configured")
        
        # Build URL
        url = f"{self.jaeger_query_url.rstrip('/')}{endpoint}"
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers
        )
        
        return response
    
    def make_jaeger_collector_request(self, method: str, 
                                     endpoint: str,
                                     params: Optional[Dict[str, Any]] = None,
                                     json: Optional[Dict[str, Any]] = None,
                                     data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a Jaeger Collector API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters (optional)
            json: JSON body (optional)
            data: Form data (optional)
            
        Returns:
            requests.Response: API response
            
        Raises:
            Exception: If Jaeger Collector URL is not configured
        """
        if not self.jaeger_collector_url:
            raise Exception("Jaeger Collector URL not configured")
        
        # Build URL
        url = f"{self.jaeger_collector_url.rstrip('/')}{endpoint}"
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers
        )
        
        return response
    
    def run_kubectl_command(self, args: List[str], check: bool = True) -> str:
        """
        Run a kubectl command.
        
        Args:
            args: Command arguments
            check: Whether to check for command success
            
        Returns:
            str: Command output
            
        Raises:
            Exception: If the command fails and check is True
        """
        cmd = [self.kubectl_binary] + args
        logger.info(f"Running kubectl command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                check=check
            )
            
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            error_message = f"kubectl command failed: {e.stderr}"
            logger.error(error_message)
            
            if check:
                raise Exception(error_message)
            
            return e.stderr
