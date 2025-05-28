"""
Capsule Shadow Manager for the Digital Twin Diplomacy Phase of the Overseer System.

This module provides capabilities for creating and managing shadow copies of capsules
for diplomacy purposes, including shadow creation, synchronization, isolation, monitoring,
comparison, and retirement.

Author: Manus AI
Date: May 25, 2025
"""

import json
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService

# Import diplomacy models
from .diplomacy_models import (
    ShadowCapsule, ShadowType, ShadowStatus, create_shadow_capsule
)

class ShadowSynchronizer:
    """Handles synchronization between shadow and original capsules."""
    
    def __init__(
        self,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the shadow synchronizer.
        
        Args:
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            data_access: Data access service
            logger: Logger instance
        """
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize synchronization tasks
        self.sync_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_sync_task(
        self,
        shadow: ShadowCapsule,
        interval_seconds: int = 60,
        max_divergence: float = 20.0
    ) -> None:
        """
        Start a synchronization task for a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            interval_seconds: Synchronization interval in seconds
            max_divergence: Maximum allowed divergence percentage
        """
        if shadow.shadow_id in self.sync_tasks:
            self.logger.warning(f"Sync task for shadow {shadow.shadow_id} already exists")
            return
        
        task = asyncio.create_task(
            self._sync_loop(shadow, interval_seconds, max_divergence)
        )
        
        self.sync_tasks[shadow.shadow_id] = task
        self.logger.info(f"Started sync task for shadow {shadow.shadow_id} with interval {interval_seconds}s")
    
    async def stop_sync_task(self, shadow_id: str) -> None:
        """
        Stop a synchronization task.
        
        Args:
            shadow_id: Shadow capsule ID
        """
        if shadow_id not in self.sync_tasks:
            self.logger.warning(f"No sync task found for shadow {shadow_id}")
            return
        
        task = self.sync_tasks[shadow_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.sync_tasks[shadow_id]
        self.logger.info(f"Stopped sync task for shadow {shadow_id}")
    
    async def _sync_loop(
        self,
        shadow: ShadowCapsule,
        interval_seconds: int,
        max_divergence: float
    ) -> None:
        """
        Synchronization loop for a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            interval_seconds: Synchronization interval in seconds
            max_divergence: Maximum allowed divergence percentage
        """
        while True:
            try:
                # Get original capsule state
                original_state = await self._get_original_state(shadow.original_id)
                
                # Synchronize shadow with original
                shadow.sync_with_original(original_state)
                
                # Update shadow in data access service
                self.data_access.update(
                    collection="shadow_capsules",
                    document_id=shadow.shadow_id,
                    data=shadow.to_dict()
                )
                
                # Check divergence
                if shadow.divergence_metrics.get("state_change_percentage", 0) > max_divergence:
                    shadow.mark_as_diverged()
                    
                    # Update shadow in data access service
                    self.data_access.update(
                        collection="shadow_capsules",
                        document_id=shadow.shadow_id,
                        data=shadow.to_dict()
                    )
                    
                    # Publish divergence event
                    await self._publish_divergence_event(shadow)
                
                self.logger.debug(f"Synchronized shadow {shadow.shadow_id} with original {shadow.original_id}")
            
            except Exception as e:
                self.logger.error(f"Error synchronizing shadow {shadow.shadow_id}: {str(e)}")
            
            # Wait for next synchronization
            await asyncio.sleep(interval_seconds)
    
    async def _get_original_state(self, original_id: str) -> Dict[str, Any]:
        """
        Get the state of the original capsule.
        
        Args:
            original_id: Original capsule ID
            
        Returns:
            Dict[str, Any]: Original capsule state
        """
        # Get state from MCP context
        context = await self.mcp_bridge.get_context(
            context_type="capsule_state",
            context_id=original_id
        )
        
        if not context:
            # Try to get state via A2A
            response = await self.a2a_bridge.send_message_async(
                message_type="get_state",
                sender_id="capsule_shadow_manager",
                recipient_id=original_id,
                content={"request_type": "full_state"}
            )
            
            if response and "state" in response:
                return response["state"]
            
            # If still no state, try data access service
            capsule_data = self.data_access.read(
                collection="capsules",
                document_id=original_id
            )
            
            if capsule_data and "state" in capsule_data:
                return capsule_data["state"]
            
            # Return empty state if all methods fail
            return {}
        
        return context.get("state", {})
    
    async def _publish_divergence_event(self, shadow: ShadowCapsule) -> None:
        """
        Publish a divergence event.
        
        Args:
            shadow: Shadow capsule
        """
        event_data = {
            "shadow_id": shadow.shadow_id,
            "original_id": shadow.original_id,
            "divergence_metrics": shadow.divergence_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publish to event bus
        await self.event_bus.publish_async(
            topic="diplomacy.shadow.diverged",
            key=shadow.shadow_id,
            value=event_data
        )
        
        # Update MCP context
        await self.mcp_bridge.update_context_async(
            context_type="shadow_divergence",
            context_id=shadow.shadow_id,
            context_data=event_data
        )
        
        self.logger.info(f"Published divergence event for shadow {shadow.shadow_id}")

class ShadowIsolator:
    """Handles isolation of shadow capsules from their originals."""
    
    def __init__(
        self,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the shadow isolator.
        
        Args:
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            data_access: Data access service
            logger: Logger instance
        """
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize isolation policies
        self.isolation_policies: Dict[str, Dict[str, Any]] = {}
    
    def set_isolation_policy(
        self,
        shadow_id: str,
        policy: Dict[str, Any]
    ) -> None:
        """
        Set isolation policy for a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
            policy: Isolation policy
        """
        self.isolation_policies[shadow_id] = policy
        
        # Store policy in data access service
        self.data_access.update(
            collection="shadow_isolation_policies",
            document_id=shadow_id,
            data=policy
        )
        
        self.logger.info(f"Set isolation policy for shadow {shadow_id}")
    
    def get_isolation_policy(self, shadow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get isolation policy for a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
            
        Returns:
            Optional[Dict[str, Any]]: Isolation policy
        """
        if shadow_id in self.isolation_policies:
            return self.isolation_policies[shadow_id]
        
        # Try to load from data access service
        policy = self.data_access.read(
            collection="shadow_isolation_policies",
            document_id=shadow_id
        )
        
        if policy:
            self.isolation_policies[shadow_id] = policy
            return policy
        
        return None
    
    def create_isolation_boundary(
        self,
        shadow: ShadowCapsule,
        boundary_type: str = "soft",
        allowed_interactions: Optional[List[str]] = None,
        blocked_interactions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an isolation boundary for a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            boundary_type: Type of boundary (soft, hard)
            allowed_interactions: List of allowed interaction types
            blocked_interactions: List of blocked interaction types
            
        Returns:
            Dict[str, Any]: Isolation boundary configuration
        """
        allowed_interactions = allowed_interactions or []
        blocked_interactions = blocked_interactions or []
        
        boundary = {
            "boundary_id": f"boundary-{uuid.uuid4()}",
            "shadow_id": shadow.shadow_id,
            "original_id": shadow.original_id,
            "boundary_type": boundary_type,
            "allowed_interactions": allowed_interactions,
            "blocked_interactions": blocked_interactions,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Store boundary in data access service
        self.data_access.create(
            collection="shadow_isolation_boundaries",
            document_id=boundary["boundary_id"],
            data=boundary
        )
        
        # Set isolation policy
        self.set_isolation_policy(
            shadow_id=shadow.shadow_id,
            policy={
                "boundary_id": boundary["boundary_id"],
                "boundary_type": boundary_type,
                "allowed_interactions": allowed_interactions,
                "blocked_interactions": blocked_interactions
            }
        )
        
        self.logger.info(f"Created {boundary_type} isolation boundary for shadow {shadow.shadow_id}")
        
        return boundary
    
    def check_interaction_allowed(
        self,
        shadow_id: str,
        interaction_type: str
    ) -> bool:
        """
        Check if an interaction is allowed for a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
            interaction_type: Type of interaction
            
        Returns:
            bool: True if allowed, False otherwise
        """
        policy = self.get_isolation_policy(shadow_id)
        
        if not policy:
            # Default to allowing if no policy exists
            return True
        
        # If interaction is explicitly allowed, return True
        if interaction_type in policy.get("allowed_interactions", []):
            return True
        
        # If interaction is explicitly blocked, return False
        if interaction_type in policy.get("blocked_interactions", []):
            return False
        
        # For hard boundaries, block by default
        if policy.get("boundary_type") == "hard":
            return False
        
        # For soft boundaries, allow by default
        return True
    
    def register_interaction_handler(
        self,
        shadow_id: str,
        interaction_type: str,
        handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Register a handler for a specific interaction type.
        
        Args:
            shadow_id: Shadow capsule ID
            interaction_type: Type of interaction
            handler: Handler function
        """
        # Implementation depends on how interactions are processed
        # This is a placeholder for the concept
        pass

class ShadowMonitor:
    """Monitors shadow capsules for behavior and performance."""
    
    def __init__(
        self,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the shadow monitor.
        
        Args:
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            data_access: Data access service
            logger: Logger instance
        """
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize metrics
        self.shadow_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def start_monitoring(
        self,
        shadow: ShadowCapsule,
        interval_seconds: int = 60,
        metrics: Optional[List[str]] = None
    ) -> None:
        """
        Start monitoring a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            interval_seconds: Monitoring interval in seconds
            metrics: List of metrics to monitor
        """
        if shadow.shadow_id in self.monitoring_tasks:
            self.logger.warning(f"Monitoring task for shadow {shadow.shadow_id} already exists")
            return
        
        metrics = metrics or ["state_size", "activity_level", "response_time", "error_rate"]
        
        task = asyncio.create_task(
            self._monitoring_loop(shadow, interval_seconds, metrics)
        )
        
        self.monitoring_tasks[shadow.shadow_id] = task
        self.logger.info(f"Started monitoring for shadow {shadow.shadow_id} with interval {interval_seconds}s")
    
    async def stop_monitoring(self, shadow_id: str) -> None:
        """
        Stop monitoring a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
        """
        if shadow_id not in self.monitoring_tasks:
            self.logger.warning(f"No monitoring task found for shadow {shadow_id}")
            return
        
        task = self.monitoring_tasks[shadow_id]
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        del self.monitoring_tasks[shadow_id]
        self.logger.info(f"Stopped monitoring for shadow {shadow_id}")
    
    async def _monitoring_loop(
        self,
        shadow: ShadowCapsule,
        interval_seconds: int,
        metrics: List[str]
    ) -> None:
        """
        Monitoring loop for a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            interval_seconds: Monitoring interval in seconds
            metrics: List of metrics to monitor
        """
        while True:
            try:
                # Collect metrics
                collected_metrics = await self._collect_metrics(shadow, metrics)
                
                # Store metrics
                self.shadow_metrics[shadow.shadow_id] = collected_metrics
                
                # Store in data access service
                self.data_access.create(
                    collection="shadow_metrics",
                    document_id=f"{shadow.shadow_id}_{datetime.now().isoformat()}",
                    data={
                        "shadow_id": shadow.shadow_id,
                        "timestamp": datetime.now().isoformat(),
                        "metrics": collected_metrics
                    }
                )
                
                # Publish metrics event
                self.event_bus.publish(
                    topic="diplomacy.shadow.metrics",
                    key=shadow.shadow_id,
                    value={
                        "shadow_id": shadow.shadow_id,
                        "original_id": shadow.original_id,
                        "timestamp": datetime.now().isoformat(),
                        "metrics": collected_metrics
                    }
                )
                
                # Check for anomalies
                anomalies = self._detect_anomalies(shadow.shadow_id, collected_metrics)
                
                if anomalies:
                    # Publish anomaly event
                    self.event_bus.publish(
                        topic="diplomacy.shadow.anomaly",
                        key=shadow.shadow_id,
                        value={
                            "shadow_id": shadow.shadow_id,
                            "original_id": shadow.original_id,
                            "timestamp": datetime.now().isoformat(),
                            "anomalies": anomalies
                        }
                    )
                    
                    self.logger.warning(f"Detected anomalies in shadow {shadow.shadow_id}: {anomalies}")
                
                self.logger.debug(f"Collected metrics for shadow {shadow.shadow_id}")
            
            except Exception as e:
                self.logger.error(f"Error monitoring shadow {shadow.shadow_id}: {str(e)}")
            
            # Wait for next monitoring cycle
            await asyncio.sleep(interval_seconds)
    
    async def _collect_metrics(
        self,
        shadow: ShadowCapsule,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Collect metrics for a shadow capsule.
        
        Args:
            shadow: Shadow capsule
            metrics: List of metrics to collect
            
        Returns:
            Dict[str, Any]: Collected metrics
        """
        collected_metrics = {}
        
        # Collect state size
        if "state_size" in metrics:
            collected_metrics["state_size"] = len(json.dumps(shadow.state))
        
        # Collect activity level (placeholder)
        if "activity_level" in metrics:
            # In a real implementation, this would track actual activity
            collected_metrics["activity_level"] = 0
        
        # Collect response time (placeholder)
        if "response_time" in metrics:
            # In a real implementation, this would measure actual response times
            collected_metrics["response_time"] = 0
        
        # Collect error rate (placeholder)
        if "error_rate" in metrics:
            # In a real implementation, this would track actual errors
            collected_metrics["error_rate"] = 0
        
        return collected_metrics
    
    def _detect_anomalies(
        self,
        shadow_id: str,
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect anomalies in shadow metrics.
        
        Args:
            shadow_id: Shadow capsule ID
            current_metrics: Current metrics
            
        Returns:
            Dict[str, Any]: Detected anomalies
        """
        anomalies = {}
        
        # Get historical metrics
        historical_metrics = self._get_historical_metrics(shadow_id)
        
        if not historical_metrics:
            return anomalies
        
        # Check for anomalies in each metric
        for metric, value in current_metrics.items():
            if metric not in historical_metrics:
                continue
            
            historical_values = historical_metrics[metric]
            
            if not historical_values:
                continue
            
            # Calculate mean and standard deviation
            mean = sum(historical_values) / len(historical_values)
            std_dev = (sum((x - mean) ** 2 for x in historical_values) / len(historical_values)) ** 0.5
            
            # Check if current value is an anomaly (more than 3 standard deviations from mean)
            if std_dev > 0 and abs(value - mean) > 3 * std_dev:
                anomalies[metric] = {
                    "current_value": value,
                    "mean": mean,
                    "std_dev": std_dev,
                    "z_score": (value - mean) / std_dev
                }
        
        return anomalies
    
    def _get_historical_metrics(self, shadow_id: str) -> Dict[str, List[float]]:
        """
        Get historical metrics for a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
            
        Returns:
            Dict[str, List[float]]: Historical metrics
        """
        # Query data access service for historical metrics
        metrics_data = self.data_access.query(
            collection="shadow_metrics",
            query={"shadow_id": shadow_id},
            limit=100,
            sort={"timestamp": -1}
        )
        
        if not metrics_data:
            return {}
        
        # Organize metrics by type
        historical_metrics: Dict[str, List[float]] = {}
        
        for entry in metrics_data:
            for metric, value in entry.get("metrics", {}).items():
                if isinstance(value, (int, float)):
                    if metric not in historical_metrics:
                        historical_metrics[metric] = []
                    
                    historical_metrics[metric].append(value)
        
        return historical_metrics

class ShadowComparator:
    """Compares shadow and original capsule behavior."""
    
    def __init__(
        self,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the shadow comparator.
        
        Args:
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            data_access: Data access service
            logger: Logger instance
        """
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
    
    async def compare_behavior(
        self,
        shadow_id: str,
        original_id: str,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare behavior of shadow and original capsules.
        
        Args:
            shadow_id: Shadow capsule ID
            original_id: Original capsule ID
            test_cases: List of test cases
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        results = {
            "shadow_id": shadow_id,
            "original_id": original_id,
            "timestamp": datetime.now().isoformat(),
            "test_cases": [],
            "summary": {}
        }
        
        for i, test_case in enumerate(test_cases):
            try:
                # Run test case on original
                original_result = await self._run_test_case(original_id, test_case)
                
                # Run test case on shadow
                shadow_result = await self._run_test_case(shadow_id, test_case)
                
                # Compare results
                comparison = self._compare_results(original_result, shadow_result)
                
                # Add to results
                results["test_cases"].append({
                    "test_id": i,
                    "test_case": test_case,
                    "original_result": original_result,
                    "shadow_result": shadow_result,
                    "comparison": comparison
                })
            
            except Exception as e:
                self.logger.error(f"Error comparing test case {i}: {str(e)}")
                
                # Add error to results
                results["test_cases"].append({
                    "test_id": i,
                    "test_case": test_case,
                    "error": str(e)
                })
        
        # Calculate summary
        results["summary"] = self._calculate_summary(results["test_cases"])
        
        # Store results in data access service
        self.data_access.create(
            collection="shadow_comparisons",
            document_id=f"{shadow_id}_{datetime.now().isoformat()}",
            data=results
        )
        
        self.logger.info(f"Completed behavior comparison between shadow {shadow_id} and original {original_id}")
        
        return results
    
    async def _run_test_case(
        self,
        capsule_id: str,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a test case on a capsule.
        
        Args:
            capsule_id: Capsule ID
            test_case: Test case
            
        Returns:
            Dict[str, Any]: Test results
        """
        # Send test case via A2A
        response = await self.a2a_bridge.send_message_async(
            message_type="test_case",
            sender_id="capsule_shadow_manager",
            recipient_id=capsule_id,
            content=test_case
        )
        
        if not response:
            raise ValueError(f"No response from capsule {capsule_id}")
        
        return response
    
    def _compare_results(
        self,
        original_result: Dict[str, Any],
        shadow_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare test results.
        
        Args:
            original_result: Original capsule result
            shadow_result: Shadow capsule result
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        comparison = {
            "identical": original_result == shadow_result,
            "differences": {}
        }
        
        # Find differences
        if not comparison["identical"]:
            comparison["differences"] = self._find_differences(original_result, shadow_result)
        
        return comparison
    
    def _find_differences(
        self,
        original: Dict[str, Any],
        shadow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Find differences between two dictionaries.
        
        Args:
            original: Original dictionary
            shadow: Shadow dictionary
            
        Returns:
            Dict[str, Any]: Differences
        """
        differences = {}
        
        # Find keys in original but not in shadow
        for key in original:
            if key not in shadow:
                differences[key] = {
                    "type": "missing_in_shadow",
                    "original_value": original[key]
                }
            elif original[key] != shadow[key]:
                if isinstance(original[key], dict) and isinstance(shadow[key], dict):
                    nested_diff = self._find_differences(original[key], shadow[key])
                    if nested_diff:
                        differences[key] = {
                            "type": "different_nested",
                            "differences": nested_diff
                        }
                else:
                    differences[key] = {
                        "type": "different_value",
                        "original_value": original[key],
                        "shadow_value": shadow[key]
                    }
        
        # Find keys in shadow but not in original
        for key in shadow:
            if key not in original:
                differences[key] = {
                    "type": "missing_in_original",
                    "shadow_value": shadow[key]
                }
        
        return differences
    
    def _calculate_summary(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate summary of test results.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Dict[str, Any]: Summary
        """
        total_tests = len(test_cases)
        identical_count = sum(1 for tc in test_cases if tc.get("comparison", {}).get("identical", False))
        error_count = sum(1 for tc in test_cases if "error" in tc)
        
        return {
            "total_tests": total_tests,
            "identical_count": identical_count,
            "different_count": total_tests - identical_count - error_count,
            "error_count": error_count,
            "identical_percentage": (identical_count / total_tests * 100) if total_tests > 0 else 0
        }
    
    async def generate_test_cases(
        self,
        capsule_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for a capsule.
        
        Args:
            capsule_id: Capsule ID
            count: Number of test cases
            
        Returns:
            List[Dict[str, Any]]: Generated test cases
        """
        # Get capsule capabilities
        capabilities = await self._get_capsule_capabilities(capsule_id)
        
        if not capabilities:
            raise ValueError(f"No capabilities found for capsule {capsule_id}")
        
        # Generate test cases based on capabilities
        test_cases = []
        
        for i in range(count):
            test_case = self._generate_test_case(capabilities, i)
            test_cases.append(test_case)
        
        return test_cases
    
    async def _get_capsule_capabilities(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get capabilities of a capsule.
        
        Args:
            capsule_id: Capsule ID
            
        Returns:
            Dict[str, Any]: Capsule capabilities
        """
        # Try to get capabilities from MCP context
        context = await self.mcp_bridge.get_context(
            context_type="capsule_capabilities",
            context_id=capsule_id
        )
        
        if context and "capabilities" in context:
            return context["capabilities"]
        
        # Try to get capabilities via A2A
        response = await self.a2a_bridge.send_message_async(
            message_type="get_capabilities",
            sender_id="capsule_shadow_manager",
            recipient_id=capsule_id,
            content={"request_type": "full_capabilities"}
        )
        
        if response and "capabilities" in response:
            return response["capabilities"]
        
        # Try to get capabilities from data access service
        capsule_data = self.data_access.read(
            collection="capsules",
            document_id=capsule_id
        )
        
        if capsule_data and "capabilities" in capsule_data:
            return capsule_data["capabilities"]
        
        # Return empty capabilities if all methods fail
        return {}
    
    def _generate_test_case(
        self,
        capabilities: Dict[str, Any],
        index: int
    ) -> Dict[str, Any]:
        """
        Generate a test case based on capsule capabilities.
        
        Args:
            capabilities: Capsule capabilities
            index: Test case index
            
        Returns:
            Dict[str, Any]: Generated test case
        """
        # This is a simplified implementation
        # In a real system, this would be more sophisticated
        
        # Get available operations
        operations = capabilities.get("operations", [])
        
        if not operations:
            return {
                "type": "echo",
                "input": f"Test case {index}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Select an operation
        operation = operations[index % len(operations)]
        
        # Generate test case for the operation
        return {
            "type": "operation",
            "operation": operation,
            "parameters": {"test_index": index},
            "timestamp": datetime.now().isoformat()
        }

class CapsuleShadowManager:
    """Manager for shadow copies of capsules."""
    
    def __init__(
        self,
        agent_id: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Capsule Shadow Manager.
        
        Args:
            agent_id: Unique identifier for the agent
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            data_access: Data access service
            logger: Logger instance
        """
        self.agent_id = agent_id
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize shadow registry
        self.shadows: Dict[str, ShadowCapsule] = {}
        
        # Initialize components
        self.synchronizer = ShadowSynchronizer(mcp_bridge, a2a_bridge, data_access, logger)
        self.isolator = ShadowIsolator(mcp_bridge, a2a_bridge, data_access, logger)
        self.monitor = ShadowMonitor(mcp_bridge, a2a_bridge, event_bus, data_access, logger)
        self.comparator = ShadowComparator(mcp_bridge, a2a_bridge, data_access, logger)
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            topic="diplomacy.shadow.create_request",
            group_id=f"capsule-shadow-manager-{self.agent_id}",
            callback=self._handle_create_request
        )
        
        self.event_bus.subscribe(
            topic="diplomacy.shadow.sync_request",
            group_id=f"capsule-shadow-manager-{self.agent_id}",
            callback=self._handle_sync_request
        )
        
        self.event_bus.subscribe(
            topic="diplomacy.shadow.retire_request",
            group_id=f"capsule-shadow-manager-{self.agent_id}",
            callback=self._handle_retire_request
        )
        
        # Subscribe to A2A messages
        self.a2a_bridge.subscribe_to_message_type(
            message_type="shadow_create_request",
            callback=self._handle_a2a_create_request
        )
        
        self.a2a_bridge.subscribe_to_message_type(
            message_type="shadow_sync_request",
            callback=self._handle_a2a_sync_request
        )
        
        self.a2a_bridge.subscribe_to_message_type(
            message_type="shadow_retire_request",
            callback=self._handle_a2a_retire_request
        )
    
    def create_shadow(
        self,
        original_id: str,
        shadow_type: ShadowType,
        capabilities: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_sync: bool = True,
        sync_interval: int = 60,
        isolation_boundary: Optional[str] = None,
        monitor: bool = True
    ) -> ShadowCapsule:
        """
        Create a shadow copy of a capsule.
        
        Args:
            original_id: ID of the original capsule
            shadow_type: Type of shadow
            capabilities: Shadow capabilities
            state: Shadow state
            metadata: Additional metadata
            auto_sync: Whether to automatically synchronize
            sync_interval: Synchronization interval in seconds
            isolation_boundary: Type of isolation boundary
            monitor: Whether to monitor the shadow
            
        Returns:
            ShadowCapsule: Created shadow
        """
        # Create shadow capsule
        shadow = create_shadow_capsule(
            original_id=original_id,
            shadow_type=shadow_type,
            capabilities=capabilities,
            state=state,
            metadata=metadata
        )
        
        # Store shadow
        self.shadows[shadow.shadow_id] = shadow
        
        # Store in data access service
        self.data_access.create(
            collection="shadow_capsules",
            document_id=shadow.shadow_id,
            data=shadow.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.shadow.created",
            key=shadow.shadow_id,
            value={
                "shadow_id": shadow.shadow_id,
                "original_id": original_id,
                "shadow_type": shadow_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="shadow_capsule",
            context_id=shadow.shadow_id,
            context_data={
                "shadow_id": shadow.shadow_id,
                "original_id": original_id,
                "shadow_type": shadow_type,
                "status": shadow.status,
                "created_at": shadow.created_at.isoformat(),
                "last_sync": shadow.last_sync.isoformat()
            }
        )
        
        # Set up auto-sync if requested
        if auto_sync:
            asyncio.create_task(
                self.synchronizer.start_sync_task(
                    shadow=shadow,
                    interval_seconds=sync_interval
                )
            )
        
        # Create isolation boundary if requested
        if isolation_boundary:
            self.isolator.create_isolation_boundary(
                shadow=shadow,
                boundary_type=isolation_boundary
            )
        
        # Set up monitoring if requested
        if monitor:
            asyncio.create_task(
                self.monitor.start_monitoring(shadow)
            )
        
        self.logger.info(f"Created {shadow_type} shadow {shadow.shadow_id} for capsule {original_id}")
        
        return shadow
    
    def get_shadow(self, shadow_id: str) -> Optional[ShadowCapsule]:
        """
        Get a shadow capsule by ID.
        
        Args:
            shadow_id: Shadow capsule ID
            
        Returns:
            Optional[ShadowCapsule]: Shadow capsule
        """
        if shadow_id in self.shadows:
            return self.shadows[shadow_id]
        
        # Try to load from data access service
        shadow_data = self.data_access.read(
            collection="shadow_capsules",
            document_id=shadow_id
        )
        
        if not shadow_data:
            return None
        
        shadow = ShadowCapsule.from_dict(shadow_data)
        self.shadows[shadow_id] = shadow
        
        return shadow
    
    def get_shadows_for_original(self, original_id: str) -> List[ShadowCapsule]:
        """
        Get all shadows for an original capsule.
        
        Args:
            original_id: Original capsule ID
            
        Returns:
            List[ShadowCapsule]: List of shadow capsules
        """
        # Query data access service
        shadows_data = self.data_access.query(
            collection="shadow_capsules",
            query={"original_id": original_id}
        )
        
        if not shadows_data:
            return []
        
        shadows = []
        
        for shadow_data in shadows_data:
            shadow = ShadowCapsule.from_dict(shadow_data)
            self.shadows[shadow.shadow_id] = shadow
            shadows.append(shadow)
        
        return shadows
    
    async def sync_shadow(self, shadow_id: str) -> Optional[ShadowCapsule]:
        """
        Synchronize a shadow with its original.
        
        Args:
            shadow_id: Shadow capsule ID
            
        Returns:
            Optional[ShadowCapsule]: Updated shadow
        """
        shadow = self.get_shadow(shadow_id)
        
        if not shadow:
            self.logger.warning(f"Shadow {shadow_id} not found")
            return None
        
        # Get original state
        original_state = await self.synchronizer._get_original_state(shadow.original_id)
        
        # Synchronize shadow
        shadow.sync_with_original(original_state)
        
        # Update shadow in data access service
        self.data_access.update(
            collection="shadow_capsules",
            document_id=shadow_id,
            data=shadow.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.shadow.synced",
            key=shadow_id,
            value={
                "shadow_id": shadow_id,
                "original_id": shadow.original_id,
                "timestamp": datetime.now().isoformat(),
                "divergence_metrics": shadow.divergence_metrics
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="shadow_capsule",
            context_id=shadow_id,
            context_data={
                "shadow_id": shadow_id,
                "original_id": shadow.original_id,
                "status": shadow.status,
                "last_sync": shadow.last_sync.isoformat(),
                "divergence_metrics": shadow.divergence_metrics
            }
        )
        
        self.logger.info(f"Synchronized shadow {shadow_id} with original {shadow.original_id}")
        
        return shadow
    
    def retire_shadow(self, shadow_id: str) -> Optional[ShadowCapsule]:
        """
        Retire a shadow capsule.
        
        Args:
            shadow_id: Shadow capsule ID
            
        Returns:
            Optional[ShadowCapsule]: Retired shadow
        """
        shadow = self.get_shadow(shadow_id)
        
        if not shadow:
            self.logger.warning(f"Shadow {shadow_id} not found")
            return None
        
        # Mark as retired
        shadow.mark_as_retired()
        
        # Update shadow in data access service
        self.data_access.update(
            collection="shadow_capsules",
            document_id=shadow_id,
            data=shadow.to_dict()
        )
        
        # Stop synchronization
        asyncio.create_task(
            self.synchronizer.stop_sync_task(shadow_id)
        )
        
        # Stop monitoring
        asyncio.create_task(
            self.monitor.stop_monitoring(shadow_id)
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.shadow.retired",
            key=shadow_id,
            value={
                "shadow_id": shadow_id,
                "original_id": shadow.original_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="shadow_capsule",
            context_id=shadow_id,
            context_data={
                "shadow_id": shadow_id,
                "original_id": shadow.original_id,
                "status": shadow.status,
                "retired_at": datetime.now().isoformat()
            }
        )
        
        self.logger.info(f"Retired shadow {shadow_id}")
        
        return shadow
    
    async def compare_with_original(
        self,
        shadow_id: str,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        test_count: int = 10
    ) -> Dict[str, Any]:
        """
        Compare a shadow with its original.
        
        Args:
            shadow_id: Shadow capsule ID
            test_cases: List of test cases
            test_count: Number of test cases to generate if not provided
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        shadow = self.get_shadow(shadow_id)
        
        if not shadow:
            raise ValueError(f"Shadow {shadow_id} not found")
        
        # Generate test cases if not provided
        if not test_cases:
            test_cases = await self.comparator.generate_test_cases(
                capsule_id=shadow.original_id,
                count=test_count
            )
        
        # Compare behavior
        results = await self.comparator.compare_behavior(
            shadow_id=shadow_id,
            original_id=shadow.original_id,
            test_cases=test_cases
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.shadow.comparison",
            key=shadow_id,
            value={
                "shadow_id": shadow_id,
                "original_id": shadow.original_id,
                "timestamp": datetime.now().isoformat(),
                "summary": results["summary"]
            }
        )
        
        self.logger.info(f"Compared shadow {shadow_id} with original {shadow.original_id}")
        
        return results
    
    def _handle_create_request(self, event: Dict[str, Any]) -> None:
        """
        Handle shadow creation request event.
        
        Args:
            event: Event data
        """
        try:
            original_id = event.get("original_id")
            shadow_type_str = event.get("shadow_type")
            capabilities = event.get("capabilities")
            state = event.get("state")
            metadata = event.get("metadata")
            auto_sync = event.get("auto_sync", True)
            sync_interval = event.get("sync_interval", 60)
            isolation_boundary = event.get("isolation_boundary")
            monitor = event.get("monitor", True)
            
            if not original_id or not shadow_type_str:
                self.logger.error("Invalid shadow creation request: missing original_id or shadow_type")
                return
            
            # Convert string enum to enum value
            shadow_type = ShadowType(shadow_type_str)
            
            self.create_shadow(
                original_id=original_id,
                shadow_type=shadow_type,
                capabilities=capabilities,
                state=state,
                metadata=metadata,
                auto_sync=auto_sync,
                sync_interval=sync_interval,
                isolation_boundary=isolation_boundary,
                monitor=monitor
            )
        except Exception as e:
            self.logger.error(f"Error handling shadow creation request: {str(e)}")
    
    def _handle_sync_request(self, event: Dict[str, Any]) -> None:
        """
        Handle shadow synchronization request event.
        
        Args:
            event: Event data
        """
        try:
            shadow_id = event.get("shadow_id")
            
            if not shadow_id:
                self.logger.error("Invalid shadow sync request: missing shadow_id")
                return
            
            asyncio.create_task(self.sync_shadow(shadow_id))
        except Exception as e:
            self.logger.error(f"Error handling shadow sync request: {str(e)}")
    
    def _handle_retire_request(self, event: Dict[str, Any]) -> None:
        """
        Handle shadow retirement request event.
        
        Args:
            event: Event data
        """
        try:
            shadow_id = event.get("shadow_id")
            
            if not shadow_id:
                self.logger.error("Invalid shadow retirement request: missing shadow_id")
                return
            
            self.retire_shadow(shadow_id)
        except Exception as e:
            self.logger.error(f"Error handling shadow retirement request: {str(e)}")
    
    def _handle_a2a_create_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A shadow creation request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            
            original_id = content.get("original_id")
            shadow_type_str = content.get("shadow_type")
            capabilities = content.get("capabilities")
            state = content.get("state")
            metadata = content.get("metadata")
            auto_sync = content.get("auto_sync", True)
            sync_interval = content.get("sync_interval", 60)
            isolation_boundary = content.get("isolation_boundary")
            monitor = content.get("monitor", True)
            
            if not original_id or not shadow_type_str:
                self.logger.error("Invalid A2A shadow creation request: missing original_id or shadow_type")
                return
            
            # Convert string enum to enum value
            shadow_type = ShadowType(shadow_type_str)
            
            shadow = self.create_shadow(
                original_id=original_id,
                shadow_type=shadow_type,
                capabilities=capabilities,
                state=state,
                metadata=metadata,
                auto_sync=auto_sync,
                sync_interval=sync_interval,
                isolation_boundary=isolation_boundary,
                monitor=monitor
            )
            
            # Send response
            self.a2a_bridge.send_message(
                message_type="shadow_create_response",
                sender_id=self.agent_id,
                recipient_id=message.get("sender_id"),
                content={
                    "shadow_id": shadow.shadow_id,
                    "original_id": original_id,
                    "shadow_type": shadow_type,
                    "status": shadow.status,
                    "created_at": shadow.created_at.isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A shadow creation request: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="shadow_create_response",
                sender_id=self.agent_id,
                recipient_id=message.get("sender_id"),
                content={
                    "error": str(e)
                }
            )
    
    def _handle_a2a_sync_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A shadow synchronization request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            
            shadow_id = content.get("shadow_id")
            
            if not shadow_id:
                self.logger.error("Invalid A2A shadow sync request: missing shadow_id")
                return
            
            asyncio.create_task(
                self._handle_a2a_sync_request_async(shadow_id, message.get("sender_id"))
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A shadow sync request: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="shadow_sync_response",
                sender_id=self.agent_id,
                recipient_id=message.get("sender_id"),
                content={
                    "shadow_id": content.get("shadow_id"),
                    "error": str(e)
                }
            )
    
    async def _handle_a2a_sync_request_async(
        self,
        shadow_id: str,
        sender_id: str
    ) -> None:
        """
        Handle A2A shadow synchronization request asynchronously.
        
        Args:
            shadow_id: Shadow capsule ID
            sender_id: Sender ID
        """
        try:
            shadow = await self.sync_shadow(shadow_id)
            
            if not shadow:
                raise ValueError(f"Shadow {shadow_id} not found")
            
            # Send response
            self.a2a_bridge.send_message(
                message_type="shadow_sync_response",
                sender_id=self.agent_id,
                recipient_id=sender_id,
                content={
                    "shadow_id": shadow_id,
                    "original_id": shadow.original_id,
                    "status": shadow.status,
                    "last_sync": shadow.last_sync.isoformat(),
                    "divergence_metrics": shadow.divergence_metrics
                }
            )
        except Exception as e:
            self.logger.error(f"Error in A2A shadow sync request async handler: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="shadow_sync_response",
                sender_id=self.agent_id,
                recipient_id=sender_id,
                content={
                    "shadow_id": shadow_id,
                    "error": str(e)
                }
            )
    
    def _handle_a2a_retire_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A shadow retirement request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            
            shadow_id = content.get("shadow_id")
            
            if not shadow_id:
                self.logger.error("Invalid A2A shadow retirement request: missing shadow_id")
                return
            
            shadow = self.retire_shadow(shadow_id)
            
            if not shadow:
                raise ValueError(f"Shadow {shadow_id} not found")
            
            # Send response
            self.a2a_bridge.send_message(
                message_type="shadow_retire_response",
                sender_id=self.agent_id,
                recipient_id=message.get("sender_id"),
                content={
                    "shadow_id": shadow_id,
                    "original_id": shadow.original_id,
                    "status": shadow.status
                }
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A shadow retirement request: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="shadow_retire_response",
                sender_id=self.agent_id,
                recipient_id=message.get("sender_id"),
                content={
                    "shadow_id": content.get("shadow_id"),
                    "error": str(e)
                }
            )
