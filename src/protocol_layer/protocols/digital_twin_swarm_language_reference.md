# Digital Twin Swarm Language (DTSL) Reference

## Overview

The Digital Twin Swarm Language (DTSL) is a declarative configuration language for digital twin swarms in industrial environments. It provides a standardized way to define, configure, and orchestrate digital twins and their interactions within the Industriverse Protocol Layer.

## Language Structure

DTSL is a domain-specific language with a hierarchical structure that defines twins, swarms, events, actions, and rules. The language is designed to be human-readable and machine-processable, with a focus on expressiveness and flexibility.

## Syntax

DTSL uses a YAML-like syntax with specific keywords and structures for defining digital twin components.

### Basic Structure

```yaml
version: "1.0"
namespace: "manufacturing.automotive"
description: "Assembly line digital twin swarm"

twins:
  - id: "robot_arm_1"
    type: "robot.arm"
    properties:
      model: "UR10e"
      payload_capacity: 10.0
      reach: 1300.0
      precision: 0.05
    state:
      position: [0.0, 0.0, 0.0]
      orientation: [0.0, 0.0, 0.0]
      status: "idle"
    interfaces:
      - protocol: "opcua"
        endpoint: "opc.tcp://192.168.1.100:4840"
        security:
          mode: "SignAndEncrypt"
          policy: "Basic256Sha256"
      - protocol: "mqtt"
        endpoint: "mqtt://broker.example.com:1883"
        topic_prefix: "factory/robot_arm_1"
    behaviors:
      - id: "pick_and_place"
        parameters:
          - name: "source_position"
            type: "vector3"
          - name: "target_position"
            type: "vector3"
        implementation:
          language: "python"
          code: |
            def execute(source_position, target_position):
              # Move to source position
              move_to(source_position)
              # Activate gripper
              set_gripper(True)
              # Move to target position
              move_to(target_position)
              # Release gripper
              set_gripper(False)
              # Return to home position
              move_to([0.0, 0.0, 0.0])

swarms:
  - id: "assembly_line_1"
    description: "Main assembly line swarm"
    members:
      - twin_id: "robot_arm_1"
        role: "assembler"
      - twin_id: "conveyor_belt_1"
        role: "transporter"
      - twin_id: "vision_system_1"
        role: "inspector"
    topology:
      type: "linear"
      connections:
        - from: "conveyor_belt_1"
          to: "vision_system_1"
        - from: "vision_system_1"
          to: "robot_arm_1"
    coordination:
      strategy: "centralized"
      coordinator: "assembly_controller_1"

events:
  - id: "part_detected"
    source: "vision_system_1"
    data:
      - name: "part_id"
        type: "string"
      - name: "position"
        type: "vector3"
      - name: "orientation"
        type: "vector3"
  - id: "assembly_completed"
    source: "robot_arm_1"
    data:
      - name: "product_id"
        type: "string"
      - name: "timestamp"
        type: "datetime"

actions:
  - id: "start_assembly"
    target: "assembly_line_1"
    parameters:
      - name: "product_id"
        type: "string"
      - name: "batch_size"
        type: "integer"
    implementation:
      type: "swarm_command"
      command: "start"
      args:
        product_id: "${product_id}"
        batch_size: "${batch_size}"

rules:
  - id: "part_detection_rule"
    description: "Handle part detection events"
    trigger:
      event: "part_detected"
      condition: "part_id.startsWith('A')"
    actions:
      - action: "start_assembly"
        args:
          product_id: "${event.part_id}"
          batch_size: 1
```

## Language Elements

### Version

Specifies the version of the DTSL language used in the document.

```yaml
version: "1.0"
```

### Namespace

Defines the namespace for the digital twin swarm, typically using a hierarchical structure.

```yaml
namespace: "manufacturing.automotive"
```

### Description

Provides a human-readable description of the digital twin swarm.

```yaml
description: "Assembly line digital twin swarm"
```

### Twins

Defines individual digital twins with their properties, state, interfaces, and behaviors.

```yaml
twins:
  - id: "robot_arm_1"
    type: "robot.arm"
    properties:
      model: "UR10e"
      payload_capacity: 10.0
    state:
      position: [0.0, 0.0, 0.0]
      status: "idle"
    interfaces:
      - protocol: "opcua"
        endpoint: "opc.tcp://192.168.1.100:4840"
    behaviors:
      - id: "pick_and_place"
        parameters:
          - name: "source_position"
            type: "vector3"
```

#### Twin Properties

