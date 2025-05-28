"""
Generated Capsule Evaluator for the Overseer System.

This module provides comprehensive evaluation capabilities for generated capsules,
enabling quality assessment, performance measurement, and compliance verification.

The Generated Capsule Evaluator is a critical component of the Capsule Evolution phase,
providing mechanisms for evaluating and ranking generated capsules based on multiple criteria.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import os
import time
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Set

from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, status
from pydantic import BaseModel, Field, validator

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
logger = logging.getLogger("generated_capsule_evaluator")

# Initialize MCP/A2A bridges
mcp_bridge = MCPProtocolBridge()
a2a_bridge = A2AProtocolBridge()

# Initialize Kafka producer/consumer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    client_id="generated-capsule-evaluator"
)

kafka_consumer = KafkaConsumer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    group_id="generated-capsule-evaluator",
    auto_offset_reset="earliest"
)

# Data models
class CapsuleEvaluationCriteria(BaseModel):
    """Model for capsule evaluation criteria."""
    criteria_id: str = Field(..., description="Unique criteria identifier")
    name: str = Field(..., description="Criteria name")
    description: str = Field(..., description="Criteria description")
    weight: float = Field(1.0, description="Criteria weight (0.0 to 10.0)")
    evaluation_method: str = Field(..., description="Evaluation method (automated, semi-automated, manual)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Evaluation parameters")
    threshold: Optional[float] = Field(None, description="Minimum acceptable score (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvaluationResult(BaseModel):
    """Model for capsule evaluation result."""
    result_id: str = Field(..., description="Unique result identifier")
    capsule_id: str = Field(..., description="Capsule ID")
    evaluator_id: str = Field(..., description="Evaluator ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Evaluation timestamp")
    criteria_scores: Dict[str, float] = Field(default_factory=dict, description="Scores by criteria ID")
    overall_score: float = Field(..., description="Overall evaluation score (0.0 to 1.0)")
    passed_threshold: bool = Field(True, description="Whether capsule passed minimum threshold")
    notes: Optional[str] = Field(None, description="Evaluation notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvaluationRequest(BaseModel):
    """Model for capsule evaluation request."""
    request_id: str = Field(..., description="Unique request identifier")
    capsule_id: str = Field(..., description="Capsule ID to evaluate")
    criteria_ids: List[str] = Field(default_factory=list, description="Criteria IDs to apply")
    evaluator_id: Optional[str] = Field(None, description="Specific evaluator ID")
    evaluation_context: Dict[str, Any] = Field(default_factory=dict, description="Evaluation context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleComparisonRequest(BaseModel):
    """Model for capsule comparison request."""
    request_id: str = Field(..., description="Unique request identifier")
    capsule_ids: List[str] = Field(..., description="List of capsule IDs to compare")
    criteria_ids: List[str] = Field(default_factory=list, description="Criteria IDs to apply")
    comparison_method: str = Field("pairwise", description="Comparison method (pairwise, ranking)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleComparisonResult(BaseModel):
    """Model for capsule comparison result."""
    result_id: str = Field(..., description="Unique result identifier")
    request_id: str = Field(..., description="Request ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Comparison timestamp")
    capsule_rankings: Dict[str, int] = Field(default_factory=dict, description="Rankings by capsule ID")
    pairwise_results: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Pairwise comparison results")
    best_capsule_id: Optional[str] = Field(None, description="Best capsule ID")
    notes: Optional[str] = Field(None, description="Comparison notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvaluationBatch(BaseModel):
    """Model for capsule evaluation batch."""
    batch_id: str = Field(..., description="Unique batch identifier")
    name: str = Field(..., description="Batch name")
    description: Optional[str] = Field(None, description="Batch description")
    capsule_ids: List[str] = Field(..., description="List of capsule IDs in batch")
    criteria_ids: List[str] = Field(..., description="List of criteria IDs to apply")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    status: str = Field("pending", description="Batch status (pending, in_progress, completed, failed)")
    progress: float = Field(0.0, description="Batch progress (0.0 to 1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CapsuleEvaluationBatchResult(BaseModel):
    """Model for capsule evaluation batch result."""
    batch_result_id: str = Field(..., description="Unique batch result identifier")
    batch_id: str = Field(..., description="Batch ID")
    completed_at: datetime = Field(default_factory=datetime.now, description="Completion timestamp")
    evaluation_results: Dict[str, str] = Field(default_factory=dict, description="Evaluation result IDs by capsule ID")
    summary_statistics: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
    best_capsule_id: Optional[str] = Field(None, description="Best capsule ID")
    notes: Optional[str] = Field(None, description="Batch evaluation notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# In-memory storage (would be replaced with database in production)
evaluation_criteria = {}
evaluation_results = {}
comparison_results = {}
evaluation_batches = {}
batch_results = {}

class CriteriaManager:
    """
    Manages evaluation criteria for capsules.
    
    This class provides methods for creating, retrieving, updating, and managing
    evaluation criteria.
    """
    
    def __init__(self):
        """Initialize the Criteria Manager."""
        logger.info("Criteria Manager initialized")
        
        # Initialize with default criteria if none exist
        if not evaluation_criteria:
            self._initialize_default_criteria()
    
    def _initialize_default_criteria(self):
        """Initialize default evaluation criteria."""
        default_criteria = [
            CapsuleEvaluationCriteria(
                criteria_id="criteria-performance",
                name="Performance Efficiency",
                description="Evaluates the computational efficiency and resource usage of the capsule",
                weight=8.0,
                evaluation_method="automated",
                parameters={
                    "metrics": ["execution_time", "memory_usage", "cpu_usage"],
                    "baseline_comparison": True
                },
                threshold=0.6
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-accuracy",
                name="Task Accuracy",
                description="Evaluates the accuracy of the capsule in performing its designated tasks",
                weight=9.0,
                evaluation_method="automated",
                parameters={
                    "test_cases": 50,
                    "validation_dataset": "standard",
                    "metrics": ["precision", "recall", "f1_score"]
                },
                threshold=0.7
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-robustness",
                name="Operational Robustness",
                description="Evaluates the capsule's ability to handle edge cases and unexpected inputs",
                weight=7.5,
                evaluation_method="automated",
                parameters={
                    "edge_case_scenarios": 20,
                    "fault_injection": True,
                    "recovery_time_measurement": True
                },
                threshold=0.65
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-compliance",
                name="Regulatory Compliance",
                description="Evaluates the capsule's adherence to regulatory requirements and standards",
                weight=9.5,
                evaluation_method="semi-automated",
                parameters={
                    "compliance_frameworks": ["ISO27001", "GDPR", "HIPAA"],
                    "audit_trail_verification": True
                },
                threshold=0.8
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-integration",
                name="System Integration",
                description="Evaluates how well the capsule integrates with other system components",
                weight=8.0,
                evaluation_method="automated",
                parameters={
                    "interface_compatibility": True,
                    "data_flow_validation": True,
                    "dependency_management": True
                },
                threshold=0.7
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-security",
                name="Security Posture",
                description="Evaluates the capsule's security features and vulnerability resistance",
                weight=9.0,
                evaluation_method="automated",
                parameters={
                    "vulnerability_scan": True,
                    "penetration_testing": True,
                    "secure_coding_practices": True
                },
                threshold=0.75
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-adaptability",
                name="Environmental Adaptability",
                description="Evaluates the capsule's ability to adapt to different operational environments",
                weight=7.0,
                evaluation_method="automated",
                parameters={
                    "environment_variations": 5,
                    "configuration_flexibility": True,
                    "adaptation_speed": True
                },
                threshold=0.6
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-usability",
                name="User Experience",
                description="Evaluates the capsule's usability and interaction quality",
                weight=6.5,
                evaluation_method="semi-automated",
                parameters={
                    "interaction_metrics": ["response_time", "clarity", "helpfulness"],
                    "user_satisfaction_simulation": True
                },
                threshold=0.65
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-innovation",
                name="Innovation Factor",
                description="Evaluates the capsule's innovative features and approaches",
                weight=5.0,
                evaluation_method="manual",
                parameters={
                    "novelty_assessment": True,
                    "competitive_advantage": True,
                    "future_potential": True
                },
                threshold=0.5
            ),
            CapsuleEvaluationCriteria(
                criteria_id="criteria-documentation",
                name="Documentation Quality",
                description="Evaluates the quality and completeness of the capsule's documentation",
                weight=6.0,
                evaluation_method="semi-automated",
                parameters={
                    "completeness_check": True,
                    "clarity_assessment": True,
                    "example_coverage": True
                },
                threshold=0.7
            )
        ]
        
        for criteria in default_criteria:
            self.create_criteria(criteria)
    
    def create_criteria(self, criteria: CapsuleEvaluationCriteria) -> str:
        """
        Create a new evaluation criteria.
        
        Args:
            criteria: The evaluation criteria to create
            
        Returns:
            str: The criteria ID
        """
        # Store the criteria
        evaluation_criteria[criteria.criteria_id] = criteria.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="evaluation-criteria",
            key=criteria.criteria_id,
            value=json.dumps({
                "action": "create",
                "criteria_id": criteria.criteria_id,
                "name": criteria.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "evaluation_criteria_created",
            "criteria_id": criteria.criteria_id,
            "name": criteria.name
        }
        mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="generated_capsule_evaluator",
            message={
                "type": "evaluation_criteria_created",
                "criteria_id": criteria.criteria_id,
                "name": criteria.name
            }
        )
        
        return criteria.criteria_id
    
    def get_criteria(self, criteria_id: str) -> Optional[CapsuleEvaluationCriteria]:
        """
        Get an evaluation criteria by ID.
        
        Args:
            criteria_id: The criteria ID
            
        Returns:
            Optional[CapsuleEvaluationCriteria]: The criteria, or None if not found
        """
        if criteria_id not in evaluation_criteria:
            return None
        
        return CapsuleEvaluationCriteria(**evaluation_criteria[criteria_id])
    
    def update_criteria(self, criteria_id: str, criteria: CapsuleEvaluationCriteria) -> bool:
        """
        Update an evaluation criteria.
        
        Args:
            criteria_id: The criteria ID to update
            criteria: The updated criteria
            
        Returns:
            bool: True if successful, False if criteria not found
        """
        if criteria_id not in evaluation_criteria:
            return False
        
        # Update the criteria
        evaluation_criteria[criteria_id] = criteria.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="evaluation-criteria",
            key=criteria_id,
            value=json.dumps({
                "action": "update",
                "criteria_id": criteria_id,
                "name": criteria.name
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "evaluation_criteria_updated",
            "criteria_id": criteria_id,
            "name": criteria.name
        }
        mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="generated_capsule_evaluator",
            message={
                "type": "evaluation_criteria_updated",
                "criteria_id": criteria_id,
                "name": criteria.name
            }
        )
        
        return True
    
    def delete_criteria(self, criteria_id: str) -> bool:
        """
        Delete an evaluation criteria.
        
        Args:
            criteria_id: The criteria ID to delete
            
        Returns:
            bool: True if successful, False if criteria not found
        """
        if criteria_id not in evaluation_criteria:
            return False
        
        # Get criteria info before deletion
        criteria_info = evaluation_criteria[criteria_id]
        
        # Delete the criteria
        del evaluation_criteria[criteria_id]
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="evaluation-criteria",
            key=criteria_id,
            value=json.dumps({
                "action": "delete",
                "criteria_id": criteria_id,
                "name": criteria_info["name"]
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "evaluation_criteria_deleted",
            "criteria_id": criteria_id,
            "name": criteria_info["name"]
        }
        mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="generated_capsule_evaluator",
            message={
                "type": "evaluation_criteria_deleted",
                "criteria_id": criteria_id,
                "name": criteria_info["name"]
            }
        )
        
        return True
    
    def list_criteria(
        self,
        method_filter: Optional[str] = None,
        min_weight: Optional[float] = None,
        max_weight: Optional[float] = None,
        min_threshold: Optional[float] = None,
        limit: int = 100
    ) -> List[CapsuleEvaluationCriteria]:
        """
        List evaluation criteria, optionally filtered.
        
        Args:
            method_filter: Optional filter for evaluation method
            min_weight: Optional minimum weight
            max_weight: Optional maximum weight
            min_threshold: Optional minimum threshold
            limit: Maximum number of criteria to return
            
        Returns:
            List[CapsuleEvaluationCriteria]: List of matching criteria
        """
        results = []
        
        for criteria_dict in evaluation_criteria.values():
            # Apply filters
            if method_filter and criteria_dict["evaluation_method"] != method_filter:
                continue
            
            if min_weight is not None and criteria_dict["weight"] < min_weight:
                continue
            
            if max_weight is not None and criteria_dict["weight"] > max_weight:
                continue
            
            if min_threshold is not None and (criteria_dict["threshold"] is None or criteria_dict["threshold"] < min_threshold):
                continue
            
            results.append(CapsuleEvaluationCriteria(**criteria_dict))
        
        # Sort by weight (highest first)
        results.sort(key=lambda c: c.weight, reverse=True)
        
        # Apply limit
        return results[:limit]

class EvaluationEngine:
    """
    Performs evaluations of generated capsules.
    
    This class provides methods for evaluating capsules against criteria,
    comparing multiple capsules, and managing evaluation batches.
    """
    
    def __init__(self, criteria_manager: CriteriaManager):
        """
        Initialize the Evaluation Engine.
        
        Args:
            criteria_manager: Criteria manager instance
        """
        self.criteria_manager = criteria_manager
        logger.info("Evaluation Engine initialized")
    
    def evaluate_capsule(self, request: CapsuleEvaluationRequest) -> CapsuleEvaluationResult:
        """
        Evaluate a capsule against specified criteria.
        
        Args:
            request: The evaluation request
            
        Returns:
            CapsuleEvaluationResult: The evaluation result
        """
        result_id = f"eval-result-{uuid.uuid4()}"
        
        try:
            # Get criteria to evaluate against
            criteria_list = []
            if request.criteria_ids:
                for criteria_id in request.criteria_ids:
                    criteria = self.criteria_manager.get_criteria(criteria_id)
                    if criteria:
                        criteria_list.append(criteria)
            else:
                # Use all criteria
                criteria_list = self.criteria_manager.list_criteria(limit=1000)
            
            if not criteria_list:
                raise ValueError("No valid evaluation criteria specified")
            
            # Perform evaluation for each criteria
            criteria_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            passed_threshold = True
            
            for criteria in criteria_list:
                # Evaluate the capsule against this criteria
                score = self._evaluate_against_criteria(
                    capsule_id=request.capsule_id,
                    criteria=criteria,
                    context=request.evaluation_context
                )
                
                criteria_scores[criteria.criteria_id] = score
                total_weighted_score += score * criteria.weight
                total_weight += criteria.weight
                
                # Check if passed threshold
                if criteria.threshold is not None and score < criteria.threshold:
                    passed_threshold = False
            
            # Calculate overall score
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Create the result
            result = CapsuleEvaluationResult(
                result_id=result_id,
                capsule_id=request.capsule_id,
                evaluator_id=request.evaluator_id or "system",
                criteria_scores=criteria_scores,
                overall_score=overall_score,
                passed_threshold=passed_threshold,
                notes=f"Evaluated against {len(criteria_list)} criteria",
                metadata={
                    "request_id": request.request_id,
                    "criteria_count": len(criteria_list),
                    "evaluation_context": request.evaluation_context
                }
            )
            
            # Store the result
            evaluation_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-evaluation-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "capsule_id": request.capsule_id,
                    "overall_score": overall_score,
                    "passed_threshold": passed_threshold
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "capsule_evaluated",
                "result_id": result_id,
                "capsule_id": request.capsule_id,
                "overall_score": overall_score,
                "passed_threshold": passed_threshold
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "capsule_evaluated",
                    "result_id": result_id,
                    "capsule_id": request.capsule_id,
                    "overall_score": overall_score,
                    "passed_threshold": passed_threshold
                }
            )
            
            return result
        
        except Exception as e:
            # Create error result
            result = CapsuleEvaluationResult(
                result_id=result_id,
                capsule_id=request.capsule_id,
                evaluator_id=request.evaluator_id or "system",
                criteria_scores={},
                overall_score=0.0,
                passed_threshold=False,
                notes=f"Evaluation failed: {str(e)}",
                metadata={
                    "request_id": request.request_id,
                    "error": str(e)
                }
            )
            
            # Store the result
            evaluation_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-evaluation-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "capsule_id": request.capsule_id,
                    "error": str(e)
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "capsule_evaluation_failed",
                "result_id": result_id,
                "capsule_id": request.capsule_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "capsule_evaluation_failed",
                    "result_id": result_id,
                    "capsule_id": request.capsule_id,
                    "error": str(e)
                }
            )
            
            return result
    
    def compare_capsules(self, request: CapsuleComparisonRequest) -> CapsuleComparisonResult:
        """
        Compare multiple capsules against each other.
        
        Args:
            request: The comparison request
            
        Returns:
            CapsuleComparisonResult: The comparison result
        """
        result_id = f"comp-result-{uuid.uuid4()}"
        
        try:
            if len(request.capsule_ids) < 2:
                raise ValueError("At least two capsules are required for comparison")
            
            # Get criteria to evaluate against
            criteria_list = []
            if request.criteria_ids:
                for criteria_id in request.criteria_ids:
                    criteria = self.criteria_manager.get_criteria(criteria_id)
                    if criteria:
                        criteria_list.append(criteria)
            else:
                # Use all criteria
                criteria_list = self.criteria_manager.list_criteria(limit=1000)
            
            if not criteria_list:
                raise ValueError("No valid evaluation criteria specified")
            
            # Evaluate each capsule
            capsule_scores = {}
            for capsule_id in request.capsule_ids:
                # Create evaluation request
                eval_request = CapsuleEvaluationRequest(
                    request_id=f"comp-eval-{uuid.uuid4()}",
                    capsule_id=capsule_id,
                    criteria_ids=[c.criteria_id for c in criteria_list],
                    evaluator_id="comparison-engine",
                    evaluation_context={"comparison_request_id": request.request_id},
                    metadata={"part_of_comparison": True}
                )
                
                # Evaluate the capsule
                eval_result = self.evaluate_capsule(eval_request)
                
                # Store the result
                capsule_scores[capsule_id] = eval_result.overall_score
            
            # Perform comparison based on method
            if request.comparison_method == "pairwise":
                # Pairwise comparison
                pairwise_results = self._perform_pairwise_comparison(capsule_scores)
                
                # Calculate rankings based on pairwise wins
                capsule_rankings = self._calculate_rankings_from_pairwise(pairwise_results)
            else:
                # Direct ranking based on overall scores
                capsule_rankings = self._calculate_direct_rankings(capsule_scores)
                
                # Create empty pairwise results
                pairwise_results = {}
            
            # Determine best capsule
            best_capsule_id = None
            best_rank = float('inf')
            for capsule_id, rank in capsule_rankings.items():
                if rank < best_rank:
                    best_rank = rank
                    best_capsule_id = capsule_id
            
            # Create the result
            result = CapsuleComparisonResult(
                result_id=result_id,
                request_id=request.request_id,
                capsule_rankings=capsule_rankings,
                pairwise_results=pairwise_results,
                best_capsule_id=best_capsule_id,
                notes=f"Compared {len(request.capsule_ids)} capsules using {request.comparison_method} method",
                metadata={
                    "capsule_count": len(request.capsule_ids),
                    "criteria_count": len(criteria_list),
                    "comparison_method": request.comparison_method,
                    "capsule_scores": capsule_scores
                }
            )
            
            # Store the result
            comparison_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-comparison-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "best_capsule_id": best_capsule_id
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "capsules_compared",
                "result_id": result_id,
                "request_id": request.request_id,
                "best_capsule_id": best_capsule_id
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "capsules_compared",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "best_capsule_id": best_capsule_id
                }
            )
            
            return result
        
        except Exception as e:
            # Create error result
            result = CapsuleComparisonResult(
                result_id=result_id,
                request_id=request.request_id,
                capsule_rankings={},
                pairwise_results={},
                best_capsule_id=None,
                notes=f"Comparison failed: {str(e)}",
                metadata={
                    "error": str(e)
                }
            )
            
            # Store the result
            comparison_results[result_id] = result.dict()
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="capsule-comparison-results",
                key=result_id,
                value=json.dumps({
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "error": str(e)
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "capsule_comparison_failed",
                "result_id": result_id,
                "request_id": request.request_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "capsule_comparison_failed",
                    "result_id": result_id,
                    "request_id": request.request_id,
                    "error": str(e)
                }
            )
            
            return result
    
    def create_evaluation_batch(self, batch: CapsuleEvaluationBatch) -> str:
        """
        Create a new evaluation batch.
        
        Args:
            batch: The evaluation batch to create
            
        Returns:
            str: The batch ID
        """
        # Store the batch
        evaluation_batches[batch.batch_id] = batch.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="evaluation-batches",
            key=batch.batch_id,
            value=json.dumps({
                "action": "create",
                "batch_id": batch.batch_id,
                "name": batch.name,
                "capsule_count": len(batch.capsule_ids)
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "evaluation_batch_created",
            "batch_id": batch.batch_id,
            "name": batch.name,
            "capsule_count": len(batch.capsule_ids)
        }
        mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="generated_capsule_evaluator",
            message={
                "type": "evaluation_batch_created",
                "batch_id": batch.batch_id,
                "name": batch.name,
                "capsule_count": len(batch.capsule_ids)
            }
        )
        
        return batch.batch_id
    
    def get_evaluation_batch(self, batch_id: str) -> Optional[CapsuleEvaluationBatch]:
        """
        Get an evaluation batch by ID.
        
        Args:
            batch_id: The batch ID
            
        Returns:
            Optional[CapsuleEvaluationBatch]: The batch, or None if not found
        """
        if batch_id not in evaluation_batches:
            return None
        
        return CapsuleEvaluationBatch(**evaluation_batches[batch_id])
    
    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        progress: float,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of an evaluation batch.
        
        Args:
            batch_id: The batch ID
            status: The new status
            progress: The new progress value (0.0 to 1.0)
            notes: Optional status notes
            
        Returns:
            bool: True if successful, False if batch not found
        """
        if batch_id not in evaluation_batches:
            return False
        
        # Get the batch
        batch = CapsuleEvaluationBatch(**evaluation_batches[batch_id])
        
        # Update status and progress
        batch.status = status
        batch.progress = progress
        if notes:
            batch.metadata["status_notes"] = notes
        
        # Store the updated batch
        evaluation_batches[batch_id] = batch.dict()
        
        # Publish event to Kafka
        kafka_producer.produce(
            topic="evaluation-batches",
            key=batch_id,
            value=json.dumps({
                "action": "update",
                "batch_id": batch_id,
                "status": status,
                "progress": progress
            })
        )
        
        # Notify via MCP
        mcp_context = {
            "action": "evaluation_batch_updated",
            "batch_id": batch_id,
            "status": status,
            "progress": progress
        }
        mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
        
        # Notify via A2A
        a2a_bridge.send_agent_message(
            agent_id="generated_capsule_evaluator",
            message={
                "type": "evaluation_batch_updated",
                "batch_id": batch_id,
                "status": status,
                "progress": progress
            }
        )
        
        return True
    
    def process_evaluation_batch(self, batch_id: str) -> Optional[CapsuleEvaluationBatchResult]:
        """
        Process an evaluation batch.
        
        Args:
            batch_id: The batch ID to process
            
        Returns:
            Optional[CapsuleEvaluationBatchResult]: The batch result, or None if batch not found
        """
        batch = self.get_evaluation_batch(batch_id)
        if not batch:
            return None
        
        # Update batch status to in_progress
        self.update_batch_status(
            batch_id=batch_id,
            status="in_progress",
            progress=0.0,
            notes="Starting batch evaluation"
        )
        
        try:
            # Create batch result
            batch_result_id = f"batch-result-{uuid.uuid4()}"
            evaluation_results_map = {}
            
            # Process each capsule in the batch
            total_capsules = len(batch.capsule_ids)
            for i, capsule_id in enumerate(batch.capsule_ids):
                # Create evaluation request
                eval_request = CapsuleEvaluationRequest(
                    request_id=f"batch-eval-{uuid.uuid4()}",
                    capsule_id=capsule_id,
                    criteria_ids=batch.criteria_ids,
                    evaluator_id="batch-processor",
                    evaluation_context={"batch_id": batch_id},
                    metadata={"part_of_batch": True}
                )
                
                # Evaluate the capsule
                eval_result = self.evaluate_capsule(eval_request)
                
                # Store the result
                evaluation_results_map[capsule_id] = eval_result.result_id
                
                # Update batch progress
                progress = (i + 1) / total_capsules
                self.update_batch_status(
                    batch_id=batch_id,
                    status="in_progress",
                    progress=progress,
                    notes=f"Processed {i + 1} of {total_capsules} capsules"
                )
            
            # Calculate summary statistics
            summary_statistics = self._calculate_batch_statistics(evaluation_results_map)
            
            # Determine best capsule
            best_capsule_id = None
            best_score = -1.0
            
            for capsule_id, result_id in evaluation_results_map.items():
                result = self.get_evaluation_result(result_id)
                if result and result.overall_score > best_score:
                    best_score = result.overall_score
                    best_capsule_id = capsule_id
            
            # Create batch result
            batch_result = CapsuleEvaluationBatchResult(
                batch_result_id=batch_result_id,
                batch_id=batch_id,
                evaluation_results=evaluation_results_map,
                summary_statistics=summary_statistics,
                best_capsule_id=best_capsule_id,
                notes=f"Successfully evaluated {total_capsules} capsules",
                metadata={
                    "completion_time": datetime.now().isoformat(),
                    "criteria_ids": batch.criteria_ids
                }
            )
            
            # Store the batch result
            batch_results[batch_result_id] = batch_result.dict()
            
            # Update batch status to completed
            self.update_batch_status(
                batch_id=batch_id,
                status="completed",
                progress=1.0,
                notes=f"Batch evaluation completed successfully. Best capsule: {best_capsule_id}"
            )
            
            # Publish event to Kafka
            kafka_producer.produce(
                topic="evaluation-batch-results",
                key=batch_result_id,
                value=json.dumps({
                    "batch_result_id": batch_result_id,
                    "batch_id": batch_id,
                    "best_capsule_id": best_capsule_id
                })
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "evaluation_batch_completed",
                "batch_result_id": batch_result_id,
                "batch_id": batch_id,
                "best_capsule_id": best_capsule_id
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "evaluation_batch_completed",
                    "batch_result_id": batch_result_id,
                    "batch_id": batch_id,
                    "best_capsule_id": best_capsule_id
                }
            )
            
            return batch_result
        
        except Exception as e:
            # Update batch status to failed
            self.update_batch_status(
                batch_id=batch_id,
                status="failed",
                progress=0.0,
                notes=f"Batch evaluation failed: {str(e)}"
            )
            
            # Notify via MCP
            mcp_context = {
                "action": "evaluation_batch_failed",
                "batch_id": batch_id,
                "error": str(e)
            }
            mcp_bridge.send_context_update("generated_capsule_evaluator", mcp_context)
            
            # Notify via A2A
            a2a_bridge.send_agent_message(
                agent_id="generated_capsule_evaluator",
                message={
                    "type": "evaluation_batch_failed",
                    "batch_id": batch_id,
                    "error": str(e)
                }
            )
            
            return None
    
    def get_evaluation_result(self, result_id: str) -> Optional[CapsuleEvaluationResult]:
        """
        Get an evaluation result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[CapsuleEvaluationResult]: The result, or None if not found
        """
        if result_id not in evaluation_results:
            return None
        
        return CapsuleEvaluationResult(**evaluation_results[result_id])
    
    def get_comparison_result(self, result_id: str) -> Optional[CapsuleComparisonResult]:
        """
        Get a comparison result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[CapsuleComparisonResult]: The result, or None if not found
        """
        if result_id not in comparison_results:
            return None
        
        return CapsuleComparisonResult(**comparison_results[result_id])
    
    def get_batch_result(self, batch_result_id: str) -> Optional[CapsuleEvaluationBatchResult]:
        """
        Get a batch result by ID.
        
        Args:
            batch_result_id: The batch result ID
            
        Returns:
            Optional[CapsuleEvaluationBatchResult]: The result, or None if not found
        """
        if batch_result_id not in batch_results:
            return None
        
        return CapsuleEvaluationBatchResult(**batch_results[batch_result_id])
    
    def _evaluate_against_criteria(
        self,
        capsule_id: str,
        criteria: CapsuleEvaluationCriteria,
        context: Dict[str, Any]
    ) -> float:
        """
        Evaluate a capsule against a specific criteria.
        
        Args:
            capsule_id: The capsule ID
            criteria: The evaluation criteria
            context: Evaluation context
            
        Returns:
            float: Evaluation score (0.0 to 1.0)
        """
        # This is a simplified implementation
        # In production, this would use more sophisticated techniques
        
        # Simulate evaluation based on criteria type
        if criteria.evaluation_method == "automated":
            # Simulate automated evaluation
            return self._simulate_automated_evaluation(capsule_id, criteria, context)
        
        elif criteria.evaluation_method == "semi-automated":
            # Simulate semi-automated evaluation
            return self._simulate_semi_automated_evaluation(capsule_id, criteria, context)
        
        else:  # manual
            # Simulate manual evaluation
            return self._simulate_manual_evaluation(capsule_id, criteria, context)
    
    def _simulate_automated_evaluation(
        self,
        capsule_id: str,
        criteria: CapsuleEvaluationCriteria,
        context: Dict[str, Any]
    ) -> float:
        """
        Simulate automated evaluation.
        
        Args:
            capsule_id: The capsule ID
            criteria: The evaluation criteria
            context: Evaluation context
            
        Returns:
            float: Evaluation score (0.0 to 1.0)
        """
        # This is a simplified simulation
        # In production, this would perform actual evaluation
        
        # Use capsule ID as seed for reproducible randomness
        seed = sum(ord(c) for c in capsule_id)
        random.seed(seed + hash(criteria.criteria_id))
        
        # Base score with some randomness
        base_score = 0.7 + random.uniform(-0.2, 0.2)
        
        # Adjust based on criteria parameters
        if "metrics" in criteria.parameters:
            metrics_count = len(criteria.parameters["metrics"])
            base_score += 0.01 * metrics_count
        
        if "test_cases" in criteria.parameters:
            test_cases = criteria.parameters["test_cases"]
            base_score += 0.001 * test_cases
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))
    
    def _simulate_semi_automated_evaluation(
        self,
        capsule_id: str,
        criteria: CapsuleEvaluationCriteria,
        context: Dict[str, Any]
    ) -> float:
        """
        Simulate semi-automated evaluation.
        
        Args:
            capsule_id: The capsule ID
            criteria: The evaluation criteria
            context: Evaluation context
            
        Returns:
            float: Evaluation score (0.0 to 1.0)
        """
        # This is a simplified simulation
        # In production, this would perform actual evaluation
        
        # Use capsule ID as seed for reproducible randomness
        seed = sum(ord(c) for c in capsule_id)
        random.seed(seed + hash(criteria.criteria_id) + 1)
        
        # Base score with some randomness
        base_score = 0.75 + random.uniform(-0.15, 0.15)
        
        # Adjust based on criteria parameters
        if "compliance_frameworks" in criteria.parameters:
            frameworks_count = len(criteria.parameters["compliance_frameworks"])
            base_score += 0.02 * frameworks_count
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))
    
    def _simulate_manual_evaluation(
        self,
        capsule_id: str,
        criteria: CapsuleEvaluationCriteria,
        context: Dict[str, Any]
    ) -> float:
        """
        Simulate manual evaluation.
        
        Args:
            capsule_id: The capsule ID
            criteria: The evaluation criteria
            context: Evaluation context
            
        Returns:
            float: Evaluation score (0.0 to 1.0)
        """
        # This is a simplified simulation
        # In production, this would involve human evaluation
        
        # Use capsule ID as seed for reproducible randomness
        seed = sum(ord(c) for c in capsule_id)
        random.seed(seed + hash(criteria.criteria_id) + 2)
        
        # Base score with more randomness (manual evaluations tend to be more variable)
        base_score = 0.65 + random.uniform(-0.25, 0.25)
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))
    
    def _perform_pairwise_comparison(self, capsule_scores: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Perform pairwise comparison of capsules.
        
        Args:
            capsule_scores: Dictionary of capsule IDs to overall scores
            
        Returns:
            Dict[str, Dict[str, float]]: Pairwise comparison results
        """
        pairwise_results = {}
        
        # Initialize pairwise results
        for capsule_id in capsule_scores:
            pairwise_results[capsule_id] = {}
        
        # Perform pairwise comparisons
        capsule_ids = list(capsule_scores.keys())
        for i in range(len(capsule_ids)):
            for j in range(i + 1, len(capsule_ids)):
                capsule_a = capsule_ids[i]
                capsule_b = capsule_ids[j]
                
                score_a = capsule_scores[capsule_a]
                score_b = capsule_scores[capsule_b]
                
                # Calculate preference (how much A is preferred over B)
                # 0.5 means equal, 1.0 means A is strongly preferred, 0.0 means B is strongly preferred
                if score_a > score_b:
                    preference = 0.5 + 0.5 * ((score_a - score_b) / max(0.001, score_a))
                elif score_b > score_a:
                    preference = 0.5 - 0.5 * ((score_b - score_a) / max(0.001, score_b))
                else:
                    preference = 0.5
                
                # Store preferences
                pairwise_results[capsule_a][capsule_b] = preference
                pairwise_results[capsule_b][capsule_a] = 1.0 - preference
        
        return pairwise_results
    
    def _calculate_rankings_from_pairwise(self, pairwise_results: Dict[str, Dict[str, float]]) -> Dict[str, int]:
        """
        Calculate rankings from pairwise comparison results.
        
        Args:
            pairwise_results: Pairwise comparison results
            
        Returns:
            Dict[str, int]: Rankings by capsule ID (1 is best)
        """
        # Calculate win count for each capsule
        win_counts = {}
        
        for capsule_id, comparisons in pairwise_results.items():
            win_count = 0
            for other_id, preference in comparisons.items():
                if preference > 0.5:
                    win_count += 1
            
            win_counts[capsule_id] = win_count
        
        # Sort capsules by win count (descending)
        sorted_capsules = sorted(win_counts.keys(), key=lambda c: win_counts[c], reverse=True)
        
        # Assign rankings
        rankings = {}
        current_rank = 1
        current_win_count = None
        
        for capsule_id in sorted_capsules:
            win_count = win_counts[capsule_id]
            
            # If win count is different from previous, increment rank
            if current_win_count is not None and win_count != current_win_count:
                current_rank += 1
            
            rankings[capsule_id] = current_rank
            current_win_count = win_count
        
        return rankings
    
    def _calculate_direct_rankings(self, capsule_scores: Dict[str, float]) -> Dict[str, int]:
        """
        Calculate rankings directly from overall scores.
        
        Args:
            capsule_scores: Dictionary of capsule IDs to overall scores
            
        Returns:
            Dict[str, int]: Rankings by capsule ID (1 is best)
        """
        # Sort capsules by score (descending)
        sorted_capsules = sorted(capsule_scores.keys(), key=lambda c: capsule_scores[c], reverse=True)
        
        # Assign rankings
        rankings = {}
        current_rank = 1
        current_score = None
        
        for capsule_id in sorted_capsules:
            score = capsule_scores[capsule_id]
            
            # If score is different from previous, increment rank
            if current_score is not None and abs(score - current_score) > 0.001:
                current_rank += 1
            
            rankings[capsule_id] = current_rank
            current_score = score
        
        return rankings
    
    def _calculate_batch_statistics(self, evaluation_results_map: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate statistics for a batch of evaluation results.
        
        Args:
            evaluation_results_map: Dictionary of capsule IDs to result IDs
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        # Collect scores
        overall_scores = []
        criteria_scores = {}
        passed_count = 0
        
        for capsule_id, result_id in evaluation_results_map.items():
            result = self.get_evaluation_result(result_id)
            if result:
                overall_scores.append(result.overall_score)
                
                if result.passed_threshold:
                    passed_count += 1
                
                # Collect criteria scores
                for criteria_id, score in result.criteria_scores.items():
                    if criteria_id not in criteria_scores:
                        criteria_scores[criteria_id] = []
                    
                    criteria_scores[criteria_id].append(score)
        
        # Calculate overall statistics
        statistics = {
            "count": len(evaluation_results_map),
            "passed_count": passed_count,
            "passed_percentage": (passed_count / len(evaluation_results_map)) * 100 if evaluation_results_map else 0,
            "overall_score": {
                "min": min(overall_scores) if overall_scores else 0,
                "max": max(overall_scores) if overall_scores else 0,
                "avg": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
                "median": sorted(overall_scores)[len(overall_scores) // 2] if overall_scores else 0
            },
            "criteria_scores": {}
        }
        
        # Calculate criteria statistics
        for criteria_id, scores in criteria_scores.items():
            statistics["criteria_scores"][criteria_id] = {
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "avg": sum(scores) / len(scores) if scores else 0,
                "median": sorted(scores)[len(scores) // 2] if scores else 0
            }
        
        return statistics

class GeneratedCapsuleEvaluator:
    """
    Generated Capsule Evaluator implementation for the Overseer System.
    
    This class provides methods for evaluating generated capsules, including:
    - Managing evaluation criteria
    - Evaluating capsules against criteria
    - Comparing multiple capsules
    - Managing evaluation batches
    """
    
    def __init__(self):
        """Initialize the Generated Capsule Evaluator."""
        self.criteria_manager = CriteriaManager()
        self.evaluation_engine = EvaluationEngine(self.criteria_manager)
        logger.info("Generated Capsule Evaluator initialized")
    
    # Criteria management methods
    
    def create_criteria(self, criteria: CapsuleEvaluationCriteria) -> str:
        """
        Create a new evaluation criteria.
        
        Args:
            criteria: The evaluation criteria to create
            
        Returns:
            str: The criteria ID
        """
        return self.criteria_manager.create_criteria(criteria)
    
    def get_criteria(self, criteria_id: str) -> Optional[CapsuleEvaluationCriteria]:
        """
        Get an evaluation criteria by ID.
        
        Args:
            criteria_id: The criteria ID
            
        Returns:
            Optional[CapsuleEvaluationCriteria]: The criteria, or None if not found
        """
        return self.criteria_manager.get_criteria(criteria_id)
    
    def update_criteria(self, criteria_id: str, criteria: CapsuleEvaluationCriteria) -> bool:
        """
        Update an evaluation criteria.
        
        Args:
            criteria_id: The criteria ID to update
            criteria: The updated criteria
            
        Returns:
            bool: True if successful, False if criteria not found
        """
        return self.criteria_manager.update_criteria(criteria_id, criteria)
    
    def delete_criteria(self, criteria_id: str) -> bool:
        """
        Delete an evaluation criteria.
        
        Args:
            criteria_id: The criteria ID to delete
            
        Returns:
            bool: True if successful, False if criteria not found
        """
        return self.criteria_manager.delete_criteria(criteria_id)
    
    def list_criteria(
        self,
        method_filter: Optional[str] = None,
        min_weight: Optional[float] = None,
        max_weight: Optional[float] = None,
        min_threshold: Optional[float] = None,
        limit: int = 100
    ) -> List[CapsuleEvaluationCriteria]:
        """
        List evaluation criteria, optionally filtered.
        
        Args:
            method_filter: Optional filter for evaluation method
            min_weight: Optional minimum weight
            max_weight: Optional maximum weight
            min_threshold: Optional minimum threshold
            limit: Maximum number of criteria to return
            
        Returns:
            List[CapsuleEvaluationCriteria]: List of matching criteria
        """
        return self.criteria_manager.list_criteria(
            method_filter=method_filter,
            min_weight=min_weight,
            max_weight=max_weight,
            min_threshold=min_threshold,
            limit=limit
        )
    
    # Evaluation methods
    
    def evaluate_capsule(self, request: CapsuleEvaluationRequest) -> CapsuleEvaluationResult:
        """
        Evaluate a capsule against specified criteria.
        
        Args:
            request: The evaluation request
            
        Returns:
            CapsuleEvaluationResult: The evaluation result
        """
        return self.evaluation_engine.evaluate_capsule(request)
    
    def compare_capsules(self, request: CapsuleComparisonRequest) -> CapsuleComparisonResult:
        """
        Compare multiple capsules against each other.
        
        Args:
            request: The comparison request
            
        Returns:
            CapsuleComparisonResult: The comparison result
        """
        return self.evaluation_engine.compare_capsules(request)
    
    def get_evaluation_result(self, result_id: str) -> Optional[CapsuleEvaluationResult]:
        """
        Get an evaluation result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[CapsuleEvaluationResult]: The result, or None if not found
        """
        return self.evaluation_engine.get_evaluation_result(result_id)
    
    def get_comparison_result(self, result_id: str) -> Optional[CapsuleComparisonResult]:
        """
        Get a comparison result by ID.
        
        Args:
            result_id: The result ID
            
        Returns:
            Optional[CapsuleComparisonResult]: The result, or None if not found
        """
        return self.evaluation_engine.get_comparison_result(result_id)
    
    # Batch evaluation methods
    
    def create_evaluation_batch(self, batch: CapsuleEvaluationBatch) -> str:
        """
        Create a new evaluation batch.
        
        Args:
            batch: The evaluation batch to create
            
        Returns:
            str: The batch ID
        """
        return self.evaluation_engine.create_evaluation_batch(batch)
    
    def get_evaluation_batch(self, batch_id: str) -> Optional[CapsuleEvaluationBatch]:
        """
        Get an evaluation batch by ID.
        
        Args:
            batch_id: The batch ID
            
        Returns:
            Optional[CapsuleEvaluationBatch]: The batch, or None if not found
        """
        return self.evaluation_engine.get_evaluation_batch(batch_id)
    
    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        progress: float,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update the status of an evaluation batch.
        
        Args:
            batch_id: The batch ID
            status: The new status
            progress: The new progress value (0.0 to 1.0)
            notes: Optional status notes
            
        Returns:
            bool: True if successful, False if batch not found
        """
        return self.evaluation_engine.update_batch_status(
            batch_id=batch_id,
            status=status,
            progress=progress,
            notes=notes
        )
    
    def process_evaluation_batch(self, batch_id: str) -> Optional[CapsuleEvaluationBatchResult]:
        """
        Process an evaluation batch.
        
        Args:
            batch_id: The batch ID to process
            
        Returns:
            Optional[CapsuleEvaluationBatchResult]: The batch result, or None if batch not found
        """
        return self.evaluation_engine.process_evaluation_batch(batch_id)
    
    def get_batch_result(self, batch_result_id: str) -> Optional[CapsuleEvaluationBatchResult]:
        """
        Get a batch result by ID.
        
        Args:
            batch_result_id: The batch result ID
            
        Returns:
            Optional[CapsuleEvaluationBatchResult]: The result, or None if not found
        """
        return self.evaluation_engine.get_batch_result(batch_result_id)
