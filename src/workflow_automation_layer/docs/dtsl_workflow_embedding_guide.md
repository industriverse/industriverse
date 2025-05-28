# DTSL Workflow Embedding Guide

## Overview

DTSL Workflow Embedding is an advanced feature of the Industriverse Workflow Automation Layer that enables workflows to be defined directly within Digital Twin Swarm Language (DTSL) twin configurations. This guide explains how to embed workflows in DTSL definitions, enabling edge-native autonomy and twin-sourced self-coordination.

## DTSL Workflow Embedding Fundamentals

DTSL Workflow Embedding allows digital twins to:

1. **Self-Orchestrate**: Define and execute workflows autonomously
2. **Edge-Native Execution**: Run workflows directly on edge devices
3. **Twin-Sourced Coordination**: Coordinate activities between twins
4. **State-Driven Workflows**: Trigger workflows based on twin state changes
5. **Hybrid Execution**: Seamlessly transition between edge and cloud execution

## Architecture

The DTSL Workflow Embedding architecture consists of the following components:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                      Workflow Automation Layer                      │
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │             │    │             │    │             │             │
│  │  Workflow   │    │    DTSL     │    │   DTSL      │             │
│  │  Runtime    │◄───┤  Workflow   │◄───┤  Parser     │             │
│  │             │    │  Interpreter│    │             │             │
│  └──────┬──────┘    └──────┬──────┘    └─────────────┘             │
│         │                  │                                       │
│         └──────────┬───────┘                                       │
│                    │                                               │
│          ┌─────────▼──────────┐                                    │
│          │                    │                                    │
│          │  Digital Twin      │                                    │
│          │  Swarm             │                                    │
│          │                    │                                    │
│          └─┬───────┬───────┬──┘                                    │
│            │       │       │                                       │
└────────────┼───────┼───────┼───────────────────────────────────────┘
             │       │       │
    ┌────────▼─┐ ┌───▼────┐ ┌▼────────┐
    │          │ │        │ │         │
    │  Edge    │ │ Cloud  │ │ Hybrid  │
    │  Twins   │ │ Twins  │ │ Twins   │
    │          │ │        │ │         │
    └──────────┘ └────────┘ └─────────┘
```

## DTSL Workflow Syntax

DTSL Workflow Embedding uses a specialized syntax within DTSL definitions:

### 1. Basic Workflow Definition

```yaml
twin:
  id: "machine-123"
  type: "manufacturing-machine"
  workflows:
    startup_sequence:
      description: "Machine startup sequence"
      triggers:
        - type: "state_change"
          condition: "state.power == 'on' && state.operational_status == 'standby'"
      tasks:
        - id: "check_systems"
          type: "system_check"
          parameters:
            check_level: "comprehensive"
        - id: "warm_up"
          type: "warm_up_procedure"
          parameters:
            duration_seconds: 300
          dependencies:
            - "check_systems"
        - id: "calibration"
          type: "calibration_procedure"
          parameters:
            precision_level: "high"
          dependencies:
            - "warm_up"
        - id: "ready_for_operation"
          type: "status_update"
          parameters:
            status: "ready"
          dependencies:
            - "calibration"
```

### 2. State-Driven Workflows

```yaml
workflows:
  temperature_management:
    description: "Temperature management workflow"
    triggers:
      - type: "state_threshold"
        property: "sensors.temperature"
        threshold: 80
        operator: ">"
    tasks:
      - id: "activate_cooling"
        type: "actuator_control"
        parameters:
          actuator: "cooling_system"
          command: "activate"
          level: 80
      - id: "monitor_temperature"
        type: "sensor_monitoring"
        parameters:
          sensor: "temperature"
          interval_seconds: 10
          duration_seconds: 300
        dependencies:
          - "activate_cooling"
      - id: "adjust_cooling"
        type: "conditional_task"
        condition: "sensors.temperature > 75"
        true_task:
          id: "increase_cooling"
          type: "actuator_control"
          parameters:
            actuator: "cooling_system"
            command: "adjust"
            level: 100
        false_task:
          id: "decrease_cooling"
          type: "actuator_control"
          parameters:
            actuator: "cooling_system"
            command: "adjust"
            level: 60
        dependencies:
          - "monitor_temperature"
