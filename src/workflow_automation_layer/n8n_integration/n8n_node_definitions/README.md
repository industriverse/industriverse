# n8n Node Definitions for Industriverse Workflow Automation Layer

This directory contains the node definitions for integrating Industriverse with n8n.
These node definitions allow n8n to interact with Industriverse workflows, agents,
and other components.

## Node Types

### IndustriverseTrigger

Triggers a workflow when an event occurs in Industriverse.

```json
{
  "name": "IndustriverseTrigger",
  "description": "Triggers when an event occurs in Industriverse",
  "type": "trigger",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": [],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Event Type",
      "name": "eventType",
      "type": "options",
      "options": [
        {
          "name": "Workflow Started",
          "value": "workflow_started"
        },
        {
          "name": "Workflow Completed",
          "value": "workflow_completed"
        },
        {
          "name": "Task Completed",
          "value": "task_completed"
        },
        {
          "name": "Human Intervention Required",
          "value": "human_intervention_required"
        },
        {
          "name": "Agent Message",
          "value": "agent_message"
        },
        {
          "name": "Trust Score Changed",
          "value": "trust_score_changed"
        },
        {
          "name": "Execution Mode Changed",
          "value": "execution_mode_changed"
        },
        {
          "name": "Custom Event",
          "value": "custom_event"
        }
      ],
      "default": "workflow_started",
      "required": true,
      "description": "The type of event to trigger on"
    },
    {
      "displayName": "Workflow ID",
      "name": "workflowId",
      "type": "string",
      "default": "",
      "required": false,
      "description": "ID of the workflow to monitor (leave empty to monitor all workflows)"
    },
    {
      "displayName": "Custom Event Name",
      "name": "customEventName",
      "type": "string",
      "default": "",
      "required": false,
      "displayOptions": {
        "show": {
          "eventType": ["custom_event"]
        }
      },
      "description": "Name of the custom event to trigger on"
    },
    {
      "displayName": "Webhook Authentication",
      "name": "authentication",
      "type": "boolean",
      "default": true,
      "description": "Whether to require authentication for the webhook"
    },
    {
      "displayName": "Authentication Key",
      "name": "authKey",
      "type": "string",
      "default": "",
      "required": true,
      "displayOptions": {
        "show": {
          "authentication": [true]
        }
      },
      "description": "Authentication key for the webhook"
    }
  ]
}
```

### IndustriverseTriggerResponse

Sends a response to a human intervention request.

```json
{
  "name": "IndustriverseTriggerResponse",
  "description": "Sends a response to a human intervention request",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Intervention ID",
      "name": "interventionId",
      "type": "string",
      "default": "={{ $json.intervention_id }}",
      "required": true,
      "description": "ID of the intervention to respond to"
    },
    {
      "displayName": "Decision",
      "name": "decision",
      "type": "options",
      "options": [
        {
          "name": "Approve",
          "value": "approve"
        },
        {
          "name": "Reject",
          "value": "reject"
        },
        {
          "name": "Escalate",
          "value": "escalate"
        },
        {
          "name": "Custom",
          "value": "custom"
        }
      ],
      "default": "approve",
      "required": true,
      "description": "The decision for the intervention"
    },
    {
      "displayName": "Custom Decision",
      "name": "customDecision",
      "type": "string",
      "default": "",
      "required": true,
      "displayOptions": {
        "show": {
          "decision": ["custom"]
        }
      },
      "description": "Custom decision value"
    },
    {
      "displayName": "Comments",
      "name": "comments",
      "type": "string",
      "default": "",
      "required": false,
      "description": "Comments about the decision"
    },
    {
      "displayName": "Response Data",
      "name": "responseData",
      "type": "json",
      "default": "{}",
      "required": false,
      "description": "Additional data to include in the response"
    },
    {
      "displayName": "Responder ID",
      "name": "responderId",
      "type": "string",
      "default": "n8n_user",
      "required": false,
      "description": "ID of the responder"
    }
  ]
}
```

### IndustriverseTriggerWorkflow

Triggers an Industriverse workflow.

