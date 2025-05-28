"""
Trust Verification Engine for the Overseer System.

This module provides comprehensive trust verification capabilities for entities
within the Overseer System ecosystem. It verifies trust claims, validates credentials,
and enforces trust policies based on configurable rules and verification methods.

The Trust Verification Engine is a critical component of the Trust Management framework,
providing robust mechanisms for establishing and verifying trust in the system.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any

import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field

# Import MCP/A2A integration
from ..mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from ..a2a_integration.a2a_protocol_bridge import A2AProtocolBridge

# Import event bus
from ..event_bus.kafka_client import KafkaProducer, KafkaConsumer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("trust_verification_engine")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="trust-verification-engine"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="trust-verification-engine",
    auto_offset_reset="earliest"
)

# Data models
class VerificationRequest(BaseModel):
    """Model for trust verification requests."""
    entity_id: str = Field(..., description="Entity ID to verify")
    verification_type: str = Field(..., description="Type of verification to perform")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Credentials to verify")
    context: Dict[str, Any] = Field(default_factory=dict, description="Verification context")
    required_trust_level: float = Field(0.7, description="Minimum required trust level", ge=0.0, le=1.0)
    verification_methods: Optional[List[str]] = Field(None, description="Specific verification methods to use")
    callback_url: Optional[str] = Field(None, description="URL to call with verification results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VerificationResult(BaseModel):
    """Model for trust verification results."""
    verification_id: str = Field(..., description="Unique verification identifier")
    entity_id: str = Field(..., description="Entity ID that was verified")
    verification_type: str = Field(..., description="Type of verification performed")
    verified: bool = Field(..., description="Whether the entity is verified")
    trust_score: float = Field(..., description="Trust score after verification", ge=0.0, le=1.0)
    confidence: float = Field(..., description="Confidence in the verification result", ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now, description="Verification timestamp")
    expiration: Optional[datetime] = Field(None, description="Expiration timestamp for the verification")
    verification_methods: List[str] = Field(default_factory=list, description="Methods used for verification")
    details: Dict[str, Any] = Field(default_factory=dict, description="Verification details")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VerificationMethod(BaseModel):
    """Model for trust verification methods."""
    method_id: str = Field(..., description="Unique method identifier")
    name: str = Field(..., description="Human-readable method name")
    description: str = Field(..., description="Method description")
    verification_types: List[str] = Field(..., description="Verification types this method supports")
    required_credentials: List[str] = Field(default_factory=list, description="Required credentials for this method")
    confidence_level: float = Field(..., description="Base confidence level for this method", ge=0.0, le=1.0)
    enabled: bool = Field(True, description="Whether this method is enabled")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TrustClaim(BaseModel):
    """Model for trust claims made by entities."""
    claim_id: str = Field(..., description="Unique claim identifier")
    entity_id: str = Field(..., description="Entity making the claim")
    claim_type: str = Field(..., description="Type of claim")
    claim_value: Any = Field(..., description="Value of the claim")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Evidence supporting the claim")
    timestamp: datetime = Field(default_factory=datetime.now, description="Claim timestamp")
    expiration: Optional[datetime] = Field(None, description="Expiration timestamp for the claim")
    signature: Optional[str] = Field(None, description="Digital signature of the claim")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
verification_results = {}
verification_methods = {}
trust_claims = {}

class TrustVerificationEngine:
    """
    Trust Verification Engine implementation for the Overseer System.
    
    This class provides methods for verifying trust in entities, including:
    - Verifying credentials and claims
    - Applying verification methods
    - Managing verification results
    - Handling trust claims
    """
    
    def __init__(self):
        """Initialize the Trust Verification Engine."""
        self._initialize_default_verification_methods()
        logger.info("Trust Verification Engine initialized")
    
    def _initialize_default_verification_methods(self):
        """Initialize default verification methods."""
        default_methods = [
            VerificationMethod(
                method_id="credential_verification",
                name="Credential Verification",
                description="Verifies entity credentials against trusted sources",
                verification_types=["identity", "access", "authorization"],
                required_credentials=["certificate", "token"],
                confidence_level=0.8
            ),
            VerificationMethod(
                method_id="reputation_check",
                name="Reputation Check",
                description="Verifies entity based on reputation score",
                verification_types=["identity", "reliability", "performance"],
                required_credentials=[],
                confidence_level=0.7
            ),
            VerificationMethod(
                method_id="behavioral_analysis",
                name="Behavioral Analysis",
                description="Verifies entity based on behavioral patterns",
                verification_types=["identity", "security", "anomaly"],
                required_credentials=["activity_log"],
                confidence_level=0.75
            ),
            VerificationMethod(
                method_id="multi_factor_verification",
                name="Multi-Factor Verification",
                description="Verifies entity using multiple factors",
                verification_types=["identity", "access", "security"],
                required_credentials=["token", "biometric", "location"],
                confidence_level=0.9
            ),
            VerificationMethod(
                method_id="zero_knowledge_proof",
                name="Zero-Knowledge Proof",
                description="Verifies entity using zero-knowledge proofs",
                verification_types=["identity", "authorization", "compliance"],
                required_credentials=["zk_proof"],
                confidence_level=0.95
            ),
            VerificationMethod(
                method_id="consensus_verification",
                name="Consensus Verification",
                description="Verifies entity through consensus of trusted entities",
                verification_types=["identity", "reliability", "performance"],
                required_credentials=["endorsements"],
                confidence_level=0.85
            )
        ]
        
        for method in default_methods:
            verification_methods[method.method_id] = method.dict()
    
    def verify(self, request: VerificationRequest) -> VerificationResult:
        """
        Verify trust for an entity.
        
        Args:
            request: The verification request
            
        Returns:
            VerificationResult: The verification result
        """
        entity_id = request.entity_id
        verification_id = f"verify-{uuid.uuid4()}"
        
        # Determine which verification methods to use
        methods_to_use = []
        if request.verification_methods:
            # Use specified methods if provided
            for method_id in request.verification_methods:
                if method_id in verification_methods and verification_methods[method_id]["enabled"]:
                    if request.verification_type in verification_methods[method_id]["verification_types"]:
                        methods_to_use.append(method_id)
        else:
            # Otherwise, use all applicable methods
            for method_id, method_data in verification_methods.items():
                if method_data["enabled"] and request.verification_type in method_data["verification_types"]:
                    methods_to_use.append(method_id)
        
        if not methods_to_use:
            # No applicable methods found
            result = VerificationResult(
                verification_id=verification_id,
                entity_id=entity_id,
                verification_type=request.verification_type,
                verified=False,
                trust_score=0.0,
                confidence=0.0,
                verification_methods=[],
                details={"error": "No applicable verification methods found"}
            )
        else:
            # Apply each verification method
            method_results = []
            for method_id in methods_to_use:
                method_result = self._apply_verification_method(
                    method_id, entity_id, request.verification_type, 
                    request.credentials, request.context
                )
                method_results.append(method_result)
            
            # Combine results
            verified = all(result["verified"] for result in method_results)
            
            # Calculate weighted average of trust scores
            total_confidence = sum(result["confidence"] for result in method_results)
            if total_confidence > 0:
                trust_score = sum(
                    result["trust_score"] * result["confidence"] 
                    for result in method_results
                ) / total_confidence
                confidence = total_confidence / len(method_results)
            else:
                trust_score = 0.0
                confidence = 0.0
            
            # Create verification result
            result = VerificationResult(
                verification_id=verification_id,
                entity_id=entity_id,
                verification_type=request.verification_type,
                verified=verified and trust_score >= request.required_trust_level,
                trust_score=trust_score,
                confidence=confidence,
                verification_methods=methods_to_use,
                details={
                    "method_results": method_results,
                    "required_trust_level": request.required_trust_level
                },
                metadata=request.metadata
            )
            
            # Set expiration if applicable
            if request.verification_type in ["access", "authorization"]:
                result.expiration = datetime.now() + timedelta(hours=24)
        
        # Store the result
        verification_results[verification_id] = result.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="verification-events",
            key=entity_id,
            value=json.dumps({
                "event_type": "trust_verification",
                "entity_id": entity_id,
                "verification_id": verification_id,
                "verified": result.verified,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "trust_verification_completed",
            "entity_id": entity_id,
            "verification_id": verification_id,
            "verified": result.verified,
            "trust_score": result.trust_score
        }
        mcp_bridge.send_context_update("trust_verification_engine", mcp_context)
        
        # Call callback URL if provided
        if request.callback_url:
            # In a real implementation, this would make an HTTP request to the callback URL
            logger.info(f"Would call callback URL: {request.callback_url}")
        
        return result
    
    def _apply_verification_method(
        self, method_id: str, entity_id: str, verification_type: str, 
        credentials: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply a verification method to an entity.
        
        Args:
            method_id: The verification method ID
            entity_id: The entity ID
            verification_type: The type of verification
            credentials: The credentials to verify
            context: The verification context
            
        Returns:
            Dict[str, Any]: The method result
        """
        method_data = verification_methods[method_id]
        
        # Check if required credentials are provided
        missing_credentials = [
            cred for cred in method_data["required_credentials"]
            if cred not in credentials
        ]
        
        if missing_credentials:
            return {
                "method_id": method_id,
                "verified": False,
                "trust_score": 0.0,
                "confidence": method_data["confidence_level"] * 0.5,  # Reduced confidence due to missing credentials
                "details": {
                    "error": "Missing required credentials",
                    "missing": missing_credentials
                }
            }
        
        # Apply method-specific verification logic
        # (In a real implementation, this would have specific logic for each method)
        if method_id == "credential_verification":
            result = self._verify_credentials(entity_id, credentials, context)
        elif method_id == "reputation_check":
            result = self._check_reputation(entity_id, context)
        elif method_id == "behavioral_analysis":
            result = self._analyze_behavior(entity_id, credentials, context)
        elif method_id == "multi_factor_verification":
            result = self._verify_multi_factor(entity_id, credentials, context)
        elif method_id == "zero_knowledge_proof":
            result = self._verify_zero_knowledge(entity_id, credentials, context)
        elif method_id == "consensus_verification":
            result = self._verify_consensus(entity_id, credentials, context)
        else:
            # Default implementation for unknown methods
            # In a real system, this would be more sophisticated
            import random
            result = {
                "verified": random.random() > 0.2,  # 80% chance of success for demo
                "trust_score": 0.5 + random.random() * 0.5,  # Random score between 0.5 and 1.0
                "confidence": method_data["confidence_level"],
                "details": {
                    "note": "Default implementation for demonstration purposes"
                }
            }
        
        # Add method ID to result
        result["method_id"] = method_id
        
        return result
    
    def _verify_credentials(self, entity_id: str, credentials: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify entity credentials."""
        # In a real implementation, this would verify certificates, tokens, etc.
        # For demonstration, we'll implement a simple token verification
        
        if "token" in credentials:
            token = credentials["token"]
            try:
                # In a real implementation, this would use proper JWT verification
                # with appropriate keys and algorithms
                secret = "demo_secret_key"  # Would be properly secured in production
                payload = jwt.decode(token, secret, algorithms=["HS256"])
                
                if payload["entity_id"] == entity_id and payload["exp"] > time.time():
                    return {
                        "verified": True,
                        "trust_score": 0.9,
                        "confidence": 0.8,
                        "details": {
                            "token_valid": True,
                            "token_type": payload.get("type", "unknown")
                        }
                    }
            except Exception as e:
                return {
                    "verified": False,
                    "trust_score": 0.1,
                    "confidence": 0.8,
                    "details": {
                        "token_valid": False,
                        "error": str(e)
                    }
                }
        
        if "certificate" in credentials:
            # In a real implementation, this would verify X.509 certificates
            # For demonstration, we'll assume a simple structure
            cert = credentials["certificate"]
            if isinstance(cert, dict) and "subject" in cert and "issuer" in cert:
                if cert["subject"] == entity_id and cert["issuer"] in ["trusted_ca_1", "trusted_ca_2"]:
                    return {
                        "verified": True,
                        "trust_score": 0.95,
                        "confidence": 0.9,
                        "details": {
                            "certificate_valid": True,
                            "issuer": cert["issuer"]
                        }
                    }
        
        return {
            "verified": False,
            "trust_score": 0.2,
            "confidence": 0.8,
            "details": {
                "error": "Invalid or insufficient credentials"
            }
        }
    
    def _check_reputation(self, entity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check entity reputation."""
        # In a real implementation, this would query the Reputation System
        # For demonstration, we'll use a simple random score
        
        import random
        reputation_score = 0.5 + random.random() * 0.5  # Random score between 0.5 and 1.0
        
        return {
            "verified": reputation_score >= 0.7,
            "trust_score": reputation_score,
            "confidence": 0.7,
            "details": {
                "reputation_score": reputation_score,
                "threshold": 0.7
            }
        }
    
    def _analyze_behavior(self, entity_id: str, credentials: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze entity behavior."""
        # In a real implementation, this would analyze behavioral patterns
        # For demonstration, we'll use a simple check of activity logs
        
        if "activity_log" in credentials:
            activity_log = credentials["activity_log"]
            if isinstance(activity_log, list) and len(activity_log) > 0:
                # Simple analysis: check for suspicious activities
                suspicious_count = sum(1 for entry in activity_log if entry.get("suspicious", False))
                suspicious_ratio = suspicious_count / len(activity_log)
                
                trust_score = 1.0 - suspicious_ratio
                
                return {
                    "verified": trust_score >= 0.8,
                    "trust_score": trust_score,
                    "confidence": 0.75,
                    "details": {
                        "activity_count": len(activity_log),
                        "suspicious_count": suspicious_count,
                        "suspicious_ratio": suspicious_ratio
                    }
                }
        
        return {
            "verified": False,
            "trust_score": 0.3,
            "confidence": 0.5,
            "details": {
                "error": "Insufficient activity data for behavioral analysis"
            }
        }
    
    def _verify_multi_factor(self, entity_id: str, credentials: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify entity using multiple factors."""
        # In a real implementation, this would verify multiple authentication factors
        # For demonstration, we'll check for token, biometric, and location
        
        factors_verified = 0
        total_factors = 3
        details = {}
        
        if "token" in credentials:
            # Simple token check
            token_valid = isinstance(credentials["token"], str) and len(credentials["token"]) > 10
            factors_verified += 1 if token_valid else 0
            details["token_verified"] = token_valid
        
        if "biometric" in credentials:
            # Simple biometric check
            biometric_valid = isinstance(credentials["biometric"], dict) and "score" in credentials["biometric"]
            if biometric_valid:
                biometric_score = credentials["biometric"]["score"]
                biometric_valid = biometric_score >= 0.9
            factors_verified += 1 if biometric_valid else 0
            details["biometric_verified"] = biometric_valid
        
        if "location" in credentials:
            # Simple location check
            location_valid = isinstance(credentials["location"], dict) and "latitude" in credentials["location"] and "longitude" in credentials["location"]
            factors_verified += 1 if location_valid else 0
            details["location_verified"] = location_valid
        
        trust_score = factors_verified / total_factors
        
        return {
            "verified": factors_verified >= 2,  # At least 2 factors required
            "trust_score": trust_score,
            "confidence": 0.9,
            "details": details
        }
    
    def _verify_zero_knowledge(self, entity_id: str, credentials: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify entity using zero-knowledge proofs."""
        # In a real implementation, this would verify zero-knowledge proofs
        # For demonstration, we'll use a simple check
        
        if "zk_proof" in credentials:
            zk_proof = credentials["zk_proof"]
            if isinstance(zk_proof, dict) and "proof" in zk_proof and "public_inputs" in zk_proof:
                # In a real implementation, this would verify the proof cryptographically
                # For demonstration, we'll assume it's valid
                return {
                    "verified": True,
                    "trust_score": 0.95,
                    "confidence": 0.95,
                    "details": {
                        "proof_valid": True,
                        "proof_type": zk_proof.get("type", "unknown")
                    }
                }
        
        return {
            "verified": False,
            "trust_score": 0.1,
            "confidence": 0.95,
            "details": {
                "error": "Invalid or missing zero-knowledge proof"
            }
        }
    
    def _verify_consensus(self, entity_id: str, credentials: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify entity through consensus of trusted entities."""
        # In a real implementation, this would verify endorsements from trusted entities
        # For demonstration, we'll use a simple check
        
        if "endorsements" in credentials:
            endorsements = credentials["endorsements"]
            if isinstance(endorsements, list) and len(endorsements) > 0:
                valid_endorsements = 0
                total_endorsements = len(endorsements)
                
                for endorsement in endorsements:
                    if isinstance(endorsement, dict) and "endorser_id" in endorsement and "signature" in endorsement:
                        # In a real implementation, this would verify the signature
                        # For demonstration, we'll assume it's valid if from a trusted endorser
                        trusted_endorsers = ["trusted_entity_1", "trusted_entity_2", "trusted_entity_3"]
                        if endorsement["endorser_id"] in trusted_endorsers:
                            valid_endorsements += 1
                
                trust_score = valid_endorsements / max(1, total_endorsements)
                
                return {
                    "verified": valid_endorsements >= 2,  # At least 2 valid endorsements required
                    "trust_score": trust_score,
                    "confidence": 0.85,
                    "details": {
                        "total_endorsements": total_endorsements,
                        "valid_endorsements": valid_endorsements,
                        "endorsement_ratio": trust_score
                    }
                }
        
        return {
            "verified": False,
            "trust_score": 0.1,
            "confidence": 0.85,
            "details": {
                "error": "Insufficient endorsements for consensus verification"
            }
        }
    
    def get_verification_result(self, verification_id: str) -> Optional[VerificationResult]:
        """
        Get a verification result by ID.
        
        Args:
            verification_id: The verification ID
            
        Returns:
            Optional[VerificationResult]: The verification result, or None if not found
        """
        if verification_id not in verification_results:
            return None
        
        return VerificationResult(**verification_results[verification_id])
    
    def add_verification_method(self, method: VerificationMethod) -> str:
        """
        Add a new verification method.
        
        Args:
            method: The verification method to add
            
        Returns:
            str: Method ID
        """
        method_dict = method.dict()
        verification_methods[method.method_id] = method_dict
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="verification-events",
            key=method.method_id,
            value=json.dumps({
                "event_type": "verification_method_added",
                "method_id": method.method_id,
                "name": method.name,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return method.method_id
    
    def get_verification_method(self, method_id: str) -> Optional[VerificationMethod]:
        """
        Get a verification method by ID.
        
        Args:
            method_id: The method ID
            
        Returns:
            Optional[VerificationMethod]: The verification method, or None if not found
        """
        if method_id not in verification_methods:
            return None
        
        return VerificationMethod(**verification_methods[method_id])
    
    def list_verification_methods(self) -> List[VerificationMethod]:
        """
        List all verification methods.
        
        Returns:
            List[VerificationMethod]: List of all verification methods
        """
        return [VerificationMethod(**method_data) for method_data in verification_methods.values()]
    
    def register_trust_claim(self, claim: TrustClaim) -> str:
        """
        Register a trust claim.
        
        Args:
            claim: The trust claim to register
            
        Returns:
            str: Claim ID
        """
        claim_dict = claim.dict()
        
        # Generate claim ID if not provided
        if not claim.claim_id:
            claim_dict["claim_id"] = f"claim-{uuid.uuid4()}"
        
        # Store the claim
        trust_claims[claim_dict["claim_id"]] = claim_dict
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="trust-events",
            key=claim.entity_id,
            value=json.dumps({
                "event_type": "trust_claim_registered",
                "entity_id": claim.entity_id,
                "claim_id": claim_dict["claim_id"],
                "claim_type": claim.claim_type,
                "timestamp": datetime.now().isoformat()
            })
        )
        
        return claim_dict["claim_id"]
    
    def verify_trust_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Verify a trust claim.
        
        Args:
            claim_id: The claim ID
            
        Returns:
            Dict[str, Any]: Verification result
        """
        if claim_id not in trust_claims:
            return {
                "verified": False,
                "error": "Claim not found"
            }
        
        claim = trust_claims[claim_id]
        
        # Check if claim has expired
        if "expiration" in claim and claim["expiration"]:
            expiration = datetime.fromisoformat(claim["expiration"])
            if expiration < datetime.now():
                return {
                    "verified": False,
                    "error": "Claim has expired",
                    "expiration": expiration.isoformat()
                }
        
        # Verify claim signature if present
        if "signature" in claim and claim["signature"]:
            # In a real implementation, this would verify the signature cryptographically
            # For demonstration, we'll assume it's valid
            signature_valid = True
        else:
            signature_valid = False
        
        # Verify claim evidence if present
        evidence_valid = False
        if "evidence" in claim and claim["evidence"]:
            # In a real implementation, this would verify the evidence
            # For demonstration, we'll assume it's valid if it has certain fields
            evidence = claim["evidence"]
            if isinstance(evidence, dict) and "source" in evidence and "timestamp" in evidence:
                evidence_valid = True
        
        # Determine overall verification result
        verified = signature_valid and evidence_valid
        
        return {
            "verified": verified,
            "claim_id": claim_id,
            "entity_id": claim["entity_id"],
            "claim_type": claim["claim_type"],
            "signature_valid": signature_valid,
            "evidence_valid": evidence_valid,
            "timestamp": datetime.now().isoformat()
        }

# Create singleton instance
trust_verification_engine = TrustVerificationEngine()

# API endpoints (if this were a standalone service)
app = FastAPI(
    title="Trust Verification Engine",
    description="Trust Verification Engine for the Overseer System",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trust_verification_engine", "timestamp": datetime.now().isoformat()}

@app.post("/verify")
async def verify_trust(request: VerificationRequest):
    """Verify trust for an entity."""
    result = trust_verification_engine.verify(request)
    return result

@app.get("/verifications/{verification_id}")
async def get_verification(verification_id: str):
    """Get a verification result by ID."""
    result = trust_verification_engine.get_verification_result(verification_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Verification result {verification_id} not found")
    return result

@app.post("/methods")
async def create_verification_method(method: VerificationMethod):
    """Create a new verification method."""
    method_id = trust_verification_engine.add_verification_method(method)
    return {"method_id": method_id, "status": "created"}

@app.get("/methods")
async def list_methods():
    """List all verification methods."""
    methods = trust_verification_engine.list_verification_methods()
    return {"methods": methods, "count": len(methods)}

@app.get("/methods/{method_id}")
async def get_method(method_id: str):
    """Get a verification method by ID."""
    method = trust_verification_engine.get_verification_method(method_id)
    if not method:
        raise HTTPException(status_code=404, detail=f"Verification method {method_id} not found")
    return method

@app.post("/claims")
async def register_claim(claim: TrustClaim):
    """Register a trust claim."""
    claim_id = trust_verification_engine.register_trust_claim(claim)
    return {"claim_id": claim_id, "status": "registered"}

@app.get("/claims/{claim_id}/verify")
async def verify_claim(claim_id: str):
    """Verify a trust claim."""
    result = trust_verification_engine.verify_trust_claim(claim_id)
    return result

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Trust Verification Engine starting up")
    
    # Subscribe to relevant Kafka topics
    kafka_consumer.subscribe(["entity-events", "trust-events"])
    
    logger.info("Trust Verification Engine started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Trust Verification Engine shutting down")
    
    # Close Kafka connections
    kafka_producer.close()
    kafka_consumer.close()
    
    logger.info("Trust Verification Engine shut down successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
