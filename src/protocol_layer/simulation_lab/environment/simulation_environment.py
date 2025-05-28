"""
Protocol Simulation Environment

This module provides a simulated environment for testing and validating
protocol components and interactions within the Industriverse Protocol Layer.
"""

import asyncio
import random
import time
import logging
from typing import Dict, List, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\')
logger = logging.getLogger("simulation_environment")

class SimulatedNetwork:
    """
    Simulates network conditions like latency, packet loss, and bandwidth limitations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the simulated network."""
        self.config = config or {
            "base_latency": 0.01,  # seconds
            "latency_variance": 0.005,
            "packet_loss_rate": 0.01,  # 1%
            "bandwidth_limit": 100 * 1024 * 1024  # 100 Mbps
        }
        logger.info("Initializing Simulated Network")
    
    async def simulate_transmission(self, message_size: int) -> bool:
        """
        Simulate the transmission of a message over the network.
        
        Args:
            message_size: Size of the message in bytes
            
        Returns:
            bool: True if transmission is successful, False if packet is lost
        """
        # Simulate latency
        latency = self.config["base_latency"] + random.uniform(-self.config["latency_variance"], self.config["latency_variance"])
        await asyncio.sleep(max(0, latency))
        
        # Simulate bandwidth limitation (simple delay based on size)
        bandwidth = self.config["bandwidth_limit"]
        if bandwidth > 0:
            transmission_time = message_size / bandwidth
            await asyncio.sleep(transmission_time)
        
        # Simulate packet loss
        if random.random() < self.config["packet_loss_rate"]:
            logger.warning("Simulated packet loss")
            return False
            
        return True

