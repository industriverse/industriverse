"""
Grafana Integration Manager

This module provides integration with Grafana for the Deployment Operations Layer.
It handles Grafana dashboards, data sources, and alerts.

Classes:
    GrafanaIntegrationManager: Manages Grafana integration
    GrafanaDashboardManager: Manages Grafana dashboards
    GrafanaDataSourceManager: Manages Grafana data sources
    GrafanaAlertManager: Manages Grafana alerts
    GrafanaExecutor: Executes Grafana API calls
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

class GrafanaIntegrationManager:
    """
    Manages Grafana integration for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with Grafana,
    handling dashboards, data sources, and alerts.
    """
    
    def __init__(self, grafana_url: Optional[str] = None,
                api_key: Optional[str] = None,
                username: Optional[str] = None,
                password: Optional[str] = None,
                kubectl_binary_path: Optional[str] = None,
                working_dir: Optional[str] = None):
        """
        Initialize the Grafana Integration Manager.
        
        Args:
            grafana_url: Grafana server URL (optional)
            api_key: Grafana API key (optional)
            username: Grafana username (optional)
            password: Grafana password (optional)
            kubectl_binary_path: Path to kubectl binary (optional, defaults to 'kubectl' in PATH)
            working_dir: Working directory for Grafana operations (optional)
        """
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.kubectl_binary = kubectl_binary_path or "kubectl"
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="grafana_")
        
        self.executor = GrafanaExecutor(
            self.grafana_url, 
            self.api_key, 
            self.username, 
            self.password, 
            self.kubectl_binary, 
            self.working_dir
        )
        self.dashboard_manager = GrafanaDashboardManager(self.executor)
        self.datasource_manager = GrafanaDataSourceManager(self.executor)
        self.alert_manager = GrafanaAlertManager(self.executor)
        
        # Verify Grafana connectivity
        if self.grafana_url:
            self._verify_grafana_connectivity()
    
    def _verify_grafana_connectivity(self):
        """
        Verify that Grafana is accessible.
        
        Logs a warning if Grafana is not accessible but does not raise an exception
        as Grafana may be accessed via other means.
        """
        try:
            response = self.executor.make_grafana_api_request("GET", "/api/health")
            if response.status_code == 200:
                logger.info("Grafana server is accessible")
            else:
                logger.warning(f"Grafana server returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Grafana server is not accessible: {str(e)}")
    
    def create_dashboard(self, dashboard_json: Dict[str, Any], 
                        folder_id: Optional[int] = None,
                        overwrite: bool = False) -> AgentResponse:
        """
        Create a Grafana dashboard.
        
        Args:
            dashboard_json: Dashboard JSON
            folder_id: Folder ID (optional)
            overwrite: Whether to overwrite existing dashboard (default: False)
            
        Returns:
            AgentResponse: Dashboard creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            result = self.dashboard_manager.create_dashboard(
                dashboard_json=dashboard_json,
                folder_id=folder_id,
                overwrite=overwrite
            )
            
            return AgentResponse(
                success=True,
                message=f"Grafana dashboard {dashboard_json.get('dashboard', {}).get('title')} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana dashboard: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana dashboard: {str(e)}",
                data={}
            )
    
    def create_datasource(self, name: str, 
                         type_: str,
                         url: str,
                         access: str = "proxy",
                         is_default: bool = False,
                         basic_auth: bool = False,
                         basic_auth_user: Optional[str] = None,
                         basic_auth_password: Optional[str] = None,
                         json_data: Optional[Dict[str, Any]] = None,
                         secure_json_data: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Create a Grafana data source.
        
        Args:
            name: Data source name
            type_: Data source type (e.g., prometheus, elasticsearch)
            url: Data source URL
            access: Access mode (default: proxy)
            is_default: Whether this is the default data source (default: False)
            basic_auth: Whether to use basic auth (default: False)
            basic_auth_user: Basic auth username (optional)
            basic_auth_password: Basic auth password (optional)
            json_data: Additional JSON data (optional)
            secure_json_data: Secure JSON data (optional)
            
        Returns:
            AgentResponse: Data source creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            result = self.datasource_manager.create_datasource(
                name=name,
                type_=type_,
                url=url,
                access=access,
                is_default=is_default,
                basic_auth=basic_auth,
                basic_auth_user=basic_auth_user,
                basic_auth_password=basic_auth_password,
                json_data=json_data,
                secure_json_data=secure_json_data
            )
            
            return AgentResponse(
                success=True,
                message=f"Grafana data source {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana data source: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana data source: {str(e)}",
                data={}
            )
    
    def create_alert_rule(self, name: str, 
                         condition: str,
                         data: List[Dict[str, Any]],
                         no_data_state: str = "NoData",
                         exec_err_state: str = "Error",
                         for_duration: str = "5m",
                         folder_uid: Optional[str] = None,
                         annotations: Optional[Dict[str, str]] = None,
                         labels: Optional[Dict[str, str]] = None) -> AgentResponse:
        """
        Create a Grafana alert rule.
        
        Args:
            name: Alert rule name
            condition: Alert condition
            data: Alert data (queries)
            no_data_state: State when no data (default: NoData)
            exec_err_state: State when execution error (default: Error)
            for_duration: Duration before alerting (default: 5m)
            folder_uid: Folder UID (optional)
            annotations: Alert annotations (optional)
            labels: Alert labels (optional)
            
        Returns:
            AgentResponse: Alert rule creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            result = self.alert_manager.create_alert_rule(
                name=name,
                condition=condition,
                data=data,
                no_data_state=no_data_state,
                exec_err_state=exec_err_state,
                for_duration=for_duration,
                folder_uid=folder_uid,
                annotations=annotations,
                labels=labels
            )
            
            return AgentResponse(
                success=True,
                message=f"Grafana alert rule {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana alert rule: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana alert rule: {str(e)}",
                data={}
            )
    
    def create_folder(self, title: str, uid: Optional[str] = None) -> AgentResponse:
        """
        Create a Grafana folder.
        
        Args:
            title: Folder title
            uid: Folder UID (optional)
            
        Returns:
            AgentResponse: Folder creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            # Build folder data
            folder_data = {
                "title": title
            }
            
            # Add UID if provided
            if uid:
                folder_data["uid"] = uid
            
            # Create folder
            response = self.executor.make_grafana_api_request(
                "POST",
                "/api/folders",
                json=folder_data
            )
            
            # Check response
            if response.status_code not in (200, 201):
                raise Exception(f"Failed to create folder: {response.text}")
            
            # Parse response
            result = response.json()
            
            return AgentResponse(
                success=True,
                message=f"Grafana folder {title} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana folder: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana folder: {str(e)}",
                data={}
            )
    
    def create_team(self, name: str, email: Optional[str] = None) -> AgentResponse:
        """
        Create a Grafana team.
        
        Args:
            name: Team name
            email: Team email (optional)
            
        Returns:
            AgentResponse: Team creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            # Build team data
            team_data = {
                "name": name
            }
            
            # Add email if provided
            if email:
                team_data["email"] = email
            
            # Create team
            response = self.executor.make_grafana_api_request(
                "POST",
                "/api/teams",
                json=team_data
            )
            
            # Check response
            if response.status_code not in (200, 201):
                raise Exception(f"Failed to create team: {response.text}")
            
            # Parse response
            result = response.json()
            
            return AgentResponse(
                success=True,
                message=f"Grafana team {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana team: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana team: {str(e)}",
                data={}
            )
    
    def create_user(self, name: str, 
                   email: str,
                   login: str,
                   password: str) -> AgentResponse:
        """
        Create a Grafana user.
        
        Args:
            name: User name
            email: User email
            login: User login
            password: User password
            
        Returns:
            AgentResponse: User creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            # Build user data
            user_data = {
                "name": name,
                "email": email,
                "login": login,
                "password": password
            }
            
            # Create user
            response = self.executor.make_grafana_api_request(
                "POST",
                "/api/admin/users",
                json=user_data
            )
            
            # Check response
            if response.status_code not in (200, 201):
                raise Exception(f"Failed to create user: {response.text}")
            
            # Parse response
            result = response.json()
            
            return AgentResponse(
                success=True,
                message=f"Grafana user {login} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana user: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana user: {str(e)}",
                data={}
            )
    
    def create_api_key(self, name: str, 
                      role: str,
                      seconds_to_live: Optional[int] = None) -> AgentResponse:
        """
        Create a Grafana API key.
        
        Args:
            name: API key name
            role: API key role (Admin, Editor, Viewer)
            seconds_to_live: Seconds until key expires (optional)
            
        Returns:
            AgentResponse: API key creation response
        """
        try:
            if not self.grafana_url:
                raise Exception("Grafana URL not configured")
            
            # Build API key data
            api_key_data = {
                "name": name,
                "role": role
            }
            
            # Add expiration if provided
            if seconds_to_live:
                api_key_data["secondsToLive"] = seconds_to_live
            
            # Create API key
            response = self.executor.make_grafana_api_request(
                "POST",
                "/api/auth/keys",
                json=api_key_data
            )
            
            # Check response
            if response.status_code not in (200, 201):
                raise Exception(f"Failed to create API key: {response.text}")
            
            # Parse response
            result = response.json()
            
            return AgentResponse(
                success=True,
                message=f"Grafana API key {name} created successfully",
                data=result
            )
        
        except Exception as e:
            logger.error(f"Failed to create Grafana API key: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to create Grafana API key: {str(e)}",
                data={}
            )
    
    def to_mcp_context(self) -> MCPContext:
        """
        Convert Grafana integration information to MCP context.
        
        Returns:
            MCPContext: MCP context with Grafana integration information
        """
        return MCPContext(
            context_type="grafana_integration",
            grafana_url=self.grafana_url,
            grafana_version=self._get_grafana_version(),
            working_dir=self.working_dir
        )
    
    def _get_grafana_version(self) -> str:
        """
        Get the Grafana version.
        
        Returns:
            str: Grafana version
        """
        try:
            if not self.grafana_url:
                return "unknown"
            
            response = self.executor.make_grafana_api_request("GET", "/api/health")
            if response.status_code == 200:
                data = response.json()
                return data.get("version", "unknown")
            else:
                logger.error(f"Failed to get Grafana version: {response.status_code}")
                return "unknown"
        except Exception as e:
            logger.error(f"Failed to get Grafana version: {str(e)}")
            return "unknown"


class GrafanaDashboardManager:
    """
    Manages Grafana dashboards.
    
    This class provides methods for managing Grafana dashboards,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'GrafanaExecutor'):
        """
        Initialize the Grafana Dashboard Manager.
        
        Args:
            executor: Grafana executor
        """
        self.executor = executor
    
    def create_dashboard(self, dashboard_json: Dict[str, Any], 
                        folder_id: Optional[int] = None,
                        overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a Grafana dashboard.
        
        Args:
            dashboard_json: Dashboard JSON
            folder_id: Folder ID (optional)
            overwrite: Whether to overwrite existing dashboard (default: False)
            
        Returns:
            Dict[str, Any]: Dashboard creation result
        """
        # Build dashboard data
        dashboard_data = {
            "dashboard": dashboard_json,
            "overwrite": overwrite
        }
        
        # Add folder ID if provided
        if folder_id is not None:
            dashboard_data["folderId"] = folder_id
        
        # Create dashboard
        response = self.executor.make_grafana_api_request(
            "POST",
            "/api/dashboards/db",
            json=dashboard_data
        )
        
        # Check response
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create dashboard: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Get a Grafana dashboard.
        
        Args:
            uid: Dashboard UID
            
        Returns:
            Dict[str, Any]: Dashboard information
        """
        # Get dashboard
        response = self.executor.make_grafana_api_request(
            "GET",
            f"/api/dashboards/uid/{uid}"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get dashboard: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def delete_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Delete a Grafana dashboard.
        
        Args:
            uid: Dashboard UID
            
        Returns:
            Dict[str, Any]: Dashboard deletion result
        """
        # Delete dashboard
        response = self.executor.make_grafana_api_request(
            "DELETE",
            f"/api/dashboards/uid/{uid}"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to delete dashboard: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List Grafana dashboards.
        
        Returns:
            List[Dict[str, Any]]: List of dashboards
        """
        # List dashboards
        response = self.executor.make_grafana_api_request(
            "GET",
            "/api/search?type=dash-db"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to list dashboards: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def import_dashboard(self, dashboard_path: str, 
                        folder_id: Optional[int] = None,
                        overwrite: bool = False) -> Dict[str, Any]:
        """
        Import a Grafana dashboard from a file.
        
        Args:
            dashboard_path: Path to dashboard JSON file
            folder_id: Folder ID (optional)
            overwrite: Whether to overwrite existing dashboard (default: False)
            
        Returns:
            Dict[str, Any]: Dashboard import result
        """
        # Read dashboard file
        with open(dashboard_path, "r") as f:
            dashboard_json = json.load(f)
        
        # Create dashboard
        return self.create_dashboard(
            dashboard_json=dashboard_json,
            folder_id=folder_id,
            overwrite=overwrite
        )
    
    def export_dashboard(self, uid: str, export_path: str) -> Dict[str, Any]:
        """
        Export a Grafana dashboard to a file.
        
        Args:
            uid: Dashboard UID
            export_path: Path to export dashboard JSON
            
        Returns:
            Dict[str, Any]: Dashboard export result
        """
        # Get dashboard
        dashboard = self.get_dashboard(uid)
        
        # Write dashboard to file
        with open(export_path, "w") as f:
            json.dump(dashboard.get("dashboard", {}), f, indent=2)
        
        return {
            "uid": uid,
            "title": dashboard.get("dashboard", {}).get("title"),
            "export_path": export_path
        }


class GrafanaDataSourceManager:
    """
    Manages Grafana data sources.
    
    This class provides methods for managing Grafana data sources,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'GrafanaExecutor'):
        """
        Initialize the Grafana Data Source Manager.
        
        Args:
            executor: Grafana executor
        """
        self.executor = executor
    
    def create_datasource(self, name: str, 
                         type_: str,
                         url: str,
                         access: str = "proxy",
                         is_default: bool = False,
                         basic_auth: bool = False,
                         basic_auth_user: Optional[str] = None,
                         basic_auth_password: Optional[str] = None,
                         json_data: Optional[Dict[str, Any]] = None,
                         secure_json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Grafana data source.
        
        Args:
            name: Data source name
            type_: Data source type (e.g., prometheus, elasticsearch)
            url: Data source URL
            access: Access mode (default: proxy)
            is_default: Whether this is the default data source (default: False)
            basic_auth: Whether to use basic auth (default: False)
            basic_auth_user: Basic auth username (optional)
            basic_auth_password: Basic auth password (optional)
            json_data: Additional JSON data (optional)
            secure_json_data: Secure JSON data (optional)
            
        Returns:
            Dict[str, Any]: Data source creation result
        """
        # Build data source data
        datasource_data = {
            "name": name,
            "type": type_,
            "url": url,
            "access": access,
            "isDefault": is_default,
            "basicAuth": basic_auth
        }
        
        # Add basic auth credentials if provided
        if basic_auth and basic_auth_user and basic_auth_password:
            datasource_data["basicAuthUser"] = basic_auth_user
            datasource_data["basicAuthPassword"] = basic_auth_password
        
        # Add JSON data if provided
        if json_data:
            datasource_data["jsonData"] = json_data
        
        # Add secure JSON data if provided
        if secure_json_data:
            datasource_data["secureJsonData"] = secure_json_data
        
        # Create data source
        response = self.executor.make_grafana_api_request(
            "POST",
            "/api/datasources",
            json=datasource_data
        )
        
        # Check response
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create data source: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_datasource(self, id_or_name: Union[int, str]) -> Dict[str, Any]:
        """
        Get a Grafana data source.
        
        Args:
            id_or_name: Data source ID or name
            
        Returns:
            Dict[str, Any]: Data source information
        """
        # Determine endpoint
        if isinstance(id_or_name, int):
            endpoint = f"/api/datasources/{id_or_name}"
        else:
            endpoint = f"/api/datasources/name/{id_or_name}"
        
        # Get data source
        response = self.executor.make_grafana_api_request(
            "GET",
            endpoint
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get data source: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def delete_datasource(self, id_or_name: Union[int, str]) -> Dict[str, Any]:
        """
        Delete a Grafana data source.
        
        Args:
            id_or_name: Data source ID or name
            
        Returns:
            Dict[str, Any]: Data source deletion result
        """
        # Determine endpoint
        if isinstance(id_or_name, int):
            endpoint = f"/api/datasources/{id_or_name}"
        else:
            endpoint = f"/api/datasources/name/{id_or_name}"
        
        # Delete data source
        response = self.executor.make_grafana_api_request(
            "DELETE",
            endpoint
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to delete data source: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def list_datasources(self) -> List[Dict[str, Any]]:
        """
        List Grafana data sources.
        
        Returns:
            List[Dict[str, Any]]: List of data sources
        """
        # List data sources
        response = self.executor.make_grafana_api_request(
            "GET",
            "/api/datasources"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to list data sources: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class GrafanaAlertManager:
    """
    Manages Grafana alerts.
    
    This class provides methods for managing Grafana alerts,
    including creation, modification, and listing.
    """
    
    def __init__(self, executor: 'GrafanaExecutor'):
        """
        Initialize the Grafana Alert Manager.
        
        Args:
            executor: Grafana executor
        """
        self.executor = executor
    
    def create_alert_rule(self, name: str, 
                         condition: str,
                         data: List[Dict[str, Any]],
                         no_data_state: str = "NoData",
                         exec_err_state: str = "Error",
                         for_duration: str = "5m",
                         folder_uid: Optional[str] = None,
                         annotations: Optional[Dict[str, str]] = None,
                         labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Grafana alert rule.
        
        Args:
            name: Alert rule name
            condition: Alert condition
            data: Alert data (queries)
            no_data_state: State when no data (default: NoData)
            exec_err_state: State when execution error (default: Error)
            for_duration: Duration before alerting (default: 5m)
            folder_uid: Folder UID (optional)
            annotations: Alert annotations (optional)
            labels: Alert labels (optional)
            
        Returns:
            Dict[str, Any]: Alert rule creation result
        """
        # Build alert rule data
        alert_rule_data = {
            "name": name,
            "condition": condition,
            "data": data,
            "noDataState": no_data_state,
            "execErrState": exec_err_state,
            "for": for_duration
        }
        
        # Add folder UID if provided
        if folder_uid:
            alert_rule_data["folderUID"] = folder_uid
        
        # Add annotations if provided
        if annotations:
            alert_rule_data["annotations"] = annotations
        
        # Add labels if provided
        if labels:
            alert_rule_data["labels"] = labels
        
        # Create alert rule
        response = self.executor.make_grafana_api_request(
            "POST",
            "/api/alerting/rule",
            json=alert_rule_data
        )
        
        # Check response
        if response.status_code not in (200, 201):
            raise Exception(f"Failed to create alert rule: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def get_alert_rule(self, uid: str) -> Dict[str, Any]:
        """
        Get a Grafana alert rule.
        
        Args:
            uid: Alert rule UID
            
        Returns:
            Dict[str, Any]: Alert rule information
        """
        # Get alert rule
        response = self.executor.make_grafana_api_request(
            "GET",
            f"/api/alerting/rule/{uid}"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to get alert rule: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def delete_alert_rule(self, uid: str) -> Dict[str, Any]:
        """
        Delete a Grafana alert rule.
        
        Args:
            uid: Alert rule UID
            
        Returns:
            Dict[str, Any]: Alert rule deletion result
        """
        # Delete alert rule
        response = self.executor.make_grafana_api_request(
            "DELETE",
            f"/api/alerting/rule/{uid}"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to delete alert rule: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result
    
    def list_alert_rules(self) -> List[Dict[str, Any]]:
        """
        List Grafana alert rules.
        
        Returns:
            List[Dict[str, Any]]: List of alert rules
        """
        # List alert rules
        response = self.executor.make_grafana_api_request(
            "GET",
            "/api/alerting/rules"
        )
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"Failed to list alert rules: {response.text}")
        
        # Parse response
        result = response.json()
        
        return result


class GrafanaExecutor:
    """
    Executes Grafana API calls and kubectl commands.
    
    This class provides methods for executing Grafana API calls and kubectl commands
    and handling their output.
    """
    
    def __init__(self, grafana_url: Optional[str],
                api_key: Optional[str],
                username: Optional[str],
                password: Optional[str],
                kubectl_binary: str,
                working_dir: str):
        """
        Initialize the Grafana Executor.
        
        Args:
            grafana_url: Grafana server URL
            api_key: Grafana API key
            username: Grafana username
            password: Grafana password
            kubectl_binary: Path to kubectl binary
            working_dir: Working directory for Grafana operations
        """
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.kubectl_binary = kubectl_binary
        self.working_dir = working_dir
    
    def make_grafana_api_request(self, method: str, 
                                endpoint: str,
                                params: Optional[Dict[str, Any]] = None,
                                json: Optional[Dict[str, Any]] = None,
                                data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a Grafana API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters (optional)
            json: JSON body (optional)
            data: Form data (optional)
            
        Returns:
            requests.Response: API response
            
        Raises:
            Exception: If Grafana URL is not configured
        """
        if not self.grafana_url:
            raise Exception("Grafana URL not configured")
        
        # Build URL
        url = f"{self.grafana_url.rstrip('/')}{endpoint}"
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add authentication
        auth = None
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.username and self.password:
            auth = (self.username, self.password)
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data,
            headers=headers,
            auth=auth
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