- **id**: Unique identifier for the twin
- **type**: Type of the twin, using a hierarchical naming scheme
- **properties**: Static properties of the twin
- **state**: Dynamic state of the twin
- **interfaces**: Communication interfaces for the twin
- **behaviors**: Behaviors that the twin can execute

### Swarms

Defines swarms of digital twins, including their members, topology, and coordination strategy.

```yaml
swarms:
  - id: "assembly_line_1"
    description: "Main assembly line swarm"
    members:
      - twin_id: "robot_arm_1"
        role: "assembler"
    topology:
      type: "linear"
      connections:
        - from: "conveyor_belt_1"
          to: "vision_system_1"
    coordination:
      strategy: "centralized"
      coordinator: "assembly_controller_1"
```

#### Swarm Properties

- **id**: Unique identifier for the swarm
- **description**: Human-readable description of the swarm
- **members**: List of twins that are members of the swarm
- **topology**: Topology of the swarm, including connections between members
- **coordination**: Coordination strategy for the swarm

### Events

Defines events that can be emitted by twins or swarms.

```yaml
events:
  - id: "part_detected"
    source: "vision_system_1"
    data:
      - name: "part_id"
        type: "string"
      - name: "position"
        type: "vector3"
```

#### Event Properties

- **id**: Unique identifier for the event
- **source**: Twin or swarm that emits the event
- **data**: Data associated with the event

### Actions

Defines actions that can be executed by twins or swarms.

```yaml
actions:
  - id: "start_assembly"
    target: "assembly_line_1"
    parameters:
      - name: "product_id"
        type: "string"
      - name: "batch_size"
        type: "integer"
    implementation:
      type: "swarm_command"
      command: "start"
```

#### Action Properties

- **id**: Unique identifier for the action
- **target**: Twin or swarm that executes the action
- **parameters**: Parameters for the action
- **implementation**: Implementation details for the action

### Rules

Defines rules that trigger actions based on events.

```yaml
rules:
  - id: "part_detection_rule"
    description: "Handle part detection events"
    trigger:
      event: "part_detected"
      condition: "part_id.startsWith('A')"
    actions:
      - action: "start_assembly"
        args:
          product_id: "${event.part_id}"
          batch_size: 1
```

#### Rule Properties

- **id**: Unique identifier for the rule
- **description**: Human-readable description of the rule
- **trigger**: Event and condition that trigger the rule
- **actions**: Actions to execute when the rule is triggered

## Data Types

DTSL supports the following data types:

- **string**: Text string
- **integer**: Integer number
- **float**: Floating-point number
- **boolean**: True or false
- **datetime**: Date and time
- **vector2**: 2D vector (x, y)
- **vector3**: 3D vector (x, y, z)
- **quaternion**: Quaternion (x, y, z, w)
- **array**: Array of values
- **object**: Key-value pairs
- **enum**: Enumerated value from a predefined set

## Expressions

DTSL supports expressions for conditions and value calculations:

### Variable References

```yaml
${twin.property}
${event.data}
${parameter}
```

### Operators

- **Arithmetic**: +, -, *, /, %
- **Comparison**: ==, !=, >, <, >=, <=
- **Logical**: &&, ||, !
- **String**: +, startsWith(), endsWith(), contains()
- **Array**: length(), contains(), indexOf()

### Functions

```yaml
min(a, b)
max(a, b)
abs(a)
floor(a)
ceil(a)
round(a)
sin(a)
cos(a)
tan(a)
sqrt(a)
pow(a, b)
```

## Behaviors

Behaviors define the actions that twins can perform. They can be implemented in various languages:

### Python Implementation

```yaml
behaviors:
  - id: "pick_and_place"
    parameters:
      - name: "source_position"
        type: "vector3"
      - name: "target_position"
        type: "vector3"
    implementation:
      language: "python"
      code: |
        def execute(source_position, target_position):
          # Move to source position
          move_to(source_position)
          # Activate gripper
          set_gripper(True)
          # Move to target position
          move_to(target_position)
          # Release gripper
          set_gripper(False)
          # Return to home position
          move_to([0.0, 0.0, 0.0])
```

### JavaScript Implementation

```yaml
behaviors:
  - id: "calculate_trajectory"
    parameters:
      - name: "start"
        type: "vector3"
      - name: "end"
        type: "vector3"
      - name: "speed"
        type: "float"
    implementation:
      language: "javascript"
      code: |
        function execute(start, end, speed) {
          const distance = Math.sqrt(
            Math.pow(end[0] - start[0], 2) +
            Math.pow(end[1] - start[1], 2) +
            Math.pow(end[2] - start[2], 2)
          );
          const time = distance / speed;
          return {
            distance: distance,
            time: time,
            velocity: [
              (end[0] - start[0]) / time,
              (end[1] - start[1]) / time,
              (end[2] - start[2]) / time
            ]
          };
        }
```

