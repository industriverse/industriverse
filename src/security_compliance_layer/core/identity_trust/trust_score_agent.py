"""
Trust Score Agent Module for the Security & Compliance Layer of Industriverse.

This module implements a comprehensive Trust Score Agent that supports:
- Dynamic trust scoring for entities, capsules, and operations
- Multi-factor trust evaluation
- Contextual trust adjustment
- Trust history tracking
- Trust-based access decisions
- Trust economy operations

The Trust Score Agent is a critical component of the Zero-Trust Security architecture,
enabling dynamic trust-based decisions across the Industriverse ecosystem.
"""

import os
import time
import uuid
import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrustScoreAgent:
    """
    Trust Score Agent for the Security & Compliance Layer.
    
    This class provides comprehensive trust scoring services including:
    - Dynamic trust scoring for entities, capsules, and operations
    - Multi-factor trust evaluation
    - Contextual trust adjustment
    - Trust history tracking
    - Trust-based access decisions
    - Trust economy operations
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Trust Score Agent with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.trust_scores = {}
        self.trust_factors = {}
        self.trust_history = {}
        self.trust_policies = {}
        self.trust_transactions = {}
        
        # Initialize from configuration
        self._initialize_from_config()
        
        logger.info("Trust Score Agent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "trust_scoring": {
                "min_score": 0,
                "max_score": 100,
                "default_score": 50,
                "score_decay_rate": 0.01,  # Score decay per day
                "score_update_frequency": 3600  # Update frequency in seconds
            },
            "trust_factors": {
                "identity": {
                    "weight": 0.25,
                    "factors": {
                        "authentication_strength": 0.4,
                        "identity_verification": 0.3,
                        "credential_age": 0.2,
                        "provider_reputation": 0.1
                    }
                },
                "behavior": {
                    "weight": 0.25,
                    "factors": {
                        "access_patterns": 0.3,
                        "operation_history": 0.3,
                        "anomaly_score": 0.3,
                        "violation_history": 0.1
                    }
                },
                "context": {
                    "weight": 0.25,
                    "factors": {
                        "location": 0.3,
                        "device": 0.3,
                        "network": 0.2,
                        "time": 0.2
                    }
                },
                "reputation": {
                    "weight": 0.25,
                    "factors": {
                        "peer_ratings": 0.3,
                        "system_ratings": 0.3,
                        "external_ratings": 0.2,
                        "age_in_system": 0.2
                    }
                }
            },
            "trust_economy": {
                "enabled": True,
                "trust_as_currency": True,
                "initial_trust_balance": 100,
                "transaction_types": {
                    "transfer": True,
                    "stake": True,
                    "earn": True,
                    "burn": True
                }
            },
            "trust_history": {
                "enabled": True,
                "max_history_items": 100,
                "history_retention_days": 90
            },
            "trust_policies": {
                "enabled": True,
                "policy_enforcement": True,
                "default_policies": {
                    "minimum_access_score": 30,
                    "minimum_operation_score": 50,
                    "minimum_critical_operation_score": 70
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        return default_config
    
    def _initialize_from_config(self):
        """Initialize trust score agent components from configuration."""
        # Initialize trust factors if defined in config
        if "default_factors" in self.config.get("trust_factors", {}):
            for factor_id, factor_data in self.config["trust_factors"]["default_factors"].items():
                self.trust_factors[factor_id] = factor_data
        
        # Initialize trust policies if defined in config
        if "default_policies" in self.config.get("trust_policies", {}):
            for policy_id, policy_data in self.config["trust_policies"]["default_policies"].items():
                self.trust_policies[policy_id] = policy_data
    
    def register_entity(self, entity_id: str, entity_type: str, initial_score: float = None) -> Dict:
        """
        Register a new entity for trust scoring.
        
        Args:
            entity_id: Entity identifier
            entity_type: Entity type (e.g., user, system, capsule)
            initial_score: Initial trust score
            
        Returns:
            Dict containing entity trust information
        """
        # Use default score if not specified
        if initial_score is None:
            initial_score = self.config["trust_scoring"]["default_score"]
        
        # Validate score
        min_score = self.config["trust_scoring"]["min_score"]
        max_score = self.config["trust_scoring"]["max_score"]
        if initial_score < min_score or initial_score > max_score:
            raise ValueError(f"Trust score must be between {min_score} and {max_score}")
        
        # Check if entity already exists
        if entity_id in self.trust_scores:
            logger.warning(f"Entity {entity_id} already registered, updating score")
            self.trust_scores[entity_id]["score"] = initial_score
            self.trust_scores[entity_id]["updated_at"] = datetime.utcnow().isoformat()
            return self.trust_scores[entity_id]
        
        # Create entity trust record
        trust_record = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "score": initial_score,
            "factors": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_evaluated_at": datetime.utcnow().isoformat()
        }
        
        # Initialize trust economy if enabled
        if self.config["trust_economy"]["enabled"]:
            trust_record["trust_balance"] = self.config["trust_economy"]["initial_trust_balance"]
            trust_record["trust_transactions"] = []
        
        # Store trust record
        self.trust_scores[entity_id] = trust_record
        
        # Initialize trust history if enabled
        if self.config["trust_history"]["enabled"]:
            self.trust_history[entity_id] = [{
                "timestamp": datetime.utcnow().isoformat(),
                "score": initial_score,
                "reason": "initial_registration",
                "details": {}
            }]
        
        logger.info(f"Registered entity {entity_id} with initial trust score {initial_score}")
        
        return trust_record
    
    def get_trust_score(self, entity_id: str) -> Optional[Dict]:
        """
        Get trust score for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Dict containing entity trust information if found, None otherwise
        """
        # Check if entity exists
        if entity_id not in self.trust_scores:
            return None
        
        # Get trust record
        trust_record = self.trust_scores[entity_id]
        
        # Check if score needs updating due to decay
        last_evaluated = datetime.fromisoformat(trust_record["last_evaluated_at"])
        current_time = datetime.utcnow()
        days_since_evaluation = (current_time - last_evaluated).total_seconds() / 86400
        
        if days_since_evaluation > 0:
            # Apply score decay
            decay_rate = self.config["trust_scoring"]["score_decay_rate"]
            decay_amount = days_since_evaluation * decay_rate * trust_record["score"]
            
            # Update score
            trust_record["score"] = max(
                self.config["trust_scoring"]["min_score"],
                trust_record["score"] - decay_amount
            )
            
            # Update evaluation timestamp
            trust_record["last_evaluated_at"] = current_time.isoformat()
            
            # Add to history if enabled
            if self.config["trust_history"]["enabled"]:
                self._add_to_history(
                    entity_id,
                    trust_record["score"],
                    "automatic_decay",
                    {"days_since_evaluation": days_since_evaluation, "decay_amount": decay_amount}
                )
        
        return trust_record
    
    def update_trust_score(self, entity_id: str, adjustment: float, reason: str, details: Dict = None) -> Dict:
        """
        Update trust score for an entity.
        
        Args:
            entity_id: Entity identifier
            adjustment: Score adjustment (positive or negative)
            reason: Reason for adjustment
            details: Additional details about the adjustment
            
        Returns:
            Dict containing updated entity trust information
        """
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get current trust record
        trust_record = self.trust_scores[entity_id]
        
        # Calculate new score
        new_score = trust_record["score"] + adjustment
        
        # Ensure score is within bounds
        min_score = self.config["trust_scoring"]["min_score"]
        max_score = self.config["trust_scoring"]["max_score"]
        new_score = max(min_score, min(new_score, max_score))
        
        # Update score
        old_score = trust_record["score"]
        trust_record["score"] = new_score
        trust_record["updated_at"] = datetime.utcnow().isoformat()
        trust_record["last_evaluated_at"] = datetime.utcnow().isoformat()
        
        # Add to history if enabled
        if self.config["trust_history"]["enabled"]:
            self._add_to_history(
                entity_id,
                new_score,
                reason,
                details or {}
            )
        
        logger.info(f"Updated trust score for entity {entity_id} from {old_score} to {new_score} ({reason})")
        
        return trust_record
    
    def _add_to_history(self, entity_id: str, score: float, reason: str, details: Dict):
        """
        Add an entry to the trust history for an entity.
        
        Args:
            entity_id: Entity identifier
            score: Current trust score
            reason: Reason for the score change
            details: Additional details
        """
        # Initialize history if not exists
        if entity_id not in self.trust_history:
            self.trust_history[entity_id] = []
        
        # Create history entry
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "score": score,
            "reason": reason,
            "details": details
        }
        
        # Add to history
        self.trust_history[entity_id].append(history_entry)
        
        # Trim history if it exceeds max size
        max_history = self.config["trust_history"]["max_history_items"]
        if len(self.trust_history[entity_id]) > max_history:
            self.trust_history[entity_id] = self.trust_history[entity_id][-max_history:]
        
        # Remove old history entries
        retention_days = self.config["trust_history"]["history_retention_days"]
        if retention_days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            self.trust_history[entity_id] = [
                entry for entry in self.trust_history[entity_id]
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
            ]
    
    def get_trust_history(self, entity_id: str, limit: int = None) -> Optional[List[Dict]]:
        """
        Get trust history for an entity.
        
        Args:
            entity_id: Entity identifier
            limit: Maximum number of history entries to return
            
        Returns:
            List of trust history entries if found, None otherwise
        """
        # Check if history is enabled
        if not self.config["trust_history"]["enabled"]:
            return None
        
        # Check if entity exists
        if entity_id not in self.trust_history:
            return None
        
        # Get history
        history = self.trust_history[entity_id]
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            history = history[-limit:]
        
        return history
    
    def evaluate_trust_factors(self, entity_id: str, factor_values: Dict) -> Dict:
        """
        Evaluate trust factors for an entity and update trust score.
        
        Args:
            entity_id: Entity identifier
            factor_values: Dict containing factor values
            
        Returns:
            Dict containing updated entity trust information
        """
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get current trust record
        trust_record = self.trust_scores[entity_id]
        
        # Calculate factor scores
        factor_scores = {}
        total_score = 0
        total_weight = 0
        
        for category, category_config in self.config["trust_factors"].items():
            if isinstance(category_config, dict) and "weight" in category_config and "factors" in category_config:
                category_weight = category_config["weight"]
                category_score = 0
                category_factors = {}
                
                for factor, factor_weight in category_config["factors"].items():
                    if factor in factor_values:
                        factor_value = factor_values[factor]
                        factor_score = factor_value * 100  # Normalize to 0-100 scale
                        category_factors[factor] = factor_score
                        category_score += factor_score * factor_weight
                
                factor_scores[category] = {
                    "score": category_score,
                    "weight": category_weight,
                    "factors": category_factors
                }
                
                total_score += category_score * category_weight
                total_weight += category_weight
        
        # Normalize total score if weights don't sum to 1
        if total_weight > 0 and total_weight != 1:
            total_score = total_score / total_weight
        
        # Update trust record
        old_score = trust_record["score"]
        trust_record["score"] = total_score
        trust_record["factors"] = factor_scores
        trust_record["updated_at"] = datetime.utcnow().isoformat()
        trust_record["last_evaluated_at"] = datetime.utcnow().isoformat()
        
        # Add to history if enabled
        if self.config["trust_history"]["enabled"]:
            self._add_to_history(
                entity_id,
                total_score,
                "factor_evaluation",
                {"factors": factor_scores}
            )
        
        logger.info(f"Evaluated trust factors for entity {entity_id}, score updated from {old_score} to {total_score}")
        
        return trust_record
    
    def adjust_trust_for_context(self, entity_id: str, context: Dict) -> Dict:
        """
        Adjust trust score based on context.
        
        Args:
            entity_id: Entity identifier
            context: Context information
            
        Returns:
            Dict containing updated entity trust information
        """
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get current trust record
        trust_record = self.trust_scores[entity_id]
        
        # Calculate context adjustment
        adjustment = 0
        adjustment_factors = {}
        
        # Location context
        if "location" in context and "expected_location" in context:
            if context["location"] == context["expected_location"]:
                adjustment += 5
                adjustment_factors["location"] = 5
            else:
                adjustment -= 10
                adjustment_factors["location"] = -10
        
        # Device context
        if "device" in context and "expected_device" in context:
            if context["device"] == context["expected_device"]:
                adjustment += 5
                adjustment_factors["device"] = 5
            else:
                adjustment -= 5
                adjustment_factors["device"] = -5
        
        # Network context
        if "network" in context and "expected_network" in context:
            if context["network"] == context["expected_network"]:
                adjustment += 5
                adjustment_factors["network"] = 5
            else:
                adjustment -= 5
                adjustment_factors["network"] = -5
        
        # Time context
        if "time" in context:
            # Business hours might be more trusted
            hour = context["time"].hour if isinstance(context["time"], datetime) else int(context["time"])
            if 9 <= hour <= 17:  # Business hours
                adjustment += 2
                adjustment_factors["time"] = 2
            else:
                adjustment -= 2
                adjustment_factors["time"] = -2
        
        # Behavior context
        if "behavior" in context and "expected_behavior" in context:
            behavior_similarity = context.get("behavior_similarity", 0)
            if behavior_similarity >= 0.8:
                adjustment += 5
                adjustment_factors["behavior"] = 5
            elif behavior_similarity <= 0.3:
                adjustment -= 10
                adjustment_factors["behavior"] = -10
        
        # Apply adjustment
        if adjustment != 0:
            # Update score
            old_score = trust_record["score"]
            new_score = old_score + adjustment
            
            # Ensure score is within bounds
            min_score = self.config["trust_scoring"]["min_score"]
            max_score = self.config["trust_scoring"]["max_score"]
            new_score = max(min_score, min(new_score, max_score))
            
            trust_record["score"] = new_score
            trust_record["updated_at"] = datetime.utcnow().isoformat()
            trust_record["last_evaluated_at"] = datetime.utcnow().isoformat()
            
            # Add to history if enabled
            if self.config["trust_history"]["enabled"]:
                self._add_to_history(
                    entity_id,
                    new_score,
                    "context_adjustment",
                    {"context": context, "adjustment_factors": adjustment_factors}
                )
            
            logger.info(f"Adjusted trust score for entity {entity_id} from {old_score} to {new_score} based on context")
        
        return trust_record
    
    def check_trust_policy(self, entity_id: str, operation: str, required_score: float = None) -> Dict:
        """
        Check if an entity meets the trust policy for an operation.
        
        Args:
            entity_id: Entity identifier
            operation: Operation to check
            required_score: Required trust score (overrides policy)
            
        Returns:
            Dict containing policy check results
        """
        # Check if policies are enabled
        if not self.config["trust_policies"]["enabled"]:
            return {"allowed": True, "reason": "policies_disabled"}
        
        # Check if entity exists
        if entity_id not in self.trust_scores:
            return {"allowed": False, "reason": "entity_not_registered"}
        
        # Get current trust record
        trust_record = self.get_trust_score(entity_id)
        current_score = trust_record["score"]
        
        # Determine required score
        if required_score is None:
            # Check if operation has a specific policy
            if operation in self.trust_policies:
                required_score = self.trust_policies[operation]
            else:
                # Use default policies based on operation type
                default_policies = self.config["trust_policies"]["default_policies"]
                if "critical" in operation.lower():
                    required_score = default_policies.get("minimum_critical_operation_score", 70)
                elif "operation" in operation.lower():
                    required_score = default_policies.get("minimum_operation_score", 50)
                else:
                    required_score = default_policies.get("minimum_access_score", 30)
        
        # Check if score meets requirement
        allowed = current_score >= required_score
        
        # Create result
        result = {
            "allowed": allowed,
            "entity_id": entity_id,
            "operation": operation,
            "current_score": current_score,
            "required_score": required_score,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        if not allowed:
            result["reason"] = "insufficient_trust"
            result["score_deficit"] = required_score - current_score
        
        logger.info(f"Trust policy check for entity {entity_id}, operation {operation}: {'allowed' if allowed else 'denied'}")
        
        return result
    
    def register_trust_policy(self, operation: str, required_score: float) -> bool:
        """
        Register a trust policy for an operation.
        
        Args:
            operation: Operation identifier
            required_score: Required trust score
            
        Returns:
            True if registration successful, False otherwise
        """
        # Check if policies are enabled
        if not self.config["trust_policies"]["enabled"]:
            return False
        
        # Validate score
        min_score = self.config["trust_scoring"]["min_score"]
        max_score = self.config["trust_scoring"]["max_score"]
        if required_score < min_score or required_score > max_score:
            raise ValueError(f"Required score must be between {min_score} and {max_score}")
        
        # Register policy
        self.trust_policies[operation] = required_score
        
        logger.info(f"Registered trust policy for operation {operation} with required score {required_score}")
        
        return True
    
    def get_trust_policy(self, operation: str) -> Optional[float]:
        """
        Get trust policy for an operation.
        
        Args:
            operation: Operation identifier
            
        Returns:
            Required trust score if found, None otherwise
        """
        return self.trust_policies.get(operation)
    
    def delete_trust_policy(self, operation: str) -> bool:
        """
        Delete a trust policy.
        
        Args:
            operation: Operation identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        if operation in self.trust_policies:
            del self.trust_policies[operation]
            logger.info(f"Deleted trust policy for operation {operation}")
            return True
        return False
    
    def transfer_trust(self, source_id: str, target_id: str, amount: float, reason: str) -> Dict:
        """
        Transfer trust from one entity to another.
        
        Args:
            source_id: Source entity identifier
            target_id: Target entity identifier
            amount: Amount of trust to transfer
            reason: Reason for the transfer
            
        Returns:
            Dict containing transaction information
        """
        # Check if trust economy is enabled
        if not self.config["trust_economy"]["enabled"] or not self.config["trust_economy"]["trust_as_currency"]:
            raise ValueError("Trust economy or trust as currency is not enabled")
        
        # Check if entities exist
        if source_id not in self.trust_scores:
            raise ValueError(f"Source entity {source_id} not registered")
        
        if target_id not in self.trust_scores:
            raise ValueError(f"Target entity {target_id} not registered")
        
        # Check if source has enough trust balance
        source_record = self.trust_scores[source_id]
        if source_record.get("trust_balance", 0) < amount:
            raise ValueError(f"Source entity {source_id} has insufficient trust balance")
        
        # Get target record
        target_record = self.trust_scores[target_id]
        
        # Create transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "type": "transfer",
            "source_id": source_id,
            "target_id": target_id,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update balances
        source_record["trust_balance"] -= amount
        target_record["trust_balance"] += amount
        
        # Add transaction to records
        if "trust_transactions" not in source_record:
            source_record["trust_transactions"] = []
        source_record["trust_transactions"].append(transaction_id)
        
        if "trust_transactions" not in target_record:
            target_record["trust_transactions"] = []
        target_record["trust_transactions"].append(transaction_id)
        
        # Store transaction
        self.trust_transactions[transaction_id] = transaction
        
        logger.info(f"Transferred {amount} trust from entity {source_id} to entity {target_id}")
        
        return transaction
    
    def stake_trust(self, entity_id: str, amount: float, purpose: str, duration_days: int) -> Dict:
        """
        Stake trust for a specific purpose.
        
        Args:
            entity_id: Entity identifier
            amount: Amount of trust to stake
            purpose: Purpose of the stake
            duration_days: Duration of the stake in days
            
        Returns:
            Dict containing stake information
        """
        # Check if trust economy is enabled
        if not self.config["trust_economy"]["enabled"] or not self.config["trust_economy"]["transaction_types"]["stake"]:
            raise ValueError("Trust economy or trust staking is not enabled")
        
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Check if entity has enough trust balance
        entity_record = self.trust_scores[entity_id]
        if entity_record.get("trust_balance", 0) < amount:
            raise ValueError(f"Entity {entity_id} has insufficient trust balance")
        
        # Create stake
        stake_id = str(uuid.uuid4())
        expiration_date = datetime.utcnow() + timedelta(days=duration_days)
        
        stake = {
            "id": stake_id,
            "type": "stake",
            "entity_id": entity_id,
            "amount": amount,
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiration_date.isoformat(),
            "status": "active"
        }
        
        # Update balance
        entity_record["trust_balance"] -= amount
        
        # Add stake to entity record
        if "trust_stakes" not in entity_record:
            entity_record["trust_stakes"] = []
        entity_record["trust_stakes"].append(stake_id)
        
        # Store stake as a transaction
        self.trust_transactions[stake_id] = stake
        
        logger.info(f"Entity {entity_id} staked {amount} trust for {purpose} until {expiration_date.isoformat()}")
        
        return stake
    
    def release_stake(self, stake_id: str, success: bool) -> Dict:
        """
        Release a trust stake.
        
        Args:
            stake_id: Stake identifier
            success: Whether the stake purpose was successful
            
        Returns:
            Dict containing release information
        """
        # Check if stake exists
        if stake_id not in self.trust_transactions:
            raise ValueError(f"Stake {stake_id} not found")
        
        # Get stake
        stake = self.trust_transactions[stake_id]
        
        # Check if it's a stake
        if stake["type"] != "stake":
            raise ValueError(f"Transaction {stake_id} is not a stake")
        
        # Check if stake is active
        if stake["status"] != "active":
            raise ValueError(f"Stake {stake_id} is not active")
        
        # Get entity record
        entity_id = stake["entity_id"]
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        entity_record = self.trust_scores[entity_id]
        
        # Create release transaction
        release_id = str(uuid.uuid4())
        release = {
            "id": release_id,
            "type": "stake_release",
            "stake_id": stake_id,
            "entity_id": entity_id,
            "amount": stake["amount"],
            "success": success,
            "released_at": datetime.utcnow().isoformat()
        }
        
        # Update stake status
        stake["status"] = "released"
        stake["released_at"] = datetime.utcnow().isoformat()
        stake["success"] = success
        
        # Update entity balance
        return_amount = stake["amount"]
        if success:
            # Bonus for successful stake
            return_amount *= 1.1
        
        entity_record["trust_balance"] += return_amount
        
        # Add release to entity record
        if "trust_transactions" not in entity_record:
            entity_record["trust_transactions"] = []
        entity_record["trust_transactions"].append(release_id)
        
        # Store release
        self.trust_transactions[release_id] = release
        
        logger.info(f"Released stake {stake_id} for entity {entity_id} with {'success' if success else 'failure'}")
        
        return release
    
    def earn_trust(self, entity_id: str, amount: float, reason: str) -> Dict:
        """
        Earn trust for an entity.
        
        Args:
            entity_id: Entity identifier
            amount: Amount of trust to earn
            reason: Reason for earning trust
            
        Returns:
            Dict containing earning information
        """
        # Check if trust economy is enabled
        if not self.config["trust_economy"]["enabled"] or not self.config["trust_economy"]["transaction_types"]["earn"]:
            raise ValueError("Trust economy or trust earning is not enabled")
        
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get entity record
        entity_record = self.trust_scores[entity_id]
        
        # Create earning transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "type": "earn",
            "entity_id": entity_id,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update balance
        if "trust_balance" not in entity_record:
            entity_record["trust_balance"] = 0
        entity_record["trust_balance"] += amount
        
        # Add transaction to entity record
        if "trust_transactions" not in entity_record:
            entity_record["trust_transactions"] = []
        entity_record["trust_transactions"].append(transaction_id)
        
        # Store transaction
        self.trust_transactions[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} earned {amount} trust for {reason}")
        
        return transaction
    
    def burn_trust(self, entity_id: str, amount: float, reason: str) -> Dict:
        """
        Burn trust from an entity.
        
        Args:
            entity_id: Entity identifier
            amount: Amount of trust to burn
            reason: Reason for burning trust
            
        Returns:
            Dict containing burning information
        """
        # Check if trust economy is enabled
        if not self.config["trust_economy"]["enabled"] or not self.config["trust_economy"]["transaction_types"]["burn"]:
            raise ValueError("Trust economy or trust burning is not enabled")
        
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get entity record
        entity_record = self.trust_scores[entity_id]
        
        # Check if entity has enough trust balance
        if entity_record.get("trust_balance", 0) < amount:
            raise ValueError(f"Entity {entity_id} has insufficient trust balance")
        
        # Create burning transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "type": "burn",
            "entity_id": entity_id,
            "amount": amount,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update balance
        entity_record["trust_balance"] -= amount
        
        # Add transaction to entity record
        if "trust_transactions" not in entity_record:
            entity_record["trust_transactions"] = []
        entity_record["trust_transactions"].append(transaction_id)
        
        # Store transaction
        self.trust_transactions[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} burned {amount} trust for {reason}")
        
        return transaction
    
    def get_trust_transactions(self, entity_id: str, transaction_type: str = None, limit: int = None) -> List[Dict]:
        """
        Get trust transactions for an entity.
        
        Args:
            entity_id: Entity identifier
            transaction_type: Filter by transaction type
            limit: Maximum number of transactions to return
            
        Returns:
            List of trust transactions
        """
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get entity record
        entity_record = self.trust_scores[entity_id]
        
        # Get transaction IDs
        transaction_ids = entity_record.get("trust_transactions", [])
        
        # Get transactions
        transactions = []
        for transaction_id in transaction_ids:
            if transaction_id in self.trust_transactions:
                transaction = self.trust_transactions[transaction_id]
                
                # Filter by type if specified
                if transaction_type is None or transaction["type"] == transaction_type:
                    transactions.append(transaction)
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            transactions = transactions[:limit]
        
        return transactions
    
    def get_trust_balance(self, entity_id: str) -> float:
        """
        Get trust balance for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Trust balance
        """
        # Check if trust economy is enabled
        if not self.config["trust_economy"]["enabled"]:
            return 0
        
        # Check if entity exists
        if entity_id not in self.trust_scores:
            raise ValueError(f"Entity {entity_id} not registered")
        
        # Get entity record
        entity_record = self.trust_scores[entity_id]
        
        # Get balance
        return entity_record.get("trust_balance", 0)


