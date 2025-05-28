"""
Self-Healing Protocol Fabric for Industriverse Protocol Layer

This module implements the Self-Healing Protocol Fabric, providing resilience
and adaptability to the Industriverse communication mesh.

Features:
1. Continuous health monitoring of protocol components and network links.
2. Automatic detection of failures (nodes, links, services).
3. Dynamic path morphing and traffic rerouting to bypass failures.
4. Reflex loops for rapid, localized responses to disruptions.
5. Integration with Protocol Kernel Intelligence for optimized healing strategies.
6. Predictive failure analysis based on historical data and telemetry.
"""

import uuid
import time
import random
import asyncio
import logging
import datetime
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)
from protocols.discovery_service import DiscoveryService, AsyncDiscoveryService
from protocols.kernel.protocol_kernel_intelligence import ProtocolKernelIntelligence, AsyncProtocolKernelIntelligence

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'
)
logger = logging.getLogger(__name__)


class NodeHealth:
    """
    Represents the health status of a node (component or agent) in the mesh.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.last_seen: float = time.time()
        self.status: str = "unknown" # unknown, healthy, degraded, unhealthy, failed
        self.latency_ms: float = -1.0
        self.error_rate: float = 0.0
        self.missed_heartbeats: int = 0
        self.metrics: Dict[str, Any] = {}
        self.history: deque = deque(maxlen=100) # Store recent status changes

    def update_status(self, status: str, metrics: Dict[str, Any] = None) -> None:
        if status != self.status:
            self.history.append((time.time(), self.status, status))
            self.status = status
            logger.info(f"Node {self.node_id} status changed to {status}")
        self.last_seen = time.time()
        self.missed_heartbeats = 0 # Reset on successful contact
        if metrics:
            self.metrics.update(metrics)
            self.latency_ms = metrics.get("latency_ms", self.latency_ms)
            self.error_rate = metrics.get("error_rate", self.error_rate)

    def record_heartbeat_miss(self) -> None:
        self.missed_heartbeats += 1
        logger.warning(f"Node {self.node_id} missed heartbeat ({self.missed_heartbeats})")

    def is_healthy(self) -> bool:
        return self.status == "healthy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "last_seen": self.last_seen,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error_rate": self.error_rate,
            "missed_heartbeats": self.missed_heartbeats,
            "metrics": self.metrics,
            "history": list(self.history)
        }


class LinkHealth:
    """
    Represents the health status of a communication link between two nodes.
    """
    def __init__(self, source_id: str, target_id: str):
        self.link_id = f"{source_id} <-> {target_id}"
        self.source_id = source_id
        self.target_id = target_id
        self.last_tested: float = time.time()
        self.status: str = "unknown" # unknown, healthy, degraded, failed
        self.latency_ms: float = -1.0
        self.packet_loss: float = 0.0
        self.bandwidth_bps: float = -1.0
        self.history: deque = deque(maxlen=50)

    def update_status(self, status: str, metrics: Dict[str, Any] = None) -> None:
        if status != self.status:
            self.history.append((time.time(), self.status, status))
            self.status = status
            logger.info(f"Link {self.link_id} status changed to {status}")
        self.last_tested = time.time()
        if metrics:
            self.latency_ms = metrics.get("latency_ms", self.latency_ms)
            self.packet_loss = metrics.get("packet_loss", self.packet_loss)
            self.bandwidth_bps = metrics.get("bandwidth_bps", self.bandwidth_bps)

    def is_healthy(self) -> bool:
        return self.status == "healthy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "link_id": self.link_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "last_tested": self.last_tested,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "packet_loss": self.packet_loss,
            "bandwidth_bps": self.bandwidth_bps,
            "history": list(self.history)
        }


class SelfHealingFabric(ProtocolService):
    """
    Manages the health and resilience of the protocol mesh.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: DiscoveryService = None,
        pki_service: ProtocolKernelIntelligence = None,
        mcp_handler: \"MCPHandler\" = None, # Needed to send probes/messages
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "self_healing_fabric")
        self.discovery_service = discovery_service
        self.pki_service = pki_service
        self.mcp_handler = mcp_handler
        self.config = config or {}
        
        # Configuration parameters
        self.heartbeat_interval_sec: float = self.config.get("heartbeat_interval_sec", 10.0)
        self.probe_interval_sec: float = self.config.get("probe_interval_sec", 30.0)
        self.max_missed_heartbeats: int = self.config.get("max_missed_heartbeats", 3)
        self.latency_threshold_ms: float = self.config.get("latency_threshold_ms", 500.0)
        self.error_rate_threshold: float = self.config.get("error_rate_threshold", 0.05)
        self.packet_loss_threshold: float = self.config.get("packet_loss_threshold", 0.02)
        
        # State
        self.node_health: Dict[str, NodeHealth] = {}
        self.link_health: Dict[str, LinkHealth] = {}
        self.mesh_topology: Dict[str, Set[str]] = defaultdict(set) # node_id -> {neighbor_id}
        self.routing_table: Dict[Tuple[str, str], str] = {} # (source, target) -> next_hop
        
        self.logger = logging.getLogger(f"{__name__}.SelfHealingFabric.{self.component_id[:8]}")
        self.logger.info(f"Self-Healing Fabric initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("health_monitoring", "Monitor health of nodes and links")
        self.add_capability("failure_detection", "Detect failures in the mesh")
        self.add_capability("dynamic_rerouting", "Reroute traffic around failures")
        self.add_capability("predictive_analysis", "Predict potential failures")
        self.add_capability("reflex_loops", "Implement rapid local healing actions")

        # Start background tasks (if running in an async context, these would be async tasks)
        # For simplicity, assuming a synchronous model where these are called periodically
        # self._start_monitoring_tasks()

    def _get_or_create_node_health(self, node_id: str) -> NodeHealth:
        if node_id not in self.node_health:
            self.node_health[node_id] = NodeHealth(node_id)
            self.logger.info(f"Tracking new node: {node_id}")
        return self.node_health[node_id]

    def _get_or_create_link_health(self, source_id: str, target_id: str) -> LinkHealth:
        # Ensure consistent link ID ordering
        nodes = sorted([source_id, target_id])
        link_id = f"{nodes[0]} <-> {nodes[1]}"
        if link_id not in self.link_health:
            self.link_health[link_id] = LinkHealth(nodes[0], nodes[1])
            self.logger.info(f"Tracking new link: {link_id}")
        return self.link_health[link_id]

    def update_node_status(self, node_id: str, status: str, metrics: Dict[str, Any] = None) -> None:
        """Explicitly update the status of a node."""
        node = self._get_or_create_node_health(node_id)
        node.update_status(status, metrics)
        self._check_node_thresholds(node)

    def update_link_status(self, source_id: str, target_id: str, status: str, metrics: Dict[str, Any] = None) -> None:
        """Explicitly update the status of a link."""
        link = self._get_or_create_link_health(source_id, target_id)
        link.update_status(status, metrics)
        self._check_link_thresholds(link)

    def record_message_transit(self, source_id: str, target_id: str, latency_ms: float, success: bool) -> None:
        """Record metrics from a message transit to update link/node health."""
        # Update source node health (implicitly healthy if sending)
        source_node = self._get_or_create_node_health(source_id)
        source_node.update_status("healthy")

        # Update target node health
        target_node = self._get_or_create_node_health(target_id)
        target_metrics = {"latency_ms": latency_ms, "error_rate": 0.0 if success else 1.0}
        target_node.update_status("healthy" if success else "degraded", target_metrics)
        self._check_node_thresholds(target_node)

        # Update link health
        link = self._get_or_create_link_health(source_id, target_id)
        link_metrics = {"latency_ms": latency_ms, "packet_loss": 0.0 if success else 1.0}
        link.update_status("healthy" if success else "degraded", link_metrics)
        self._check_link_thresholds(link)

        # Update topology
        self.mesh_topology[source_id].add(target_id)
        self.mesh_topology[target_id].add(source_id)

    def perform_health_checks(self) -> None:
        """Periodically perform health checks on nodes and links."""
        self.logger.info("Performing periodic health checks...")
        now = time.time()
        
        # Check for stale nodes (missed heartbeats)
        for node_id, node in list(self.node_health.items()):
            if now - node.last_seen > self.heartbeat_interval_sec * (node.missed_heartbeats + 1):
                node.record_heartbeat_miss()
                if node.missed_heartbeats > self.max_missed_heartbeats:
                    if node.status != "failed":
                        self.logger.warning(f"Node {node_id} exceeded max missed heartbeats. Marking as failed.")
                        node.update_status("failed")
                        self._trigger_healing_actions(node_id=node_id)
                elif node.status == "healthy":
                    node.update_status("degraded") # Mark as degraded if missing heartbeats
            
            # Send explicit probes if needed (e.g., using MCP ping)
            if now - node.last_seen > self.probe_interval_sec and node.status != "failed":
                 self._send_probe(node_id)

        # Check link health (can be inferred or actively probed)
        # Active probing might involve sending echo requests between nodes
        # For now, link health is mostly updated via record_message_transit

        # Recompute routing table if topology or health changed significantly
        self._update_routing_table()
        
        self.logger.info("Health checks completed.")

    def _check_node_thresholds(self, node: NodeHealth) -> None:
        """Check if a node has crossed health thresholds."""
        if node.status == "failed": return # Already failed

        is_degraded = False
        if node.latency_ms > self.latency_threshold_ms:
            self.logger.warning(f"Node {node.node_id} latency high: {node.latency_ms:.2f}ms")
            is_degraded = True
        if node.error_rate > self.error_rate_threshold:
            self.logger.warning(f"Node {node.node_id} error rate high: {node.error_rate:.2%}")
            is_degraded = True
        if node.missed_heartbeats > 0:
             is_degraded = True # Already marked degraded by missed heartbeat logic

        if is_degraded and node.status == "healthy":
            node.update_status("degraded")
            self._trigger_healing_actions(node_id=node.node_id)
        elif not is_degraded and node.status == "degraded":
            # Potentially recover status if metrics improve
            # Add hysteresis or recovery logic here if needed
            node.update_status("healthy")

    def _check_link_thresholds(self, link: LinkHealth) -> None:
        """Check if a link has crossed health thresholds."""
        if link.status == "failed": return # Already failed

        is_degraded = False
        if link.latency_ms > self.latency_threshold_ms:
            self.logger.warning(f"Link {link.link_id} latency high: {link.latency_ms:.2f}ms")
            is_degraded = True
        if link.packet_loss > self.packet_loss_threshold:
            self.logger.warning(f"Link {link.link_id} packet loss high: {link.packet_loss:.2%}")
            is_degraded = True

        if is_degraded and link.status == "healthy":
            link.update_status("degraded")
            self._trigger_healing_actions(link_id=link.link_id)
        elif not is_degraded and link.status == "degraded":
            link.update_status("healthy")

    def _send_probe(self, target_id: str) -> None:
        """Send a health probe (e.g., ping) to a target node."""
        if not self.mcp_handler:
            self.logger.warning("MCP Handler not available, cannot send probe")
            return

        self.logger.debug(f"Sending health probe to {target_id}")
        probe_message = MessageFactory.create_command(
            command="health_ping",
            params={"timestamp": time.time()},
            sender_id=self.component_id,
            receiver_id=target_id,
            priority=MessagePriority.LOW
        )
        # Send the message - response handling would update health
        # This requires the MCP handler and target node to support ping/pong
        try:
            response = self.mcp_handler.send_message(probe_message)
            # Process response to update health (omitted for brevity)
            if response and response.status == MessageStatus.SUCCESS:
                 latency = (time.time() - response.payload.get("request_timestamp", time.time())) * 1000
                 self.record_message_transit(self.component_id, target_id, latency, True)
            elif response:
                 self.record_message_transit(self.component_id, target_id, -1, False)
            # Handle timeout implicitly via missed heartbeats
        except Exception as e:
            self.logger.error(f"Error sending probe to {target_id}: {e}")
            self.record_message_transit(self.component_id, target_id, -1, False)

    def _trigger_healing_actions(self, node_id: str = None, link_id: str = None) -> None:
        """Trigger healing actions in response to detected issues."""
        if node_id:
            self.logger.warning(f"Healing action triggered for node: {node_id}")
            # Actions: Mark node as unhealthy, update routing table, notify PKI
            if self.pki_service:
                # Provide feedback to the routing optimizer
                # This requires knowing which routes used this node
                pass # PKI feedback logic here
            self._update_routing_table() # Recompute routes excluding the failed node

        if link_id:
            self.logger.warning(f"Healing action triggered for link: {link_id}")
            # Actions: Mark link as unhealthy, update routing table, notify PKI
            if self.pki_service:
                # Provide feedback to the routing optimizer about the link
                pass # PKI feedback logic here
            self._update_routing_table() # Recompute routes avoiding the failed link

        # TODO: Implement more sophisticated healing actions:
        # - Reflex loops: Localized, rapid rerouting by neighboring nodes
        # - Predictive analysis: Proactively reroute based on degradation trends
        # - Service migration: If a service fails, attempt to restart or migrate it

    def _update_routing_table(self) -> None:
        """Update the routing table based on current mesh health and topology."""
        self.logger.debug("Updating routing table...")
        new_routing_table = {} # (source, target) -> next_hop
        
        # Use a graph algorithm (e.g., Dijkstra or Bellman-Ford) on the healthy topology
        # For simplicity, let's assume a basic shortest path calculation (hop count)
        
        nodes = [nid for nid, health in self.node_health.items() if health.status != "failed"]
        if not nodes:
            self.routing_table = {}
            return

        # Build adjacency list with weights (e.g., latency or 1 for hop count)
        adj = defaultdict(dict)
        for link_id, link in self.link_health.items():
            if link.status != "failed":
                n1, n2 = link.source_id, link.target_id
                if n1 in nodes and n2 in nodes:
                    weight = link.latency_ms if link.latency_ms > 0 else 1.0 # Use latency or hop count
                    adj[n1][n2] = weight
                    adj[n2][n1] = weight
        
        # Calculate shortest paths from each node (using Dijkstra as example)
        for start_node in nodes:
            distances = {node: float(\'inf\') for node in nodes}
            previous_nodes = {node: None for node in nodes}
            distances[start_node] = 0
            priority_queue = [(0, start_node)]

            while priority_queue:
                current_distance, current_node = min(priority_queue, key=lambda x: x[0])
                priority_queue.remove((current_distance, current_node))

                if current_distance > distances[current_node]:
                    continue

                if current_node in adj:
                    for neighbor, weight in adj[current_node].items():
                        distance = current_distance + weight
                        if distance < distances[neighbor]:
                            distances[neighbor] = distance
                            previous_nodes[neighbor] = current_node
                            priority_queue.append((distance, neighbor))
            
            # Build the routing table entries for this source node
            for target_node in nodes:
                if start_node == target_node: continue
                
                path_node = target_node
                next_hop = None
                while previous_nodes[path_node] is not None:
                    if previous_nodes[path_node] == start_node:
                        next_hop = path_node
                        break
                    path_node = previous_nodes[path_node]
                
                if next_hop:
                    new_routing_table[(start_node, target_node)] = next_hop

        if new_routing_table != self.routing_table:
            self.logger.info(f"Routing table updated. {len(new_routing_table)} entries.")
            self.routing_table = new_routing_table
            # Optionally, disseminate routing updates to nodes
        else:
            self.logger.debug("Routing table unchanged.")

    def get_next_hop(self, source_id: str, target_id: str) -> Optional[str]:
        """Get the next hop for routing a message from source to target."""
        # Use PKI if available for optimized routing
        if self.pki_service:
            # PKI might consider more than just topology (intent, load, etc.)
            # Assume PKI provides the best next hop directly
            # This requires PKI to have access to the routing table or topology
            # context = {"current_topology": self.mesh_topology, "node_health": self.node_health}
            # return self.pki_service.optimize_route(source_id, [target_id], context=context)
            pass # PKI integration logic here
        
        # Fallback to static routing table
        return self.routing_table.get((source_id, target_id))

    # --- ProtocolService Methods ---

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process messages related to fabric health and management.
        """
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "update_node_health":
                params = msg_obj.params
                if "node_id" in params and "status" in params:
                    self.update_node_status(params["node_id"], params["status"], params.get("metrics"))
                    response_payload = {"status": "node_health_updated"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing node_id or status"}
            elif msg_obj.command == "update_link_health":
                params = msg_obj.params
                if "source_id" in params and "target_id" in params and "status" in params:
                    self.update_link_status(params["source_id"], params["target_id"], params["status"], params.get("metrics"))
                    response_payload = {"status": "link_health_updated"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing source_id, target_id, or status"}
            elif msg_obj.command == "trigger_health_check":
                self.perform_health_checks()
                response_payload = {"status": "health_check_triggered"}
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_node_health":
                node_id = msg_obj.params.get("node_id")
                if node_id:
                    health = self.node_health.get(node_id)
                    response_payload = health.to_dict() if health else None
                else:
                    response_payload = {nid: h.to_dict() for nid, h in self.node_health.items()}
            elif msg_obj.query == "get_link_health":
                link_id = msg_obj.params.get("link_id")
                if link_id:
                    health = self.link_health.get(link_id)
                    response_payload = health.to_dict() if health else None
                else:
                    response_payload = {lid: h.to_dict() for lid, h in self.link_health.items()}
            elif msg_obj.query == "get_topology":
                response_payload = {node: list(neighbors) for node, neighbors in self.mesh_topology.items()}
            elif msg_obj.query == "get_routing_table":
                response_payload = {f"{src}->{tgt}": hop for (src, tgt), hop in self.routing_table.items()}
            elif msg_obj.query == "get_next_hop":
                 params = msg_obj.params
                 if "source_id" in params and "target_id" in params:
                     next_hop = self.get_next_hop(params["source_id"], params["target_id"])
                     response_payload = {"next_hop": next_hop}
                 else:
                     status = MessageStatus.FAILED
                     response_payload = {"error": "Missing source_id or target_id"}
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        elif isinstance(msg_obj, EventMessage):
            # Process events (e.g., node joined, node left)
            if msg_obj.event_type == "node_joined":
                node_id = msg_obj.payload.get("node_id")
                if node_id:
                    self._get_or_create_node_health(node_id)
                    self.update_node_status(node_id, "healthy", msg_obj.payload.get("metrics"))
            elif msg_obj.event_type == "node_left":
                node_id = msg_obj.payload.get("node_id")
                if node_id and node_id in self.node_health:
                    self.node_health[node_id].update_status("failed")
                    self._trigger_healing_actions(node_id=node_id)
            # No response needed for events
            return None
        else:
            # Ignore other message types
            return None

        # Create and return response message
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the fabric service itself.
        """
        num_nodes = len(self.node_health)
        num_links = len(self.link_health)
        num_failed_nodes = sum(1 for n in self.node_health.values() if n.status == "failed")
        num_failed_links = sum(1 for l in self.link_health.values() if l.status == "failed")
        
        return {
            "status": "healthy",
            "tracked_nodes": num_nodes,
            "tracked_links": num_links,
            "failed_nodes": num_failed_nodes,
            "failed_links": num_failed_links,
            "routing_table_size": len(self.routing_table),
            "discovery_service_status": "configured" if self.discovery_service else "not_configured",
            "pki_service_status": "configured" if self.pki_service else "not_configured",
            "mcp_handler_status": "configured" if self.mcp_handler else "not_configured"
        }

    def get_manifest(self) -> Dict[str, Any]:
        manifest = super().get_manifest()
        manifest.update(self.health_check()) # Include health status in manifest
        return manifest


# --- Async Version --- 

class AsyncSelfHealingFabric(ProtocolService):
    """
    Asynchronous version of the Self-Healing Protocol Fabric.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: AsyncDiscoveryService = None,
        pki_service: AsyncProtocolKernelIntelligence = None,
        mcp_handler: \"AsyncMCPHandler\" = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "async_self_healing_fabric")
        self.discovery_service = discovery_service
        self.pki_service = pki_service
        self.mcp_handler = mcp_handler
        self.config = config or {}
        
        # Configuration parameters (same as sync)
        self.heartbeat_interval_sec: float = self.config.get("heartbeat_interval_sec", 10.0)
        self.probe_interval_sec: float = self.config.get("probe_interval_sec", 30.0)
        self.max_missed_heartbeats: int = self.config.get("max_missed_heartbeats", 3)
        self.latency_threshold_ms: float = self.config.get("latency_threshold_ms", 500.0)
        self.error_rate_threshold: float = self.config.get("error_rate_threshold", 0.05)
        self.packet_loss_threshold: float = self.config.get("packet_loss_threshold", 0.02)
        
        # State (using async locks where needed)
        self.node_health: Dict[str, NodeHealth] = {}
        self.link_health: Dict[str, LinkHealth] = {}
        self.mesh_topology: Dict[str, Set[str]] = defaultdict(set)
        self.routing_table: Dict[Tuple[str, str], str] = {}
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.AsyncSelfHealingFabric.{self.component_id[:8]}")
        self.logger.info(f"Async Self-Healing Fabric initialized with ID {self.component_id}")
        
        # Add capabilities (same as sync)
        self.add_capability("health_monitoring", "Monitor health of nodes and links")
        self.add_capability("failure_detection", "Detect failures in the mesh")
        self.add_capability("dynamic_rerouting", "Reroute traffic around failures")
        self.add_capability("predictive_analysis", "Predict potential failures")
        self.add_capability("reflex_loops", "Implement rapid local healing actions")

        # Background tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._probe_task: Optional[asyncio.Task] = None

    async def start_monitoring(self) -> None:
        """Start the background monitoring tasks."""
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._run_periodic_checks())
            self.logger.info("Started periodic health monitoring task.")
        if self._probe_task is None or self._probe_task.done():
             self._probe_task = asyncio.create_task(self._run_periodic_probes())
             self.logger.info("Started periodic probing task.")

    async def stop_monitoring(self) -> None:
        """Stop the background monitoring tasks."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self.logger.info("Stopped periodic health monitoring task.")
        if self._probe_task and not self._probe_task.done():
            self._probe_task.cancel()
            try:
                await self._probe_task
            except asyncio.CancelledError:
                pass
            self.logger.info("Stopped periodic probing task.")

    async def _run_periodic_checks(self) -> None:
        """Coroutine for running periodic health checks."""
        while True:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(self.heartbeat_interval_sec)
            except asyncio.CancelledError:
                self.logger.info("Periodic check task cancelled.")
                break
            except Exception as e:
                self.logger.exception(f"Error in periodic health check: {e}")
                await asyncio.sleep(self.heartbeat_interval_sec) # Avoid tight loop on error

    async def _run_periodic_probes(self) -> None:
        """Coroutine for running periodic health probes."""
        while True:
            try:
                await self.send_probes_to_nodes()
                await asyncio.sleep(self.probe_interval_sec)
            except asyncio.CancelledError:
                self.logger.info("Periodic probe task cancelled.")
                break
            except Exception as e:
                self.logger.exception(f"Error in periodic probing: {e}")
                await asyncio.sleep(self.probe_interval_sec)

    async def _get_or_create_node_health(self, node_id: str) -> NodeHealth:
        async with self.lock:
            if node_id not in self.node_health:
                self.node_health[node_id] = NodeHealth(node_id)
                self.logger.info(f"Tracking new node: {node_id}")
            return self.node_health[node_id]

    async def _get_or_create_link_health(self, source_id: str, target_id: str) -> LinkHealth:
        nodes = sorted([source_id, target_id])
        link_id = f"{nodes[0]} <-> {nodes[1]}"
        async with self.lock:
            if link_id not in self.link_health:
                self.link_health[link_id] = LinkHealth(nodes[0], nodes[1])
                self.logger.info(f"Tracking new link: {link_id}")
            return self.link_health[link_id]

    async def update_node_status(self, node_id: str, status: str, metrics: Dict[str, Any] = None) -> None:
        node = await self._get_or_create_node_health(node_id)
        async with self.lock:
            node.update_status(status, metrics)
        await self._check_node_thresholds(node)

    async def update_link_status(self, source_id: str, target_id: str, status: str, metrics: Dict[str, Any] = None) -> None:
        link = await self._get_or_create_link_health(source_id, target_id)
        async with self.lock:
            link.update_status(status, metrics)
        await self._check_link_thresholds(link)

    async def record_message_transit(self, source_id: str, target_id: str, latency_ms: float, success: bool) -> None:
        source_node = await self._get_or_create_node_health(source_id)
        target_node = await self._get_or_create_node_health(target_id)
        link = await self._get_or_create_link_health(source_id, target_id)
        
        async with self.lock:
            source_node.update_status("healthy")
            target_metrics = {"latency_ms": latency_ms, "error_rate": 0.0 if success else 1.0}
            target_node.update_status("healthy" if success else "degraded", target_metrics)
            link_metrics = {"latency_ms": latency_ms, "packet_loss": 0.0 if success else 1.0}
            link.update_status("healthy" if success else "degraded", link_metrics)
            self.mesh_topology[source_id].add(target_id)
            self.mesh_topology[target_id].add(source_id)
            
        await self._check_node_thresholds(target_node)
        await self._check_link_thresholds(link)

    async def perform_health_checks(self) -> None:
        self.logger.debug("Performing async periodic health checks...")
        now = time.time()
        nodes_to_update = []
        links_to_update = []
        nodes_to_heal = []
        links_to_heal = []

        async with self.lock:
            for node_id, node in list(self.node_health.items()):
                if now - node.last_seen > self.heartbeat_interval_sec * (node.missed_heartbeats + 1):
                    node.record_heartbeat_miss()
                    if node.missed_heartbeats > self.max_missed_heartbeats:
                        if node.status != "failed":
                            self.logger.warning(f"Node {node_id} exceeded max missed heartbeats. Marking as failed.")
                            node.update_status("failed")
                            nodes_to_heal.append(node_id)
                    elif node.status == "healthy":
                        node.update_status("degraded") # Mark as degraded if missing heartbeats
        
        # Trigger healing actions outside the lock
        if nodes_to_heal or links_to_heal:
             await self._trigger_healing_actions(nodes_to_heal, links_to_heal)
             await self._update_routing_table() # Recompute routes
        
        self.logger.debug("Async health checks completed.")

    async def send_probes_to_nodes(self) -> None:
        """Periodically send probes to nodes that haven\"t been seen recently."""
        self.logger.debug("Sending periodic probes...")
        now = time.time()
        nodes_to_probe = []
        async with self.lock:
            for node_id, node in self.node_health.items():
                 if now - node.last_seen > self.probe_interval_sec and node.status != "failed":
                     nodes_to_probe.append(node_id)
        
        probe_tasks = [self._send_probe(node_id) for node_id in nodes_to_probe]
        await asyncio.gather(*probe_tasks)
        self.logger.debug(f"Sent probes to {len(nodes_to_probe)} nodes.")

    async def _check_node_thresholds(self, node: NodeHealth) -> None:
        async with self.lock:
            if node.status == "failed": return
            is_degraded = False
            if node.latency_ms > self.latency_threshold_ms: is_degraded = True
            if node.error_rate > self.error_rate_threshold: is_degraded = True
            if node.missed_heartbeats > 0: is_degraded = True

            status_changed = False
            if is_degraded and node.status == "healthy":
                node.update_status("degraded")
                status_changed = True
            elif not is_degraded and node.status == "degraded":
                node.update_status("healthy")
                status_changed = True
        
        if status_changed and node.status == "degraded":
             await self._trigger_healing_actions(node_ids=[node.node_id])

    async def _check_link_thresholds(self, link: LinkHealth) -> None:
        async with self.lock:
            if link.status == "failed": return
            is_degraded = False
            if link.latency_ms > self.latency_threshold_ms: is_degraded = True
            if link.packet_loss > self.packet_loss_threshold: is_degraded = True

            status_changed = False
            if is_degraded and link.status == "healthy":
                link.update_status("degraded")
                status_changed = True
            elif not is_degraded and link.status == "degraded":
                link.update_status("healthy")
                status_changed = True
        
        if status_changed and link.status == "degraded":
             await self._trigger_healing_actions(link_ids=[link.link_id])

    async def _send_probe(self, target_id: str) -> None:
        if not self.mcp_handler:
            self.logger.warning("Async MCP Handler not available, cannot send probe")
            return

        self.logger.debug(f"Sending async health probe to {target_id}")
        probe_message = MessageFactory.create_command(
            command="health_ping",
            params={"timestamp": time.time(), "request_timestamp": time.time()}, # Add request timestamp
            sender_id=self.component_id,
            receiver_id=target_id,
            priority=MessagePriority.LOW
        )
        try:
            response = await self.mcp_handler.send_message(probe_message)
            if response and response.status == MessageStatus.SUCCESS:
                 latency = (time.time() - response.payload.get("request_timestamp", time.time())) * 1000
                 await self.record_message_transit(self.component_id, target_id, latency, True)
            elif response:
                 await self.record_message_transit(self.component_id, target_id, -1, False)
            # Handle timeout implicitly via missed heartbeats
        except Exception as e:
            self.logger.error(f"Error sending async probe to {target_id}: {e}")
            await self.record_message_transit(self.component_id, target_id, -1, False)

    async def _trigger_healing_actions(self, node_ids: List[str] = None, link_ids: List[str] = None) -> None:
        node_ids = node_ids or []
        link_ids = link_ids or []
        if not node_ids and not link_ids: return

        self.logger.warning(f"Async healing action triggered for nodes: {node_ids}, links: {link_ids}")
        
        # PKI Feedback (run concurrently)
        feedback_tasks = []
        if self.pki_service:
            for node_id in node_ids:
                # Provide negative feedback for routes involving this node
                # feedback_tasks.append(self.pki_service.provide_feedback(...))
                pass
            for link_id in link_ids:
                # Provide negative feedback for routes involving this link
                # feedback_tasks.append(self.pki_service.provide_feedback(...))
                pass
        
        await asyncio.gather(*feedback_tasks)
        await self._update_routing_table() # Recompute routes

    async def _update_routing_table(self) -> None:
        self.logger.debug("Updating async routing table...")
        async with self.lock:
            # Copy data needed for calculation to avoid holding lock too long
            current_node_health = self.node_health.copy()
            current_link_health = self.link_health.copy()
        
        # Perform calculation outside the lock (can be CPU intensive)
        loop = asyncio.get_event_loop()
        new_routing_table = await loop.run_in_executor(
            None, self._calculate_routing_table, current_node_health, current_link_health
        )

        async with self.lock:
            if new_routing_table != self.routing_table:
                self.logger.info(f"Async routing table updated. {len(new_routing_table)} entries.")
                self.routing_table = new_routing_table
                # TODO: Disseminate routing updates if necessary
            else:
                self.logger.debug("Async routing table unchanged.")

    def _calculate_routing_table(self, node_health: Dict[str, NodeHealth], link_health: Dict[str, LinkHealth]) -> Dict[Tuple[str, str], str]:
        """Synchronous helper function to calculate routing table (can be run in executor)."""
        new_routing_table = {}
        nodes = [nid for nid, health in node_health.items() if health.status != "failed"]
        if not nodes: return {}

        adj = defaultdict(dict)
        for link_id, link in link_health.items():
            if link.status != "failed":
                n1, n2 = link.source_id, link.target_id
                if n1 in nodes and n2 in nodes:
                    weight = link.latency_ms if link.latency_ms > 0 else 1.0
                    adj[n1][n2] = weight
                    adj[n2][n1] = weight
        
        for start_node in nodes:
            distances = {node: float(\'inf\') for node in nodes}
            previous_nodes = {node: None for node in nodes}
            distances[start_node] = 0
            priority_queue = [(0, start_node)]

            processed_nodes = set()
            while priority_queue:
                current_distance, current_node = min(priority_queue, key=lambda x: x[0])
                priority_queue.remove((current_distance, current_node))

                if current_node in processed_nodes:
                    continue
                processed_nodes.add(current_node)

                if current_node in adj:
                    for neighbor, weight in adj[current_node].items():
                        if neighbor not in processed_nodes:
                             distance = current_distance + weight
                             if distance < distances[neighbor]:
                                 distances[neighbor] = distance
                                 previous_nodes[neighbor] = current_node
                                 # Update priority in queue if exists, else add
                                 pq_entry = next(((d, n) for d, n in priority_queue if n == neighbor), None)
                                 if pq_entry:
                                     priority_queue.remove(pq_entry)
                                 priority_queue.append((distance, neighbor))
            
            for target_node in nodes:
                if start_node == target_node: continue
                path_node = target_node
                next_hop = None
                # Check if reachable
                if distances[target_node] == float(\'inf\'): continue 
                while previous_nodes[path_node] is not None:
                    if previous_nodes[path_node] == start_node:
                        next_hop = path_node
                        break
                    path_node = previous_nodes[path_node]
                if next_hop:
                    new_routing_table[(start_node, target_node)] = next_hop
        return new_routing_table

    async def get_next_hop(self, source_id: str, target_id: str) -> Optional[str]:
        if self.pki_service:
            # context = {...} # Gather context needed by PKI
            # return await self.pki_service.optimize_route(source_id, [target_id], context=context)
            pass # Async PKI integration logic here
        
        async with self.lock:
            return self.routing_table.get((source_id, target_id))

    # --- Async ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "update_node_health":
                params = msg_obj.params
                if "node_id" in params and "status" in params:
                    await self.update_node_status(params["node_id"], params["status"], params.get("metrics"))
                    response_payload = {"status": "node_health_updated"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing node_id or status"}
            elif msg_obj.command == "update_link_health":
                params = msg_obj.params
                if "source_id" in params and "target_id" in params and "status" in params:
                    await self.update_link_status(params["source_id"], params["target_id"], params["status"], params.get("metrics"))
                    response_payload = {"status": "link_health_updated"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing source_id, target_id, or status"}
            elif msg_obj.command == "trigger_health_check":
                await self.perform_health_checks()
                response_payload = {"status": "health_check_triggered"}
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            async with self.lock:
                if msg_obj.query == "get_node_health":
                    node_id = msg_obj.params.get("node_id")
                    if node_id:
                        health = self.node_health.get(node_id)
                        response_payload = health.to_dict() if health else None
                    else:
                        response_payload = {nid: h.to_dict() for nid, h in self.node_health.items()}
                elif msg_obj.query == "get_link_health":
                    link_id = msg_obj.params.get("link_id")
                    if link_id:
                        health = self.link_health.get(link_id)
                        response_payload = health.to_dict() if health else None
                    else:
                        response_payload = {lid: h.to_dict() for lid, h in self.link_health.items()}
                elif msg_obj.query == "get_topology":
                    response_payload = {node: list(neighbors) for node, neighbors in self.mesh_topology.items()}
                elif msg_obj.query == "get_routing_table":
                    response_payload = {f"{src}->{tgt}": hop for (src, tgt), hop in self.routing_table.items()}
                elif msg_obj.query == "get_next_hop":
                     params = msg_obj.params
                     if "source_id" in params and "target_id" in params:
                         # Need to call async version if PKI is used
                         next_hop = self.routing_table.get((params["source_id"], params["target_id"]))
                         response_payload = {"next_hop": next_hop}
                     else:
                         status = MessageStatus.FAILED
                         response_payload = {"error": "Missing source_id or target_id"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        elif isinstance(msg_obj, EventMessage):
            if msg_obj.event_type == "node_joined":
                node_id = msg_obj.payload.get("node_id")
                if node_id:
                    await self._get_or_create_node_health(node_id)
                    await self.update_node_status(node_id, "healthy", msg_obj.payload.get("metrics"))
            elif msg_obj.event_type == "node_left":
                node_id = msg_obj.payload.get("node_id")
                async with self.lock:
                    node_exists = node_id in self.node_health
                if node_id and node_exists:
                    await self.update_node_status(node_id, "failed") # update_node_status handles healing trigger
            return None
        else:
            return None

        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        async with self.lock:
            num_nodes = len(self.node_health)
            num_links = len(self.link_health)
            num_failed_nodes = sum(1 for n in self.node_health.values() if n.status == "failed")
            num_failed_links = sum(1 for l in self.link_health.values() if l.status == "failed")
            routing_table_size = len(self.routing_table)
        
        return {
            "status": "healthy" if self._monitor_task and not self._monitor_task.done() else "degraded",
            "monitoring_active": self._monitor_task is not None and not self._monitor_task.done(),
            "probing_active": self._probe_task is not None and not self._probe_task.done(),
            "tracked_nodes": num_nodes,
            "tracked_links": num_links,
            "failed_nodes": num_failed_nodes,
            "failed_links": num_failed_links,
            "routing_table_size": routing_table_size,
            "discovery_service_status": "configured" if self.discovery_service else "not_configured",
            "pki_service_status": "configured" if self.pki_service else "not_configured",
            "mcp_handler_status": "configured" if self.mcp_handler else "not_configured"
        }

    async def get_manifest(self) -> Dict[str, Any]:
        manifest = await super().get_manifest()
        health_status = await self.health_check()
        manifest.update(health_status)
        return manifest

    def __del__(self):
        # Ensure tasks are stopped when the object is deleted
        # This might not always be called reliably in Python
        if self._monitor_task or self._probe_task:
             try:
                 loop = asyncio.get_event_loop()
                 if loop.is_running():
                     loop.create_task(self.stop_monitoring())
                 else:
                     # If no loop running, can't schedule stop_monitoring
                     pass 
             except RuntimeError: # No event loop
                 pass
"""