```

### 3. Twin-to-Twin Coordination

```yaml
workflows:
  material_transfer:
    description: "Coordinate material transfer between machines"
    triggers:
      - type: "message"
        source: "conveyor-system-1"
        message_type: "material_ready"
    tasks:
      - id: "prepare_for_receipt"
        type: "actuator_control"
        parameters:
          actuator: "intake_system"
          command: "prepare"
      - id: "confirm_ready"
        type: "twin_message"
        parameters:
          target_twin: "conveyor-system-1"
          message_type: "ready_for_transfer"
          payload:
            status: "ready"
            estimated_processing_time_seconds: 120
        dependencies:
          - "prepare_for_receipt"
      - id: "process_material"
        type: "processing_procedure"
        parameters:
          procedure_type: "standard_processing"
          quality_check: true
        dependencies:
          - "confirm_ready"
          - condition: "event.message_type == 'transfer_complete'"
            timeout_seconds: 60
      - id: "notify_completion"
        type: "twin_message"
        parameters:
          target_twin: "next-machine-in-line"
          message_type: "material_ready"
          payload:
            material_id: "{{event.payload.material_id}}"
            processing_status: "complete"
        dependencies:
          - "process_material"
```

## Workflow Triggers

DTSL Workflows can be triggered by various events:

### 1. State Change Triggers

```yaml
triggers:
  - type: "state_change"
    property: "operational_status"
    from: "standby"
    to: "active"
```

### 2. Threshold Triggers

```yaml
triggers:
  - type: "state_threshold"
    property: "sensors.pressure"
    threshold: 100
    operator: ">"
    duration_seconds: 30
```

### 3. Schedule Triggers

```yaml
triggers:
  - type: "schedule"
    cron: "0 0 * * *"  # Daily at midnight
    timezone: "UTC"
```

### 4. Message Triggers

```yaml
triggers:
  - type: "message"
    source: "any"
    message_type: "maintenance_request"
```

### 5. External Event Triggers

```yaml
triggers:
  - type: "external_event"
    event_type: "api_call"
    event_source: "maintenance_system"
```

## Task Types

DTSL Workflows support various task types:

### 1. Basic Tasks

```yaml
tasks:
  - id: "data_collection"
    type: "sensor_reading"
    parameters:
      sensors: ["temperature", "pressure", "vibration"]
      sampling_rate: 1
      duration_seconds: 60
```

### 2. Conditional Tasks

```yaml
tasks:
  - id: "quality_check"
    type: "conditional_task"
    condition: "sensors.quality_score < 0.9"
    true_task:
      id: "reject_product"
      type: "actuator_control"
      parameters:
        actuator: "rejection_system"
        command: "activate"
    false_task:
      id: "approve_product"
      type: "status_update"
      parameters:
        status: "approved"
```

### 3. Loop Tasks

```yaml
tasks:
  - id: "batch_processing"
    type: "loop_task"
    iteration_source: "state.batch_items"
    max_parallel: 5
    task_template:
      id: "process_item_{{item.id}}"
      type: "processing_procedure"
      parameters:
        item_id: "{{item.id}}"
        procedure_type: "{{item.type}}"
```

### 4. Twin Interaction Tasks

```yaml
tasks:
  - id: "request_material"
    type: "twin_message"
    parameters:
      target_twin: "warehouse-system"
      message_type: "material_request"
      payload:
        material_type: "raw_aluminum"
        quantity: 10
        priority: "high"
```

### 5. External System Tasks

```yaml
tasks:
  - id: "create_maintenance_ticket"
    type: "external_system"
    system: "maintenance_ticketing"
    operation: "create_ticket"
    parameters:
      title: "Preventive Maintenance Required"
      description: "Scheduled maintenance based on operating hours"
      priority: "medium"
      assigned_team: "maintenance_crew_a"
