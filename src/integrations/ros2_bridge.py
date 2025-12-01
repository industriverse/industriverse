import sys
import time
import json

# Try to import ROS2 python client library
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from std_msgs.msg import String
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    # Mock Classes for environments without ROS2
    class Node:
        def __init__(self, name): self.name = name
        def create_publisher(self, msg_type, topic, qos): return MockPublisher(topic)
        def get_logger(self): return MockLogger()
    class MockPublisher:
        def __init__(self, topic): self.topic = topic
        def publish(self, msg): print(f"[ROS2 Mock] Publishing to {self.topic}: {msg}")
    class MockLogger:
        def info(self, msg): print(f"[ROS2 Log] {msg}")
    class Twist:
        def __init__(self): self.linear = MockVector3(); self.angular = MockVector3()
        def __str__(self): return f"Twist(linear={self.linear}, angular={self.angular})"
    class MockVector3:
        def __init__(self): self.x=0.0; self.y=0.0; self.z=0.0
        def __str__(self): return f"[{self.x}, {self.y}, {self.z}]"
    class String:
        def __init__(self): self.data = ""
        def __str__(self): return self.data

class TelekinesisBridge(Node):
    """
    The Physical Interface.
    Bridges 'Dark Factory' logic to ROS2-compatible robots.
    """
    def __init__(self):
        if ROS_AVAILABLE:
            rclpy.init()
        super().__init__('telekinesis_bridge')
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/factory/status', 10)
        
        self.get_logger().info("🔮 Telekinesis Bridge Initialized. Ready to move matter.")

    def publish_correction(self, correction_vector):
        """
        Translates a DriftCanceller vector into robot movement.
        """
        msg = Twist()
        # Map correction X/Y to linear velocity
        msg.linear.x = correction_vector[0] * 0.1 # Scale factor
        msg.linear.y = correction_vector[1] * 0.1
        msg.angular.z = correction_vector[2] * 0.05 # Rotation
        
        self.cmd_vel_pub.publish(msg)
        self.get_logger().info(f"Sent Correction Command: {msg}")

    def publish_status(self, status_dict):
        """
        Publishes factory status as a JSON string.
        """
        msg = String()
        msg.data = json.dumps(status_dict)
        self.status_pub.publish(msg)

    def shutdown(self):
        if ROS_AVAILABLE:
            rclpy.shutdown()

if __name__ == "__main__":
    bridge = TelekinesisBridge()
    
    # Simulate a Drift Correction
    print("\n--- Simulating Drift Correction Event ---")
    correction = [0.5, -0.2, 0.1]
    bridge.publish_correction(correction)
    
    # Simulate Status Update
    print("\n--- Simulating Status Update ---")
    bridge.publish_status({"system": "Aletheia", "status": "NOMINAL"})
    
    bridge.shutdown()
