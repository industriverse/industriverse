"""
Execution Mode Manager Module for Industriverse Workflow Automation Layer

This module is responsible for managing and determining the execution mode
of workflows based on trust scores, agent confidence, and manifest configurations.
It implements the logic for switching between Passive, Reactive, Predictive,
and Strategic modes, enabling dynamic governance and adaptive behavior.

The ExecutionModeManager class provides the core logic for determining the
appropriate execution mode for a given context.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """Enum representing the possible execution modes for workflows."""
    PASSIVE = "passive"
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    STRATEGIC = "strategic"


class ExecutionModeConfig(BaseModel):
    """Model representing an execution mode configuration with triggers and conditions."""
    mode: ExecutionMode
    trigger: str
    threshold: Optional[str] = None  # e.g., "trust_score >= 0.6"
    condition: Optional[str] = None  # e.g., "agent_confidence > 0.8"


class ExecutionModeManager:
    """
    Manages the determination of workflow execution modes.
    
    This class evaluates trust scores, agent confidence, and workflow manifest
    configurations to select the appropriate execution mode (Passive, Reactive,
    Predictive, Strategic).
    """
    
    def __init__(self, default_mode: ExecutionMode = ExecutionMode.REACTIVE):
        """
        Initialize the ExecutionModeManager.
        
        Args:
            default_mode: The default execution mode if no specific mode is determined
        """
        self.default_mode = default_mode
        logger.info(f"ExecutionModeManager initialized with default mode: {default_mode}")
    
    def determine_execution_mode(
        self,
        trust_score: float,
        agent_confidence: float,
        mode_configs: Optional[List[ExecutionModeConfig]] = None,
        current_mode: Optional[ExecutionMode] = None
    ) -> ExecutionMode:
        """
        Determine the appropriate execution mode based on context and configuration.
        
        Args:
            trust_score: The current trust score (0.0 to 1.0)
            agent_confidence: The current agent confidence (0.0 to 1.0)
            mode_configs: List of execution mode configurations from the workflow manifest
            current_mode: The current execution mode (optional, for hysteresis)
            
        Returns:
            The determined ExecutionMode
        """
        
        if not mode_configs:
            # Fallback to simple logic if no specific configs are provided
            if trust_score >= 0.8 and agent_confidence >= 0.9:
                return ExecutionMode.STRATEGIC
            elif trust_score >= 0.7 and agent_confidence >= 0.8:
                return ExecutionMode.PREDICTIVE
            elif trust_score >= 0.6:
                return ExecutionMode.REACTIVE
            else:
                return ExecutionMode.PASSIVE
        
        # Evaluate configured modes (prioritize stricter modes first: Strategic > Predictive > Reactive > Passive)
        ordered_modes = [ExecutionMode.STRATEGIC, ExecutionMode.PREDICTIVE, ExecutionMode.REACTIVE, ExecutionMode.PASSIVE]
        
        for target_mode in ordered_modes:
            config = next((mc for mc in mode_configs if mc.mode == target_mode), None)
            if config:
                if self._evaluate_condition(config.threshold, trust_score, agent_confidence) and \
                   self._evaluate_condition(config.condition, trust_score, agent_confidence):
                    logger.debug(f"Determined execution mode: {target_mode} based on config: {config}")
                    return target_mode
        
        # If no configured mode matches, return the default
        logger.debug(f"No specific execution mode matched, returning default: {self.default_mode}")
        return self.default_mode
    
    def _evaluate_condition(self, condition_str: Optional[str], trust_score: float, agent_confidence: float) -> bool:
        """
        Evaluate a condition string using the provided context.
        
        Args:
            condition_str: The condition string (e.g., "trust_score >= 0.6")
            trust_score: The current trust score
            agent_confidence: The current agent confidence
            
        Returns:
            True if the condition evaluates to true, False otherwise
        """
        if not condition_str:
            return True  # No condition means it always passes
        
        try:
            # Define the context for evaluation
            context = {
                "trust_score": trust_score,
                "agent_confidence": agent_confidence,
                "True": True,
                "False": False
            }
            
            # Evaluate the condition string
            # Warning: Using eval can be risky if the condition string is user-provided.
            # In a production system, use a safer evaluation method (e.g., a dedicated expression language parser).
            result = eval(condition_str, {"__builtins__": {}}, context)
            return bool(result)
        
        except Exception as e:
            logger.error(f"Failed to evaluate condition 	'{condition_str}	': {e}")
            return False

# Example Usage:
if __name__ == "__main__":
    manager = ExecutionModeManager()
    
    # Example configurations from the prompt
    configs = [
        ExecutionModeConfig(mode=ExecutionMode.REACTIVE, trigger="external_event", threshold="trust_score >= 0.6"),
        ExecutionModeConfig(mode=ExecutionMode.PREDICTIVE, trigger="forecasted_task", condition="agent_confidence > 0.8"),
        ExecutionModeConfig(mode=ExecutionMode.STRATEGIC, trigger="optimization_opportunity", condition="trust_score >= 0.8 and agent_confidence > 0.9"),
        ExecutionModeConfig(mode=ExecutionMode.PASSIVE, trigger="default", condition="trust_score < 0.6")
    ]
    
    # Test cases
    test_cases = [
        {"trust": 0.9, "confidence": 0.95, "expected": ExecutionMode.STRATEGIC},
        {"trust": 0.85, "confidence": 0.85, "expected": ExecutionMode.PREDICTIVE}, # Strategic condition fails (confidence <= 0.9)
        {"trust": 0.7, "confidence": 0.9, "expected": ExecutionMode.PREDICTIVE}, # Reactive threshold passes, but Predictive condition also passes
        {"trust": 0.65, "confidence": 0.7, "expected": ExecutionMode.REACTIVE}, # Predictive condition fails
        {"trust": 0.5, "confidence": 0.9, "expected": ExecutionMode.PASSIVE}, # Reactive threshold fails
    ]
    
    print("Testing with configurations:")
    for case in test_cases:
        mode = manager.determine_execution_mode(case["trust"], case["confidence"], configs)
        print(f"Trust: {case['trust']}, Confidence: {case['confidence']} -> Mode: {mode} (Expected: {case['expected']}) - {'Correct' if mode == case['expected'] else 'Incorrect'}")
    
    print("\nTesting without configurations (default logic):")
    for case in test_cases:
        mode = manager.determine_execution_mode(case["trust"], case["confidence"], None)
        # Adjust expected for default logic
        if case["trust"] >= 0.8 and case["confidence"] >= 0.9:
            expected_default = ExecutionMode.STRATEGIC
        elif case["trust"] >= 0.7 and case["confidence"] >= 0.8:
            expected_default = ExecutionMode.PREDICTIVE
        elif case["trust"] >= 0.6:
            expected_default = ExecutionMode.REACTIVE
        else:
            expected_default = ExecutionMode.PASSIVE
        print(f"Trust: {case['trust']}, Confidence: {case['confidence']} -> Mode: {mode} (Expected: {expected_default}) - {'Correct' if mode == expected_default else 'Incorrect'}")
