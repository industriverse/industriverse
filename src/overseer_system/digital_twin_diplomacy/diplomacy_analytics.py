"""
Diplomacy Analytics Module for the Digital Twin Diplomacy Phase of the Overseer System.

This module provides advanced analytics capabilities for analyzing diplomacy operations,
including negotiation patterns, shadow performance, and conflict resolution metrics.

Author: Manus AI
Date: May 25, 2025
"""

import json
import uuid
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService

# Import diplomacy models
from .diplomacy_models import (
    NegotiationSession, NegotiationProposal, NegotiationAgreement,
    ResourceSpecification, ResourceType, NegotiationStatus, ProposalStatus,
    ResourceConflict, ConflictResolution, ConflictType, ConflictSeverity,
    ResolutionStrategy, ShadowCapsule, ShadowType, ShadowStatus
)

class NegotiationAnalytics:
    """Analytics for negotiation operations."""
    
    def __init__(
        self,
        data_access: DataAccessService,
        mcp_bridge: Optional[MCPProtocolBridge] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the negotiation analytics.
        
        Args:
            data_access: Data access service
            mcp_bridge: MCP protocol bridge (optional)
            logger: Logger instance
        """
        self.data_access = data_access
        self.mcp_bridge = mcp_bridge
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_negotiation_trends(
        self,
        time_period: str = "last_30_days",
        agent_ids: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None,
        include_visualizations: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze negotiation trends over time.
        
        Args:
            time_period: Time period for analysis
            agent_ids: List of agent IDs to filter
            resource_types: List of resource types to filter
            include_visualizations: Whether to include visualization data
            
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
        
        # Convert to DataFrame for analysis
        sessions_df = pd.DataFrame(sessions_data)
        
        # Convert timestamps to datetime
        sessions_df["created_at"] = pd.to_datetime(sessions_df["created_at"])
        sessions_df["completed_at"] = pd.to_datetime(sessions_df["completed_at"])
        
        # Calculate duration
        sessions_df["duration_minutes"] = (sessions_df["completed_at"] - sessions_df["created_at"]).dt.total_seconds() / 60
        
        # Group by day
        sessions_df["date"] = sessions_df["created_at"].dt.date
        daily_sessions = sessions_df.groupby("date").size().reset_index(name="session_count")
        
        # Calculate success rate
        daily_success = sessions_df[sessions_df["agreement_id"].notnull()].groupby("date").size().reset_index(name="success_count")
        daily_metrics = pd.merge(daily_sessions, daily_success, on="date", how="left")
        daily_metrics["success_count"] = daily_metrics["success_count"].fillna(0)
        daily_metrics["success_rate"] = daily_metrics["success_count"] / daily_metrics["session_count"] * 100
        
        # Calculate average duration
        daily_duration = sessions_df.groupby("date")["duration_minutes"].mean().reset_index(name="avg_duration")
        daily_metrics = pd.merge(daily_metrics, daily_duration, on="date", how="left")
        
        # Prepare results
        results = {
            "total_sessions": len(sessions_df),
            "successful_sessions": sessions_df["agreement_id"].notnull().sum(),
            "overall_success_rate": (sessions_df["agreement_id"].notnull().sum() / len(sessions_df)) * 100,
            "avg_duration_minutes": sessions_df["duration_minutes"].mean(),
            "daily_metrics": daily_metrics.to_dict(orient="records"),
            "trend_analysis": {
                "success_rate_trend": self._calculate_trend(daily_metrics["success_rate"]),
                "session_count_trend": self._calculate_trend(daily_metrics["session_count"]),
                "duration_trend": self._calculate_trend(daily_metrics["avg_duration"])
            }
        }
        
        # Add resource type analysis if requested
        if resource_types or resource_types is None:
            results["resource_analysis"] = self._analyze_resources(sessions_df, resource_types)
        
        # Add visualizations if requested
        if include_visualizations:
            results["visualizations"] = self._generate_negotiation_visualizations(daily_metrics)
        
        # Update MCP context if available
        if self.mcp_bridge:
            self.mcp_bridge.update_context(
                context_type="negotiation_analytics",
                context_id=f"trend_analysis_{datetime.now().isoformat()}",
                context_data={
                    "total_sessions": results["total_sessions"],
                    "successful_sessions": results["successful_sessions"],
                    "overall_success_rate": results["overall_success_rate"],
                    "avg_duration_minutes": results["avg_duration_minutes"],
                    "trend_analysis": results["trend_analysis"],
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return results
    
    def _calculate_trend(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate trend from a time series.
        
        Args:
            series: Time series data
            
        Returns:
            Dict[str, Any]: Trend analysis
        """
        if series.empty or len(series) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate linear regression
        x = np.arange(len(series))
        y = series.values
        
        # Handle NaN values
        mask = ~np.isnan(y)
        if not np.any(mask):
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate slope and correlation
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine direction
        if slope > 0:
            direction = "increasing"
        elif slope < 0:
            direction = "decreasing"
        else:
            direction = "neutral"
        
        # Determine strength
        strength = abs(correlation)
        
        return {
            "direction": direction,
            "slope": slope,
            "strength": strength,
            "correlation": correlation
        }
    
    def _analyze_resources(
        self,
        sessions_df: pd.DataFrame,
        resource_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze resource usage in negotiations.
        
        Args:
            sessions_df: DataFrame of negotiation sessions
            resource_types: List of resource types to filter
            
        Returns:
            Dict[str, Any]: Resource analysis
        """
        # Get all proposals
        proposal_ids = []
        for proposals in sessions_df["proposals"]:
            if proposals:
                proposal_ids.extend(proposals)
        
        if not proposal_ids:
            return {"error": "No proposals found"}
        
        # Query proposals
        proposals_data = []
        for proposal_id in proposal_ids:
            proposal_data = self.data_access.read(
                collection="negotiation_proposals",
                document_id=proposal_id
            )
            
            if proposal_data:
                proposals_data.append(proposal_data)
        
        if not proposals_data:
            return {"error": "No proposal data found"}
        
        # Extract resources
        resources_data = []
        
        for proposal in proposals_data:
            for resource in proposal.get("resources", []):
                if resource_types and resource.get("resource_type") not in resource_types:
                    continue
                
                resources_data.append({
                    "proposal_id": proposal.get("proposal_id"),
                    "session_id": proposal.get("session_id"),
                    "proposer_id": proposal.get("proposer_id"),
                    "resource_type": resource.get("resource_type"),
                    "quantity": resource.get("quantity"),
                    "priority": resource.get("priority"),
                    "status": proposal.get("status")
                })
        
        if not resources_data:
            return {"error": "No resource data found"}
        
        # Convert to DataFrame
        resources_df = pd.DataFrame(resources_data)
        
        # Analyze by resource type
        resource_type_analysis = resources_df.groupby("resource_type").agg({
            "proposal_id": "count",
            "quantity": ["mean", "min", "max"],
            "priority": ["mean", "min", "max"]
        }).reset_index()
        
        # Flatten column names
        resource_type_analysis.columns = ["_".join(col).strip("_") for col in resource_type_analysis.columns.values]
        
        # Calculate success rate by resource type
        success_by_type = resources_df[resources_df["status"] == "accepted"].groupby("resource_type").size()
        total_by_type = resources_df.groupby("resource_type").size()
        success_rate_by_type = (success_by_type / total_by_type * 100).reset_index(name="success_rate")
        
        resource_type_analysis = pd.merge(
            resource_type_analysis,
            success_rate_by_type,
            on="resource_type",
            how="left"
        )
        
        return {
            "resource_type_analysis": resource_type_analysis.to_dict(orient="records"),
            "total_resources": len(resources_df),
            "unique_resource_types": resources_df["resource_type"].nunique(),
            "most_common_resource": resources_df["resource_type"].value_counts().index[0],
            "highest_priority_resource": resources_df.loc[resources_df["priority"].idxmax()]["resource_type"]
        }
    
    def _generate_negotiation_visualizations(self, daily_metrics: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate visualizations for negotiation trends.
        
        Args:
            daily_metrics: Daily metrics DataFrame
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        # Convert date to string for JSON serialization
        daily_metrics["date_str"] = daily_metrics["date"].astype(str)
        
        return {
            "time_series": {
                "dates": daily_metrics["date_str"].tolist(),
                "session_counts": daily_metrics["session_count"].tolist(),
                "success_rates": daily_metrics["success_rate"].tolist(),
                "avg_durations": daily_metrics["avg_duration"].tolist()
            }
        }
    
    def analyze_strategy_effectiveness(
        self,
        time_period: str = "last_30_days",
        strategies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze effectiveness of negotiation strategies.
        
        Args:
            time_period: Time period for analysis
            strategies: List of strategies to filter
            
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
        
        # Query proposals
        proposals_data = self.data_access.query(
            collection="negotiation_proposals",
            query=query
        )
        
        if not proposals_data:
            return {"error": "No proposals found for the specified criteria"}
        
        # Filter by strategy if specified
        if strategies:
            proposals_data = [
                p for p in proposals_data
                if p.get("metadata", {}).get("strategy") in strategies
            ]
            
            if not proposals_data:
                return {"error": f"No proposals found with strategies: {strategies}"}
        
        # Convert to DataFrame
        proposals_df = pd.DataFrame(proposals_data)
        
        # Extract strategy from metadata
        proposals_df["strategy"] = proposals_df["metadata"].apply(
            lambda x: x.get("strategy") if isinstance(x, dict) else None
        )
        
        # Filter out proposals without strategy
        proposals_df = proposals_df[proposals_df["strategy"].notnull()]
        
        if proposals_df.empty:
            return {"error": "No proposals with strategy information found"}
        
        # Calculate response counts
        strategy_stats = []
        
        for strategy, group in proposals_df.groupby("strategy"):
            total = len(group)
            accepted = 0
            rejected = 0
            countered = 0
            
            for _, row in group.iterrows():
                responses = row.get("responses", {})
                
                if not responses:
                    continue
                
                for response in responses.values():
                    if response == "accept":
                        accepted += 1
                    elif response == "reject":
                        rejected += 1
                    elif response == "counter":
                        countered += 1
            
            # Calculate rates
            total_responses = accepted + rejected + countered
            
            if total_responses > 0:
                acceptance_rate = (accepted / total_responses) * 100
                rejection_rate = (rejected / total_responses) * 100
                counter_rate = (countered / total_responses) * 100
            else:
                acceptance_rate = 0
                rejection_rate = 0
                counter_rate = 0
            
            strategy_stats.append({
                "strategy": strategy,
                "total_proposals": total,
                "accepted": accepted,
                "rejected": rejected,
                "countered": countered,
                "acceptance_rate": acceptance_rate,
                "rejection_rate": rejection_rate,
                "counter_rate": counter_rate
            })
        
        # Sort by acceptance rate
        strategy_stats.sort(key=lambda x: x["acceptance_rate"], reverse=True)
        
        # Calculate overall stats
        total_proposals = len(proposals_df)
        total_accepted = sum(s["accepted"] for s in strategy_stats)
        total_rejected = sum(s["rejected"] for s in strategy_stats)
        total_countered = sum(s["countered"] for s in strategy_stats)
        total_responses = total_accepted + total_rejected + total_countered
        
        if total_responses > 0:
            overall_acceptance_rate = (total_accepted / total_responses) * 100
            overall_rejection_rate = (total_rejected / total_responses) * 100
            overall_counter_rate = (total_countered / total_responses) * 100
        else:
            overall_acceptance_rate = 0
            overall_rejection_rate = 0
            overall_counter_rate = 0
        
        return {
            "strategy_stats": strategy_stats,
            "overall_stats": {
                "total_proposals": total_proposals,
                "total_accepted": total_accepted,
                "total_rejected": total_rejected,
                "total_countered": total_countered,
                "overall_acceptance_rate": overall_acceptance_rate,
                "overall_rejection_rate": overall_rejection_rate,
                "overall_counter_rate": overall_counter_rate
            },
            "most_effective_strategy": strategy_stats[0]["strategy"] if strategy_stats else None,
            "least_effective_strategy": strategy_stats[-1]["strategy"] if strategy_stats else None
        }

class ShadowAnalytics:
    """Analytics for shadow capsule operations."""
    
    def __init__(
        self,
        data_access: DataAccessService,
        mcp_bridge: Optional[MCPProtocolBridge] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the shadow analytics.
        
        Args:
            data_access: Data access service
            mcp_bridge: MCP protocol bridge (optional)
            logger: Logger instance
        """
        self.data_access = data_access
        self.mcp_bridge = mcp_bridge
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_shadow_divergence(
        self,
        time_period: str = "last_30_days",
        shadow_types: Optional[List[str]] = None,
        original_ids: Optional[List[str]] = None,
        include_visualizations: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze shadow divergence patterns.
        
        Args:
            time_period: Time period for analysis
            shadow_types: List of shadow types to filter
            original_ids: List of original capsule IDs to filter
            include_visualizations: Whether to include visualization data
            
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
        
        # Convert to DataFrame
        shadows_df = pd.DataFrame(shadows_data)
        
        # Extract divergence metrics
        shadows_df["divergence_percentage"] = shadows_df["divergence_metrics"].apply(
            lambda x: x.get("state_change_percentage", 0) if isinstance(x, dict) else 0
        )
        
        # Convert timestamps to datetime
        shadows_df["created_at"] = pd.to_datetime(shadows_df["created_at"])
        shadows_df["last_sync"] = pd.to_datetime(shadows_df["last_sync"])
        
        # Calculate time since creation
        shadows_df["age_hours"] = (datetime.now() - shadows_df["created_at"]).dt.total_seconds() / 3600
        
        # Group by shadow type
        shadow_type_stats = shadows_df.groupby("shadow_type").agg({
            "shadow_id": "count",
            "divergence_percentage": ["mean", "min", "max", "std"],
            "age_hours": "mean"
        }).reset_index()
        
        # Flatten column names
        shadow_type_stats.columns = ["_".join(col).strip("_") for col in shadow_type_stats.columns.values]
        
        # Group by original ID
        original_stats = shadows_df.groupby("original_id").agg({
            "shadow_id": "count",
            "divergence_percentage": "mean"
        }).reset_index()
        
        # Sort by divergence
        original_stats = original_stats.sort_values("divergence_percentage", ascending=False)
        
        # Analyze divergence over time
        shadows_df["date"] = shadows_df["created_at"].dt.date
        daily_divergence = shadows_df.groupby("date")["divergence_percentage"].mean().reset_index()
        
        # Prepare results
        results = {
            "total_shadows": len(shadows_df),
            "average_divergence": shadows_df["divergence_percentage"].mean(),
            "max_divergence": shadows_df["divergence_percentage"].max(),
            "shadow_type_stats": shadow_type_stats.to_dict(orient="records"),
            "original_stats": original_stats.to_dict(orient="records"),
            "daily_divergence": daily_divergence.to_dict(orient="records"),
            "divergence_trend": self._calculate_trend(daily_divergence["divergence_percentage"]),
            "high_divergence_count": (shadows_df["divergence_percentage"] > 50).sum(),
            "low_divergence_count": (shadows_df["divergence_percentage"] < 10).sum()
        }
        
        # Add status distribution
        status_counts = shadows_df["status"].value_counts().to_dict()
        results["status_distribution"] = status_counts
        
        # Add visualizations if requested
        if include_visualizations:
            results["visualizations"] = self._generate_shadow_visualizations(shadows_df, daily_divergence)
        
        # Update MCP context if available
        if self.mcp_bridge:
            self.mcp_bridge.update_context(
                context_type="shadow_analytics",
                context_id=f"divergence_analysis_{datetime.now().isoformat()}",
                context_data={
                    "total_shadows": results["total_shadows"],
                    "average_divergence": results["average_divergence"],
                    "max_divergence": results["max_divergence"],
                    "divergence_trend": results["divergence_trend"],
                    "high_divergence_count": results["high_divergence_count"],
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return results
    
    def _calculate_trend(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate trend from a time series.
        
        Args:
            series: Time series data
            
        Returns:
            Dict[str, Any]: Trend analysis
        """
        if series.empty or len(series) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate linear regression
        x = np.arange(len(series))
        y = series.values
        
        # Handle NaN values
        mask = ~np.isnan(y)
        if not np.any(mask):
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate slope and correlation
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine direction
        if slope > 0:
            direction = "increasing"
        elif slope < 0:
            direction = "decreasing"
        else:
            direction = "neutral"
        
        # Determine strength
        strength = abs(correlation)
        
        return {
            "direction": direction,
            "slope": slope,
            "strength": strength,
            "correlation": correlation
        }
    
    def _generate_shadow_visualizations(
        self,
        shadows_df: pd.DataFrame,
        daily_divergence: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate visualizations for shadow analytics.
        
        Args:
            shadows_df: Shadows DataFrame
            daily_divergence: Daily divergence DataFrame
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        # Convert date to string for JSON serialization
        daily_divergence["date_str"] = daily_divergence["date"].astype(str)
        
        # Prepare divergence distribution
        divergence_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        divergence_hist = np.histogram(shadows_df["divergence_percentage"], bins=divergence_bins)
        
        return {
            "time_series": {
                "dates": daily_divergence["date_str"].tolist(),
                "divergence": daily_divergence["divergence_percentage"].tolist()
            },
            "divergence_distribution": {
                "bins": divergence_bins[:-1],
                "counts": divergence_hist[0].tolist()
            },
            "shadow_type_distribution": shadows_df["shadow_type"].value_counts().to_dict(),
            "status_distribution": shadows_df["status"].value_counts().to_dict()
        }
    
    def analyze_shadow_comparison_results(
        self,
        time_period: str = "last_30_days",
        shadow_types: Optional[List[str]] = None,
        original_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze shadow comparison results.
        
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
            
            query["started_at"] = {"$gte": start_time.isoformat()}
        
        # Add original ID filter
        if original_ids:
            query["original_id"] = {"$in": original_ids}
        
        # Query comparison results
        comparisons_data = self.data_access.query(
            collection="orchestration_results",
            query=query
        )
        
        if not comparisons_data:
            return {"error": "No comparison results found for the specified criteria"}
        
        # Filter for comparison orchestrations
        comparisons_data = [
            c for c in comparisons_data
            if c.get("comparisons") is not None
        ]
        
        if not comparisons_data:
            return {"error": "No shadow comparison results found"}
        
        # Extract comparison data
        comparison_records = []
        
        for comparison in comparisons_data:
            original_id = comparison.get("original_id")
            
            for shadow_comparison in comparison.get("comparisons", []):
                shadow_id = shadow_comparison.get("shadow_id")
                shadow_type = shadow_comparison.get("shadow_type")
                
                if shadow_types and shadow_type not in shadow_types:
                    continue
                
                summary = shadow_comparison.get("summary", {})
                
                comparison_records.append({
                    "original_id": original_id,
                    "shadow_id": shadow_id,
                    "shadow_type": shadow_type,
                    "total_tests": summary.get("total_tests", 0),
                    "identical_count": summary.get("identical_count", 0),
                    "different_count": summary.get("different_count", 0),
                    "error_count": summary.get("error_count", 0),
                    "identical_percentage": summary.get("identical_percentage", 0)
                })
        
        if not comparison_records:
            return {"error": "No comparison records found after filtering"}
        
        # Convert to DataFrame
        comparisons_df = pd.DataFrame(comparison_records)
        
        # Group by shadow type
        shadow_type_stats = comparisons_df.groupby("shadow_type").agg({
            "shadow_id": "count",
            "identical_percentage": ["mean", "min", "max", "std"],
            "error_count": "sum"
        }).reset_index()
        
        # Flatten column names
        shadow_type_stats.columns = ["_".join(col).strip("_") for col in shadow_type_stats.columns.values]
        
        # Group by original ID
        original_stats = comparisons_df.groupby("original_id").agg({
            "shadow_id": "count",
            "identical_percentage": "mean"
        }).reset_index()
        
        # Sort by identical percentage
        original_stats = original_stats.sort_values("identical_percentage", ascending=False)
        
        # Prepare results
        results = {
            "total_comparisons": len(comparisons_df),
            "average_identical_percentage": comparisons_df["identical_percentage"].mean(),
            "shadow_type_stats": shadow_type_stats.to_dict(orient="records"),
            "original_stats": original_stats.to_dict(orient="records"),
            "high_fidelity_count": (comparisons_df["identical_percentage"] > 90).sum(),
            "low_fidelity_count": (comparisons_df["identical_percentage"] < 50).sum(),
            "most_accurate_shadow_type": shadow_type_stats.iloc[shadow_type_stats["identical_percentage_mean"].argmax()]["shadow_type"] if not shadow_type_stats.empty else None,
            "least_accurate_shadow_type": shadow_type_stats.iloc[shadow_type_stats["identical_percentage_mean"].argmin()]["shadow_type"] if not shadow_type_stats.empty else None
        }
        
        return results

class ConflictAnalytics:
    """Analytics for conflict detection and resolution."""
    
    def __init__(
        self,
        data_access: DataAccessService,
        mcp_bridge: Optional[MCPProtocolBridge] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the conflict analytics.
        
        Args:
            data_access: Data access service
            mcp_bridge: MCP protocol bridge (optional)
            logger: Logger instance
        """
        self.data_access = data_access
        self.mcp_bridge = mcp_bridge
        self.logger = logger or logging.getLogger(__name__)
    
    def analyze_conflict_patterns(
        self,
        time_period: str = "last_30_days",
        conflict_types: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        agent_ids: Optional[List[str]] = None,
        include_visualizations: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze conflict patterns.
        
        Args:
            time_period: Time period for analysis
            conflict_types: List of conflict types to filter
            severities: List of severities to filter
            agent_ids: List of agent IDs to filter
            include_visualizations: Whether to include visualization data
            
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
            
            query["detected_at"] = {"$gte": start_time.isoformat()}
        
        # Add conflict type filter
        if conflict_types:
            query["conflict_type"] = {"$in": conflict_types}
        
        # Add severity filter
        if severities:
            query["severity"] = {"$in": severities}
        
        # Add agent filter
        if agent_ids:
            query["participants"] = {"$in": agent_ids}
        
        # Query conflicts
        conflicts_data = self.data_access.query(
            collection="resource_conflicts",
            query=query
        )
        
        if not conflicts_data:
            return {"error": "No conflicts found for the specified criteria"}
        
        # Convert to DataFrame
        conflicts_df = pd.DataFrame(conflicts_data)
        
        # Convert timestamps to datetime
        conflicts_df["detected_at"] = pd.to_datetime(conflicts_df["detected_at"])
        
        # Add resolution status
        conflicts_df["is_resolved"] = conflicts_df["resolution"].apply(
            lambda x: x is not None and isinstance(x, dict)
        )
        
        # Extract resolution strategy
        conflicts_df["resolution_strategy"] = conflicts_df["resolution"].apply(
            lambda x: x.get("strategy") if isinstance(x, dict) else None
        )
        
        # Group by day
        conflicts_df["date"] = conflicts_df["detected_at"].dt.date
        daily_conflicts = conflicts_df.groupby("date").size().reset_index(name="conflict_count")
        
        # Calculate resolution rate
        daily_resolved = conflicts_df[conflicts_df["is_resolved"]].groupby("date").size().reset_index(name="resolved_count")
        daily_metrics = pd.merge(daily_conflicts, daily_resolved, on="date", how="left")
        daily_metrics["resolved_count"] = daily_metrics["resolved_count"].fillna(0)
        daily_metrics["resolution_rate"] = daily_metrics["resolved_count"] / daily_metrics["conflict_count"] * 100
        
        # Group by conflict type
        type_stats = conflicts_df.groupby("conflict_type").agg({
            "conflict_id": "count",
            "is_resolved": "mean"
        }).reset_index()
        
        type_stats["resolution_rate"] = type_stats["is_resolved"] * 100
        
        # Group by severity
        severity_stats = conflicts_df.groupby("severity").agg({
            "conflict_id": "count",
            "is_resolved": "mean"
        }).reset_index()
        
        severity_stats["resolution_rate"] = severity_stats["is_resolved"] * 100
        
        # Group by resolution strategy
        strategy_stats = conflicts_df[conflicts_df["resolution_strategy"].notnull()].groupby("resolution_strategy").size().reset_index(name="count")
        
        # Prepare results
        results = {
            "total_conflicts": len(conflicts_df),
            "resolved_conflicts": conflicts_df["is_resolved"].sum(),
            "overall_resolution_rate": (conflicts_df["is_resolved"].sum() / len(conflicts_df)) * 100,
            "daily_metrics": daily_metrics.to_dict(orient="records"),
            "type_stats": type_stats.to_dict(orient="records"),
            "severity_stats": severity_stats.to_dict(orient="records"),
            "strategy_stats": strategy_stats.to_dict(orient="records"),
            "trend_analysis": {
                "conflict_count_trend": self._calculate_trend(daily_conflicts["conflict_count"]),
                "resolution_rate_trend": self._calculate_trend(daily_metrics["resolution_rate"])
            }
        }
        
        # Add most common attributes
        if not conflicts_df.empty:
            results["most_common_conflict_type"] = conflicts_df["conflict_type"].value_counts().index[0]
            results["most_common_severity"] = conflicts_df["severity"].value_counts().index[0]
            
            if not conflicts_df[conflicts_df["resolution_strategy"].notnull()].empty:
                results["most_common_resolution_strategy"] = conflicts_df["resolution_strategy"].value_counts().index[0]
        
        # Add visualizations if requested
        if include_visualizations:
            results["visualizations"] = self._generate_conflict_visualizations(
                conflicts_df, daily_metrics, type_stats, severity_stats
            )
        
        # Update MCP context if available
        if self.mcp_bridge:
            self.mcp_bridge.update_context(
                context_type="conflict_analytics",
                context_id=f"pattern_analysis_{datetime.now().isoformat()}",
                context_data={
                    "total_conflicts": results["total_conflicts"],
                    "resolved_conflicts": results["resolved_conflicts"],
                    "overall_resolution_rate": results["overall_resolution_rate"],
                    "trend_analysis": results["trend_analysis"],
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return results
    
    def _calculate_trend(self, series: pd.Series) -> Dict[str, Any]:
        """
        Calculate trend from a time series.
        
        Args:
            series: Time series data
            
        Returns:
            Dict[str, Any]: Trend analysis
        """
        if series.empty or len(series) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate linear regression
        x = np.arange(len(series))
        y = series.values
        
        # Handle NaN values
        mask = ~np.isnan(y)
        if not np.any(mask):
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {"direction": "neutral", "slope": 0, "strength": 0}
        
        # Calculate slope and correlation
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine direction
        if slope > 0:
            direction = "increasing"
        elif slope < 0:
            direction = "decreasing"
        else:
            direction = "neutral"
        
        # Determine strength
        strength = abs(correlation)
        
        return {
            "direction": direction,
            "slope": slope,
            "strength": strength,
            "correlation": correlation
        }
    
    def _generate_conflict_visualizations(
        self,
        conflicts_df: pd.DataFrame,
        daily_metrics: pd.DataFrame,
        type_stats: pd.DataFrame,
        severity_stats: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate visualizations for conflict analytics.
        
        Args:
            conflicts_df: Conflicts DataFrame
            daily_metrics: Daily metrics DataFrame
            type_stats: Conflict type statistics
            severity_stats: Severity statistics
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        # Convert date to string for JSON serialization
        daily_metrics["date_str"] = daily_metrics["date"].astype(str)
        
        return {
            "time_series": {
                "dates": daily_metrics["date_str"].tolist(),
                "conflict_counts": daily_metrics["conflict_count"].tolist(),
                "resolution_rates": daily_metrics["resolution_rate"].tolist()
            },
            "conflict_type_distribution": {
                "types": type_stats["conflict_type"].tolist(),
                "counts": type_stats["conflict_id"].tolist(),
                "resolution_rates": type_stats["resolution_rate"].tolist()
            },
            "severity_distribution": {
                "severities": severity_stats["severity"].tolist(),
                "counts": severity_stats["conflict_id"].tolist(),
                "resolution_rates": severity_stats["resolution_rate"].tolist()
            },
            "resolution_strategy_distribution": conflicts_df["resolution_strategy"].value_counts().to_dict()
        }
    
    def analyze_resolution_effectiveness(
        self,
        time_period: str = "last_30_days",
        strategies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze effectiveness of conflict resolution strategies.
        
        Args:
            time_period: Time period for analysis
            strategies: List of strategies to filter
            
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
            
            query["resolved_at"] = {"$gte": start_time.isoformat()}
        
        # Add strategy filter
        if strategies:
            query["strategy"] = {"$in": strategies}
        
        # Query resolutions
        resolutions_data = self.data_access.query(
            collection="conflict_resolutions",
            query=query
        )
        
        if not resolutions_data:
            return {"error": "No resolutions found for the specified criteria"}
        
        # Convert to DataFrame
        resolutions_df = pd.DataFrame(resolutions_data)
        
        # Convert timestamps to datetime
        resolutions_df["resolved_at"] = pd.to_datetime(resolutions_df["resolved_at"])
        
        # Get conflicts for these resolutions
        conflict_ids = resolutions_df["conflict_id"].tolist()
        
        conflicts_data = []
        for conflict_id in conflict_ids:
            conflict_data = self.data_access.read(
                collection="resource_conflicts",
                document_id=conflict_id
            )
            
            if conflict_data:
                conflicts_data.append(conflict_data)
        
        if not conflicts_data:
            return {"error": "No conflict data found for resolutions"}
        
        # Convert to DataFrame
        conflicts_df = pd.DataFrame(conflicts_data)
        
        # Merge with resolutions
        merged_df = pd.merge(
            resolutions_df,
            conflicts_df[["conflict_id", "severity", "conflict_type"]],
            on="conflict_id",
            how="left"
        )
        
        # Group by strategy
        strategy_stats = merged_df.groupby("strategy").agg({
            "resolution_id": "count",
            "agreement_id": lambda x: x.notnull().sum()
        }).reset_index()
        
        strategy_stats["agreement_rate"] = (strategy_stats["agreement_id"] / strategy_stats["resolution_id"]) * 100
        
        # Group by strategy and severity
        severity_strategy_stats = merged_df.groupby(["strategy", "severity"]).agg({
            "resolution_id": "count",
            "agreement_id": lambda x: x.notnull().sum()
        }).reset_index()
        
        severity_strategy_stats["agreement_rate"] = (severity_strategy_stats["agreement_id"] / severity_strategy_stats["resolution_id"]) * 100
        
        # Group by strategy and conflict type
        type_strategy_stats = merged_df.groupby(["strategy", "conflict_type"]).agg({
            "resolution_id": "count",
            "agreement_id": lambda x: x.notnull().sum()
        }).reset_index()
        
        type_strategy_stats["agreement_rate"] = (type_strategy_stats["agreement_id"] / type_strategy_stats["resolution_id"]) * 100
        
        # Calculate resolution time
        conflicts_df["detected_at"] = pd.to_datetime(conflicts_df["detected_at"])
        
        resolution_times = []
        for _, resolution in resolutions_df.iterrows():
            conflict_id = resolution["conflict_id"]
            conflict = conflicts_df[conflicts_df["conflict_id"] == conflict_id]
            
            if not conflict.empty:
                detected_at = conflict.iloc[0]["detected_at"]
                resolved_at = resolution["resolved_at"]
                
                if detected_at and resolved_at:
                    resolution_time = (resolved_at - detected_at).total_seconds() / 60  # in minutes
                    
                    resolution_times.append({
                        "resolution_id": resolution["resolution_id"],
                        "conflict_id": conflict_id,
                        "strategy": resolution["strategy"],
                        "resolution_time_minutes": resolution_time
                    })
        
        if resolution_times:
            resolution_times_df = pd.DataFrame(resolution_times)
            
            # Group by strategy
            time_stats = resolution_times_df.groupby("strategy").agg({
                "resolution_time_minutes": ["mean", "min", "max", "std"]
            }).reset_index()
            
            # Flatten column names
            time_stats.columns = ["_".join(col).strip("_") for col in time_stats.columns.values]
        else:
            time_stats = pd.DataFrame(columns=["strategy", "resolution_time_minutes_mean", "resolution_time_minutes_min", "resolution_time_minutes_max", "resolution_time_minutes_std"])
        
        # Prepare results
        results = {
            "total_resolutions": len(resolutions_df),
            "with_agreement": resolutions_df["agreement_id"].notnull().sum(),
            "agreement_rate": (resolutions_df["agreement_id"].notnull().sum() / len(resolutions_df)) * 100,
            "strategy_stats": strategy_stats.to_dict(orient="records"),
            "severity_strategy_stats": severity_strategy_stats.to_dict(orient="records"),
            "type_strategy_stats": type_strategy_stats.to_dict(orient="records"),
            "resolution_time_stats": time_stats.to_dict(orient="records")
        }
        
        # Add most effective strategy
        if not strategy_stats.empty:
            most_effective_idx = strategy_stats["agreement_rate"].argmax()
            results["most_effective_strategy"] = strategy_stats.iloc[most_effective_idx]["strategy"]
            results["most_effective_agreement_rate"] = strategy_stats.iloc[most_effective_idx]["agreement_rate"]
            
            # Add fastest strategy
            if not time_stats.empty and "resolution_time_minutes_mean" in time_stats.columns:
                fastest_idx = time_stats["resolution_time_minutes_mean"].argmin()
                results["fastest_strategy"] = time_stats.iloc[fastest_idx]["strategy"]
                results["fastest_resolution_time"] = time_stats.iloc[fastest_idx]["resolution_time_minutes_mean"]
        
        return results

class DiplomacyAnalyticsService:
    """Service for diplomacy analytics."""
    
    def __init__(
        self,
        data_access: DataAccessService,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the diplomacy analytics service.
        
        Args:
            data_access: Data access service
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            logger: Logger instance
        """
        self.data_access = data_access
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize analytics components
        self.negotiation_analytics = NegotiationAnalytics(
            data_access=data_access,
            mcp_bridge=mcp_bridge,
            logger=logger
        )
        
        self.shadow_analytics = ShadowAnalytics(
            data_access=data_access,
            mcp_bridge=mcp_bridge,
            logger=logger
        )
        
        self.conflict_analytics = ConflictAnalytics(
            data_access=data_access,
            mcp_bridge=mcp_bridge,
            logger=logger
        )
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            topic="diplomacy.analytics.request",
            group_id="diplomacy-analytics-service",
            callback=self._handle_analytics_request
        )
        
        # Subscribe to A2A messages
        self.a2a_bridge.subscribe_to_message_type(
            message_type="diplomacy_analytics_request",
            callback=self._handle_a2a_analytics_request
        )
    
    def _handle_analytics_request(self, event: Dict[str, Any]) -> None:
        """
        Handle analytics request event.
        
        Args:
            event: Event data
        """
        try:
            request_type = event.get("request_type")
            request_id = event.get("request_id", str(uuid.uuid4()))
            
            if not request_type:
                self.logger.error("Invalid analytics request: missing request_type")
                return
            
            # Handle different request types
            if request_type == "negotiation_trends":
                self._handle_negotiation_trends(request_id, event)
            elif request_type == "strategy_effectiveness":
                self._handle_strategy_effectiveness(request_id, event)
            elif request_type == "shadow_divergence":
                self._handle_shadow_divergence(request_id, event)
            elif request_type == "shadow_comparison":
                self._handle_shadow_comparison(request_id, event)
            elif request_type == "conflict_patterns":
                self._handle_conflict_patterns(request_id, event)
            elif request_type == "resolution_effectiveness":
                self._handle_resolution_effectiveness(request_id, event)
            else:
                self.logger.error(f"Unknown request type: {request_type}")
                
                # Publish error response
                self.event_bus.publish(
                    topic="diplomacy.analytics.response",
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
            self.logger.error(f"Error handling analytics request: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=event.get("request_id", str(uuid.uuid4())),
                value={
                    "request_id": event.get("request_id", str(uuid.uuid4())),
                    "request_type": event.get("request_type", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_negotiation_trends(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle negotiation trends request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            agent_ids = event.get("agent_ids")
            resource_types = event.get("resource_types")
            include_visualizations = event.get("include_visualizations", False)
            
            # Perform analysis
            results = self.negotiation_analytics.analyze_negotiation_trends(
                time_period=time_period,
                agent_ids=agent_ids,
                resource_types=resource_types,
                include_visualizations=include_visualizations
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "negotiation_trends",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing negotiation trends: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "negotiation_trends",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_strategy_effectiveness(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle strategy effectiveness request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            strategies = event.get("strategies")
            
            # Perform analysis
            results = self.negotiation_analytics.analyze_strategy_effectiveness(
                time_period=time_period,
                strategies=strategies
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "strategy_effectiveness",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing strategy effectiveness: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "strategy_effectiveness",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_shadow_divergence(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle shadow divergence request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            shadow_types = event.get("shadow_types")
            original_ids = event.get("original_ids")
            include_visualizations = event.get("include_visualizations", False)
            
            # Perform analysis
            results = self.shadow_analytics.analyze_shadow_divergence(
                time_period=time_period,
                shadow_types=shadow_types,
                original_ids=original_ids,
                include_visualizations=include_visualizations
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "shadow_divergence",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing shadow divergence: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "shadow_divergence",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_shadow_comparison(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle shadow comparison request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            shadow_types = event.get("shadow_types")
            original_ids = event.get("original_ids")
            
            # Perform analysis
            results = self.shadow_analytics.analyze_shadow_comparison_results(
                time_period=time_period,
                shadow_types=shadow_types,
                original_ids=original_ids
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "shadow_comparison",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing shadow comparison: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "shadow_comparison",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_conflict_patterns(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle conflict patterns request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            conflict_types = event.get("conflict_types")
            severities = event.get("severities")
            agent_ids = event.get("agent_ids")
            include_visualizations = event.get("include_visualizations", False)
            
            # Perform analysis
            results = self.conflict_analytics.analyze_conflict_patterns(
                time_period=time_period,
                conflict_types=conflict_types,
                severities=severities,
                agent_ids=agent_ids,
                include_visualizations=include_visualizations
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "conflict_patterns",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing conflict patterns: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "conflict_patterns",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_resolution_effectiveness(self, request_id: str, event: Dict[str, Any]) -> None:
        """
        Handle resolution effectiveness request.
        
        Args:
            request_id: Request ID
            event: Event data
        """
        try:
            time_period = event.get("time_period", "last_30_days")
            strategies = event.get("strategies")
            
            # Perform analysis
            results = self.conflict_analytics.analyze_resolution_effectiveness(
                time_period=time_period,
                strategies=strategies
            )
            
            # Publish response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "resolution_effectiveness",
                    "status": "success",
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error analyzing resolution effectiveness: {str(e)}")
            
            # Publish error response
            self.event_bus.publish(
                topic="diplomacy.analytics.response",
                key=request_id,
                value={
                    "request_id": request_id,
                    "request_type": "resolution_effectiveness",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_a2a_analytics_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A analytics request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            sender_id = message.get("sender_id")
            
            request_type = content.get("request_type")
            request_id = content.get("request_id", str(uuid.uuid4()))
            
            if not request_type:
                self.logger.error("Invalid A2A analytics request: missing request_type")
                return
            
            # Convert A2A message to event
            event = {
                "request_id": request_id,
                "request_type": request_type,
                "sender_id": sender_id,
                **content
            }
            
            # Handle request
            self._handle_analytics_request(event)
            
            # Subscribe to response for this request
            self.event_bus.subscribe(
                topic="diplomacy.analytics.response",
                group_id=f"a2a-response-handler-{request_id}",
                callback=lambda response: self._handle_a2a_response(response, sender_id),
                auto_unsubscribe=True
            )
        
        except Exception as e:
            self.logger.error(f"Error handling A2A analytics request: {str(e)}")
            
            # Send error response
            self.a2a_bridge.send_message(
                message_type="diplomacy_analytics_response",
                sender_id="diplomacy_analytics_service",
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
                message_type="diplomacy_analytics_response",
                sender_id="diplomacy_analytics_service",
                recipient_id=recipient_id,
                content=response
            )
        
        except Exception as e:
            self.logger.error(f"Error handling A2A response: {str(e)}")
    
    def generate_analytics_report(
        self,
        report_type: str,
        time_period: str = "last_30_days",
        include_visualizations: bool = True,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report.
        
        Args:
            report_type: Type of report (negotiation, shadow, conflict, comprehensive)
            time_period: Time period for analysis
            include_visualizations: Whether to include visualization data
            output_format: Output format (json, html)
            
        Returns:
            Dict[str, Any]: Report data
        """
        report = {
            "report_type": report_type,
            "time_period": time_period,
            "generated_at": datetime.now().isoformat(),
            "sections": []
        }
        
        try:
            # Generate report based on type
            if report_type == "negotiation" or report_type == "comprehensive":
                # Add negotiation trends
                negotiation_trends = self.negotiation_analytics.analyze_negotiation_trends(
                    time_period=time_period,
                    include_visualizations=include_visualizations
                )
                
                report["sections"].append({
                    "title": "Negotiation Trends",
                    "data": negotiation_trends
                })
                
                # Add strategy effectiveness
                strategy_effectiveness = self.negotiation_analytics.analyze_strategy_effectiveness(
                    time_period=time_period
                )
                
                report["sections"].append({
                    "title": "Negotiation Strategy Effectiveness",
                    "data": strategy_effectiveness
                })
            
            if report_type == "shadow" or report_type == "comprehensive":
                # Add shadow divergence
                shadow_divergence = self.shadow_analytics.analyze_shadow_divergence(
                    time_period=time_period,
                    include_visualizations=include_visualizations
                )
                
                report["sections"].append({
                    "title": "Shadow Divergence Analysis",
                    "data": shadow_divergence
                })
                
                # Add shadow comparison
                shadow_comparison = self.shadow_analytics.analyze_shadow_comparison_results(
                    time_period=time_period
                )
                
                report["sections"].append({
                    "title": "Shadow Comparison Analysis",
                    "data": shadow_comparison
                })
            
            if report_type == "conflict" or report_type == "comprehensive":
                # Add conflict patterns
                conflict_patterns = self.conflict_analytics.analyze_conflict_patterns(
                    time_period=time_period,
                    include_visualizations=include_visualizations
                )
                
                report["sections"].append({
                    "title": "Conflict Patterns Analysis",
                    "data": conflict_patterns
                })
                
                # Add resolution effectiveness
                resolution_effectiveness = self.conflict_analytics.analyze_resolution_effectiveness(
                    time_period=time_period
                )
                
                report["sections"].append({
                    "title": "Resolution Effectiveness Analysis",
                    "data": resolution_effectiveness
                })
            
            # Generate HTML if requested
            if output_format == "html":
                report["html"] = self._generate_html_report(report)
            
            return report
        
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {str(e)}")
            
            return {
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """
        Generate HTML report from report data.
        
        Args:
            report: Report data
            
        Returns:
            str: HTML report
        """
        # This is a simplified implementation
        # In a real system, this would use a template engine
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Diplomacy Analytics Report: {report["report_type"]}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
                .metric {{ margin-bottom: 10px; }}
                .metric-name {{ font-weight: bold; }}
                .metric-value {{ color: #2980b9; }}
                .chart {{ margin-top: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Diplomacy Analytics Report: {report["report_type"].capitalize()}</h1>
            <p>Generated at: {report["generated_at"]}</p>
            <p>Time period: {report["time_period"]}</p>
        """
        
        # Add sections
        for section in report["sections"]:
            html += f"""
            <div class="section">
                <h2>{section["title"]}</h2>
            """
            
            # Add section data
            data = section["data"]
            
            # Handle different section types
            if "total_sessions" in data:
                # Negotiation trends
                html += f"""
                <div class="metric">
                    <span class="metric-name">Total Sessions:</span>
                    <span class="metric-value">{data.get("total_sessions", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Successful Sessions:</span>
                    <span class="metric-value">{data.get("successful_sessions", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Overall Success Rate:</span>
                    <span class="metric-value">{data.get("overall_success_rate", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Average Duration:</span>
                    <span class="metric-value">{data.get("avg_duration_minutes", 0):.2f} minutes</span>
                </div>
                """
            elif "strategy_stats" in data:
                # Strategy effectiveness
                html += f"""
                <div class="metric">
                    <span class="metric-name">Most Effective Strategy:</span>
                    <span class="metric-value">{data.get("most_effective_strategy", "N/A")}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Least Effective Strategy:</span>
                    <span class="metric-value">{data.get("least_effective_strategy", "N/A")}</span>
                </div>
                
                <h3>Strategy Statistics</h3>
                <table>
                    <tr>
                        <th>Strategy</th>
                        <th>Total Proposals</th>
                        <th>Accepted</th>
                        <th>Rejected</th>
                        <th>Countered</th>
                        <th>Acceptance Rate</th>
                    </tr>
                """
                
                for stat in data.get("strategy_stats", []):
                    html += f"""
                    <tr>
                        <td>{stat.get("strategy", "N/A")}</td>
                        <td>{stat.get("total_proposals", 0)}</td>
                        <td>{stat.get("accepted", 0)}</td>
                        <td>{stat.get("rejected", 0)}</td>
                        <td>{stat.get("countered", 0)}</td>
                        <td>{stat.get("acceptance_rate", 0):.2f}%</td>
                    </tr>
                    """
                
                html += "</table>"
            elif "total_shadows" in data:
                # Shadow divergence
                html += f"""
                <div class="metric">
                    <span class="metric-name">Total Shadows:</span>
                    <span class="metric-value">{data.get("total_shadows", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Average Divergence:</span>
                    <span class="metric-value">{data.get("average_divergence", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Max Divergence:</span>
                    <span class="metric-value">{data.get("max_divergence", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">High Divergence Count:</span>
                    <span class="metric-value">{data.get("high_divergence_count", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Low Divergence Count:</span>
                    <span class="metric-value">{data.get("low_divergence_count", 0)}</span>
                </div>
                """
            elif "total_comparisons" in data:
                # Shadow comparison
                html += f"""
                <div class="metric">
                    <span class="metric-name">Total Comparisons:</span>
                    <span class="metric-value">{data.get("total_comparisons", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Average Identical Percentage:</span>
                    <span class="metric-value">{data.get("average_identical_percentage", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Most Accurate Shadow Type:</span>
                    <span class="metric-value">{data.get("most_accurate_shadow_type", "N/A")}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Least Accurate Shadow Type:</span>
                    <span class="metric-value">{data.get("least_accurate_shadow_type", "N/A")}</span>
                </div>
                """
            elif "total_conflicts" in data:
                # Conflict patterns
                html += f"""
                <div class="metric">
                    <span class="metric-name">Total Conflicts:</span>
                    <span class="metric-value">{data.get("total_conflicts", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Resolved Conflicts:</span>
                    <span class="metric-value">{data.get("resolved_conflicts", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Overall Resolution Rate:</span>
                    <span class="metric-value">{data.get("overall_resolution_rate", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Most Common Conflict Type:</span>
                    <span class="metric-value">{data.get("most_common_conflict_type", "N/A")}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Most Common Severity:</span>
                    <span class="metric-value">{data.get("most_common_severity", "N/A")}</span>
                </div>
                """
            elif "total_resolutions" in data:
                # Resolution effectiveness
                html += f"""
                <div class="metric">
                    <span class="metric-name">Total Resolutions:</span>
                    <span class="metric-value">{data.get("total_resolutions", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">With Agreement:</span>
                    <span class="metric-value">{data.get("with_agreement", 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Agreement Rate:</span>
                    <span class="metric-value">{data.get("agreement_rate", 0):.2f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Most Effective Strategy:</span>
                    <span class="metric-value">{data.get("most_effective_strategy", "N/A")}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">Fastest Strategy:</span>
                    <span class="metric-value">{data.get("fastest_strategy", "N/A")}</span>
                </div>
                """
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
