"""
Prometheus Integration Manager

This module provides integration with Prometheus for the Deployment Operations Layer.
It handles Prometheus monitoring, alerting, and metrics collection.

Classes:
    PrometheusIntegrationManager: Manages Prometheus integration
    PrometheusRuleManager: Manages Prometheus alerting rules
    PrometheusServiceMonitorManager: Manages Prometheus service monitors
    PrometheusExecutor: Executes Prometheus API calls
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

class PrometheusIntegrationManager:
    """
    Manages Prometheus integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Prometheus,
    handling monitoring, alerting, and metrics collection.
    """
    
    def __init__(self, prometheus_url: Optional[str] = None,
                alertmanager_url: Optional[str] = None,
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Prometheus Integration Manager.
        
        Args:
            prometheus_url: Prometheus server URL (optional)
            alertmanager_url: Alertmanager URL (optional)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Prometheus operations (optional)
        """
        self.prometheus_url = prometheus_url
        self.alertmanager_url = alertmanager_url
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="prometheus_")
        
        self.executor = PrometheusExecutor(self.prometheus_url, self.alertmanager_url, self.kubectl_binary, self.working_dir)
        self.rule_manager = PrometheusRuleManager(self.executor)
        self.service_monitor_manager = PrometheusServiceMonitorManager(self.executor)
        
        # Verify Prometheus connectivity
        if self.prometheus_url:
            self._verify_prometheus_connectivity()
    
    def _verify_prometheus_connectivity(self):
        """
        Verify that Prometheus is accessible.
        
        Logs a warning if Prometheus is not accessible but does not raise an exception
        as Prometheus may be accessed via other means.
        """
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                logger.info("Prometheus server is accessible")
            else:
                logger.warning(f"Prometheus server returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Prometheus server is not accessible: {str(e)}")
    
    def create_service_monitor(self, name: str, 
                              namespace: str,
                              selector: Dict[str, str],
                              port: str,
                              path: str = "/metrics",
                              interval: str = "30s",
                              labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a Prometheus service monitor.
        
        Args:
            name: Service monitor name
            namespace: Namespace
            selector: Label selector for services
            port: Port name or number
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            AgentResponse: Service monitor creation response
        """
        try:
            result = self.service_monitor_manager.create_service_monitor(
                name=name,
                namespace=namespace,
                selector=selector,
                port=port,
                path=path,
                interval=interval,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"Prometheus service monitor {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Prometheus service monitor: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Prometheus service monitor: {str(e)}",
                data={}
            )
    
    def create_prometheus_rule(self, name: str, 
                              namespace: str,
                              rules: List[Dict[str, Any]],
                              labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a Prometheus rule.
        
        Args:
            name: Rule name
            namespace: Namespace
            rules: List of rules
            labels: Additional labels (optional)
            
        Returns:
            AgentResponse: Rule creation response
        """
        try:
            result = self.rule_manager.create_prometheus_rule(
                name=name,
                namespace=namespace,
                rules=rules,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"Prometheus rule {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Prometheus rule: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Prometheus rule: {str(e)}",
                data={}
            )
    
    def query_prometheus(self, query: str, 
                        time: Optional[str] = None,
                        timeout: Optional[str] = None) -> AgentResponse:
        """
        Query Prometheus.
        
        Args:
            query: PromQL query
            time: Query time (optional)
            timeout: Query timeout (optional)
            
        Returns:
            AgentResponse: Query response
        """
        try:
            if not self.prometheus_url:
                raise Exception("Prometheus URL not configured")
            
            result = self.executor.query_prometheus(
                query=query,
                time=time,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Prometheus query executed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to query Prometheus: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to query Prometheus: {str(e)}",
                data={}
            )
    
    def query_prometheus_range(self, query: str, 
                              start: str,
                              end: str,
                              step: str,
                              timeout: Optional[str] = None) -> AgentResponse:
        """
        Query Prometheus range.
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Step interval
            timeout: Query timeout (optional)
            
        Returns:
            AgentResponse: Query response
        """
        try:
            if not self.prometheus_url:
                raise Exception("Prometheus URL not configured")
            
            result = self.executor.query_prometheus_range(
                query=query,
                start=start,
                end=end,
                step=step,
                timeout=timeout
            )
            
            return AgentResponse(
                success=True,
                message=f"Prometheus range query executed successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to query Prometheus range: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to query Prometheus range: {str(e)}",
                data={}
            )
    
    def get_alerts(self) -> AgentResponse:
        """
        Get Prometheus alerts.
        
        Returns:
            AgentResponse: Alerts response
        """
        try:
            if not self.prometheus_url:
                raise Exception("Prometheus URL not configured")
            
            result = self.executor.get_alerts()
            
            return AgentResponse(
                success=True,
                message=f"Retrieved {len(result.get('alerts', []))} Prometheus alerts",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Prometheus alerts: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Prometheus alerts: {str(e)}",
                data={}
            )
    
    def get_targets(self) -> AgentResponse:
        """
        Get Prometheus targets.
        
        Returns:
            AgentResponse: Targets response
        """
        try:
            if not self.prometheus_url:
                raise Exception("Prometheus URL not configured")
            
            result = self.executor.get_targets()
            
            return AgentResponse(
                success=True,
                message=f"Retrieved Prometheus targets",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to get Prometheus targets: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to get Prometheus targets: {str(e)}",
                data={}
            )
    
    def create_alert_manager_config(self, name: str, 
                                   namespace: str,
                                   receivers: List[Dict[str, Any]],
                                   route: Dict[str, Any],
                                   inhibit_rules: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        """
        Create an Alertmanager configuration.
        
        Args:
            name: Config name
            namespace: Namespace
            receivers: List of receivers
            route: Routing configuration
            inhibit_rules: List of inhibit rules (optional)
            
        Returns:
            AgentResponse: Config creation response
        """
        try:
            # Create Alertmanager config
            alertmanager_config = {
                "receivers": receivers,
                "route": route
            }
            
            # Add inhibit rules if provided
            if inhibit_rules:
                alertmanager_config["inhibit_rules"] = inhibit_rules
            
            # Create Secret manifest
            secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": name,
                    "namespace": namespace
                },
                "type": "Opaque",
                "stringData": {
                    "alertmanager.yaml": yaml.dump(alertmanager_config)
                }
            }
            
            # Write Secret to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(secret, f)
                secret_file = f.name
            
            try:
                # Apply Secret
                output = self.executor.run_kubectl_command([
                    "apply", "-f", secret_file
                ])
                
                return AgentResponse(
                    success=True,
                    message=f"Alertmanager config {name} created successfully",
                    data={
                        "name": name,
                        "namespace": namespace,
                        "receivers": receivers,
                        "route": route,
                        "inhibit_rules": inhibit_rules,
                        "output": output
                    }
                )
            
            finally:
                # Clean up temporary file
                if os.path.exists(secret_file):
                    os.unlink(secret_file)
        
        except Exception as e:
            logger.error(f"Failed to create Alertmanager config: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Alertmanager config: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Prometheus integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Prometheus integration information
        """
        return MCPContext(
            context_type="prometheus_integration",
            prometheus_url=self.prometheus_url,
            alertmanager_url=self.alertmanager_url,
            prometheus_version=self._get_prometheus_version(),
            working_dir=self.working_dir
        )
    
    def _get_prometheus_version(self) -> str:
        """
        Get the Prometheus version.
        
        Returns:
            str: Prometheus version
        """
        try:
            if not self.prometheus_url:
                return "unknown"
            
            response = requests.get(f"{self.prometheus_url}/api/v1/status/buildinfo", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("version", "unknown")
            else:
                logger.error(f"Failed to get Prometheus version: {response.status_code}")
                return "unknown"
        except Exception as e:
            logger.error(f"Failed to get Prometheus version: {str(e)}")
            return "unknown"


class PrometheusRuleManager:
    """
    Manages Prometheus rules.
    
    This class provides methods for managing Prometheus rules,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'PrometheusExecutor'):
        """
        Initialize the Prometheus Rule Manager.
        
        Args:
            executor: Prometheus executor
        """
        self.executor = executor
    
    def create_prometheus_rule(self, name: str, 
                              namespace: str,
                              rules: List[Dict[str, Any]],
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Prometheus rule.
        
        Args:
            name: Rule name
            namespace: Namespace
            rules: List of rules
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Rule creation result
        """
        # Create rule manifest
        prometheus_rule = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PrometheusRule",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "groups": [
                    {
                        "name": f"{name}-rules",
                        "rules": rules
                    }
                ]
            }
        }
        
        # Add labels if provided
        if labels:
            prometheus_rule["metadata"]["labels"] = labels
        
        # Write rule to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(prometheus_rule, f)
            rule_file = f.name
        
        try:
            # Apply rule
            output = self.executor.run_kubectl_command([
                "apply", "-f", rule_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "rules": rules,
                "labels": labels,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(rule_file):
                os.unlink(rule_file)
    
    def get_prometheus_rule(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Prometheus rule.
        
        Args:
            name: Rule name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Rule information
        """
        output = self.executor.run_kubectl_command([
            "get", "prometheusrule", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            rule_json = json.loads(output)
            
            return {
                "name": rule_json["metadata"]["name"],
                "namespace": rule_json["metadata"]["namespace"],
                "labels": rule_json["metadata"].get("labels", {}),
                "groups": rule_json["spec"].get("groups", []),
                "created_at": rule_json["metadata"].get("creationTimestamp")
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse rule information: {str(e)}")
            return {
                "name": name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def list_prometheus_rules(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List Prometheus rules.
        
        Args:
            namespace: Namespace (optional)
            
        Returns:
            List[Dict[str, Any]]: List of rules
        """
        # Build command
        cmd = ["get", "prometheusrules"]
        
        # Add namespace if provided
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")
        
        # Add output format
        cmd.extend(["-o", "json"])
        
        # Get rules
        output = self.executor.run_kubectl_command(cmd)
        
        try:
            rules_json = json.loads(output)
            
            rules = []
            for rule in rules_json.get("items", []):
                rule_info = {
                    "name": rule["metadata"]["name"],
                    "namespace": rule["metadata"]["namespace"],
                    "labels": rule["metadata"].get("labels", {}),
                    "groups": len(rule["spec"].get("groups", [])),
                    "created_at": rule["metadata"].get("creationTimestamp")
                }
                rules.append(rule_info)
            
            return rules
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse rule list: {str(e)}")
            return []


class PrometheusServiceMonitorManager:
    """
    Manages Prometheus service monitors.
    
    This class provides methods for managing Prometheus service monitors,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'PrometheusExecutor'):
        """
        Initialize the Prometheus Service Monitor Manager.
        
        Args:
            executor: Prometheus executor
        """
        self.executor = executor
    
    def create_service_monitor(self, name: str, 
                              namespace: str,
                              selector: Dict[str, str],
                              port: str,
                              path: str = "/metrics",
                              interval: str = "30s",
                              labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Prometheus service monitor.
        
        Args:
            name: Service monitor name
            namespace: Namespace
            selector: Label selector for services
            port: Port name or number
            path: Metrics path (default: /metrics)
            interval: Scrape interval (default: 30s)
            labels: Additional labels (optional)
            
        Returns:
            Dict[str, Any]: Service monitor creation result
        """
        # Create service monitor manifest
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": selector
                },
                "endpoints": [
                    {
                        "port": port,
                        "path": path,
                        "interval": interval
                    }
                ]
            }
        }
        
        # Add labels if provided
        if labels:
            service_monitor["metadata"]["labels"] = labels
        
        # Write service monitor to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(service_monitor, f)
            service_monitor_file = f.name
        
        try:
            # Apply service monitor
            output = self.executor.run_kubectl_command([
                "apply", "-f", service_monitor_file
            ])
            
            return {
                "name": name,
                "namespace": namespace,
                "selector": selector,
                "port": port,
                "path": path,
                "interval": interval,
                "labels": labels,
                "output": output
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(service_monitor_file):
                os.unlink(service_monitor_file)
    
    def get_service_monitor(self, name: str, namespace: str) -> Dict[str, Any]:
        """
        Get a Prometheus service monitor.
        
        Args:
            name: Service monitor name
            namespace: Namespace
            
        Returns:
            Dict[str, Any]: Service monitor information
        """
        output = self.executor.run_kubectl_command([
            "get", "servicemonitor", name, "-n", namespace, "-o", "json"
        ])
        
        try:
            service_monitor_json = json.loads(output)
            
            return {
                "name": service_monitor_json["metadata"]["name"],
                "namespace": service_monitor_json["metadata"]["namespace"],
                "labels": service_monitor_json["metadata"].get("labels", {}),
                "selector": service_monitor_json["spec"].get("selector", {}),
                "endpoints": service_monitor_json["spec"].get("endpoints", []),
                "created_at": service_monitor_json["metadata"].get("creationTimestamp")
            }
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse service monitor information: {str(e)}")
            return {
                "name": name,
                "namespace": namespace,
                "error": str(e),
                "output": output
            }
    
    def list_service_monitors(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List Prometheus service monitors.
        
        Args:
            namespace: Namespace (optional)
            
        Returns:
            List[Dict[str, Any]]: List of service monitors
        """
        # Build command
        cmd = ["get", "servicemonitors"]
        
        # Add namespace if provided
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")
        
        # Add output format
        cmd.extend(["-o", "json"])
        
        # Get service monitors
        output = self.executor.run_kubectl_command(cmd)
        
        try:
            service_monitors_json = json.loads(output)
            
            service_monitors = []
            for service_monitor in service_monitors_json.get("items", []):
                service_monitor_info = {
                    "name": service_monitor["metadata"]["name"],
                    "namespace": service_monitor["metadata"]["namespace"],
                    "labels": service_monitor["metadata"].get("labels", {}),
                    "selector": service_monitor["spec"].get("selector", {}),
                    "endpoints": len(service_monitor["spec"].get("endpoints", [])),
                    "created_at": service_monitor["metadata"].get("creationTimestamp")
                }
                service_monitors.append(service_monitor_info)
            
            return service_monitors
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse service monitor list: {str(e)}")
            return []


class PrometheusExecutor:
    """
    Executes Prometheus API calls and kubectl commands.
    
    This class provides methods for executing Prometheus API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, prometheus_url: Optional[str],
                alertmanager_url: Optional[str],
                kubectl_binary: str,
                working_dir: str):
        """
        Initialize the Prometheus Executor.
        
        Args:
            prometheus_url: Prometheus server URL
            alertmanager_url: Alertmanager URL
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Prometheus operations
        """
        self.prometheus_url = prometheus_url
        self.alertmanager_url = alertmanager_url
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
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
    
    def query_prometheus(self, query: str, 
                        time: Optional[str] = None,
                        timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Query Prometheus.
        
        Args:
            query: PromQL query
            time: Query time (optional)
            timeout: Query timeout (optional)
            
        Returns:
            Dict[str, Any]: Query result
        """
        if not self.prometheus_url:
            raise Exception("Prometheus URL not configured")
        
        # Build URL
        url = f"{self.prometheus_url}/api/v1/query"
        
        # Build parameters
        params = {"query": query}
        
        # Add time if provided
        if time:
            params["time"] = time
        
        # Add timeout if provided
        if timeout:
            params["timeout"] = timeout
        
        # Execute query
        response = requests.get(url, params=params)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Prometheus query failed: {response.text}")
        
        # Parse response
        data = response.json()
        
        return data
    
    def query_prometheus_range(self, query: str, 
                              start: str,
                              end: str,
                              step: str,
                              timeout: Optional[str] = None) -> Dict[str, Any]:
        """
        Query Prometheus range.
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Step interval
            timeout: Query timeout (optional)
            
        Returns:
            Dict[str, Any]: Query result
        """
        if not self.prometheus_url:
            raise Exception("Prometheus URL not configured")
        
        # Build URL
        url = f"{self.prometheus_url}/api/v1/query_range"
        
        # Build parameters
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        
        # Add timeout if provided
        if timeout:
            params["timeout"] = timeout
        
        # Execute query
        response = requests.get(url, params=params)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Prometheus range query failed: {response.text}")
        
        # Parse response
        data = response.json()
        
        return data
    
    def get_alerts(self) -> Dict[str, Any]:
        """
        Get Prometheus alerts.
        
        Returns:
            Dict[str, Any]: Alerts result
        """
        if not self.prometheus_url:
            raise Exception("Prometheus URL not configured")
        
        # Build URL
        url = f"{self.prometheus_url}/api/v1/alerts"
        
        # Execute query
        response = requests.get(url)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get Prometheus alerts: {response.text}")
        
        # Parse response
        data = response.json()
        
        return data
    
    def get_targets(self) -> Dict[str, Any]:
        """
        Get Prometheus targets.
        
        Returns:
            Dict[str, Any]: Targets result
        """
        if not self.prometheus_url:
            raise Exception("Prometheus URL not configured")
        
        # Build URL
        url = f"{self.prometheus_url}/api/v1/targets"
        
        # Execute query
        response = requests.get(url)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get Prometheus targets: {response.text}")
        
        # Parse response
        data = response.json()
        
        return data
