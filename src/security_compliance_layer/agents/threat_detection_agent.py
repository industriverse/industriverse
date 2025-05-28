"""
Threat Detection Agent for the Security & Compliance Layer

This agent monitors for security threats across the Industriverse platform.
It detects, analyzes, and responds to security threats in real-time.

Key capabilities:
1. Threat monitoring and detection
2. Threat intelligence integration
3. Behavioral analysis
4. Anomaly detection
5. Threat response coordination

The Threat Detection Agent provides comprehensive threat monitoring and detection
capabilities to protect the Industriverse platform from security threats.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ThreatDetectionAgent")

class ThreatDetectionAgent:
    """
    Threat Detection Agent for monitoring and detecting security threats
    across the Industriverse platform.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Threat Detection Agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.threat_intelligence = self._load_threat_intelligence()
        self.active_monitors = {}
        self.detection_rules = self._load_detection_rules()
        self.alert_history = []
        self.threat_status = {
            "overall_threat_level": "low",
            "active_threats": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.logger.info("Threat Detection Agent initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load the agent configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing the configuration
        """
        default_config = {
            "monitoring_interval": 60,  # seconds
            "alert_threshold": "medium",
            "auto_response": True,
            "threat_intelligence_update_interval": 3600,  # seconds
            "max_alert_history": 1000,
            "detection_modes": {
                "signature_based": True,
                "anomaly_based": True,
                "behavior_based": True,
                "heuristic_based": True
            },
            "integration": {
                "identity_provider": True,
                "access_control": True,
                "data_security": True,
                "protocol_security": True,
                "policy_governance": True
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    
                self.logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {str(e)}")
                self.logger.info("Using default configuration")
        
        return default_config
    
    def _load_threat_intelligence(self) -> Dict:
        """
        Load threat intelligence data.
        
        Returns:
            Dict containing threat intelligence data
        """
        # In production, this would load from a threat intelligence feed or database
        # For now, we'll use a simple dictionary
        return {
            "indicators": {
                "ip_addresses": [
                    {"value": "192.168.1.100", "threat_type": "command_and_control", "confidence": "high"},
                    {"value": "10.0.0.5", "threat_type": "malware_distribution", "confidence": "medium"}
                ],
                "domains": [
                    {"value": "malicious-domain.com", "threat_type": "phishing", "confidence": "high"},
                    {"value": "suspicious-site.net", "threat_type": "malware_distribution", "confidence": "medium"}
                ],
                "file_hashes": [
                    {"value": "e1a73c9e4e95db7ffcaae7eb1ca5f6b7", "threat_type": "ransomware", "confidence": "high"},
                    {"value": "b2a63c9e4e95db7ffcaae7eb1ca5f6b8", "threat_type": "trojan", "confidence": "medium"}
                ]
            },
            "threat_actors": {
                "APT28": {
                    "aliases": ["Fancy Bear", "Sofacy"],
                    "tactics": ["spear_phishing", "zero_day_exploits", "custom_malware"],
                    "target_sectors": ["government", "defense", "manufacturing"],
                    "threat_level": "high"
                },
                "Lazarus": {
                    "aliases": ["Hidden Cobra", "Guardians of Peace"],
                    "tactics": ["watering_hole_attacks", "ransomware", "wiper_malware"],
                    "target_sectors": ["finance", "critical_infrastructure", "manufacturing"],
                    "threat_level": "high"
                }
            },
            "vulnerabilities": {
                "CVE-2021-44228": {
                    "description": "Log4j Remote Code Execution",
                    "affected_systems": ["Java applications using Log4j"],
                    "severity": "critical",
                    "exploitability": "high"
                },
                "CVE-2021-26855": {
                    "description": "Microsoft Exchange Server Remote Code Execution",
                    "affected_systems": ["Microsoft Exchange Server"],
                    "severity": "critical",
                    "exploitability": "high"
                }
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_detection_rules(self) -> Dict:
        """
        Load threat detection rules.
        
        Returns:
            Dict containing detection rules
        """
        # In production, this would load from a rule database or file
        # For now, we'll use a simple dictionary
        return {
            "signature_based": {
                "malware_signatures": [
                    {"id": "SIG-001", "pattern": "4d5a90000300000004000000ffff", "threat_type": "trojan", "severity": "high"},
                    {"id": "SIG-002", "pattern": "504b0304140000000800", "threat_type": "ransomware", "severity": "critical"}
                ],
                "network_signatures": [
                    {"id": "SIG-101", "pattern": "GET /admin/config.php?action=", "threat_type": "web_attack", "severity": "medium"},
                    {"id": "SIG-102", "pattern": "SELECT * FROM users WHERE username=", "threat_type": "sql_injection", "severity": "high"}
                ]
            },
            "anomaly_based": {
                "authentication": [
                    {"id": "ANO-001", "condition": "login_attempts > 5 in 1 minute", "threat_type": "brute_force", "severity": "medium"},
                    {"id": "ANO-002", "condition": "login_location_change > 1000 km in 1 hour", "threat_type": "account_takeover", "severity": "high"}
                ],
                "network": [
                    {"id": "ANO-101", "condition": "outbound_traffic > 1 GB in 5 minutes", "threat_type": "data_exfiltration", "severity": "high"},
                    {"id": "ANO-102", "condition": "connection_count > 100 in 1 minute", "threat_type": "ddos", "severity": "medium"}
                ],
                "system": [
                    {"id": "ANO-201", "condition": "cpu_usage > 90% for 5 minutes", "threat_type": "resource_abuse", "severity": "medium"},
                    {"id": "ANO-202", "condition": "file_changes > 1000 in 1 minute", "threat_type": "ransomware", "severity": "high"}
                ]
            },
            "behavior_based": {
                "user": [
                    {"id": "BEH-001", "pattern": "access_sensitive_data + download_large_files", "threat_type": "insider_threat", "severity": "high"},
                    {"id": "BEH-002", "pattern": "failed_login + password_reset + login_success", "threat_type": "account_takeover", "severity": "high"}
                ],
                "system": [
                    {"id": "BEH-101", "pattern": "process_injection + network_connection + file_encryption", "threat_type": "ransomware", "severity": "critical"},
                    {"id": "BEH-102", "pattern": "registry_modification + service_creation + scheduled_task", "threat_type": "persistence", "severity": "high"}
                ]
            },
            "heuristic_based": [
                {"id": "HEU-001", "condition": "entropy(file) > 7.8", "threat_type": "encrypted_malware", "severity": "medium"},
                {"id": "HEU-002", "condition": "obfuscation_score > 80", "threat_type": "obfuscated_code", "severity": "medium"}
            ]
        }
    
    def start_monitoring(self):
        """
        Start monitoring for threats.
        """
        self.logger.info("Starting threat monitoring")
        
        # In a real implementation, this would start background threads or processes
        # For now, we'll just log that monitoring has started
        self.monitoring_active = True
        
        # Register monitors for different detection methods
        if self.config["detection_modes"]["signature_based"]:
            self._register_monitor("signature_based", self._monitor_signatures)
        
        if self.config["detection_modes"]["anomaly_based"]:
            self._register_monitor("anomaly_based", self._monitor_anomalies)
        
        if self.config["detection_modes"]["behavior_based"]:
            self._register_monitor("behavior_based", self._monitor_behaviors)
        
        if self.config["detection_modes"]["heuristic_based"]:
            self._register_monitor("heuristic_based", self._monitor_heuristics)
        
        self.logger.info(f"Monitoring active for {len(self.active_monitors)} detection methods")
    
    def stop_monitoring(self):
        """
        Stop monitoring for threats.
        """
        self.logger.info("Stopping threat monitoring")
        self.monitoring_active = False
        self.active_monitors = {}
    
    def _register_monitor(self, method: str, monitor_func):
        """
        Register a monitor function for a detection method.
        
        Args:
            method: Detection method
            monitor_func: Function to call for monitoring
        """
        self.active_monitors[method] = {
            "function": monitor_func,
            "last_run": None,
            "alerts": 0
        }
    
    def _monitor_signatures(self) -> List[Dict]:
        """
        Monitor for signature-based threats.
        
        Returns:
            List of threat alerts
        """
        # In a real implementation, this would scan for known signatures
        # For now, we'll simulate some alerts
        alerts = []
        
        # Simulate malware signature detection
        if random.random() < 0.1:  # 10% chance of detection
            signature = random.choice(self.detection_rules["signature_based"]["malware_signatures"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "signature_based",
                "rule_id": signature["id"],
                "threat_type": signature["threat_type"],
                "severity": signature["severity"],
                "source": {
                    "type": "file",
                    "path": f"/tmp/suspicious_file_{random.randint(1000, 9999)}.bin"
                },
                "details": f"Detected {signature['threat_type']} signature pattern"
            })
        
        # Simulate network signature detection
        if random.random() < 0.05:  # 5% chance of detection
            signature = random.choice(self.detection_rules["signature_based"]["network_signatures"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "signature_based",
                "rule_id": signature["id"],
                "threat_type": signature["threat_type"],
                "severity": signature["severity"],
                "source": {
                    "type": "network",
                    "ip": f"192.168.1.{random.randint(2, 254)}",
                    "port": random.randint(1024, 65535)
                },
                "details": f"Detected {signature['threat_type']} network pattern"
            })
        
        return alerts
    
    def _monitor_anomalies(self) -> List[Dict]:
        """
        Monitor for anomaly-based threats.
        
        Returns:
            List of threat alerts
        """
        # In a real implementation, this would analyze system behavior for anomalies
        # For now, we'll simulate some alerts
        alerts = []
        
        # Simulate authentication anomaly detection
        if random.random() < 0.08:  # 8% chance of detection
            anomaly = random.choice(self.detection_rules["anomaly_based"]["authentication"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "anomaly_based",
                "rule_id": anomaly["id"],
                "threat_type": anomaly["threat_type"],
                "severity": anomaly["severity"],
                "source": {
                    "type": "authentication",
                    "user": f"user_{random.randint(100, 999)}",
                    "ip": f"192.168.1.{random.randint(2, 254)}"
                },
                "details": f"Detected {anomaly['threat_type']} anomaly: {anomaly['condition']}"
            })
        
        # Simulate network anomaly detection
        if random.random() < 0.07:  # 7% chance of detection
            anomaly = random.choice(self.detection_rules["anomaly_based"]["network"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "anomaly_based",
                "rule_id": anomaly["id"],
                "threat_type": anomaly["threat_type"],
                "severity": anomaly["severity"],
                "source": {
                    "type": "network",
                    "ip": f"192.168.1.{random.randint(2, 254)}",
                    "port": random.randint(1024, 65535)
                },
                "details": f"Detected {anomaly['threat_type']} anomaly: {anomaly['condition']}"
            })
        
        return alerts
    
    def _monitor_behaviors(self) -> List[Dict]:
        """
        Monitor for behavior-based threats.
        
        Returns:
            List of threat alerts
        """
        # In a real implementation, this would analyze behavior patterns
        # For now, we'll simulate some alerts
        alerts = []
        
        # Simulate user behavior detection
        if random.random() < 0.06:  # 6% chance of detection
            behavior = random.choice(self.detection_rules["behavior_based"]["user"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "behavior_based",
                "rule_id": behavior["id"],
                "threat_type": behavior["threat_type"],
                "severity": behavior["severity"],
                "source": {
                    "type": "user",
                    "user": f"user_{random.randint(100, 999)}",
                    "ip": f"192.168.1.{random.randint(2, 254)}"
                },
                "details": f"Detected {behavior['threat_type']} behavior pattern: {behavior['pattern']}"
            })
        
        # Simulate system behavior detection
        if random.random() < 0.05:  # 5% chance of detection
            behavior = random.choice(self.detection_rules["behavior_based"]["system"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "behavior_based",
                "rule_id": behavior["id"],
                "threat_type": behavior["threat_type"],
                "severity": behavior["severity"],
                "source": {
                    "type": "system",
                    "host": f"host-{random.randint(100, 999)}",
                    "process": f"process-{random.randint(1000, 9999)}"
                },
                "details": f"Detected {behavior['threat_type']} behavior pattern: {behavior['pattern']}"
            })
        
        return alerts
    
    def _monitor_heuristics(self) -> List[Dict]:
        """
        Monitor for heuristic-based threats.
        
        Returns:
            List of threat alerts
        """
        # In a real implementation, this would apply heuristic analysis
        # For now, we'll simulate some alerts
        alerts = []
        
        # Simulate heuristic detection
        if random.random() < 0.04:  # 4% chance of detection
            heuristic = random.choice(self.detection_rules["heuristic_based"])
            alerts.append({
                "id": f"ALERT-{self._generate_alert_id()}",
                "timestamp": datetime.now().isoformat(),
                "detection_method": "heuristic_based",
                "rule_id": heuristic["id"],
                "threat_type": heuristic["threat_type"],
                "severity": heuristic["severity"],
                "source": {
                    "type": "file",
                    "path": f"/tmp/suspicious_file_{random.randint(1000, 9999)}.bin"
                },
                "details": f"Detected {heuristic['threat_type']} using heuristic: {heuristic['condition']}"
            })
        
        return alerts
    
    def _generate_alert_id(self) -> str:
        """
        Generate a unique alert ID.
        
        Returns:
            Unique alert ID
        """
        timestamp = datetime.now().isoformat()
        random_value = random.randint(1000, 9999)
        hash_input = f"{timestamp}-{random_value}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def check_for_threats(self) -> Dict:
        """
        Check for threats using all active monitors.
        
        Returns:
            Dict containing check results
        """
        if not self.monitoring_active:
            return {
                "status": "error",
                "message": "Threat monitoring is not active",
                "timestamp": datetime.now().isoformat()
            }
        
        all_alerts = []
        
        # Run each active monitor
        for method, monitor in self.active_monitors.items():
            monitor["last_run"] = datetime.now().isoformat()
            alerts = monitor["function"]()
            
            if alerts:
                monitor["alerts"] += len(alerts)
                all_alerts.extend(alerts)
        
        # Process alerts
        for alert in all_alerts:
            # Add to alert history
            self.alert_history.append(alert)
            
            # Trim history if it exceeds the maximum size
            if len(self.alert_history) > self.config["max_alert_history"]:
                self.alert_history = self.alert_history[-self.config["max_alert_history"]:]
            
            # Auto-respond if enabled
            if self.config["auto_response"]:
                self._respond_to_threat(alert)
        
        # Update threat status
        self._update_threat_status()
        
        return {
            "status": "success",
            "alerts_detected": len(all_alerts),
            "alerts": all_alerts,
            "threat_status": self.threat_status,
            "timestamp": datetime.now().isoformat()
        }
    
    def _respond_to_threat(self, alert: Dict) -> Dict:
        """
        Respond to a detected threat.
        
        Args:
            alert: Threat alert
            
        Returns:
            Dict containing response result
        """
        # In a real implementation, this would take action based on the threat
        # For now, we'll just log the response
        severity = alert.get("severity", "low")
        threat_type = alert.get("threat_type", "unknown")
        source = alert.get("source", {})
        
        response = {
            "alert_id": alert["id"],
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        # Determine response actions based on severity and threat type
        if severity == "critical":
            if source.get("type") == "network":
                response["actions"].append({
                    "type": "block_ip",
                    "target": source.get("ip"),
                    "duration": "permanent",
                    "status": "success"
                })
            
            if source.get("type") == "file":
                response["actions"].append({
                    "type": "quarantine_file",
                    "target": source.get("path"),
                    "status": "success"
                })
            
            if source.get("type") == "user":
                response["actions"].append({
                    "type": "lock_account",
                    "target": source.get("user"),
                    "duration": "until_review",
                    "status": "success"
                })
            
            response["actions"].append({
                "type": "create_incident",
                "severity": "critical",
                "assigned_to": "security_team",
                "status": "success"
            })
        
        elif severity == "high":
            if source.get("type") == "network":
                response["actions"].append({
                    "type": "monitor_ip",
                    "target": source.get("ip"),
                    "duration": "24_hours",
                    "status": "success"
                })
            
            if source.get("type") == "file":
                response["actions"].append({
                    "type": "scan_file",
                    "target": source.get("path"),
                    "status": "success"
                })
            
            if source.get("type") == "user":
                response["actions"].append({
                    "type": "require_mfa",
                    "target": source.get("user"),
                    "duration": "7_days",
                    "status": "success"
                })
            
            response["actions"].append({
                "type": "create_incident",
                "severity": "high",
                "assigned_to": "security_team",
                "status": "success"
            })
        
        elif severity == "medium":
            response["actions"].append({
                "type": "log_alert",
                "details": f"Medium severity {threat_type} alert logged",
                "status": "success"
            })
            
            response["actions"].append({
                "type": "create_ticket",
                "severity": "medium",
                "assigned_to": "security_analyst",
                "status": "success"
            })
        
        else:  # low severity
            response["actions"].append({
                "type": "log_alert",
                "details": f"Low severity {threat_type} alert logged",
                "status": "success"
            })
        
        self.logger.info(f"Responded to {severity} severity {threat_type} threat: {response['actions']}")
        
        return response
    
    def _update_threat_status(self):
        """
        Update the overall threat status.
        """
        # Count active threats by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        # Consider alerts from the last hour as "active"
        one_hour_ago = datetime.now().timestamp() - 3600
        
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert["timestamp"]).timestamp()
            if alert_time >= one_hour_ago:
                severity = alert.get("severity", "low")
                if severity in severity_counts:
                    severity_counts[severity] += 1
        
        # Determine overall threat level
        if severity_counts["critical"] > 0:
            overall_threat_level = "critical"
        elif severity_counts["high"] > 0:
            overall_threat_level = "high"
        elif severity_counts["medium"] > 0:
            overall_threat_level = "medium"
        else:
            overall_threat_level = "low"
        
        # Update threat status
        self.threat_status = {
            "overall_threat_level": overall_threat_level,
            "active_threats": sum(severity_counts.values()),
            "severity_breakdown": severity_counts,
            "last_updated": datetime.now().isoformat()
        }
    
    def update_threat_intelligence(self) -> Dict:
        """
        Update threat intelligence data.
        
        Returns:
            Dict containing update result
        """
        # In a real implementation, this would fetch updates from threat intelligence feeds
        # For now, we'll just simulate an update
        self.logger.info("Updating threat intelligence")
        
        # Simulate updating indicators
        new_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        self.threat_intelligence["indicators"]["ip_addresses"].append({
            "value": new_ip,
            "threat_type": "command_and_control",
            "confidence": "medium"
        })
        
        new_domain = f"malicious-{random.randint(1000, 9999)}.com"
        self.threat_intelligence["indicators"]["domains"].append({
            "value": new_domain,
            "threat_type": "phishing",
            "confidence": "high"
        })
        
        # Update last updated timestamp
        self.threat_intelligence["last_updated"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Threat intelligence updated",
            "new_indicators": 2,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_threat_status(self) -> Dict:
        """
        Get the current threat status.
        
        Returns:
            Dict containing threat status
        """
        return {
            "status": "success",
            "threat_status": self.threat_status,
            "monitoring_active": self.monitoring_active,
            "active_monitors": list(self.active_monitors.keys()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_alert_history(self, limit: int = None, severity: str = None, threat_type: str = None) -> Dict:
        """
        Get the alert history.
        
        Args:
            limit: Maximum number of alerts to return
            severity: Filter by severity
            threat_type: Filter by threat type
            
        Returns:
            Dict containing alert history
        """
        filtered_history = self.alert_history
        
        if severity:
            filtered_history = [a for a in filtered_history if a.get("severity") == severity]
        
        if threat_type:
            filtered_history = [a for a in filtered_history if a.get("threat_type") == threat_type]
        
        # Sort by timestamp (newest first)
        filtered_history = sorted(
            filtered_history,
            key=lambda a: datetime.fromisoformat(a["timestamp"]).timestamp(),
            reverse=True
        )
        
        if limit:
            filtered_history = filtered_history[:limit]
        
        return {
            "status": "success",
            "total_alerts": len(self.alert_history),
            "filtered_alerts": len(filtered_history),
            "alerts": filtered_history,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_threat_intelligence(self, indicator_type: str = None, value: str = None) -> Dict:
        """
        Get threat intelligence data.
        
        Args:
            indicator_type: Type of indicator (ip_addresses, domains, file_hashes)
            value: Specific indicator value to look up
            
        Returns:
            Dict containing threat intelligence data
        """
        if indicator_type and indicator_type not in self.threat_intelligence["indicators"]:
            return {
                "status": "error",
                "message": f"Unknown indicator type: {indicator_type}",
                "timestamp": datetime.now().isoformat()
            }
        
        if indicator_type and value:
            # Look up specific indicator
            indicators = self.threat_intelligence["indicators"][indicator_type]
            matching_indicators = [i for i in indicators if i["value"] == value]
            
            if not matching_indicators:
                return {
                    "status": "success",
                    "found": False,
                    "message": f"No {indicator_type} indicator found for value: {value}",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "status": "success",
                "found": True,
                "indicator": matching_indicators[0],
                "timestamp": datetime.now().isoformat()
            }
        
        elif indicator_type:
            # Return all indicators of a specific type
            return {
                "status": "success",
                "indicators": self.threat_intelligence["indicators"][indicator_type],
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            # Return all threat intelligence data
            return {
                "status": "success",
                "threat_intelligence": self.threat_intelligence,
                "timestamp": datetime.now().isoformat()
            }

# Example usage
if __name__ == "__main__":
    agent = ThreatDetectionAgent()
    agent.start_monitoring()
    
    # Check for threats
    threats = agent.check_for_threats()
    print(f"Threat check results: {threats}")
    
    # Get threat status
    status = agent.get_threat_status()
    print(f"Threat status: {status}")
    
    # Get alert history
    history = agent.get_alert_history(limit=5)
    print(f"Alert history: {history}")
    
    # Get threat intelligence
    intel = agent.get_threat_intelligence()
    print(f"Threat intelligence: {intel}")
