# Universal Skin / Dynamic Agent Capsules

## Overview

The Universal Skin (also known as Dynamic Agent Capsules) is a modern UI/UX paradigm for the Deployment Operations Layer, inspired by the iPhone's Dynamic Island. It represents live agent instances and digital twins as floating, adaptive UI nodes ("Islands" or "Capsules") that provide contextual information and micro-interactions.

## Features

- **Contextual Agent Representation**: Display agents as interactive capsules with real-time status
- **Adaptive UI**: Capsules expand, contract, and adapt based on context and user interaction
- **Decentralized Access**: Pin capsules to OS (desktop widgets, mobile bars, AR HUDs)
- **Micro-Interactions**: Quick actions for agent management (Fork, Migrate, Suspend, Rescope)
- **Cross-Platform**: Works across web, desktop, and mobile environments

## Components

### UniversalSkin

The base component representing a single agent capsule. It displays agent information, status, and provides interaction capabilities.

```jsx
<UniversalSkin
  agent={agentData}
  status="active"
  isPinned={false}
  onPin={handlePin}
  onFork={handleFork}
  onSuspend={handleSuspend}
  onRescope={handleRescope}
/>
```

### UniversalSkinContainer

Container component that manages multiple agent capsules, handling their arrangement and organization.

```jsx
<UniversalSkinContainer
  agents={agentsArray}
  position="fixed"
  maxWidth="360px"
  top="20px"
  right="20px"
  onAgentAction={handleAgentAction}
/>
```

### UniversalSkinContext

React context provider for managing Universal Skin state across the application.

```jsx
<UniversalSkinProvider apiEndpoint="/api/universal-skin">
  <YourApplication />
</UniversalSkinProvider>
```

### UniversalSkinAPI

API service for communicating with the backend agent system.

```javascript
const api = new UniversalSkinAPI('/api/universal-skin');
const agents = await api.getAgents();
```

### UniversalSkinApp

Complete application component that integrates all Universal Skin components.

```jsx
<UniversalSkinApp
  apiEndpoint="/api/universal-skin"
  position="fixed"
  maxWidth="360px"
  top="20px"
  right="20px"
/>
```

## Integration

To integrate the Universal Skin into your application:

1. Import the necessary components:
```javascript
import { UniversalSkinApp } from '../ui/universal_skin';
```

2. Add the UniversalSkinApp component to your application:
```jsx
<div className="your-app">
  <UniversalSkinApp apiEndpoint="/api/universal-skin" />
  {/* Your application content */}
</div>
```

3. Ensure your backend API implements the required endpoints for agent management.

## Customization

The Universal Skin components can be customized using styled-components or by passing className and style props:

```jsx
<UniversalSkinApp
  className="custom-skin"
  style={{ zIndex: 2000 }}
/>
```

## Backend API Requirements

The Universal Skin expects the following API endpoints:

- `GET /agents` - List all agents
- `GET /agents/:id` - Get a specific agent
- `POST /agents` - Create a new agent
- `PUT /agents/:id` - Update an agent
- `DELETE /agents/:id` - Delete an agent
- `POST /agents/:id/actions` - Perform an action on an agent
- `GET /agents/:id/metrics` - Get agent metrics
- `GET /agents/:id/status` - Get agent status

## Agent Data Structure

```javascript
{
  id: "agent-123",
  name: "Deployer Agent",
  description: "Handles deployment operations",
  avatarUrl: "/images/agent-avatar.png",
  currentTask: "Deploying to production",
  context: "Production environment",
  statusMessage: "Deployment in progress",
  status: "active", // active, warning, error, idle
  isPinned: false,
  isDocked: true,
  metrics: {
    deployments: 42,
    successRate: "99.5%",
    avgDeployTime: "2m 30s"
  }
}
```
