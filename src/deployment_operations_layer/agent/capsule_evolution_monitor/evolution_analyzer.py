"""
Evolution Analyzer - Analyzes capsule evolution patterns

This module analyzes the evolution of capsules over time, identifying patterns,
trends, and potential issues in how capsules change after deployment.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

logger = logging.getLogger(__name__)

class EvolutionAnalyzer:
    """
    Analyzes the evolution of capsules over time.
    
    This component is responsible for analyzing how capsules evolve after
    deployment, identifying patterns, trends, and potential issues in
    capsule mutations and overrides.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Evolution Analyzer.
        
        Args:
            config: Configuration dictionary for the analyzer
        """
        self.config = config or {}
        self.analysis_cache = {}  # Capsule ID -> Analysis results
        self.anomaly_thresholds = self.config.get("anomaly_thresholds", {
            "mutation_rate": 5,  # mutations per day
            "override_rate": 2,  # overrides per day
            "drift_percentage": 30  # percent change from original
        })
        
        logger.info("Initializing Evolution Analyzer")
    
    def initialize(self):
        """Initialize the analyzer."""
        logger.info("Initializing Evolution Analyzer")
        return True
    
    def analyze_evolution(self, capsule_id: str, changes: Dict[str, Any], 
                         mutation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a single evolution event.
        
        Args:
            capsule_id: ID of the capsule
            changes: Dictionary describing the changes
            mutation_history: History of mutations for this capsule
            
        Returns:
            Dictionary with analysis results
        """
        # Calculate basic metrics
        total_mutations = len(mutation_history)
        
        # Calculate mutation rate (mutations per day)
        if total_mutations > 1:
            first_mutation_time = datetime.fromisoformat(mutation_history[0]["timestamp"])
            last_mutation_time = datetime.fromisoformat(mutation_history[-1]["timestamp"])
            days_diff = (last_mutation_time - first_mutation_time).total_seconds() / 86400
            mutation_rate = total_mutations / max(days_diff, 1)
        else:
            mutation_rate = 0
        
        # Analyze change patterns
        change_patterns = self._analyze_change_patterns(mutation_history)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(capsule_id, changes, mutation_history, mutation_rate)
        
        # Prepare analysis result
        analysis = {
            "capsule_id": capsule_id,
            "timestamp": datetime.now().isoformat(),
            "total_mutations": total_mutations,
            "mutation_rate": mutation_rate,
            "change_patterns": change_patterns,
            "anomalies": anomalies,
            "stability_score": self._calculate_stability_score(mutation_rate, anomalies),
            "recommendations": self._generate_recommendations(mutation_rate, anomalies, change_patterns)
        }
        
        # Cache analysis result
        self.analysis_cache[capsule_id] = analysis
        
        logger.info(f"Analyzed evolution for capsule {capsule_id}")
        return analysis
    
    def generate_evolution_report(self, capsule_id: str, mutation_history: List[Dict[str, Any]],
                                 override_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive evolution report for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            mutation_history: History of mutations for this capsule
            override_history: History of overrides for this capsule
            
        Returns:
            Dictionary with report data
        """
        # Calculate basic metrics
        total_mutations = len(mutation_history)
        total_overrides = len(override_history)
        
        # Calculate time-based metrics
        if total_mutations > 1:
            first_mutation_time = datetime.fromisoformat(mutation_history[0]["timestamp"])
            last_mutation_time = datetime.fromisoformat(mutation_history[-1]["timestamp"])
            days_diff = (last_mutation_time - first_mutation_time).total_seconds() / 86400
            mutation_rate = total_mutations / max(days_diff, 1)
        else:
            mutation_rate = 0
            days_diff = 0
        
        # Calculate override rate
        if total_overrides > 1:
            first_override_time = datetime.fromisoformat(override_history[0]["timestamp"])
            last_override_time = datetime.fromisoformat(override_history[-1]["timestamp"])
            override_days_diff = (last_override_time - first_override_time).total_seconds() / 86400
            override_rate = total_overrides / max(override_days_diff, 1)
        else:
            override_rate = 0
        
        # Analyze change patterns
        change_patterns = self._analyze_change_patterns(mutation_history)
        
        # Analyze override patterns
        override_patterns = self._analyze_override_patterns(override_history)
        
        # Detect anomalies
        anomalies = []
        for mutation in mutation_history:
            anomalies.extend(self._detect_anomalies(
                capsule_id, 
                mutation.get("changes", {}), 
                mutation_history, 
                mutation_rate
            ))
        
        # Prepare report
        report = {
            "capsule_id": capsule_id,
            "report_timestamp": datetime.now().isoformat(),
            "monitoring_period_days": days_diff,
            "total_mutations": total_mutations,
            "total_overrides": total_overrides,
            "mutation_rate": mutation_rate,
            "override_rate": override_rate,
            "change_patterns": change_patterns,
            "override_patterns": override_patterns,
            "anomalies": anomalies,
            "stability_score": self._calculate_stability_score(mutation_rate, anomalies),
            "health_assessment": self._assess_health(mutation_rate, override_rate, anomalies),
            "recommendations": self._generate_recommendations(mutation_rate, anomalies, change_patterns),
            "trend_analysis": self._analyze_trends(mutation_history, override_history)
        }
        
        # Add MCP/A2A integration data
        report["mcp_context"] = self._generate_mcp_context(capsule_id, report)
        report["a2a_metadata"] = self._generate_a2a_metadata(capsule_id, report)
        
        logger.info(f"Generated evolution report for capsule {capsule_id}")
        return report
    
    def _analyze_change_patterns(self, mutation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in capsule changes.
        
        Args:
            mutation_history: History of mutations
            
        Returns:
            Dictionary with pattern analysis
        """
        if not mutation_history:
            return {"patterns_detected": False}
        
        # Count changes by type
        change_types = {}
        for mutation in mutation_history:
            changes = mutation.get("changes", {})
            for change_type, _ in changes.items():
                if change_type not in ["source", "reason", "authorized"]:
                    change_types[change_type] = change_types.get(change_type, 0) + 1
        
        # Identify most common change types
        most_common_changes = sorted(change_types.items(), key=lambda x: x[1], reverse=True)
        
        # Analyze time patterns
        time_patterns = self._analyze_time_patterns(mutation_history)
        
        return {
            "patterns_detected": len(most_common_changes) > 0,
            "most_common_changes": most_common_changes[:5] if most_common_changes else [],
            "time_patterns": time_patterns,
            "cyclic_changes": self._detect_cyclic_changes(mutation_history)
        }
    
    def _analyze_override_patterns(self, override_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in capsule overrides.
        
        Args:
            override_history: History of overrides
            
        Returns:
            Dictionary with pattern analysis
        """
        if not override_history:
            return {"patterns_detected": False}
        
        # Count overrides by source
        override_sources = {}
        for override in override_history:
            source = override.get("override_source", "unknown")
            override_sources[source] = override_sources.get(source, 0) + 1
        
        # Identify most common override sources
        most_common_sources = sorted(override_sources.items(), key=lambda x: x[1], reverse=True)
        
        # Analyze time patterns
        time_patterns = self._analyze_time_patterns(override_history)
        
        return {
            "patterns_detected": len(most_common_sources) > 0,
            "most_common_sources": most_common_sources[:5] if most_common_sources else [],
            "time_patterns": time_patterns,
            "authorization_rate": self._calculate_authorization_rate(override_history)
        }
    
    def _analyze_time_patterns(self, event_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze time patterns in events.
        
        Args:
            event_history: History of events
            
        Returns:
            Dictionary with time pattern analysis
        """
        if len(event_history) < 2:
            return {"patterns_detected": False}
        
        # Extract timestamps
        timestamps = [datetime.fromisoformat(event["timestamp"]) for event in event_history]
        
        # Calculate time differences between consecutive events
        time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                     for i in range(1, len(timestamps))]
        
        # Calculate statistics
        avg_time_diff = statistics.mean(time_diffs)
        median_time_diff = statistics.median(time_diffs)
        
        try:
            stddev_time_diff = statistics.stdev(time_diffs)
            regularity = 1 - min(stddev_time_diff / avg_time_diff, 1) if avg_time_diff > 0 else 0
        except statistics.StatisticsError:
            stddev_time_diff = 0
            regularity = 0
        
        # Detect time of day patterns
        hours = [ts.hour for ts in timestamps]
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        most_common_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "patterns_detected": True,
            "avg_time_between_events_seconds": avg_time_diff,
            "median_time_between_events_seconds": median_time_diff,
            "time_regularity_score": regularity,
            "most_common_hours": most_common_hours[:3] if most_common_hours else []
        }
    
    def _detect_cyclic_changes(self, mutation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect cyclic changes in mutation history.
        
        Args:
            mutation_history: History of mutations
            
        Returns:
            Dictionary with cyclic change analysis
        """
        if len(mutation_history) < 3:
            return {"cyclic_changes_detected": False}
        
        # This is a simplified implementation
        # A more sophisticated implementation would use time series analysis
        
        # Check for alternating values in common fields
        cyclic_fields = []
        
        # Get all fields that appear in changes
        all_fields = set()
        for mutation in mutation_history:
            changes = mutation.get("changes", {})
            for field in changes.keys():
                if field not in ["source", "reason", "authorized"]:
                    all_fields.add(field)
        
        # Check each field for cyclic patterns
        for field in all_fields:
            values = []
            for mutation in mutation_history:
                changes = mutation.get("changes", {})
                if field in changes:
                    values.append(str(changes[field]))
            
            # Check for repeating patterns
            if len(values) >= 4:  # Need at least 4 values to detect a pattern of length 2
                for pattern_length in range(1, min(3, len(values) // 2)):
                    is_cyclic = True
                    pattern = values[:pattern_length]
                    
                    for i in range(pattern_length, len(values), pattern_length):
                        if i + pattern_length > len(values):
                            # Partial pattern at the end
                            if values[i:] != pattern[:len(values) - i]:
                                is_cyclic = False
                                break
                        elif values[i:i+pattern_length] != pattern:
                            is_cyclic = False
                            break
                    
                    if is_cyclic:
                        cyclic_fields.append({
                            "field": field,
                            "pattern": pattern,
                            "pattern_length": pattern_length
                        })
                        break
        
        return {
            "cyclic_changes_detected": len(cyclic_fields) > 0,
            "cyclic_fields": cyclic_fields
        }
    
    def _calculate_authorization_rate(self, override_history: List[Dict[str, Any]]) -> float:
        """
        Calculate the rate of authorized overrides.
        
        Args:
            override_history: History of overrides
            
        Returns:
            Authorization rate (0-1)
        """
        if not override_history:
            return 0
        
        authorized_count = 0
        for override in override_history:
            metadata = override.get("metadata", {})
            if metadata.get("authorized", False):
                authorized_count += 1
        
        return authorized_count / len(override_history)
    
    def _detect_anomalies(self, capsule_id: str, changes: Dict[str, Any], 
                         mutation_history: List[Dict[str, Any]], mutation_rate: float) -> List[Dict[str, Any]]:
        """
        Detect anomalies in capsule evolution.
        
        Args:
            capsule_id: ID of the capsule
            changes: Dictionary describing the changes
            mutation_history: History of mutations for this capsule
            mutation_rate: Rate of mutations per day
            
        Returns:
            List of anomaly dictionaries
        """
        anomalies = []
        
        # Check mutation rate anomaly
        if mutation_rate > self.anomaly_thresholds["mutation_rate"]:
            anomalies.append({
                "type": "high_mutation_rate",
                "severity": "medium",
                "description": f"Mutation rate ({mutation_rate:.2f}/day) exceeds threshold ({self.anomaly_thresholds['mutation_rate']}/day)",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for unauthorized changes
        if not changes.get("authorized", False):
            anomalies.append({
                "type": "unauthorized_change",
                "severity": "high",
                "description": "Change was not authorized",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for rapid successive changes
        if len(mutation_history) >= 2:
            latest_mutations = mutation_history[-2:]
            latest_time = datetime.fromisoformat(latest_mutations[1]["timestamp"])
            previous_time = datetime.fromisoformat(latest_mutations[0]["timestamp"])
            time_diff_seconds = (latest_time - previous_time).total_seconds()
            
            if time_diff_seconds < 60:  # Less than a minute apart
                anomalies.append({
                    "type": "rapid_successive_changes",
                    "severity": "medium",
                    "description": f"Changes occurred only {time_diff_seconds:.1f} seconds apart",
                    "timestamp": datetime.now().isoformat()
                })
        
        return anomalies
    
    def _calculate_stability_score(self, mutation_rate: float, anomalies: List[Dict[str, Any]]) -> float:
        """
        Calculate a stability score for the capsule.
        
        Args:
            mutation_rate: Rate of mutations per day
            anomalies: List of detected anomalies
            
        Returns:
            Stability score (0-100)
        """
        # Base score
        score = 100
        
        # Deduct for mutation rate
        rate_factor = min(mutation_rate / self.anomaly_thresholds["mutation_rate"], 1)
        score -= rate_factor * 30
        
        # Deduct for anomalies
        for anomaly in anomalies:
            if anomaly["severity"] == "high":
                score -= 15
            elif anomaly["severity"] == "medium":
                score -= 10
            else:
                score -= 5
        
        return max(0, score)
    
    def _assess_health(self, mutation_rate: float, override_rate: float, 
                      anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess the health of the capsule based on its evolution.
        
        Args:
            mutation_rate: Rate of mutations per day
            override_rate: Rate of overrides per day
            anomalies: List of detected anomalies
            
        Returns:
            Dictionary with health assessment
        """
        # Calculate stability score
        stability_score = self._calculate_stability_score(mutation_rate, anomalies)
        
        # Determine health status
        if stability_score >= 80:
            status = "healthy"
        elif stability_score >= 60:
            status = "stable"
        elif stability_score >= 40:
            status = "unstable"
        else:
            status = "critical"
        
        # Count anomalies by severity
        high_severity = sum(1 for a in anomalies if a["severity"] == "high")
        medium_severity = sum(1 for a in anomalies if a["severity"] == "medium")
        low_severity = sum(1 for a in anomalies if a["severity"] == "low")
        
        return {
            "status": status,
            "stability_score": stability_score,
            "mutation_health": "high" if mutation_rate > self.anomaly_thresholds["mutation_rate"] else "normal",
            "override_health": "high" if override_rate > self.anomaly_thresholds["override_rate"] else "normal",
            "anomaly_counts": {
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity
            }
        }
    
    def _generate_recommendations(self, mutation_rate: float, anomalies: List[Dict[str, Any]],
                                change_patterns: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on analysis.
        
        Args:
            mutation_rate: Rate of mutations per day
            anomalies: List of detected anomalies
            change_patterns: Dictionary with change pattern analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Recommendations based on mutation rate
        if mutation_rate > self.anomaly_thresholds["mutation_rate"]:
            recommendations.append(
                "Reduce the frequency of changes to improve stability"
            )
        
        # Recommendations based on anomalies
        unauthorized_changes = any(a["type"] == "unauthorized_change" for a in anomalies)
        if unauthorized_changes:
            recommendations.append(
                "Implement stricter authorization controls for capsule changes"
            )
        
        rapid_changes = any(a["type"] == "rapid_successive_changes" for a in anomalies)
        if rapid_changes:
            recommendations.append(
                "Implement a cooldown period between changes to prevent rapid successive modifications"
            )
        
        # Recommendations based on change patterns
        if change_patterns.get("patterns_detected", False):
            cyclic_changes = change_patterns.get("cyclic_changes", {}).get("cyclic_changes_detected", False)
            if cyclic_changes:
                recommendations.append(
                    "Review cyclic changes to identify and fix oscillating configurations"
                )
            
            time_patterns = change_patterns.get("time_patterns", {})
            if time_patterns.get("patterns_detected", False) and time_patterns.get("time_regularity_score", 0) > 0.7:
                recommendations.append(
                    "Consider automating regular changes to reduce manual intervention"
                )
        
        # Default recommendation if none generated
        if not recommendations:
            recommendations.append(
                "Continue monitoring capsule evolution for potential issues"
            )
        
        return recommendations
    
    def _analyze_trends(self, mutation_history: List[Dict[str, Any]], 
                       override_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends in capsule evolution.
        
        Args:
            mutation_history: History of mutations
            override_history: History of overrides
            
        Returns:
            Dictionary with trend analysis
        """
        if not mutation_history:
            return {"trends_detected": False}
        
        # Group mutations by day
        mutations_by_day = {}
        for mutation in mutation_history:
            timestamp = datetime.fromisoformat(mutation["timestamp"])
            day_key = timestamp.strftime("%Y-%m-%d")
            if day_key not in mutations_by_day:
                mutations_by_day[day_key] = []
            mutations_by_day[day_key].append(mutation)
        
        # Calculate daily mutation counts
        daily_counts = {day: len(mutations) for day, mutations in mutations_by_day.items()}
        
        # Sort days
        sorted_days = sorted(daily_counts.keys())
        
        # Calculate trend
        if len(sorted_days) >= 3:
            first_half = sorted_days[:len(sorted_days)//2]
            second_half = sorted_days[len(sorted_days)//2:]
            
            first_half_avg = sum(daily_counts[day] for day in first_half) / len(first_half)
            second_half_avg = sum(daily_counts[day] for day in second_half) / len(second_half)
            
            if second_half_avg > first_half_avg * 1.2:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trends_detected": True,
            "mutation_trend": trend,
            "daily_mutation_counts": daily_counts,
            "override_trend": self._calculate_override_trend(override_history)
        }
    
    def _calculate_override_trend(self, override_history: List[Dict[str, Any]]) -> str:
        """
        Calculate the trend in override frequency.
        
        Args:
            override_history: History of overrides
            
        Returns:
            Trend description
        """
        if len(override_history) < 3:
            return "insufficient_data"
        
        # Group overrides by day
        overrides_by_day = {}
        for override in override_history:
            timestamp = datetime.fromisoformat(override["timestamp"])
            day_key = timestamp.strftime("%Y-%m-%d")
            if day_key not in overrides_by_day:
                overrides_by_day[day_key] = []
            overrides_by_day[day_key].append(override)
        
        # Calculate daily override counts
        daily_counts = {day: len(overrides) for day, overrides in overrides_by_day.items()}
        
        # Sort days
        sorted_days = sorted(daily_counts.keys())
        
        # Calculate trend
        if len(sorted_days) >= 3:
            first_half = sorted_days[:len(sorted_days)//2]
            second_half = sorted_days[len(sorted_days)//2:]
            
            first_half_avg = sum(daily_counts[day] for day in first_half) / len(first_half)
            second_half_avg = sum(daily_counts[day] for day in second_half) / len(second_half)
            
            if second_half_avg > first_half_avg * 1.2:
                return "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                return "decreasing"
            else:
                return "stable"
        else:
            return "insufficient_data"
    
    def _generate_mcp_context(self, capsule_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MCP context for the evolution report.
        
        Args:
            capsule_id: ID of the capsule
            report: Evolution report
            
        Returns:
            Dictionary with MCP context
        """
        # This is a placeholder for MCP integration
        # In a real implementation, this would generate a proper MCP context
        return {
            "contextType": "capsule_evolution",
            "capsuleId": capsule_id,
            "stabilityScore": report["stability_score"],
            "healthStatus": report["health_assessment"]["status"],
            "anomalyCount": sum(report["health_assessment"]["anomaly_counts"].values()),
            "recommendations": report["recommendations"]
        }
    
    def _generate_a2a_metadata(self, capsule_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate A2A metadata for the evolution report.
        
        Args:
            capsule_id: ID of the capsule
            report: Evolution report
            
        Returns:
            Dictionary with A2A metadata
        """
        # This is a placeholder for A2A integration
        # In a real implementation, this would generate proper A2A metadata
        return {
            "agentId": f"evolution_analyzer_{capsule_id}",
            "industryTags": ["manufacturing", "industrial_automation"],
            "priority": "medium" if report["health_assessment"]["status"] in ["unstable", "critical"] else "low",
            "capabilities": {
                "evolutionAnalysis": True,
                "anomalyDetection": True,
                "trendAnalysis": True
            }
        }
