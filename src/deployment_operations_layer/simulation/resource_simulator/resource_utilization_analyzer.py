"""
Resource Utilization Analyzer

This module is responsible for analyzing resource utilization patterns and providing
insights for optimization. It works with the Resource Simulator to analyze simulated
resource data and with real deployment data to provide optimization recommendations.
"""

import logging
import time
import json
import os
import statistics
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ResourceUtilizationAnalyzer:
    """
    Analyzes resource utilization patterns and provides optimization insights.
    
    This class works with the Resource Simulator to analyze simulated resource data
    and with real deployment data to provide optimization recommendations. It can
    identify resource bottlenecks, usage patterns, and provide recommendations for
    resource allocation and scaling.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Resource Utilization Analyzer.
        
        Args:
            config: Configuration dictionary for the analyzer
        """
        self.config = config or {}
        
        # Analysis settings
        self.analysis_window = self.config.get("analysis_window", 300)  # 5 minutes
        self.sampling_interval = self.config.get("sampling_interval", 5)  # 5 seconds
        
        # Resource data
        self.resource_data = {
            "cpu": [],
            "memory": [],
            "storage": [],
            "network": {
                "bandwidth": [],
                "latency": [],
                "packet_loss": []
            }
        }
        
        # Analysis results
        self.analysis_results = {}
        
        # Data storage
        self.data_dir = self.config.get("data_dir", "/tmp/resource_analysis")
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info("Resource Utilization Analyzer initialized")
    
    def record_resource_state(self, resource_state: Dict[str, Any]):
        """
        Record a resource state snapshot.
        
        Args:
            resource_state: Resource state snapshot
        """
        timestamp = time.time()
        
        # Add CPU data
        cpu_state = resource_state.get("cpu", {})
        self.resource_data["cpu"].append({
            "timestamp": timestamp,
            "total": cpu_state.get("total", 0),
            "available": cpu_state.get("available", 0),
            "utilized": cpu_state.get("utilized", 0),
            "utilization_percent": self._calculate_utilization_percent(
                cpu_state.get("utilized", 0),
                cpu_state.get("total", 0)
            )
        })
        
        # Add memory data
        memory_state = resource_state.get("memory", {})
        self.resource_data["memory"].append({
            "timestamp": timestamp,
            "total": memory_state.get("total", 0),
            "available": memory_state.get("available", 0),
            "utilized": memory_state.get("utilized", 0),
            "utilization_percent": self._calculate_utilization_percent(
                memory_state.get("utilized", 0),
                memory_state.get("total", 0)
            )
        })
        
        # Add storage data
        storage_state = resource_state.get("storage", {})
        self.resource_data["storage"].append({
            "timestamp": timestamp,
            "total": storage_state.get("total", 0),
            "available": storage_state.get("available", 0),
            "utilized": storage_state.get("utilized", 0),
            "utilization_percent": self._calculate_utilization_percent(
                storage_state.get("utilized", 0),
                storage_state.get("total", 0)
            )
        })
        
        # Add network data
        network_state = resource_state.get("network", {})
        bandwidth_state = network_state.get("bandwidth", {})
        
        self.resource_data["network"]["bandwidth"].append({
            "timestamp": timestamp,
            "total": bandwidth_state.get("total", 0),
            "available": bandwidth_state.get("available", 0),
            "utilized": bandwidth_state.get("utilized", 0),
            "utilization_percent": self._calculate_utilization_percent(
                bandwidth_state.get("utilized", 0),
                bandwidth_state.get("total", 0)
            )
        })
        
        self.resource_data["network"]["latency"].append({
            "timestamp": timestamp,
            "value": network_state.get("latency", 0)
        })
        
        self.resource_data["network"]["packet_loss"].append({
            "timestamp": timestamp,
            "value": network_state.get("packet_loss", 0)
        })
        
        # Trim data to analysis window
        self._trim_data()
    
    def _calculate_utilization_percent(self, utilized: float, total: float) -> float:
        """
        Calculate utilization percentage.
        
        Args:
            utilized: Utilized resources
            total: Total resources
            
        Returns:
            Utilization percentage
        """
        if total <= 0:
            return 0
        
        return (utilized / total) * 100
    
    def _trim_data(self):
        """
        Trim data to analysis window.
        """
        cutoff_time = time.time() - self.analysis_window
        
        # Trim CPU data
        self.resource_data["cpu"] = [
            data for data in self.resource_data["cpu"]
            if data["timestamp"] >= cutoff_time
        ]
        
        # Trim memory data
        self.resource_data["memory"] = [
            data for data in self.resource_data["memory"]
            if data["timestamp"] >= cutoff_time
        ]
        
        # Trim storage data
        self.resource_data["storage"] = [
            data for data in self.resource_data["storage"]
            if data["timestamp"] >= cutoff_time
        ]
        
        # Trim network data
        self.resource_data["network"]["bandwidth"] = [
            data for data in self.resource_data["network"]["bandwidth"]
            if data["timestamp"] >= cutoff_time
        ]
        
        self.resource_data["network"]["latency"] = [
            data for data in self.resource_data["network"]["latency"]
            if data["timestamp"] >= cutoff_time
        ]
        
        self.resource_data["network"]["packet_loss"] = [
            data for data in self.resource_data["network"]["packet_loss"]
            if data["timestamp"] >= cutoff_time
        ]
    
    def analyze_resource_utilization(self) -> Dict[str, Any]:
        """
        Analyze resource utilization data.
        
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Analyzing resource utilization")
        
        # Initialize analysis results
        self.analysis_results = {
            "timestamp": time.time(),
            "analysis_window": self.analysis_window,
            "data_points": {
                "cpu": len(self.resource_data["cpu"]),
                "memory": len(self.resource_data["memory"]),
                "storage": len(self.resource_data["storage"]),
                "network_bandwidth": len(self.resource_data["network"]["bandwidth"]),
                "network_latency": len(self.resource_data["network"]["latency"]),
                "network_packet_loss": len(self.resource_data["network"]["packet_loss"])
            },
            "cpu": self._analyze_cpu_utilization(),
            "memory": self._analyze_memory_utilization(),
            "storage": self._analyze_storage_utilization(),
            "network": self._analyze_network_utilization(),
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Identify bottlenecks
        self._identify_bottlenecks()
        
        # Generate recommendations
        self._generate_recommendations()
        
        logger.info("Resource utilization analysis completed")
        
        return self.analysis_results
    
    def _analyze_cpu_utilization(self) -> Dict[str, Any]:
        """
        Analyze CPU utilization.
        
        Returns:
            Dictionary containing CPU utilization analysis
        """
        if not self.resource_data["cpu"]:
            return {
                "status": "insufficient_data",
                "message": "No CPU data available for analysis"
            }
        
        # Extract utilization percentages
        utilization_percentages = [
            data["utilization_percent"]
            for data in self.resource_data["cpu"]
        ]
        
        # Calculate statistics
        avg_utilization = statistics.mean(utilization_percentages) if utilization_percentages else 0
        max_utilization = max(utilization_percentages) if utilization_percentages else 0
        min_utilization = min(utilization_percentages) if utilization_percentages else 0
        
        try:
            std_dev = statistics.stdev(utilization_percentages) if len(utilization_percentages) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine utilization pattern
        pattern = self._determine_utilization_pattern(utilization_percentages)
        
        # Determine utilization level
        level = self._determine_utilization_level(avg_utilization)
        
        return {
            "status": "analyzed",
            "average_utilization": avg_utilization,
            "max_utilization": max_utilization,
            "min_utilization": min_utilization,
            "std_dev": std_dev,
            "pattern": pattern,
            "level": level
        }
    
    def _analyze_memory_utilization(self) -> Dict[str, Any]:
        """
        Analyze memory utilization.
        
        Returns:
            Dictionary containing memory utilization analysis
        """
        if not self.resource_data["memory"]:
            return {
                "status": "insufficient_data",
                "message": "No memory data available for analysis"
            }
        
        # Extract utilization percentages
        utilization_percentages = [
            data["utilization_percent"]
            for data in self.resource_data["memory"]
        ]
        
        # Calculate statistics
        avg_utilization = statistics.mean(utilization_percentages) if utilization_percentages else 0
        max_utilization = max(utilization_percentages) if utilization_percentages else 0
        min_utilization = min(utilization_percentages) if utilization_percentages else 0
        
        try:
            std_dev = statistics.stdev(utilization_percentages) if len(utilization_percentages) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine utilization pattern
        pattern = self._determine_utilization_pattern(utilization_percentages)
        
        # Determine utilization level
        level = self._determine_utilization_level(avg_utilization)
        
        # Check for memory leaks
        leak_detected = self._check_for_memory_leak(utilization_percentages)
        
        return {
            "status": "analyzed",
            "average_utilization": avg_utilization,
            "max_utilization": max_utilization,
            "min_utilization": min_utilization,
            "std_dev": std_dev,
            "pattern": pattern,
            "level": level,
            "leak_detected": leak_detected
        }
    
    def _analyze_storage_utilization(self) -> Dict[str, Any]:
        """
        Analyze storage utilization.
        
        Returns:
            Dictionary containing storage utilization analysis
        """
        if not self.resource_data["storage"]:
            return {
                "status": "insufficient_data",
                "message": "No storage data available for analysis"
            }
        
        # Extract utilization percentages
        utilization_percentages = [
            data["utilization_percent"]
            for data in self.resource_data["storage"]
        ]
        
        # Calculate statistics
        avg_utilization = statistics.mean(utilization_percentages) if utilization_percentages else 0
        max_utilization = max(utilization_percentages) if utilization_percentages else 0
        min_utilization = min(utilization_percentages) if utilization_percentages else 0
        
        try:
            std_dev = statistics.stdev(utilization_percentages) if len(utilization_percentages) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine utilization pattern
        pattern = self._determine_utilization_pattern(utilization_percentages)
        
        # Determine utilization level
        level = self._determine_utilization_level(avg_utilization)
        
        # Calculate growth rate
        growth_rate = self._calculate_growth_rate(utilization_percentages)
        
        return {
            "status": "analyzed",
            "average_utilization": avg_utilization,
            "max_utilization": max_utilization,
            "min_utilization": min_utilization,
            "std_dev": std_dev,
            "pattern": pattern,
            "level": level,
            "growth_rate": growth_rate
        }
    
    def _analyze_network_utilization(self) -> Dict[str, Any]:
        """
        Analyze network utilization.
        
        Returns:
            Dictionary containing network utilization analysis
        """
        # Analyze bandwidth
        bandwidth_analysis = self._analyze_network_bandwidth()
        
        # Analyze latency
        latency_analysis = self._analyze_network_latency()
        
        # Analyze packet loss
        packet_loss_analysis = self._analyze_network_packet_loss()
        
        return {
            "bandwidth": bandwidth_analysis,
            "latency": latency_analysis,
            "packet_loss": packet_loss_analysis
        }
    
    def _analyze_network_bandwidth(self) -> Dict[str, Any]:
        """
        Analyze network bandwidth utilization.
        
        Returns:
            Dictionary containing network bandwidth utilization analysis
        """
        if not self.resource_data["network"]["bandwidth"]:
            return {
                "status": "insufficient_data",
                "message": "No network bandwidth data available for analysis"
            }
        
        # Extract utilization percentages
        utilization_percentages = [
            data["utilization_percent"]
            for data in self.resource_data["network"]["bandwidth"]
        ]
        
        # Calculate statistics
        avg_utilization = statistics.mean(utilization_percentages) if utilization_percentages else 0
        max_utilization = max(utilization_percentages) if utilization_percentages else 0
        min_utilization = min(utilization_percentages) if utilization_percentages else 0
        
        try:
            std_dev = statistics.stdev(utilization_percentages) if len(utilization_percentages) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine utilization pattern
        pattern = self._determine_utilization_pattern(utilization_percentages)
        
        # Determine utilization level
        level = self._determine_utilization_level(avg_utilization)
        
        return {
            "status": "analyzed",
            "average_utilization": avg_utilization,
            "max_utilization": max_utilization,
            "min_utilization": min_utilization,
            "std_dev": std_dev,
            "pattern": pattern,
            "level": level
        }
    
    def _analyze_network_latency(self) -> Dict[str, Any]:
        """
        Analyze network latency.
        
        Returns:
            Dictionary containing network latency analysis
        """
        if not self.resource_data["network"]["latency"]:
            return {
                "status": "insufficient_data",
                "message": "No network latency data available for analysis"
            }
        
        # Extract latency values
        latency_values = [
            data["value"]
            for data in self.resource_data["network"]["latency"]
        ]
        
        # Calculate statistics
        avg_latency = statistics.mean(latency_values) if latency_values else 0
        max_latency = max(latency_values) if latency_values else 0
        min_latency = min(latency_values) if latency_values else 0
        
        try:
            std_dev = statistics.stdev(latency_values) if len(latency_values) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine latency level
        level = self._determine_latency_level(avg_latency)
        
        return {
            "status": "analyzed",
            "average_latency": avg_latency,
            "max_latency": max_latency,
            "min_latency": min_latency,
            "std_dev": std_dev,
            "level": level
        }
    
    def _analyze_network_packet_loss(self) -> Dict[str, Any]:
        """
        Analyze network packet loss.
        
        Returns:
            Dictionary containing network packet loss analysis
        """
        if not self.resource_data["network"]["packet_loss"]:
            return {
                "status": "insufficient_data",
                "message": "No network packet loss data available for analysis"
            }
        
        # Extract packet loss values
        packet_loss_values = [
            data["value"]
            for data in self.resource_data["network"]["packet_loss"]
        ]
        
        # Calculate statistics
        avg_packet_loss = statistics.mean(packet_loss_values) if packet_loss_values else 0
        max_packet_loss = max(packet_loss_values) if packet_loss_values else 0
        min_packet_loss = min(packet_loss_values) if packet_loss_values else 0
        
        try:
            std_dev = statistics.stdev(packet_loss_values) if len(packet_loss_values) > 1 else 0
        except statistics.StatisticsError:
            std_dev = 0
        
        # Determine packet loss level
        level = self._determine_packet_loss_level(avg_packet_loss)
        
        return {
            "status": "analyzed",
            "average_packet_loss": avg_packet_loss,
            "max_packet_loss": max_packet_loss,
            "min_packet_loss": min_packet_loss,
            "std_dev": std_dev,
            "level": level
        }
    
    def _determine_utilization_pattern(self, values: List[float]) -> str:
        """
        Determine utilization pattern.
        
        Args:
            values: List of utilization values
            
        Returns:
            Pattern description
        """
        if not values or len(values) < 3:
            return "insufficient_data"
        
        # Check for steady pattern
        try:
            std_dev = statistics.stdev(values)
            mean = statistics.mean(values)
            
            if std_dev < 5:
                return "steady"
            
            # Check for increasing pattern
            first_third = values[:len(values)//3]
            last_third = values[-len(values)//3:]
            
            first_avg = statistics.mean(first_third)
            last_avg = statistics.mean(last_third)
            
            if last_avg > first_avg * 1.2:
                return "increasing"
            
            if first_avg > last_avg * 1.2:
                return "decreasing"
            
            # Check for spiky pattern
            if std_dev > 15:
                return "spiky"
            
            return "variable"
            
        except statistics.StatisticsError:
            return "unknown"
    
    def _determine_utilization_level(self, avg_utilization: float) -> str:
        """
        Determine utilization level.
        
        Args:
            avg_utilization: Average utilization percentage
            
        Returns:
            Utilization level
        """
        if avg_utilization < 20:
            return "very_low"
        elif avg_utilization < 40:
            return "low"
        elif avg_utilization < 70:
            return "moderate"
        elif avg_utilization < 85:
            return "high"
        else:
            return "very_high"
    
    def _determine_latency_level(self, avg_latency: float) -> str:
        """
        Determine latency level.
        
        Args:
            avg_latency: Average latency in milliseconds
            
        Returns:
            Latency level
        """
        if avg_latency < 10:
            return "very_low"
        elif avg_latency < 50:
            return "low"
        elif avg_latency < 100:
            return "moderate"
        elif avg_latency < 200:
            return "high"
        else:
            return "very_high"
    
    def _determine_packet_loss_level(self, avg_packet_loss: float) -> str:
        """
        Determine packet loss level.
        
        Args:
            avg_packet_loss: Average packet loss percentage
            
        Returns:
            Packet loss level
        """
        if avg_packet_loss < 0.1:
            return "very_low"
        elif avg_packet_loss < 1:
            return "low"
        elif avg_packet_loss < 2:
            return "moderate"
        elif avg_packet_loss < 5:
            return "high"
        else:
            return "very_high"
    
    def _check_for_memory_leak(self, values: List[float]) -> bool:
        """
        Check for memory leak.
        
        Args:
            values: List of memory utilization values
            
        Returns:
            True if memory leak is detected, False otherwise
        """
        if not values or len(values) < 10:
            return False
        
        # Check for consistently increasing memory usage
        is_increasing = True
        for i in range(1, len(values)):
            if values[i] < values[i-1]:
                is_increasing = False
                break
        
        if is_increasing:
            return True
        
        # Check for overall trend
        first_quarter = values[:len(values)//4]
        last_quarter = values[-len(values)//4:]
        
        first_avg = statistics.mean(first_quarter)
        last_avg = statistics.mean(last_quarter)
        
        return last_avg > first_avg * 1.5
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """
        Calculate growth rate.
        
        Args:
            values: List of values
            
        Returns:
            Growth rate in percentage per hour
        """
        if not values or len(values) < 2:
            return 0
        
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            return 0
        
        # Calculate time difference in hours
        time_diff = (self.resource_data["storage"][-1]["timestamp"] - self.resource_data["storage"][0]["timestamp"]) / 3600
        
        if time_diff == 0:
            return 0
        
        # Calculate growth rate
        growth_rate = ((last_value - first_value) / first_value) * 100 / time_diff
        
        return growth_rate
    
    def _identify_bottlenecks(self):
        """
        Identify resource bottlenecks.
        """
        bottlenecks = []
        
        # Check CPU bottleneck
        cpu_analysis = self.analysis_results.get("cpu", {})
        if cpu_analysis.get("level") in ["high", "very_high"]:
            bottlenecks.append({
                "resource": "cpu",
                "level": cpu_analysis.get("level"),
                "average_utilization": cpu_analysis.get("average_utilization"),
                "max_utilization": cpu_analysis.get("max_utilization"),
                "impact": "high" if cpu_analysis.get("level") == "very_high" else "medium"
            })
        
        # Check memory bottleneck
        memory_analysis = self.analysis_results.get("memory", {})
        if memory_analysis.get("level") in ["high", "very_high"] or memory_analysis.get("leak_detected", False):
            bottlenecks.append({
                "resource": "memory",
                "level": memory_analysis.get("level"),
                "average_utilization": memory_analysis.get("average_utilization"),
                "max_utilization": memory_analysis.get("max_utilization"),
                "leak_detected": memory_analysis.get("leak_detected", False),
                "impact": "high" if memory_analysis.get("level") == "very_high" or memory_analysis.get("leak_detected", False) else "medium"
            })
        
        # Check storage bottleneck
        storage_analysis = self.analysis_results.get("storage", {})
        if storage_analysis.get("level") in ["high", "very_high"] or storage_analysis.get("growth_rate", 0) > 10:
            bottlenecks.append({
                "resource": "storage",
                "level": storage_analysis.get("level"),
                "average_utilization": storage_analysis.get("average_utilization"),
                "max_utilization": storage_analysis.get("max_utilization"),
                "growth_rate": storage_analysis.get("growth_rate"),
                "impact": "high" if storage_analysis.get("level") == "very_high" or storage_analysis.get("growth_rate", 0) > 20 else "medium"
            })
        
        # Check network bottlenecks
        network_analysis = self.analysis_results.get("network", {})
        
        # Check bandwidth bottleneck
        bandwidth_analysis = network_analysis.get("bandwidth", {})
        if bandwidth_analysis.get("level") in ["high", "very_high"]:
            bottlenecks.append({
                "resource": "network_bandwidth",
                "level": bandwidth_analysis.get("level"),
                "average_utilization": bandwidth_analysis.get("average_utilization"),
                "max_utilization": bandwidth_analysis.get("max_utilization"),
                "impact": "high" if bandwidth_analysis.get("level") == "very_high" else "medium"
            })
        
        # Check latency bottleneck
        latency_analysis = network_analysis.get("latency", {})
        if latency_analysis.get("level") in ["high", "very_high"]:
            bottlenecks.append({
                "resource": "network_latency",
                "level": latency_analysis.get("level"),
                "average_latency": latency_analysis.get("average_latency"),
                "max_latency": latency_analysis.get("max_latency"),
                "impact": "high" if latency_analysis.get("level") == "very_high" else "medium"
            })
        
        # Check packet loss bottleneck
        packet_loss_analysis = network_analysis.get("packet_loss", {})
        if packet_loss_analysis.get("level") in ["high", "very_high"]:
            bottlenecks.append({
                "resource": "network_packet_loss",
                "level": packet_loss_analysis.get("level"),
                "average_packet_loss": packet_loss_analysis.get("average_packet_loss"),
                "max_packet_loss": packet_loss_analysis.get("max_packet_loss"),
                "impact": "high" if packet_loss_analysis.get("level") == "very_high" else "medium"
            })
        
        # Sort bottlenecks by impact
        bottlenecks.sort(key=lambda x: 0 if x["impact"] == "high" else 1)
        
        self.analysis_results["bottlenecks"] = bottlenecks
    
    def _generate_recommendations(self):
        """
        Generate optimization recommendations.
        """
        recommendations = []
        
        # Process bottlenecks
        for bottleneck in self.analysis_results.get("bottlenecks", []):
            resource = bottleneck.get("resource")
            
            if resource == "cpu":
                recommendations.extend(self._generate_cpu_recommendations(bottleneck))
            
            elif resource == "memory":
                recommendations.extend(self._generate_memory_recommendations(bottleneck))
            
            elif resource == "storage":
                recommendations.extend(self._generate_storage_recommendations(bottleneck))
            
            elif resource == "network_bandwidth":
                recommendations.extend(self._generate_bandwidth_recommendations(bottleneck))
            
            elif resource == "network_latency":
                recommendations.extend(self._generate_latency_recommendations(bottleneck))
            
            elif resource == "network_packet_loss":
                recommendations.extend(self._generate_packet_loss_recommendations(bottleneck))
        
        # Add general recommendations
        if not self.analysis_results.get("bottlenecks"):
            recommendations.append({
                "type": "general",
                "resource": "all",
                "action": "monitor",
                "description": "Continue monitoring resource utilization for potential issues",
                "priority": "low"
            })
        
        # Check for underutilized resources
        cpu_analysis = self.analysis_results.get("cpu", {})
        if cpu_analysis.get("level") in ["very_low", "low"]:
            recommendations.append({
                "type": "optimization",
                "resource": "cpu",
                "action": "consolidate",
                "description": "Consider consolidating workloads to reduce CPU resources and costs",
                "priority": "medium"
            })
        
        memory_analysis = self.analysis_results.get("memory", {})
        if memory_analysis.get("level") in ["very_low", "low"]:
            recommendations.append({
                "type": "optimization",
                "resource": "memory",
                "action": "reduce",
                "description": "Consider reducing memory allocation to optimize costs",
                "priority": "medium"
            })
        
        # Sort recommendations by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        self.analysis_results["recommendations"] = recommendations
    
    def _generate_cpu_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate CPU optimization recommendations.
        
        Args:
            bottleneck: CPU bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        
        if level == "very_high":
            recommendations.append({
                "type": "scaling",
                "resource": "cpu",
                "action": "increase",
                "description": "Increase CPU allocation to address severe CPU bottleneck",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "cpu",
                "action": "profile",
                "description": "Profile application to identify CPU-intensive operations",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "scaling",
                "resource": "cpu",
                "action": "increase",
                "description": "Consider increasing CPU allocation to address CPU bottleneck",
                "priority": "medium"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "cpu",
                "action": "optimize",
                "description": "Optimize CPU-intensive operations in the application",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_memory_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate memory optimization recommendations.
        
        Args:
            bottleneck: Memory bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        leak_detected = bottleneck.get("leak_detected", False)
        
        if leak_detected:
            recommendations.append({
                "type": "issue",
                "resource": "memory",
                "action": "fix_leak",
                "description": "Investigate and fix potential memory leak in the application",
                "priority": "high"
            })
        
        if level == "very_high":
            recommendations.append({
                "type": "scaling",
                "resource": "memory",
                "action": "increase",
                "description": "Increase memory allocation to address severe memory bottleneck",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "memory",
                "action": "profile",
                "description": "Profile application to identify memory-intensive operations",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "scaling",
                "resource": "memory",
                "action": "increase",
                "description": "Consider increasing memory allocation to address memory bottleneck",
                "priority": "medium"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "memory",
                "action": "optimize",
                "description": "Optimize memory usage in the application",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_storage_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate storage optimization recommendations.
        
        Args:
            bottleneck: Storage bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        growth_rate = bottleneck.get("growth_rate", 0)
        
        if growth_rate > 20:
            recommendations.append({
                "type": "issue",
                "resource": "storage",
                "action": "investigate_growth",
                "description": f"Investigate rapid storage growth rate of {growth_rate:.1f}% per hour",
                "priority": "high"
            })
        
        if level == "very_high":
            recommendations.append({
                "type": "scaling",
                "resource": "storage",
                "action": "increase",
                "description": "Increase storage allocation to address severe storage bottleneck",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "storage",
                "action": "cleanup",
                "description": "Clean up unnecessary data to free up storage space",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "scaling",
                "resource": "storage",
                "action": "increase",
                "description": "Consider increasing storage allocation to address storage bottleneck",
                "priority": "medium"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "storage",
                "action": "optimize",
                "description": "Optimize storage usage by compressing or archiving data",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_bandwidth_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate network bandwidth optimization recommendations.
        
        Args:
            bottleneck: Network bandwidth bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        
        if level == "very_high":
            recommendations.append({
                "type": "scaling",
                "resource": "network_bandwidth",
                "action": "increase",
                "description": "Increase network bandwidth to address severe bandwidth bottleneck",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "network_bandwidth",
                "action": "optimize",
                "description": "Optimize network usage by reducing data transfer or implementing compression",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "scaling",
                "resource": "network_bandwidth",
                "action": "increase",
                "description": "Consider increasing network bandwidth to address bandwidth bottleneck",
                "priority": "medium"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "network_bandwidth",
                "action": "optimize",
                "description": "Optimize network usage by batching requests or implementing caching",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_latency_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate network latency optimization recommendations.
        
        Args:
            bottleneck: Network latency bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        
        if level == "very_high":
            recommendations.append({
                "type": "issue",
                "resource": "network_latency",
                "action": "investigate",
                "description": "Investigate causes of high network latency",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "network_latency",
                "action": "optimize",
                "description": "Optimize application to handle high latency or consider geographic redistribution",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "optimization",
                "resource": "network_latency",
                "action": "optimize",
                "description": "Implement caching or asynchronous processing to mitigate latency impact",
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_packet_loss_recommendations(self, bottleneck: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate network packet loss optimization recommendations.
        
        Args:
            bottleneck: Network packet loss bottleneck information
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        level = bottleneck.get("level")
        impact = bottleneck.get("impact")
        
        if level == "very_high":
            recommendations.append({
                "type": "issue",
                "resource": "network_packet_loss",
                "action": "investigate",
                "description": "Investigate causes of high packet loss",
                "priority": "high"
            })
            
            recommendations.append({
                "type": "optimization",
                "resource": "network_packet_loss",
                "action": "optimize",
                "description": "Implement reliable transmission protocols or retry mechanisms",
                "priority": "high"
            })
        
        elif level == "high":
            recommendations.append({
                "type": "optimization",
                "resource": "network_packet_loss",
                "action": "optimize",
                "description": "Implement error correction or packet loss recovery mechanisms",
                "priority": "medium"
            })
        
        return recommendations
    
    def save_analysis_results(self, file_name: Optional[str] = None) -> str:
        """
        Save analysis results to file.
        
        Args:
            file_name: Optional file name
            
        Returns:
            Path to saved file
        """
        if not file_name:
            file_name = f"resource_analysis_{int(time.time())}.json"
        
        file_path = os.path.join(self.data_dir, file_name)
        
        with open(file_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        logger.info(f"Saved analysis results to {file_path}")
        
        return file_path
    
    def load_analysis_results(self, file_path: str) -> Dict[str, Any]:
        """
        Load analysis results from file.
        
        Args:
            file_path: Path to analysis results file
            
        Returns:
            Analysis results
        """
        with open(file_path, 'r') as f:
            self.analysis_results = json.load(f)
        
        logger.info(f"Loaded analysis results from {file_path}")
        
        return self.analysis_results
    
    def clear_resource_data(self):
        """
        Clear resource data.
        """
        self.resource_data = {
            "cpu": [],
            "memory": [],
            "storage": [],
            "network": {
                "bandwidth": [],
                "latency": [],
                "packet_loss": []
            }
        }
        
        logger.info("Cleared resource data")
