# Industriverse Protocol Layer Integration Guide

## Overview

The Industriverse Protocol Layer serves as the communication backbone and orchestration layer for the entire Industrial Foundry Framework. This guide outlines how to integrate with the Protocol Layer from other layers and external systems.

## Protocol Layer Architecture

The Protocol Layer consists of several key components:

1. **Protocol Kernel Intelligence (PKI)** - Provides intent-aware routing and semantic compression
2. **Self-Healing Protocol Fabric** - Ensures resilient communication with dynamic path morphing
3. **Digital Twin Swarm Language (DTSL)** - Enables declarative configuration of industrial systems
4. **Cross-Mesh Federation** - Facilitates secure communication between independent protocol meshes
5. **Protocol-Driven Genetic Algorithm Layer (PK-Alpha)** - Enables algorithm evolution and optimization
6. **Enhanced UDEP** - Provides optimized communication for mobile/edge devices
7. **Dynamic Protocol AppStore** - Manages protocol-native applications

## Integration Points

### For Other Industriverse Layers

#### Data Layer Integration

```python
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory, MessagePriority

class DataLayerAdapter(ProtocolComponent):
    def __init__(self, component_id=None):
        super().__init__(component_id or str(uuid.uuid4()), "data_layer_adapter")
        self.add_capability("data_access", "Access to industrial data sources")
        
    async def query_data(self, data_source, query_params):
        # Create a query message for the Protocol Layer
        query_msg = MessageFactory.create_query(
            "data_query",
            params={
                "data_source": data_source,
                "query": query_params
            },
            priority=MessagePriority.HIGH
        )
        
        # Send the query through the Protocol Layer
        response = await self.send_message(query_msg)
        return response
```

#### Core AI Layer Integration

```python
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory

class CoreAIAdapter(ProtocolComponent):
    def __init__(self, component_id=None):
        super().__init__(component_id or str(uuid.uuid4()), "core_ai_adapter")
        self.add_capability("model_inference", "Access to AI models")
        
    async def run_inference(self, model_id, input_data):
        # Create a command message for the Protocol Layer
        cmd_msg = MessageFactory.create_command(
            "run_inference",
            params={
                "model_id": model_id,
                "input_data": input_data
            }
        )
        
        # Send the command through the Protocol Layer
        response = await self.send_message(cmd_msg)
        return response
```

#### Generative Layer Integration

```python
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory

class GenerativeLayerAdapter(ProtocolComponent):
    def __init__(self, component_id=None):
        super().__init__(component_id or str(uuid.uuid4()), "generative_layer_adapter")
        self.add_capability("content_generation", "Generate content")
        
    async def generate_content(self, content_type, parameters):
        # Create a command message for the Protocol Layer
        cmd_msg = MessageFactory.create_command(
            "generate_content",
            params={
                "content_type": content_type,
                "parameters": parameters
            }
        )
        
        # Send the command through the Protocol Layer
        response = await self.send_message(cmd_msg)
        return response
```

#### Application Layer Integration

```python
from protocols.protocol_base import ProtocolComponent
from protocols.message_formats import MessageFactory

class ApplicationLayerAdapter(ProtocolComponent):
    def __init__(self, component_id=None):
        super().__init__(component_id or str(uuid.uuid4()), "application_layer_adapter")
        self.add_capability("user_interface", "User interface integration")
        
    async def update_ui(self, ui_component, state):
        # Create an event message for the Protocol Layer
        event_msg = MessageFactory.create_event(
            "ui_update",
            payload={
                "component": ui_component,
                "state": state
            }
        )
        
        # Send the event through the Protocol Layer
        await self.publish_event(event_msg)
```

### For External Systems

#### REST API Integration

The Protocol Layer exposes a REST API for external systems:

```bash
# Example: Query the Protocol Layer
curl -X POST https://industriverse-protocol-udep.example.com:8443/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "get_device_status",
    "params": {
      "device_id": "device-123"
    }
  }'
```

#### gRPC Integration

The Protocol Layer also provides gRPC endpoints:

```python
import grpc
from industriverse.protocol.api import protocol_pb2, protocol_pb2_grpc

# Create a gRPC channel
channel = grpc.secure_channel('industriverse-protocol-udep.example.com:9095', grpc.ssl_channel_credentials())

# Create a stub
stub = protocol_pb2_grpc.ProtocolServiceStub(channel)

# Create a request
request = protocol_pb2.QueryRequest(
    query="get_device_status",
    params={"device_id": "device-123"}
)

# Send the request
response = stub.Query(request)
```

#### WebSocket Integration

For real-time updates, the Protocol Layer provides WebSocket endpoints:

