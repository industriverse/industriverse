"""
REST API for ASAL Integration and UX Genome Management.

This module exposes HTTP endpoints for genome collection, policy generation,
and ASAL distribution. Week 11 deliverable.

Endpoints:
- POST /api/v1/asal/genomes/collect - Collect evidence for genome extraction
- POST /api/v1/asal/genomes/extract - Extract UX genomes from evidence
- GET /api/v1/asal/genomes - List all discovered genomes
- GET /api/v1/asal/genomes/{genome_id} - Get specific genome
- POST /api/v1/asal/policies/generate - Generate GIPs from genomes
- POST /api/v1/asal/policies/distribute - Distribute policies via ASAL
- GET /api/v1/asal/policies - List all policies
- GET /api/v1/asal/policies/{policy_id} - Get specific policy
- POST /api/v1/asal/policies/{policy_id}/track - Track policy effectiveness
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

# Import ASAL integration components
from .ux_genome_collector import ux_genome_collector, UXGenome
from .asal_policy_generator import asal_policy_generator, GlobalInteractionPolicy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ASAL Integration API",
    description="REST API for UX genome collection and global policy distribution",
    version="1.0.0"
)


# Pydantic models
class EvidenceCollectionRequest(BaseModel):
    """Request to collect evidence for genome extraction."""
    user_id: str
    behavioral_vector: Dict[str, Any]
    ux_configuration: Dict[str, Any]
    effectiveness_metrics: Dict[str, float]


class GenomeExtractionRequest(BaseModel):
    """Request to extract genomes from collected evidence."""
    min_sample_size: int = Field(default=10, ge=5)
    min_confidence: float = Field(default=0.7, ge=0.5, le=1.0)


class GenomeResponse(BaseModel):
    """Response with genome information."""
    genome_id: str
    genome_type: str
    genome_name: str
    description: str
    user_archetype: str
    conditions: Dict[str, Any]
    ux_configuration: Dict[str, Any]
    sample_size: int
    confidence: float
    effectiveness_score: float
    discovered_at: str


class PolicyGenerationRequest(BaseModel):
    """Request to generate policies from genomes."""
    genome_ids: Optional[List[str]] = None  # None = all genomes
    validate: bool = True
    resolve_conflicts: bool = True


class PolicyDistributionRequest(BaseModel):
    """Request to distribute policies via ASAL."""
    policy_ids: Optional[List[str]] = None  # None = all policies


class PolicyResponse(BaseModel):
    """Response with policy information."""
    policy_id: str
    policy_name: str
    policy_type: str
    description: str
    trigger_conditions: Dict[str, Any]
    ux_actions: Dict[str, Any]
    priority: int
    confidence: float
    effectiveness: float
    source_genome_id: str
    version: str
    distributed_at: Optional[str]
    devices_applied: int


class PolicyEffectivenessRequest(BaseModel):
    """Request to track policy effectiveness."""
    effectiveness_metrics: Dict[str, float]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "asal-integration-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/asal/genomes/collect")
async def collect_evidence(request: EvidenceCollectionRequest):
    """
    Collect evidence from a user's interaction for genome extraction.
    
    This endpoint should be called after each UX adjustment to build
    the evidence base for pattern extraction.
    """
    try:
        await ux_genome_collector.collect_evidence(
            user_id=request.user_id,
            behavioral_vector=request.behavioral_vector,
            ux_configuration=request.ux_configuration,
            effectiveness_metrics=request.effectiveness_metrics
        )
        
        # Get current evidence count by archetype
        archetype = request.behavioral_vector.get("expertise_level", "unknown")
        evidence_count = len(ux_genome_collector.evidence.get(archetype, []))
        
        return {
            "success": True,
            "message": "Evidence collected",
            "archetype": archetype,
            "evidence_count": evidence_count
        }
    
    except Exception as e:
        logger.error(f"Error collecting evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/asal/genomes/extract")
async def extract_genomes(request: GenomeExtractionRequest):
    """
    Extract UX genomes from collected evidence.
    
    This endpoint analyzes all collected evidence and identifies
    common patterns across user archetypes.
    """
    try:
        genomes = await ux_genome_collector.extract_patterns(
            min_sample_size=request.min_sample_size,
            min_confidence=request.min_confidence
        )
        
        return {
            "success": True,
            "genomes_discovered": len(genomes),
            "genomes": [
                {
                    "genome_id": g.genome_id,
                    "genome_type": g.genome_type,
                    "genome_name": g.genome_name,
                    "user_archetype": g.user_archetype,
                    "sample_size": g.sample_size,
                    "confidence": g.confidence,
                    "effectiveness_score": g.effectiveness_score
                }
                for g in genomes
            ]
        }
    
    except Exception as e:
        logger.error(f"Error extracting genomes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/asal/genomes")
async def list_genomes(
    archetype: Optional[str] = None,
    genome_type: Optional[str] = None
):
    """
    List all discovered UX genomes.
    
    Optional filters:
    - archetype: Filter by user archetype
    - genome_type: Filter by genome type
    """
    try:
        genomes = ux_genome_collector.get_all_genomes()
        
        # Apply filters
        if archetype:
            genomes = [g for g in genomes if g.user_archetype == archetype]
        
        if genome_type:
            genomes = [g for g in genomes if g.genome_type == genome_type]
        
        return {
            "total_genomes": len(genomes),
            "genomes": [
                GenomeResponse(
                    genome_id=g.genome_id,
                    genome_type=g.genome_type,
                    genome_name=g.genome_name,
                    description=g.description,
                    user_archetype=g.user_archetype,
                    conditions=g.conditions,
                    ux_configuration=g.ux_configuration,
                    sample_size=g.sample_size,
                    confidence=g.confidence,
                    effectiveness_score=g.effectiveness_score,
                    discovered_at=g.discovered_at
                )
                for g in genomes
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing genomes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/asal/genomes/{genome_id}")
async def get_genome(genome_id: str):
    """Get details of a specific genome."""
    try:
        genome = ux_genome_collector.get_genome(genome_id)
        
        if not genome:
            raise HTTPException(status_code=404, detail="Genome not found")
        
        return GenomeResponse(
            genome_id=genome.genome_id,
            genome_type=genome.genome_type,
            genome_name=genome.genome_name,
            description=genome.description,
            user_archetype=genome.user_archetype,
            conditions=genome.conditions,
            ux_configuration=genome.ux_configuration,
            sample_size=genome.sample_size,
            confidence=genome.confidence,
            effectiveness_score=genome.effectiveness_score,
            discovered_at=genome.discovered_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting genome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/asal/policies/generate")
async def generate_policies(request: PolicyGenerationRequest):
    """
    Generate Global Interaction Policies (GIPs) from UX genomes.
    
    This endpoint converts genomes into distributable policies.
    """
    try:
        # Get genomes to process
        if request.genome_ids:
            genomes = [
                ux_genome_collector.get_genome(gid)
                for gid in request.genome_ids
            ]
            genomes = [g for g in genomes if g is not None]
        else:
            genomes = ux_genome_collector.get_all_genomes()
        
        if not genomes:
            return {
                "success": False,
                "message": "No genomes available for policy generation"
            }
        
        # Export genomes in ASAL format
        asal_genomes = await ux_genome_collector.export_genomes_for_asal()
        
        # Generate policies
        policies = await asal_policy_generator.generate_policies_from_genomes(
            asal_genomes
        )
        
        # Validate policies
        validation_report = None
        if request.validate:
            validation_report = await asal_policy_generator.validate_policy_consistency(
                policies
            )
            
            # Resolve conflicts if requested
            if request.resolve_conflicts and not validation_report["valid"]:
                policies = await asal_policy_generator.resolve_conflicts(
                    policies,
                    validation_report
                )
        
        return {
            "success": True,
            "policies_generated": len(policies),
            "validation_report": validation_report,
            "policies": [
                {
                    "policy_id": p.policy_id,
                    "policy_name": p.policy_name,
                    "policy_type": p.policy_type,
                    "priority": p.priority,
                    "confidence": p.confidence,
                    "source_genome_id": p.source_genome_id
                }
                for p in policies
            ]
        }
    
    except Exception as e:
        logger.error(f"Error generating policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/asal/policies/distribute")
async def distribute_policies(request: PolicyDistributionRequest):
    """
    Distribute policies to all devices via ASAL.
    
    This endpoint pushes policies to ASAL for global distribution.
    """
    try:
        # Get policies to distribute
        if request.policy_ids:
            policies = [
                asal_policy_generator.get_policy(pid)
                for pid in request.policy_ids
            ]
            policies = [p for p in policies if p is not None]
        else:
            policies = asal_policy_generator.get_all_policies()
        
        if not policies:
            return {
                "success": False,
                "message": "No policies available for distribution"
            }
        
        # Distribute policies
        results = await asal_policy_generator.distribute_all_policies(policies)
        
        total_devices = sum(r.devices_applied for r in results)
        total_failed = sum(r.devices_failed for r in results)
        
        return {
            "success": True,
            "policies_distributed": len(results),
            "total_devices_reached": sum(r.devices_reached for r in results),
            "total_devices_applied": total_devices,
            "total_devices_failed": total_failed,
            "success_rate": total_devices / (total_devices + total_failed) if (total_devices + total_failed) > 0 else 0,
            "results": [
                {
                    "policy_id": r.policy_id,
                    "devices_reached": r.devices_reached,
                    "devices_applied": r.devices_applied,
                    "devices_failed": r.devices_failed,
                    "distribution_time_ms": r.distribution_time_ms
                }
                for r in results
            ]
        }
    
    except Exception as e:
        logger.error(f"Error distributing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/asal/policies")
async def list_policies(
    policy_type: Optional[str] = None,
    min_confidence: Optional[float] = None
):
    """
    List all generated policies.
    
    Optional filters:
    - policy_type: Filter by policy type
    - min_confidence: Filter by minimum confidence
    """
    try:
        policies = asal_policy_generator.get_all_policies()
        
        # Apply filters
        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]
        
        if min_confidence:
            policies = [p for p in policies if p.confidence >= min_confidence]
        
        return {
            "total_policies": len(policies),
            "policies": [
                PolicyResponse(
                    policy_id=p.policy_id,
                    policy_name=p.policy_name,
                    policy_type=p.policy_type,
                    description=p.description,
                    trigger_conditions=p.trigger_conditions,
                    ux_actions=p.ux_actions,
                    priority=p.priority,
                    confidence=p.confidence,
                    effectiveness=p.effectiveness,
                    source_genome_id=p.source_genome_id,
                    version=p.version,
                    distributed_at=p.distributed_at,
                    devices_applied=p.devices_applied
                )
                for p in policies
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/asal/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get details of a specific policy."""
    try:
        policy = asal_policy_generator.get_policy(policy_id)
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return PolicyResponse(
            policy_id=policy.policy_id,
            policy_name=policy.policy_name,
            policy_type=policy.policy_type,
            description=policy.description,
            trigger_conditions=policy.trigger_conditions,
            ux_actions=policy.ux_actions,
            priority=policy.priority,
            confidence=policy.confidence,
            effectiveness=policy.effectiveness,
            source_genome_id=policy.source_genome_id,
            version=policy.version,
            distributed_at=policy.distributed_at,
            devices_applied=policy.devices_applied
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/asal/policies/{policy_id}/track")
async def track_policy_effectiveness(
    policy_id: str,
    request: PolicyEffectivenessRequest
):
    """
    Track effectiveness of a distributed policy.
    
    Devices should call this endpoint to report how well a policy
    is performing in production.
    """
    try:
        await asal_policy_generator.track_policy_effectiveness(
            policy_id=policy_id,
            effectiveness_metrics=request.effectiveness_metrics
        )
        
        policy = asal_policy_generator.get_policy(policy_id)
        
        return {
            "success": True,
            "policy_id": policy_id,
            "updated_effectiveness": policy.effectiveness if policy else None
        }
    
    except Exception as e:
        logger.error(f"Error tracking policy effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