```

## Edge-Native Execution

DTSL Workflows can be configured for edge-native execution:

```yaml
workflows:
  emergency_shutdown:
    description: "Emergency shutdown procedure"
    edge_execution:
      enabled: true
      offline_capable: true
      resource_requirements:
        cpu: "0.5"
        memory: "256Mi"
    triggers:
      - type: "state_threshold"
        property: "sensors.temperature"
        threshold: 95
        operator: ">"
    tasks:
      - id: "shutdown_power"
        type: "actuator_control"
        parameters:
          actuator: "main_power"
          command: "shutdown"
          emergency: true
      - id: "activate_cooling"
        type: "actuator_control"
        parameters:
          actuator: "emergency_cooling"
          command: "activate"
        dependencies:
          - "shutdown_power"
      - id: "notify_operators"
        type: "notification"
        parameters:
          channels: ["local_alarm", "operator_panel"]
          message: "EMERGENCY SHUTDOWN ACTIVATED: High temperature detected"
          severity: "critical"
        dependencies:
          - "shutdown_power"
      - id: "log_event"
        type: "data_logging"
        parameters:
          event_type: "emergency_shutdown"
          data:
            temperature: "{{sensors.temperature}}"
            timestamp: "{{system.timestamp}}"
            reason: "Temperature threshold exceeded"
        dependencies:
          - "shutdown_power"
```

## Twin-Sourced Self-Coordination

DTSL Workflows enable twins to coordinate activities:

```yaml
# Twin A: Manufacturing Machine
workflows:
  request_maintenance:
    description: "Request maintenance when needed"
    triggers:
      - type: "state_threshold"
        property: "maintenance.operating_hours"
        threshold: 500
        operator: ">"
    tasks:
      - id: "check_maintenance_availability"
        type: "twin_query"
        parameters:
          target_twin: "maintenance-scheduler"
          query: "availability"
          parameters:
            duration_hours: 2
            urgency: "routine"
      - id: "schedule_maintenance"
        type: "twin_message"
        parameters:
          target_twin: "maintenance-scheduler"
          message_type: "maintenance_request"
          payload:
            machine_id: "{{twin.id}}"
            maintenance_type: "routine"
            estimated_duration_hours: 2
            preferred_time: "{{tasks.check_maintenance_availability.result.next_available_slot}}"
        dependencies:
          - "check_maintenance_availability"
      - id: "prepare_for_maintenance"
        type: "workflow"
        parameters:
          workflow: "maintenance_preparation"
        dependencies:
          - condition: "event.message_type == 'maintenance_scheduled'"
            timeout_seconds: 3600
```

```yaml
# Twin B: Maintenance Scheduler
workflows:
  handle_maintenance_request:
    description: "Handle incoming maintenance requests"
    triggers:
      - type: "message"
        message_type: "maintenance_request"
    tasks:
      - id: "check_technician_availability"
        type: "external_system"
        system: "workforce_management"
        operation: "check_availability"
        parameters:
          skill_required: "machine_maintenance"
          duration_hours: "{{event.payload.estimated_duration_hours}}"
          preferred_time: "{{event.payload.preferred_time}}"
      - id: "schedule_technician"
        type: "external_system"
        system: "workforce_management"
        operation: "schedule_task"
        parameters:
          task_type: "maintenance"
          machine_id: "{{event.payload.machine_id}}"
          scheduled_time: "{{tasks.check_technician_availability.result.best_time_slot}}"
          duration_hours: "{{event.payload.estimated_duration_hours}}"
        dependencies:
          - "check_technician_availability"
      - id: "confirm_maintenance"
        type: "twin_message"
        parameters:
          target_twin: "{{event.source}}"
          message_type: "maintenance_scheduled"
          payload:
            scheduled_time: "{{tasks.schedule_technician.result.scheduled_time}}"
            technician_id: "{{tasks.schedule_technician.result.technician_id}}"
        dependencies:
          - "schedule_technician"
