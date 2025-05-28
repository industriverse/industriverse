"""
Workflow Feedback Agent Module for the Workflow Automation Layer.

This agent collects, processes, and applies feedback on workflow execution,
enabling continuous improvement and optimization of workflows.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowFeedbackAgent:
    """Agent for collecting and processing workflow feedback."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow feedback agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.feedback_store = {}
        self.feedback_patterns = {}
        self.retraining_thresholds = {
            "error_rate": 0.2,  # 20% error rate triggers retraining
            "feedback_count": 10,  # At least 10 feedback items needed
            "negative_feedback_ratio": 0.3  # 30% negative feedback triggers retraining
        }
        self.core_ai_connector = None
        self.agent_id = "workflow-feedback-agent"
        self.agent_capabilities = ["feedback_collection", "pattern_analysis", "retraining_trigger"]
        self.supported_protocols = ["MCP", "A2A"]
        
        # Initialize feedback categories
        self.feedback_categories = {
            "accuracy": [],
            "performance": [],
            "usability": [],
            "reliability": [],
            "explainability": []
        }
        
        logger.info("Workflow Feedback Agent initialized")

    def register_core_ai_connector(self, core_ai_connector):
        """Register the Core AI Layer connector.

        Args:
            core_ai_connector: The Core AI Layer connector instance.
        """
        self.core_ai_connector = core_ai_connector
        logger.info("Core AI connector registered with Workflow Feedback Agent")

    async def collect_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect feedback on workflow execution.

        Args:
            feedback_data: Feedback data including workflow_id, task_id, rating, comments, etc.

        Returns:
            Dict containing feedback collection status and details.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "source", "rating"]
            for field in required_fields:
                if field not in feedback_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            # Generate feedback ID
            feedback_id = str(uuid.uuid4())
            
            # Add timestamp and feedback ID
            feedback_data["timestamp"] = datetime.utcnow().isoformat()
            feedback_data["feedback_id"] = feedback_id
            
            # Categorize feedback
            category = feedback_data.get("category", "general")
            if category in self.feedback_categories:
                self.feedback_categories[category].append(feedback_data)
            else:
                # Default to general category
                if "general" not in self.feedback_categories:
                    self.feedback_categories["general"] = []
                self.feedback_categories["general"].append(feedback_data)
            
            # Store feedback
            self.feedback_store[feedback_id] = feedback_data
            
            # Log feedback collection
            logger.info(f"Collected feedback {feedback_id} for workflow {feedback_data['workflow_id']}")
            
            # Process feedback asynchronously
            asyncio.create_task(self._process_feedback(feedback_data))
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Feedback collected successfully"
            }
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _process_feedback(self, feedback_data: Dict[str, Any]):
        """Process collected feedback.

        Args:
            feedback_data: Feedback data to process.
        """
        try:
            workflow_id = feedback_data["workflow_id"]
            
            # Update workflow metadata with feedback
            await self.workflow_runtime.update_workflow_metadata(workflow_id, {
                "last_feedback": {
                    "timestamp": feedback_data["timestamp"],
                    "rating": feedback_data["rating"],
                    "source": feedback_data["source"]
                }
            })
            
            # Extract patterns from feedback
            await self._extract_patterns(feedback_data)
            
            # Check if retraining is needed
            await self._check_retraining_triggers(workflow_id)
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "process_feedback",
                "reason": f"Processed feedback for workflow {workflow_id} with rating {feedback_data['rating']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Processed feedback for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")

    async def _extract_patterns(self, feedback_data: Dict[str, Any]):
        """Extract patterns from feedback data.

        Args:
            feedback_data: Feedback data to analyze.
        """
        workflow_id = feedback_data["workflow_id"]
        
        # Initialize pattern store for this workflow if not exists
        if workflow_id not in self.feedback_patterns:
            self.feedback_patterns[workflow_id] = {
                "ratings": [],
                "common_issues": {},
                "improvement_suggestions": []
            }
        
        # Add rating to pattern
        self.feedback_patterns[workflow_id]["ratings"].append(feedback_data["rating"])
        
        # Extract issues from comments if available
        if "comments" in feedback_data and feedback_data["comments"]:
            # In a real implementation, this would use NLP from Core AI Layer
            # For now, use simple keyword matching
            comments = feedback_data["comments"].lower()
            issue_keywords = {
                "slow": "performance",
                "error": "reliability",
                "crash": "reliability",
                "confusing": "usability",
                "unclear": "explainability",
                "wrong": "accuracy",
                "incorrect": "accuracy"
            }
            
            for keyword, issue_type in issue_keywords.items():
                if keyword in comments:
                    if issue_type not in self.feedback_patterns[workflow_id]["common_issues"]:
                        self.feedback_patterns[workflow_id]["common_issues"][issue_type] = 0
                    self.feedback_patterns[workflow_id]["common_issues"][issue_type] += 1
        
        # Extract improvement suggestions
        if "suggestions" in feedback_data and feedback_data["suggestions"]:
            self.feedback_patterns[workflow_id]["improvement_suggestions"].append(feedback_data["suggestions"])

    async def _check_retraining_triggers(self, workflow_id: str):
        """Check if retraining triggers have been met.

        Args:
            workflow_id: ID of the workflow to check.
        """
        if workflow_id not in self.feedback_patterns:
            return
        
        patterns = self.feedback_patterns[workflow_id]
        
        # Check if we have enough feedback
        if len(patterns["ratings"]) < self.retraining_thresholds["feedback_count"]:
            return
        
        # Calculate error rate (ratings below 3 out of 5)
        error_count = sum(1 for rating in patterns["ratings"] if rating < 3)
        error_rate = error_count / len(patterns["ratings"])
        
        # Calculate negative feedback ratio
        negative_feedback = sum(1 for rating in patterns["ratings"] if rating <= 2)
        negative_ratio = negative_feedback / len(patterns["ratings"])
        
        # Check if thresholds are met
        if (error_rate >= self.retraining_thresholds["error_rate"] or
                negative_ratio >= self.retraining_thresholds["negative_feedback_ratio"]):
            await self._trigger_retraining(workflow_id, patterns)

    async def _trigger_retraining(self, workflow_id: str, patterns: Dict[str, Any]):
        """Trigger retraining based on feedback patterns.

        Args:
            workflow_id: ID of the workflow to retrain.
            patterns: Feedback patterns for the workflow.
        """
        logger.info(f"Triggering retraining for workflow {workflow_id}")
        
        # Get workflow definition
        workflow = self.workflow_runtime.workflow_registry.get_workflow(workflow_id)
        if not workflow:
            logger.error(f"Cannot trigger retraining: workflow {workflow_id} not found")
            return
        
        # Prepare retraining data
        retraining_data = {
            "workflow_id": workflow_id,
            "workflow_definition": workflow,
            "feedback_patterns": patterns,
            "common_issues": patterns["common_issues"],
            "improvement_suggestions": patterns["improvement_suggestions"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # If Core AI connector is available, trigger retraining
        if self.core_ai_connector:
            try:
                result = await self.core_ai_connector.trigger_model_retraining(retraining_data)
                logger.info(f"Retraining triggered for workflow {workflow_id}: {result}")
                
                # Update workflow metadata
                await self.workflow_runtime.update_workflow_metadata(workflow_id, {
                    "last_retraining": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "trigger": "feedback_patterns",
                        "result": result
                    }
                })
                
            except Exception as e:
                logger.error(f"Error triggering retraining: {str(e)}")
        else:
            logger.warning(f"Core AI connector not available, cannot trigger retraining for {workflow_id}")

    async def get_workflow_feedback(self, workflow_id: str) -> Dict[str, Any]:
        """Get all feedback for a specific workflow.

        Args:
            workflow_id: ID of the workflow.

        Returns:
            Dict containing all feedback for the workflow.
        """
        feedback_items = [item for item in self.feedback_store.values() 
                         if item["workflow_id"] == workflow_id]
        
        # Calculate statistics
        if feedback_items:
            avg_rating = sum(item["rating"] for item in feedback_items) / len(feedback_items)
            ratings_distribution = {}
            for i in range(1, 6):  # Assuming 1-5 rating scale
                ratings_distribution[i] = sum(1 for item in feedback_items if item["rating"] == i)
        else:
            avg_rating = 0
            ratings_distribution = {i: 0 for i in range(1, 6)}
        
        return {
            "workflow_id": workflow_id,
            "feedback_count": len(feedback_items),
            "average_rating": avg_rating,
            "ratings_distribution": ratings_distribution,
            "feedback_items": feedback_items,
            "patterns": self.feedback_patterns.get(workflow_id, {})
        }

    async def get_feedback_summary(self) -> Dict[str, Any]:
        """Get a summary of all feedback across workflows.

        Returns:
            Dict containing feedback summary statistics.
        """
        all_workflows = {}
        all_ratings = []
        
        for feedback_id, feedback in self.feedback_store.items():
            workflow_id = feedback["workflow_id"]
            if workflow_id not in all_workflows:
                all_workflows[workflow_id] = []
            all_workflows[workflow_id].append(feedback)
            all_ratings.append(feedback["rating"])
        
        # Calculate overall statistics
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
        ratings_distribution = {}
        for i in range(1, 6):  # Assuming 1-5 rating scale
            ratings_distribution[i] = sum(1 for rating in all_ratings if rating == i)
        
        # Calculate per-workflow statistics
        workflow_stats = {}
        for workflow_id, feedback_items in all_workflows.items():
            workflow_avg = sum(item["rating"] for item in feedback_items) / len(feedback_items)
            workflow_stats[workflow_id] = {
                "feedback_count": len(feedback_items),
                "average_rating": workflow_avg
            }
        
        # Calculate per-category statistics
        category_stats = {}
        for category, items in self.feedback_categories.items():
            if items:
                category_avg = sum(item["rating"] for item in items) / len(items)
                category_stats[category] = {
                    "feedback_count": len(items),
                    "average_rating": category_avg
                }
        
        return {
            "total_feedback": len(self.feedback_store),
            "total_workflows": len(all_workflows),
            "average_rating": avg_rating,
            "ratings_distribution": ratings_distribution,
            "workflow_statistics": workflow_stats,
            "category_statistics": category_stats
        }

    async def generate_improvement_recommendations(self, workflow_id: str) -> Dict[str, Any]:
        """Generate improvement recommendations based on feedback.

        Args:
            workflow_id: ID of the workflow.

        Returns:
            Dict containing improvement recommendations.
        """
        if workflow_id not in self.feedback_patterns:
            return {
                "success": False,
                "error": f"No feedback patterns available for workflow {workflow_id}"
            }
        
        patterns = self.feedback_patterns[workflow_id]
        
        # Identify top issues
        top_issues = sorted(
            patterns["common_issues"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate recommendations based on issues
        recommendations = []
        for issue_type, count in top_issues:
            if issue_type == "performance":
                recommendations.append({
                    "type": "performance",
                    "description": "Optimize workflow execution time",
                    "suggestion": "Consider parallelizing tasks or reducing wait times between steps"
                })
            elif issue_type == "reliability":
                recommendations.append({
                    "type": "reliability",
                    "description": "Improve workflow reliability",
                    "suggestion": "Add more robust error handling and retry mechanisms"
                })
            elif issue_type == "usability":
                recommendations.append({
                    "type": "usability",
                    "description": "Enhance workflow usability",
                    "suggestion": "Simplify user interfaces and provide clearer instructions"
                })
            elif issue_type == "explainability":
                recommendations.append({
                    "type": "explainability",
                    "description": "Improve workflow explainability",
                    "suggestion": "Add more detailed explanations for each step and decision"
                })
            elif issue_type == "accuracy":
                recommendations.append({
                    "type": "accuracy",
                    "description": "Enhance workflow accuracy",
                    "suggestion": "Review decision logic and validation steps"
                })
        
        # Include user suggestions
        user_suggestions = []
        if "improvement_suggestions" in patterns and patterns["improvement_suggestions"]:
            user_suggestions = patterns["improvement_suggestions"]
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "recommendations": recommendations,
            "user_suggestions": user_suggestions,
            "feedback_count": len(patterns["ratings"]),
            "average_rating": sum(patterns["ratings"]) / len(patterns["ratings"]) if patterns["ratings"] else 0
        }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["feedback_collection_node", "feedback_analysis_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            
            if message_type == "collect_feedback":
                return await self.collect_feedback(message.get("payload", {}))
            elif message_type == "get_workflow_feedback":
                workflow_id = message.get("payload", {}).get("workflow_id")
                if not workflow_id:
                    return {"success": False, "error": "Missing workflow_id"}
                return await self.get_workflow_feedback(workflow_id)
            elif message_type == "get_feedback_summary":
                return await self.get_feedback_summary()
            elif message_type == "generate_recommendations":
                workflow_id = message.get("payload", {}).get("workflow_id")
                if not workflow_id:
                    return {"success": False, "error": "Missing workflow_id"}
                return await self.generate_improvement_recommendations(workflow_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
