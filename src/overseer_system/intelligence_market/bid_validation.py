"""
Bid Validation Module for the Intelligence Market Phase of the Overseer System.

This module provides functionality for validating bids in the intelligence market,
ensuring they meet all requirements and constraints before being accepted.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

from .market_models import (
    Bid, BidStatus, BidType, MarketRole, ResourceType,
    AgentProfile, ResourceSpecification, PriceSpecification
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.bid_validation")

class BidValidator:
    """
    Validates bids in the intelligence market to ensure they meet all requirements.
    """
    
    def __init__(self, market_policies: Dict[str, Any] = None):
        """
        Initialize the bid validator.
        
        Args:
            market_policies: Dictionary of market policies to enforce
        """
        self.market_policies = market_policies or {}
        logger.info("BidValidator initialized with %d policies", len(self.market_policies))
    
    def validate_bid(self, bid: Bid, agent_profile: Optional[AgentProfile] = None) -> Tuple[bool, List[str]]:
        """
        Validate a bid against all requirements and constraints.
        
        Args:
            bid: The bid to validate
            agent_profile: Optional agent profile for additional validation
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_validation_errors)
        """
        errors = []
        
        # Basic validation
        if not self._validate_bid_basics(bid, errors):
            return False, errors
        
        # Agent validation
        if agent_profile and not self._validate_agent(bid, agent_profile, errors):
            return False, errors
        
        # Resource validation
        if not self._validate_resources(bid, errors):
            return False, errors
        
        # Price validation
        if not self._validate_price(bid, errors):
            return False, errors
        
        # Task validation if present
        if bid.task and not self._validate_task(bid, agent_profile, errors):
            return False, errors
        
        # Policy validation
        if not self._validate_against_policies(bid, agent_profile, errors):
            return False, errors
        
        # If we got here with no errors, the bid is valid
        return len(errors) == 0, errors
    
    def _validate_bid_basics(self, bid: Bid, errors: List[str]) -> bool:
        """
        Validate basic bid properties.
        
        Args:
            bid: The bid to validate
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        if not bid.bid_id:
            errors.append("Bid ID is required")
        
        if not bid.agent_id:
            errors.append("Agent ID is required")
        
        # Check bid type
        try:
            BidType(bid.bid_type)
        except ValueError:
            errors.append(f"Invalid bid type: {bid.bid_type}")
        
        # Check role
        try:
            MarketRole(bid.role)
        except ValueError:
            errors.append(f"Invalid market role: {bid.role}")
        
        # Check expiration
        if bid.expires_at and bid.expires_at <= datetime.now():
            errors.append("Bid expiration must be in the future")
        
        # Check resources
        if not bid.resources or len(bid.resources) == 0:
            errors.append("Bid must include at least one resource")
        
        # Check price
        if not bid.price:
            errors.append("Bid must include a price specification")
        
        return len(errors) == 0
    
    def _validate_agent(self, bid: Bid, agent_profile: AgentProfile, errors: List[str]) -> bool:
        """
        Validate the agent making the bid.
        
        Args:
            bid: The bid to validate
            agent_profile: The agent profile
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check agent ID matches
        if bid.agent_id != agent_profile.agent_id:
            errors.append(f"Bid agent ID {bid.agent_id} does not match profile agent ID {agent_profile.agent_id}")
        
        # Check agent has appropriate role
        if bid.role not in agent_profile.market_roles:
            errors.append(f"Agent does not have the {bid.role} role required for this bid")
        
        # Check trust score meets minimum requirements
        min_trust_score = self.market_policies.get("min_trust_score", 0.0)
        if agent_profile.trust_score < min_trust_score:
            errors.append(f"Agent trust score {agent_profile.trust_score} is below minimum required {min_trust_score}")
        
        # For seller bids, check if agent has the resources
        if bid.role == MarketRole.SELLER:
            for resource_spec in bid.resources:
                resource_type = resource_spec.resource_type
                quantity = resource_spec.quantity
                
                if resource_type not in agent_profile.resource_availability:
                    errors.append(f"Agent does not have {resource_type} resources available")
                elif agent_profile.resource_availability[resource_type] < quantity:
                    errors.append(f"Agent has insufficient {resource_type} resources: {agent_profile.resource_availability[resource_type]} < {quantity}")
        
        # For buyer bids with tasks, check if agent has required capabilities
        if bid.role == MarketRole.BUYER and bid.task:
            required_capabilities = bid.task.required_capabilities
            agent_capability_ids = [cap.capability_id for cap in agent_profile.capabilities]
            
            for req_cap in required_capabilities:
                if req_cap not in agent_capability_ids:
                    errors.append(f"Agent does not have required capability: {req_cap}")
        
        return len(errors) == 0
    
    def _validate_resources(self, bid: Bid, errors: List[str]) -> bool:
        """
        Validate the resources in the bid.
        
        Args:
            bid: The bid to validate
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        for i, resource in enumerate(bid.resources):
            # Check resource type
            try:
                ResourceType(resource.resource_type)
            except ValueError:
                errors.append(f"Invalid resource type in resource {i}: {resource.resource_type}")
            
            # Check quantity
            if resource.quantity <= 0:
                errors.append(f"Resource {i} quantity must be positive: {resource.quantity}")
            
            # Check unit
            if not resource.unit:
                errors.append(f"Resource {i} must specify a unit")
            
            # Check for resource-specific constraints
            resource_type = resource.resource_type
            if resource_type in self.market_policies.get("resource_constraints", {}):
                constraints = self.market_policies["resource_constraints"][resource_type]
                
                # Check minimum quantity
                min_quantity = constraints.get("min_quantity")
                if min_quantity is not None and resource.quantity < min_quantity:
                    errors.append(f"Resource {i} quantity {resource.quantity} is below minimum {min_quantity}")
                
                # Check maximum quantity
                max_quantity = constraints.get("max_quantity")
                if max_quantity is not None and resource.quantity > max_quantity:
                    errors.append(f"Resource {i} quantity {resource.quantity} exceeds maximum {max_quantity}")
        
        return len(errors) == 0
    
    def _validate_price(self, bid: Bid, errors: List[str]) -> bool:
        """
        Validate the price in the bid.
        
        Args:
            bid: The bid to validate
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        price = bid.price
        
        # Check required fields
        if not price.currency:
            errors.append("Price must specify a currency")
        
        if price.amount <= 0:
            errors.append(f"Price amount must be positive: {price.amount}")
        
        if not price.unit:
            errors.append("Price must specify a unit")
        
        # Check min/max consistency
        if price.min_amount is not None and price.max_amount is not None:
            if price.min_amount > price.max_amount:
                errors.append(f"Price minimum {price.min_amount} cannot be greater than maximum {price.max_amount}")
        
        # Check against market price constraints
        if "price_constraints" in self.market_policies:
            constraints = self.market_policies["price_constraints"]
            
            # Check currency
            allowed_currencies = constraints.get("allowed_currencies")
            if allowed_currencies and price.currency not in allowed_currencies:
                errors.append(f"Currency {price.currency} is not allowed. Allowed currencies: {', '.join(allowed_currencies)}")
            
            # Check price floor
            price_floor = constraints.get("price_floor")
            if price_floor is not None and price.amount < price_floor:
                errors.append(f"Price {price.amount} is below the price floor {price_floor}")
            
            # Check price ceiling
            price_ceiling = constraints.get("price_ceiling")
            if price_ceiling is not None and price.amount > price_ceiling:
                errors.append(f"Price {price.amount} exceeds the price ceiling {price_ceiling}")
        
        return len(errors) == 0
    
    def _validate_task(self, bid: Bid, agent_profile: Optional[AgentProfile], errors: List[str]) -> bool:
        """
        Validate the task in the bid.
        
        Args:
            bid: The bid to validate
            agent_profile: Optional agent profile
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        task = bid.task
        
        # Check required fields
        if not task.task_id:
            errors.append("Task ID is required")
        
        if not task.name:
            errors.append("Task name is required")
        
        if not task.description:
            errors.append("Task description is required")
        
        # Check deadline
        if task.deadline and task.deadline <= datetime.now():
            errors.append("Task deadline must be in the future")
        
        # Check priority range
        if task.priority < 0 or task.priority > 100:
            errors.append(f"Task priority must be between 0 and 100: {task.priority}")
        
        # Check required capabilities
        if not task.required_capabilities:
            errors.append("Task must specify at least one required capability")
        
        # Check if buyer has required capabilities (for seller bids)
        if bid.role == MarketRole.SELLER and agent_profile:
            buyer_capabilities = self.market_policies.get("buyer_capabilities", {}).get(bid.agent_id, [])
            for req_cap in task.required_capabilities:
                if req_cap not in buyer_capabilities:
                    errors.append(f"Buyer does not have required capability: {req_cap}")
        
        return len(errors) == 0
    
    def _validate_against_policies(self, bid: Bid, agent_profile: Optional[AgentProfile], errors: List[str]) -> bool:
        """
        Validate the bid against market policies.
        
        Args:
            bid: The bid to validate
            agent_profile: Optional agent profile
            errors: List to append errors to
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check bid type restrictions
        allowed_bid_types = self.market_policies.get("allowed_bid_types")
        if allowed_bid_types and bid.bid_type not in allowed_bid_types:
            errors.append(f"Bid type {bid.bid_type} is not allowed. Allowed types: {', '.join(allowed_bid_types)}")
        
        # Check role restrictions
        allowed_roles = self.market_policies.get("allowed_roles")
        if allowed_roles and bid.role not in allowed_roles:
            errors.append(f"Role {bid.role} is not allowed. Allowed roles: {', '.join(allowed_roles)}")
        
        # Check agent restrictions
        blacklisted_agents = self.market_policies.get("blacklisted_agents", [])
        if bid.agent_id in blacklisted_agents:
            errors.append(f"Agent {bid.agent_id} is blacklisted from the market")
        
        # Check bid dependencies
        if bid.dependencies:
            # Check for circular dependencies
            if bid.bid_id in bid.dependencies:
                errors.append("Bid cannot depend on itself")
            
            # Check for maximum dependency depth
            max_dependency_depth = self.market_policies.get("max_dependency_depth", 3)
            if len(bid.dependencies) > max_dependency_depth:
                errors.append(f"Bid has too many dependencies: {len(bid.dependencies)} > {max_dependency_depth}")
        
        # Check for market pause
        if self.market_policies.get("market_paused", False):
            errors.append("Market is currently paused, no new bids accepted")
        
        return len(errors) == 0

class BidSignatureValidator:
    """
    Validates cryptographic signatures on bids.
    """
    
    def __init__(self, public_keys: Dict[str, str] = None):
        """
        Initialize the signature validator.
        
        Args:
            public_keys: Dictionary mapping agent IDs to public keys
        """
        self.public_keys = public_keys or {}
        logger.info("BidSignatureValidator initialized with %d public keys", len(self.public_keys))
    
    def validate_signature(self, bid: Bid) -> Tuple[bool, Optional[str]]:
        """
        Validate the cryptographic signature on a bid.
        
        Args:
            bid: The bid to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Skip validation if signature is not required
        if not bid.signature:
            return True, None
        
        # Check if we have the agent's public key
        if bid.agent_id not in self.public_keys:
            return False, f"No public key available for agent {bid.agent_id}"
        
        # In a real implementation, this would verify the signature
        # using the agent's public key and the bid data
        # For this implementation, we'll just log the validation
        logger.info("Validating signature for bid %s from agent %s", bid.bid_id, bid.agent_id)
        
        # Simulate signature validation
        is_valid = True  # In a real implementation, this would be the result of verification
        error_message = None if is_valid else "Invalid signature"
        
        return is_valid, error_message

def validate_bid_complete(
    bid: Bid,
    agent_profile: Optional[AgentProfile] = None,
    market_policies: Dict[str, Any] = None,
    public_keys: Dict[str, str] = None
) -> Tuple[bool, List[str]]:
    """
    Perform complete validation of a bid, including content and signature.
    
    Args:
        bid: The bid to validate
        agent_profile: Optional agent profile for additional validation
        market_policies: Dictionary of market policies to enforce
        public_keys: Dictionary mapping agent IDs to public keys
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_validation_errors)
    """
    # Create validators
    bid_validator = BidValidator(market_policies)
    signature_validator = BidSignatureValidator(public_keys)
    
    # Validate bid content
    content_valid, content_errors = bid_validator.validate_bid(bid, agent_profile)
    
    # Validate signature if content is valid
    if content_valid and bid.signature:
        sig_valid, sig_error = signature_validator.validate_signature(bid)
        if not sig_valid and sig_error:
            content_errors.append(sig_error)
            content_valid = False
    
    return content_valid, content_errors