### Reference Implementation

```yaml
behaviors:
  - id: "move_to_position"
    parameters:
      - name: "position"
        type: "vector3"
    implementation:
      type: "reference"
      reference: "common.robotics.movement.move_to"
```

## Interfaces

Interfaces define how twins communicate with external systems:

### OPC UA Interface

```yaml
interfaces:
  - protocol: "opcua"
    endpoint: "opc.tcp://192.168.1.100:4840"
    security:
      mode: "SignAndEncrypt"
      policy: "Basic256Sha256"
    mappings:
      - twin_property: "position"
        node_id: "ns=2;s=Robot1.Position"
      - twin_property: "status"
        node_id: "ns=2;s=Robot1.Status"
```

### MQTT Interface

```yaml
interfaces:
  - protocol: "mqtt"
    endpoint: "mqtt://broker.example.com:1883"
    topic_prefix: "factory/robot_arm_1"
    qos: 1
    mappings:
      - twin_property: "position"
        topic: "position"
        direction: "both"
      - twin_property: "status"
        topic: "status"
        direction: "publish"
```

### Modbus Interface

```yaml
interfaces:
  - protocol: "modbus"
    endpoint: "tcp://192.168.1.101:502"
    unit_id: 1
    mappings:
      - twin_property: "temperature"
        register_type: "holding"
        address: 100
        data_type: "float32"
      - twin_property: "status"
        register_type: "coil"
        address: 0
        data_type: "boolean"
```

## Swarm Topologies

DTSL supports various swarm topologies:

### Linear Topology

```yaml
topology:
  type: "linear"
  connections:
    - from: "conveyor_belt_1"
      to: "vision_system_1"
    - from: "vision_system_1"
      to: "robot_arm_1"
```

### Star Topology

```yaml
topology:
  type: "star"
  center: "controller_1"
  connections:
    - to: "robot_arm_1"
    - to: "robot_arm_2"
    - to: "robot_arm_3"
```

### Mesh Topology

```yaml
topology:
  type: "mesh"
  connections:
    - from: "robot_arm_1"
      to: "robot_arm_2"
    - from: "robot_arm_1"
      to: "robot_arm_3"
    - from: "robot_arm_2"
      to: "robot_arm_3"
```

### Hierarchical Topology

```yaml
topology:
  type: "hierarchical"
  levels:
    - id: "level_1"
      nodes: ["controller_1"]
    - id: "level_2"
      nodes: ["robot_arm_1", "robot_arm_2"]
    - id: "level_3"
      nodes: ["sensor_1", "sensor_2", "sensor_3"]
  connections:
    - from: "controller_1"
      to: ["robot_arm_1", "robot_arm_2"]
    - from: "robot_arm_1"
      to: ["sensor_1", "sensor_2"]
    - from: "robot_arm_2"
      to: ["sensor_3"]
```

## Coordination Strategies

DTSL supports various coordination strategies for swarms:

### Centralized Coordination

```yaml
coordination:
  strategy: "centralized"
  coordinator: "assembly_controller_1"
```

### Decentralized Coordination

```yaml
coordination:
  strategy: "decentralized"
  protocol: "consensus"
  parameters:
    algorithm: "raft"
    timeout: 5000
```

### Hierarchical Coordination

```yaml
coordination:
  strategy: "hierarchical"
  levels:
    - coordinator: "factory_controller"
      members: ["assembly_line_1", "assembly_line_2"]
    - coordinator: "assembly_line_1"
      members: ["robot_arm_1", "conveyor_belt_1"]
```

## Best Practices

### Naming Conventions

- Use lowercase for namespaces, with dots as separators
- Use snake_case for twin IDs, event IDs, action IDs, and rule IDs
- Use camelCase for property names and parameter names

### Organization

- Group related twins, events, actions, and rules together
- Use namespaces to organize twins by domain or function
- Define common behaviors in a separate file and reference them

### Security

- Always specify security settings for interfaces
- Use secure protocols when possible
- Limit access to sensitive operations

### Performance

- Minimize the number of connections between twins
- Use efficient data types for properties and state
- Optimize behavior implementations for performance

## Integration with Industriverse Protocol Layer

DTSL integrates with the Industriverse Protocol Layer through the following mechanisms:

### Protocol Kernel Intelligence

DTSL definitions are processed by the Protocol Kernel Intelligence to enable intent-aware routing and semantic compression of digital twin data.

