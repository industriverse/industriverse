"""
Digital Twin Diplomacy Service for the Overseer System.

This service coordinates the Digital Twin Diplomacy phase components,
including Twin Negotiation Agent and Capsule Shadow Manager, providing
a unified interface for digital twin diplomacy operations.

Author: Manus AI
Date: May 25, 2025
"""

import json
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService

# Import diplomacy components
from .twin_negotiation_agent import TwinNegotiationAgent
from .capsule_shadow_manager import CapsuleShadowManager
from .diplomacy_models import (
    NegotiationSession, NegotiationProposal, NegotiationAgreement,
    ResourceSpecification, ResourceType, NegotiationStatus, ProposalStatus,
    ResourceConflict, ConflictResolution, ConflictType, ConflictSeverity,
    ResolutionStrategy, ShadowCapsule, ShadowType, ShadowStatus
)

class DiplomacyAnalytics:
    """Analytics for digital twin diplomacy operations."""
    
    def __init__(
        self,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the diplomacy analytics.
        
        Args:
            data_access: Data access service
            logger: Logger instance
        """
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_negotiation_patterns(
        self,
        time_period: Optional[str] = "last_30_days",
        agent_ids: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze negotiation patterns.
        
        Args:
            time_period: Time period for analysis
            agent_ids: List of agent IDs to filter
            resource_types: List of resource types to filter
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Build query
        query = {}
        
        # Add time filter
        if time_period:
            now = datetime.now()
            
            if time_period == "last_24_hours":
                start_time = now - timedelta(hours=24)
            elif time_period == "last_7_days":
                start_time = now - timedelta(days=7)
            elif time_period == "last_30_days":
                start_time = now - timedelta(days=30)
            elif time_period == "last_90_days":
                start_time = now - timedelta(days=90)
            else:
                start_time = now - timedelta(days=30)  # Default to 30 days
            
            query["created_at"] = {"$gte": start_time.isoformat()}
        
        # Add agent filter
        if agent_ids:
            query["$or"] = [
                {"initiator_id": {"$in": agent_ids}},
                {"participants": {"$in": agent_ids}}
            ]
        
        # Query sessions
        sessions_data = self.data_access.query(
            collection="negotiation_sessions",
            query=query
        )
        
        if not sessions_data:
            return {"error": "No negotiation sessions found for the specified criteria"}
        
        # Analyze sessions
        results = {
            "total_sessions": len(sessions_data),
            "completed_sessions": 0,
            "agreement_rate": 0,
            "average_proposals_per_session": 0,
            "average_negotiation_duration": 0,
            "resource_type_frequency": {},
            "agent_participation": {},
            "strategy_effectiveness": {},
            "time_series": {}
        }
        
        total_proposals = 0
        total_duration = 0
        completed_with_agreement = 0
        
        # Process each session
        for session_data in sessions_data:
            session = NegotiationSession.from_dict(session_data)
            
            # Count completed sessions
            if session.status in [NegotiationStatus.COMPLETED, NegotiationStatus.EXPIRED]:
                results["completed_sessions"] += 1
                
                # Count agreements
                if session.agreement_id:
                    completed_with_agreement += 1
                
                # Calculate duration
                if session.completed_at and session.created_at:
                    duration = (session.completed_at - session.created_at).total_seconds() / 60  # in minutes
                    total_duration += duration
            
            # Count proposals
            total_proposals += len(session.proposals)
            
            # Track agent participation
            for participant in session.participants:
                if participant not in results["agent_participation"]:
                    results["agent_participation"][participant] = 0
                
                results["agent_participation"][participant] += 1
            
            # Track initiator
            if session.initiator_id not in results["agent_participation"]:
                results["agent_participation"][session.initiator_id] = 0
            
            results["agent_participation"][session.initiator_id] += 1
            
            # Process proposals for resource types and strategies
            for proposal_id in session.proposals:
                proposal_data = self.data_access.read(
                    collection="negotiation_proposals",
                    document_id=proposal_id
                )
                
                if not proposal_data:
                    continue
                
                proposal = NegotiationProposal.from_dict(proposal_data)
                
                # Track resource types
                for resource in proposal.resources:
                    resource_type = resource.resource_type
                    
                    if resource_types and resource_type not in resource_types:
                        continue
                    
                    if resource_type not in results["resource_type_frequency"]:
                        results["resource_type_frequency"][resource_type] = 0
                    
                    results["resource_type_frequency"][resource_type] += 1
                
                # Track strategy effectiveness
                strategy = proposal.metadata.get("strategy")
                
                if strategy:
                    if strategy not in results["strategy_effectiveness"]:
                        results["strategy_effectiveness"][strategy] = {
                            "used": 0,
                            "accepted": 0,
                            "rejected": 0,
                            "countered": 0
                        }
                    
                    results["strategy_effectiveness"][strategy]["used"] += 1
                    
                    # Track responses
                    for responder_id, response in proposal.responses.items():
                        if response == "accept":
                            results["strategy_effectiveness"][strategy]["accepted"] += 1
                        elif response == "reject":
                            results["strategy_effectiveness"][strategy]["rejected"] += 1
                        elif response == "counter":
                            results["strategy_effectiveness"][strategy]["countered"] += 1
        
        # Calculate averages and rates
        if results["completed_sessions"] > 0:
            results["agreement_rate"] = (completed_with_agreement / results["completed_sessions"]) * 100
            results["average_negotiation_duration"] = total_duration / results["completed_sessions"]
        
        if results["total_sessions"] > 0:
            results["average_proposals_per_session"] = total_proposals / results["total_sessions"]
        
        # Calculate strategy effectiveness rates
        for strategy, stats in results["strategy_effectiveness"].items():
            if stats["used"] > 0:
                stats["acceptance_rate"] = (stats["accepted"] / stats["used"]) * 100
                stats["rejection_rate"] = (stats["rejected"] / stats["used"]) * 100
                stats["counter_rate"] = (stats["countered"] / stats["used"]) * 100
        
        # Generate time series data
        results["time_series"] = self._generate_time_series(sessions_data)
        
        return results
    
    def _generate_time_series(self, sessions_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate time series data from sessions.
        
        Args:
            sessions_data: List of session data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Time series data
        """
        # Group sessions by day
        sessions_by_day = {}
        
        for session_data in sessions_data:
            created_at = datetime.fromisoformat(session_data.get("created_at", ""))
            day_key = created_at.strftime("%Y-%m-%d")
            
            if day_key not in sessions_by_day:
                sessions_by_day[day_key] = []
            
            sessions_by_day[day_key].append(session_data)
        
        # Generate time series
        time_series = {
            "sessions": [],
            "agreements": [],
            "proposals": []
        }
        
        # Sort days
        sorted_days = sorted(sessions_by_day.keys())
        
        for day in sorted_days:
            day_sessions = sessions_by_day[day]
            
            # Count sessions
            time_series["sessions"].append({
                "date": day,
                "count": len(day_sessions)
            })
            
            # Count agreements
            agreements_count = sum(1 for s in day_sessions if s.get("agreement_id"))
            
            time_series["agreements"].append({
                "date": day,
                "count": agreements_count
            })
            
            # Count proposals
            proposals_count = sum(len(s.get("proposals", [])) for s in day_sessions)
            
            time_series["proposals"].append({
                "date": day,
                "count": proposals_count
            })
        
        return time_series
    
    def analyze_shadow_performance(
        self,
        time_period: Optional[str] = "last_30_days",
        shadow_types: Optional[List[str]] = None,
        original_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze shadow capsule performance.
        
        Args:
            time_period: Time period for analysis
            shadow_types: List of shadow types to filter
            original_ids: List of original capsule IDs to filter
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Build query
        query = {}
        
        # Add time filter
        if time_period:
            now = datetime.now()
            
            if time_period == "last_24_hours":
                start_time = now - timedelta(hours=24)
            elif time_period == "last_7_days":
                start_time = now - timedelta(days=7)
            elif time_period == "last_30_days":
                start_time = now - timedelta(days=30)
            elif time_period == "last_90_days":
                start_time = now - timedelta(days=90)
            else:
                start_time = now - timedelta(days=30)  # Default to 30 days
            
            query["created_at"] = {"$gte": start_time.isoformat()}
        
        # Add shadow type filter
        if shadow_types:
            query["shadow_type"] = {"$in": shadow_types}
        
        # Add original ID filter
        if original_ids:
            query["original_id"] = {"$in": original_ids}
        
        # Query shadows
        shadows_data = self.data_access.query(
            collection="shadow_capsules",
            query=query
        )
        
        if not shadows_data:
            return {"error": "No shadow capsules found for the specified criteria"}
        
        # Analyze shadows
        results = {
            "total_shadows": len(shadows_data),
            "active_shadows": 0,
            "retired_shadows": 0,
            "diverged_shadows": 0,
            "average_divergence": 0,
            "shadow_type_distribution": {},
            "original_distribution": {},
            "divergence_by_type": {},
            "time_series": {}
        }
        
        total_divergence = 0
        
        # Process each shadow
        for shadow_data in shadows_data:
            shadow = ShadowCapsule.from_dict(shadow_data)
            
            # Count by status
            if shadow.status == ShadowStatus.ACTIVE:
                results["active_shadows"] += 1
            elif shadow.status == ShadowStatus.RETIRED:
                results["retired_shadows"] += 1
            
            # Count diverged
            if shadow.status == ShadowStatus.DIVERGED:
                results["diverged_shadows"] += 1
            
            # Track shadow type
            shadow_type = shadow.shadow_type
            
            if shadow_type not in results["shadow_type_distribution"]:
                results["shadow_type_distribution"][shadow_type] = 0
            
            results["shadow_type_distribution"][shadow_type] += 1
            
            # Track original
            original_id = shadow.original_id
            
            if original_id not in results["original_distribution"]:
                results["original_distribution"][original_id] = 0
            
            results["original_distribution"][original_id] += 1
            
            # Track divergence
            divergence = shadow.divergence_metrics.get("state_change_percentage", 0)
            total_divergence += divergence
            
            # Track divergence by type
            if shadow_type not in results["divergence_by_type"]:
                results["divergence_by_type"][shadow_type] = {
                    "count": 0,
                    "total_divergence": 0,
                    "average_divergence": 0
                }
            
            results["divergence_by_type"][shadow_type]["count"] += 1
            results["divergence_by_type"][shadow_type]["total_divergence"] += divergence
        
        # Calculate averages
        if results["total_shadows"] > 0:
            results["average_divergence"] = total_divergence / results["total_shadows"]
        
        # Calculate average divergence by type
        for shadow_type, stats in results["divergence_by_type"].items():
            if stats["count"] > 0:
                stats["average_divergence"] = stats["total_divergence"] / stats["count"]
        
        # Generate time series data
        results["time_series"] = self._generate_shadow_time_series(shadows_data)
        
        return results
    
    def _generate_shadow_time_series(self, shadows_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate time series data from shadows.
        
        Args:
            shadows_data: List of shadow data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Time series data
        """
        # Group shadows by day
        shadows_by_day = {}
        
        for shadow_data in shadows_data:
            created_at = datetime.fromisoformat(shadow_data.get("created_at", ""))
            day_key = created_at.strftime("%Y-%m-%d")
            
            if day_key not in shadows_by_day:
                shadows_by_day[day_key] = []
            
            shadows_by_day[day_key].append(shadow_data)
        
        # Generate time series
        time_series = {
            "created": [],
            "retired": [],
            "diverged": []
        }
        
        # Sort days
        sorted_days = sorted(shadows_by_day.keys())
        
        for day in sorted_days:
            day_shadows = shadows_by_day[day]
            
            # Count created
            time_series["created"].append({
                "date": day,
                "count": len(day_shadows)
            })
            
            # Count retired
            retired_count = sum(1 for s in day_shadows if s.get("status") == ShadowStatus.RETIRED)
            
            time_series["retired"].append({
                "date": day,
                "count": retired_count
            })
            
            # Count diverged
            diverged_count = sum(1 for s in day_shadows if s.get("status") == ShadowStatus.DIVERGED)
            
            time_series["diverged"].append({
                "date": day,
                "count": diverged_count
            })
        
        return time_series

class DiplomacyOrchestrator:
    """Orchestrates diplomacy operations between digital twins."""
    
    def __init__(
        self,
        negotiation_agent: TwinNegotiationAgent,
        shadow_manager: CapsuleShadowManager,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the diplomacy orchestrator.
        
        Args:
            negotiation_agent: Twin negotiation agent
            shadow_manager: Capsule shadow manager
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            data_access: Data access service
            logger: Logger instance
        """
        self.negotiation_agent = negotiation_agent
        self.shadow_manager = shadow_manager
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize orchestration tasks
        self.orchestration_tasks: Dict[str, asyncio.Task] = {}
    
    async def orchestrate_negotiation_with_shadows(
        self,
        original_ids: List[str],
        resource_specifications: Dict[str, List[ResourceSpecification]],
        shadow_type: ShadowType = ShadowType.NEGOTIATION,
        strategy: str = "collaborative",
        max_rounds: int = 10,
        timeout_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Orchestrate negotiation using shadow capsules.
        
        Args:
            original_ids: List of original capsule IDs
            resource_specifications: Resource specifications by capsule ID
            shadow_type: Type of shadow to create
            strategy: Negotiation strategy
            max_rounds: Maximum negotiation rounds
            timeout_minutes: Negotiation timeout in minutes
            
        Returns:
            Dict[str, Any]: Orchestration results
        """
        # Create shadows for each original
        shadows = []
        
        for original_id in original_ids:
            shadow = self.shadow_manager.create_shadow(
                original_id=original_id,
                shadow_type=shadow_type,
                metadata={
                    "orchestration_type": "negotiation",
                    "strategy": strategy
                }
            )
            
            shadows.append(shadow)
        
        # Create negotiation session
        session = self.negotiation_agent.create_negotiation_session(
            initiator_id=self.negotiation_agent.agent_id,
            participants=[s.shadow_id for s in shadows],
            context={
                "orchestration_id": str(uuid.uuid4()),
                "original_ids": original_ids,
                "shadow_type": shadow_type,
                "strategy": strategy,
                "max_rounds": max_rounds
            },
            expires_in_hours=timeout_minutes / 60,
            metadata={
                "orchestrated": True,
                "shadow_negotiation": True
            }
        )
        
        # Start orchestration task
        task = asyncio.create_task(
            self._run_shadow_negotiation(
                session=session,
                shadows=shadows,
                resource_specifications=resource_specifications,
                strategy=strategy,
                max_rounds=max_rounds,
                timeout_minutes=timeout_minutes
            )
        )
        
        self.orchestration_tasks[session.session_id] = task
        
        self.logger.info(f"Started orchestrated negotiation {session.session_id} with {len(shadows)} shadows")
        
        # Return initial state
        return {
            "orchestration_id": session.context.get("orchestration_id"),
            "session_id": session.session_id,
            "shadow_ids": [s.shadow_id for s in shadows],
            "original_ids": original_ids,
            "status": "started",
            "created_at": datetime.now().isoformat()
        }
    
    async def _run_shadow_negotiation(
        self,
        session: NegotiationSession,
        shadows: List[ShadowCapsule],
        resource_specifications: Dict[str, List[ResourceSpecification]],
        strategy: str,
        max_rounds: int,
        timeout_minutes: int
    ) -> Dict[str, Any]:
        """
        Run a shadow negotiation.
        
        Args:
            session: Negotiation session
            shadows: List of shadow capsules
            resource_specifications: Resource specifications by capsule ID
            strategy: Negotiation strategy
            max_rounds: Maximum negotiation rounds
            timeout_minutes: Negotiation timeout in minutes
            
        Returns:
            Dict[str, Any]: Negotiation results
        """
        try:
            # Map shadows by original ID
            shadows_by_original = {s.original_id: s for s in shadows}
            
            # Initialize round counter
            current_round = 0
            
            # Initialize timeout
            timeout = datetime.now() + timedelta(minutes=timeout_minutes)
            
            # Initialize result
            result = {
                "orchestration_id": session.context.get("orchestration_id"),
                "session_id": session.session_id,
                "shadow_ids": [s.shadow_id for s in shadows],
                "original_ids": list(shadows_by_original.keys()),
                "rounds": [],
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            }
            
            # Start negotiation
            while current_round < max_rounds and datetime.now() < timeout:
                current_round += 1
                
                self.logger.info(f"Starting negotiation round {current_round} for session {session.session_id}")
                
                # Initialize round
                round_result = {
                    "round": current_round,
                    "proposals": [],
                    "responses": [],
                    "status": "in_progress"
                }
                
                # Each shadow submits a proposal
                for original_id, shadow in shadows_by_original.items():
                    # Get resource specifications
                    resources = resource_specifications.get(original_id, [])
                    
                    if not resources:
                        self.logger.warning(f"No resource specifications for {original_id}")
                        continue
                    
                    # Submit proposal
                    proposal = self.negotiation_agent.submit_proposal(
                        session_id=session.session_id,
                        proposer_id=shadow.shadow_id,
                        resources=resources,
                        strategy_name=strategy
                    )
                    
                    # Add to round result
                    round_result["proposals"].append({
                        "proposal_id": proposal.proposal_id,
                        "proposer_id": shadow.shadow_id,
                        "original_id": original_id,
                        "resources": [r.to_dict() for r in resources]
                    })
                    
                    # Wait a bit to avoid race conditions
                    await asyncio.sleep(1)
                
                # Each shadow responds to all proposals
                for proposal_info in round_result["proposals"]:
                    proposal_id = proposal_info["proposal_id"]
                    proposer_id = proposal_info["proposer_id"]
                    
                    # Get proposal
                    proposal_data = self.data_access.read(
                        collection="negotiation_proposals",
                        document_id=proposal_id
                    )
                    
                    if not proposal_data:
                        self.logger.warning(f"Proposal {proposal_id} not found")
                        continue
                    
                    proposal = NegotiationProposal.from_dict(proposal_data)
                    
                    # Each shadow responds
                    for original_id, shadow in shadows_by_original.items():
                        # Skip if this is the proposer
                        if shadow.shadow_id == proposer_id:
                            continue
                        
                        # Get resource specifications
                        resources = resource_specifications.get(original_id, [])
                        
                        if not resources:
                            self.logger.warning(f"No resource specifications for {original_id}")
                            continue
                        
                        # Create strategy
                        strategy_obj = self.negotiation_agent.strategy_factory.create_strategy(strategy)
                        
                        # Evaluate proposal
                        response, rationale, counter_proposal = strategy_obj.evaluate_proposal(
                            proposal=proposal,
                            agent_id=shadow.shadow_id,
                            resources=resources,
                            context={"session": session}
                        )
                        
                        # Respond to proposal
                        self.negotiation_agent.respond_to_proposal(
                            proposal_id=proposal_id,
                            responder_id=shadow.shadow_id,
                            response=response,
                            strategy_name=strategy,
                            rationale=rationale,
                            resources=resources if response == "counter" else None
                        )
                        
                        # Add to round result
                        round_result["responses"].append({
                            "proposal_id": proposal_id,
                            "responder_id": shadow.shadow_id,
                            "original_id": original_id,
                            "response": response,
                            "rationale": rationale
                        })
                        
                        # Wait a bit to avoid race conditions
                        await asyncio.sleep(1)
                
                # Check if agreement reached
                session_data = self.data_access.read(
                    collection="negotiation_sessions",
                    document_id=session.session_id
                )
                
                if not session_data:
                    self.logger.warning(f"Session {session.session_id} not found")
                    break
                
                session = NegotiationSession.from_dict(session_data)
                
                if session.agreement_id:
                    round_result["status"] = "agreement_reached"
                    result["status"] = "completed"
                    result["agreement_id"] = session.agreement_id
                    
                    # Get agreement
                    agreement_data = self.data_access.read(
                        collection="negotiation_agreements",
                        document_id=session.agreement_id
                    )
                    
                    if agreement_data:
                        agreement = NegotiationAgreement.from_dict(agreement_data)
                        result["agreement"] = agreement.to_dict()
                    
                    self.logger.info(f"Agreement reached in round {current_round} for session {session.session_id}")
                    
                    break
                
                # Add round to result
                result["rounds"].append(round_result)
                
                # Check if max rounds reached
                if current_round >= max_rounds:
                    result["status"] = "max_rounds_reached"
                    self.logger.info(f"Max rounds reached for session {session.session_id}")
                    break
                
                # Check if timeout reached
                if datetime.now() >= timeout:
                    result["status"] = "timeout"
                    self.logger.info(f"Timeout reached for session {session.session_id}")
                    break
            
            # Finalize result
            result["completed_at"] = datetime.now().isoformat()
            result["rounds_completed"] = current_round
            
            # Store result
            self.data_access.create(
                collection="orchestration_results",
                document_id=session.context.get("orchestration_id", str(uuid.uuid4())),
                data=result
            )
            
            # Publish event
            self.event_bus.publish(
                topic="diplomacy.orchestration.completed",
                key=session.session_id,
                value={
                    "orchestration_id": session.context.get("orchestration_id"),
                    "session_id": session.session_id,
                    "status": result["status"],
                    "rounds_completed": current_round,
                    "agreement_id": result.get("agreement_id"),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Retire shadows
            for shadow in shadows:
                self.shadow_manager.retire_shadow(shadow.shadow_id)
            
            self.logger.info(f"Completed orchestrated negotiation {session.session_id} with status {result['status']}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in shadow negotiation: {str(e)}")
            
            # Publish error event
            self.event_bus.publish(
                topic="diplomacy.orchestration.error",
                key=session.session_id,
                value={
                    "orchestration_id": session.context.get("orchestration_id"),
                    "session_id": session.session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Retire shadows
            for shadow in shadows:
                try:
                    self.shadow_manager.retire_shadow(shadow.shadow_id)
                except Exception as shadow_error:
                    self.logger.error(f"Error retiring shadow {shadow.shadow_id}: {str(shadow_error)}")
            
            return {
                "orchestration_id": session.context.get("orchestration_id"),
                "session_id": session.session_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def orchestrate_shadow_comparison(
        self,
        original_id: str,
        shadow_types: List[ShadowType],
        test_cases: Optional[List[Dict[str, Any]]] = None,
        test_count: int = 10
    ) -> Dict[str, Any]:
        """
        Orchestrate comparison of multiple shadow types for a capsule.
        
        Args:
            original_id: Original capsule ID
            shadow_types: List of shadow types to create
            test_cases: List of test cases
            test_count: Number of test cases to generate if not provided
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        # Create shadows for each type
        shadows = []
        
        for shadow_type in shadow_types:
            shadow = self.shadow_manager.create_shadow(
                original_id=original_id,
                shadow_type=shadow_type,
                metadata={
                    "orchestration_type": "comparison",
                    "comparison_group": str(uuid.uuid4())
                }
            )
            
            shadows.append(shadow)
        
        # Generate test cases if not provided
        if not test_cases:
            test_cases = await self.shadow_manager.comparator.generate_test_cases(
                capsule_id=original_id,
                count=test_count
            )
        
        # Initialize result
        orchestration_id = str(uuid.uuid4())
        
        result = {
            "orchestration_id": orchestration_id,
            "original_id": original_id,
            "shadow_ids": [s.shadow_id for s in shadows],
            "shadow_types": [s.shadow_type for s in shadows],
            "comparisons": [],
            "status": "in_progress",
            "started_at": datetime.now().isoformat()
        }
        
        # Start orchestration task
        task = asyncio.create_task(
            self._run_shadow_comparison(
                orchestration_id=orchestration_id,
                original_id=original_id,
                shadows=shadows,
                test_cases=test_cases
            )
        )
        
        self.orchestration_tasks[orchestration_id] = task
        
        self.logger.info(f"Started orchestrated comparison {orchestration_id} for {original_id} with {len(shadows)} shadows")
        
        return result
    
    async def _run_shadow_comparison(
        self,
        orchestration_id: str,
        original_id: str,
        shadows: List[ShadowCapsule],
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run a shadow comparison.
        
        Args:
            orchestration_id: Orchestration ID
            original_id: Original capsule ID
            shadows: List of shadow capsules
            test_cases: List of test cases
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        try:
            # Initialize result
            result = {
                "orchestration_id": orchestration_id,
                "original_id": original_id,
                "shadow_ids": [s.shadow_id for s in shadows],
                "shadow_types": [s.shadow_type for s in shadows],
                "comparisons": [],
                "status": "in_progress",
                "started_at": datetime.now().isoformat()
            }
            
            # Compare each shadow with original
            for shadow in shadows:
                comparison = await self.shadow_manager.compare_with_original(
                    shadow_id=shadow.shadow_id,
                    test_cases=test_cases
                )
                
                # Add to result
                result["comparisons"].append({
                    "shadow_id": shadow.shadow_id,
                    "shadow_type": shadow.shadow_type,
                    "summary": comparison["summary"]
                })
            
            # Finalize result
            result["completed_at"] = datetime.now().isoformat()
            result["status"] = "completed"
            
            # Store result
            self.data_access.create(
                collection="orchestration_results",
                document_id=orchestration_id,
                data=result
            )
            
            # Publish event
            self.event_bus.publish(
                topic="diplomacy.orchestration.completed",
                key=orchestration_id,
                value={
                    "orchestration_id": orchestration_id,
                    "original_id": original_id,
                    "status": "completed",
                    "shadow_count": len(shadows),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Retire shadows
            for shadow in shadows:
                self.shadow_manager.retire_shadow(shadow.shadow_id)
            
            self.logger.info(f"Completed orchestrated comparison {orchestration_id}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in shadow comparison: {str(e)}")
            
            # Publish error event
            self.event_bus.publish(
                topic="diplomacy.orchestration.error",
                key=orchestration_id,
                value={
                    "orchestration_id": orchestration_id,
                    "original_id": original_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Retire shadows
            for shadow in shadows:
                try:
                    self.shadow_manager.retire_shadow(shadow.shadow_id)
                except Exception as shadow_error:
                    self.logger.error(f"Error retiring shadow {shadow.shadow_id}: {str(shadow_error)}")
            
            return {
                "orchestration_id": orchestration_id,
                "original_id": original_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class DigitalTwinDiplomacyService:
    """Service for digital twin diplomacy operations."""
    
    def __init__(
        self,
        service_id: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Digital Twin Diplomacy Service.
        
        Args:
            service_id: Unique identifier for the service
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            data_access: Data access service
            logger: Logger instance
        """
        self.service_id = service_id
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.negotiation_agent = TwinNegotiationAgent(
            agent_id=f"{service_id}-negotiation",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            logger=logger
        )
        
        self.shadow_manager = CapsuleShadowManager(
            agent_id=f"{service_id}-shadow",
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            logger=logger
        )
        
        self.analytics = DiplomacyAnalytics(
            data_access=data_access,
            logger=logger
        )
        
        self.orchestrator = DiplomacyOrchestrator(
            negotiation_agent=self.negotiation_agent,
            shadow_manager=self.shadow_manager,
            mcp_bridge=mcp_bridge,
            a2a_bridge=a2a_bridge,
            event_bus=event_bus,
            data_access=data_access,
            logger=logger
        )
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            topic="diplomacy.service.request",
            group_id=f"digital-twin-diplomacy-service-{self.service_id}",
            callback=self._handle_service_request
        )
        
        # Subscribe to A2A messages
        self.a2a_bridge.subscribe_to_message_type(
            message_type="diplomacy_service_request",
            callback=self._handle_a2a_service_request
        )
    
    def _handle_service_request(self, event: Dict[str, Any]) -> None:
        """
        Handle service request event.
        
        Args:
            event: Event data
        """
        try:
            request_type = event.get("request_type")
            request_id = event.get("request_id", str(uuid.uuid4()))
            
            if not request_type:
                self.logger.error("Invalid service request: missing request_type")
                return
            
            # Handle different request types
            if request_type == "create_negotiation_session":
                self._handle_create_negotiation_session(request_id, event)
            elif request_type == "create_shadow":
                self._handle_create_shadow(request_id, event)
            elif request_type == "orchestrate_negotiation":
                self._handle_orchestrate_negotiation(request_id, event)
            elif request_type == "orchestrate_comparison":
                self._handle_orchestrate_comparison(request_id, event)
            elif request_type == "analyze_negotiations":
                self._handle_analyze_negotiations(request_id, event)
            elif request_type == "analyze_shadows":
                self._handle_analyze_shadows(request_id, event)
            else:
                self.logger.error(f"Unknown request type: {request_type}")
                
                # Publish error response
                self.event_bus.publish(
                    topic="diplomacy.service.response",
                    key=request_id,
                    value={
                        "request_id": request_id,
                        "request_type": request_type,
                        "status": "error",
                        "error": f"Unknown request type: {request_type}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        except Exception as e:
            self.logger.error(f"Error handling service request: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=event.get("request_id", str(uuid.uuid4())),
                value={
                    "request_id": event.get("request_id", str(uuid.uuid4())),
                    "request_type": event.get("request_type", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_create_negotiation_session(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle create negotiation session request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            initiator_id = event.get("initiator_id")
            participants = event.get("participants", [])
            context = event.get("context", {})
            expires_in_hours = event.get("expires_in_hours")
            metadata = event.get("metadata")
            
            if not initiator_id or not participants:
                raise ValueError("Missing required parameters: initiator_id or participants")
            
            session = self.negotiation_agent.create_negotiation_session(
                initiator_id=initiator_id,
                participants=participants,
                context=context,
                expires_in_hours=expires_in_hours,
                metadata=metadata
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "create_negotiation_session",
                    "status": "success",
                    "session_id": session.session_id,
                    "initiator_id": initiator_id,
                    "participants": participants,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error creating negotiation session: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "create_negotiation_session",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_create_shadow(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle create shadow request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            original_id = event.get("original_id")
            shadow_type_str = event.get("shadow_type")
            capabilities = event.get("capabilities")
            state = event.get("state")
            metadata = event.get("metadata")
            auto_sync = event.get("auto_sync", True)
            sync_interval = event.get("sync_interval", 60)
            isolation_boundary = event.get("isolation_boundary")
            monitor = event.get("monitor", True)
            
            if not original_id or not shadow_type_str:
                raise ValueError("Missing required parameters: original_id or shadow_type")
            
            # Convert string enum to enum value
            shadow_type = ShadowType(shadow_type_str)
            
            shadow = self.shadow_manager.create_shadow(
                original_id=original_id,
                shadow_type=shadow_type,
                capabilities=capabilities,
                state=state,
                metadata=metadata,
                auto_sync=auto_sync,
                sync_interval=sync_interval,
                isolation_boundary=isolation_boundary,
                monitor=monitor
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "create_shadow",
                    "status": "success",
                    "shadow_id": shadow.shadow_id,
                    "original_id": original_id,
                    "shadow_type": shadow_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error creating shadow: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "create_shadow",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_orchestrate_negotiation(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle orchestrate negotiation request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            original_ids = event.get("original_ids", [])
            resource_specifications_data = event.get("resource_specifications", {})
            shadow_type_str = event.get("shadow_type", "negotiation")
            strategy = event.get("strategy", "collaborative")
            max_rounds = event.get("max_rounds", 10)
            timeout_minutes = event.get("timeout_minutes", 30)
            
            if not original_ids or not resource_specifications_data:
                raise ValueError("Missing required parameters: original_ids or resource_specifications")
            
            # Convert string enum to enum value
            shadow_type = ShadowType(shadow_type_str)
            
            # Convert resource specifications data
            resource_specifications = {}
            
            for original_id, resources_data in resource_specifications_data.items():
                resource_specifications[original_id] = [
                    ResourceSpecification.from_dict(r) for r in resources_data
                ]
            
            # Start orchestration
            asyncio.create_task(
                self._handle_orchestrate_negotiation_async(
                    request_id=request_id,
                    original_ids=original_ids,
                    resource_specifications=resource_specifications,
                    shadow_type=shadow_type,
                    strategy=strategy,
                    max_rounds=max_rounds,
                    timeout_minutes=timeout_minutes
                )
            )
        
        except Exception as e:
            self.logger.error(f"Error orchestrating negotiation: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_negotiation",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _handle_orchestrate_negotiation_async(
        self,
        request_id: str,
        original_ids: List[str],
        resource_specifications: Dict[str, List[ResourceSpecification]],
        shadow_type: ShadowType,
        strategy: str,
        max_rounds: int,
        timeout_minutes: int
    ) -> None:
        """
        Handle orchestrate negotiation request asynchronously.
        
        Args:
            request_id: Request ID
            original_ids: List of original capsule IDs
            resource_specifications: Resource specifications by capsule ID
            shadow_type: Type of shadow to create
            strategy: Negotiation strategy
            max_rounds: Maximum negotiation rounds
            timeout_minutes: Negotiation timeout in minutes
        """
        try:
            # Start orchestration
            result = await self.orchestrator.orchestrate_negotiation_with_shadows(
                original_ids=original_ids,
                resource_specifications=resource_specifications,
                shadow_type=shadow_type,
                strategy=strategy,
                max_rounds=max_rounds,
                timeout_minutes=timeout_minutes
            )
            
            # Publish initial response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_negotiation",
                    "status": "started",
                    "orchestration_id": result["orchestration_id"],
                    "session_id": result["session_id"],
                    "shadow_ids": result["shadow_ids"],
                    "original_ids": original_ids,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error in orchestrate negotiation async handler: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_negotiation",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_orchestrate_comparison(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle orchestrate comparison request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            original_id = event.get("original_id")
            shadow_types_str = event.get("shadow_types", [])
            test_cases = event.get("test_cases")
            test_count = event.get("test_count", 10)
            
            if not original_id or not shadow_types_str:
                raise ValueError("Missing required parameters: original_id or shadow_types")
            
            # Convert string enums to enum values
            shadow_types = [ShadowType(t) for t in shadow_types_str]
            
            # Start orchestration
            asyncio.create_task(
                self._handle_orchestrate_comparison_async(
                    request_id=request_id,
                    original_id=original_id,
                    shadow_types=shadow_types,
                    test_cases=test_cases,
                    test_count=test_count
                )
            )
        
        except Exception as e:
            self.logger.error(f"Error orchestrating comparison: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_comparison",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _handle_orchestrate_comparison_async(
        self,
        request_id: str,
        original_id: str,
        shadow_types: List[ShadowType],
        test_cases: Optional[List[Dict[str, Any]]],
        test_count: int
    ) -> None:
        """
        Handle orchestrate comparison request asynchronously.
        
        Args:
            request_id: Request ID
            original_id: Original capsule ID
            shadow_types: List of shadow types to create
            test_cases: List of test cases
            test_count: Number of test cases to generate if not provided
        """
        try:
            # Start orchestration
            result = await self.orchestrator.orchestrate_shadow_comparison(
                original_id=original_id,
                shadow_types=shadow_types,
                test_cases=test_cases,
                test_count=test_count
            )
            
            # Publish initial response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_comparison",
                    "status": "started",
                    "orchestration_id": result["orchestration_id"],
                    "original_id": original_id,
                    "shadow_ids": result["shadow_ids"],
                    "shadow_types": [str(t) for t in shadow_types],
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error in orchestrate comparison async handler: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "orchestrate_comparison",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_analyze_negotiations(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle analyze negotiations request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            agent_ids = event.get("agent_ids")
            resource_types = event.get("resource_types")
            
            # Perform analysis
            results = self.analytics.analyze_negotiation_patterns(
                time_period=time_period,
                agent_ids=agent_ids,
                resource_types=resource_types
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "analyze_negotiations",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing negotiations: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "analyze_negotiations",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_analyze_shadows(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle analyze shadows request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            shadow_types = event.get("shadow_types")
            original_ids = event.get("original_ids")
            
            # Perform analysis
            results = self.analytics.analyze_shadow_performance(
                time_period=time_period,
                shadow_types=shadow_types,
                original_ids=original_ids
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "analyze_shadows",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing shadows: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.service.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "analyze_shadows",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_a2a_service_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A service request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            sender_id = message.get("sender_id")
            
            request_type = content.get("request_type")
            request_id = content.get("request_id", str(uuid.uuid4()))
            
            if not request_type:
                self.logger.error("Invalid A2A service request: missing request_type")
                return
            
            # Convert A2A message to event
            event = {
                "request_id": request_id,
                "request_type": request_type,
                "sender_id": sender_id,
                **content
            }
            
            # Handle request
            self._handle_service_request(event)
            
            # Subscribe to response for this request
            self.event_bus.subscribe(
                topic="diplomacy.service.response",
                group_id=f"a2a-response-handler-{request_id}",
                callback=lambda response: self._handle_a2a_response(response, sender_id),
                auto_unsubscribe=True
            )
        
        except Exception as e:
            self.logger.error(f"Error handling A2A service request: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="diplomacy_service_response",
                sender_id=self.service_id,
                recipient_id=message.get("sender_id"),
                content={
                    "request_id": message.get("content", {}).get("request_id", str(uuid.uuid4())),
                    "request_type": message.get("content", {}).get("request_type", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_a2a_response(self, response: Dict[str, Any], recipient_id: str) -> None:
        """
        Handle A2A response.
        
        Args:
            response: Response data
            recipient_id: Recipient ID
        """
        try:
            # Send response via A2A
            self.a2a_bridge.send_message(
                message_type="diplomacy_service_response",
                sender_id=self.service_id,
                recipient_id=recipient_id,
                content=response
            )
        
        except Exception as e:
            self.logger.error(f"Error handling A2A response: {str(e)}")
    
    def start(self) -> None:
        """Start the service."""
        self.logger.info(f"Starting Digital Twin Diplomacy Service {self.service_id}")
        
        # Publish service started event
        self.event_bus.publish(
            topic="diplomacy.service.status",
            key=self.service_id,
            value={
                "service_id": self.service_id,
                "status": "started",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def stop(self) -> None:
        """Stop the service."""
        self.logger.info(f"Stopping Digital Twin Diplomacy Service {self.service_id}")
        
        # Publish service stopped event
        self.event_bus.publish(
            topic="diplomacy.service.status",
            key=self.service_id,
            value={
                "service_id": self.service_id,
                "status": "stopped",
                "timestamp": datetime.now().isoformat()
            }
        )