```javascript
// Create a WebSocket connection
const socket = new WebSocket('wss://industriverse-protocol-udep.example.com:8443/ws');

// Connection opened
socket.addEventListener('open', (event) => {
    socket.send(JSON.stringify({
        type: 'subscribe',
        topic: 'device.status',
        filter: {
            device_id: 'device-123'
        }
    }));
});

// Listen for messages
socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    console.log('Message from server:', message);
});
```

## Using Protocol Layer Features

### Intent-Aware Routing

```python
from protocols.kernel.intent_aware_router import IntentAwareRouter

# Create an intent-aware router
router = IntentAwareRouter()

# Route a message based on intent
result = await router.route_message(
    message,
    intent="predictive_maintenance",
    context={
        "industry": "manufacturing",
        "device_type": "cnc_machine"
    }
)
```

### Semantic Compression

```python
from protocols.kernel.semantic_compressor import SemanticCompressor

# Create a semantic compressor
compressor = SemanticCompressor()

# Compress a message
compressed_message = await compressor.compress(
    message,
    compression_level="high",
    preserve_fields=["id", "timestamp", "priority"]
)

# Decompress a message
original_message = await compressor.decompress(compressed_message)
```

### Digital Twin Swarm Language

```python
from protocols.dtsl.dtsl_handler import DTSLHandler

# Create a DTSL handler
dtsl_handler = DTSLHandler()

# Parse a DTSL script
parsed_script = await dtsl_handler.parse_script(dtsl_script)

# Execute a DTSL script
result = await dtsl_handler.execute_script(
    parsed_script,
    context={
        "factory_id": "factory-123",
        "line_id": "line-456"
    }
)
```

### Agent Reflex Timers

```python
from protocols.reflex.agent_reflex_timers import AgentReflexTimers, EscalationLevel

# Create a reflex timer service
art = AgentReflexTimers()

# Create a timer for an operation
timer = await art.create_timer(
    operation_id="maintenance-task-123",
    operation_type="predictive_maintenance",
    timeout_ms=60000,  # 60 seconds
    escalation_level=EscalationLevel.NOTIFY,
    escalation_target="maintenance-supervisor",
    context={
        "device_id": "device-123",
        "severity": "high"
    }
)

# Complete a timer
await art.complete_timer(timer.timer_id, success=True)
```

### Cross-Mesh Federation

```python
from protocols.federation.cross_mesh_federation import CrossMeshFederation, FederationTrustLevel

# Create a federation service
federation = CrossMeshFederation()

# Initiate federation with another mesh
result = await federation.initiate_federation(
    remote_mesh_id="mesh-456",
    remote_endpoint="https://mesh-456.example.com/federation",
    trust_level=FederationTrustLevel.MEDIUM,
    metadata={
        "industry": "manufacturing",
        "region": "europe"
    }
)

# Send a message to a federated mesh
result = await federation.send_federated_message(
    federation_id=result["federation_id"],
    message={
        "message_type": "device_status_update",
        "device_id": "device-123",
        "status": "online"
    }
)
```

### Enhanced UDEP

```python
from mobile.udep.enhanced_udep_handler import EnhancedUDEPHandler, DeviceCapabilityLevel, ConnectionType

# Create an Enhanced UDEP handler
udep = EnhancedUDEPHandler()

# Register a device
profile = await udep.register_device(
    device_id="mobile-123",
    capability_level=DeviceCapabilityLevel.MEDIUM,
    connection_type=ConnectionType.CELLULAR,
    max_message_size=262144,  # 256KB
    supports_compression=True,
    supports_encryption=True,
    battery_constrained=True
)

# Send a message to a device
result = await udep.send_message_to_device(
    device_id="mobile-123",
    message={
        "message_type": "alert",
        "alert_id": "alert-123",
        "severity": "high",
        "description": "Temperature exceeding threshold"
    },
    optimize=True
)

# Transfer an agent to another device
transfer = await udep.initiate_agent_transfer(
    agent_id="agent-123",
    source_device_id="server-456",
    target_device_id="mobile-123",
    agent_state={
        "knowledge": {...},
        "context": {...},
        "tasks": [...]
    }
)
```

## Security Considerations

- Always use secure connections (TLS) when communicating with the Protocol Layer
- Implement proper authentication and authorization
- Follow the principle of least privilege when requesting access
- Validate all inputs and outputs
- Handle sensitive data according to your organization's security policies

## Performance Optimization

- Use semantic compression for large messages
- Implement batching for multiple small messages
- Use appropriate message priorities
- Consider using the Enhanced UDEP handler for mobile/edge devices
- Monitor and optimize resource usage

## Troubleshooting

Common issues and solutions:

1. **Connection refused**: Check service endpoints and network connectivity
2. **Authentication failed**: Verify credentials and token validity
3. **Message timeout**: Check for network issues or service overload
4. **Invalid message format**: Validate message structure against the schema

## Support

For support, contact the Industriverse team at support@industriverse.io or open an issue in the repository.