```json
{
  "name": "IndustriverseTriggerWorkflow",
  "description": "Triggers an Industriverse workflow",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Workflow ID",
      "name": "workflowId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow to trigger"
    },
    {
      "displayName": "Input Data",
      "name": "inputData",
      "type": "json",
      "default": "{}",
      "required": false,
      "description": "Input data for the workflow"
    },
    {
      "displayName": "Execution Mode",
      "name": "executionMode",
      "type": "options",
      "options": [
        {
          "name": "Default",
          "value": "default"
        },
        {
          "name": "Reactive",
          "value": "reactive"
        },
        {
          "name": "Proactive",
          "value": "proactive"
        },
        {
          "name": "Autonomous",
          "value": "autonomous"
        },
        {
          "name": "Supervised",
          "value": "supervised"
        }
      ],
      "default": "default",
      "required": false,
      "description": "Execution mode for the workflow"
    },
    {
      "displayName": "Wait for Completion",
      "name": "waitForCompletion",
      "type": "boolean",
      "default": false,
      "description": "Whether to wait for the workflow to complete before continuing"
    },
    {
      "displayName": "Timeout (seconds)",
      "name": "timeout",
      "type": "number",
      "default": 300,
      "required": false,
      "displayOptions": {
        "show": {
          "waitForCompletion": [true]
        }
      },
      "description": "Maximum time to wait for workflow completion (in seconds)"
    }
  ]
}
```

### IndustriverseTriggerGetWorkflowStatus

Gets the status of an Industriverse workflow.

```json
{
  "name": "IndustriverseTriggerGetWorkflowStatus",
  "description": "Gets the status of an Industriverse workflow",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Workflow ID",
      "name": "workflowId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow to get status for"
    },
    {
      "displayName": "Execution ID",
      "name": "executionId",
      "type": "string",
      "default": "",
      "required": false,
      "description": "ID of the specific execution to get status for (leave empty for latest)"
    }
  ]
}
```

### IndustriverseTriggerUpdateTaskStatus

Updates the status of a task in an Industriverse workflow.

```json
{
  "name": "IndustriverseTriggerUpdateTaskStatus",
  "description": "Updates the status of a task in an Industriverse workflow",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Workflow ID",
      "name": "workflowId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow containing the task"
    },
    {
      "displayName": "Execution ID",
      "name": "executionId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow execution"
    },
    {
      "displayName": "Task ID",
      "name": "taskId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the task to update"
    },
    {
      "displayName": "Status",
      "name": "status",
      "type": "options",
      "options": [
        {
          "name": "Pending",
          "value": "pending"
        },
        {
          "name": "In Progress",
          "value": "in_progress"
        },
        {
          "name": "Completed",
          "value": "completed"
        },
        {
          "name": "Failed",
          "value": "failed"
        },
        {
          "name": "Skipped",
          "value": "skipped"
        }
      ],
      "default": "completed",
      "required": true,
      "description": "New status for the task"
    },
    {
      "displayName": "Result Data",
      "name": "resultData",
      "type": "json",
      "default": "{}",
      "required": false,
      "description": "Result data for the task"
    }
  ]
}
```

### IndustriverseTriggerCreateIntervention

Creates a human intervention request in Industriverse.

```json
{
  "name": "IndustriverseTriggerCreateIntervention",
  "description": "Creates a human intervention request in Industriverse",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Workflow ID",
      "name": "workflowId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow requiring intervention"
    },
    {
      "displayName": "Execution ID",
      "name": "executionId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the workflow execution"
    },
    {
      "displayName": "Task ID",
      "name": "taskId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the task requiring intervention"
    },
    {
      "displayName": "Intervention Type",
      "name": "interventionType",
      "type": "options",
      "options": [
        {
          "name": "Approval",
          "value": "approval"
        },
        {
          "name": "Decision",
          "value": "decision"
        },
        {
          "name": "Information",
          "value": "information"
        },
        {
          "name": "Error",
          "value": "error"
        },
        {
          "name": "Custom",
          "value": "custom"
        }
      ],
      "default": "approval",
      "required": true,
      "description": "Type of intervention required"
    },
    {
      "displayName": "Title",
      "name": "title",
      "type": "string",
      "default": "",
      "required": true,
      "description": "Title of the intervention request"
    },
    {
      "displayName": "Description",
      "name": "description",
      "type": "string",
      "default": "",
      "required": true,
      "description": "Description of the intervention request"
    },
    {
      "displayName": "Priority",
      "name": "priority",
      "type": "options",
      "options": [
        {
          "name": "Low",
          "value": "low"
        },
        {
          "name": "Medium",
          "value": "medium"
        },
        {
          "name": "High",
          "value": "high"
        },
        {
          "name": "Critical",
          "value": "critical"
        }
      ],
      "default": "medium",
      "required": false,
      "description": "Priority of the intervention request"
    },
    {
      "displayName": "Assigned To",
      "name": "assignedTo",
      "type": "string",
      "default": "",
      "required": false,
      "description": "User or role to assign the intervention to"
    },
    {
      "displayName": "Expiration (minutes)",
      "name": "expirationMinutes",
      "type": "number",
      "default": 60,
      "required": false,
      "description": "Time until the intervention expires (in minutes)"
    },
    {
      "displayName": "Options",
      "name": "options",
      "type": "json",
      "default": "[]",
      "required": false,
      "description": "Available options for the intervention (for decision type)"
    },
    {
      "displayName": "Context Data",
      "name": "contextData",
      "type": "json",
      "default": "{}",
      "required": false,
      "description": "Additional context data for the intervention"
    }
  ]
}
```

