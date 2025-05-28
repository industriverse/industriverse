"""
Workflow Feedback Loop Agent Module for the Workflow Automation Layer.

This agent collects and processes feedback from workflow executions,
enabling continuous improvement and optimization of workflows.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowFeedbackLoopAgent:
    """Agent for collecting and processing workflow feedback."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow feedback loop agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-feedback-loop-agent"
        self.agent_capabilities = ["feedback_collection", "pattern_recognition", "workflow_optimization"]
        self.supported_protocols = ["MCP", "A2A"]
        self.feedback_store = {}  # Store for collected feedback
        self.pattern_cache = {}  # Cache for recognized patterns
        self.improvement_suggestions = {}  # Store for improvement suggestions
        
        logger.info("Workflow Feedback Loop Agent initialized")

    async def collect_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect feedback from workflow execution.

        Args:
            feedback_data: Feedback data including workflow_id, metrics, etc.

        Returns:
            Dict containing feedback collection status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "feedback_source", "feedback_type"]
            for field in required_fields:
                if field not in feedback_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = feedback_data["workflow_id"]
            feedback_source = feedback_data["feedback_source"]
            feedback_type = feedback_data["feedback_type"]
            
            # Generate feedback ID
            feedback_id = str(uuid.uuid4())
            
            # Add timestamp if not provided
            if "timestamp" not in feedback_data:
                feedback_data["timestamp"] = datetime.utcnow().isoformat()
            
            # Initialize workflow feedback if not exists
            if workflow_id not in self.feedback_store:
                self.feedback_store[workflow_id] = []
            
            # Store feedback
            self.feedback_store[workflow_id].append({
                "feedback_id": feedback_id,
                "source": feedback_source,
                "type": feedback_type,
                "data": feedback_data
            })
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "collect_feedback",
                "reason": f"Collected {feedback_type} feedback from {feedback_source} for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Collected {feedback_type} feedback from {feedback_source} for workflow {workflow_id}")
            
            # Check if we should analyze patterns based on new feedback
            should_analyze = feedback_data.get("analyze_immediately", False)
            if should_analyze:
                await self.analyze_feedback_patterns(workflow_id)
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "workflow_id": workflow_id,
                "message": f"Feedback collected successfully"
            }
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def analyze_feedback_patterns(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze feedback patterns for a workflow.

        Args:
            workflow_id: ID of the workflow to analyze.

        Returns:
            Dict containing analysis results.
        """
        try:
            # Check if workflow has feedback
            if workflow_id not in self.feedback_store or not self.feedback_store[workflow_id]:
                return {
                    "success": False,
                    "error": f"No feedback found for workflow {workflow_id}"
                }
            
            # Get workflow feedback
            feedback_items = self.feedback_store[workflow_id]
            
            # Group feedback by type
            feedback_by_type = {}
            for item in feedback_items:
                feedback_type = item["type"]
                if feedback_type not in feedback_by_type:
                    feedback_by_type[feedback_type] = []
                feedback_by_type[feedback_type].append(item)
            
            # Analyze patterns for each feedback type
            patterns = {}
            for feedback_type, items in feedback_by_type.items():
                if feedback_type == "performance":
                    patterns[feedback_type] = await self._analyze_performance_patterns(items)
                elif feedback_type == "error":
                    patterns[feedback_type] = await self._analyze_error_patterns(items)
                elif feedback_type == "user":
                    patterns[feedback_type] = await self._analyze_user_feedback_patterns(items)
                elif feedback_type == "agent":
                    patterns[feedback_type] = await self._analyze_agent_feedback_patterns(items)
                else:
                    patterns[feedback_type] = await self._analyze_generic_patterns(items)
            
            # Store patterns in cache
            self.pattern_cache[workflow_id] = {
                "timestamp": datetime.utcnow().isoformat(),
                "patterns": patterns
            }
            
            # Generate improvement suggestions based on patterns
            suggestions = await self._generate_improvement_suggestions(workflow_id, patterns)
            
            # Store suggestions
            self.improvement_suggestions[workflow_id] = {
                "timestamp": datetime.utcnow().isoformat(),
                "suggestions": suggestions
            }
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "analyze_feedback_patterns",
                "reason": f"Analyzed feedback patterns for workflow {workflow_id}, found {sum(len(p) for p in patterns.values())} patterns",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Analyzed feedback patterns for workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "pattern_count": sum(len(p) for p in patterns.values()),
                "patterns": patterns,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _analyze_performance_patterns(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze performance feedback patterns.

        Args:
            feedback_items: List of performance feedback items.

        Returns:
            List of identified patterns.
        """
        patterns = []
        
        # Extract performance metrics
        metrics_by_task = {}
        for item in feedback_items:
            data = item["data"]
            task_id = data.get("task_id")
            if task_id:
                if task_id not in metrics_by_task:
                    metrics_by_task[task_id] = []
                
                metrics = data.get("metrics", {})
                if metrics:
                    metrics_by_task[task_id].append({
                        "timestamp": data.get("timestamp"),
                        "metrics": metrics
                    })
        
        # Analyze metrics for each task
        for task_id, task_metrics in metrics_by_task.items():
            # Sort metrics by timestamp
            sorted_metrics = sorted(task_metrics, key=lambda x: x["timestamp"])
            
            # Check for performance degradation
            if len(sorted_metrics) >= 3:
                # Calculate average execution time trend
                if all("execution_time" in m["metrics"] for m in sorted_metrics):
                    execution_times = [m["metrics"]["execution_time"] for m in sorted_metrics]
                    
                    # Check if execution time is consistently increasing
                    is_increasing = all(execution_times[i] < execution_times[i+1] for i in range(len(execution_times)-1))
                    if is_increasing:
                        patterns.append({
                            "pattern_type": "performance_degradation",
                            "task_id": task_id,
                            "metric": "execution_time",
                            "values": execution_times,
                            "confidence": 0.8,
                            "description": f"Task {task_id} shows consistent execution time increase"
                        })
                
                # Check for memory usage patterns
                if all("memory_usage" in m["metrics"] for m in sorted_metrics):
                    memory_usage = [m["metrics"]["memory_usage"] for m in sorted_metrics]
                    
                    # Check for memory leaks (consistently increasing memory usage)
                    is_increasing = all(memory_usage[i] < memory_usage[i+1] for i in range(len(memory_usage)-1))
                    if is_increasing:
                        patterns.append({
                            "pattern_type": "potential_memory_leak",
                            "task_id": task_id,
                            "metric": "memory_usage",
                            "values": memory_usage,
                            "confidence": 0.7,
                            "description": f"Task {task_id} shows consistent memory usage increase"
                        })
        
        # Check for bottleneck tasks
        if len(metrics_by_task) >= 2:
            avg_execution_times = {}
            for task_id, task_metrics in metrics_by_task.items():
                if all("execution_time" in m["metrics"] for m in task_metrics):
                    avg_execution_times[task_id] = sum(m["metrics"]["execution_time"] for m in task_metrics) / len(task_metrics)
            
            if avg_execution_times:
                # Find task with highest average execution time
                bottleneck_task = max(avg_execution_times.items(), key=lambda x: x[1])
                
                # Check if bottleneck task is significantly slower than others
                other_tasks_avg = sum(t for tid, t in avg_execution_times.items() if tid != bottleneck_task[0]) / (len(avg_execution_times) - 1) if len(avg_execution_times) > 1 else 0
                
                if bottleneck_task[1] > 2 * other_tasks_avg:
                    patterns.append({
                        "pattern_type": "bottleneck_task",
                        "task_id": bottleneck_task[0],
                        "metric": "execution_time",
                        "value": bottleneck_task[1],
                        "avg_other_tasks": other_tasks_avg,
                        "confidence": 0.9,
                        "description": f"Task {bottleneck_task[0]} is a bottleneck, {bottleneck_task[1]:.2f}ms vs {other_tasks_avg:.2f}ms avg for other tasks"
                    })
        
        return patterns

    async def _analyze_error_patterns(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze error feedback patterns.

        Args:
            feedback_items: List of error feedback items.

        Returns:
            List of identified patterns.
        """
        patterns = []
        
        # Group errors by type
        errors_by_type = {}
        for item in feedback_items:
            data = item["data"]
            error_type = data.get("error_type", "unknown")
            
            if error_type not in errors_by_type:
                errors_by_type[error_type] = []
            
            errors_by_type[error_type].append({
                "timestamp": data.get("timestamp"),
                "task_id": data.get("task_id"),
                "error_details": data.get("error_details", {})
            })
        
        # Analyze each error type
        for error_type, errors in errors_by_type.items():
            # Check for frequent errors
            if len(errors) >= 3:
                patterns.append({
                    "pattern_type": "frequent_error",
                    "error_type": error_type,
                    "count": len(errors),
                    "confidence": 0.8,
                    "description": f"Frequent error of type {error_type} occurred {len(errors)} times"
                })
            
            # Check for errors in specific tasks
            errors_by_task = {}
            for error in errors:
                task_id = error.get("task_id")
                if task_id:
                    if task_id not in errors_by_task:
                        errors_by_task[task_id] = []
                    errors_by_task[task_id].append(error)
            
            for task_id, task_errors in errors_by_task.items():
                if len(task_errors) >= 2:
                    patterns.append({
                        "pattern_type": "task_specific_error",
                        "error_type": error_type,
                        "task_id": task_id,
                        "count": len(task_errors),
                        "confidence": 0.9,
                        "description": f"Task {task_id} consistently produces {error_type} errors ({len(task_errors)} occurrences)"
                    })
            
            # Check for temporal patterns (errors occurring at specific times)
            if len(errors) >= 5:
                # Group errors by hour of day
                errors_by_hour = {}
                for error in errors:
                    timestamp = error.get("timestamp")
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            hour = dt.hour
                            
                            if hour not in errors_by_hour:
                                errors_by_hour[hour] = 0
                            errors_by_hour[hour] += 1
                        except (ValueError, TypeError):
                            pass
                
                # Check if errors are concentrated in specific hours
                total_errors = sum(errors_by_hour.values())
                for hour, count in errors_by_hour.items():
                    if count >= 3 and count / total_errors >= 0.5:
                        patterns.append({
                            "pattern_type": "temporal_error_pattern",
                            "error_type": error_type,
                            "hour": hour,
                            "count": count,
                            "percentage": count / total_errors,
                            "confidence": 0.7,
                            "description": f"{error_type} errors occur frequently during hour {hour} ({count} occurrences, {count/total_errors:.1%} of total)"
                        })
        
        return patterns

    async def _analyze_user_feedback_patterns(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze user feedback patterns.

        Args:
            feedback_items: List of user feedback items.

        Returns:
            List of identified patterns.
        """
        patterns = []
        
        # Extract ratings and comments
        ratings = []
        comments = []
        
        for item in feedback_items:
            data = item["data"]
            
            if "rating" in data:
                ratings.append({
                    "timestamp": data.get("timestamp"),
                    "rating": data["rating"],
                    "task_id": data.get("task_id"),
                    "user_id": data.get("user_id")
                })
            
            if "comment" in data:
                comments.append({
                    "timestamp": data.get("timestamp"),
                    "comment": data["comment"],
                    "task_id": data.get("task_id"),
                    "user_id": data.get("user_id")
                })
        
        # Analyze ratings
        if ratings:
            avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
            
            # Check for low average rating
            if avg_rating < 3.0:
                patterns.append({
                    "pattern_type": "low_user_satisfaction",
                    "avg_rating": avg_rating,
                    "rating_count": len(ratings),
                    "confidence": 0.8,
                    "description": f"Low average user satisfaction rating: {avg_rating:.1f}/5 across {len(ratings)} ratings"
                })
            
            # Check for rating trends
            if len(ratings) >= 5:
                # Sort ratings by timestamp
                sorted_ratings = sorted(ratings, key=lambda x: x["timestamp"])
                
                # Calculate moving average
                window_size = min(3, len(sorted_ratings))
                moving_avgs = []
                
                for i in range(len(sorted_ratings) - window_size + 1):
                    window = sorted_ratings[i:i+window_size]
                    avg = sum(r["rating"] for r in window) / window_size
                    moving_avgs.append(avg)
                
                # Check for declining trend
                if len(moving_avgs) >= 3 and moving_avgs[0] > moving_avgs[-1] and all(moving_avgs[i] >= moving_avgs[i+1] for i in range(len(moving_avgs)-1)):
                    patterns.append({
                        "pattern_type": "declining_user_satisfaction",
                        "initial_rating": moving_avgs[0],
                        "final_rating": moving_avgs[-1],
                        "confidence": 0.7,
                        "description": f"User satisfaction is declining from {moving_avgs[0]:.1f} to {moving_avgs[-1]:.1f}"
                    })
            
            # Check for ratings by task
            ratings_by_task = {}
            for rating in ratings:
                task_id = rating.get("task_id")
                if task_id:
                    if task_id not in ratings_by_task:
                        ratings_by_task[task_id] = []
                    ratings_by_task[task_id].append(rating["rating"])
            
            for task_id, task_ratings in ratings_by_task.items():
                if len(task_ratings) >= 3:
                    task_avg = sum(task_ratings) / len(task_ratings)
                    
                    # Check for tasks with particularly low ratings
                    if task_avg < 2.5:
                        patterns.append({
                            "pattern_type": "problematic_task",
                            "task_id": task_id,
                            "avg_rating": task_avg,
                            "rating_count": len(task_ratings),
                            "confidence": 0.9,
                            "description": f"Task {task_id} has very low user satisfaction: {task_avg:.1f}/5 across {len(task_ratings)} ratings"
                        })
        
        # Analyze comments (simplified, would use NLP in a real implementation)
        if comments:
            # Check for common keywords indicating issues
            issue_keywords = ["slow", "error", "crash", "bug", "difficult", "confusing", "unclear"]
            keyword_counts = {keyword: 0 for keyword in issue_keywords}
            
            for comment in comments:
                comment_text = comment["comment"].lower()
                for keyword in issue_keywords:
                    if keyword in comment_text:
                        keyword_counts[keyword] += 1
            
            # Identify frequently mentioned issues
            for keyword, count in keyword_counts.items():
                if count >= 3:
                    patterns.append({
                        "pattern_type": "common_feedback_issue",
                        "keyword": keyword,
                        "count": count,
                        "percentage": count / len(comments),
                        "confidence": 0.6,
                        "description": f"Common issue in user feedback: '{keyword}' mentioned in {count} comments ({count/len(comments):.1%})"
                    })
        
        return patterns

    async def _analyze_agent_feedback_patterns(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze agent feedback patterns.

        Args:
            feedback_items: List of agent feedback items.

        Returns:
            List of identified patterns.
        """
        patterns = []
        
        # Group feedback by agent
        feedback_by_agent = {}
        for item in feedback_items:
            data = item["data"]
            agent_id = data.get("agent_id", "unknown")
            
            if agent_id not in feedback_by_agent:
                feedback_by_agent[agent_id] = []
            
            feedback_by_agent[agent_id].append(data)
        
        # Analyze feedback for each agent
        for agent_id, agent_feedback in feedback_by_agent.items():
            # Check for frequent issues reported by agents
            issues = [f for f in agent_feedback if f.get("feedback_category") == "issue"]
            if issues:
                issue_types = {}
                for issue in issues:
                    issue_type = issue.get("issue_type", "unknown")
                    if issue_type not in issue_types:
                        issue_types[issue_type] = 0
                    issue_types[issue_type] += 1
                
                for issue_type, count in issue_types.items():
                    if count >= 2:
                        patterns.append({
                            "pattern_type": "agent_reported_issue",
                            "agent_id": agent_id,
                            "issue_type": issue_type,
                            "count": count,
                            "confidence": 0.8,
                            "description": f"Agent {agent_id} reported {issue_type} issue {count} times"
                        })
            
            # Check for agent performance self-assessments
            performance_reports = [f for f in agent_feedback if f.get("feedback_category") == "performance"]
            if performance_reports and len(performance_reports) >= 3:
                # Check for declining performance trend
                if all("performance_score" in report for report in performance_reports):
                    # Sort by timestamp
                    sorted_reports = sorted(performance_reports, key=lambda x: x.get("timestamp", ""))
                    scores = [report["performance_score"] for report in sorted_reports]
                    
                    # Check if scores are consistently decreasing
                    is_decreasing = all(scores[i] > scores[i+1] for i in range(len(scores)-1))
                    if is_decreasing:
                        patterns.append({
                            "pattern_type": "declining_agent_performance",
                            "agent_id": agent_id,
                            "initial_score": scores[0],
                            "final_score": scores[-1],
                            "confidence": 0.7,
                            "description": f"Agent {agent_id} reports declining performance from {scores[0]:.2f} to {scores[-1]:.2f}"
                        })
            
            # Check for resource constraints reported by agents
            resource_reports = [f for f in agent_feedback if f.get("feedback_category") == "resource"]
            if resource_reports and len(resource_reports) >= 2:
                resource_types = {}
                for report in resource_reports:
                    resource_type = report.get("resource_type", "unknown")
                    if resource_type not in resource_types:
                        resource_types[resource_type] = 0
                    resource_types[resource_type] += 1
                
                for resource_type, count in resource_types.items():
                    if count >= 2:
                        patterns.append({
                            "pattern_type": "agent_resource_constraint",
                            "agent_id": agent_id,
                            "resource_type": resource_type,
                            "count": count,
                            "confidence": 0.8,
                            "description": f"Agent {agent_id} reported {resource_type} resource constraint {count} times"
                        })
        
        return patterns

    async def _analyze_generic_patterns(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze generic feedback patterns.

        Args:
            feedback_items: List of generic feedback items.

        Returns:
            List of identified patterns.
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated pattern recognition
        return []

    async def _generate_improvement_suggestions(self, workflow_id: str, patterns: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on identified patterns.

        Args:
            workflow_id: ID of the workflow.
            patterns: Identified patterns by feedback type.

        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        # Get workflow manifest
        workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
        if not workflow_manifest:
            return suggestions
        
        # Process performance patterns
        if "performance" in patterns:
            for pattern in patterns["performance"]:
                if pattern["pattern_type"] == "performance_degradation":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "task_id": pattern["task_id"],
                        "priority": "high",
                        "suggestion": f"Optimize task {pattern['task_id']} to address increasing execution time",
                        "actions": [
                            {
                                "action_type": "optimize_task",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "focus_area": "execution_time"
                                }
                            },
                            {
                                "action_type": "profile_task",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "profile_type": "performance"
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "potential_memory_leak":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "task_id": pattern["task_id"],
                        "priority": "high",
                        "suggestion": f"Investigate potential memory leak in task {pattern['task_id']}",
                        "actions": [
                            {
                                "action_type": "memory_profile",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "duration": "full_execution"
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "bottleneck_task":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "task_id": pattern["task_id"],
                        "priority": "medium",
                        "suggestion": f"Address bottleneck in task {pattern['task_id']}",
                        "actions": [
                            {
                                "action_type": "optimize_task",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "focus_area": "execution_time"
                                }
                            },
                            {
                                "action_type": "parallelize_task",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "parallelization_strategy": "auto"
                                }
                            }
                        ]
                    })
        
        # Process error patterns
        if "error" in patterns:
            for pattern in patterns["error"]:
                if pattern["pattern_type"] == "frequent_error":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "error_type": pattern["error_type"],
                        "priority": "high",
                        "suggestion": f"Address frequent {pattern['error_type']} errors",
                        "actions": [
                            {
                                "action_type": "error_analysis",
                                "error_type": pattern["error_type"],
                                "parameters": {
                                    "detailed": True
                                }
                            },
                            {
                                "action_type": "add_error_handling",
                                "error_type": pattern["error_type"],
                                "parameters": {
                                    "strategy": "robust"
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "task_specific_error":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "task_id": pattern["task_id"],
                        "error_type": pattern["error_type"],
                        "priority": "high",
                        "suggestion": f"Fix {pattern['error_type']} errors in task {pattern['task_id']}",
                        "actions": [
                            {
                                "action_type": "task_error_analysis",
                                "task_id": pattern["task_id"],
                                "error_type": pattern["error_type"],
                                "parameters": {
                                    "detailed": True
                                }
                            }
                        ]
                    })
        
        # Process user feedback patterns
        if "user" in patterns:
            for pattern in patterns["user"]:
                if pattern["pattern_type"] == "low_user_satisfaction":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "priority": "medium",
                        "suggestion": "Improve overall user experience based on low satisfaction ratings",
                        "actions": [
                            {
                                "action_type": "user_experience_review",
                                "parameters": {
                                    "focus_areas": ["usability", "performance", "clarity"]
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "problematic_task":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "task_id": pattern["task_id"],
                        "priority": "high",
                        "suggestion": f"Improve user experience for task {pattern['task_id']} based on low ratings",
                        "actions": [
                            {
                                "action_type": "task_ux_review",
                                "task_id": pattern["task_id"],
                                "parameters": {
                                    "focus_areas": ["usability", "clarity", "feedback"]
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "common_feedback_issue":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "keyword": pattern["keyword"],
                        "priority": "medium",
                        "suggestion": f"Address common user feedback issue: '{pattern['keyword']}'",
                        "actions": [
                            {
                                "action_type": "feedback_analysis",
                                "parameters": {
                                    "focus_keyword": pattern["keyword"]
                                }
                            }
                        ]
                    })
        
        # Process agent feedback patterns
        if "agent" in patterns:
            for pattern in patterns["agent"]:
                if pattern["pattern_type"] == "agent_reported_issue":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "agent_id": pattern["agent_id"],
                        "issue_type": pattern["issue_type"],
                        "priority": "medium",
                        "suggestion": f"Address {pattern['issue_type']} issues reported by agent {pattern['agent_id']}",
                        "actions": [
                            {
                                "action_type": "agent_issue_analysis",
                                "agent_id": pattern["agent_id"],
                                "issue_type": pattern["issue_type"],
                                "parameters": {
                                    "detailed": True
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "declining_agent_performance":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "agent_id": pattern["agent_id"],
                        "priority": "high",
                        "suggestion": f"Investigate declining performance of agent {pattern['agent_id']}",
                        "actions": [
                            {
                                "action_type": "agent_performance_analysis",
                                "agent_id": pattern["agent_id"],
                                "parameters": {
                                    "time_range": "last_30_days"
                                }
                            }
                        ]
                    })
                
                elif pattern["pattern_type"] == "agent_resource_constraint":
                    suggestions.append({
                        "suggestion_id": str(uuid.uuid4()),
                        "pattern_type": pattern["pattern_type"],
                        "agent_id": pattern["agent_id"],
                        "resource_type": pattern["resource_type"],
                        "priority": "medium",
                        "suggestion": f"Address {pattern['resource_type']} resource constraints for agent {pattern['agent_id']}",
                        "actions": [
                            {
                                "action_type": "resource_allocation_review",
                                "agent_id": pattern["agent_id"],
                                "resource_type": pattern["resource_type"],
                                "parameters": {
                                    "allocation_strategy": "dynamic"
                                }
                            }
                        ]
                    })
        
        return suggestions

    async def get_feedback(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get collected feedback.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing feedback data.
        """
        if workflow_id:
            # Get feedback for specific workflow
            if workflow_id in self.feedback_store:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "feedback_count": len(self.feedback_store[workflow_id]),
                    "feedback": self.feedback_store[workflow_id]
                }
            else:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "feedback_count": 0,
                    "feedback": []
                }
        else:
            # Get all feedback
            total_count = sum(len(items) for items in self.feedback_store.values())
            return {
                "success": True,
                "workflow_count": len(self.feedback_store),
                "feedback_count": total_count,
                "feedback_by_workflow": self.feedback_store
            }

    async def get_patterns(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get identified patterns.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing pattern data.
        """
        if workflow_id:
            # Get patterns for specific workflow
            if workflow_id in self.pattern_cache:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "timestamp": self.pattern_cache[workflow_id]["timestamp"],
                    "patterns": self.pattern_cache[workflow_id]["patterns"]
                }
            else:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "patterns": {}
                }
        else:
            # Get all patterns
            return {
                "success": True,
                "workflow_count": len(self.pattern_cache),
                "patterns_by_workflow": self.pattern_cache
            }

    async def get_suggestions(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get improvement suggestions.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing suggestion data.
        """
        if workflow_id:
            # Get suggestions for specific workflow
            if workflow_id in self.improvement_suggestions:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "timestamp": self.improvement_suggestions[workflow_id]["timestamp"],
                    "suggestions": self.improvement_suggestions[workflow_id]["suggestions"]
                }
            else:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "suggestions": []
                }
        else:
            # Get all suggestions
            all_suggestions = {}
            for wf_id, data in self.improvement_suggestions.items():
                all_suggestions[wf_id] = {
                    "timestamp": data["timestamp"],
                    "suggestion_count": len(data["suggestions"]),
                    "suggestions": data["suggestions"]
                }
            
            return {
                "success": True,
                "workflow_count": len(self.improvement_suggestions),
                "suggestions_by_workflow": all_suggestions
            }

    async def apply_suggestion(self, suggestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an improvement suggestion.

        Args:
            suggestion_data: Suggestion data including workflow_id, suggestion_id, etc.

        Returns:
            Dict containing application status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "suggestion_id"]
            for field in required_fields:
                if field not in suggestion_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = suggestion_data["workflow_id"]
            suggestion_id = suggestion_data["suggestion_id"]
            
            # Check if workflow has suggestions
            if workflow_id not in self.improvement_suggestions:
                return {
                    "success": False,
                    "error": f"No suggestions found for workflow {workflow_id}"
                }
            
            # Find the suggestion
            suggestions = self.improvement_suggestions[workflow_id]["suggestions"]
            suggestion = next((s for s in suggestions if s["suggestion_id"] == suggestion_id), None)
            
            if not suggestion:
                return {
                    "success": False,
                    "error": f"Suggestion {suggestion_id} not found for workflow {workflow_id}"
                }
            
            # Apply the suggestion (in a real implementation, this would execute the actions)
            # For now, we'll just simulate applying it
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "apply_suggestion",
                "reason": f"Applied suggestion {suggestion_id}: {suggestion['suggestion']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Applied suggestion {suggestion_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "suggestion_id": suggestion_id,
                "suggestion": suggestion["suggestion"],
                "actions_applied": [a["action_type"] for a in suggestion["actions"]],
                "message": "Suggestion applied successfully"
            }
            
        except Exception as e:
            logger.error(f"Error applying suggestion: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
                "editable_nodes": ["feedback_collection_node", "pattern_analysis_node"]
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
            elif message_type == "analyze_feedback_patterns":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.analyze_feedback_patterns(workflow_id)
            elif message_type == "get_feedback":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_feedback(workflow_id)
            elif message_type == "get_patterns":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_patterns(workflow_id)
            elif message_type == "get_suggestions":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_suggestions(workflow_id)
            elif message_type == "apply_suggestion":
                return await self.apply_suggestion(message.get("payload", {}))
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
