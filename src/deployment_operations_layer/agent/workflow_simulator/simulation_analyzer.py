"""
Simulation Analyzer

This module is responsible for analyzing simulation results for the Workflow Simulator Agent.
It processes the data collected during simulation runs, identifies patterns, anomalies,
and insights, and provides recommendations for deployment decisions.
"""

import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)

class SimulationAnalyzer:
    """
    Analyzes simulation results to provide insights and recommendations.
    
    This class processes the raw data from simulation runs, calculates key metrics,
    identifies patterns and anomalies, and generates actionable insights to support
    deployment decisions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Simulation Analyzer.
        
        Args:
            config: Configuration dictionary for the analyzer
        """
        self.config = config or {}
        
        # Analysis thresholds
        self.thresholds = self.config.get("thresholds", {
            "response_time_ms": {
                "excellent": 100,
                "good": 300,
                "acceptable": 500,
                "poor": 1000
            },
            "throughput_rps": {
                "excellent": 500,
                "good": 200,
                "acceptable": 100,
                "poor": 50
            },
            "error_rate_percent": {
                "excellent": 0.1,
                "good": 1.0,
                "acceptable": 3.0,
                "poor": 5.0
            },
            "cpu_usage_percent": {
                "excellent": 50,
                "good": 70,
                "acceptable": 85,
                "poor": 95
            },
            "memory_usage_percent": {
                "excellent": 50,
                "good": 70,
                "acceptable": 85,
                "poor": 95
            }
        })
        
        # Weights for scoring
        self.weights = self.config.get("weights", {
            "response_time_ms": 0.2,
            "throughput_rps": 0.2,
            "error_rate_percent": 0.3,
            "cpu_usage_percent": 0.15,
            "memory_usage_percent": 0.15
        })
        
        logger.info("Simulation Analyzer initialized")
    
    def analyze_results(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze simulation results to provide insights and recommendations.
        
        Args:
            simulation_results: Results from simulation execution
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing simulation results")
        
        # Extract scenario results
        scenario_results = simulation_results.get("scenario_results", [])
        
        if not scenario_results:
            logger.warning("No scenario results to analyze")
            return {
                "success_rate": 0,
                "performance_score": 0,
                "resource_utilization": 0,
                "error_count": 0,
                "insights": ["No scenario results available for analysis"],
                "improvement_suggestions": ["Ensure scenarios are properly executed"]
            }
        
        # Calculate success rate
        success_count = sum(1 for result in scenario_results if result.get("success", False))
        success_rate = success_count / len(scenario_results)
        
        # Analyze each scenario
        scenario_analyses = []
        for result in scenario_results:
            scenario_analysis = self._analyze_scenario(result)
            scenario_analyses.append(scenario_analysis)
        
        # Calculate overall metrics
        performance_scores = [analysis["performance_score"] for analysis in scenario_analyses]
        resource_utilizations = [analysis["resource_utilization"] for analysis in scenario_analyses]
        error_counts = [analysis["error_count"] for analysis in scenario_analyses]
        
        overall_performance_score = statistics.mean(performance_scores) if performance_scores else 0
        overall_resource_utilization = statistics.mean(resource_utilizations) if resource_utilizations else 0
        overall_error_count = sum(error_counts)
        
        # Generate insights
        insights = self._generate_insights(scenario_analyses, success_rate, 
                                          overall_performance_score, overall_resource_utilization)
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            scenario_analyses, success_rate, overall_performance_score, overall_resource_utilization
        )
        
        # Compile analysis results
        analysis_results = {
            "success_rate": success_rate,
            "performance_score": overall_performance_score,
            "resource_utilization": overall_resource_utilization,
            "error_count": overall_error_count,
            "scenario_analyses": scenario_analyses,
            "insights": insights,
            "improvement_suggestions": improvement_suggestions,
            "deployment_readiness": self._assess_deployment_readiness(
                success_rate, overall_performance_score, overall_resource_utilization, overall_error_count
            )
        }
        
        logger.info(f"Analysis complete. Success rate: {success_rate:.2f}, "
                   f"Performance score: {overall_performance_score:.2f}")
        
        return analysis_results
    
    def _analyze_scenario(self, scenario_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single scenario result.
        
        Args:
            scenario_result: Result from a single scenario execution
            
        Returns:
            Dictionary containing scenario analysis
        """
        scenario_id = scenario_result.get("scenario_id", "unknown")
        success = scenario_result.get("success", False)
        errors = scenario_result.get("errors", [])
        
        # Extract metrics if available
        app_metrics = []
        resource_metrics = []
        
        if "metrics" in scenario_result:
            app_metrics = scenario_result["metrics"].get("application", [])
            resource_metrics = scenario_result["metrics"].get("resources", [])
        
        # Calculate performance metrics
        performance_metrics = {}
        if app_metrics:
            performance_metrics = {
                "response_time_ms": {
                    "avg": statistics.mean([m["response_time_ms"] for m in app_metrics]),
                    "min": min([m["response_time_ms"] for m in app_metrics]),
                    "max": max([m["response_time_ms"] for m in app_metrics]),
                    "p95": self._percentile([m["response_time_ms"] for m in app_metrics], 95)
                },
                "throughput_rps": {
                    "avg": statistics.mean([m["throughput_rps"] for m in app_metrics]),
                    "min": min([m["throughput_rps"] for m in app_metrics]),
                    "max": max([m["throughput_rps"] for m in app_metrics]),
                    "p95": self._percentile([m["throughput_rps"] for m in app_metrics], 95)
                },
                "error_rate_percent": {
                    "avg": statistics.mean([m["error_rate_percent"] for m in app_metrics]),
                    "min": min([m["error_rate_percent"] for m in app_metrics]),
                    "max": max([m["error_rate_percent"] for m in app_metrics]),
                    "p95": self._percentile([m["error_rate_percent"] for m in app_metrics], 95)
                }
            }
        
        # Calculate resource metrics
        resource_usage = {}
        if resource_metrics:
            resource_usage = {
                "cpu_usage_percent": {
                    "avg": statistics.mean([m["cpu_usage_percent"] for m in resource_metrics]),
                    "min": min([m["cpu_usage_percent"] for m in resource_metrics]),
                    "max": max([m["cpu_usage_percent"] for m in resource_metrics]),
                    "p95": self._percentile([m["cpu_usage_percent"] for m in resource_metrics], 95)
                },
                "memory_usage_percent": {
                    "avg": statistics.mean([m["memory_usage_percent"] for m in resource_metrics]),
                    "min": min([m["memory_usage_percent"] for m in resource_metrics]),
                    "max": max([m["memory_usage_percent"] for m in resource_metrics]),
                    "p95": self._percentile([m["memory_usage_percent"] for m in resource_metrics], 95)
                }
            }
        
        # Calculate performance score
        performance_score = 0
        if performance_metrics:
            performance_score = self._calculate_performance_score(performance_metrics)
        
        # Calculate resource utilization
        resource_utilization = 0
        if resource_usage:
            resource_utilization = self._calculate_resource_utilization(resource_usage)
        
        # Analyze errors
        error_analysis = self._analyze_errors(errors)
        
        # Generate scenario-specific insights
        insights = self._generate_scenario_insights(
            success, performance_metrics, resource_usage, error_analysis
        )
        
        return {
            "scenario_id": scenario_id,
            "success": success,
            "performance_score": performance_score,
            "resource_utilization": resource_utilization,
            "error_count": len(errors),
            "error_analysis": error_analysis,
            "performance_metrics": performance_metrics,
            "resource_usage": resource_usage,
            "insights": insights
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        Calculate the percentile value from a list of data points.
        
        Args:
            data: List of data points
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not data:
            return 0
        
        return np.percentile(data, percentile)
    
    def _calculate_performance_score(self, performance_metrics: Dict[str, Any]) -> float:
        """
        Calculate a performance score based on performance metrics.
        
        Args:
            performance_metrics: Dictionary of performance metrics
            
        Returns:
            Performance score (0-1)
        """
        scores = {}
        
        # Response time score (lower is better)
        if "response_time_ms" in performance_metrics:
            avg_response_time = performance_metrics["response_time_ms"]["avg"]
            thresholds = self.thresholds["response_time_ms"]
            
            if avg_response_time <= thresholds["excellent"]:
                scores["response_time_ms"] = 1.0
            elif avg_response_time <= thresholds["good"]:
                scores["response_time_ms"] = 0.8
            elif avg_response_time <= thresholds["acceptable"]:
                scores["response_time_ms"] = 0.6
            elif avg_response_time <= thresholds["poor"]:
                scores["response_time_ms"] = 0.3
            else:
                scores["response_time_ms"] = 0.1
        
        # Throughput score (higher is better)
        if "throughput_rps" in performance_metrics:
            avg_throughput = performance_metrics["throughput_rps"]["avg"]
            thresholds = self.thresholds["throughput_rps"]
            
            if avg_throughput >= thresholds["excellent"]:
                scores["throughput_rps"] = 1.0
            elif avg_throughput >= thresholds["good"]:
                scores["throughput_rps"] = 0.8
            elif avg_throughput >= thresholds["acceptable"]:
                scores["throughput_rps"] = 0.6
            elif avg_throughput >= thresholds["poor"]:
                scores["throughput_rps"] = 0.3
            else:
                scores["throughput_rps"] = 0.1
        
        # Error rate score (lower is better)
        if "error_rate_percent" in performance_metrics:
            avg_error_rate = performance_metrics["error_rate_percent"]["avg"]
            thresholds = self.thresholds["error_rate_percent"]
            
            if avg_error_rate <= thresholds["excellent"]:
                scores["error_rate_percent"] = 1.0
            elif avg_error_rate <= thresholds["good"]:
                scores["error_rate_percent"] = 0.8
            elif avg_error_rate <= thresholds["acceptable"]:
                scores["error_rate_percent"] = 0.6
            elif avg_error_rate <= thresholds["poor"]:
                scores["error_rate_percent"] = 0.3
            else:
                scores["error_rate_percent"] = 0.1
        
        # Calculate weighted score
        if not scores:
            return 0
        
        weighted_score = 0
        total_weight = 0
        
        for metric, score in scores.items():
            weight = self.weights.get(metric, 1)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def _calculate_resource_utilization(self, resource_usage: Dict[str, Any]) -> float:
        """
        Calculate resource utilization score based on resource usage metrics.
        
        Args:
            resource_usage: Dictionary of resource usage metrics
            
        Returns:
            Resource utilization score (0-1)
        """
        scores = {}
        
        # CPU usage score (lower is better, but too low might indicate underutilization)
        if "cpu_usage_percent" in resource_usage:
            avg_cpu_usage = resource_usage["cpu_usage_percent"]["avg"]
            thresholds = self.thresholds["cpu_usage_percent"]
            
            if avg_cpu_usage <= thresholds["excellent"]:
                scores["cpu_usage_percent"] = 1.0
            elif avg_cpu_usage <= thresholds["good"]:
                scores["cpu_usage_percent"] = 0.8
            elif avg_cpu_usage <= thresholds["acceptable"]:
                scores["cpu_usage_percent"] = 0.6
            elif avg_cpu_usage <= thresholds["poor"]:
                scores["cpu_usage_percent"] = 0.3
            else:
                scores["cpu_usage_percent"] = 0.1
        
        # Memory usage score (lower is better, but too low might indicate underutilization)
        if "memory_usage_percent" in resource_usage:
            avg_memory_usage = resource_usage["memory_usage_percent"]["avg"]
            thresholds = self.thresholds["memory_usage_percent"]
            
            if avg_memory_usage <= thresholds["excellent"]:
                scores["memory_usage_percent"] = 1.0
            elif avg_memory_usage <= thresholds["good"]:
                scores["memory_usage_percent"] = 0.8
            elif avg_memory_usage <= thresholds["acceptable"]:
                scores["memory_usage_percent"] = 0.6
            elif avg_memory_usage <= thresholds["poor"]:
                scores["memory_usage_percent"] = 0.3
            else:
                scores["memory_usage_percent"] = 0.1
        
        # Calculate weighted score
        if not scores:
            return 0
        
        weighted_score = 0
        total_weight = 0
        
        for metric, score in scores.items():
            weight = self.weights.get(metric, 1)
            weighted_score += score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0
    
    def _analyze_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze errors from simulation results.
        
        Args:
            errors: List of error dictionaries
            
        Returns:
            Dictionary containing error analysis
        """
        if not errors:
            return {
                "count": 0,
                "types": {},
                "severity": {},
                "components": {}
            }
        
        # Count error types
        error_types = Counter([error.get("type", "unknown") for error in errors])
        
        # Count error severities
        error_severities = Counter([
            error.get("details", {}).get("severity", "unknown") 
            for error in errors
        ])
        
        # Count affected components
        error_components = Counter([
            error.get("details", {}).get("component", "unknown") 
            for error in errors
        ])
        
        return {
            "count": len(errors),
            "types": dict(error_types),
            "severity": dict(error_severities),
            "components": dict(error_components)
        }
    
    def _generate_scenario_insights(self, 
                                   success: bool,
                                   performance_metrics: Dict[str, Any],
                                   resource_usage: Dict[str, Any],
                                   error_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate insights for a specific scenario.
        
        Args:
            success: Whether the scenario was successful
            performance_metrics: Performance metrics for the scenario
            resource_usage: Resource usage metrics for the scenario
            error_analysis: Error analysis for the scenario
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Success/failure insights
        if success:
            insights.append("Scenario completed successfully")
        else:
            insights.append(f"Scenario failed with {error_analysis['count']} errors")
            
            # Add insights about error types
            for error_type, count in error_analysis.get("types", {}).items():
                insights.append(f"Encountered {count} {error_type} errors")
        
        # Performance insights
        if "response_time_ms" in performance_metrics:
            avg_response_time = performance_metrics["response_time_ms"]["avg"]
            p95_response_time = performance_metrics["response_time_ms"]["p95"]
            
            if avg_response_time < 100:
                insights.append("Response time is excellent")
            elif avg_response_time < 300:
                insights.append("Response time is good")
            elif avg_response_time < 500:
                insights.append("Response time is acceptable")
            else:
                insights.append("Response time is poor and needs improvement")
            
            if p95_response_time > avg_response_time * 2:
                insights.append("Response time has high variability, indicating potential instability")
        
        if "throughput_rps" in performance_metrics:
            avg_throughput = performance_metrics["throughput_rps"]["avg"]
            
            if avg_throughput > 500:
                insights.append("Throughput is excellent")
            elif avg_throughput > 200:
                insights.append("Throughput is good")
            elif avg_throughput > 100:
                insights.append("Throughput is acceptable")
            else:
                insights.append("Throughput is low and may need improvement")
        
        if "error_rate_percent" in performance_metrics:
            avg_error_rate = performance_metrics["error_rate_percent"]["avg"]
            
            if avg_error_rate < 0.1:
                insights.append("Error rate is negligible")
            elif avg_error_rate < 1.0:
                insights.append("Error rate is acceptable")
            elif avg_error_rate < 3.0:
                insights.append("Error rate is concerning and should be addressed")
            else:
                insights.append("Error rate is high and requires immediate attention")
        
        # Resource usage insights
        if "cpu_usage_percent" in resource_usage:
            avg_cpu_usage = resource_usage["cpu_usage_percent"]["avg"]
            max_cpu_usage = resource_usage["cpu_usage_percent"]["max"]
            
            if max_cpu_usage > 90:
                insights.append("CPU usage peaked above 90%, indicating potential resource constraints")
            
            if avg_cpu_usage < 30:
                insights.append("Average CPU usage is low, indicating potential resource underutilization")
            elif avg_cpu_usage > 80:
                insights.append("Average CPU usage is high, consider allocating more CPU resources")
        
        if "memory_usage_percent" in resource_usage:
            avg_memory_usage = resource_usage["memory_usage_percent"]["avg"]
            max_memory_usage = resource_usage["memory_usage_percent"]["max"]
            
            if max_memory_usage > 90:
                insights.append("Memory usage peaked above 90%, indicating potential resource constraints")
            
            if avg_memory_usage < 30:
                insights.append("Average memory usage is low, indicating potential resource underutilization")
            elif avg_memory_usage > 80:
                insights.append("Average memory usage is high, consider allocating more memory")
        
        return insights
    
    def _generate_insights(self, 
                          scenario_analyses: List[Dict[str, Any]],
                          success_rate: float,
                          performance_score: float,
                          resource_utilization: float) -> List[str]:
        """
        Generate overall insights from all scenario analyses.
        
        Args:
            scenario_analyses: List of scenario analysis dictionaries
            success_rate: Overall success rate
            performance_score: Overall performance score
            resource_utilization: Overall resource utilization
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Success rate insights
        if success_rate == 1.0:
            insights.append("All scenarios completed successfully")
        elif success_rate >= 0.8:
            insights.append(f"{success_rate*100:.1f}% of scenarios completed successfully")
        else:
            insights.append(f"Only {success_rate*100:.1f}% of scenarios completed successfully, indicating significant issues")
        
        # Performance score insights
        if performance_score >= 0.9:
            insights.append("Overall performance is excellent")
        elif performance_score >= 0.7:
            insights.append("Overall performance is good")
        elif performance_score >= 0.5:
            insights.append("Overall performance is acceptable")
        else:
            insights.append("Overall performance is poor and needs improvement")
        
        # Resource utilization insights
        if resource_utilization >= 0.9:
            insights.append("Resource utilization is optimal")
        elif resource_utilization >= 0.7:
            insights.append("Resource utilization is good")
        elif resource_utilization >= 0.5:
            insights.append("Resource utilization is acceptable")
        else:
            insights.append("Resource utilization is poor, indicating potential inefficiencies")
        
        # Error pattern insights
        error_types = Counter()
        error_components = Counter()
        
        for analysis in scenario_analyses:
            error_analysis = analysis.get("error_analysis", {})
            for error_type, count in error_analysis.get("types", {}).items():
                error_types[error_type] += count
            for component, count in error_analysis.get("components", {}).items():
                error_components[component] += count
        
        if error_types:
            most_common_error = error_types.most_common(1)[0]
            insights.append(f"Most common error type: {most_common_error[0]} ({most_common_error[1]} occurrences)")
        
        if error_components:
            most_affected_component = error_components.most_common(1)[0]
            insights.append(f"Most affected component: {most_affected_component[0]} ({most_affected_component[1]} errors)")
        
        # Scenario-specific insights
        failed_scenarios = [a for a in scenario_analyses if not a.get("success", False)]
        if failed_scenarios:
            insights.append(f"{len(failed_scenarios)} scenarios failed, requiring attention")
        
        return insights
    
    def _generate_improvement_suggestions(self,
                                         scenario_analyses: List[Dict[str, Any]],
                                         success_rate: float,
                                         performance_score: float,
                                         resource_utilization: float) -> List[str]:
        """
        Generate improvement suggestions based on analysis results.
        
        Args:
            scenario_analyses: List of scenario analysis dictionaries
            success_rate: Overall success rate
            performance_score: Overall performance score
            resource_utilization: Overall resource utilization
            
        Returns:
            List of improvement suggestion strings
        """
        suggestions = []
        
        # Success rate suggestions
        if success_rate < 1.0:
            suggestions.append("Address failures in scenarios to improve overall success rate")
        
        # Performance suggestions
        if performance_score < 0.7:
            # Analyze specific performance metrics
            response_time_issues = False
            throughput_issues = False
            error_rate_issues = False
            
            for analysis in scenario_analyses:
                metrics = analysis.get("performance_metrics", {})
                
                if "response_time_ms" in metrics and metrics["response_time_ms"]["avg"] > 300:
                    response_time_issues = True
                
                if "throughput_rps" in metrics and metrics["throughput_rps"]["avg"] < 100:
                    throughput_issues = True
                
                if "error_rate_percent" in metrics and metrics["error_rate_percent"]["avg"] > 1.0:
                    error_rate_issues = True
            
            if response_time_issues:
                suggestions.append("Optimize code and database queries to improve response times")
            
            if throughput_issues:
                suggestions.append("Increase capacity or optimize request handling to improve throughput")
            
            if error_rate_issues:
                suggestions.append("Implement better error handling and fix bugs to reduce error rates")
        
        # Resource utilization suggestions
        if resource_utilization < 0.7:
            # Analyze specific resource metrics
            cpu_underutilization = False
            memory_underutilization = False
            cpu_overutilization = False
            memory_overutilization = False
            
            for analysis in scenario_analyses:
                usage = analysis.get("resource_usage", {})
                
                if "cpu_usage_percent" in usage:
                    if usage["cpu_usage_percent"]["avg"] < 30:
                        cpu_underutilization = True
                    elif usage["cpu_usage_percent"]["avg"] > 80:
                        cpu_overutilization = True
                
                if "memory_usage_percent" in usage:
                    if usage["memory_usage_percent"]["avg"] < 30:
                        memory_underutilization = True
                    elif usage["memory_usage_percent"]["avg"] > 80:
                        memory_overutilization = True
            
            if cpu_underutilization:
                suggestions.append("Consider reducing CPU allocation to improve resource efficiency")
            
            if memory_underutilization:
                suggestions.append("Consider reducing memory allocation to improve resource efficiency")
            
            if cpu_overutilization:
                suggestions.append("Increase CPU allocation or optimize CPU usage to prevent bottlenecks")
            
            if memory_overutilization:
                suggestions.append("Increase memory allocation or optimize memory usage to prevent out-of-memory errors")
        
        # Error-based suggestions
        error_types = Counter()
        for analysis in scenario_analyses:
            error_analysis = analysis.get("error_analysis", {})
            for error_type, count in error_analysis.get("types", {}).items():
                error_types[error_type] += count
        
        if "network_error" in error_types:
            suggestions.append("Improve network resilience with retry mechanisms and circuit breakers")
        
        if "timeout_error" in error_types:
            suggestions.append("Optimize slow operations or increase timeout thresholds")
        
        if "resource_error" in error_types:
            suggestions.append("Increase resource limits or implement better resource management")
        
        if "application_error" in error_types:
            suggestions.append("Fix application bugs and improve error handling")
        
        # Add general suggestions if list is empty
        if not suggestions:
            if success_rate == 1.0 and performance_score >= 0.7 and resource_utilization >= 0.7:
                suggestions.append("Current implementation is performing well, focus on monitoring and maintenance")
            else:
                suggestions.append("Conduct more detailed analysis to identify specific areas for improvement")
        
        return suggestions
    
    def _assess_deployment_readiness(self,
                                    success_rate: float,
                                    performance_score: float,
                                    resource_utilization: float,
                                    error_count: int) -> Dict[str, Any]:
        """
        Assess deployment readiness based on analysis results.
        
        Args:
            success_rate: Overall success rate
            performance_score: Overall performance score
            resource_utilization: Overall resource utilization
            error_count: Total number of errors
            
        Returns:
            Dictionary with deployment readiness assessment
        """
        # Calculate readiness score
        readiness_score = (
            success_rate * 0.4 +
            performance_score * 0.3 +
            resource_utilization * 0.2 -
            min(1.0, error_count / 10) * 0.1  # Penalize for errors, max penalty 0.1
        )
        
        # Determine readiness level
        if readiness_score >= 0.8:
            readiness_level = "ready"
            confidence = "high"
        elif readiness_score >= 0.6:
            readiness_level = "ready_with_caution"
            confidence = "medium"
        elif readiness_score >= 0.4:
            readiness_level = "needs_improvements"
            confidence = "medium"
        else:
            readiness_level = "not_ready"
            confidence = "high"
        
        # Generate readiness factors
        factors = []
        
        if success_rate >= 0.9:
            factors.append({"factor": "success_rate", "assessment": "positive", "value": success_rate})
        else:
            factors.append({"factor": "success_rate", "assessment": "negative", "value": success_rate})
        
        if performance_score >= 0.7:
            factors.append({"factor": "performance", "assessment": "positive", "value": performance_score})
        else:
            factors.append({"factor": "performance", "assessment": "negative", "value": performance_score})
        
        if resource_utilization >= 0.7:
            factors.append({"factor": "resource_utilization", "assessment": "positive", "value": resource_utilization})
        else:
            factors.append({"factor": "resource_utilization", "assessment": "negative", "value": resource_utilization})
        
        if error_count == 0:
            factors.append({"factor": "errors", "assessment": "positive", "value": error_count})
        else:
            factors.append({"factor": "errors", "assessment": "negative", "value": error_count})
        
        return {
            "score": readiness_score,
            "level": readiness_level,
            "confidence": confidence,
            "factors": factors
        }
    
    def compare_simulations(self, simulations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple simulations to identify trends and differences.
        
        Args:
            simulations: List of simulation data dictionaries
            
        Returns:
            Dictionary with comparison results
        """
        if not simulations:
            return {"error": "No simulations to compare"}
        
        if len(simulations) == 1:
            return {"error": "Need at least two simulations to compare"}
        
        # Extract key metrics from each simulation
        metrics = []
        for sim in simulations:
            analysis = sim.get("analysis", {})
            metrics.append({
                "timestamp": sim.get("timestamp", 0),
                "success_rate": analysis.get("success_rate", 0),
                "performance_score": analysis.get("performance_score", 0),
                "resource_utilization": analysis.get("resource_utilization", 0),
                "error_count": analysis.get("error_count", 0)
            })
        
        # Sort by timestamp
        metrics.sort(key=lambda x: x["timestamp"])
        
        # Calculate trends
        trends = {
            "success_rate": self._calculate_trend([m["success_rate"] for m in metrics]),
            "performance_score": self._calculate_trend([m["performance_score"] for m in metrics]),
            "resource_utilization": self._calculate_trend([m["resource_utilization"] for m in metrics]),
            "error_count": self._calculate_trend([m["error_count"] for m in metrics], lower_is_better=True)
        }
        
        # Calculate differences between first and last
        first = metrics[0]
        last = metrics[-1]
        
        differences = {
            "success_rate": last["success_rate"] - first["success_rate"],
            "performance_score": last["performance_score"] - first["performance_score"],
            "resource_utilization": last["resource_utilization"] - first["resource_utilization"],
            "error_count": last["error_count"] - first["error_count"]
        }
        
        # Generate insights
        insights = []
        
        if trends["success_rate"] == "improving":
            insights.append("Success rate is improving over time")
        elif trends["success_rate"] == "declining":
            insights.append("Success rate is declining over time")
        
        if trends["performance_score"] == "improving":
            insights.append("Performance is improving over time")
        elif trends["performance_score"] == "declining":
            insights.append("Performance is declining over time")
        
        if trends["error_count"] == "improving":
            insights.append("Error count is decreasing over time")
        elif trends["error_count"] == "declining":
            insights.append("Error count is increasing over time")
        
        return {
            "metrics": metrics,
            "trends": trends,
            "differences": differences,
            "insights": insights
        }
    
    def _calculate_trend(self, values: List[float], lower_is_better: bool = False) -> str:
        """
        Calculate the trend in a series of values.
        
        Args:
            values: List of values
            lower_is_better: Whether lower values are better
            
        Returns:
            Trend description: "improving", "declining", or "stable"
        """
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Determine trend
        if abs(slope) < 0.01:  # Threshold for stability
            return "stable"
        
        if lower_is_better:
            return "improving" if slope < 0 else "declining"
        else:
            return "improving" if slope > 0 else "declining"
