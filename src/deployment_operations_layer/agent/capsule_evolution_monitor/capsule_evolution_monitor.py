"""
Capsule Evolution Monitor - Core agent implementation

This agent tracks post-deployment capsule mutation or override events, ensuring
that all changes to capsules are properly tracked, analyzed, and reported.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CapsuleEvolutionMonitor:
    """
    Monitors and tracks the evolution of capsules after deployment.
    
    This agent is responsible for detecting, tracking, and analyzing changes to
    capsules after they have been deployed, including mutations, overrides, and
    drift from the original configuration.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Capsule Evolution Monitor.
        
        Args:
            config: Configuration dictionary for the monitor
        """
        self.config = config or {}
        self.mutation_tracker = None
        self.override_logger = None
        self.evolution_analyzer = None
        self.drift_detector = None
        self.monitoring_interval = self.config.get("monitoring_interval", 300)  # 5 minutes default
        self.is_running = False
        self.capsule_states = {}
        self.last_check_time = {}
        
        logger.info("Initializing Capsule Evolution Monitor")
    
    def initialize(self):
        """Initialize all subcomponents and prepare for monitoring."""
        from .mutation_tracker import MutationTracker
        from .override_logger import OverrideLogger
        from .evolution_analyzer import EvolutionAnalyzer
        from .drift_detector import DriftDetector
        
        logger.info("Initializing Capsule Evolution Monitor subcomponents")
        
        self.mutation_tracker = MutationTracker(self.config.get("mutation_tracker_config", {}))
        self.override_logger = OverrideLogger(self.config.get("override_logger_config", {}))
        self.evolution_analyzer = EvolutionAnalyzer(self.config.get("evolution_analyzer_config", {}))
        self.drift_detector = DriftDetector(self.config.get("drift_detector_config", {}))
        
        # Initialize subcomponents
        self.mutation_tracker.initialize()
        self.override_logger.initialize()
        self.evolution_analyzer.initialize()
        self.drift_detector.initialize()
        
        logger.info("Capsule Evolution Monitor initialization complete")
        return True
    
    def start_monitoring(self, capsule_ids: List[str] = None):
        """
        Start monitoring the specified capsules.
        
        Args:
            capsule_ids: List of capsule IDs to monitor. If None, monitor all capsules.
        """
        if self.is_running:
            logger.warning("Monitoring is already running")
            return False
        
        logger.info(f"Starting monitoring for capsules: {capsule_ids if capsule_ids else 'all'}")
        self.is_running = True
        
        # Initialize monitoring state for each capsule
        if capsule_ids:
            for capsule_id in capsule_ids:
                self._initialize_capsule_monitoring(capsule_id)
        
        return True
    
    def stop_monitoring(self):
        """Stop monitoring all capsules."""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return False
        
        logger.info("Stopping capsule monitoring")
        self.is_running = False
        return True
    
    def _initialize_capsule_monitoring(self, capsule_id: str):
        """
        Initialize monitoring for a specific capsule.
        
        Args:
            capsule_id: ID of the capsule to monitor
        """
        # Get initial state of the capsule
        initial_state = self._get_capsule_state(capsule_id)
        self.capsule_states[capsule_id] = initial_state
        self.last_check_time[capsule_id] = datetime.now()
        
        logger.info(f"Initialized monitoring for capsule {capsule_id}")
    
    def _get_capsule_state(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get the current state of a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Dictionary representing the current state of the capsule
        """
        # In a real implementation, this would query the capsule registry or other source
        # For now, we'll return a placeholder
        return {
            "capsule_id": capsule_id,
            "version": "1.0.0",
            "configuration": {},
            "status": "active",
            "last_updated": datetime.now().isoformat()
        }
    
    def check_for_changes(self, capsule_id: str) -> Dict[str, Any]:
        """
        Check for changes in a capsule since the last check.
        
        Args:
            capsule_id: ID of the capsule to check
            
        Returns:
            Dictionary with change information
        """
        if capsule_id not in self.capsule_states:
            logger.warning(f"Capsule {capsule_id} is not being monitored")
            return {"error": "Capsule not monitored"}
        
        # Get current state
        current_state = self._get_capsule_state(capsule_id)
        previous_state = self.capsule_states[capsule_id]
        
        # Detect changes
        changes = self.drift_detector.detect_drift(previous_state, current_state)
        
        if changes["has_changes"]:
            # Log mutations
            self.mutation_tracker.track_mutation(
                capsule_id, 
                previous_state, 
                current_state, 
                changes["changes"]
            )
            
            # Log overrides if applicable
            if changes.get("is_override", False):
                self.override_logger.log_override(
                    capsule_id,
                    previous_state,
                    current_state,
                    changes["changes"],
                    changes.get("override_source", "unknown")
                )
            
            # Update stored state
            self.capsule_states[capsule_id] = current_state
            self.last_check_time[capsule_id] = datetime.now()
            
            # Analyze evolution
            evolution_analysis = self.evolution_analyzer.analyze_evolution(
                capsule_id,
                changes["changes"],
                self.mutation_tracker.get_mutation_history(capsule_id)
            )
            
            changes["analysis"] = evolution_analysis
        
        return changes
    
    def get_evolution_report(self, capsule_id: str) -> Dict[str, Any]:
        """
        Generate an evolution report for a capsule.
        
        Args:
            capsule_id: ID of the capsule
            
        Returns:
            Dictionary with evolution report data
        """
        if capsule_id not in self.capsule_states:
            logger.warning(f"Capsule {capsule_id} is not being monitored")
            return {"error": "Capsule not monitored"}
        
        mutation_history = self.mutation_tracker.get_mutation_history(capsule_id)
        override_history = self.override_logger.get_override_history(capsule_id)
        
        analysis = self.evolution_analyzer.generate_evolution_report(
            capsule_id,
            mutation_history,
            override_history
        )
        
        return {
            "capsule_id": capsule_id,
            "first_monitored": self.last_check_time.get(capsule_id).isoformat(),
            "current_state": self.capsule_states.get(capsule_id),
            "mutation_count": len(mutation_history),
            "override_count": len(override_history),
            "analysis": analysis
        }
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle for all monitored capsules."""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return False
        
        logger.info("Running monitoring cycle")
        
        for capsule_id in self.capsule_states.keys():
            try:
                changes = self.check_for_changes(capsule_id)
                if changes.get("has_changes", False):
                    logger.info(f"Detected changes in capsule {capsule_id}: {changes['changes']}")
            except Exception as e:
                logger.error(f"Error checking capsule {capsule_id}: {str(e)}")
        
        return True
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring until stopped."""
        self.is_running = True
        
        logger.info(f"Starting continuous monitoring with interval {self.monitoring_interval}s")
        
        try:
            while self.is_running:
                self.run_monitoring_cycle()
                time.sleep(self.monitoring_interval)
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted")
            self.is_running = False
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
            self.is_running = False
        
        logger.info("Continuous monitoring stopped")
