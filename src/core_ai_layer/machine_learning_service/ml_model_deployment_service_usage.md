# MLModelDeploymentService Usage Guide

This document outlines the usage of the `MLModelDeploymentService`, a key component of the `machine_learning_service` within the Core AI Layer. It is designed to manage the deployment lifecycle of trained machine learning models.

## 1. Overview

The `MLModelDeploymentService` facilitates the deployment of models to various target environments (e.g., as real-time API services or for batch inference jobs). It handles fetching model artifacts, packaging them for serving (conceptually, this could involve containerization), provisioning the deployment target, and managing active deployments. It aims to integrate with a Model Registry and potentially container registries and orchestration platforms.

## 2. Initialization

To use the `MLModelDeploymentService`, instantiate it. For full functionality, especially when interacting with a model registry or orchestrators, provide concrete client implementations.

```python
from core_ai_layer.machine_learning_service.ml_model_deployment_service import MLModelDeploymentService
# Assuming you have concrete implementations of these interfaces:
# from your_concrete_implementations import MyModelRegistryClient, MyContainerRegistryClient, MyOrchestratorClient

# model_registry_client = MyModelRegistryClient() # Optional
# container_registry_client = MyContainerRegistryClient() # Optional, for building/pushing images
# orchestrator_client = MyOrchestratorClient() # Optional, for deploying to K8s etc.

# deployment_service = MLModelDeploymentService(
#     model_registry_client=model_registry_client,
#     container_registry_client=container_registry_client, # If used
#     orchestrator_client=orchestrator_client # If used
# )
# For placeholder usage without external clients:
deployment_service = MLModelDeploymentService()
```

## 3. Core Functionalities

### 3.1. Deploying a Model

To deploy a trained model, call the `deploy_model` method with a `DeploymentRequest` object.

**Method:** `async deploy_model(request: DeploymentRequest) -> DeploymentStatusResponse`

**Request Schema (`DeploymentRequest` from `ml_models_schemas.py`):**

*   `model_uri: str`: URI of the trained model to deploy (e.g., from a model registry or a direct path).
*   `deployment_name: str`: A unique name for this deployment.
*   `deployment_target_config: DeploymentTargetConfig`: Configuration for the deployment target (e.g., type like "api_service", serving image, replicas).
*   `resource_allocation: Optional[ResourceConfig]`: (Optional) Resource requirements for the deployment (conceptual).
*   `tags: Optional[Dict[str, Any]]`: (Optional) Tags for the deployment.

**Response Schema (`DeploymentStatusResponse` from `ml_models_schemas.py`):**

Returns the initial status of the deployment, including a unique `deployment_id` and status "creating".

**Example:**

```python
# from core_ai_layer.machine_learning_service.ml_models_schemas import (
#     DeploymentRequest, DeploymentTargetConfig, ResourceConfig
# )
# import asyncio

# async def run_submit_deploy_example():
#     sample_target_config = DeploymentTargetConfig(
#         type="api_service",
#         serving_image="custom/my-model-server:v1.0",
#         replicas=2,
#         port=8080
#     )
#     deployment_request = DeploymentRequest(
#         model_uri="mlflow_runs:/<some_run_id>/my_model",
#         deployment_name="MyModelAPIService_Prod",
#         deployment_target_config=sample_target_config
#     )
#     try:
#         job_status = await deployment_service.deploy_model(deployment_request)
#         print(f"Submitted deployment ID: {job_status.deployment_id}, Name: {job_status.deployment_name}, Status: {job_status.status}")
#     except ConfigurationError as e:
#         print(f"Configuration Error: {e.message}")

# asyncio.run(run_submit_deploy_example())
```

### 3.2. Getting Deployment Status

Retrieve the current status of a specific deployment using its `deployment_id`.

**Method:** `async get_deployment_status(deployment_id: uuid.UUID) -> DeploymentStatusResponse`

**Response Schema (`DeploymentStatusResponse`):**

Contains detailed status, including `status` (e.g., "creating", "active", "failed", "inactive"), `message`, `endpoint_url` (if applicable), `deployed_model_version`, etc.

**Example:**

```python
# import uuid
# # Assuming deployment_id was obtained from deploy_model
# # target_deployment_id = uuid.UUID("your-deployment-id-here") 
# async def run_deploy_status_example(target_deployment_id):
#     try:
#         status = await deployment_service.get_deployment_status(target_deployment_id)
#         print(f"Deployment {status.deployment_id} Status: {status.status}")
#         if status.status == "active":
#             print(f"Endpoint URL: {status.endpoint_url}")
#             print(f"Deployed Model URI: {status.deployed_model_version}") # Note: field is model_uri in request, deployed_model_version in response
#         elif status.status == "failed":
#             print(f"Error Message: {status.message}")
#     except ResourceNotFoundError as e:
#         print(e.message)

# # To run: asyncio.run(run_deploy_status_example(target_deployment_id))
```

