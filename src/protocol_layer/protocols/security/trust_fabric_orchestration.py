"""
Trust Fabric Orchestration for Industriverse Protocol Layer

This module implements the Trust Fabric Orchestration, providing a decentralized
and dynamic trust management system for the Industriverse protocol mesh.

Features:
1. Decentralized Identity Management (DID)
2. Verifiable Credentials (VC) issuance and verification
3. Reputation tracking and scoring
4. Policy enforcement based on trust levels
5. Secure key management and rotation
6. Audit logging for trust-related events
7. Integration with Cross-Mesh Federation for inter-mesh trust
"""

import uuid
import time
import asyncio
import logging
import json
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'
)
logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Levels of trust for protocol components."""
    UNKNOWN = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAXIMUM = 4


class CredentialType(Enum):
    """Types of verifiable credentials."""
    IDENTITY = "identity"
    CAPABILITY = "capability"
    MEMBERSHIP = "membership"
    REPUTATION = "reputation"
    CUSTOM = "custom"


@dataclass
class DecentralizedIdentity:
    """
    Represents a Decentralized Identity (DID) for a protocol component.
    """
    did: str  # e.g., did:industriverse:component:<uuid>
    public_key_pem: str
    private_key_pem: Optional[str] = None  # Only stored locally for the component itself
    creation_date: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self, include_private_key: bool = False) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = {
            "did": self.did,
            "public_key_pem": self.public_key_pem,
            "creation_date": self.creation_date,
            "metadata": self.metadata
        }
        if include_private_key and self.private_key_pem:
            data["private_key_pem"] = self.private_key_pem
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'DecentralizedIdentity\':
        """Create from dictionary representation."""
        return cls(
            did=data["did"],
            public_key_pem=data["public_key_pem"],
            private_key_pem=data.get("private_key_pem"),
            creation_date=data.get("creation_date", time.time()),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def generate(cls, component_id: str, metadata: Dict[str, Any] = None) -> \'DecentralizedIdentity\':
        """Generate a new DID with RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode(\'utf-8\')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode(\'utf-8\')
        
        did = f"did:industriverse:component:{component_id}"
        
        return cls(
            did=did,
            public_key_pem=public_pem,
            private_key_pem=private_pem,
            metadata=metadata or {}
        )
    
    def sign(self, data: bytes) -> bytes:
        """Sign data using the private key."""
        if not self.private_key_pem:
            raise ValueError("Private key not available for signing")
        
        private_key = serialization.load_pem_private_key(
            self.private_key_pem.encode(\'utf-8\'),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify a signature using the public key."""
        public_key = serialization.load_pem_public_key(
            self.public_key_pem.encode(\'utf-8\'),
            backend=default_backend()
        )
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


@dataclass
class VerifiableCredential:
    """
    Represents a Verifiable Credential (VC).
    """
    id: str
    type: List[str]  # e.g., ["VerifiableCredential", "IdentityCredential"]
    issuer: str  # DID of the issuer
    issuance_date: float
    credential_subject: Dict[str, Any]  # Claims about the subject
    proof: Dict[str, Any]  # Signature proof
    expiration_date: Optional[float] = None
    credential_schema: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": self.id,
            "type": self.type,
            "issuer": self.issuer,
            "issuanceDate": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.issuance_date)),
            "credentialSubject": self.credential_subject,
            "proof": self.proof,
            "expirationDate": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.expiration_date)) if self.expiration_date else None,
            "credentialSchema": self.credential_schema
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'VerifiableCredential\':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            type=data["type"],
            issuer=data["issuer"],
            issuance_date=time.mktime(time.strptime(data["issuanceDate"], "%Y-%m-%dT%H:%M:%SZ")),
            credential_subject=data["credentialSubject"],
            proof=data["proof"],
            expiration_date=time.mktime(time.strptime(data["expirationDate"], "%Y-%m-%dT%H:%M:%SZ")) if data.get("expirationDate") else None,
            credential_schema=data.get("credentialSchema")
        )
    
    def get_payload_for_signing(self) -> bytes:
        """Get the payload that needs to be signed."""
        payload = self.to_dict()
        del payload["proof"]  # Proof is added after signing
        # Canonicalize JSON for consistent signing
        return json.dumps(payload, sort_keys=True, separators=(\',\', \':\')).encode(\'utf-8\')


@dataclass
class TrustScore:
    """
    Represents the trust score and reputation of a component.
    """
    component_id: str
    score: float  # 0.0 - 1.0
    level: TrustLevel
    last_updated: float = field(default_factory=time.time)
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    credentials_held: List[str] = field(default_factory=list)  # List of VC IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "component_id": self.component_id,
            "score": self.score,
            "level": self.level.name,
            "last_updated": self.last_updated,
            "interaction_history": self.interaction_history,
            "credentials_held": self.credentials_held,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'TrustScore\':
        """Create from dictionary representation."""
        return cls(
            component_id=data["component_id"],
            score=data["score"],
            level=TrustLevel[data["level"]],
            last_updated=data.get("last_updated", time.time()),
            interaction_history=data.get("interaction_history", []),
            credentials_held=data.get("credentials_held", []),
            metadata=data.get("metadata", {})
        )


class TrustPolicy:
    """
    Represents a policy based on trust levels.
    """
    def __init__(self, policy_id: str, rules: List[Dict[str, Any]]):
        self.policy_id = policy_id
        self.rules = rules
        self.logger = logging.getLogger(f"{__name__}.TrustPolicy.{self.policy_id[:8]}")
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the policy against a given context."""
        # Context might include source_trust_level, target_trust_level, action, resource, etc.
        self.logger.debug(f"Evaluating policy {self.policy_id} with context: {context}")
        
        # Simple example: Allow if source trust level is >= required level
        for rule in self.rules:
            required_level = TrustLevel[rule.get("required_trust_level", "MEDIUM")]
            source_level = context.get("source_trust_level", TrustLevel.UNKNOWN)
            action = context.get("action")
            
            if rule.get("action") == action:
                if source_level.value >= required_level.value:
                    self.logger.debug(f"Policy {self.policy_id} allows action {action}")
                    return True
                else:
                    self.logger.warning(f"Policy {self.policy_id} denies action {action} due to insufficient trust level")
                    return False
        
        # Default deny if no rule matches
        self.logger.warning(f"Policy {self.policy_id} denies action {action} (no matching rule)")
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "policy_id": self.policy_id,
            "rules": self.rules
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'TrustPolicy\':
        """Create from dictionary representation."""
        return cls(
            policy_id=data["policy_id"],
            rules=data["rules"]
        )


class TrustFabricOrchestrator(ProtocolService):
    """
    Service for managing the Trust Fabric.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "trust_fabric_orchestrator")
        self.config = config or {}
        
        # Initialize storage (in-memory for this example)
        self.identities: Dict[str, DecentralizedIdentity] = {}
        self.credentials: Dict[str, VerifiableCredential] = {}
        self.trust_scores: Dict[str, TrustScore] = {}
        self.policies: Dict[str, TrustPolicy] = {}
        
        # Local identity for the orchestrator itself
        self.local_identity: Optional[DecentralizedIdentity] = None
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.TrustFabricOrchestrator.{self.component_id[:8]}")
        self.logger.info(f"Trust Fabric Orchestrator initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("identity_management", "Manage decentralized identities (DIDs)")
        self.add_capability("credential_management", "Issue and verify verifiable credentials (VCs)")
        self.add_capability("reputation_management", "Track and score component reputation")
        self.add_capability("policy_enforcement", "Enforce trust-based policies")
        self.add_capability("secure_communication", "Facilitate secure communication based on trust")

    async def initialize(self) -> bool:
        """Initialize the orchestrator service."""
        self.logger.info("Initializing Trust Fabric Orchestrator")
        
        # Generate local identity if not provided
        if not self.config.get("local_identity"):
            self.local_identity = DecentralizedIdentity.generate(self.component_id)
            self.logger.info(f"Generated local identity: {self.local_identity.did}")
        else:
            self.local_identity = DecentralizedIdentity.from_dict(self.config["local_identity"])
            self.logger.info(f"Loaded local identity: {self.local_identity.did}")
        
        # Store local identity
        await self.register_identity(self.local_identity.to_dict(include_private_key=True))
        
        # Load initial policies
        initial_policies = self.config.get("initial_policies", [])
        for policy_data in initial_policies:
            await self.register_policy(policy_data)
        
        self.logger.info("Trust Fabric Orchestrator initialized successfully")
        return True

    # --- Identity Management ---

    async def register_identity(self, identity_data: Dict[str, Any]) -> str:
        """Register a decentralized identity."""
        identity = DecentralizedIdentity.from_dict(identity_data)
        did = identity.did
        
        async with self.lock:
            if did in self.identities:
                self.logger.warning(f"Identity {did} already registered, updating")
            
            self.identities[did] = identity
            self.logger.info(f"Registered identity: {did}")
            
            # Initialize trust score if not present
            if identity.did not in self.trust_scores:
                await self._initialize_trust_score(identity.did)
        
        # Publish identity registration event
        await self._publish_trust_event("identity_registered", {"did": did})
        
        return did

    async def get_identity(self, did: str) -> Optional[Dict[str, Any]]:
        """Get a decentralized identity by DID."""
        async with self.lock:
            if did not in self.identities:
                self.logger.error(f"Identity {did} not found")
                return None
            
            # Return without private key
            return self.identities[did].to_dict(include_private_key=False)

    async def resolve_did(self, did: str) -> Optional[Dict[str, Any]]:
        """Resolve a DID to its DID Document (public key info)."""
        # In a real DID system, this might involve querying a distributed ledger
        # For this implementation, we just retrieve from local storage
        return await self.get_identity(did)

    # --- Credential Management ---

    async def issue_credential(self, subject_did: str, credential_type: CredentialType, claims: Dict[str, Any], expiration_seconds: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Issue a verifiable credential."""
        if not self.local_identity or not self.local_identity.private_key_pem:
            self.logger.error("Orchestrator identity not configured for issuing credentials")
            return None
        
        # Ensure subject identity exists
        subject_identity = await self.get_identity(subject_did)
        if not subject_identity:
            self.logger.error(f"Subject identity {subject_did} not found")
            return None
        
        # Create credential
        vc_id = f"urn:uuid:{uuid.uuid4()}"
        issuance_date = time.time()
        expiration_date = issuance_date + expiration_seconds if expiration_seconds else None
        
        credential = VerifiableCredential(
            id=vc_id,
            type=["VerifiableCredential", f"{credential_type.value.capitalize()}Credential"],
            issuer=self.local_identity.did,
            issuance_date=issuance_date,
            credential_subject={
                "id": subject_did,
                **claims
            },
            proof={},  # Will be added after signing
            expiration_date=expiration_date
        )
        
        # Sign the credential
        payload_to_sign = credential.get_payload_for_signing()
        signature = self.local_identity.sign(payload_to_sign)
        
        # Add proof
        credential.proof = {
            "type": "RsaSignature2018",
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(issuance_date)),
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"{self.local_identity.did}#keys-1",  # Assuming key ID convention
            "jws": signature.hex()  # Using hex representation for simplicity
        }
        
        # Store the credential
        async with self.lock:
            self.credentials[vc_id] = credential
            
            # Update trust score with credential info
            if subject_did in self.trust_scores:
                self.trust_scores[subject_did].credentials_held.append(vc_id)
                self.trust_scores[subject_did].last_updated = time.time()
            
            self.logger.info(f"Issued credential {vc_id} of type {credential_type.value} to {subject_did}")
        
        # Publish credential issuance event
        await self._publish_trust_event("credential_issued", {
            "credential_id": vc_id,
            "issuer_did": self.local_identity.did,
            "subject_did": subject_did,
            "type": credential_type.value
        })
        
        return credential.to_dict()

    async def verify_credential(self, credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a verifiable credential."""
        try:
            credential = VerifiableCredential.from_dict(credential_data)
            
            # Check expiration
            if credential.expiration_date and credential.expiration_date < time.time():
                self.logger.warning(f"Credential {credential.id} has expired")
                return {"verified": False, "reason": "Credential expired"}
            
            # Get issuer identity
            issuer_did = credential.issuer
            issuer_identity_data = await self.resolve_did(issuer_did)
            if not issuer_identity_data:
                self.logger.error(f"Issuer identity {issuer_did} not found")
                return {"verified": False, "reason": "Issuer identity not found"}
            
            issuer_identity = DecentralizedIdentity.from_dict(issuer_identity_data)
            
            # Verify signature
            payload_to_verify = credential.get_payload_for_signing()
            signature = bytes.fromhex(credential.proof["jws"])
            
            if issuer_identity.verify(payload_to_verify, signature):
                self.logger.info(f"Credential {credential.id} verified successfully")
                return {"verified": True, "credential": credential.to_dict()}
            else:
                self.logger.warning(f"Credential {credential.id} signature verification failed")
                return {"verified": False, "reason": "Invalid signature"}
        
        except Exception as e:
            self.logger.error(f"Error verifying credential: {e}")
            return {"verified": False, "reason": f"Verification error: {e}"}

    async def get_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get a verifiable credential by ID."""
        async with self.lock:
            if credential_id not in self.credentials:
                self.logger.error(f"Credential {credential_id} not found")
                return None
            
            return self.credentials[credential_id].to_dict()

    # --- Reputation Management ---

    async def _initialize_trust_score(self, component_did: str) -> None:
        """Initialize the trust score for a component."""
        async with self.lock:
            if component_did not in self.trust_scores:
                self.trust_scores[component_did] = TrustScore(
                    component_id=component_did,
                    score=0.5,  # Default starting score
                    level=TrustLevel.MEDIUM
                )
                self.logger.info(f"Initialized trust score for {component_did}")

    async def update_trust_score(self, component_did: str, interaction_event: Dict[str, Any]) -> bool:
        """Update the trust score based on an interaction event."""
        # Interaction event might include: type (success, failure, violation), weight, details
        async with self.lock:
            if component_did not in self.trust_scores:
                await self._initialize_trust_score(component_did)
            
            trust_info = self.trust_scores[component_did]
            
            # Simple update logic (can be much more complex)
            interaction_type = interaction_event.get("type", "neutral")
            weight = interaction_event.get("weight", 0.1)
            
            if interaction_type == "success":
                trust_info.score = min(1.0, trust_info.score + weight * (1.0 - trust_info.score))
            elif interaction_type == "failure":
                trust_info.score = max(0.0, trust_info.score - weight * trust_info.score)
            elif interaction_type == "violation":
                trust_info.score = max(0.0, trust_info.score - weight * 2 * trust_info.score)  # Heavier penalty
            
            # Update trust level based on score
            if trust_info.score >= 0.9:
                trust_info.level = TrustLevel.MAXIMUM
            elif trust_info.score >= 0.7:
                trust_info.level = TrustLevel.HIGH
            elif trust_info.score >= 0.4:
                trust_info.level = TrustLevel.MEDIUM
            elif trust_info.score >= 0.1:
                trust_info.level = TrustLevel.LOW
            else:
                trust_info.level = TrustLevel.UNKNOWN
            
            # Record interaction
            trust_info.interaction_history.append({
                "timestamp": time.time(),
                **interaction_event
            })
            # Keep history limited (optional)
            max_history = self.config.get("max_interaction_history", 100)
            if len(trust_info.interaction_history) > max_history:
                trust_info.interaction_history.pop(0)
            
            trust_info.last_updated = time.time()
            self.logger.info(f"Updated trust score for {component_did}: {trust_info.score:.2f} ({trust_info.level.name})")
        
        # Publish trust score update event
        await self._publish_trust_event("trust_score_updated", {
            "component_did": component_did,
            "score": trust_info.score,
            "level": trust_info.level.name
        })
        
        return True

    async def get_trust_score(self, component_did: str) -> Optional[Dict[str, Any]]:
        """Get the trust score for a component."""
        async with self.lock:
            if component_did not in self.trust_scores:
                # Initialize if not found (could also return None)
                await self._initialize_trust_score(component_did)
            
            return self.trust_scores[component_did].to_dict()

    # --- Policy Management ---

    async def register_policy(self, policy_data: Dict[str, Any]) -> str:
        """Register a trust policy."""
        policy_id = policy_data.get("policy_id", str(uuid.uuid4()))
        
        async with self.lock:
            if policy_id in self.policies:
                self.logger.warning(f"Policy {policy_id} already registered, updating")
            
            policy = TrustPolicy.from_dict({"policy_id": policy_id, **policy_data})
            self.policies[policy_id] = policy
            self.logger.info(f"Registered policy: {policy_id}")
        
        # Publish policy registration event
        await self._publish_trust_event("policy_registered", {"policy_id": policy_id})
        
        return policy_id

    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get a trust policy by ID."""
        async with self.lock:
            if policy_id not in self.policies:
                self.logger.error(f"Policy {policy_id} not found")
                return None
            
            return self.policies[policy_id].to_dict()

    async def evaluate_policy(self, policy_id: str, context: Dict[str, Any]) -> bool:
        """Evaluate a trust policy."""
        async with self.lock:
            if policy_id not in self.policies:
                self.logger.error(f"Policy {policy_id} not found for evaluation")
                return False  # Default deny if policy not found
            
            policy = self.policies[policy_id]
        
        # Add trust levels to context if not provided
        if "source_trust_level" not in context and "source_did" in context:
            source_trust = await self.get_trust_score(context["source_did"])
            context["source_trust_level"] = TrustLevel[source_trust["level"]] if source_trust else TrustLevel.UNKNOWN
        
        if "target_trust_level" not in context and "target_did" in context:
            target_trust = await self.get_trust_score(context["target_did"])
            context["target_trust_level"] = TrustLevel[target_trust["level"]] if target_trust else TrustLevel.UNKNOWN
        
        return policy.evaluate(context)

    # --- Event Publishing ---

    async def _publish_trust_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish a trust fabric-related event."""
        data = data or {}
        
        # Create event message
        event = {
            "event_type": f"trust.{event_type}",
            "timestamp": time.time(),
            "data": data
        }
        
        # In a real implementation, this would publish to an event bus or message broker
        self.logger.debug(f"Published trust event: {event_type}")

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "register_identity":
                did = await self.register_identity(msg_obj.params)
                response_payload = {"did": did}
            
            elif msg_obj.command == "issue_credential":
                params = msg_obj.params
                if "subject_did" in params and "type" in params and "claims" in params:
                    credential = await self.issue_credential(
                        params["subject_did"],
                        CredentialType(params["type"]),
                        params["claims"],
                        params.get("expiration_seconds")
                    )
                    if credential:
                        response_payload = credential
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to issue credential"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing subject_did, type, or claims"}
            
            elif msg_obj.command == "verify_credential":
                params = msg_obj.params
                if "credential" in params:
                    result = await self.verify_credential(params["credential"])
                    response_payload = result
                    if not result["verified"]:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing credential"}
            
            elif msg_obj.command == "update_trust_score":
                params = msg_obj.params
                if "component_did" in params and "event" in params:
                    success = await self.update_trust_score(params["component_did"], params["event"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing component_did or event"}
            
            elif msg_obj.command == "register_policy":
                policy_id = await self.register_policy(msg_obj.params)
                response_payload = {"policy_id": policy_id}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_identity":
                params = msg_obj.params
                if "did" in params:
                    identity = await self.get_identity(params["did"])
                    if identity:
                        response_payload = identity
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Identity not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing did"}
            
            elif msg_obj.query == "resolve_did":
                params = msg_obj.params
                if "did" in params:
                    did_doc = await self.resolve_did(params["did"])
                    if did_doc:
                        response_payload = did_doc
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "DID not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing did"}
            
            elif msg_obj.query == "get_credential":
                params = msg_obj.params
                if "credential_id" in params:
                    credential = await self.get_credential(params["credential_id"])
                    if credential:
                        response_payload = credential
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Credential not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing credential_id"}
            
            elif msg_obj.query == "get_trust_score":
                params = msg_obj.params
                if "component_did" in params:
                    trust_score = await self.get_trust_score(params["component_did"])
                    if trust_score:
                        response_payload = trust_score
                    else:
                        # Should not happen if initialized correctly
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Trust score not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing component_did"}
            
            elif msg_obj.query == "get_policy":
                params = msg_obj.params
                if "policy_id" in params:
                    policy = await self.get_policy(params["policy_id"])
                    if policy:
                        response_payload = policy
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Policy not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing policy_id"}
            
            elif msg_obj.query == "evaluate_policy":
                params = msg_obj.params
                if "policy_id" in params and "context" in params:
                    allowed = await self.evaluate_policy(params["policy_id"], params["context"])
                    response_payload = {"allowed": allowed}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing policy_id or context"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # Ignore other message types
            return None

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_identities = len(self.identities)
            num_credentials = len(self.credentials)
            num_policies = len(self.policies)
            num_trust_scores = len(self.trust_scores)
        
        return {
            "status": "healthy",
            "identities": num_identities,
            "credentials": num_credentials,
            "policies": num_policies,
            "trust_scores": num_trust_scores
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
