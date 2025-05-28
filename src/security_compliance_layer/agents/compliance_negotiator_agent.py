"""
Compliance Negotiator Agent for the Security & Compliance Layer

This agent facilitates compliance negotiations between different systems, layers, and external entities.
It ensures that compliance requirements are properly communicated, negotiated, and enforced.

Key capabilities:
1. Compliance requirement negotiation
2. Compliance attestation exchange
3. Cross-framework mapping
4. Compliance evidence collection
5. Regulatory framework adaptation

The Compliance Negotiator Agent enables dynamic compliance negotiations across different
regulatory frameworks, jurisdictions, and security domains.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ComplianceNegotiatorAgent")

class ComplianceNegotiatorAgent:
    """
    Compliance Negotiator Agent for facilitating compliance negotiations between
    different systems, layers, and external entities.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Compliance Negotiator Agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.compliance_frameworks = self._load_compliance_frameworks()
        self.active_negotiations = {}
        self.negotiation_history = []
        self.attestation_cache = {}
        
        self.logger.info("Compliance Negotiator Agent initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load the agent configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing the configuration
        """
        default_config = {
            "negotiation_timeout": 300,  # seconds
            "attestation_cache_ttl": 3600,  # seconds
            "default_compliance_level": "standard",
            "auto_negotiate": True,
            "evidence_collection": True,
            "max_negotiation_history": 1000,
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
    
    def _load_compliance_frameworks(self) -> Dict:
        """
        Load compliance frameworks.
        
        Returns:
            Dict containing the compliance frameworks
        """
        # In production, this would load from a compliance framework store or database
        # For now, we'll use a simple dictionary
        return {
            "GDPR": {
                "version": "2018",
                "requirements": {
                    "data_protection": {
                        "level": "high",
                        "controls": ["encryption", "access_control", "data_minimization", "purpose_limitation"]
                    },
                    "consent": {
                        "level": "high",
                        "controls": ["explicit_consent", "withdrawal_mechanism", "purpose_specification"]
                    },
                    "data_subject_rights": {
                        "level": "high",
                        "controls": ["access", "rectification", "erasure", "portability", "objection"]
                    },
                    "breach_notification": {
                        "level": "high",
                        "controls": ["detection", "notification", "documentation"]
                    }
                },
                "mappings": {
                    "NIST": {
                        "data_protection": ["SC-8", "SC-13", "AC-3", "AC-6"],
                        "consent": ["PM-9"],
                        "data_subject_rights": ["IP-4"],
                        "breach_notification": ["IR-6"]
                    },
                    "ISO27001": {
                        "data_protection": ["A.8.2", "A.10.1", "A.9.2", "A.9.4"],
                        "consent": ["A.18.1"],
                        "data_subject_rights": ["A.18.1"],
                        "breach_notification": ["A.16.1"]
                    }
                }
            },
            "NIST": {
                "version": "800-53 Rev 5",
                "requirements": {
                    "access_control": {
                        "level": "high",
                        "controls": ["identification", "authentication", "authorization", "least_privilege"]
                    },
                    "audit_logging": {
                        "level": "medium",
                        "controls": ["generation", "review", "protection", "retention"]
                    },
                    "system_protection": {
                        "level": "high",
                        "controls": ["boundary_protection", "cryptography", "malware_protection"]
                    },
                    "incident_response": {
                        "level": "medium",
                        "controls": ["planning", "detection", "analysis", "containment", "recovery"]
                    }
                },
                "mappings": {
                    "GDPR": {
                        "access_control": ["data_protection"],
                        "audit_logging": ["data_protection", "breach_notification"],
                        "system_protection": ["data_protection"],
                        "incident_response": ["breach_notification"]
                    },
                    "ISO27001": {
                        "access_control": ["A.9.2", "A.9.4"],
                        "audit_logging": ["A.12.4"],
                        "system_protection": ["A.13.1", "A.10.1", "A.8.3"],
                        "incident_response": ["A.16.1"]
                    }
                }
            },
            "ISO27001": {
                "version": "2013",
                "requirements": {
                    "information_security_policies": {
                        "level": "medium",
                        "controls": ["documentation", "review"]
                    },
                    "organization_of_information_security": {
                        "level": "medium",
                        "controls": ["roles_responsibilities", "segregation_of_duties", "mobile_devices", "teleworking"]
                    },
                    "human_resource_security": {
                        "level": "medium",
                        "controls": ["screening", "terms_conditions", "awareness", "disciplinary_process"]
                    },
                    "asset_management": {
                        "level": "medium",
                        "controls": ["inventory", "ownership", "classification", "handling", "disposal"]
                    }
                },
                "mappings": {
                    "GDPR": {
                        "information_security_policies": ["data_protection"],
                        "organization_of_information_security": ["data_protection"],
                        "human_resource_security": ["data_protection"],
                        "asset_management": ["data_protection", "data_subject_rights"]
                    },
                    "NIST": {
                        "information_security_policies": ["PM-1"],
                        "organization_of_information_security": ["PM-2", "AC-5"],
                        "human_resource_security": ["PS-1", "PS-3", "AT-1", "PS-8"],
                        "asset_management": ["CM-8", "PM-5", "MP-4", "MP-6"]
                    }
                }
            },
            "HIPAA": {
                "version": "2013",
                "requirements": {
                    "privacy_rule": {
                        "level": "high",
                        "controls": ["notice", "access", "disclosure_accounting", "amendment"]
                    },
                    "security_rule": {
                        "level": "high",
                        "controls": ["risk_analysis", "risk_management", "sanction_policy", "information_system_activity_review"]
                    },
                    "breach_notification_rule": {
                        "level": "high",
                        "controls": ["breach_definition", "notification", "timing", "content"]
                    }
                },
                "mappings": {
                    "GDPR": {
                        "privacy_rule": ["data_protection", "data_subject_rights", "consent"],
                        "security_rule": ["data_protection"],
                        "breach_notification_rule": ["breach_notification"]
                    },
                    "NIST": {
                        "privacy_rule": ["IP-1", "IP-2", "IP-3", "IP-4"],
                        "security_rule": ["RA-1", "RA-3", "PM-9", "AU-6"],
                        "breach_notification_rule": ["IR-6"]
                    },
                    "ISO27001": {
                        "privacy_rule": ["A.18.1"],
                        "security_rule": ["A.8.2", "A.12.4", "A.18.1"],
                        "breach_notification_rule": ["A.16.1"]
                    }
                }
            }
        }
    
    def start_negotiation(self, negotiation_id: str, requester: Dict, responder: Dict, 
                         framework: str, requirements: List[str]) -> Dict:
        """
        Start a compliance negotiation.
        
        Args:
            negotiation_id: Unique identifier for the negotiation
            requester: Information about the requester
            responder: Information about the responder
            framework: Compliance framework to use
            requirements: List of requirements to negotiate
            
        Returns:
            Dict containing the negotiation status
        """
        if negotiation_id in self.active_negotiations:
            return {
                "status": "error",
                "message": f"Negotiation with ID {negotiation_id} already exists",
                "timestamp": datetime.now().isoformat()
            }
        
        if framework not in self.compliance_frameworks:
            return {
                "status": "error",
                "message": f"Unknown compliance framework: {framework}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Validate requirements
        framework_requirements = self.compliance_frameworks[framework]["requirements"]
        invalid_requirements = [r for r in requirements if r not in framework_requirements]
        
        if invalid_requirements:
            return {
                "status": "error",
                "message": f"Invalid requirements for framework {framework}: {', '.join(invalid_requirements)}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create negotiation
        negotiation = {
            "id": negotiation_id,
            "requester": requester,
            "responder": responder,
            "framework": framework,
            "requirements": requirements,
            "status": "initiated",
            "start_time": datetime.now().isoformat(),
            "timeout": time.time() + self.config["negotiation_timeout"],
            "attestations": {},
            "evidence": {},
            "result": None
        }
        
        self.active_negotiations[negotiation_id] = negotiation
        
        self.logger.info(f"Started negotiation {negotiation_id} for framework {framework}")
        
        # If auto-negotiate is enabled, start the negotiation process
        if self.config["auto_negotiate"]:
            self._process_negotiation(negotiation_id)
        
        return {
            "status": "success",
            "negotiation_id": negotiation_id,
            "message": f"Negotiation started for framework {framework}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_negotiation(self, negotiation_id: str) -> Dict:
        """
        Process a negotiation.
        
        Args:
            negotiation_id: Unique identifier for the negotiation
            
        Returns:
            Dict containing the negotiation result
        """
        if negotiation_id not in self.active_negotiations:
            return {
                "status": "error",
                "message": f"Unknown negotiation ID: {negotiation_id}",
                "timestamp": datetime.now().isoformat()
            }
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Check if negotiation has timed out
        if time.time() > negotiation["timeout"]:
            negotiation["status"] = "timeout"
            negotiation["result"] = {
                "status": "failed",
                "reason": "Negotiation timed out",
                "timestamp": datetime.now().isoformat()
            }
            
            # Move to history
            self._complete_negotiation(negotiation_id)
            
            return negotiation["result"]
        
        # Get framework and requirements
        framework = negotiation["framework"]
        requirements = negotiation["requirements"]
        framework_data = self.compliance_frameworks[framework]
        
        # Process each requirement
        for requirement in requirements:
            # Skip if already attested
            if requirement in negotiation["attestations"]:
                continue
            
            requirement_data = framework_data["requirements"][requirement]
            controls = requirement_data["controls"]
            
            # Check if we have attestations for this requirement
            attestation = self._get_attestation(
                negotiation["responder"], 
                framework, 
                requirement
            )
            
            if attestation:
                negotiation["attestations"][requirement] = attestation
            else:
                # Request attestation from responder
                # In a real implementation, this would make an API call to the responder
                # For now, we'll simulate a successful attestation
                attestation = {
                    "framework": framework,
                    "requirement": requirement,
                    "controls": {control: True for control in controls},
                    "timestamp": datetime.now().isoformat(),
                    "expiry": time.time() + 86400  # 24 hours
                }
                
                negotiation["attestations"][requirement] = attestation
                
                # Cache the attestation
                self._cache_attestation(
                    negotiation["responder"],
                    framework,
                    requirement,
                    attestation
                )
            
            # Collect evidence if enabled
            if self.config["evidence_collection"]:
                evidence = self._collect_evidence(
                    negotiation["responder"],
                    framework,
                    requirement
                )
                
                if evidence:
                    if requirement not in negotiation["evidence"]:
                        negotiation["evidence"][requirement] = []
                    
                    negotiation["evidence"][requirement].append(evidence)
        
        # Check if all requirements have been attested
        if len(negotiation["attestations"]) == len(requirements):
            negotiation["status"] = "completed"
            negotiation["result"] = {
                "status": "success",
                "attestations": negotiation["attestations"],
                "evidence": negotiation["evidence"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Move to history
            self._complete_negotiation(negotiation_id)
        else:
            negotiation["status"] = "in_progress"
        
        return {
            "status": negotiation["status"],
            "progress": f"{len(negotiation['attestations'])}/{len(requirements)} requirements attested",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_attestation(self, entity: Dict, framework: str, requirement: str) -> Optional[Dict]:
        """
        Get an attestation from the cache.
        
        Args:
            entity: Entity information
            framework: Compliance framework
            requirement: Requirement name
            
        Returns:
            Dict containing the attestation, or None if not found
        """
        entity_id = entity.get("id")
        
        if not entity_id:
            return None
        
        cache_key = f"{entity_id}:{framework}:{requirement}"
        
        if cache_key in self.attestation_cache:
            attestation = self.attestation_cache[cache_key]
            
            # Check if attestation has expired
            if attestation["expiry"] < time.time():
                del self.attestation_cache[cache_key]
                return None
            
            return attestation
        
        return None
    
    def _cache_attestation(self, entity: Dict, framework: str, requirement: str, attestation: Dict):
        """
        Cache an attestation.
        
        Args:
            entity: Entity information
            framework: Compliance framework
            requirement: Requirement name
            attestation: Attestation data
        """
        entity_id = entity.get("id")
        
        if not entity_id:
            return
        
        cache_key = f"{entity_id}:{framework}:{requirement}"
        
        self.attestation_cache[cache_key] = attestation
    
    def _collect_evidence(self, entity: Dict, framework: str, requirement: str) -> Optional[Dict]:
        """
        Collect evidence for a requirement.
        
        Args:
            entity: Entity information
            framework: Compliance framework
            requirement: Requirement name
            
        Returns:
            Dict containing the evidence, or None if not found
        """
        # In a real implementation, this would collect evidence from the entity
        # For now, we'll simulate evidence collection
        return {
            "type": "log",
            "source": "system",
            "content": f"Evidence for {framework}:{requirement}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _complete_negotiation(self, negotiation_id: str):
        """
        Complete a negotiation and move it to history.
        
        Args:
            negotiation_id: Negotiation ID
        """
        if negotiation_id not in self.active_negotiations:
            return
        
        negotiation = self.active_negotiations[negotiation_id]
        
        # Add to history
        self.negotiation_history.append(negotiation)
        
        # Trim history if it exceeds the maximum size
        if len(self.negotiation_history) > self.config["max_negotiation_history"]:
            self.negotiation_history = self.negotiation_history[-self.config["max_negotiation_history"]:]
        
        # Remove from active negotiations
        del self.active_negotiations[negotiation_id]
        
        self.logger.info(f"Completed negotiation {negotiation_id} with status {negotiation['status']}")
    
    def get_negotiation_status(self, negotiation_id: str) -> Dict:
        """
        Get the status of a negotiation.
        
        Args:
            negotiation_id: Negotiation ID
            
        Returns:
            Dict containing the negotiation status
        """
        # Check active negotiations
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            
            return {
                "status": negotiation["status"],
                "framework": negotiation["framework"],
                "requirements": negotiation["requirements"],
                "progress": f"{len(negotiation['attestations'])}/{len(negotiation['requirements'])} requirements attested",
                "start_time": negotiation["start_time"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Check negotiation history
        for negotiation in self.negotiation_history:
            if negotiation["id"] == negotiation_id:
                return {
                    "status": negotiation["status"],
                    "framework": negotiation["framework"],
                    "requirements": negotiation["requirements"],
                    "result": negotiation["result"],
                    "start_time": negotiation["start_time"],
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "error",
            "message": f"Unknown negotiation ID: {negotiation_id}",
            "timestamp": datetime.now().isoformat()
        }
    
    def map_requirements(self, source_framework: str, target_framework: str, requirements: List[str]) -> Dict:
        """
        Map requirements from one framework to another.
        
        Args:
            source_framework: Source compliance framework
            target_framework: Target compliance framework
            requirements: List of requirements to map
            
        Returns:
            Dict containing the mapped requirements
        """
        if source_framework not in self.compliance_frameworks:
            return {
                "status": "error",
                "message": f"Unknown source framework: {source_framework}",
                "timestamp": datetime.now().isoformat()
            }
        
        if target_framework not in self.compliance_frameworks:
            return {
                "status": "error",
                "message": f"Unknown target framework: {target_framework}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Validate requirements
        source_framework_requirements = self.compliance_frameworks[source_framework]["requirements"]
        invalid_requirements = [r for r in requirements if r not in source_framework_requirements]
        
        if invalid_requirements:
            return {
                "status": "error",
                "message": f"Invalid requirements for framework {source_framework}: {', '.join(invalid_requirements)}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get mappings
        framework_data = self.compliance_frameworks[source_framework]
        mappings = framework_data.get("mappings", {}).get(target_framework, {})
        
        if not mappings:
            return {
                "status": "error",
                "message": f"No mappings available from {source_framework} to {target_framework}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Map requirements
        mapped_requirements = {}
        
        for requirement in requirements:
            if requirement in mappings:
                mapped_requirements[requirement] = mappings[requirement]
            else:
                mapped_requirements[requirement] = []
        
        return {
            "status": "success",
            "source_framework": source_framework,
            "target_framework": target_framework,
            "mapped_requirements": mapped_requirements,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_compliance_frameworks(self) -> Dict:
        """
        Get the list of supported compliance frameworks.
        
        Returns:
            Dict containing the supported compliance frameworks
        """
        frameworks = {}
        
        for framework, data in self.compliance_frameworks.items():
            frameworks[framework] = {
                "version": data["version"],
                "requirements": list(data["requirements"].keys()),
                "mappings": list(data.get("mappings", {}).keys())
            }
        
        return {
            "status": "success",
            "frameworks": frameworks,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_framework_requirements(self, framework: str) -> Dict:
        """
        Get the requirements for a compliance framework.
        
        Args:
            framework: Compliance framework
            
        Returns:
            Dict containing the framework requirements
        """
        if framework not in self.compliance_frameworks:
            return {
                "status": "error",
                "message": f"Unknown framework: {framework}",
                "timestamp": datetime.now().isoformat()
            }
        
        framework_data = self.compliance_frameworks[framework]
        
        return {
            "status": "success",
            "framework": framework,
            "version": framework_data["version"],
            "requirements": framework_data["requirements"],
            "timestamp": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    agent = ComplianceNegotiatorAgent()
    
    # Get supported frameworks
    frameworks = agent.get_compliance_frameworks()
    print(f"Supported frameworks: {frameworks}")
    
    # Get framework requirements
    requirements = agent.get_framework_requirements("GDPR")
    print(f"GDPR requirements: {requirements}")
    
    # Map requirements
    mapped = agent.map_requirements("GDPR", "NIST", ["data_protection", "consent"])
    print(f"Mapped requirements: {mapped}")
    
    # Start a negotiation
    negotiation = agent.start_negotiation(
        "test-negotiation",
        {"id": "requester-1", "name": "Requester System"},
        {"id": "responder-1", "name": "Responder System"},
        "GDPR",
        ["data_protection", "consent"]
    )
    print(f"Negotiation started: {negotiation}")
    
    # Get negotiation status
    status = agent.get_negotiation_status("test-negotiation")
    print(f"Negotiation status: {status}")