```

## Hybrid Execution Models

DTSL Workflows support hybrid execution across edge and cloud:

```yaml
workflows:
  predictive_maintenance:
    description: "Predictive maintenance workflow"
    hybrid_execution:
      enabled: true
      task_placement:
        data_collection:
          location: "edge"
          fallback: "cloud"
        data_preprocessing:
          location: "edge"
          fallback: "cloud"
        model_inference:
          location: "edge"
          fallback: "cloud"
        anomaly_analysis:
          location: "cloud"
          fallback: "none"
        maintenance_planning:
          location: "cloud"
          fallback: "none"
    triggers:
      - type: "schedule"
        cron: "0 */6 * * *"  # Every 6 hours
    tasks:
      - id: "data_collection"
        type: "sensor_reading"
        parameters:
          sensors: ["temperature", "vibration", "power_consumption"]
          duration_seconds: 300
      - id: "data_preprocessing"
        type: "data_processing"
        parameters:
          operations: ["filtering", "normalization", "feature_extraction"]
        dependencies:
          - "data_collection"
      - id: "model_inference"
        type: "ml_inference"
        parameters:
          model: "predictive_maintenance_model"
          input_data: "{{tasks.data_preprocessing.result}}"
        dependencies:
          - "data_preprocessing"
      - id: "anomaly_analysis"
        type: "data_analysis"
        parameters:
          analysis_type: "anomaly_detection"
          threshold: 0.8
          input_data: "{{tasks.model_inference.result}}"
        dependencies:
          - "model_inference"
      - id: "maintenance_planning"
        type: "conditional_task"
        condition: "tasks.anomaly_analysis.result.anomaly_detected"
        true_task:
          id: "schedule_maintenance"
          type: "workflow"
          parameters:
            workflow: "request_maintenance"
        false_task:
          id: "update_health_status"
          type: "state_update"
          parameters:
            property: "health_status"
            value: "{{tasks.anomaly_analysis.result.health_score}}"
        dependencies:
          - "anomaly_analysis"
```

## Configuring DTSL Workflow Embedding

DTSL Workflow Embedding is configured at multiple levels:

### 1. System Level

In the Workflow Automation Layer configuration:

```yaml
dtsl_workflow_embedding:
  enabled: true
  default_execution_location: "hybrid"
  edge_capabilities:
    enabled: true
    offline_support: true
    resource_monitoring: true
  twin_coordination:
    enabled: true
    message_reliability: "at_least_once"
    coordination_patterns:
      - "request_response"
      - "publish_subscribe"
      - "choreography"
```

### 2. Twin Type Level

In the twin type definition:

```yaml
twin_type:
  id: "manufacturing_machine"
  workflow_capabilities:
    execution_environments:
      - "edge"
      - "cloud"
    supported_task_types:
      - "sensor_reading"
      - "actuator_control"
      - "data_processing"
      - "ml_inference"
    offline_capabilities:
      enabled: true
      max_offline_duration_hours: 24
      sync_strategy: "incremental"
```

### 3. Twin Instance Level

In the twin instance definition:

```yaml
twin:
  id: "machine-123"
  type: "manufacturing_machine"
  workflow_config:
    preferred_execution_location: "edge"
    resource_limits:
      cpu: "2"
      memory: "1Gi"
      storage: "10Gi"
    connectivity:
      offline_mode_enabled: true
      sync_interval_seconds: 300
```

## Integration with Workflow Automation Layer

DTSL Workflows integrate with the broader Workflow Automation Layer:

### 1. Workflow Registry Integration

```yaml
dtsl_workflow_embedding:
  registry_integration:
    enabled: true
    registration_mode: "automatic"
    versioning_enabled: true
    discovery_enabled: true
```

### 2. Execution Mode Integration

```yaml
dtsl_workflow_embedding:
  execution_mode_integration:
    enabled: true
    trust_inheritance: true
    mode_mapping:
      autonomous: "edge_preferred"
      supervised: "hybrid"
      manual: "cloud_only"
```

### 3. Mesh Topology Integration

```yaml
dtsl_workflow_embedding:
  mesh_topology_integration:
    enabled: true
    twin_as_mesh_node: true
    mesh_discovery: true
    routing_constraints_inheritance: true
```

### 4. Debug Trace Integration

```yaml
dtsl_workflow_embedding:
  debug_trace_integration:
    enabled: true
    trace_level: "standard"
    edge_trace_buffer_size: "100Mi"
    sync_interval_seconds: 300
