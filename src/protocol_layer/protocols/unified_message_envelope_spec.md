# Unified Message Envelope (UME) Specification

## Overview

The Unified Message Envelope (UME) is a standardized message format for all protocol communications within the Industriverse Protocol Layer. It provides a consistent structure for messages exchanged between components, ensuring context preservation, security, and interoperability across different protocols.

## Specification

### Message Structure

```json
{
  "envelope": {
    "version": "1.0",
    "id": "msg_1234567890abcdef",
    "timestamp": 1621234567890,
    "source": {
      "id": "component_abc123",
      "type": "agent",
      "protocol": "a2a"
    },
    "target": {
      "id": "component_def456",
      "type": "service",
      "protocol": "mcp"
    },
    "context": {
      "conversation_id": "conv_9876543210fedcba",
      "correlation_id": "corr_1a2b3c4d5e6f7g8h",
      "causation_id": "msg_0987654321abcdef",
      "workflow_id": "workflow_123456789",
      "session_id": "session_abcdef123456"
    },
    "security": {
      "signature": "base64_encoded_signature",
      "certificate": "base64_encoded_certificate",
      "encryption": {
        "algorithm": "AES-256-GCM",
        "key_id": "key_12345",
        "iv": "base64_encoded_iv"
      },
      "trust_level": 3,
      "audit_trail": "hash_of_previous_messages"
    },
    "reflex": {
      "timer_id": "timer_12345",
      "timeout": 30000,
      "escalation_path": ["component_ghi789", "component_jkl012"],
      "priority": 2,
      "interrupt_level": 1
    },
    "routing": {
      "path": ["node_1", "node_2", "node_3"],
      "ttl": 10,
      "hops": 2,
      "flags": ["reliable", "ordered"],
      "qos": 2
    },
    "metadata": {
      "protocol_version": "2.0",
      "content_type": "application/json",
      "content_encoding": "utf-8",
      "schema_id": "schema_12345",
      "industry_tags": ["manufacturing", "automotive"],
      "semantic_compression": {
        "algorithm": "intent_based",
        "ratio": 0.75,
        "original_size": 8192
      }
    }
  },
  "payload": {
    // Protocol-specific message content
  }
}
```

### Field Descriptions

#### Envelope

- **version**: Version of the UME specification
- **id**: Unique identifier for the message
- **timestamp**: Unix timestamp in milliseconds when the message was created

#### Source/Target

- **id**: Unique identifier of the source/target component
- **type**: Type of component (agent, service, device, etc.)
- **protocol**: Protocol used by the component (a2a, mcp, etc.)

#### Context

- **conversation_id**: Identifier for a conversation thread
- **correlation_id**: Identifier for correlating related messages
- **causation_id**: Identifier of the message that caused this message
- **workflow_id**: Identifier for a workflow
- **session_id**: Identifier for a session

#### Security

- **signature**: Digital signature of the message
- **certificate**: Certificate used for signing
- **encryption**: Encryption details
  - **algorithm**: Encryption algorithm used
  - **key_id**: Identifier for the encryption key
  - **iv**: Initialization vector
- **trust_level**: Trust level of the message (0-5)
- **audit_trail**: Hash of previous messages for immutable audit trail

#### Reflex

- **timer_id**: Identifier for the reflex timer
- **timeout**: Timeout in milliseconds
- **escalation_path**: List of components to escalate to if timeout occurs
- **priority**: Priority level (0-5)
- **interrupt_level**: Interrupt level (0-3)

#### Routing

- **path**: List of nodes the message should pass through
- **ttl**: Time-to-live in hops
- **hops**: Number of hops the message has traversed
- **flags**: Routing flags
- **qos**: Quality of service level (0-2)

#### Metadata

- **protocol_version**: Version of the protocol
- **content_type**: MIME type of the payload
- **content_encoding**: Encoding of the payload
- **schema_id**: Identifier for the payload schema
- **industry_tags**: Industry-specific tags
- **semantic_compression**: Details about semantic compression
  - **algorithm**: Compression algorithm used
  - **ratio**: Compression ratio
  - **original_size**: Original size in bytes

#### Payload

- Protocol-specific message content

## Usage Guidelines

### Message Creation

1. Create a new UME with a unique ID and current timestamp
2. Set source and target information
3. Set context information for traceability
4. Add security information if required
5. Add reflex timer information if needed
6. Set routing information
7. Add metadata
8. Add payload

### Message Processing

1. Validate the envelope structure and version
2. Verify security (signature, encryption)
3. Check routing information (ttl, hops)
4. Process reflex timer information
5. Extract context information
6. Process payload based on metadata

### Security Considerations

- Always verify signatures before processing messages
- Use appropriate encryption for sensitive data
- Maintain the audit trail for traceability
- Respect trust levels when processing messages

### Performance Considerations

- Use semantic compression for large payloads
- Consider QoS requirements when routing messages
- Be mindful of reflex timer overhead

## Protocol Compatibility

The UME is designed to be compatible with the following protocols:

- **MCP (Mesh Communication Protocol)**
- **A2A (Agent-to-Agent Protocol)**
- **DTSL (Digital Twin Swarm Language)**
- **UDEP (Universal Device Endpoint Protocol)**

Each protocol may extend the UME with protocol-specific fields in the metadata section.

## Extensions

### Industry-Specific Extensions

Industry-specific extensions can be added to the metadata section using the `industry_tags` field and additional fields specific to the industry.

### Protocol-Specific Extensions

Protocol-specific extensions can be added to the metadata section using protocol-specific fields.

### Custom Extensions

Custom extensions can be added to the metadata section as needed, but should follow the naming convention `x-{namespace}-{name}` to avoid conflicts.

## Versioning

The UME specification follows semantic versioning:

- **Major version**: Incompatible changes
- **Minor version**: Backwards-compatible additions
- **Patch version**: Backwards-compatible fixes

## Compliance

All components in the Industriverse Protocol Layer must comply with this specification for interoperability.
