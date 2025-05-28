"""
Resource Simulator

This module is responsible for simulating resource availability and utilization
in various deployment environments. It provides realistic resource constraints
and behavior for deployment simulations.
"""

import logging
import time
import random
import threading
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class ResourceSimulator:
    """
    Simulates resource availability and utilization in deployment environments.
    
    This class provides realistic resource constraints and behavior for deployment
    simulations, including CPU, memory, storage, and network resources. It can
    simulate various resource profiles and scenarios, including resource contention,
    throttling, and failures.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Resource Simulator.
        
        Args:
            config: Configuration dictionary for the simulator
        """
        self.config = config or {}
        
        # Resource profiles
        self.resource_profiles = self.config.get("resource_profiles", {})
        if not self.resource_profiles:
            self._initialize_default_profiles()
        
        # Current simulation state
        self.current_simulation = None
        self.simulation_thread = None
        self.simulation_stop_event = threading.Event()
        
        # Resource state
        self.resource_state = {
            "cpu": {
                "total": 100,
                "available": 100,
                "utilized": 0
            },
            "memory": {
                "total": 100,
                "available": 100,
                "utilized": 0
            },
            "storage": {
                "total": 100,
                "available": 100,
                "utilized": 0
            },
            "network": {
                "bandwidth": {
                    "total": 100,
                    "available": 100,
                    "utilized": 0
                },
                "latency": 0,
                "packet_loss": 0
            }
        }
        
        logger.info("Resource Simulator initialized")
    
    def _initialize_default_profiles(self):
        """
        Initialize default resource profiles.
        """
        self.resource_profiles = {
            "high_availability": {
                "description": "High availability environment with abundant resources",
                "cpu": {
                    "total": 100,
                    "utilization_range": [5, 20],
                    "failure_probability": 0.001
                },
                "memory": {
                    "total": 100,
                    "utilization_range": [10, 30],
                    "failure_probability": 0.001
                },
                "storage": {
                    "total": 100,
                    "utilization_range": [5, 25],
                    "failure_probability": 0.001
                },
                "network": {
                    "bandwidth": {
                        "total": 100,
                        "utilization_range": [5, 30]
                    },
                    "latency_range": [1, 10],
                    "packet_loss_range": [0, 0.1]
                }
            },
            "standard": {
                "description": "Standard environment with moderate resources",
                "cpu": {
                    "total": 100,
                    "utilization_range": [20, 50],
                    "failure_probability": 0.01
                },
                "memory": {
                    "total": 100,
                    "utilization_range": [30, 60],
                    "failure_probability": 0.01
                },
                "storage": {
                    "total": 100,
                    "utilization_range": [20, 50],
                    "failure_probability": 0.01
                },
                "network": {
                    "bandwidth": {
                        "total": 100,
                        "utilization_range": [20, 50]
                    },
                    "latency_range": [10, 50],
                    "packet_loss_range": [0.1, 1]
                }
            },
            "constrained": {
                "description": "Constrained environment with limited resources",
                "cpu": {
                    "total": 100,
                    "utilization_range": [60, 90],
                    "failure_probability": 0.05
                },
                "memory": {
                    "total": 100,
                    "utilization_range": [70, 90],
                    "failure_probability": 0.05
                },
                "storage": {
                    "total": 100,
                    "utilization_range": [60, 85],
                    "failure_probability": 0.05
                },
                "network": {
                    "bandwidth": {
                        "total": 100,
                        "utilization_range": [60, 90]
                    },
                    "latency_range": [50, 200],
                    "packet_loss_range": [1, 5]
                }
            },
            "edge": {
                "description": "Edge environment with very limited resources",
                "cpu": {
                    "total": 50,
                    "utilization_range": [40, 90],
                    "failure_probability": 0.1
                },
                "memory": {
                    "total": 50,
                    "utilization_range": [50, 95],
                    "failure_probability": 0.1
                },
                "storage": {
                    "total": 50,
                    "utilization_range": [40, 90],
                    "failure_probability": 0.1
                },
                "network": {
                    "bandwidth": {
                        "total": 50,
                        "utilization_range": [40, 95]
                    },
                    "latency_range": [100, 500],
                    "packet_loss_range": [2, 10]
                }
            }
        }
    
    def start_simulation(self, 
                        profile_name: str = "standard", 
                        duration_seconds: int = 300,
                        custom_profile: Optional[Dict[str, Any]] = None,
                        callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Start a resource simulation.
        
        Args:
            profile_name: Name of the resource profile to use
            duration_seconds: Duration of the simulation in seconds
            custom_profile: Optional custom resource profile
            callback: Optional callback function to receive state updates
            
        Returns:
            Dictionary with simulation information
        """
        # Stop any existing simulation
        self.stop_simulation()
        
        # Get profile
        profile = custom_profile
        if not profile:
            if profile_name not in self.resource_profiles:
                logger.warning(f"Profile {profile_name} not found, using standard")
                profile_name = "standard"
            
            profile = self.resource_profiles[profile_name]
        
        # Initialize simulation
        self.current_simulation = {
            "id": f"sim-{int(time.time())}",
            "profile_name": profile_name if not custom_profile else "custom",
            "profile": profile,
            "start_time": time.time(),
            "end_time": time.time() + duration_seconds,
            "duration_seconds": duration_seconds,
            "status": "running",
            "callback": callback
        }
        
        # Initialize resource state
        self._initialize_resource_state(profile)
        
        # Start simulation thread
        self.simulation_stop_event.clear()
        self.simulation_thread = threading.Thread(
            target=self._run_simulation,
            args=(self.current_simulation, self.simulation_stop_event)
        )
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        logger.info(f"Started resource simulation {self.current_simulation['id']} with profile {profile_name}")
        
        return {
            "simulation_id": self.current_simulation["id"],
            "profile_name": profile_name if not custom_profile else "custom",
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
        
        logger.info(f"Stopping resource simulation {self.current_simulation['id']}")
        
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
    
    def get_resource_state(self) -> Dict[str, Any]:
        """
        Get the current resource state.
        
        Returns:
            Dictionary containing current resource state
        """
        return self.resource_state.copy()
    
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
            "profile_name": self.current_simulation["profile_name"],
            "start_time": self.current_simulation["start_time"],
            "end_time": self.current_simulation["end_time"],
            "duration_seconds": self.current_simulation["duration_seconds"],
            "elapsed_seconds": time.time() - self.current_simulation["start_time"],
            "remaining_seconds": max(0, self.current_simulation["end_time"] - time.time()),
            "status": self.current_simulation["status"]
        }
    
    def _initialize_resource_state(self, profile: Dict[str, Any]):
        """
        Initialize resource state based on profile.
        
        Args:
            profile: Resource profile
        """
        # Initialize CPU
        cpu_profile = profile.get("cpu", {})
        self.resource_state["cpu"] = {
            "total": cpu_profile.get("total", 100),
            "available": cpu_profile.get("total", 100),
            "utilized": 0
        }
        
        # Initialize memory
        memory_profile = profile.get("memory", {})
        self.resource_state["memory"] = {
            "total": memory_profile.get("total", 100),
            "available": memory_profile.get("total", 100),
            "utilized": 0
        }
        
        # Initialize storage
        storage_profile = profile.get("storage", {})
        self.resource_state["storage"] = {
            "total": storage_profile.get("total", 100),
            "available": storage_profile.get("total", 100),
            "utilized": 0
        }
        
        # Initialize network
        network_profile = profile.get("network", {})
        bandwidth_profile = network_profile.get("bandwidth", {})
        self.resource_state["network"] = {
            "bandwidth": {
                "total": bandwidth_profile.get("total", 100),
                "available": bandwidth_profile.get("total", 100),
                "utilized": 0
            },
            "latency": 0,
            "packet_loss": 0
        }
    
    def _run_simulation(self, simulation: Dict[str, Any], stop_event: threading.Event):
        """
        Run the simulation.
        
        Args:
            simulation: Simulation configuration
            stop_event: Event to signal simulation to stop
        """
        profile = simulation["profile"]
        callback = simulation.get("callback")
        
        # Simulation loop
        while not stop_event.is_set():
            # Check if simulation time is up
            if time.time() >= simulation["end_time"]:
                logger.info(f"Simulation {simulation['id']} completed")
                simulation["status"] = "completed"
                break
            
            # Update resource state
            self._update_resource_state(profile)
            
            # Call callback if provided
            if callback:
                try:
                    callback(self.get_resource_state())
                except Exception as e:
                    logger.error(f"Error in simulation callback: {e}")
            
            # Sleep for a short time
            time.sleep(1)
    
    def _update_resource_state(self, profile: Dict[str, Any]):
        """
        Update resource state based on profile.
        
        Args:
            profile: Resource profile
        """
        # Update CPU
        self._update_cpu_state(profile.get("cpu", {}))
        
        # Update memory
        self._update_memory_state(profile.get("memory", {}))
        
        # Update storage
        self._update_storage_state(profile.get("storage", {}))
        
        # Update network
        self._update_network_state(profile.get("network", {}))
    
    def _update_cpu_state(self, cpu_profile: Dict[str, Any]):
        """
        Update CPU state.
        
        Args:
            cpu_profile: CPU profile
        """
        # Get utilization range
        utilization_range = cpu_profile.get("utilization_range", [0, 0])
        
        # Check for failure
        failure_probability = cpu_profile.get("failure_probability", 0)
        if random.random() < failure_probability:
            # Simulate CPU failure
            self.resource_state["cpu"]["available"] = 0
            self.resource_state["cpu"]["utilized"] = self.resource_state["cpu"]["total"]
            return
        
        # Update utilization
        utilization = random.uniform(utilization_range[0], utilization_range[1])
        utilized = self.resource_state["cpu"]["total"] * (utilization / 100)
        
        self.resource_state["cpu"]["utilized"] = utilized
        self.resource_state["cpu"]["available"] = self.resource_state["cpu"]["total"] - utilized
    
    def _update_memory_state(self, memory_profile: Dict[str, Any]):
        """
        Update memory state.
        
        Args:
            memory_profile: Memory profile
        """
        # Get utilization range
        utilization_range = memory_profile.get("utilization_range", [0, 0])
        
        # Check for failure
        failure_probability = memory_profile.get("failure_probability", 0)
        if random.random() < failure_probability:
            # Simulate memory failure
            self.resource_state["memory"]["available"] = 0
            self.resource_state["memory"]["utilized"] = self.resource_state["memory"]["total"]
            return
        
        # Update utilization
        utilization = random.uniform(utilization_range[0], utilization_range[1])
        utilized = self.resource_state["memory"]["total"] * (utilization / 100)
        
        self.resource_state["memory"]["utilized"] = utilized
        self.resource_state["memory"]["available"] = self.resource_state["memory"]["total"] - utilized
    
    def _update_storage_state(self, storage_profile: Dict[str, Any]):
        """
        Update storage state.
        
        Args:
            storage_profile: Storage profile
        """
        # Get utilization range
        utilization_range = storage_profile.get("utilization_range", [0, 0])
        
        # Check for failure
        failure_probability = storage_profile.get("failure_probability", 0)
        if random.random() < failure_probability:
            # Simulate storage failure
            self.resource_state["storage"]["available"] = 0
            self.resource_state["storage"]["utilized"] = self.resource_state["storage"]["total"]
            return
        
        # Update utilization
        utilization = random.uniform(utilization_range[0], utilization_range[1])
        utilized = self.resource_state["storage"]["total"] * (utilization / 100)
        
        self.resource_state["storage"]["utilized"] = utilized
        self.resource_state["storage"]["available"] = self.resource_state["storage"]["total"] - utilized
    
    def _update_network_state(self, network_profile: Dict[str, Any]):
        """
        Update network state.
        
        Args:
            network_profile: Network profile
        """
        # Update bandwidth
        bandwidth_profile = network_profile.get("bandwidth", {})
        utilization_range = bandwidth_profile.get("utilization_range", [0, 0])
        
        utilization = random.uniform(utilization_range[0], utilization_range[1])
        utilized = self.resource_state["network"]["bandwidth"]["total"] * (utilization / 100)
        
        self.resource_state["network"]["bandwidth"]["utilized"] = utilized
        self.resource_state["network"]["bandwidth"]["available"] = self.resource_state["network"]["bandwidth"]["total"] - utilized
        
        # Update latency
        latency_range = network_profile.get("latency_range", [0, 0])
        self.resource_state["network"]["latency"] = random.uniform(latency_range[0], latency_range[1])
        
        # Update packet loss
        packet_loss_range = network_profile.get("packet_loss_range", [0, 0])
        self.resource_state["network"]["packet_loss"] = random.uniform(packet_loss_range[0], packet_loss_range[1])
    
    def create_resource_profile(self, 
                               name: str,
                               description: str,
                               cpu_total: int,
                               cpu_utilization_range: List[float],
                               cpu_failure_probability: float,
                               memory_total: int,
                               memory_utilization_range: List[float],
                               memory_failure_probability: float,
                               storage_total: int,
                               storage_utilization_range: List[float],
                               storage_failure_probability: float,
                               bandwidth_total: int,
                               bandwidth_utilization_range: List[float],
                               latency_range: List[float],
                               packet_loss_range: List[float]) -> Dict[str, Any]:
        """
        Create a custom resource profile.
        
        Args:
            name: Profile name
            description: Profile description
            cpu_total: Total CPU resources
            cpu_utilization_range: CPU utilization range [min, max]
            cpu_failure_probability: CPU failure probability
            memory_total: Total memory resources
            memory_utilization_range: Memory utilization range [min, max]
            memory_failure_probability: Memory failure probability
            storage_total: Total storage resources
            storage_utilization_range: Storage utilization range [min, max]
            storage_failure_probability: Storage failure probability
            bandwidth_total: Total bandwidth resources
            bandwidth_utilization_range: Bandwidth utilization range [min, max]
            latency_range: Latency range [min, max]
            packet_loss_range: Packet loss range [min, max]
            
        Returns:
            Created profile
        """
        profile = {
            "description": description,
            "cpu": {
                "total": cpu_total,
                "utilization_range": cpu_utilization_range,
                "failure_probability": cpu_failure_probability
            },
            "memory": {
                "total": memory_total,
                "utilization_range": memory_utilization_range,
                "failure_probability": memory_failure_probability
            },
            "storage": {
                "total": storage_total,
                "utilization_range": storage_utilization_range,
                "failure_probability": storage_failure_probability
            },
            "network": {
                "bandwidth": {
                    "total": bandwidth_total,
                    "utilization_range": bandwidth_utilization_range
                },
                "latency_range": latency_range,
                "packet_loss_range": packet_loss_range
            }
        }
        
        # Add to profiles
        self.resource_profiles[name] = profile
        
        logger.info(f"Created resource profile: {name}")
        
        return profile
    
    def get_resource_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a resource profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Resource profile or None if not found
        """
        return self.resource_profiles.get(name)
    
    def list_resource_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available resource profiles.
        
        Returns:
            Dictionary of profile names to profiles
        """
        return self.resource_profiles
    
    def delete_resource_profile(self, name: str) -> bool:
        """
        Delete a resource profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if deleted, False if not found
        """
        if name not in self.resource_profiles:
            return False
        
        # Don't delete default profiles
        if name in ["high_availability", "standard", "constrained", "edge"]:
            logger.warning(f"Cannot delete default profile: {name}")
            return False
        
        del self.resource_profiles[name]
        logger.info(f"Deleted resource profile: {name}")
        
        return True
