"""
Digital Twin Diplomacy Service for the Overseer System.

This module provides the Digital Twin Diplomacy Service that manages diplomatic relations
between digital twins and capsules across the Industriverse ecosystem.
"""

import os
import json
import logging
import asyncio
import datetime
import uuid
from typing import Dict, Any, List, Optional, Union, Set
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("digital_twin_diplomacy")

class DiplomaticRelation(BaseModel):
    """Diplomatic relation between two entities."""
    relation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relation_type: str  # alliance, cooperation, competition, conflict
    trust_level: float = 0.5  # 0.0 to 1.0
    cooperation_level: float = 0.5  # 0.0 to 1.0
    data_sharing_level: float = 0.5  # 0.0 to 1.0
    resource_sharing_level: float = 0.5  # 0.0 to 1.0
    established_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = Field(default_factory=datetime.datetime.now)
    status: str = "active"  # active, suspended, terminated
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DiplomaticEvent(BaseModel):
    """Diplomatic event between entities."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    relation_id: str
    source_id: str
    target_id: str
    event_type: str  # cooperation, conflict, negotiation, agreement, breach
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    description: str
    impact: Dict[str, float] = Field(default_factory=dict)  # trust_impact, cooperation_impact, etc.
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DiplomaticAgreement(BaseModel):
    """Diplomatic agreement between entities."""
    agreement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    relation_id: str
    title: str
    description: str
    terms: Dict[str, Any] = Field(default_factory=dict)
    start_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    end_date: Optional[datetime.datetime] = None
    status: str = "active"  # draft, active, expired, terminated, breached
    compliance_level: float = 1.0  # 0.0 to 1.0
    last_reviewed: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DigitalTwinDiplomacyService:
    """
    Digital Twin Diplomacy Service.
    
    This service manages diplomatic relations between digital twins and capsules
    across the Industriverse ecosystem.
    """
    
    def __init__(self, event_bus_client=None, mcp_client=None, a2a_client=None):
        """
        Initialize the Digital Twin Diplomacy Service.
        
        Args:
            event_bus_client: Event bus client for publishing and subscribing to events
            mcp_client: MCP client for context-aware communication
            a2a_client: A2A client for agent-based communication
        """
        self.event_bus_client = event_bus_client
        self.mcp_client = mcp_client
        self.a2a_client = a2a_client
        
        # In-memory storage (would be replaced with database in production)
        self.relations = {}  # relation_id -> DiplomaticRelation
        self.entity_relations = {}  # entity_id -> Set[relation_id]
        self.events = {}  # event_id -> DiplomaticEvent
        self.agreements = {}  # agreement_id -> DiplomaticAgreement
        self.relation_agreements = {}  # relation_id -> Set[agreement_id]
        
    async def initialize(self):
        """Initialize the Digital Twin Diplomacy Service."""
        logger.info("Initializing Digital Twin Diplomacy Service")
        
        # In a real implementation, we would initialize connections to external systems
        # For example:
        # await self.event_bus_client.connect()
        # await self.mcp_client.connect()
        # await self.a2a_client.connect()
        
        # Subscribe to events
        # await self.event_bus_client.subscribe("capsule.created", self._handle_capsule_created)
        # await self.event_bus_client.subscribe("capsule.interaction", self._handle_capsule_interaction)
        
        logger.info("Digital Twin Diplomacy Service initialized")
        
    async def create_relation(self, source_id: str, target_id: str, relation_type: str, 
                             initial_trust: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> DiplomaticRelation:
        """
        Create a diplomatic relation between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relation (alliance, cooperation, competition, conflict)
            initial_trust: Initial trust level (0.0 to 1.0)
            metadata: Optional metadata
            
        Returns:
            Created diplomatic relation
        """
        logger.info(f"Creating diplomatic relation between {source_id} and {target_id}")
        
        # Create relation
        relation = DiplomaticRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            trust_level=initial_trust,
            metadata=metadata or {}
        )
        
        # Store relation
        self.relations[relation.relation_id] = relation
        
        # Update entity relations
        if source_id not in self.entity_relations:
            self.entity_relations[source_id] = set()
        self.entity_relations[source_id].add(relation.relation_id)
        
        if target_id not in self.entity_relations:
            self.entity_relations[target_id] = set()
        self.entity_relations[target_id].add(relation.relation_id)
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("diplomacy.relation.created", relation.dict())
        
        logger.info(f"Created diplomatic relation {relation.relation_id} between {source_id} and {target_id}")
        
        return relation
        
    async def update_relation(self, relation_id: str, updates: Dict[str, Any]) -> Optional[DiplomaticRelation]:
        """
        Update a diplomatic relation.
        
        Args:
            relation_id: ID of the relation to update
            updates: Updates to apply
            
        Returns:
            Updated diplomatic relation, or None if not found
        """
        if relation_id not in self.relations:
            logger.warning(f"Diplomatic relation {relation_id} not found")
            return None
            
        relation = self.relations[relation_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(relation, key):
                setattr(relation, key, value)
                
        # Update last_updated
        relation.last_updated = datetime.datetime.now()
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("diplomacy.relation.updated", relation.dict())
        
        logger.info(f"Updated diplomatic relation {relation_id}")
        
        return relation
        
    async def get_relation(self, relation_id: str) -> Optional[DiplomaticRelation]:
        """
        Get a diplomatic relation by ID.
        
        Args:
            relation_id: ID of the relation
            
        Returns:
            Diplomatic relation, or None if not found
        """
        return self.relations.get(relation_id)
        
    async def get_entity_relations(self, entity_id: str) -> List[DiplomaticRelation]:
        """
        Get all diplomatic relations for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of diplomatic relations
        """
        if entity_id not in self.entity_relations:
            return []
            
        relations = []
        for relation_id in self.entity_relations[entity_id]:
            if relation_id in self.relations:
                relations.append(self.relations[relation_id])
                
        return relations
        
    async def get_relation_between(self, source_id: str, target_id: str) -> Optional[DiplomaticRelation]:
        """
        Get the diplomatic relation between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            
        Returns:
            Diplomatic relation, or None if not found
        """
        if source_id not in self.entity_relations:
            return None
            
        for relation_id in self.entity_relations[source_id]:
            relation = self.relations.get(relation_id)
            if relation and ((relation.source_id == source_id and relation.target_id == target_id) or
                            (relation.source_id == target_id and relation.target_id == source_id)):
                return relation
                
        return None
        
    async def record_diplomatic_event(self, relation_id: str, event_type: str, description: str,
                                     impact: Optional[Dict[str, float]] = None,
                                     context: Optional[Dict[str, Any]] = None,
                                     metadata: Optional[Dict[str, Any]] = None) -> DiplomaticEvent:
        """
        Record a diplomatic event.
        
        Args:
            relation_id: ID of the relation
            event_type: Type of event (cooperation, conflict, negotiation, agreement, breach)
            description: Description of the event
            impact: Optional impact on relation metrics
            context: Optional context information
            metadata: Optional metadata
            
        Returns:
            Created diplomatic event
        """
        if relation_id not in self.relations:
            logger.warning(f"Diplomatic relation {relation_id} not found")
            raise ValueError(f"Diplomatic relation {relation_id} not found")
            
        relation = self.relations[relation_id]
        
        # Create event
        event = DiplomaticEvent(
            relation_id=relation_id,
            source_id=relation.source_id,
            target_id=relation.target_id,
            event_type=event_type,
            description=description,
            impact=impact or {},
            context=context or {},
            metadata=metadata or {}
        )
        
        # Store event
        self.events[event.event_id] = event
        
        # Update relation based on impact
        if impact:
            updates = {}
            for metric, value in impact.items():
                if hasattr(relation, metric):
                    current = getattr(relation, metric)
                    new_value = max(0.0, min(1.0, current + value))  # Ensure within 0.0-1.0
                    updates[metric] = new_value
                    
            if updates:
                await self.update_relation(relation_id, updates)
                
        # In a real implementation, we would publish the event
        # For example:
        # await self.event_bus_client.publish("diplomacy.event.recorded", event.dict())
        
        logger.info(f"Recorded diplomatic event {event.event_id} for relation {relation_id}")
        
        return event
        
    async def get_diplomatic_events(self, relation_id: Optional[str] = None,
                                   entity_id: Optional[str] = None,
                                   event_type: Optional[str] = None,
                                   start_time: Optional[datetime.datetime] = None,
                                   end_time: Optional[datetime.datetime] = None) -> List[DiplomaticEvent]:
        """
        Get diplomatic events.
        
        Args:
            relation_id: Optional relation ID filter
            entity_id: Optional entity ID filter
            event_type: Optional event type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of diplomatic events
        """
        events = list(self.events.values())
        
        # Apply filters
        if relation_id:
            events = [e for e in events if e.relation_id == relation_id]
            
        if entity_id:
            events = [e for e in events if e.source_id == entity_id or e.target_id == entity_id]
            
        if event_type:
            events = [e for e in events if e.event_type == event_type]
            
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
            
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
            
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events
        
    async def create_agreement(self, relation_id: str, title: str, description: str,
                              terms: Dict[str, Any], end_date: Optional[datetime.datetime] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> DiplomaticAgreement:
        """
        Create a diplomatic agreement.
        
        Args:
            relation_id: ID of the relation
            title: Title of the agreement
            description: Description of the agreement
            terms: Terms of the agreement
            end_date: Optional end date
            metadata: Optional metadata
            
        Returns:
            Created diplomatic agreement
        """
        if relation_id not in self.relations:
            logger.warning(f"Diplomatic relation {relation_id} not found")
            raise ValueError(f"Diplomatic relation {relation_id} not found")
            
        # Create agreement
        agreement = DiplomaticAgreement(
            relation_id=relation_id,
            title=title,
            description=description,
            terms=terms,
            end_date=end_date,
            metadata=metadata or {}
        )
        
        # Store agreement
        self.agreements[agreement.agreement_id] = agreement
        
        # Update relation agreements
        if relation_id not in self.relation_agreements:
            self.relation_agreements[relation_id] = set()
        self.relation_agreements[relation_id].add(agreement.agreement_id)
        
        # Record event
        await self.record_diplomatic_event(
            relation_id=relation_id,
            event_type="agreement",
            description=f"Agreement '{title}' established",
            impact={"trust_level": 0.1, "cooperation_level": 0.1},
            context={"agreement_id": agreement.agreement_id}
        )
        
        # In a real implementation, we would publish the creation
        # For example:
        # await self.event_bus_client.publish("diplomacy.agreement.created", agreement.dict())
        
        logger.info(f"Created diplomatic agreement {agreement.agreement_id} for relation {relation_id}")
        
        return agreement
        
    async def update_agreement(self, agreement_id: str, updates: Dict[str, Any]) -> Optional[DiplomaticAgreement]:
        """
        Update a diplomatic agreement.
        
        Args:
            agreement_id: ID of the agreement to update
            updates: Updates to apply
            
        Returns:
            Updated diplomatic agreement, or None if not found
        """
        if agreement_id not in self.agreements:
            logger.warning(f"Diplomatic agreement {agreement_id} not found")
            return None
            
        agreement = self.agreements[agreement_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(agreement, key):
                setattr(agreement, key, value)
                
        # Update last_reviewed
        agreement.last_reviewed = datetime.datetime.now()
        
        # In a real implementation, we would publish the update
        # For example:
        # await self.event_bus_client.publish("diplomacy.agreement.updated", agreement.dict())
        
        logger.info(f"Updated diplomatic agreement {agreement_id}")
        
        return agreement
        
    async def get_agreement(self, agreement_id: str) -> Optional[DiplomaticAgreement]:
        """
        Get a diplomatic agreement by ID.
        
        Args:
            agreement_id: ID of the agreement
            
        Returns:
            Diplomatic agreement, or None if not found
        """
        return self.agreements.get(agreement_id)
        
    async def get_relation_agreements(self, relation_id: str) -> List[DiplomaticAgreement]:
        """
        Get all diplomatic agreements for a relation.
        
        Args:
            relation_id: ID of the relation
            
        Returns:
            List of diplomatic agreements
        """
        if relation_id not in self.relation_agreements:
            return []
            
        agreements = []
        for agreement_id in self.relation_agreements[relation_id]:
            if agreement_id in self.agreements:
                agreements.append(self.agreements[agreement_id])
                
        return agreements
        
    async def record_agreement_breach(self, agreement_id: str, description: str,
                                     severity: float = 0.5,
                                     context: Optional[Dict[str, Any]] = None) -> DiplomaticEvent:
        """
        Record a breach of a diplomatic agreement.
        
        Args:
            agreement_id: ID of the agreement
            description: Description of the breach
            severity: Severity of the breach (0.0 to 1.0)
            context: Optional context information
            
        Returns:
            Created diplomatic event
        """
        if agreement_id not in self.agreements:
            logger.warning(f"Diplomatic agreement {agreement_id} not found")
            raise ValueError(f"Diplomatic agreement {agreement_id} not found")
            
        agreement = self.agreements[agreement_id]
        relation_id = agreement.relation_id
        
        # Update agreement
        compliance_impact = -severity
        new_compliance = max(0.0, agreement.compliance_level + compliance_impact)
        await self.update_agreement(agreement_id, {
            "compliance_level": new_compliance,
            "status": "breached" if new_compliance < 0.5 else agreement.status
        })
        
        # Calculate trust impact based on severity
        trust_impact = -severity * 0.2  # Scale down the impact
        
        # Record event
        event = await self.record_diplomatic_event(
            relation_id=relation_id,
            event_type="breach",
            description=f"Agreement '{agreement.title}' breached: {description}",
            impact={"trust_level": trust_impact, "cooperation_level": trust_impact / 2},
            context={"agreement_id": agreement_id, "severity": severity, **(context or {})}
        )
        
        logger.info(f"Recorded breach of diplomatic agreement {agreement_id}")
        
        return event
        
    async def negotiate(self, source_id: str, target_id: str, 
                       proposal: Dict[str, Any],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Negotiate between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            proposal: Negotiation proposal
            context: Optional context information
            
        Returns:
            Negotiation result
        """
        logger.info(f"Negotiating between {source_id} and {target_id}")
        
        # Get or create relation
        relation = await self.get_relation_between(source_id, target_id)
        if not relation:
            relation = await self.create_relation(source_id, target_id, "negotiation", 0.5)
            
        # In a real implementation, we would use the A2A protocol to negotiate
        # For example:
        # negotiation_result = await self.a2a_client.negotiate(source_id, target_id, proposal)
        
        # For simulation, we'll create a simple negotiation result
        negotiation_result = {
            "success": True,
            "counter_proposal": None,
            "agreement": proposal,
            "relation_id": relation.relation_id
        }
        
        # Record event
        await self.record_diplomatic_event(
            relation_id=relation.relation_id,
            event_type="negotiation",
            description=f"Negotiation between {source_id} and {target_id}",
            impact={"trust_level": 0.05, "cooperation_level": 0.05},
            context={"proposal": proposal, "result": negotiation_result, **(context or {})}
        )
        
        # If successful, create agreement
        if negotiation_result["success"] and "agreement" in negotiation_result:
            agreement_data = negotiation_result["agreement"]
            await self.create_agreement(
                relation_id=relation.relation_id,
                title=agreement_data.get("title", "Negotiated Agreement"),
                description=agreement_data.get("description", "Agreement resulting from negotiation"),
                terms=agreement_data.get("terms", {}),
                end_date=agreement_data.get("end_date"),
                metadata={"negotiation_context": context or {}}
            )
            
        logger.info(f"Completed negotiation between {source_id} and {target_id}")
        
        return negotiation_result
        
    async def calculate_diplomatic_network(self) -> Dict[str, Any]:
        """
        Calculate the diplomatic network across all entities.
        
        Returns:
            Diplomatic network analysis
        """
        logger.info("Calculating diplomatic network")
        
        # Extract entities and relations
        entities = set()
        for relation in self.relations.values():
            entities.add(relation.source_id)
            entities.add(relation.target_id)
            
        # Calculate metrics
        entity_metrics = {}
        for entity_id in entities:
            relations = await self.get_entity_relations(entity_id)
            
            # Calculate average trust
            trust_values = [r.trust_level for r in relations]
            avg_trust = sum(trust_values) / len(trust_values) if trust_values else 0.0
            
            # Calculate average cooperation
            coop_values = [r.cooperation_level for r in relations]
            avg_coop = sum(coop_values) / len(coop_values) if coop_values else 0.0
            
            # Calculate network centrality (simplified)
            centrality = len(relations) / len(entities) if entities else 0.0
            
            entity_metrics[entity_id] = {
                "relations_count": len(relations),
                "average_trust": avg_trust,
                "average_cooperation": avg_coop,
                "centrality": centrality
            }
            
        # Calculate overall network metrics
        overall_metrics = {
            "entity_count": len(entities),
            "relation_count": len(self.relations),
            "average_trust": sum(m["average_trust"] for m in entity_metrics.values()) / len(entity_metrics) if entity_metrics else 0.0,
            "average_cooperation": sum(m["average_cooperation"] for m in entity_metrics.values()) / len(entity_metrics) if entity_metrics else 0.0,
            "density": len(self.relations) / (len(entities) * (len(entities) - 1) / 2) if len(entities) > 1 else 0.0
        }
        
        # Identify key entities
        key_entities = sorted(
            [(entity_id, metrics["centrality"]) for entity_id, metrics in entity_metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 entities by centrality
        
        network_analysis = {
            "timestamp": datetime.datetime.now(),
            "entity_metrics": entity_metrics,
            "overall_metrics": overall_metrics,
            "key_entities": key_entities
        }
        
        logger.info("Completed diplomatic network calculation")
        
        return network_analysis
        
    async def _handle_capsule_created(self, event):
        """
        Handle capsule created event.
        
        Args:
            event: Capsule created event
        """
        capsule_id = event["capsule_id"]
        
        logger.info(f"Handling capsule created event for capsule {capsule_id}")
        
        # In a real implementation, we might initialize relations with existing entities
        # based on capsule purpose, domain, etc.
        
    async def _handle_capsule_interaction(self, event):
        """
        Handle capsule interaction event.
        
        Args:
            event: Capsule interaction event
        """
        source_id = event["source_id"]
        target_id = event["target_id"]
        interaction_type = event["interaction_type"]
        
        logger.info(f"Handling capsule interaction event between {source_id} and {target_id}")
        
        # Get or create relation
        relation = await self.get_relation_between(source_id, target_id)
        if not relation:
            relation_type = "cooperation" if interaction_type in ["collaborate", "assist", "share"] else "competition"
            relation = await self.create_relation(source_id, target_id, relation_type, 0.5)
            
        # Update relation based on interaction
        impact = {}
        if interaction_type == "collaborate":
            impact = {"trust_level": 0.05, "cooperation_level": 0.1, "resource_sharing_level": 0.05}
        elif interaction_type == "compete":
            impact = {"cooperation_level": -0.05}
        elif interaction_type == "conflict":
            impact = {"trust_level": -0.1, "cooperation_level": -0.1}
        elif interaction_type == "assist":
            impact = {"trust_level": 0.1, "cooperation_level": 0.05}
        elif interaction_type == "share":
            impact = {"trust_level": 0.05, "data_sharing_level": 0.1}
            
        # Record event
        await self.record_diplomatic_event(
            relation_id=relation.relation_id,
            event_type=interaction_type,
            description=f"{interaction_type.capitalize()} interaction between {source_id} and {target_id}",
            impact=impact,
            context=event.get("context", {})
        )
