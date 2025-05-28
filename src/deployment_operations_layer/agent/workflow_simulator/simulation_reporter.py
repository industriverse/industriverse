"""
Simulation Reporter

This module is responsible for generating reports from simulation results for the Workflow Simulator Agent.
It creates comprehensive, detailed reports that summarize simulation outcomes, provide insights,
and offer recommendations for deployment decisions.
"""

import logging
import time
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SimulationReporter:
    """
    Generates reports from simulation results.
    
    This class creates detailed reports that summarize simulation outcomes,
    provide insights, and offer recommendations for deployment decisions.
    The reports can be generated in various formats including JSON, HTML, and PDF.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Simulation Reporter.
        
        Args:
            config: Configuration dictionary for the reporter
        """
        self.config = config or {}
        
        # Report storage directory
        self.report_dir = self.config.get("report_dir", "/tmp/simulation_reports")
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Report formats
        self.formats = self.config.get("formats", ["json", "html"])
        
        # Report templates
        self.templates = self.config.get("templates", {})
        
        logger.info("Simulation Reporter initialized")
    
    def generate_report(self,
                       simulation_id: str,
                       deployment_manifest: Dict[str, Any],
                       environment_config: Dict[str, Any],
                       scenarios: List[Dict[str, Any]],
                       simulation_results: Dict[str, Any],
                       analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive report from simulation results and analysis.
        
        Args:
            simulation_id: Unique identifier for the simulation
            deployment_manifest: The deployment manifest being tested
            environment_config: Configuration of the target environment
            scenarios: List of simulation scenarios
            simulation_results: Results from simulation execution
            analysis_results: Results from simulation analysis
            
        Returns:
            Dictionary containing report information and file paths
        """
        logger.info(f"Generating report for simulation {simulation_id}")
        
        # Create report data structure
        report_data = self._create_report_data(
            simulation_id,
            deployment_manifest,
            environment_config,
            scenarios,
            simulation_results,
            analysis_results
        )
        
        # Generate reports in requested formats
        report_files = {}
        
        if "json" in self.formats:
            json_path = self._generate_json_report(report_data, simulation_id)
            report_files["json"] = json_path
        
        if "html" in self.formats:
            html_path = self._generate_html_report(report_data, simulation_id)
            report_files["html"] = html_path
        
        if "pdf" in self.formats:
            pdf_path = self._generate_pdf_report(report_data, simulation_id)
            report_files["pdf"] = pdf_path
        
        # Create report summary
        report_summary = self._create_report_summary(report_data)
        
        logger.info(f"Report generation complete for simulation {simulation_id}")
        
        return {
            "id": simulation_id,
            "timestamp": time.time(),
            "summary": report_summary,
            "files": report_files,
            "data": report_data
        }
    
    def _create_report_data(self,
                           simulation_id: str,
                           deployment_manifest: Dict[str, Any],
                           environment_config: Dict[str, Any],
                           scenarios: List[Dict[str, Any]],
                           simulation_results: Dict[str, Any],
                           analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the complete report data structure.
        
        Args:
            simulation_id: Unique identifier for the simulation
            deployment_manifest: The deployment manifest being tested
            environment_config: Configuration of the target environment
            scenarios: List of simulation scenarios
            simulation_results: Results from simulation execution
            analysis_results: Results from simulation analysis
            
        Returns:
            Dictionary containing complete report data
        """
        # Format timestamp
        timestamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract key information from deployment manifest
        deployment_info = {
            "id": deployment_manifest.get("id", "unknown"),
            "name": deployment_manifest.get("name", "unknown"),
            "version": deployment_manifest.get("version", "unknown"),
            "type": deployment_manifest.get("type", "unknown"),
            "components": len(deployment_manifest.get("components", [])),
            "resources": deployment_manifest.get("resources", {})
        }
        
        # Extract key information from environment config
        environment_info = {
            "name": environment_config.get("name", "unknown"),
            "type": environment_config.get("type", "unknown"),
            "region": environment_config.get("region", "unknown"),
            "is_edge": environment_config.get("is_edge", False),
            "resources": environment_config.get("resources", {})
        }
        
        # Extract key metrics from analysis results
        key_metrics = {
            "success_rate": analysis_results.get("success_rate", 0),
            "performance_score": analysis_results.get("performance_score", 0),
            "resource_utilization": analysis_results.get("resource_utilization", 0),
            "error_count": analysis_results.get("error_count", 0)
        }
        
        # Extract deployment readiness assessment
        deployment_readiness = analysis_results.get("deployment_readiness", {
            "score": 0,
            "level": "unknown",
            "confidence": "unknown",
            "factors": []
        })
        
        # Create report data structure
        report_data = {
            "report_id": f"sim-report-{simulation_id}",
            "simulation_id": simulation_id,
            "timestamp": timestamp,
            "title": f"Deployment Simulation Report - {deployment_info['name']} v{deployment_info['version']}",
            "summary": {
                "deployment": deployment_info,
                "environment": environment_info,
                "scenarios_count": len(scenarios),
                "key_metrics": key_metrics,
                "deployment_readiness": deployment_readiness,
                "recommendation": self._generate_recommendation(analysis_results)
            },
            "scenarios": self._format_scenarios(scenarios),
            "results": self._format_results(simulation_results),
            "analysis": {
                "key_metrics": key_metrics,
                "insights": analysis_results.get("insights", []),
                "improvement_suggestions": analysis_results.get("improvement_suggestions", []),
                "deployment_readiness": deployment_readiness,
                "scenario_analyses": analysis_results.get("scenario_analyses", [])
            },
            "deployment_manifest": deployment_manifest,
            "environment_config": environment_config
        }
        
        return report_data
    
    def _format_scenarios(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format scenario information for the report.
        
        Args:
            scenarios: List of simulation scenarios
            
        Returns:
            List of formatted scenario dictionaries
        """
        formatted_scenarios = []
        
        for scenario in scenarios:
            formatted_scenario = {
                "id": scenario.get("id", "unknown"),
                "type": scenario.get("type", "unknown"),
                "description": scenario.get("description", "No description"),
                "network_conditions": {
                    "profile": scenario.get("network_conditions", {}).get("profile", "unknown"),
                    "latency_ms": scenario.get("network_conditions", {}).get("latency_ms", 0),
                    "packet_loss_percent": scenario.get("network_conditions", {}).get("packet_loss_percent", 0),
                    "bandwidth_mbps": scenario.get("network_conditions", {}).get("bandwidth_mbps", 0)
                },
                "resource_availability": {
                    "profile": scenario.get("resource_availability", {}).get("profile", "unknown"),
                    "cpu_available_percent": scenario.get("resource_availability", {}).get("cpu_available_percent", 0),
                    "memory_available_percent": scenario.get("resource_availability", {}).get("memory_available_percent", 0),
                    "storage_available_percent": scenario.get("resource_availability", {}).get("storage_available_percent", 0)
                },
                "load_profile": {
                    "profile": scenario.get("load_profile", {}).get("profile", "unknown"),
                    "requests_per_second": scenario.get("load_profile", {}).get("requests_per_second", 0),
                    "concurrent_users": scenario.get("load_profile", {}).get("concurrent_users", 0),
                    "data_transfer_mbps": scenario.get("load_profile", {}).get("data_transfer_mbps", 0)
                },
                "duration_seconds": scenario.get("duration_seconds", 0)
            }
            
            formatted_scenarios.append(formatted_scenario)
        
        return formatted_scenarios
    
    def _format_results(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format simulation results for the report.
        
        Args:
            simulation_results: Results from simulation execution
            
        Returns:
            Dictionary of formatted simulation results
        """
        # Extract overall metrics
        overall_metrics = simulation_results.get("overall_metrics", {})
        
        # Format scenario results
        scenario_results = []
        for result in simulation_results.get("scenario_results", []):
            # Format events
            events = []
            for event in result.get("events", []):
                events.append({
                    "timestamp": datetime.fromtimestamp(event.get("timestamp", 0)).strftime("%H:%M:%S"),
                    "type": event.get("type", "unknown"),
                    "details": event.get("details", {})
                })
            
            # Format errors
            errors = []
            for error in result.get("errors", []):
                errors.append({
                    "type": error.get("type", "unknown"),
                    "message": error.get("message", "Unknown error"),
                    "details": error.get("details", {})
                })
            
            # Create formatted result
            formatted_result = {
                "scenario_id": result.get("scenario_id", "unknown"),
                "success": result.get("success", False),
                "duration": result.get("duration", 0),
                "events_count": len(events),
                "errors_count": len(errors),
                "events": events,
                "errors": errors
            }
            
            # Add summary metrics if available
            if "summary" in result:
                formatted_result["summary"] = result["summary"]
            
            scenario_results.append(formatted_result)
        
        return {
            "overall_metrics": overall_metrics,
            "scenario_results": scenario_results,
            "execution_time": simulation_results.get("execution_time", 0)
        }
    
    def _generate_recommendation(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a deployment recommendation based on analysis results.
        
        Args:
            analysis_results: Results from simulation analysis
            
        Returns:
            Recommendation dictionary
        """
        # Check if analysis already includes a recommendation
        if "recommendation" in analysis_results:
            return analysis_results["recommendation"]
        
        # Extract key metrics
        success_rate = analysis_results.get("success_rate", 0)
        performance_score = analysis_results.get("performance_score", 0)
        resource_utilization = analysis_results.get("resource_utilization", 0)
        error_count = analysis_results.get("error_count", 0)
        
        # Get deployment readiness assessment
        readiness = analysis_results.get("deployment_readiness", {})
        readiness_level = readiness.get("level", "unknown")
        
        # Determine recommendation
        if readiness_level == "ready":
            recommendation = "approve"
            confidence = "high"
            message = "Deployment is ready for production"
        elif readiness_level == "ready_with_caution":
            recommendation = "approve_with_caution"
            confidence = "medium"
            message = "Deployment can proceed with caution and monitoring"
        elif readiness_level == "needs_improvements":
            recommendation = "needs_improvements"
            confidence = "medium"
            message = "Deployment needs improvements before proceeding"
        else:
            recommendation = "reject"
            confidence = "high"
            message = "Deployment is not ready for production"
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "message": message,
            "reasons": analysis_results.get("insights", []),
            "improvements": analysis_results.get("improvement_suggestions", [])
        }
    
    def _create_report_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the report.
        
        Args:
            report_data: Complete report data
            
        Returns:
            Dictionary containing report summary
        """
        summary = report_data["summary"]
        
        # Add recommendation message
        recommendation = summary.get("recommendation", {})
        recommendation_message = recommendation.get("message", "No recommendation available")
        
        # Format timestamp
        timestamp = report_data["timestamp"]
        
        # Create summary
        return {
            "report_id": report_data["report_id"],
            "simulation_id": report_data["simulation_id"],
            "timestamp": timestamp,
            "deployment_name": summary["deployment"]["name"],
            "deployment_version": summary["deployment"]["version"],
            "environment_name": summary["environment"]["name"],
            "scenarios_count": summary["scenarios_count"],
            "success_rate": summary["key_metrics"]["success_rate"],
            "performance_score": summary["key_metrics"]["performance_score"],
            "error_count": summary["key_metrics"]["error_count"],
            "readiness_level": summary["deployment_readiness"]["level"],
            "readiness_score": summary["deployment_readiness"]["score"],
            "recommendation": recommendation.get("recommendation", "unknown"),
            "recommendation_message": recommendation_message
        }
    
    def _generate_json_report(self, report_data: Dict[str, Any], simulation_id: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            report_data: Report data dictionary
            simulation_id: Unique identifier for the simulation
            
        Returns:
            Path to the generated JSON file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"simulation_report_{simulation_id}.json")
        
        # Write JSON file
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Generated JSON report: {file_path}")
        
        return file_path
    
    def _generate_html_report(self, report_data: Dict[str, Any], simulation_id: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            report_data: Report data dictionary
            simulation_id: Unique identifier for the simulation
            
        Returns:
            Path to the generated HTML file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"simulation_report_{simulation_id}.html")
        
        # Get HTML template
        template = self._get_html_template()
        
        # Replace placeholders with actual data
        html_content = self._render_html_template(template, report_data)
        
        # Write HTML file
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {file_path}")
        
        return file_path
    
    def _get_html_template(self) -> str:
        """
        Get the HTML template for reports.
        
        Returns:
            HTML template string
        """
        # Check if template is provided in config
        if "html" in self.templates:
            template_path = self.templates["html"]
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return f.read()
        
        # Return default template
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{title}}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
                h1 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }
                h2 { color: #3498db; margin-top: 30px; }
                h3 { color: #2980b9; }
                .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .metrics { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }
                .metric { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; flex: 1; min-width: 200px; }
                .metric h3 { margin-top: 0; }
                .success { color: #27ae60; }
                .warning { color: #f39c12; }
                .danger { color: #e74c3c; }
                .recommendation { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .scenario { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
                .scenario-success { border-left: 5px solid #27ae60; }
                .scenario-failure { border-left: 5px solid #e74c3c; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .insights, .improvements { margin-bottom: 20px; }
                .insights li, .improvements li { margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>{{title}}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Simulation ID:</strong> {{simulation_id}}</p>
                <p><strong>Timestamp:</strong> {{timestamp}}</p>
                <p><strong>Deployment:</strong> {{summary.deployment.name}} v{{summary.deployment.version}}</p>
                <p><strong>Environment:</strong> {{summary.environment.name}} ({{summary.environment.type}})</p>
                <p><strong>Scenarios:</strong> {{summary.scenarios_count}}</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Success Rate</h3>
                    <p class="{{success_rate_class}}">{{success_rate_formatted}}</p>
                </div>
                <div class="metric">
                    <h3>Performance Score</h3>
                    <p class="{{performance_score_class}}">{{performance_score_formatted}}</p>
                </div>
                <div class="metric">
                    <h3>Resource Utilization</h3>
                    <p class="{{resource_utilization_class}}">{{resource_utilization_formatted}}</p>
                </div>
                <div class="metric">
                    <h3>Error Count</h3>
                    <p class="{{error_count_class}}">{{error_count}}</p>
                </div>
            </div>
            
            <div class="recommendation">
                <h2>Recommendation</h2>
                <p><strong>{{summary.recommendation.recommendation}}</strong> (Confidence: {{summary.recommendation.confidence}})</p>
                <p>{{summary.recommendation.message}}</p>
            </div>
            
            <div class="insights">
                <h2>Key Insights</h2>
                <ul>
                    {{insights_list}}
                </ul>
            </div>
            
            <div class="improvements">
                <h2>Improvement Suggestions</h2>
                <ul>
                    {{improvements_list}}
                </ul>
            </div>
            
            <h2>Scenarios</h2>
            {{scenarios_html}}
            
            <h2>Detailed Results</h2>
            {{results_html}}
        </body>
        </html>
        """
    
    def _render_html_template(self, template: str, report_data: Dict[str, Any]) -> str:
        """
        Render the HTML template with report data.
        
        Args:
            template: HTML template string
            report_data: Report data dictionary
            
        Returns:
            Rendered HTML string
        """
        # Replace simple placeholders
        html = template.replace("{{title}}", report_data["title"])
        html = html.replace("{{simulation_id}}", report_data["simulation_id"])
        html = html.replace("{{timestamp}}", report_data["timestamp"])
        
        # Format metrics with classes
        success_rate = report_data["summary"]["key_metrics"]["success_rate"]
        success_rate_formatted = f"{success_rate * 100:.1f}%"
        if success_rate >= 0.9:
            success_rate_class = "success"
        elif success_rate >= 0.7:
            success_rate_class = "warning"
        else:
            success_rate_class = "danger"
        
        html = html.replace("{{success_rate_formatted}}", success_rate_formatted)
        html = html.replace("{{success_rate_class}}", success_rate_class)
        
        performance_score = report_data["summary"]["key_metrics"]["performance_score"]
        performance_score_formatted = f"{performance_score * 100:.1f}%"
        if performance_score >= 0.8:
            performance_score_class = "success"
        elif performance_score >= 0.6:
            performance_score_class = "warning"
        else:
            performance_score_class = "danger"
        
        html = html.replace("{{performance_score_formatted}}", performance_score_formatted)
        html = html.replace("{{performance_score_class}}", performance_score_class)
        
        resource_utilization = report_data["summary"]["key_metrics"]["resource_utilization"]
        resource_utilization_formatted = f"{resource_utilization * 100:.1f}%"
        if resource_utilization >= 0.8:
            resource_utilization_class = "success"
        elif resource_utilization >= 0.6:
            resource_utilization_class = "warning"
        else:
            resource_utilization_class = "danger"
        
        html = html.replace("{{resource_utilization_formatted}}", resource_utilization_formatted)
        html = html.replace("{{resource_utilization_class}}", resource_utilization_class)
        
        error_count = report_data["summary"]["key_metrics"]["error_count"]
        if error_count == 0:
            error_count_class = "success"
        elif error_count <= 3:
            error_count_class = "warning"
        else:
            error_count_class = "danger"
        
        html = html.replace("{{error_count}}", str(error_count))
        html = html.replace("{{error_count_class}}", error_count_class)
        
        # Generate insights list
        insights_list = ""
        for insight in report_data["analysis"]["insights"]:
            insights_list += f"<li>{insight}</li>\n"
        
        html = html.replace("{{insights_list}}", insights_list)
        
        # Generate improvements list
        improvements_list = ""
        for improvement in report_data["analysis"]["improvement_suggestions"]:
            improvements_list += f"<li>{improvement}</li>\n"
        
        html = html.replace("{{improvements_list}}", improvements_list)
        
        # Generate scenarios HTML
        scenarios_html = ""
        for scenario in report_data["scenarios"]:
            scenario_class = "scenario"
            
            # Find corresponding result
            scenario_result = None
            for result in report_data["results"]["scenario_results"]:
                if result["scenario_id"] == scenario["id"]:
                    scenario_result = result
                    break
            
            if scenario_result:
                if scenario_result["success"]:
                    scenario_class += " scenario-success"
                else:
                    scenario_class += " scenario-failure"
            
            scenarios_html += f"""
            <div class="{scenario_class}">
                <h3>{scenario["description"]} ({scenario["id"]})</h3>
                <p><strong>Type:</strong> {scenario["type"]}</p>
                <p><strong>Network:</strong> {scenario["network_conditions"]["profile"]} 
                   (Latency: {scenario["network_conditions"]["latency_ms"]}ms, 
                   Packet Loss: {scenario["network_conditions"]["packet_loss_percent"]}%, 
                   Bandwidth: {scenario["network_conditions"]["bandwidth_mbps"]}Mbps)</p>
                <p><strong>Resources:</strong> {scenario["resource_availability"]["profile"]} 
                   (CPU: {scenario["resource_availability"]["cpu_available_percent"]}%, 
                   Memory: {scenario["resource_availability"]["memory_available_percent"]}%)</p>
                <p><strong>Load:</strong> {scenario["load_profile"]["profile"]} 
                   (RPS: {scenario["load_profile"]["requests_per_second"]}, 
                   Users: {scenario["load_profile"]["concurrent_users"]})</p>
            """
            
            if scenario_result:
                scenarios_html += f"""
                <p><strong>Result:</strong> {"Success" if scenario_result["success"] else "Failure"}</p>
                <p><strong>Duration:</strong> {scenario_result["duration"]:.2f} seconds</p>
                <p><strong>Errors:</strong> {scenario_result["errors_count"]}</p>
                """
            
            scenarios_html += "</div>\n"
        
        html = html.replace("{{scenarios_html}}", scenarios_html)
        
        # Generate results HTML
        results_html = f"""
        <p><strong>Overall Execution Time:</strong> {report_data["results"]["execution_time"]:.2f} seconds</p>
        
        <h3>Overall Metrics</h3>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        """
        
        for key, value in report_data["results"]["overall_metrics"].items():
            if isinstance(value, dict):
                continue
            results_html += f"""
            <tr>
                <td>{key.replace('_', ' ').title()}</td>
                <td>{value}</td>
            </tr>
            """
        
        results_html += "</table>\n"
        
        html = html.replace("{{results_html}}", results_html)
        
        return html
    
    def _generate_pdf_report(self, report_data: Dict[str, Any], simulation_id: str) -> str:
        """
        Generate a PDF report.
        
        Args:
            report_data: Report data dictionary
            simulation_id: Unique identifier for the simulation
            
        Returns:
            Path to the generated PDF file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"simulation_report_{simulation_id}.pdf")
        
        # Generate HTML first
        html_path = self._generate_html_report(report_data, simulation_id)
        
        try:
            # Convert HTML to PDF using weasyprint
            from weasyprint import HTML
            HTML(html_path).write_pdf(file_path)
            logger.info(f"Generated PDF report: {file_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            file_path = ""
        
        return file_path
