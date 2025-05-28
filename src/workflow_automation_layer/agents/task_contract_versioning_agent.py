"""
Task Contract Versioning Agent Module for the Workflow Automation Layer.

This agent manages versioning, tracking, and approval of task contracts,
ensuring consistency and compatibility across workflow versions.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskContractVersioningAgent:
    """Agent for managing task contract versioning and approvals."""

    def __init__(self, workflow_runtime):
        """Initialize the task contract versioning agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.contract_versions = {}  # Store contract versions by contract_id
        self.contract_approvals = {}  # Store approvals by contract_id and version
        self.contract_dependencies = {}  # Store dependencies between contracts
        self.agent_id = "workflow-contract-versioning-agent"
        self.agent_capabilities = ["contract_versioning", "approval_tracking", "compatibility_checking"]
        self.supported_protocols = ["MCP", "A2A"]
        
        logger.info("Task Contract Versioning Agent initialized")

    async def register_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new task contract or a new version of an existing contract.

        Args:
            contract_data: Contract data including schema, version, dependencies, etc.

        Returns:
            Dict containing registration status and details.
        """
        try:
            # Validate required fields
            required_fields = ["contract_id", "schema", "version"]
            for field in required_fields:
                if field not in contract_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            contract_id = contract_data["contract_id"]
            version = contract_data["version"]
            
            # Initialize contract versions if not exists
            if contract_id not in self.contract_versions:
                self.contract_versions[contract_id] = {}
            
            # Check if version already exists
            if version in self.contract_versions[contract_id]:
                return {
                    "success": False,
                    "error": f"Contract version {version} already exists for contract {contract_id}"
                }
            
            # Add timestamp
            contract_data["registered_at"] = datetime.utcnow().isoformat()
            
            # Store contract version
            self.contract_versions[contract_id][version] = contract_data
            
            # Initialize approvals for this version
            if contract_id not in self.contract_approvals:
                self.contract_approvals[contract_id] = {}
            self.contract_approvals[contract_id][version] = {
                "approvals": [],
                "status": "pending"
            }
            
            # Store dependencies
            if "dependencies" in contract_data:
                self.contract_dependencies[f"{contract_id}:{version}"] = contract_data["dependencies"]
            
            # Log registration
            logger.info(f"Registered contract {contract_id} version {version}")
            
            # Check compatibility with dependent contracts
            compatibility_issues = await self._check_compatibility(contract_id, version)
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version": version,
                "status": "registered",
                "compatibility_issues": compatibility_issues
            }
            
        except Exception as e:
            logger.error(f"Error registering contract: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def approve_contract(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve a contract version.

        Args:
            approval_data: Approval data including contract_id, version, approver, etc.

        Returns:
            Dict containing approval status and details.
        """
        try:
            # Validate required fields
            required_fields = ["contract_id", "version", "approver", "approval_type"]
            for field in required_fields:
                if field not in approval_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            contract_id = approval_data["contract_id"]
            version = approval_data["version"]
            
            # Check if contract and version exist
            if (contract_id not in self.contract_versions or
                    version not in self.contract_versions[contract_id]):
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version} not found"
                }
            
            # Add timestamp
            approval_data["approved_at"] = datetime.utcnow().isoformat()
            
            # Add approval
            self.contract_approvals[contract_id][version]["approvals"].append(approval_data)
            
            # Check if all required approvals are received
            contract = self.contract_versions[contract_id][version]
            required_approvals = contract.get("required_approvals", [])
            received_approvals = set(a["approver"] for a in self.contract_approvals[contract_id][version]["approvals"])
            
            all_approved = all(approver in received_approvals for approver in required_approvals)
            
            if all_approved:
                self.contract_approvals[contract_id][version]["status"] = "approved"
                logger.info(f"Contract {contract_id} version {version} fully approved")
            else:
                logger.info(f"Contract {contract_id} version {version} partially approved")
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version": version,
                "status": self.contract_approvals[contract_id][version]["status"],
                "approvals_received": len(self.contract_approvals[contract_id][version]["approvals"]),
                "approvals_required": len(required_approvals),
                "pending_approvers": [a for a in required_approvals if a not in received_approvals]
            }
            
        except Exception as e:
            logger.error(f"Error approving contract: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_contract_version(self, contract_id: str, version: str = None) -> Dict[str, Any]:
        """Get a specific contract version or the latest version.

        Args:
            contract_id: ID of the contract.
            version: Specific version to get, or None for latest.

        Returns:
            Dict containing contract data.
        """
        try:
            if contract_id not in self.contract_versions:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} not found"
                }
            
            if version is None:
                # Get latest version
                latest_version = max(self.contract_versions[contract_id].keys())
                version = latest_version
            elif version not in self.contract_versions[contract_id]:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version} not found"
                }
            
            contract_data = self.contract_versions[contract_id][version]
            approval_data = self.contract_approvals[contract_id][version]
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version": version,
                "contract_data": contract_data,
                "approval_status": approval_data["status"],
                "approvals": approval_data["approvals"]
            }
            
        except Exception as e:
            logger.error(f"Error getting contract version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_contract_versions(self, contract_id: str) -> Dict[str, Any]:
        """List all versions of a contract.

        Args:
            contract_id: ID of the contract.

        Returns:
            Dict containing list of contract versions.
        """
        try:
            if contract_id not in self.contract_versions:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} not found"
                }
            
            versions = []
            for version, contract_data in self.contract_versions[contract_id].items():
                approval_data = self.contract_approvals[contract_id][version]
                versions.append({
                    "version": version,
                    "registered_at": contract_data["registered_at"],
                    "approval_status": approval_data["status"],
                    "approvals_count": len(approval_data["approvals"])
                })
            
            # Sort by version (assuming semantic versioning)
            versions.sort(key=lambda v: [int(x) for x in v["version"].split(".")])
            
            return {
                "success": True,
                "contract_id": contract_id,
                "versions": versions
            }
            
        except Exception as e:
            logger.error(f"Error listing contract versions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def compare_contract_versions(self, contract_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a contract.

        Args:
            contract_id: ID of the contract.
            version1: First version to compare.
            version2: Second version to compare.

        Returns:
            Dict containing comparison results.
        """
        try:
            if contract_id not in self.contract_versions:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} not found"
                }
            
            if version1 not in self.contract_versions[contract_id]:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version1} not found"
                }
            
            if version2 not in self.contract_versions[contract_id]:
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version2} not found"
                }
            
            contract1 = self.contract_versions[contract_id][version1]
            contract2 = self.contract_versions[contract_id][version2]
            
            # Compare schemas
            schema1 = contract1["schema"]
            schema2 = contract2["schema"]
            
            # Identify added, removed, and modified fields
            added_fields = []
            removed_fields = []
            modified_fields = []
            
            # Compare input schema
            if "input" in schema1 and "input" in schema2:
                input1_fields = set(schema1["input"].keys())
                input2_fields = set(schema2["input"].keys())
                
                for field in input2_fields - input1_fields:
                    added_fields.append(f"input.{field}")
                
                for field in input1_fields - input2_fields:
                    removed_fields.append(f"input.{field}")
                
                for field in input1_fields.intersection(input2_fields):
                    if schema1["input"][field] != schema2["input"][field]:
                        modified_fields.append(f"input.{field}")
            
            # Compare output schema
            if "output" in schema1 and "output" in schema2:
                output1_fields = set(schema1["output"].keys())
                output2_fields = set(schema2["output"].keys())
                
                for field in output2_fields - output1_fields:
                    added_fields.append(f"output.{field}")
                
                for field in output1_fields - output2_fields:
                    removed_fields.append(f"output.{field}")
                
                for field in output1_fields.intersection(output2_fields):
                    if schema1["output"][field] != schema2["output"][field]:
                        modified_fields.append(f"output.{field}")
            
            # Compare dependencies
            dependencies1 = contract1.get("dependencies", [])
            dependencies2 = contract2.get("dependencies", [])
            
            added_dependencies = [d for d in dependencies2 if d not in dependencies1]
            removed_dependencies = [d for d in dependencies1 if d not in dependencies2]
            
            # Determine compatibility type
            if removed_fields or modified_fields:
                compatibility = "breaking"
            elif added_fields:
                compatibility = "non-breaking"
            else:
                compatibility = "identical"
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version1": version1,
                "version2": version2,
                "compatibility": compatibility,
                "changes": {
                    "added_fields": added_fields,
                    "removed_fields": removed_fields,
                    "modified_fields": modified_fields,
                    "added_dependencies": added_dependencies,
                    "removed_dependencies": removed_dependencies
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing contract versions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _check_compatibility(self, contract_id: str, version: str) -> List[Dict[str, Any]]:
        """Check compatibility with dependent contracts.

        Args:
            contract_id: ID of the contract.
            version: Version of the contract.

        Returns:
            List of compatibility issues.
        """
        issues = []
        
        # Find all contracts that depend on this one
        for dep_key, dependencies in self.contract_dependencies.items():
            dep_contract_id, dep_version = dep_key.split(":")
            
            # Check if this contract is in dependencies
            for dependency in dependencies:
                if dependency.get("contract_id") == contract_id:
                    # Check if version constraint is specified
                    version_constraint = dependency.get("version_constraint")
                    if version_constraint:
                        # Simple version constraint check (in real implementation, use semver)
                        if version_constraint.startswith(">="):
                            min_version = version_constraint[2:]
                            if version < min_version:
                                issues.append({
                                    "dependent_contract_id": dep_contract_id,
                                    "dependent_version": dep_version,
                                    "issue": f"Version {version} is less than minimum required version {min_version}"
                                })
                        elif version_constraint.startswith("=="):
                            exact_version = version_constraint[2:]
                            if version != exact_version:
                                issues.append({
                                    "dependent_contract_id": dep_contract_id,
                                    "dependent_version": dep_version,
                                    "issue": f"Version {version} does not match required version {exact_version}"
                                })
        
        return issues

    async def publish_contract(self, publish_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish an approved contract version.

        Args:
            publish_data: Publish data including contract_id, version, etc.

        Returns:
            Dict containing publish status and details.
        """
        try:
            # Validate required fields
            required_fields = ["contract_id", "version"]
            for field in required_fields:
                if field not in publish_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            contract_id = publish_data["contract_id"]
            version = publish_data["version"]
            
            # Check if contract and version exist
            if (contract_id not in self.contract_versions or
                    version not in self.contract_versions[contract_id]):
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version} not found"
                }
            
            # Check if contract is approved
            if self.contract_approvals[contract_id][version]["status"] != "approved":
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version} is not approved"
                }
            
            # Update contract status
            self.contract_versions[contract_id][version]["status"] = "published"
            self.contract_versions[contract_id][version]["published_at"] = datetime.utcnow().isoformat()
            
            # Notify workflow runtime
            await self.workflow_runtime.update_task_contract(
                contract_id, 
                version, 
                self.contract_versions[contract_id][version]
            )
            
            logger.info(f"Published contract {contract_id} version {version}")
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version": version,
                "status": "published",
                "published_at": self.contract_versions[contract_id][version]["published_at"]
            }
            
        except Exception as e:
            logger.error(f"Error publishing contract: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def deprecate_contract(self, deprecate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deprecate a contract version.

        Args:
            deprecate_data: Deprecate data including contract_id, version, reason, etc.

        Returns:
            Dict containing deprecation status and details.
        """
        try:
            # Validate required fields
            required_fields = ["contract_id", "version", "reason"]
            for field in required_fields:
                if field not in deprecate_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            contract_id = deprecate_data["contract_id"]
            version = deprecate_data["version"]
            reason = deprecate_data["reason"]
            
            # Check if contract and version exist
            if (contract_id not in self.contract_versions or
                    version not in self.contract_versions[contract_id]):
                return {
                    "success": False,
                    "error": f"Contract {contract_id} version {version} not found"
                }
            
            # Update contract status
            self.contract_versions[contract_id][version]["status"] = "deprecated"
            self.contract_versions[contract_id][version]["deprecated_at"] = datetime.utcnow().isoformat()
            self.contract_versions[contract_id][version]["deprecation_reason"] = reason
            
            # Notify workflow runtime
            await self.workflow_runtime.update_task_contract(
                contract_id, 
                version, 
                self.contract_versions[contract_id][version]
            )
            
            logger.info(f"Deprecated contract {contract_id} version {version}: {reason}")
            
            return {
                "success": True,
                "contract_id": contract_id,
                "version": version,
                "status": "deprecated",
                "deprecated_at": self.contract_versions[contract_id][version]["deprecated_at"],
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Error deprecating contract: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["contract_version_node", "contract_approval_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            
            if message_type == "register_contract":
                return await self.register_contract(message.get("payload", {}))
            elif message_type == "approve_contract":
                return await self.approve_contract(message.get("payload", {}))
            elif message_type == "get_contract_version":
                payload = message.get("payload", {})
                contract_id = payload.get("contract_id")
                version = payload.get("version")
                if not contract_id:
                    return {"success": False, "error": "Missing contract_id"}
                return await self.get_contract_version(contract_id, version)
            elif message_type == "list_contract_versions":
                payload = message.get("payload", {})
                contract_id = payload.get("contract_id")
                if not contract_id:
                    return {"success": False, "error": "Missing contract_id"}
                return await self.list_contract_versions(contract_id)
            elif message_type == "compare_contract_versions":
                payload = message.get("payload", {})
                contract_id = payload.get("contract_id")
                version1 = payload.get("version1")
                version2 = payload.get("version2")
                if not contract_id or not version1 or not version2:
                    return {"success": False, "error": "Missing required fields"}
                return await self.compare_contract_versions(contract_id, version1, version2)
            elif message_type == "publish_contract":
                return await self.publish_contract(message.get("payload", {}))
            elif message_type == "deprecate_contract":
                return await self.deprecate_contract(message.get("payload", {}))
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