### 3.3. Listing Deployments

List all active (or otherwise tracked) deployments, with optional pagination.

**Method:** `async list_deployments(limit: int = 100, offset: int = 0) -> List[DeploymentStatusResponse]`

**Response:** A list of `DeploymentStatusResponse` objects.

**Example:**

```python
# async def run_list_deploy_example():
#     deployments = await deployment_service.list_deployments(limit=10)
#     print(f"Found {len(deployments)} deployments:")
#     for dep in deployments:
#         print(f"  ID: {dep.deployment_id}, Name: {dep.deployment_name}, Status: {dep.status}")

# # To run: asyncio.run(run_list_deploy_example())
```

### 3.4. Updating a Deployment

Update an existing deployment, for instance, to deploy a new model version or change resource allocation.

**Method:** `async update_deployment(deployment_id: uuid.UUID, request: DeploymentRequest) -> DeploymentStatusResponse`

**Request Schema (`DeploymentRequest`):** Similar to `deploy_model`, providing the new configuration.

**Response Schema (`DeploymentStatusResponse`):** The status of the deployment as it begins the update process (typically "updating").

**Example:**

```python
# # Assuming target_deployment_id exists
# # updated_target_config = DeploymentTargetConfig(...) 
# # updated_deployment_request = DeploymentRequest(
# #     model_uri="mlflow_runs:/<new_run_id>/my_model", 
# #     deployment_name="MyModelAPIService_Prod_V2", 
# #     deployment_target_config=updated_target_config
# # )
# async def run_update_deploy_example(target_deployment_id, updated_deployment_request):
#     try:
#         status = await deployment_service.update_deployment(target_deployment_id, updated_deployment_request)
#         print(f"Deployment {status.deployment_id} update initiated. Status: {status.status}")
#     except (ResourceNotFoundError, ConfigurationError) as e:
#         print(f"Error updating deployment: {e.message}")

# # To run: asyncio.run(run_update_deploy_example(target_deployment_id, updated_deployment_request))
```

### 3.5. Deleting a Deployment

Decommission and delete an active deployment.

**Method:** `async delete_deployment(deployment_id: uuid.UUID) -> DeploymentStatusResponse`

**Response Schema (`DeploymentStatusResponse`):** The status of the deployment as it undergoes deletion (e.g., "deleting", then "inactive" or a specific deleted status).

**Example:**

```python
# # Assuming target_deployment_id exists and is active
# async def run_delete_deploy_example(target_deployment_id):
#     try:
#         status = await deployment_service.delete_deployment(target_deployment_id)
#         print(f"Deployment {status.deployment_id} deletion process. Status: {status.status}")
#         # Poll get_deployment_status to confirm final inactive/deleted state
#     except ResourceNotFoundError as e:
#         print(e.message)

# # To run: asyncio.run(run_delete_deploy_example(target_deployment_id))
```

## 4. Asynchronous Job Execution (`_execute_deployment_job`)

This internal method, triggered by `deploy_model` or `update_deployment`, simulates the deployment pipeline:

1.  **Fetch Model Artifacts**: Simulates downloading model artifacts using the `ModelRegistryClient` (if provided and `model_uri` is a registry URI) or accessing them from a direct path.
2.  **Package Model for Serving**: Simulates packaging the model, potentially into a container image. This step might involve a `ContainerRegistryClient` in a real implementation.
3.  **Provision Deployment Target**: Simulates deploying the packaged model to the specified target (e.g., creating a Kubernetes service). This would involve an `OrchestratorClient` in a real system.

The `DeploymentStatusResponse` is updated throughout this process, reflecting status changes and the final endpoint URL if successful.

## 5. Error Handling

The service uses custom exceptions from `ml_service_exceptions.py`:

*   `ConfigurationError`: For invalid or missing request parameters.
*   `ResourceNotFoundError`: If a deployment ID is not found.
*   `ModelRegistryError`: If the `ModelRegistryClient` fails (e.g., downloading artifacts).
*   `ExternalServiceError`: For errors interacting with conceptual external services like container registries or orchestrators.
*   `DeploymentError`: For general errors during the deployment job execution.

Failed deployment operations will result in a "failed" (or e.g., "delete_failed") status in the `DeploymentStatusResponse`, with details in the `message` field.

## 6. Dependencies and Configuration

*   **Pydantic Schemas**: All data structures are defined in `ml_models_schemas.py`.
*   **Client Interfaces**: For full functionality, concrete implementations of `ModelRegistryClientInterface`, and potentially clients for container registries and orchestrators, should be passed during service initialization.
*   **Logging**: Uses standard Python logging. Configure the logger for `ml_model_deployment_service` to view logs.

This guide provides an overview of the `MLModelDeploymentService`. For precise details, consult the source code and Pydantic schema definitions.
