"""
Semantic Compressor for Industriverse Protocol Layer

This module implements the Semantic Compressor component of the Protocol Kernel Intelligence,
enabling efficient compression of protocol messages based on semantic understanding.

Features:
1. Semantic analysis of message content
2. Context-aware compression strategies
3. Adaptive compression based on network conditions
4. Integration with BitNet/EKIS for optimized compression
5. Compression strategy selection based on message type and priority
"""

import uuid
import time
import asyncio
import logging
import json
import zlib
import base64
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompressionStrategy(Enum):
    """Compression strategies for different message types and contexts."""
    NONE = "none"  # No compression
    LOSSLESS = "lossless"  # Standard lossless compression
    SEMANTIC = "semantic"  # Semantic-aware compression
    DIFFERENTIAL = "differential"  # Differential compression based on previous messages
    ADAPTIVE = "adaptive"  # Adaptive compression based on network conditions
    EXTREME = "extreme"  # Maximum compression with potential information loss
    CUSTOM = "custom"  # Custom compression strategy


@dataclass
class CompressionResult:
    """
    Represents the result of a compression operation.
    """
    message_id: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    strategy: CompressionStrategy
    compression_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "compression_ratio": self.compression_ratio,
            "strategy": self.strategy.value,
            "compression_time": self.compression_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompressionResult':
        """Create from dictionary representation."""
        return cls(
            message_id=data["message_id"],
            original_size=data["original_size"],
            compressed_size=data["compressed_size"],
            compression_ratio=data["compression_ratio"],
            strategy=CompressionStrategy(data["strategy"]),
            compression_time=data["compression_time"],
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", time.time())
        )