```

## Example: Manufacturing Cell Orchestration

This example demonstrates DTSL Workflow Embedding for a manufacturing cell:

```yaml
# Cell Controller Twin
twin:
  id: "cell-controller-1"
  type: "manufacturing_cell_controller"
  workflows:
    production_sequence:
      description: "Coordinate production sequence across machines"
      triggers:
        - type: "message"
          message_type: "production_order"
      tasks:
        - id: "validate_order"
          type: "data_validation"
          parameters:
            schema: "production_order_schema"
            data: "{{event.payload}}"
        - id: "allocate_resources"
          type: "resource_allocation"
          parameters:
            required_machines: ["cnc-1", "robot-1", "inspection-1"]
            materials: "{{event.payload.materials}}"
          dependencies:
            - "validate_order"
        - id: "coordinate_production"
          type: "parallel_task"
          tasks:
            - id: "setup_cnc"
              type: "twin_message"
              parameters:
                target_twin: "cnc-1"
                message_type: "setup_request"
                payload:
                  program: "{{event.payload.program_id}}"
                  parameters: "{{event.payload.machining_parameters}}"
            - id: "setup_robot"
              type: "twin_message"
              parameters:
                target_twin: "robot-1"
                message_type: "setup_request"
                payload:
                  program: "{{event.payload.robot_program_id}}"
                  parameters: "{{event.payload.robot_parameters}}"
            - id: "setup_inspection"
              type: "twin_message"
              parameters:
                target_twin: "inspection-1"
                message_type: "setup_request"
                payload:
                  inspection_profile: "{{event.payload.quality_profile}}"
          dependencies:
            - "allocate_resources"
        - id: "start_production"
          type: "twin_message"
          parameters:
            target_twin: "robot-1"
            message_type: "start_operation"
            payload:
              sequence_id: "{{event.payload.order_id}}"
          dependencies:
            - "coordinate_production"
        - id: "monitor_production"
          type: "monitoring_task"
          parameters:
            targets: ["cnc-1", "robot-1", "inspection-1"]
            metrics: ["status", "progress", "quality_metrics"]
            interval_seconds: 10
            alert_conditions:
              - "cnc-1.status != 'running' && cnc-1.progress < 100"
              - "robot-1.status != 'running' && robot-1.progress < 100"
              - "inspection-1.status != 'running' && inspection-1.progress < 100"
          dependencies:
            - "start_production"
        - id: "complete_production"
          type: "conditional_task"
          condition: "cnc-1.progress == 100 && robot-1.progress == 100 && inspection-1.progress == 100"
          true_task:
            id: "report_completion"
            type: "external_system"
            system: "production_management"
            operation: "update_order_status"
            parameters:
              order_id: "{{event.payload.order_id}}"
              status: "completed"
              quality_metrics: "{{inspection-1.quality_metrics}}"
          dependencies:
            - "monitor_production"
