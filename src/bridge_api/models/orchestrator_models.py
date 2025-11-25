from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ServicePackage(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str
    required_resources: Dict[str, str]  # e.g., {"cpu": "2", "memory": "4Gi"}
    capabilities: List[str]  # e.g., ["widget:ai_shield", "api:inference"]
    monthly_cost_est: float

class DeploymentRequest(BaseModel):
    package_id: str
    tenant_id: str
    user_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class DeploymentResponse(BaseModel):
    deployment_id: str
    status: str
    message: str
    estimated_completion: str