class SemanticCompressor(ProtocolService):
    """
    Service for semantic compression of protocol messages.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "semantic_compressor")
        self.config = config or {}
        
        # Initialize storage
        self.compression_results: Dict[str, CompressionResult] = {}
        self.compression_history: List[Dict[str, Any]] = []
        
        # Message cache for differential compression
        self.message_cache: Dict[str, Dict[str, Any]] = {}
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.SemanticCompressor.{self.component_id[:8]}")
        self.logger.info(f"Semantic Compressor initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("semantic_compression", "Compress messages based on semantic understanding")
        self.add_capability("adaptive_compression", "Adapt compression based on network conditions")
        self.add_capability("differential_compression", "Compress based on differences from previous messages")
        self.add_capability("compression_strategy_selection", "Select optimal compression strategy")

    async def initialize(self) -> bool:
        """Initialize the compressor service."""
        self.logger.info("Initializing Semantic Compressor")
        
        # Initialize any required resources
        # In a real implementation, this might load ML models, etc.
        
        self.logger.info("Semantic Compressor initialized successfully")
        return True

    # --- Compression Strategy Selection ---

    async def select_compression_strategy(self, message: Dict[str, Any], context: Dict[str, Any] = None) -> CompressionStrategy:
        """Select the optimal compression strategy for a message."""
        context = context or {}
        
        # Parse message
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            self.logger.error("Invalid message for compression strategy selection")
            return CompressionStrategy.LOSSLESS  # Default to lossless for unknown messages
        
        # Extract message properties
        message_type = type(msg_obj).__name__
        priority = getattr(msg_obj, "priority", MessagePriority.NORMAL)
        security_level = getattr(msg_obj, "security_level", SecurityLevel.NORMAL)
        
        # Get network conditions from context
        bandwidth = context.get("bandwidth", "high")  # high, medium, low
        latency = context.get("latency", "low")  # low, medium, high
        
        # Select strategy based on message type, priority, and network conditions
        if priority == MessagePriority.CRITICAL:
            # Critical messages use minimal compression to ensure delivery
            return CompressionStrategy.LOSSLESS
        
        if message_type == "CommandMessage":
            # Commands need to be precise
            return CompressionStrategy.LOSSLESS
        
        if message_type == "QueryMessage":
            # Queries can use semantic compression
            return CompressionStrategy.SEMANTIC
        
        if message_type == "EventMessage":
            # Events can use differential compression if similar events exist
            event_type = getattr(msg_obj, "event_type", "")
            if self._has_similar_cached_message(message, event_type):
                return CompressionStrategy.DIFFERENTIAL
            else:
                return CompressionStrategy.SEMANTIC
        
        if message_type == "ResponseMessage":
            # Responses can use adaptive compression based on network conditions
            if bandwidth == "low" or latency == "high":
                return CompressionStrategy.EXTREME
            elif bandwidth == "medium" or latency == "medium":
                return CompressionStrategy.ADAPTIVE
            else:
                return CompressionStrategy.SEMANTIC
        
        # Default to lossless compression
        return CompressionStrategy.LOSSLESS

    def _has_similar_cached_message(self, message: Dict[str, Any], key: str) -> bool:
        """Check if there's a similar message in the cache."""
        return key in self.message_cache

    # --- Compression Operations ---

    async def compress_message(self, message: Dict[str, Any], strategy: Optional[CompressionStrategy] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compress a message using the specified or automatically selected strategy."""
        context = context or {}
        
        # Get message ID
        message_id = message.get("message_id", str(uuid.uuid4()))
        
        # Select strategy if not provided
        if not strategy:
            strategy = await self.select_compression_strategy(message, context)
        
        # Measure original size
        original_json = json.dumps(message)
        original_size = len(original_json.encode('utf-8'))
        
        # Start timing
        start_time = time.time()
        
        # Apply compression based on strategy
        compressed_message = None
        metadata = {}
        
        if strategy == CompressionStrategy.NONE:
            # No compression
            compressed_message = message
            metadata["note"] = "No compression applied"
        
        elif strategy == CompressionStrategy.LOSSLESS:
            # Standard lossless compression
            compressed_data = zlib.compress(original_json.encode('utf-8'))
            compressed_message = {
                "message_id": message_id,
                "compression": {
                    "strategy": strategy.value,
                    "algorithm": "zlib",
                    "original_size": original_size
                },
                "data": base64.b64encode(compressed_data).decode('utf-8')
            }
            metadata["algorithm"] = "zlib"
        
        elif strategy == CompressionStrategy.SEMANTIC:
            # Semantic compression (simplified simulation)
            # In a real implementation, this would use ML models for semantic understanding
            compressed_message = self._apply_semantic_compression(message)
            metadata["semantic_features"] = ["intent", "entities", "context"]
        
        elif strategy == CompressionStrategy.DIFFERENTIAL:
            # Differential compression based on previous messages
            msg_obj = MessageFactory.create_from_dict(message)
            if msg_obj and hasattr(msg_obj, "event_type"):
                event_type = msg_obj.event_type
                if event_type in self.message_cache:
                    base_message = self.message_cache[event_type]
                    compressed_message = self._apply_differential_compression(message, base_message)
                    metadata["base_message_id"] = base_message.get("message_id")
                else:
                    # Fallback to lossless if no base message
                    compressed_data = zlib.compress(original_json.encode('utf-8'))
                    compressed_message = {
                        "message_id": message_id,
                        "compression": {
                            "strategy": CompressionStrategy.LOSSLESS.value,
                            "algorithm": "zlib",
                            "original_size": original_size
                        },
                        "data": base64.b64encode(compressed_data).decode('utf-8')
                    }
                    metadata["algorithm"] = "zlib"
                    metadata["note"] = "Fallback to lossless, no base message"
            else:
                # Fallback to lossless if not an event
                compressed_data = zlib.compress(original_json.encode('utf-8'))
                compressed_message = {
                    "message_id": message_id,
                    "compression": {
                        "strategy": CompressionStrategy.LOSSLESS.value,
                        "algorithm": "zlib",
                        "original_size": original_size
                    },
                    "data": base64.b64encode(compressed_data).decode('utf-8')
                }
                metadata["algorithm"] = "zlib"
                metadata["note"] = "Fallback to lossless, not an event"
        
        elif strategy == CompressionStrategy.ADAPTIVE:
            # Adaptive compression based on network conditions
            bandwidth = context.get("bandwidth", "high")
            latency = context.get("latency", "low")
            
            if bandwidth == "low" or latency == "high":
                # Use more aggressive compression
                compressed_message = self._apply_semantic_compression(message, aggressive=True)
                metadata["adaptive_level"] = "aggressive"
            else:
                # Use standard compression
                compressed_message = self._apply_semantic_compression(message, aggressive=False)
                metadata["adaptive_level"] = "standard"
            
            metadata["network_conditions"] = {"bandwidth": bandwidth, "latency": latency}
        
        elif strategy == CompressionStrategy.EXTREME:
            # Extreme compression with potential information loss
            compressed_message = self._apply_extreme_compression(message)
            metadata["warning"] = "Extreme compression may result in information loss"
        
        elif strategy == CompressionStrategy.CUSTOM:
            # Custom compression strategy
            custom_strategy = context.get("custom_strategy", {})
            if "compressor_function" in custom_strategy:
                # This would be a function reference in a real implementation
                # Here we just simulate it
                compressed_message = self._apply_semantic_compression(message)
                metadata["custom_strategy"] = custom_strategy.get("name", "unnamed")
            else:
                # Fallback to lossless
                compressed_data = zlib.compress(original_json.encode('utf-8'))
                compressed_message = {
                    "message_id": message_id,
                    "compression": {
                        "strategy": CompressionStrategy.LOSSLESS.value,
                        "algorithm": "zlib",
                        "original_size": original_size
                    },
                    "data": base64.b64encode(compressed_data).decode('utf-8')
                }
                metadata["algorithm"] = "zlib"
                metadata["note"] = "Fallback to lossless, invalid custom strategy"
        
        # End timing
        compression_time = time.time() - start_time
        
        # Calculate compressed size
        compressed_json = json.dumps(compressed_message)
        compressed_size = len(compressed_json.encode('utf-8'))
        
        # Calculate compression ratio
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        # Create compression result
        result = CompressionResult(
            message_id=message_id,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            strategy=strategy,
            compression_time=compression_time,
            metadata=metadata
        )
        
        # Store the result
        async with self.lock:
            self.compression_results[message_id] = result
            
            # Add to compression history
            self.compression_history.append({
                "message_id": message_id,
                "timestamp": time.time(),
                "strategy": strategy.value,
                "compression_ratio": compression_ratio,
                "compression_time": compression_time
            })
            
            # Keep history limited
            max_history = self.config.get("max_compression_history", 1000)
            if len(self.compression_history) > max_history:
                self.compression_history = self.compression_history[-max_history:]
            
            # Update message cache for differential compression
            msg_obj = MessageFactory.create_from_dict(message)
            if msg_obj and hasattr(msg_obj, "event_type"):
                event_type = msg_obj.event_type
                self.message_cache[event_type] = message
        
        self.logger.debug(f"Compressed message {message_id} using {strategy.value} strategy, ratio: {compression_ratio:.2f}")
        return compressed_message

    async def decompress_message(self, compressed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress a message that was compressed using any strategy."""
        # Check if this is actually a compressed message
        if "compression" not in compressed_message:
            # Not compressed, return as is
            return compressed_message
        
        # Extract compression info
        compression_info = compressed_message.get("compression", {})
        strategy = CompressionStrategy(compression_info.get("strategy", "lossless"))
        
        # Decompress based on strategy
        if strategy == CompressionStrategy.LOSSLESS:
            # Standard lossless decompression
            compressed_data = base64.b64decode(compressed_message["data"])
            decompressed_data = zlib.decompress(compressed_data)
            return json.loads(decompressed_data.decode('utf-8'))
        
        elif strategy == CompressionStrategy.SEMANTIC:
            # Semantic decompression
            return self._apply_semantic_decompression(compressed_message)
        
        elif strategy == CompressionStrategy.DIFFERENTIAL:
            # Differential decompression
            base_message_id = compressed_message.get("base_message_id")
            if base_message_id and base_message_id in self.compression_results:
                # Get the base message
                base_message = self.message_cache.get(base_message_id)
                if base_message:
                    return self._apply_differential_decompression(compressed_message, base_message)
            
            # Fallback if base message not found
            self.logger.warning(f"Base message not found for differential decompression, using direct data")
            if "data" in compressed_message:
                compressed_data = base64.b64decode(compressed_message["data"])
                decompressed_data = zlib.decompress(compressed_data)
                return json.loads(decompressed_data.decode('utf-8'))
            else:
                self.logger.error("Cannot decompress message, no data field")
                return compressed_message
        
        elif strategy == CompressionStrategy.ADAPTIVE or strategy == CompressionStrategy.EXTREME:
            # These strategies use semantic compression internally
            return self._apply_semantic_decompression(compressed_message)
        
        elif strategy == CompressionStrategy.CUSTOM:
            # Custom decompression strategy
            if "custom_decompressor" in compressed_message:
                # This would be a function reference in a real implementation
                # Here we just simulate it
                return self._apply_semantic_decompression(compressed_message)
            else:
                # Fallback to direct data
                if "data" in compressed_message:
                    compressed_data = base64.b64decode(compressed_message["data"])
                    decompressed_data = zlib.decompress(compressed_data)
                    return json.loads(decompressed_data.decode('utf-8'))
                else:
                    self.logger.error("Cannot decompress message, no data field")
                    return compressed_message
        
        else:  # CompressionStrategy.NONE
            # Not compressed, return original data if available
            if "original_data" in compressed_message:
                return compressed_message["original_data"]
            else:
                return compressed_message

    async def get_compression_result(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get the compression result for a message."""
        async with self.lock:
            if message_id not in self.compression_results:
                self.logger.error(f"Compression result for message {message_id} not found")
                return None
            
            return self.compression_results[message_id].to_dict()

    # --- Compression Implementation Methods ---

    def _apply_semantic_compression(self, message: Dict[str, Any], aggressive: bool = False) -> Dict[str, Any]:
        """Apply semantic compression to a message."""
        # In a real implementation, this would use ML models for semantic understanding
        # Here we simulate it with a simplified approach
        
        # Get message ID
        message_id = message.get("message_id", str(uuid.uuid4()))
        
        # Parse message
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            # Fallback to lossless if parsing fails
            compressed_data = zlib.compress(json.dumps(message).encode('utf-8'))
            return {
                "message_id": message_id,
                "compression": {
                    "strategy": CompressionStrategy.LOSSLESS.value,
                    "algorithm": "zlib",
                    "original_size": len(json.dumps(message).encode('utf-8'))
                },
                "data": base64.b64encode(compressed_data).decode('utf-8')
            }
        
        # Extract essential information based on message type
        compressed_content = {}
        
        if isinstance(msg_obj, CommandMessage):
            compressed_content = {
                "type": "command",
                "command": msg_obj.command,
                "params": self._compress_params(msg_obj.params, aggressive)
            }
        
        elif isinstance(msg_obj, QueryMessage):
            compressed_content = {
                "type": "query",
                "query": msg_obj.query,
                "params": self._compress_params(msg_obj.params, aggressive)
            }
        
        elif isinstance(msg_obj, EventMessage):
            compressed_content = {
                "type": "event",
                "event_type": msg_obj.event_type,
                "payload": self._compress_payload(msg_obj.payload, aggressive)
            }
        
        elif isinstance(msg_obj, ResponseMessage):
            compressed_content = {
                "type": "response",
                "correlation_id": msg_obj.correlation_id,
                "status": msg_obj.status.value,
                "payload": self._compress_payload(msg_obj.payload, aggressive)
            }
        
        else:
            # Unknown message type, use lossless
            compressed_data = zlib.compress(json.dumps(message).encode('utf-8'))
            return {
                "message_id": message_id,
                "compression": {
                    "strategy": CompressionStrategy.LOSSLESS.value,
                    "algorithm": "zlib",
                    "original_size": len(json.dumps(message).encode('utf-8'))
                },
                "data": base64.b64encode(compressed_data).decode('utf-8')
            }
        
        # Add essential metadata
        compressed_content["message_id"] = message_id
        if hasattr(msg_obj, "sender_id"):
            compressed_content["sender_id"] = msg_obj.sender_id
        if hasattr(msg_obj, "receiver_id"):
            compressed_content["receiver_id"] = msg_obj.receiver_id
        if hasattr(msg_obj, "timestamp"):
            compressed_content["timestamp"] = msg_obj.timestamp
        
        # Create compressed message
        return {
            "message_id": message_id,
            "compression": {
                "strategy": CompressionStrategy.SEMANTIC.value,
                "aggressive": aggressive,
                "original_size": len(json.dumps(message).encode('utf-8'))
            },
            "content": compressed_content
        }

    def _compress_params(self, params: Dict[str, Any], aggressive: bool) -> Dict[str, Any]:
        """Compress parameters in a message."""
        if not params:
            return {}
        
        if not aggressive:
            # Standard compression: keep all params
            return params
        else:
            # Aggressive compression: keep only essential params
            essential_params = {}
            for key, value in params.items():
                # Keep only non-null primitive types and short strings
                if value is None:
                    continue
                elif isinstance(value, (bool, int, float)):
                    essential_params[key] = value
                elif isinstance(value, str) and len(value) < 100:
                    essential_params[key] = value
                elif isinstance(value, dict) and len(value) < 5:
                    essential_params[key] = self._compress_params(value, aggressive)
                elif isinstance(value, list) and len(value) < 5:
                    essential_params[key] = value[:3]  # Keep only first 3 items
            return essential_params

    def _compress_payload(self, payload: Dict[str, Any], aggressive: bool) -> Dict[str, Any]:
        """Compress payload in a message."""
        if not payload:
            return {}
        
        if not aggressive:
            # Standard compression: keep all payload
            return payload
        else:
            # Aggressive compression: keep only essential payload
            if isinstance(payload, dict):
                essential_payload = {}
                for key, value in payload.items():
                    # Keep only non-null primitive types and short strings
                    if value is None:
                        continue
                    elif isinstance(value, (bool, int, float)):
                        essential_payload[key] = value
                    elif isinstance(value, str) and len(value) < 100:
                        essential_payload[key] = value
                    elif isinstance(value, dict) and len(value) < 5:
                        essential_payload[key] = self._compress_payload(value, aggressive)
                    elif isinstance(value, list) and len(value) < 5:
                        essential_payload[key] = value[:3]  # Keep only first 3 items
                return essential_payload
            elif isinstance(payload, list):
                return payload[:5]  # Keep only first 5 items
            else:
                return payload

    def _apply_semantic_decompression(self, compressed_message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply semantic decompression to a message."""
        # Extract content
        content = compressed_message.get("content", {})
        if not content:
            self.logger.error("Cannot decompress semantic message, no content field")
            return compressed_message
        
        # Extract message type
        message_type = content.get("type")
        if not message_type:
            self.logger.error("Cannot decompress semantic message, no type field")
            return compressed_message
        
        # Reconstruct message based on type
        if message_type == "command":
            message = {
                "message_id": content.get("message_id"),
                "message_type": "command",
                "command": content.get("command"),
                "params": content.get("params", {})
            }
        
        elif message_type == "query":
            message = {
                "message_id": content.get("message_id"),
                "message_type": "query",
                "query": content.get("query"),
                "params": content.get("params", {})
            }
        
        elif message_type == "event":
            message = {
                "message_id": content.get("message_id"),
                "message_type": "event",
                "event_type": content.get("event_type"),
                "payload": content.get("payload", {})
            }
        
        elif message_type == "response":
            message = {
                "message_id": content.get("message_id"),
                "message_type": "response",
                "correlation_id": content.get("correlation_id"),
                "status": content.get("status"),
                "payload": content.get("payload", {})
            }
        
        else:
            self.logger.error(f"Unknown message type in semantic decompression: {message_type}")
            return compressed_message
        
        # Add metadata
        if "sender_id" in content:
            message["sender_id"] = content["sender_id"]
        if "receiver_id" in content:
            message["receiver_id"] = content["receiver_id"]
        if "timestamp" in content:
            message["timestamp"] = content["timestamp"]
        
        return message

    def _apply_differential_compression(self, message: Dict[str, Any], base_message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential compression to a message based on a base message."""
        # In a real implementation, this would compute and store only the differences
        # Here we simulate it with a simplified approach
        
        # Get message ID
        message_id = message.get("message_id", str(uuid.uuid4()))
        
        # Calculate differences (simplified)
        differences = {}
        
        # For simplicity, we'll just identify changed top-level keys
        for key, value in message.items():
            if key not in base_message or base_message[key] != value:
                differences[key] = value
        
        # Create compressed message
        return {
            "message_id": message_id,
            "compression": {
                "strategy": CompressionStrategy.DIFFERENTIAL.value,
                "base_message_id": base_message.get("message_id"),
                "original_size": len(json.dumps(message).encode('utf-8'))
            },
            "differences": differences
        }

    def _apply_differential_decompression(self, compressed_message: Dict[str, Any], base_message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential decompression to a message based on a base message."""
        # Extract differences
        differences = compressed_message.get("differences", {})
        if not differences:
            self.logger.error("Cannot decompress differential message, no differences field")
            return compressed_message
        
        # Start with the base message
        decompressed_message = base_message.copy()
        
        # Apply differences
        for key, value in differences.items():
            decompressed_message[key] = value
        
        return decompressed_message

    def _apply_extreme_compression(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Apply extreme compression to a message with potential information loss."""
        # In a real implementation, this would use more sophisticated techniques
        # Here we simulate it with a simplified approach that removes non-essential data
        
        # Get message ID
        message_id = message.get("message_id", str(uuid.uuid4()))
        
        # Parse message
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            # Fallback to lossless if parsing fails
            compressed_data = zlib.compress(json.dumps(message).encode('utf-8'))
            return {
                "message_id": message_id,
                "compression": {
                    "strategy": CompressionStrategy.LOSSLESS.value,
                    "algorithm": "zlib",
                    "original_size": len(json.dumps(message).encode('utf-8'))
                },
                "data": base64.b64encode(compressed_data).decode('utf-8')
            }
        
        # Extract only the most essential information
        compressed_content = {
            "message_id": message_id
        }
        
        if isinstance(msg_obj, CommandMessage):
            compressed_content["type"] = "command"
            compressed_content["command"] = msg_obj.command
            # Keep only essential params
            essential_params = {}
            for key, value in msg_obj.params.items():
                if key in ["id", "action", "target"]:
                    essential_params[key] = value
            compressed_content["params"] = essential_params
        
        elif isinstance(msg_obj, QueryMessage):
            compressed_content["type"] = "query"
            compressed_content["query"] = msg_obj.query
            # Keep only essential params
            essential_params = {}
            for key, value in msg_obj.params.items():
                if key in ["id", "filter"]:
                    essential_params[key] = value
            compressed_content["params"] = essential_params
        
        elif isinstance(msg_obj, EventMessage):
            compressed_content["type"] = "event"
            compressed_content["event_type"] = msg_obj.event_type
            # Keep only essential payload
            if isinstance(msg_obj.payload, dict):
                essential_payload = {}
                for key, value in msg_obj.payload.items():
                    if key in ["id", "status", "type"]:
                        essential_payload[key] = value
                compressed_content["payload"] = essential_payload
            else:
                compressed_content["payload"] = {}
        
        elif isinstance(msg_obj, ResponseMessage):
            compressed_content["type"] = "response"
            compressed_content["correlation_id"] = msg_obj.correlation_id
            compressed_content["status"] = msg_obj.status.value
            # Keep only essential payload
            if isinstance(msg_obj.payload, dict):
                essential_payload = {}
                for key, value in msg_obj.payload.items():
                    if key in ["id", "result", "status"]:
                        essential_payload[key] = value
                compressed_content["payload"] = essential_payload
            else:
                compressed_content["payload"] = {}
        
        # Add sender ID if available
        if hasattr(msg_obj, "sender_id"):
            compressed_content["sender_id"] = msg_obj.sender_id
        
        # Create compressed message
        return {
            "message_id": message_id,
            "compression": {
                "strategy": CompressionStrategy.EXTREME.value,
                "original_size": len(json.dumps(message).encode('utf-8')),
                "warning": "Information loss may have occurred"
            },
            "content": compressed_content
        }

    # --- Analytics and Statistics ---

    async def get_compression_statistics(self) -> Dict[str, Any]:
        """Get statistics about compression operations."""
        async with self.lock:
            total_compressions = len(self.compression_history)
            if total_compressions == 0:
                return {
                    "total_compressions": 0,
                    "strategies": {},
                    "avg_compression_ratio": 0,
                    "avg_compression_time": 0
                }
            
            # Count strategies
            strategies = {}
            for entry in self.compression_history:
                strategy = entry["strategy"]
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            # Calculate averages
            avg_ratio = sum(entry["compression_ratio"] for entry in self.compression_history) / total_compressions
            avg_time = sum(entry["compression_time"] for entry in self.compression_history) / total_compressions
            
            # Calculate percentages
            strategies_pct = {k: (v / total_compressions) * 100 for k, v in strategies.items()}
            
            return {
                "total_compressions": total_compressions,
                "strategies": strategies_pct,
                "avg_compression_ratio": avg_ratio,
                "avg_compression_time": avg_time
            }

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "compress_message":
                params = msg_obj.params
                if "message" in params:
                    strategy = None
                    if "strategy" in params:
                        try:
                            strategy = CompressionStrategy(params["strategy"])
                        except ValueError:
                            status = MessageStatus.FAILED
                            response_payload = {"error": f"Invalid compression strategy: {params['strategy']}"}
                            return MessageFactory.create_response(
                                correlation_id=msg_obj.message_id,
                                status=status,
                                payload=response_payload,
                                sender_id=self.component_id,
                                receiver_id=msg_obj.sender_id
                            ).to_dict()
                    
                    compressed_message = await self.compress_message(
                        params["message"],
                        strategy,
                        params.get("context")
                    )
                    response_payload = {
                        "compressed_message": compressed_message,
                        "compression_result": self.compression_results[params["message"].get("message_id", "unknown")].to_dict()
                    }
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message parameter"}
            
            elif msg_obj.command == "decompress_message":
                params = msg_obj.params
                if "compressed_message" in params:
                    decompressed_message = await self.decompress_message(params["compressed_message"])
                    response_payload = {"decompressed_message": decompressed_message}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing compressed_message parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_compression_result":
                params = msg_obj.params
                if "message_id" in params:
                    result = await self.get_compression_result(params["message_id"])
                    if result:
                        response_payload = result
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Compression result not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message_id parameter"}
            
            elif msg_obj.query == "get_compression_statistics":
                stats = await self.get_compression_statistics()
                response_payload = stats
            
            elif msg_obj.query == "select_compression_strategy":
                params = msg_obj.params
                if "message" in params:
                    strategy = await self.select_compression_strategy(params["message"], params.get("context"))
                    response_payload = {"strategy": strategy.value}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing message parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # For other message types, just compress and return
            compressed_message = await self.compress_message(message)
            message_id = message.get("message_id", "unknown")
            
            # Return the compression result
            if message_id in self.compression_results:
                response_payload = {
                    "compressed_message": compressed_message,
                    "compression_result": self.compression_results[message_id].to_dict()
                }
            else:
                response_payload = {"compressed_message": compressed_message}

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_results = len(self.compression_results)
            num_history = len(self.compression_history)
            num_cached = len(self.message_cache)
        
        return {
            "status": "healthy",
            "compression_results": num_results,
            "compression_history": num_history,
            "cached_messages": num_cached
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