```

```yaml
# CNC Machine Twin
twin:
  id: "cnc-1"
  type: "cnc_machine"
  workflows:
    handle_setup_request:
      description: "Handle setup requests from cell controller"
      edge_execution:
        enabled: true
        offline_capable: true
      triggers:
        - type: "message"
          message_type: "setup_request"
      tasks:
        - id: "load_program"
          type: "actuator_control"
          parameters:
            actuator: "program_loader"
            command: "load"
            program_id: "{{event.payload.program}}"
        - id: "configure_parameters"
          type: "actuator_control"
          parameters:
            actuator: "parameter_controller"
            command: "set_multiple"
            parameters: "{{event.payload.parameters}}"
          dependencies:
            - "load_program"
        - id: "verify_setup"
          type: "system_check"
          parameters:
            check_type: "program_loaded"
            expected_program: "{{event.payload.program}}"
          dependencies:
            - "configure_parameters"
        - id: "confirm_setup"
          type: "twin_message"
          parameters:
            target_twin: "{{event.source}}"
            message_type: "setup_complete"
            payload:
              status: "ready"
              loaded_program: "{{event.payload.program}}"
          dependencies:
            - "verify_setup"
    
    handle_operation:
      description: "Handle machining operations"
      edge_execution:
        enabled: true
        offline_capable: true
      triggers:
        - type: "message"
          message_type: "start_operation"
        - type: "state_change"
          property: "operational_status"
          to: "ready_to_start"
      tasks:
        - id: "start_machining"
          type: "actuator_control"
          parameters:
            actuator: "machine_controller"
            command: "start"
            sequence_id: "{{event.payload.sequence_id || state.current_sequence_id}}"
        - id: "monitor_progress"
          type: "sensor_monitoring"
          parameters:
            sensors: ["spindle_load", "feed_rate", "temperature"]
            interval_seconds: 5
            duration_seconds: -1  # Continuous until stopped
          dependencies:
            - "start_machining"
        - id: "update_progress"
          type: "state_update"
          parameters:
            property: "progress"
            value: "{{sensors.program_progress}}"
            property: "status"
            value: "running"
          dependencies:
            - "monitor_progress"
          repeat:
            interval_seconds: 5
            condition: "sensors.program_progress < 100"
        - id: "complete_operation"
          type: "actuator_control"
          parameters:
            actuator: "machine_controller"
            command: "complete"
          dependencies:
            - condition: "sensors.program_progress >= 100"
        - id: "update_final_status"
          type: "state_update"
          parameters:
            property: "progress"
            value: 100
            property: "status"
            value: "completed"
          dependencies:
            - "complete_operation"
        - id: "notify_completion"
          type: "twin_message"
          parameters:
            target_twin: "cell-controller-1"
            message_type: "operation_complete"
            payload:
              sequence_id: "{{event.payload.sequence_id || state.current_sequence_id}}"
              status: "completed"
              machining_metrics:
                cycle_time_seconds: "{{sensors.cycle_time}}"
                quality_indicators: "{{sensors.quality_indicators}}"
          dependencies:
            - "update_final_status"
```

## Best Practices

1. **Appropriate Granularity**: Define workflows with appropriate task granularity
2. **Clear Triggers**: Define clear and specific triggers for workflows
3. **Edge Awareness**: Be aware of edge capabilities and limitations
4. **Resilience**: Design workflows to handle connectivity issues
5. **State Management**: Use twin state effectively for workflow control
6. **Coordination Patterns**: Use appropriate coordination patterns between twins
7. **Resource Efficiency**: Configure resource constraints for efficient execution
8. **Testing**: Test workflows under various connectivity scenarios
9. **Versioning**: Version workflows and manage updates carefully
10. **Documentation**: Document workflow behavior and dependencies

## Troubleshooting

### Common Issues

1. **Edge Execution Failures**
   - **Symptom**: Workflows failing to execute on edge devices
   - **Cause**: Insufficient resources or missing capabilities
   - **Solution**: Review resource requirements and edge capabilities

2. **Coordination Failures**
   - **Symptom**: Twins failing to coordinate activities
   - **Cause**: Connectivity issues or message delivery failures
   - **Solution**: Implement retry mechanisms and fallback strategies

3. **State Synchronization Issues**
   - **Symptom**: Inconsistent state between edge and cloud
   - **Cause**: Connectivity issues or synchronization failures
   - **Solution**: Implement conflict resolution strategies and eventual consistency

4. **Trigger Misfires**
   - **Symptom**: Workflows triggering incorrectly or not at all
   - **Cause**: Misconfigured triggers or state issues
   - **Solution**: Review trigger configurations and state management

## Conclusion

DTSL Workflow Embedding provides a powerful framework for defining workflows directly within digital twin definitions, enabling edge-native autonomy and twin-sourced self-coordination. By configuring appropriate workflows, triggers, and tasks, you can create digital twins that can operate autonomously at the edge while maintaining coordination with the broader system.

## Additional Resources

- [Workflow Manifest Specification](workflow_manifest_spec.md)
- [Task Contract Specification](task_contract_spec.md)
- [Mesh Topology Guide](mesh_topology_guide.md)
- [Execution Modes Guide](execution_modes_guide.md)
- [Digital Twin Swarm Language Reference](../protocols/digital_twin_swarm_language_reference.md)

## Version History

- **1.0.0** (2025-05-22): Initial guide
