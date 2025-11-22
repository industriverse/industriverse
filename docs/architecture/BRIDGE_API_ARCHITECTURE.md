# Bridge API Architecture

## 1. Purpose
The Bridge API serves as the unified gateway for all Industriverse services, abstracting the complexity of the underlying subsystems (Trifecta, Expansion Packs, etc.) from external clients.

## 2. Architecture

### 2.1 Core Components
- **FastAPI Server**: The main entry point handling HTTP requests.
- **Middleware Stack**:
    - `Authentication`: Verifies JWTs and API keys.
    - `Rate Limiting`: Enforces usage limits based on CEU.
    - `AI Shield`: Performs safety checks on inputs/outputs.
- **Route Controllers**:
    - `/eil/*`: Energy Intelligence Layer endpoints.
    - `/trifecta/*`: Trifecta AI endpoints.
    - `/packs/*`: Expansion Pack endpoints.
- **Protocol Adapters**:
    - `MCP Adapter`: Connects to the Model Context Protocol.
    - `A2A Adapter`: Connects to the Agent-to-Agent protocol.

## 3. Data Flow
1. **Request**: Client sends request to Bridge API.
2. **Auth**: Middleware verifies identity.
3. **Safety**: AI Shield scans input.
4. **Routing**: Controller dispatches to appropriate service.
5. **Response**: Service returns result, AI Shield scans output, Bridge API responds to client.

## 4. Deployment
Deployed as a scalable microservice in the `overseer-system` namespace on Kubernetes.