# Example usage
if __name__ == "__main__":
    # Initialize Trust Score Agent
    agent = TrustScoreAgent()
    
    # Register entities
    user_record = agent.register_entity("user123", "user", 60)
    system_record = agent.register_entity("system456", "system", 80)
    capsule_record = agent.register_entity("capsule789", "capsule", 50)
    
    print(f"User trust score: {user_record['score']}")
    print(f"System trust score: {system_record['score']}")
    print(f"Capsule trust score: {capsule_record['score']}")
    
    # Update trust score
    updated_record = agent.update_trust_score("user123", 5, "successful_authentication")
    print(f"Updated user trust score: {updated_record['score']}")
    
    # Evaluate trust factors
    factor_values = {
        "authentication_strength": 0.8,
        "identity_verification": 0.9,
        "access_patterns": 0.7,
        "operation_history": 0.8,
        "location": 0.9,
        "device": 0.8,
        "network": 0.7,
        "time": 0.9,
        "peer_ratings": 0.8,
        "system_ratings": 0.7
    }
    
    evaluated_record = agent.evaluate_trust_factors("user123", factor_values)
    print(f"Evaluated user trust score: {evaluated_record['score']}")
    
    # Adjust trust for context
    context = {
        "location": "office",
        "expected_location": "office",
        "device": "laptop",
        "expected_device": "laptop",
        "network": "corporate",
        "expected_network": "corporate",
        "time": datetime.now()
    }
    
    adjusted_record = agent.adjust_trust_for_context("user123", context)
    print(f"Context-adjusted user trust score: {adjusted_record['score']}")
    
    # Check trust policy
    policy_check = agent.check_trust_policy("user123", "access_sensitive_data")
    print(f"Policy check result: {policy_check['allowed']}")
    
    # Trust economy operations
    if agent.config["trust_economy"]["enabled"]:
        # Earn trust
        earn_transaction = agent.earn_trust("user123", 20, "completed_training")
        print(f"User earned trust: {earn_transaction['amount']}")
        
        # Transfer trust
        transfer_transaction = agent.transfer_trust("user123", "capsule789", 10, "delegation")
        print(f"Trust transfer: {transfer_transaction['amount']} from {transfer_transaction['source_id']} to {transfer_transaction['target_id']}")
        
        # Stake trust
        stake = agent.stake_trust("user123", 15, "critical_operation", 7)
        print(f"User staked trust: {stake['amount']} for {stake['purpose']}")
        
        # Release stake
        release = agent.release_stake(stake["id"], True)
        print(f"Stake released: {release['amount']} with success={release['success']}")
        
        # Get trust balance
        balance = agent.get_trust_balance("user123")
        print(f"User trust balance: {balance}")
    
    # Get trust history
    history = agent.get_trust_history("user123")
    if history:
        print(f"Trust history entries: {len(history)}")
        for entry in history:
            print(f"  {entry['timestamp']}: {entry['score']} ({entry['reason']})")