### Self-Healing Protocol Fabric

DTSL swarms can leverage the Self-Healing Protocol Fabric for resilient communication and dynamic path morphing.

### Cross-Mesh Federation

DTSL swarms can participate in Cross-Mesh Federation to enable secure communication between independent protocol meshes.

### Protocol-Driven Genetic Algorithm Layer

DTSL behaviors can be optimized using the Protocol-Driven Genetic Algorithm Layer (PK-Alpha) for algorithm evolution and optimization.

## Examples

### Manufacturing Example

```yaml
version: "1.0"
namespace: "manufacturing.automotive"
description: "Automotive assembly line digital twin swarm"

twins:
  - id: "robot_arm_1"
    type: "robot.arm"
    properties:
      model: "UR10e"
      payload_capacity: 10.0
    state:
      position: [0.0, 0.0, 0.0]
      status: "idle"
    interfaces:
      - protocol: "opcua"
        endpoint: "opc.tcp://192.168.1.100:4840"
  
  - id: "conveyor_belt_1"
    type: "conveyor.belt"
    properties:
      length: 5000.0
      width: 800.0
    state:
      speed: 0.5
      running: true
    interfaces:
      - protocol: "modbus"
        endpoint: "tcp://192.168.1.101:502"

swarms:
  - id: "assembly_line_1"
    description: "Main assembly line swarm"
    members:
      - twin_id: "robot_arm_1"
        role: "assembler"
      - twin_id: "conveyor_belt_1"
        role: "transporter"
    topology:
      type: "linear"
      connections:
        - from: "conveyor_belt_1"
          to: "robot_arm_1"
    coordination:
      strategy: "centralized"
      coordinator: "assembly_controller_1"

events:
  - id: "part_arrived"
    source: "conveyor_belt_1"
    data:
      - name: "part_id"
        type: "string"
      - name: "position"
        type: "vector3"

actions:
  - id: "assemble_part"
    target: "robot_arm_1"
    parameters:
      - name: "part_id"
        type: "string"
      - name: "position"
        type: "vector3"

rules:
  - id: "assembly_rule"
    description: "Trigger assembly when part arrives"
    trigger:
      event: "part_arrived"
    actions:
      - action: "assemble_part"
        args:
          part_id: "${event.part_id}"
          position: "${event.position}"
```

### Energy Management Example

```yaml
version: "1.0"
namespace: "energy.smartgrid"
description: "Smart grid energy management digital twin swarm"

twins:
  - id: "solar_panel_1"
    type: "energy.generator.solar"
    properties:
      capacity: 5000.0
      efficiency: 0.22
    state:
      power_output: 0.0
      temperature: 25.0
    interfaces:
      - protocol: "mqtt"
        endpoint: "mqtt://broker.example.com:1883"
        topic_prefix: "energy/solar_panel_1"
  
  - id: "battery_1"
    type: "energy.storage.battery"
    properties:
      capacity: 10000.0
      max_charge_rate: 2000.0
      max_discharge_rate: 3000.0
    state:
      charge_level: 0.5
      temperature: 22.0
    interfaces:
      - protocol: "modbus"
        endpoint: "tcp://192.168.1.102:502"

swarms:
  - id: "microgrid_1"
    description: "Residential microgrid"
    members:
      - twin_id: "solar_panel_1"
        role: "generator"
      - twin_id: "battery_1"
        role: "storage"
    topology:
      type: "star"
      center: "energy_controller_1"
      connections:
        - to: "solar_panel_1"
        - to: "battery_1"
    coordination:
      strategy: "centralized"
      coordinator: "energy_controller_1"

events:
  - id: "power_surplus"
    source: "solar_panel_1"
    data:
      - name: "amount"
        type: "float"
      - name: "timestamp"
        type: "datetime"

actions:
  - id: "charge_battery"
    target: "battery_1"
    parameters:
      - name: "amount"
        type: "float"
      - name: "rate"
        type: "float"

rules:
  - id: "energy_storage_rule"
    description: "Store excess energy in battery"
    trigger:
      event: "power_surplus"
      condition: "amount > 500.0"
    actions:
      - action: "charge_battery"
        args:
          amount: "${event.amount}"
          rate: "min(${event.amount}, 2000.0)"
```

## Conclusion

The Digital Twin Swarm Language (DTSL) provides a powerful and flexible way to define, configure, and orchestrate digital twins and their interactions within the Industriverse Protocol Layer. By using DTSL, industrial systems can be modeled and controlled in a standardized and interoperable manner, enabling advanced capabilities such as self-organization, adaptation, and optimization.
