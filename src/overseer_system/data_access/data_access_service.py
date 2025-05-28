"""
Data Access Service for the Overseer System.

This service provides a database abstraction layer for all Overseer System components.
It handles CRUD operations, data validation, and ensures data integrity.
"""

import os
import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Generic, TypeVar
from uuid import UUID, uuid4

# Initialize FastAPI app
app = FastAPI(
    title="Overseer Data Access Service",
    description="Data access service for the Overseer System",
    version="1.0.0"
)

# Generic type for data models
T = TypeVar('T', bound=BaseModel)

# Base models
class Entity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class DataResponse(BaseModel, Generic[T]):
    data: T
    success: bool = True
    message: Optional[str] = None

class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# Mock database - would be replaced with actual database in production
data_stores: Dict[str, Dict[UUID, Any]] = {}

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    # In production, validate token with Auth Service
    return True

# Generic CRUD operations
def get_store(entity_type: str) -> Dict[UUID, Any]:
    if entity_type not in data_stores:
        data_stores[entity_type] = {}
    return data_stores[entity_type]

def create_entity(entity_type: str, entity: Entity) -> Entity:
    store = get_store(entity_type)
    store[entity.id] = entity
    return entity

def get_entity(entity_type: str, entity_id: UUID) -> Optional[Entity]:
    store = get_store(entity_type)
    return store.get(entity_id)

def update_entity(entity_type: str, entity_id: UUID, updates: Dict[str, Any]) -> Optional[Entity]:
    store = get_store(entity_type)
    entity = store.get(entity_id)
    if not entity:
        return None
    
    # Update fields
    for key, value in updates.items():
        if hasattr(entity, key):
            setattr(entity, key, value)
    
    # Update timestamp
    entity.updated_at = datetime.datetime.now()
    store[entity_id] = entity
    return entity

def delete_entity(entity_type: str, entity_id: UUID) -> bool:
    store = get_store(entity_type)
    if entity_id not in store:
        return False
    del store[entity_id]
    return True

def list_entities(entity_type: str, page: int = 1, page_size: int = 100) -> List[Entity]:
    store = get_store(entity_type)
    entities = list(store.values())
    
    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    return entities[start:end], len(entities)

# Routes
@app.post("/{entity_type}", response_model=DataResponse)
async def create_data(
    entity_type: str,
    entity: Dict[str, Any] = Body(...),
    _: bool = Depends(verify_token)
):
    """Create a new entity."""
    try:
        # Convert to Entity model
        entity_obj = Entity(**entity)
        result = create_entity(entity_type, entity_obj)
        return DataResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/{entity_type}/{entity_id}", response_model=DataResponse)
async def get_data(
    entity_type: str,
    entity_id: UUID,
    _: bool = Depends(verify_token)
):
    """Get an entity by ID."""
    entity = get_entity(entity_type, entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found in {entity_type}"
        )
    return DataResponse(data=entity)

@app.put("/{entity_type}/{entity_id}", response_model=DataResponse)
async def update_data(
    entity_type: str,
    entity_id: UUID,
    updates: Dict[str, Any] = Body(...),
    _: bool = Depends(verify_token)
):
    """Update an entity."""
    result = update_entity(entity_type, entity_id, updates)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found in {entity_type}"
        )
    return DataResponse(data=result)

@app.delete("/{entity_type}/{entity_id}", response_model=DataResponse)
async def delete_data(
    entity_type: str,
    entity_id: UUID,
    _: bool = Depends(verify_token)
):
    """Delete an entity."""
    success = delete_entity(entity_type, entity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found in {entity_type}"
        )
    return DataResponse(data={"id": entity_id}, message="Entity deleted successfully")

@app.get("/{entity_type}", response_model=ListResponse)
async def list_data(
    entity_type: str,
    page: int = 1,
    page_size: int = 100,
    _: bool = Depends(verify_token)
):
    """List entities with pagination."""
    entities, total = list_entities(entity_type, page, page_size)
    return ListResponse(
        data=entities,
        total=total,
        page=page,
        page_size=page_size
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
