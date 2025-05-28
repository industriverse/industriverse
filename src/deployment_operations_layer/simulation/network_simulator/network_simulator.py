"""
Network Simulator

This module is responsible for simulating network conditions and behaviors
in various deployment environments. It provides realistic network simulation
for testing deployment scenarios under different network conditions.
"""

import logging
import time
import random
import threading
import math
from typing import Dict, List, Any, Optional, Callable, Tuple

logger = logging.getLogger(__name__)

class NetworkSimulator:
    """
    Simulates network conditions and behaviors in deployment environments.
    
    This class provides realistic network simulation for testing deployment scenarios
    under different network conditions, including bandwidth limitations, latency,
    packet loss, and network partitions. It can simulate various network profiles
    and scenarios, including edge networks, cloud networks, and hybrid deployments.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Network Simulator.
        
        Args:
            config: Configuration dictionary for the simulator
        """
        self.config = config or {}
        
        # Network profiles
        self.network_profiles = self.config.get("network_profiles", {})
        if not self.network_profiles:
            self._initialize_default_profiles()
        
        # Network topology
        self.network_topology = self.config.get("network_topology", {})
        if not self.network_topology:
            self._initialize_default_topology()
        
        # Current simulation state
        self.current_simulation = None
        self.simulation_thread = None
        self.simulation_stop_event = threading.Event()
        
        # Network state
        self.network_state = {
            "nodes": {},
            "links": {},
            "global": {
                "bandwidth_utilization": 0,
                "average_latency": 0,
                "packet_loss": 0,
                "partitioned": False
            }
        }
        
        # Initialize network state
        self._initialize_network_state()
        
        logger.info("Network Simulator initialized")
    
    def _initialize_default_profiles(self):
        """
        Initialize default network profiles.
        """
        self.network_profiles = {
            "high_performance": {
                "description": "High performance network with high bandwidth and low latency",
                "bandwidth": {
                    "capacity": 10000,  # 10 Gbps
                    "utilization_range": [5, 20]
                },
                "latency": {
                    "base": 1,  # 1 ms
                    "jitter": 0.5,  # 0.5 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 0.01,  # 0.01%
                    "burst_probability": 0.001
                },
                "partition": {
                    "probability": 0.0001,
                    "duration_range": [5, 30]  # seconds
                }
            },
            "standard_datacenter": {
                "description": "Standard datacenter network with good bandwidth and low latency",
                "bandwidth": {
                    "capacity": 1000,  # 1 Gbps
                    "utilization_range": [10, 40]
                },
                "latency": {
                    "base": 5,  # 5 ms
                    "jitter": 2,  # 2 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 0.05,  # 0.05%
                    "burst_probability": 0.005
                },
                "partition": {
                    "probability": 0.001,
                    "duration_range": [10, 60]  # seconds
                }
            },
            "cloud_region": {
                "description": "Cross-region cloud network with moderate bandwidth and latency",
                "bandwidth": {
                    "capacity": 500,  # 500 Mbps
                    "utilization_range": [20, 60]
                },
                "latency": {
                    "base": 50,  # 50 ms
                    "jitter": 10,  # 10 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 0.1,  # 0.1%
                    "burst_probability": 0.01
                },
                "partition": {
                    "probability": 0.005,
                    "duration_range": [30, 300]  # seconds
                }
            },
            "wan": {
                "description": "Wide area network with limited bandwidth and high latency",
                "bandwidth": {
                    "capacity": 100,  # 100 Mbps
                    "utilization_range": [30, 80]
                },
                "latency": {
                    "base": 100,  # 100 ms
                    "jitter": 20,  # 20 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 0.5,  # 0.5%
                    "burst_probability": 0.05
                },
                "partition": {
                    "probability": 0.01,
                    "duration_range": [60, 600]  # seconds
                }
            },
            "edge": {
                "description": "Edge network with very limited bandwidth and high latency",
                "bandwidth": {
                    "capacity": 10,  # 10 Mbps
                    "utilization_range": [40, 90]
                },
                "latency": {
                    "base": 200,  # 200 ms
                    "jitter": 50,  # 50 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 2,  # 2%
                    "burst_probability": 0.1
                },
                "partition": {
                    "probability": 0.05,
                    "duration_range": [300, 1800]  # seconds
                }
            },
            "mobile": {
                "description": "Mobile network with variable bandwidth and high latency",
                "bandwidth": {
                    "capacity": 5,  # 5 Mbps
                    "utilization_range": [50, 95]
                },
                "latency": {
                    "base": 300,  # 300 ms
                    "jitter": 100,  # 100 ms
                    "distribution": "normal"
                },
                "packet_loss": {
                    "rate": 5,  # 5%
                    "burst_probability": 0.2
                },
                "partition": {
                    "probability": 0.1,
                    "duration_range": [600, 3600]  # seconds
                }
            }
        }
    
    def _initialize_default_topology(self):
        """
        Initialize default network topology.
        """
        self.network_topology = {
            "nodes": {
                "datacenter-1": {
                    "type": "datacenter",
                    "profile": "standard_datacenter"
                },
                "datacenter-2": {
                    "type": "datacenter",
                    "profile": "standard_datacenter"
                },
                "cloud-region-1": {
                    "type": "cloud",
                    "profile": "cloud_region"
                },
                "cloud-region-2": {
                    "type": "cloud",
                    "profile": "cloud_region"
                },
                "edge-1": {
                    "type": "edge",
                    "profile": "edge"
                },
                "edge-2": {
                    "type": "edge",
                    "profile": "edge"
                },
                "mobile-1": {
                    "type": "mobile",
                    "profile": "mobile"
                }
            },
            "links": {
                "datacenter-1-datacenter-2": {
                    "source": "datacenter-1",
                    "target": "datacenter-2",
                    "profile": "high_performance"
                },
                "datacenter-1-cloud-region-1": {
                    "source": "datacenter-1",
                    "target": "cloud-region-1",
                    "profile": "wan"
                },
                "datacenter-2-cloud-region-2": {
                    "source": "datacenter-2",
                    "target": "cloud-region-2",
                    "profile": "wan"
                },
                "cloud-region-1-cloud-region-2": {
                    "source": "cloud-region-1",
                    "target": "cloud-region-2",
                    "profile": "cloud_region"
                },
                "cloud-region-1-edge-1": {
                    "source": "cloud-region-1",
                    "target": "edge-1",
                    "profile": "edge"
                },
                "cloud-region-2-edge-2": {
                    "source": "cloud-region-2",
                    "target": "edge-2",
                    "profile": "edge"
                },
                "edge-1-mobile-1": {
                    "source": "edge-1",
                    "target": "mobile-1",
                    "profile": "mobile"
                }
            }
        }
    
    def _initialize_network_state(self):
        """
        Initialize network state based on topology.
        """
        # Initialize nodes
        for node_id, node_config in self.network_topology["nodes"].items():
            profile_name = node_config.get("profile", "standard_datacenter")
            profile = self.network_profiles.get(profile_name, self.network_profiles["standard_datacenter"])
            
            self.network_state["nodes"][node_id] = {
                "type": node_config.get("type", "unknown"),
                "profile": profile_name,
                "bandwidth": {
                    "capacity": profile["bandwidth"]["capacity"],
                    "available": profile["bandwidth"]["capacity"],
                    "utilized": 0,
                    "utilization_percent": 0
                },
                "latency": profile["latency"]["base"],
                "packet_loss": profile["packet_loss"]["rate"],
                "partitioned": False,
                "partition_until": 0
            }
        
        # Initialize links
        for link_id, link_config in self.network_topology["links"].items():
            profile_name = link_config.get("profile", "standard_datacenter")
            profile = self.network_profiles.get(profile_name, self.network_profiles["standard_datacenter"])
            
            self.network_state["links"][link_id] = {
                "source": link_config["source"],
                "target": link_config["target"],
                "profile": profile_name,
                "bandwidth": {
                    "capacity": profile["bandwidth"]["capacity"],
                    "available": profile["bandwidth"]["capacity"],
                    "utilized": 0,
                    "utilization_percent": 0
                },
                "latency": profile["latency"]["base"],
                "packet_loss": profile["packet_loss"]["rate"],
                "partitioned": False,
                "partition_until": 0
            }
    
    def start_simulation(self, 
                        duration_seconds: int = 300,
                        scenario: Optional[str] = None,
                        custom_topology: Optional[Dict[str, Any]] = None,
                        callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Start a network simulation.
        
        Args:
            duration_seconds: Duration of the simulation in seconds
            scenario: Optional scenario name (e.g., "normal", "congestion", "partition")
            custom_topology: Optional custom network topology
            callback: Optional callback function to receive state updates
            
        Returns:
            Dictionary with simulation information
        """
        # Stop any existing simulation
        self.stop_simulation()
        
        # Use custom topology if provided
        if custom_topology:
            self.network_topology = custom_topology
            self._initialize_network_state()
        
        # Initialize simulation
        self.current_simulation = {
            "id": f"net-sim-{int(time.time())}",
            "scenario": scenario or "normal",
            "start_time": time.time(),
            "end_time": time.time() + duration_seconds,
            "duration_seconds": duration_seconds,
            "status": "running",
            "callback": callback
        }
        
        # Apply scenario-specific configuration
        if scenario:
            self._apply_scenario(scenario)
        
        # Start simulation thread
        self.simulation_stop_event.clear()
        self.simulation_thread = threading.Thread(
            target=self._run_simulation,
            args=(self.current_simulation, self.simulation_stop_event)
        )
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        logger.info(f"Started network simulation {self.current_simulation['id']} with scenario {scenario or 'normal'}")
        
        return {
            "simulation_id": self.current_simulation["id"],
            "scenario": scenario or "normal",
            "duration_seconds": duration_seconds,
            "start_time": self.current_simulation["start_time"]
        }
    
    def stop_simulation(self) -> bool:
        """
        Stop the current simulation.
        
        Returns:
            True if a simulation was stopped, False otherwise
        """
        if not self.current_simulation:
            return False
        
        logger.info(f"Stopping network simulation {self.current_simulation['id']}")
        
        # Signal thread to stop
        self.simulation_stop_event.set()
        
        # Wait for thread to finish
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5)
        
        # Update simulation status
        if self.current_simulation:
            self.current_simulation["status"] = "stopped"
            self.current_simulation["end_time"] = time.time()
        
        # Reset state
        self.simulation_thread = None
        self.current_simulation = None
        
        return True
    
    def get_network_state(self) -> Dict[str, Any]:
        """
        Get the current network state.
        
        Returns:
            Dictionary containing current network state
        """
        return self.network_state.copy()
    
    def get_simulation_status(self) -> Optional[Dict[str, Any]]:
        """
        Get the status of the current simulation.
        
        Returns:
            Dictionary containing simulation status or None if no simulation is running
        """
        if not self.current_simulation:
            return None
        
        return {
            "simulation_id": self.current_simulation["id"],
            "scenario": self.current_simulation["scenario"],
            "start_time": self.current_simulation["start_time"],
            "end_time": self.current_simulation["end_time"],
            "duration_seconds": self.current_simulation["duration_seconds"],
            "elapsed_seconds": time.time() - self.current_simulation["start_time"],
            "remaining_seconds": max(0, self.current_simulation["end_time"] - time.time()),
            "status": self.current_simulation["status"]
        }
    
    def _apply_scenario(self, scenario: str):
        """
        Apply a predefined scenario to the network.
        
        Args:
            scenario: Scenario name
        """
        if scenario == "normal":
            # Normal operation, no changes
            pass
        
        elif scenario == "congestion":
            # Simulate network congestion
            for link_id, link_state in self.network_state["links"].items():
                # Increase utilization
                profile = self.network_profiles.get(link_state["profile"], {})
                bandwidth_profile = profile.get("bandwidth", {})
                utilization_range = bandwidth_profile.get("utilization_range", [0, 0])
                
                # Set utilization to high end of range
                utilization = utilization_range[1] if len(utilization_range) > 1 else 80
                utilized = link_state["bandwidth"]["capacity"] * (utilization / 100)
                
                link_state["bandwidth"]["utilized"] = utilized
                link_state["bandwidth"]["available"] = max(0, link_state["bandwidth"]["capacity"] - utilized)
                link_state["bandwidth"]["utilization_percent"] = utilization
                
                # Increase latency
                link_state["latency"] *= 2
        
        elif scenario == "partition":
            # Simulate network partition
            # Choose a random link to partition
            link_ids = list(self.network_state["links"].keys())
            if link_ids:
                partition_link_id = random.choice(link_ids)
                link_state = self.network_state["links"][partition_link_id]
                
                # Partition the link
                link_state["partitioned"] = True
                link_state["partition_until"] = time.time() + 60  # 1 minute partition
                
                logger.info(f"Partitioned link {partition_link_id} for 60 seconds")
        
        elif scenario == "high_latency":
            # Simulate high latency
            for link_id, link_state in self.network_state["links"].items():
                # Increase latency
                link_state["latency"] *= 5
        
        elif scenario == "packet_loss":
            # Simulate high packet loss
            for link_id, link_state in self.network_state["links"].items():
                # Increase packet loss
                link_state["packet_loss"] = min(20, link_state["packet_loss"] * 10)
        
        elif scenario == "edge_failure":
            # Simulate edge node failure
            for node_id, node_state in self.network_state["nodes"].items():
                if node_state["type"] == "edge":
                    # Partition the node
                    node_state["partitioned"] = True
                    node_state["partition_until"] = time.time() + 300  # 5 minute partition
                    
                    logger.info(f"Partitioned edge node {node_id} for 300 seconds")
        
        elif scenario == "datacenter_failure":
            # Simulate datacenter failure
            for node_id, node_state in self.network_state["nodes"].items():
                if node_state["type"] == "datacenter":
                    # Partition the node
                    node_state["partitioned"] = True
                    node_state["partition_until"] = time.time() + 180  # 3 minute partition
                    
                    logger.info(f"Partitioned datacenter node {node_id} for 180 seconds")
                    break  # Only partition one datacenter
        
        elif scenario == "cloud_degradation":
            # Simulate cloud service degradation
            for node_id, node_state in self.network_state["nodes"].items():
                if node_state["type"] == "cloud":
                    # Degrade performance
                    node_state["latency"] *= 3
                    node_state["packet_loss"] = min(10, node_state["packet_loss"] * 5)
                    
                    # Reduce bandwidth
                    node_state["bandwidth"]["capacity"] /= 2
                    node_state["bandwidth"]["available"] = node_state["bandwidth"]["capacity"]
                    
                    logger.info(f"Degraded cloud node {node_id} performance")
        
        else:
            logger.warning(f"Unknown scenario: {scenario}")
    
    def _run_simulation(self, simulation: Dict[str, Any], stop_event: threading.Event):
        """
        Run the simulation.
        
        Args:
            simulation: Simulation configuration
            stop_event: Event to signal simulation to stop
        """
        scenario = simulation["scenario"]
        callback = simulation.get("callback")
        
        # Simulation loop
        while not stop_event.is_set():
            # Check if simulation time is up
            if time.time() >= simulation["end_time"]:
                logger.info(f"Simulation {simulation['id']} completed")
                simulation["status"] = "completed"
                break
            
            # Update network state
            self._update_network_state(scenario)
            
            # Update global state
            self._update_global_state()
            
            # Call callback if provided
            if callback:
                try:
                    callback(self.get_network_state())
                except Exception as e:
                    logger.error(f"Error in simulation callback: {e}")
            
            # Sleep for a short time
            time.sleep(1)
    
    def _update_network_state(self, scenario: str):
        """
        Update network state.
        
        Args:
            scenario: Simulation scenario
        """
        # Update nodes
        for node_id, node_state in self.network_state["nodes"].items():
            self._update_node_state(node_id, node_state, scenario)
        
        # Update links
        for link_id, link_state in self.network_state["links"].items():
            self._update_link_state(link_id, link_state, scenario)
    
    def _update_node_state(self, node_id: str, node_state: Dict[str, Any], scenario: str):
        """
        Update node state.
        
        Args:
            node_id: Node ID
            node_state: Node state
            scenario: Simulation scenario
        """
        # Check if node is partitioned
        if node_state["partitioned"] and time.time() > node_state["partition_until"]:
            node_state["partitioned"] = False
            logger.info(f"Node {node_id} partition healed")
        
        # Get profile
        profile_name = node_state["profile"]
        profile = self.network_profiles.get(profile_name, {})
        
        # Update bandwidth
        bandwidth_profile = profile.get("bandwidth", {})
        utilization_range = bandwidth_profile.get("utilization_range", [0, 0])
        
        # Adjust utilization based on scenario
        if scenario == "congestion":
            # Higher utilization for congestion scenario
            utilization = random.uniform(
                utilization_range[1] * 0.8 if len(utilization_range) > 1 else 70,
                utilization_range[1] if len(utilization_range) > 1 else 90
            )
        else:
            # Normal utilization
            utilization = random.uniform(
                utilization_range[0] if len(utilization_range) > 0 else 0,
                utilization_range[1] if len(utilization_range) > 1 else 50
            )
        
        utilized = node_state["bandwidth"]["capacity"] * (utilization / 100)
        
        node_state["bandwidth"]["utilized"] = utilized
        node_state["bandwidth"]["available"] = max(0, node_state["bandwidth"]["capacity"] - utilized)
        node_state["bandwidth"]["utilization_percent"] = utilization
        
        # Update latency
        latency_profile = profile.get("latency", {})
        base_latency = latency_profile.get("base", 0)
        jitter = latency_profile.get("jitter", 0)
        distribution = latency_profile.get("distribution", "normal")
        
        if distribution == "normal":
            # Normal distribution around base latency
            latency = random.normalvariate(base_latency, jitter / 3)
        else:
            # Uniform distribution
            latency = random.uniform(base_latency - jitter, base_latency + jitter)
        
        # Ensure latency is positive
        latency = max(0.1, latency)
        
        # Adjust latency based on scenario
        if scenario == "high_latency":
            latency *= 5
        elif scenario == "congestion":
            latency *= 2
        
        node_state["latency"] = latency
        
        # Update packet loss
        packet_loss_profile = profile.get("packet_loss", {})
        base_packet_loss = packet_loss_profile.get("rate", 0)
        burst_probability = packet_loss_profile.get("burst_probability", 0)
        
        # Check for packet loss burst
        if random.random() < burst_probability:
            # Burst of packet loss
            packet_loss = base_packet_loss * random.uniform(5, 10)
        else:
            # Normal packet loss
            packet_loss = base_packet_loss * random.uniform(0.5, 1.5)
        
        # Adjust packet loss based on scenario
        if scenario == "packet_loss":
            packet_loss *= 10
        elif scenario == "congestion":
            packet_loss *= 2
        
        node_state["packet_loss"] = packet_loss
        
        # Check for partition
        partition_profile = profile.get("partition", {})
        partition_probability = partition_profile.get("probability", 0)
        
        # Adjust partition probability based on scenario
        if scenario == "partition":
            partition_probability *= 10
        
        if not node_state["partitioned"] and random.random() < partition_probability:
            # Partition the node
            node_state["partitioned"] = True
            
            # Determine partition duration
            duration_range = partition_profile.get("duration_range", [0, 0])
            duration = random.uniform(
                duration_range[0] if len(duration_range) > 0 else 10,
                duration_range[1] if len(duration_range) > 1 else 60
            )
            
            node_state["partition_until"] = time.time() + duration
            
            logger.info(f"Node {node_id} partitioned for {duration:.1f} seconds")
    
    def _update_link_state(self, link_id: str, link_state: Dict[str, Any], scenario: str):
        """
        Update link state.
        
        Args:
            link_id: Link ID
            link_state: Link state
            scenario: Simulation scenario
        """
        # Check if link is partitioned
        if link_state["partitioned"] and time.time() > link_state["partition_until"]:
            link_state["partitioned"] = False
            logger.info(f"Link {link_id} partition healed")
        
        # Get profile
        profile_name = link_state["profile"]
        profile = self.network_profiles.get(profile_name, {})
        
        # Update bandwidth
        bandwidth_profile = profile.get("bandwidth", {})
        utilization_range = bandwidth_profile.get("utilization_range", [0, 0])
        
        # Adjust utilization based on scenario
        if scenario == "congestion":
            # Higher utilization for congestion scenario
            utilization = random.uniform(
                utilization_range[1] * 0.8 if len(utilization_range) > 1 else 70,
                utilization_range[1] if len(utilization_range) > 1 else 90
            )
        else:
            # Normal utilization
            utilization = random.uniform(
                utilization_range[0] if len(utilization_range) > 0 else 0,
                utilization_range[1] if len(utilization_range) > 1 else 50
            )
        
        utilized = link_state["bandwidth"]["capacity"] * (utilization / 100)
        
        link_state["bandwidth"]["utilized"] = utilized
        link_state["bandwidth"]["available"] = max(0, link_state["bandwidth"]["capacity"] - utilized)
        link_state["bandwidth"]["utilization_percent"] = utilization
        
        # Update latency
        latency_profile = profile.get("latency", {})
        base_latency = latency_profile.get("base", 0)
        jitter = latency_profile.get("jitter", 0)
        distribution = latency_profile.get("distribution", "normal")
        
        if distribution == "normal":
            # Normal distribution around base latency
            latency = random.normalvariate(base_latency, jitter / 3)
        else:
            # Uniform distribution
            latency = random.uniform(base_latency - jitter, base_latency + jitter)
        
        # Ensure latency is positive
        latency = max(0.1, latency)
        
        # Adjust latency based on scenario
        if scenario == "high_latency":
            latency *= 5
        elif scenario == "congestion":
            latency *= 2
        
        link_state["latency"] = latency
        
        # Update packet loss
        packet_loss_profile = profile.get("packet_loss", {})
        base_packet_loss = packet_loss_profile.get("rate", 0)
        burst_probability = packet_loss_profile.get("burst_probability", 0)
        
        # Check for packet loss burst
        if random.random() < burst_probability:
            # Burst of packet loss
            packet_loss = base_packet_loss * random.uniform(5, 10)
        else:
            # Normal packet loss
            packet_loss = base_packet_loss * random.uniform(0.5, 1.5)
        
        # Adjust packet loss based on scenario
        if scenario == "packet_loss":
            packet_loss *= 10
        elif scenario == "congestion":
            packet_loss *= 2
        
        link_state["packet_loss"] = packet_loss
        
        # Check for partition
        partition_profile = profile.get("partition", {})
        partition_probability = partition_profile.get("probability", 0)
        
        # Adjust partition probability based on scenario
        if scenario == "partition":
            partition_probability *= 10
        
        if not link_state["partitioned"] and random.random() < partition_probability:
            # Partition the link
            link_state["partitioned"] = True
            
            # Determine partition duration
            duration_range = partition_profile.get("duration_range", [0, 0])
            duration = random.uniform(
                duration_range[0] if len(duration_range) > 0 else 10,
                duration_range[1] if len(duration_range) > 1 else 60
            )
            
            link_state["partition_until"] = time.time() + duration
            
            logger.info(f"Link {link_id} partitioned for {duration:.1f} seconds")
    
    def _update_global_state(self):
        """
        Update global network state.
        """
        # Calculate global bandwidth utilization
        total_capacity = 0
        total_utilized = 0
        
        for link_id, link_state in self.network_state["links"].items():
            total_capacity += link_state["bandwidth"]["capacity"]
            total_utilized += link_state["bandwidth"]["utilized"]
        
        global_bandwidth_utilization = (total_utilized / total_capacity * 100) if total_capacity > 0 else 0
        
        # Calculate global average latency
        latencies = [link_state["latency"] for link_state in self.network_state["links"].values()]
        global_average_latency = sum(latencies) / len(latencies) if latencies else 0
        
        # Calculate global packet loss
        packet_losses = [link_state["packet_loss"] for link_state in self.network_state["links"].values()]
        global_packet_loss = sum(packet_losses) / len(packet_losses) if packet_losses else 0
        
        # Check for global partition
        partitioned_links = [link_state for link_state in self.network_state["links"].values() if link_state["partitioned"]]
        global_partitioned = len(partitioned_links) > 0
        
        # Update global state
        self.network_state["global"] = {
            "bandwidth_utilization": global_bandwidth_utilization,
            "average_latency": global_average_latency,
            "packet_loss": global_packet_loss,
            "partitioned": global_partitioned
        }
    
    def calculate_path_metrics(self, source_node: str, target_node: str) -> Dict[str, Any]:
        """
        Calculate network metrics for a path between two nodes.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            
        Returns:
            Dictionary containing path metrics
        """
        # Find path between nodes
        path = self._find_path(source_node, target_node)
        
        if not path:
            return {
                "status": "no_path",
                "message": f"No path found between {source_node} and {target_node}"
            }
        
        # Calculate path metrics
        bandwidth = float('inf')
        latency = 0
        packet_loss = 0
        partitioned = False
        
        # Process each link in the path
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Find link between source and target
            link_id = None
            for lid, link_state in self.network_state["links"].items():
                if (link_state["source"] == source and link_state["target"] == target) or \
                   (link_state["source"] == target and link_state["target"] == source):
                    link_id = lid
                    break
            
            if not link_id:
                return {
                    "status": "invalid_path",
                    "message": f"No link found between {source} and {target}"
                }
            
            link_state = self.network_state["links"][link_id]
            
            # Update bandwidth (minimum bandwidth along the path)
            link_bandwidth = link_state["bandwidth"]["available"]
            bandwidth = min(bandwidth, link_bandwidth)
            
            # Update latency (sum of latencies along the path)
            latency += link_state["latency"]
            
            # Update packet loss (compound packet loss along the path)
            packet_loss = packet_loss + link_state["packet_loss"] - (packet_loss * link_state["packet_loss"] / 100)
            
            # Update partition status
            partitioned = partitioned or link_state["partitioned"]
        
        # Handle infinite bandwidth
        if bandwidth == float('inf'):
            bandwidth = 0
        
        return {
            "status": "calculated",
            "path": path,
            "bandwidth": bandwidth,
            "latency": latency,
            "packet_loss": packet_loss,
            "partitioned": partitioned
        }
    
    def _find_path(self, source_node: str, target_node: str) -> List[str]:
        """
        Find a path between two nodes using breadth-first search.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            
        Returns:
            List of node IDs representing the path, or empty list if no path found
        """
        if source_node not in self.network_state["nodes"] or target_node not in self.network_state["nodes"]:
            return []
        
        # Check if source or target is partitioned
        if self.network_state["nodes"][source_node]["partitioned"] or self.network_state["nodes"][target_node]["partitioned"]:
            return []
        
        # Build adjacency list
        adjacency = {}
        for node_id in self.network_state["nodes"]:
            adjacency[node_id] = []
        
        for link_id, link_state in self.network_state["links"].items():
            if not link_state["partitioned"]:
                source = link_state["source"]
                target = link_state["target"]
                
                if source in adjacency and target in adjacency:
                    adjacency[source].append(target)
                    adjacency[target].append(source)  # Bidirectional
        
        # Breadth-first search
        queue = [(source_node, [source_node])]
        visited = set([source_node])
        
        while queue:
            node, path = queue.pop(0)
            
            if node == target_node:
                return path
            
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def create_network_profile(self, 
                              name: str,
                              description: str,
                              bandwidth_capacity: int,
                              bandwidth_utilization_range: List[float],
                              latency_base: float,
                              latency_jitter: float,
                              packet_loss_rate: float,
                              packet_loss_burst_probability: float,
                              partition_probability: float,
                              partition_duration_range: List[float]) -> Dict[str, Any]:
        """
        Create a custom network profile.
        
        Args:
            name: Profile name
            description: Profile description
            bandwidth_capacity: Bandwidth capacity in Mbps
            bandwidth_utilization_range: Bandwidth utilization range [min, max] in percent
            latency_base: Base latency in milliseconds
            latency_jitter: Latency jitter in milliseconds
            packet_loss_rate: Packet loss rate in percent
            packet_loss_burst_probability: Probability of packet loss burst
            partition_probability: Probability of network partition
            partition_duration_range: Partition duration range [min, max] in seconds
            
        Returns:
            Created profile
        """
        profile = {
            "description": description,
            "bandwidth": {
                "capacity": bandwidth_capacity,
                "utilization_range": bandwidth_utilization_range
            },
            "latency": {
                "base": latency_base,
                "jitter": latency_jitter,
                "distribution": "normal"
            },
            "packet_loss": {
                "rate": packet_loss_rate,
                "burst_probability": packet_loss_burst_probability
            },
            "partition": {
                "probability": partition_probability,
                "duration_range": partition_duration_range
            }
        }
        
        # Add to profiles
        self.network_profiles[name] = profile
        
        logger.info(f"Created network profile: {name}")
        
        return profile
    
    def create_custom_topology(self, 
                              nodes: Dict[str, Dict[str, Any]],
                              links: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a custom network topology.
        
        Args:
            nodes: Dictionary of node IDs to node configurations
            links: Dictionary of link IDs to link configurations
            
        Returns:
            Created topology
        """
        topology = {
            "nodes": nodes,
            "links": links
        }
        
        # Update topology
        self.network_topology = topology
        
        # Initialize network state
        self._initialize_network_state()
        
        logger.info(f"Created custom network topology with {len(nodes)} nodes and {len(links)} links")
        
        return topology
    
    def get_network_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a network profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Network profile or None if not found
        """
        return self.network_profiles.get(name)
    
    def list_network_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available network profiles.
        
        Returns:
            Dictionary of profile names to profiles
        """
        return self.network_profiles
    
    def get_network_topology(self) -> Dict[str, Any]:
        """
        Get the current network topology.
        
        Returns:
            Dictionary containing network topology
        """
        return self.network_topology
    
    def simulate_request(self, 
                        source_node: str,
                        target_node: str,
                        request_size_kb: float = 10,
                        response_size_kb: float = 100) -> Dict[str, Any]:
        """
        Simulate a request between two nodes.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            request_size_kb: Request size in KB
            response_size_kb: Response size in KB
            
        Returns:
            Dictionary containing request simulation results
        """
        # Calculate path metrics
        path_metrics = self.calculate_path_metrics(source_node, target_node)
        
        if path_metrics["status"] != "calculated":
            return {
                "status": "failed",
                "message": path_metrics.get("message", "Path calculation failed")
            }
        
        # Check if path is partitioned
        if path_metrics["partitioned"]:
            return {
                "status": "failed",
                "message": "Network partition detected in path"
            }
        
        # Calculate request time
        bandwidth_mbps = path_metrics["bandwidth"]
        latency_ms = path_metrics["latency"]
        packet_loss_percent = path_metrics["packet_loss"]
        
        # Convert sizes to megabits
        request_size_mb = request_size_kb / 1024
        response_size_mb = response_size_kb / 1024
        
        request_size_mbits = request_size_mb * 8
        response_size_mbits = response_size_mb * 8
        
        # Calculate transfer times
        if bandwidth_mbps <= 0:
            request_transfer_time_ms = float('inf')
            response_transfer_time_ms = float('inf')
        else:
            request_transfer_time_ms = (request_size_mbits / bandwidth_mbps) * 1000
            response_transfer_time_ms = (response_size_mbits / bandwidth_mbps) * 1000
        
        # Calculate total time with latency
        total_time_ms = latency_ms + request_transfer_time_ms + latency_ms + response_transfer_time_ms
        
        # Adjust for packet loss (simplified model)
        if packet_loss_percent > 0:
            # Assume each 1% of packet loss adds 10% to transfer time due to retransmissions
            packet_loss_factor = 1 + (packet_loss_percent * 0.1)
            total_time_ms *= packet_loss_factor
        
        # Determine if request succeeded
        succeeded = True
        message = "Request completed successfully"
        
        # Check for extreme conditions
        if packet_loss_percent > 20:
            succeeded = False
            message = f"Request failed due to excessive packet loss ({packet_loss_percent:.1f}%)"
        
        if total_time_ms > 30000:  # 30 seconds timeout
            succeeded = False
            message = f"Request timed out after {total_time_ms/1000:.1f} seconds"
        
        return {
            "status": "succeeded" if succeeded else "failed",
            "message": message,
            "path": path_metrics["path"],
            "bandwidth_mbps": bandwidth_mbps,
            "latency_ms": latency_ms,
            "packet_loss_percent": packet_loss_percent,
            "request_size_kb": request_size_kb,
            "response_size_kb": response_size_kb,
            "request_transfer_time_ms": request_transfer_time_ms,
            "response_transfer_time_ms": response_transfer_time_ms,
            "total_time_ms": total_time_ms
        }