class SimulatedDevice:
    """
    Represents a simulated device in the environment.
    """
    
    def __init__(self, device_id: str, device_type: str, config: Dict[str, Any] = None):
        """Initialize a simulated device."""
        self.device_id = device_id
        self.device_type = device_type
        self.config = config or {
            "processing_power": 1.0,  # Relative processing power
            "memory_limit": 1024 * 1024 * 1024,  # 1 GB
            "failure_rate": 0.001  # Probability of failure per operation
        }
        self.state = "running"
        self.message_queue = asyncio.Queue()
        self.network = SimulatedNetwork()
        logger.info(f"Initializing Simulated Device: {device_id} ({device_type})")
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Simulate processing a message.
        
        Args:
            message: The message to process
            
        Returns:
            Optional[Dict[str, Any]]: Response message or None if processing fails
        """
        if self.state != "running":
            logger.warning(f"Device {self.device_id} is not running, cannot process message")
            return None
            
        # Simulate processing time based on device power
        processing_time = random.uniform(0.01, 0.1) / self.config["processing_power"]
        await asyncio.sleep(processing_time)
        
        # Simulate potential failure
        if random.random() < self.config["failure_rate"]:
            self.state = "failed"
            logger.error(f"Simulated failure for device {self.device_id}")
            return None
            
        # Simulate response generation
        response = {
            "response_to": message.get("id"),
            "sender": self.device_id,
            "payload": f"Processed payload from {message.get(\'sender\', \'unknown\')}",
            "timestamp": time.time()
        }
        
        return response
    
    async def send_message(self, target_device: \'SimulatedDevice\', message: Dict[str, Any]) -> bool:
        """
        Simulate sending a message to another device.
        
        Args:
            target_device: The target device
            message: The message to send
            
        Returns:
            bool: True if message is successfully sent (not lost)
        """
        message_size = len(json.dumps(message).encode(\'utf-8\'))
        
        if await self.network.simulate_transmission(message_size):
            await target_device.receive_message(message)
            return True
        else:
            return False
            
    async def receive_message(self, message: Dict[str, Any]):
        """Receive a message and put it in the queue."""
        await self.message_queue.put(message)
        logger.debug(f"Device {self.device_id} received message: {message.get(\'id\', \'N/A\')}")
    
    async def run(self):
        """Main loop for the simulated device."""
        logger.info(f"Device {self.device_id} starting run loop")
        while self.state == "running":
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                response = await self.process_message(message)
                
                if response:
                    # In a real simulation, we would need a way to route responses
                    # For now, just log the response
                    logger.debug(f"Device {self.device_id} generated response: {response}")
                    
                self.message_queue.task_done()
            except asyncio.TimeoutError:
                # No message received, continue loop
                pass
            except Exception as e:
                logger.error(f"Error in device {self.device_id} run loop: {e}")
                self.state = "failed"
        
        logger.info(f"Device {self.device_id} stopping run loop (state: {self.state})")

class SimulationEnvironment:
    """
    Manages the overall simulation environment, including devices and network.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the simulation environment."""
        self.config = config or {
            "duration": 60,  # seconds
            "num_devices": 10
        }
        self.devices: Dict[str, SimulatedDevice] = {}
        self.network = SimulatedNetwork()
        self.simulation_time = 0
        self.running = False
        logger.info("Initializing Simulation Environment")
    
    def add_device(self, device_id: str, device_type: str, config: Dict[str, Any] = None):
        """Add a simulated device to the environment."""
        if device_id in self.devices:
            logger.warning(f"Device {device_id} already exists")
            return
            
        device = SimulatedDevice(device_id, device_type, config)
        device.network = self.network  # Share the same network instance
        self.devices[device_id] = device
        logger.info(f"Added device {device_id} to environment")
    
    async def run_simulation(self, duration: int = None):
        """
        Run the simulation for a specified duration.
        
        Args:
            duration: Duration of the simulation in seconds
        """
        sim_duration = duration or self.config["duration"]
        logger.info(f"Starting simulation for {sim_duration} seconds")
        self.running = True
        start_time = time.time()
        
        # Start device run loops
        device_tasks = [asyncio.create_task(device.run()) for device in self.devices.values()]
        
        # Main simulation loop
        while self.running and (time.time() - start_time) < sim_duration:
            self.simulation_time = time.time() - start_time
            
            # Simulate some interactions between devices
            if self.devices:
                sender = random.choice(list(self.devices.values()))
                receiver = random.choice(list(self.devices.values()))
                
                if sender != receiver and sender.state == "running":
                    message = {
                        "id": f"msg_{int(time.time())}_{random.randint(1000, 9999)}",
                        "sender": sender.device_id,
                        "payload": f"Simulation message at {self.simulation_time:.2f}s",
                        "timestamp": time.time()
                    }
                    await sender.send_message(receiver, message)
            
            # Wait for a short interval
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # Check if all devices have failed
            if all(d.state == "failed" for d in self.devices.values()):
                logger.warning("All devices failed, stopping simulation")
                break
        
        # Stop simulation
        self.running = False
        logger.info("Simulation finished")
        
        # Stop device tasks
        for device in self.devices.values():
            device.state = "stopped"
            
        await asyncio.gather(*device_tasks, return_exceptions=True)
        logger.info("All device tasks stopped")
    
    def get_environment_state(self) -> Dict[str, Any]:
        """
        Get the current state of the simulation environment.
        
        Returns:
            Dict[str, Any]: Current state information
        """
        return {
            "simulation_time": self.simulation_time,
            "num_devices": len(self.devices),
            "device_states": {did: dev.state for did, dev in self.devices.items()},
            "network_config": self.network.config,
            "running": self.running
        }

# Example usage (can be run separately)
async def main():
    env = SimulationEnvironment({"duration": 10, "num_devices": 5})
    
    # Add devices
    for i in range(env.config["num_devices"]):
        env.add_device(f"device_{i}", "generic_sensor")
    
    # Run simulation
    await env.run_simulation()
    
    # Get final state
    final_state = env.get_environment_state()
    logger.info(f"Final simulation state: {final_state}")

if __name__ == "__main__":
    asyncio.run(main())

