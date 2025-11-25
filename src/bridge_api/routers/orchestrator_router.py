from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from src.bridge_api.models.orchestrator_models import ServicePackage, DeploymentRequest, DeploymentResponse
from src.bridge_api.services.orchestrator_service import OrchestratorService

router = APIRouter(
    prefix="/orchestrator",
    tags=["orchestrator"],
    responses={404: {"description": "Not found"}},
)

service = OrchestratorService()

@router.get("/packages", response_model=List[ServicePackage])
async def list_packages():
    """
    List all available Service Packages in the catalog.
    """
    return await service.list_packages()

@router.post("/deploy", response_model=DeploymentResponse)
async def deploy_package(request: DeploymentRequest):
    """
    Trigger the deployment (rehydration) of a specific service package.
    """
    try:
        return await service.deploy_package(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
