"""
Compliance Reporter

This module is responsible for generating compliance reports from validation results.
It creates comprehensive, detailed reports that summarize compliance status, violations,
and recommendations for remediation.
"""

import logging
import time
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ComplianceReporter:
    """
    Generates compliance reports from validation results.
    
    This class creates detailed reports that summarize compliance status, violations,
    and recommendations for remediation. The reports can be generated in various formats
    including JSON, HTML, and PDF.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Compliance Reporter.
        
        Args:
            config: Configuration dictionary for the reporter
        """
        self.config = config or {}
        
        # Report storage directory
        self.report_dir = self.config.get("report_dir", "/tmp/compliance_reports")
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Report formats
        self.formats = self.config.get("formats", ["json", "html"])
        
        # Report templates
        self.templates = self.config.get("templates", {})
        
        logger.info("Compliance Reporter initialized")
    
    def generate_report(self,
                       snapshot_id: str,
                       deployment_manifest: Dict[str, Any],
                       environment_config: Dict[str, Any],
                       policy_set: Dict[str, Any],
                       evidence: Dict[str, Any],
                       validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report.
        
        Args:
            snapshot_id: Unique identifier for the compliance snapshot
            deployment_manifest: The deployment manifest being validated
            environment_config: Configuration of the target environment
            policy_set: Policy set used for validation
            evidence: Evidence collected for validation
            validation_results: Results from compliance validation
            
        Returns:
            Dictionary containing report information and file paths
        """
        logger.info(f"Generating compliance report for snapshot {snapshot_id}")
        
        # Create report data structure
        report_data = self._create_report_data(
            snapshot_id,
            deployment_manifest,
            environment_config,
            policy_set,
            evidence,
            validation_results
        )
        
        # Generate reports in requested formats
        report_files = {}
        
        if "json" in self.formats:
            json_path = self._generate_json_report(report_data, snapshot_id)
            report_files["json"] = json_path
        
        if "html" in self.formats:
            html_path = self._generate_html_report(report_data, snapshot_id)
            report_files["html"] = html_path
        
        if "pdf" in self.formats:
            pdf_path = self._generate_pdf_report(report_data, snapshot_id)
            report_files["pdf"] = pdf_path
        
        # Create report summary
        report_summary = self._create_report_summary(report_data)
        
        logger.info(f"Report generation complete for snapshot {snapshot_id}")
        
        return {
            "id": f"compliance-report-{snapshot_id}",
            "snapshot_id": snapshot_id,
            "timestamp": time.time(),
            "summary": report_summary,
            "files": report_files,
            "data": report_data
        }
    
    def _create_report_data(self,
                           snapshot_id: str,
                           deployment_manifest: Dict[str, Any],
                           environment_config: Dict[str, Any],
                           policy_set: Dict[str, Any],
                           evidence: Dict[str, Any],
                           validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the complete report data structure.
        
        Args:
            snapshot_id: Unique identifier for the compliance snapshot
            deployment_manifest: The deployment manifest being validated
            environment_config: Configuration of the target environment
            policy_set: Policy set used for validation
            evidence: Evidence collected for validation
            validation_results: Results from compliance validation
            
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
        
        # Extract key information from policy set
        policy_info = {
            "id": policy_set.get("id", "unknown"),
            "name": policy_set.get("name", "unknown"),
            "version": policy_set.get("version", "unknown"),
            "description": policy_set.get("description", ""),
            "policies_count": len(policy_set.get("policies", [])),
            "metadata": policy_set.get("metadata", {})
        }
        
        # Generate remediation recommendations
        remediation_recommendations = self._generate_remediation_recommendations(validation_results)
        
        # Create report data structure
        report_data = {
            "report_id": f"compliance-report-{snapshot_id}",
            "snapshot_id": snapshot_id,
            "timestamp": timestamp,
            "title": f"Compliance Report - {deployment_info['name']} v{deployment_info['version']}",
            "summary": {
                "deployment": deployment_info,
                "environment": environment_info,
                "policy_set": policy_info,
                "compliant": validation_results.get("compliant", False),
                "compliance_rate": validation_results.get("summary", {}).get("compliance_rate", 0),
                "violations_count": len(validation_results.get("violations", [])),
                "validation_time": validation_results.get("validation_time", 0)
            },
            "validation_results": validation_results,
            "remediation_recommendations": remediation_recommendations,
            "deployment_manifest": deployment_manifest,
            "environment_config": environment_config,
            "policy_set": policy_set
        }
        
        return report_data
    
    def _generate_remediation_recommendations(self, validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate remediation recommendations for compliance violations.
        
        Args:
            validation_results: Results from compliance validation
            
        Returns:
            List of remediation recommendation dictionaries
        """
        recommendations = []
        
        # Process each violation
        for violation in validation_results.get("violations", []):
            code = violation.get("code", "unknown")
            
            # Generate recommendation based on violation code
            if code == "missing_security_controls":
                missing_controls = violation.get("missing_controls", [])
                for control in missing_controls:
                    recommendations.append({
                        "violation_code": code,
                        "severity": violation.get("severity", "medium"),
                        "recommendation": f"Implement the missing security control: {control}",
                        "details": f"The security control '{control}' is required by policy but not implemented in the deployment."
                    })
            
            elif code == "insecure_communication":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Enable secure communication channels",
                    "details": "Configure TLS/SSL for all communication channels in the deployment."
                })
            
            elif code == "missing_authentication":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Enable authentication",
                    "details": "Configure authentication for all components in the deployment."
                })
            
            elif code == "missing_authorization":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Enable authorization",
                    "details": "Configure authorization mechanisms for all components in the deployment."
                })
            
            elif code == "missing_vulnerability_scan":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Perform vulnerability scanning",
                    "details": "Run a vulnerability scan on all components of the deployment."
                })
            
            elif code == "high_vulnerabilities":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "high"),
                    "recommendation": "Address high severity vulnerabilities",
                    "details": "Fix all high severity vulnerabilities identified in the vulnerability scan."
                })
            
            elif code == "missing_encryption":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Enable data encryption",
                    "details": "Configure encryption for all sensitive data in the deployment."
                })
            
            elif code == "missing_data_classification":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Implement data classification",
                    "details": "Classify all data handled by the deployment according to sensitivity levels."
                })
            
            elif code == "missing_data_retention_policy":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Implement data retention policies",
                    "details": "Configure data retention policies for all data handled by the deployment."
                })
            
            elif code == "missing_data_backup":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Configure data backup",
                    "details": "Set up regular data backups for all critical data in the deployment."
                })
            
            elif code == "missing_regulatory_frameworks":
                missing_frameworks = violation.get("missing_frameworks", [])
                for framework in missing_frameworks:
                    recommendations.append({
                        "violation_code": code,
                        "severity": violation.get("severity", "medium"),
                        "recommendation": f"Implement the regulatory framework: {framework}",
                        "details": f"The regulatory framework '{framework}' is required but not implemented in the deployment."
                    })
            
            elif code == "missing_certifications":
                missing_certifications = violation.get("missing_certifications", [])
                for certification in missing_certifications:
                    recommendations.append({
                        "violation_code": code,
                        "severity": violation.get("severity", "medium"),
                        "recommendation": f"Obtain the certification: {certification}",
                        "details": f"The certification '{certification}' is required but not obtained for the deployment."
                    })
            
            elif code == "data_sovereignty_violation":
                allowed_regions = violation.get("allowed_regions", [])
                current_region = violation.get("current_region", "unknown")
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "high"),
                    "recommendation": f"Deploy to an allowed region: {', '.join(allowed_regions)}",
                    "details": f"The current deployment region '{current_region}' violates data sovereignty requirements. Deploy to one of the allowed regions: {', '.join(allowed_regions)}."
                })
            
            elif code == "missing_monitoring":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Configure monitoring",
                    "details": "Set up monitoring for all components in the deployment."
                })
            
            elif code == "missing_logging":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Configure logging",
                    "details": "Set up logging for all components in the deployment."
                })
            
            elif code == "missing_alerting":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Configure alerting",
                    "details": "Set up alerting for critical events in the deployment."
                })
            
            elif code == "missing_resource_limits":
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": "Configure resource limits",
                    "details": "Set resource limits (CPU, memory, storage) for all components in the deployment."
                })
            
            elif code == "resource_property_violation":
                property_name = violation.get("property", "unknown")
                actual_value = violation.get("actual_value", "unknown")
                expected_value = violation.get("expected_value", "unknown")
                operator = violation.get("operator", "equals")
                
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": f"Update resource property '{property_name}' to comply with policy",
                    "details": f"The resource property '{property_name}' with value '{actual_value}' does not satisfy the condition '{operator} {expected_value}'. Update the property to comply with the policy."
                })
            
            elif code == "config_value_violation":
                config_path = violation.get("config_path", "unknown")
                actual_value = violation.get("actual_value", "unknown")
                expected_value = violation.get("expected_value", "unknown")
                operator = violation.get("operator", "equals")
                
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": f"Update configuration at path '{config_path}' to comply with policy",
                    "details": f"The configuration at path '{config_path}' with value '{actual_value}' does not satisfy the condition '{operator} {expected_value}'. Update the configuration to comply with the policy."
                })
            
            else:
                # Generic recommendation for unknown violation codes
                recommendations.append({
                    "violation_code": code,
                    "severity": violation.get("severity", "medium"),
                    "recommendation": f"Address compliance violation: {code}",
                    "details": violation.get("message", "No details available")
                })
        
        # Sort recommendations by severity
        recommendations.sort(key=lambda r: {
            "high": 0,
            "medium": 1,
            "low": 2
        }.get(r.get("severity", "medium"), 1))
        
        return recommendations
    
    def _create_report_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of the report.
        
        Args:
            report_data: Complete report data
            
        Returns:
            Dictionary containing report summary
        """
        summary = report_data["summary"]
        
        # Format compliance rate as percentage
        compliance_rate_percent = f"{summary['compliance_rate'] * 100:.1f}%"
        
        # Get violation counts by severity
        violations = report_data["validation_results"].get("violations", [])
        high_violations = sum(1 for v in violations if v.get("severity") == "high")
        medium_violations = sum(1 for v in violations if v.get("severity") == "medium")
        low_violations = sum(1 for v in violations if v.get("severity") == "low")
        
        # Create summary
        return {
            "report_id": report_data["report_id"],
            "snapshot_id": report_data["snapshot_id"],
            "timestamp": report_data["timestamp"],
            "deployment_name": summary["deployment"]["name"],
            "deployment_version": summary["deployment"]["version"],
            "environment_name": summary["environment"]["name"],
            "policy_set_name": summary["policy_set"]["name"],
            "compliant": summary["compliant"],
            "compliance_rate": summary["compliance_rate"],
            "compliance_rate_percent": compliance_rate_percent,
            "violations_count": summary["violations_count"],
            "violations_by_severity": {
                "high": high_violations,
                "medium": medium_violations,
                "low": low_violations
            },
            "validation_time": summary["validation_time"]
        }
    
    def _generate_json_report(self, report_data: Dict[str, Any], snapshot_id: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            report_data: Report data dictionary
            snapshot_id: Unique identifier for the compliance snapshot
            
        Returns:
            Path to the generated JSON file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"compliance_report_{snapshot_id}.json")
        
        # Write JSON file
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Generated JSON report: {file_path}")
        
        return file_path
    
    def _generate_html_report(self, report_data: Dict[str, Any], snapshot_id: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            report_data: Report data dictionary
            snapshot_id: Unique identifier for the compliance snapshot
            
        Returns:
            Path to the generated HTML file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"compliance_report_{snapshot_id}.html")
        
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
                .violations { margin-bottom: 20px; }
                .violation { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
                .violation-high { border-left: 5px solid #e74c3c; }
                .violation-medium { border-left: 5px solid #f39c12; }
                .violation-low { border-left: 5px solid #3498db; }
                .recommendations { margin-bottom: 20px; }
                .recommendation { background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
                .recommendation-high { border-left: 5px solid #e74c3c; }
                .recommendation-medium { border-left: 5px solid #f39c12; }
                .recommendation-low { border-left: 5px solid #3498db; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>{{title}}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Snapshot ID:</strong> {{snapshot_id}}</p>
                <p><strong>Timestamp:</strong> {{timestamp}}</p>
                <p><strong>Deployment:</strong> {{summary.deployment.name}} v{{summary.deployment.version}}</p>
                <p><strong>Environment:</strong> {{summary.environment.name}} ({{summary.environment.type}})</p>
                <p><strong>Policy Set:</strong> {{summary.policy_set.name}} v{{summary.policy_set.version}}</p>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>Compliance Status</h3>
                    <p class="{{compliance_status_class}}">{{compliance_status}}</p>
                </div>
                <div class="metric">
                    <h3>Compliance Rate</h3>
                    <p class="{{compliance_rate_class}}">{{compliance_rate_formatted}}</p>
                </div>
                <div class="metric">
                    <h3>Violations</h3>
                    <p class="{{violations_class}}">{{violations_count}}</p>
                </div>
                <div class="metric">
                    <h3>Validation Time</h3>
                    <p>{{validation_time}} seconds</p>
                </div>
            </div>
            
            <h2>Violations</h2>
            <div class="violations">
                {{violations_html}}
            </div>
            
            <h2>Remediation Recommendations</h2>
            <div class="recommendations">
                {{recommendations_html}}
            </div>
            
            <h2>Policy Results</h2>
            <table>
                <tr>
                    <th>Policy</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Status</th>
                </tr>
                {{policy_results_html}}
            </table>
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
        html = html.replace("{{snapshot_id}}", report_data["snapshot_id"])
        html = html.replace("{{timestamp}}", report_data["timestamp"])
        
        # Format compliance status
        compliance_status = "Compliant" if report_data["summary"]["compliant"] else "Non-Compliant"
        compliance_status_class = "success" if report_data["summary"]["compliant"] else "danger"
        
        html = html.replace("{{compliance_status}}", compliance_status)
        html = html.replace("{{compliance_status_class}}", compliance_status_class)
        
        # Format compliance rate
        compliance_rate = report_data["summary"]["compliance_rate"]
        compliance_rate_formatted = f"{compliance_rate * 100:.1f}%"
        
        if compliance_rate >= 0.9:
            compliance_rate_class = "success"
        elif compliance_rate >= 0.7:
            compliance_rate_class = "warning"
        else:
            compliance_rate_class = "danger"
        
        html = html.replace("{{compliance_rate_formatted}}", compliance_rate_formatted)
        html = html.replace("{{compliance_rate_class}}", compliance_rate_class)
        
        # Format violations count
        violations_count = report_data["summary"]["violations_count"]
        
        if violations_count == 0:
            violations_class = "success"
        elif violations_count <= 5:
            violations_class = "warning"
        else:
            violations_class = "danger"
        
        html = html.replace("{{violations_count}}", str(violations_count))
        html = html.replace("{{violations_class}}", violations_class)
        
        # Format validation time
        validation_time = f"{report_data['summary']['validation_time']:.2f}"
        html = html.replace("{{validation_time}}", validation_time)
        
        # Generate violations HTML
        violations_html = ""
        for violation in report_data["validation_results"].get("violations", []):
            severity = violation.get("severity", "medium")
            violations_html += f"""
            <div class="violation violation-{severity}">
                <h3>{violation.get("message", "Unknown violation")}</h3>
                <p><strong>Code:</strong> {violation.get("code", "unknown")}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Policy:</strong> {violation.get("policy_name", "unknown")}</p>
            """
            
            # Add additional details if available
            for key, value in violation.items():
                if key not in ["code", "message", "severity", "policy_id", "policy_name"]:
                    violations_html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
            
            violations_html += "</div>\n"
        
        if not violations_html:
            violations_html = "<p>No violations found.</p>"
        
        html = html.replace("{{violations_html}}", violations_html)
        
        # Generate recommendations HTML
        recommendations_html = ""
        for recommendation in report_data["remediation_recommendations"]:
            severity = recommendation.get("severity", "medium")
            recommendations_html += f"""
            <div class="recommendation recommendation-{severity}">
                <h3>{recommendation.get("recommendation", "Unknown recommendation")}</h3>
                <p><strong>Violation Code:</strong> {recommendation.get("violation_code", "unknown")}</p>
                <p><strong>Severity:</strong> {severity}</p>
                <p><strong>Details:</strong> {recommendation.get("details", "No details available")}</p>
            </div>
            """
        
        if not recommendations_html:
            recommendations_html = "<p>No recommendations available.</p>"
        
        html = html.replace("{{recommendations_html}}", recommendations_html)
        
        # Generate policy results HTML
        policy_results_html = ""
        for result in report_data["validation_results"].get("policy_results", []):
            status = "Compliant" if result.get("compliant", False) else "Non-Compliant"
            status_class = "success" if result.get("compliant", False) else "danger"
            
            policy_results_html += f"""
            <tr>
                <td>{result.get("policy_name", "unknown")}</td>
                <td>{result.get("policy_type", "unknown")}</td>
                <td>{result.get("policy_severity", "medium")}</td>
                <td class="{status_class}">{status}</td>
            </tr>
            """
        
        html = html.replace("{{policy_results_html}}", policy_results_html)
        
        return html
    
    def _generate_pdf_report(self, report_data: Dict[str, Any], snapshot_id: str) -> str:
        """
        Generate a PDF report.
        
        Args:
            report_data: Report data dictionary
            snapshot_id: Unique identifier for the compliance snapshot
            
        Returns:
            Path to the generated PDF file
        """
        # Create file path
        file_path = os.path.join(self.report_dir, f"compliance_report_{snapshot_id}.pdf")
        
        # Generate HTML first
        html_path = self._generate_html_report(report_data, snapshot_id)
        
        try:
            # Convert HTML to PDF using weasyprint
            from weasyprint import HTML
            HTML(html_path).write_pdf(file_path)
            logger.info(f"Generated PDF report: {file_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            file_path = ""
        
        return file_path
    
    def export_report(self, report: Dict[str, Any], format: str = "json") -> Dict[str, Any]:
        """
        Export a report in the specified format.
        
        Args:
            report: Report data dictionary
            format: Export format (json, pdf, html)
            
        Returns:
            Dictionary with export information
        """
        snapshot_id = report.get("snapshot_id", "unknown")
        report_data = report.get("data", {})
        
        if not report_data:
            return {
                "success": False,
                "error": "Report data not found"
            }
        
        if format == "json":
            file_path = self._generate_json_report(report_data, snapshot_id)
        elif format == "html":
            file_path = self._generate_html_report(report_data, snapshot_id)
        elif format == "pdf":
            file_path = self._generate_pdf_report(report_data, snapshot_id)
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}"
            }
        
        if not file_path:
            return {
                "success": False,
                "error": f"Failed to generate {format} report"
            }
        
        return {
            "success": True,
            "format": format,
            "file_path": file_path
        }