### IndustriverseTriggerGetInterventionStatus

Gets the status of a human intervention request.

```json
{
  "name": "IndustriverseTriggerGetInterventionStatus",
  "description": "Gets the status of a human intervention request",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Intervention ID",
      "name": "interventionId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the intervention to get status for"
    }
  ]
}
```

### IndustriverseTriggerUpdateCapsule

Updates a workflow capsule in Industriverse.

```json
{
  "name": "IndustriverseTriggerUpdateCapsule",
  "description": "Updates a workflow capsule in Industriverse",
  "type": "action",
  "icon": "file:industriverse.svg",
  "version": 1,
  "inputs": ["main"],
  "outputs": ["main"],
  "properties": [
    {
      "displayName": "Capsule ID",
      "name": "capsuleId",
      "type": "string",
      "default": "",
      "required": true,
      "description": "ID of the capsule to update"
    },
    {
      "displayName": "Update Type",
      "name": "updateType",
      "type": "options",
      "options": [
        {
          "name": "State",
          "value": "state"
        },
        {
          "name": "Visibility",
          "value": "visibility"
        },
        {
          "name": "UI Mode",
          "value": "ui_mode"
        },
        {
          "name": "Execution Mode",
          "value": "execution_mode"
        },
        {
          "name": "Progress",
          "value": "progress"
        },
        {
          "name": "Context",
          "value": "context"
        }
      ],
      "default": "state",
      "required": true,
      "description": "Type of update to perform"
    },
    {
      "displayName": "State",
      "name": "state",
      "type": "options",
      "options": [
        {
          "name": "Running",
          "value": "running"
        },
        {
          "name": "Paused",
          "value": "paused"
        },
        {
          "name": "Completed",
          "value": "completed"
        },
        {
          "name": "Failed",
          "value": "failed"
        },
        {
          "name": "Suspended",
          "value": "suspended"
        }
      ],
      "default": "running",
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["state"]
        }
      },
      "description": "New state for the capsule"
    },
    {
      "displayName": "Visibility",
      "name": "visibility",
      "type": "options",
      "options": [
        {
          "name": "Visible",
          "value": "visible"
        },
        {
          "name": "Minimized",
          "value": "minimized"
        },
        {
          "name": "Background",
          "value": "background"
        },
        {
          "name": "Pinned",
          "value": "pinned"
        }
      ],
      "default": "visible",
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["visibility"]
        }
      },
      "description": "New visibility for the capsule"
    },
    {
      "displayName": "UI Mode",
      "name": "uiMode",
      "type": "options",
      "options": [
        {
          "name": "Standard",
          "value": "standard"
        },
        {
          "name": "Compact",
          "value": "compact"
        },
        {
          "name": "Detailed",
          "value": "detailed"
        },
        {
          "name": "Debug",
          "value": "debug"
        }
      ],
      "default": "standard",
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["ui_mode"]
        }
      },
      "description": "New UI mode for the capsule"
    },
    {
      "displayName": "Execution Mode",
      "name": "executionMode",
      "type": "options",
      "options": [
        {
          "name": "Reactive",
          "value": "reactive"
        },
        {
          "name": "Proactive",
          "value": "proactive"
        },
        {
          "name": "Autonomous",
          "value": "autonomous"
        },
        {
          "name": "Supervised",
          "value": "supervised"
        }
      ],
      "default": "reactive",
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["execution_mode"]
        }
      },
      "description": "New execution mode for the capsule"
    },
    {
      "displayName": "Progress",
      "name": "progress",
      "type": "number",
      "default": 0,
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["progress"]
        }
      },
      "description": "New progress value for the capsule (0-100)"
    },
    {
      "displayName": "Context Variables",
      "name": "contextVariables",
      "type": "json",
      "default": "{}",
      "required": true,
      "displayOptions": {
        "show": {
          "updateType": ["context"]
        }
      },
      "description": "New context variables for the capsule"
    }
  ]
}
```

## Usage

These node definitions can be used to create n8n nodes that interact with Industriverse.
The nodes can be used in n8n workflows to trigger Industriverse workflows, respond to
human intervention requests, and update workflow status.

## Integration

To integrate these node definitions with n8n, they need to be packaged as an n8n
community node package. This involves creating a package.json file, implementing
the node functionality, and publishing the package to npm.

See the `industriverse_nodes_plugin` directory for the complete n8n community node
package implementation.
