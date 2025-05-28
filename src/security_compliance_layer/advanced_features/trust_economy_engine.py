"""
Trust Economy Engine Module for the Security & Compliance Layer

This module implements the Trust Economy Engine, which makes trust a protocol-native, 
computable resource within the Industriverse ecosystem. It enables trust to be earned, 
spent, transferred, and verified across the platform.

Key features:
1. Trust as a spendable resource with balance management
2. Trust transfer, staking, and verification
3. Trust-based transaction validation
4. Trust economy analytics and reporting

Dependencies:
- identity_trust.trust_score_agent
- identity_trust.zk_attestation_agent
- core.protocol_security.protocol_ethics_engine
- advanced_features.zk_native_identity_mesh

Author: Industriverse Security Team
"""

import logging
import uuid
import time
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class TrustTransactionType(Enum):
    """Enumeration of trust transaction types"""
    EARN = "earn"
    SPEND = "spend"
    TRANSFER = "transfer"
    STAKE = "stake"
    UNSTAKE = "unstake"
    BURN = "burn"
    MINT = "mint"
    VERIFY = "verify"

class TrustTransactionStatus(Enum):
    """Enumeration of trust transaction statuses"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    VERIFIED = "verified"

class TrustEconomyEngine:
    """
    Trust Economy Engine for the Security & Compliance Layer
    
    This class implements the Trust Economy Engine, which makes trust a protocol-native,
    computable resource within the Industriverse ecosystem.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Trust Economy Engine
        
        Args:
            config: Configuration dictionary for the Trust Economy Engine
        """
        self.config = config or {}
        self.trust_ledger = {}  # Maps entity_id to trust balance
        self.transaction_history = {}  # Maps transaction_id to transaction details
        self.staking_registry = {}  # Maps stake_id to staking details
        self.verification_registry = {}  # Maps verification_id to verification details
        self.trust_policies = self.config.get("trust_policies", {})
        self.min_trust_threshold = self.config.get("min_trust_threshold", 10)
        self.max_trust_cap = self.config.get("max_trust_cap", 1000)
        self.trust_decay_rate = self.config.get("trust_decay_rate", 0.01)  # Daily decay rate
        self.trust_score_agent = None  # Will be set by dependency injection
        self.zk_attestation_agent = None  # Will be set by dependency injection
        
        logger.info("Trust Economy Engine initialized")
    
    def set_dependencies(self, trust_score_agent=None, zk_attestation_agent=None):
        """
        Set dependencies for the Trust Economy Engine
        
        Args:
            trust_score_agent: Trust Score Agent instance
            zk_attestation_agent: ZK Attestation Agent instance
        """
        self.trust_score_agent = trust_score_agent
        self.zk_attestation_agent = zk_attestation_agent
        logger.info("Trust Economy Engine dependencies set")
    
    def get_trust_balance(self, entity_id: str) -> float:
        """
        Get the current trust balance for an entity
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            Current trust balance
        """
        if entity_id not in self.trust_ledger:
            # Initialize with default trust balance
            self.trust_ledger[entity_id] = self.config.get("initial_trust_balance", 50)
        
        return self.trust_ledger[entity_id]
    
    def earn_trust(self, entity_id: str, amount: float, reason: str, 
                  evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Earn trust for an entity
        
        Args:
            entity_id: Unique identifier for the entity
            amount: Amount of trust to earn
            reason: Reason for earning trust
            evidence: Evidence supporting the trust earning
            
        Returns:
            Transaction details
        """
        if amount <= 0:
            raise ValueError("Trust earning amount must be positive")
        
        # Verify evidence if provided
        if evidence and self.zk_attestation_agent:
            verification_result = self.zk_attestation_agent.verify_evidence(evidence)
            if not verification_result["verified"]:
                raise ValueError(f"Evidence verification failed: {verification_result['reason']}")
        
        # Apply trust earning policies
        adjusted_amount = self._apply_trust_policies(entity_id, amount, TrustTransactionType.EARN)
        
        # Update trust balance with cap
        current_balance = self.get_trust_balance(entity_id)
        new_balance = min(current_balance + adjusted_amount, self.max_trust_cap)
        self.trust_ledger[entity_id] = new_balance
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "type": TrustTransactionType.EARN.value,
            "amount": adjusted_amount,
            "reason": reason,
            "evidence_hash": self._hash_evidence(evidence) if evidence else None,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "timestamp": datetime.utcnow().isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} earned {adjusted_amount} trust for {reason}")
        return transaction
    
    def spend_trust(self, entity_id: str, amount: float, reason: str, 
                   operation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Spend trust for an entity
        
        Args:
            entity_id: Unique identifier for the entity
            amount: Amount of trust to spend
            reason: Reason for spending trust
            operation_context: Context of the operation requiring trust
            
        Returns:
            Transaction details
        """
        if amount <= 0:
            raise ValueError("Trust spending amount must be positive")
        
        current_balance = self.get_trust_balance(entity_id)
        if current_balance < amount:
            raise ValueError(f"Insufficient trust balance: {current_balance} < {amount}")
        
        # Apply trust spending policies
        adjusted_amount = self._apply_trust_policies(entity_id, amount, TrustTransactionType.SPEND)
        
        # Update trust balance
        new_balance = current_balance - adjusted_amount
        self.trust_ledger[entity_id] = new_balance
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "type": TrustTransactionType.SPEND.value,
            "amount": adjusted_amount,
            "reason": reason,
            "operation_context": operation_context,
            "previous_balance": current_balance,
            "new_balance": new_balance,
            "timestamp": datetime.utcnow().isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} spent {adjusted_amount} trust for {reason}")
        return transaction
    
    def transfer_trust(self, from_entity_id: str, to_entity_id: str, amount: float, 
                      reason: str) -> Dict[str, Any]:
        """
        Transfer trust from one entity to another
        
        Args:
            from_entity_id: Unique identifier for the source entity
            to_entity_id: Unique identifier for the destination entity
            amount: Amount of trust to transfer
            reason: Reason for transferring trust
            
        Returns:
            Transaction details
        """
        if amount <= 0:
            raise ValueError("Trust transfer amount must be positive")
        
        if from_entity_id == to_entity_id:
            raise ValueError("Cannot transfer trust to self")
        
        from_balance = self.get_trust_balance(from_entity_id)
        if from_balance < amount:
            raise ValueError(f"Insufficient trust balance: {from_balance} < {amount}")
        
        # Apply trust transfer policies
        adjusted_amount = self._apply_trust_policies(from_entity_id, amount, TrustTransactionType.TRANSFER)
        
        # Apply transfer fee if configured
        transfer_fee = self.config.get("transfer_fee_percentage", 0) * adjusted_amount
        transfer_amount = adjusted_amount - transfer_fee
        
        # Update trust balances
        self.trust_ledger[from_entity_id] = from_balance - adjusted_amount
        to_balance = self.get_trust_balance(to_entity_id)
        self.trust_ledger[to_entity_id] = min(to_balance + transfer_amount, self.max_trust_cap)
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "from_entity_id": from_entity_id,
            "to_entity_id": to_entity_id,
            "type": TrustTransactionType.TRANSFER.value,
            "amount": adjusted_amount,
            "transfer_amount": transfer_amount,
            "transfer_fee": transfer_fee,
            "reason": reason,
            "from_previous_balance": from_balance,
            "from_new_balance": self.trust_ledger[from_entity_id],
            "to_previous_balance": to_balance,
            "to_new_balance": self.trust_ledger[to_entity_id],
            "timestamp": datetime.utcnow().isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Entity {from_entity_id} transferred {transfer_amount} trust to {to_entity_id} for {reason}")
        return transaction
    
    def stake_trust(self, entity_id: str, amount: float, purpose: str, 
                   duration_days: int, conditions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Stake trust for a specific purpose
        
        Args:
            entity_id: Unique identifier for the entity
            amount: Amount of trust to stake
            purpose: Purpose of staking
            duration_days: Duration of staking in days
            conditions: Conditions for stake release
            
        Returns:
            Staking details
        """
        if amount <= 0:
            raise ValueError("Trust staking amount must be positive")
        
        current_balance = self.get_trust_balance(entity_id)
        if current_balance < amount:
            raise ValueError(f"Insufficient trust balance: {current_balance} < {amount}")
        
        # Apply trust staking policies
        adjusted_amount = self._apply_trust_policies(entity_id, amount, TrustTransactionType.STAKE)
        
        # Update trust balance
        self.trust_ledger[entity_id] = current_balance - adjusted_amount
        
        # Record stake
        stake_id = str(uuid.uuid4())
        expiration_date = datetime.utcnow() + timedelta(days=duration_days)
        stake = {
            "stake_id": stake_id,
            "entity_id": entity_id,
            "amount": adjusted_amount,
            "purpose": purpose,
            "conditions": conditions,
            "creation_date": datetime.utcnow().isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "status": "active"
        }
        self.staking_registry[stake_id] = stake
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "type": TrustTransactionType.STAKE.value,
            "amount": adjusted_amount,
            "purpose": purpose,
            "stake_id": stake_id,
            "previous_balance": current_balance,
            "new_balance": self.trust_ledger[entity_id],
            "timestamp": datetime.utcnow().isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} staked {adjusted_amount} trust for {purpose}")
        return stake
    
    def unstake_trust(self, stake_id: str, verification_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Unstake previously staked trust
        
        Args:
            stake_id: Unique identifier for the stake
            verification_data: Data for verifying stake conditions
            
        Returns:
            Unstaking details
        """
        if stake_id not in self.staking_registry:
            raise ValueError(f"Stake not found: {stake_id}")
        
        stake = self.staking_registry[stake_id]
        if stake["status"] != "active":
            raise ValueError(f"Stake is not active: {stake['status']}")
        
        entity_id = stake["entity_id"]
        amount = stake["amount"]
        
        # Verify conditions if provided
        if stake["conditions"] and verification_data:
            conditions_met = self._verify_stake_conditions(stake["conditions"], verification_data)
            if not conditions_met:
                raise ValueError("Stake conditions not met")
        
        # Check expiration
        current_time = datetime.utcnow()
        expiration_date = datetime.fromisoformat(stake["expiration_date"])
        if current_time < expiration_date and not verification_data:
            raise ValueError(f"Stake has not expired yet: {stake['expiration_date']}")
        
        # Update trust balance
        current_balance = self.get_trust_balance(entity_id)
        self.trust_ledger[entity_id] = current_balance + amount
        
        # Update stake status
        stake["status"] = "released"
        stake["release_date"] = current_time.isoformat()
        stake["verification_data_hash"] = self._hash_evidence(verification_data) if verification_data else None
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "type": TrustTransactionType.UNSTAKE.value,
            "amount": amount,
            "stake_id": stake_id,
            "previous_balance": current_balance,
            "new_balance": self.trust_ledger[entity_id],
            "timestamp": current_time.isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Entity {entity_id} unstaked {amount} trust from stake {stake_id}")
        return {
            "transaction_id": transaction_id,
            "stake_id": stake_id,
            "entity_id": entity_id,
            "amount": amount,
            "previous_balance": current_balance,
            "new_balance": self.trust_ledger[entity_id],
            "status": "released"
        }
    
    def verify_trust(self, entity_id: str, required_trust: float, 
                    operation: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Verify if an entity has sufficient trust for an operation
        
        Args:
            entity_id: Unique identifier for the entity
            required_trust: Required trust amount
            operation: Operation requiring trust
            context: Operation context
            
        Returns:
            Verification result
        """
        if required_trust <= 0:
            raise ValueError("Required trust must be positive")
        
        current_balance = self.get_trust_balance(entity_id)
        has_sufficient_trust = current_balance >= required_trust
        
        # Apply operation-specific trust policies
        operation_trust_requirement = self._get_operation_trust_requirement(operation, context)
        if operation_trust_requirement > required_trust:
            required_trust = operation_trust_requirement
            has_sufficient_trust = current_balance >= required_trust
        
        # Record verification
        verification_id = str(uuid.uuid4())
        verification = {
            "verification_id": verification_id,
            "entity_id": entity_id,
            "required_trust": required_trust,
            "current_trust": current_balance,
            "operation": operation,
            "context_hash": self._hash_evidence(context) if context else None,
            "has_sufficient_trust": has_sufficient_trust,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.verification_registry[verification_id] = verification
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        transaction = {
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "type": TrustTransactionType.VERIFY.value,
            "required_trust": required_trust,
            "current_trust": current_balance,
            "operation": operation,
            "verification_id": verification_id,
            "result": has_sufficient_trust,
            "timestamp": datetime.utcnow().isoformat(),
            "status": TrustTransactionStatus.COMPLETED.value
        }
        self.transaction_history[transaction_id] = transaction
        
        logger.info(f"Trust verification for entity {entity_id}: required={required_trust}, current={current_balance}, result={has_sufficient_trust}")
        return {
            "verification_id": verification_id,
            "transaction_id": transaction_id,
            "entity_id": entity_id,
            "required_trust": required_trust,
            "current_trust": current_balance,
            "has_sufficient_trust": has_sufficient_trust,
            "operation": operation
        }
    
    def get_transaction_history(self, entity_id: str = None, 
                               transaction_types: List[str] = None,
                               start_time: str = None,
                               end_time: str = None,
                               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get transaction history for an entity
        
        Args:
            entity_id: Unique identifier for the entity (optional)
            transaction_types: List of transaction types to filter (optional)
            start_time: Start time for filtering (ISO format, optional)
            end_time: End time for filtering (ISO format, optional)
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction details
        """
        transactions = list(self.transaction_history.values())
        
        # Apply filters
        if entity_id:
            transactions = [t for t in transactions if t.get("entity_id") == entity_id or 
                           t.get("from_entity_id") == entity_id or 
                           t.get("to_entity_id") == entity_id]
        
        if transaction_types:
            transactions = [t for t in transactions if t.get("type") in transaction_types]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            transactions = [t for t in transactions if datetime.fromisoformat(t.get("timestamp")) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            transactions = [t for t in transactions if datetime.fromisoformat(t.get("timestamp")) <= end_dt]
        
        # Sort by timestamp (newest first)
        transactions.sort(key=lambda t: t.get("timestamp"), reverse=True)
        
        # Apply limit
        return transactions[:limit]
    
    def get_trust_analytics(self, entity_id: str = None) -> Dict[str, Any]:
        """
        Get trust analytics for the entire system or a specific entity
        
        Args:
            entity_id: Unique identifier for the entity (optional)
            
        Returns:
            Trust analytics data
        """
        if entity_id:
            return self._get_entity_trust_analytics(entity_id)
        
        # System-wide analytics
        total_entities = len(self.trust_ledger)
        total_trust = sum(self.trust_ledger.values())
        avg_trust = total_trust / total_entities if total_entities > 0 else 0
        
        # Trust distribution
        trust_distribution = {
            "low": len([v for v in self.trust_ledger.values() if v < self.min_trust_threshold]),
            "medium": len([v for v in self.trust_ledger.values() if self.min_trust_threshold <= v < self.max_trust_cap * 0.7]),
            "high": len([v for v in self.trust_ledger.values() if v >= self.max_trust_cap * 0.7])
        }
        
        # Transaction analytics
        transactions = list(self.transaction_history.values())
        transaction_count_by_type = {}
        for t_type in TrustTransactionType:
            transaction_count_by_type[t_type.value] = len([t for t in transactions if t.get("type") == t_type.value])
        
        return {
            "total_entities": total_entities,
            "total_trust": total_trust,
            "average_trust": avg_trust,
            "trust_distribution": trust_distribution,
            "transaction_count_by_type": transaction_count_by_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_entity_trust_analytics(self, entity_id: str) -> Dict[str, Any]:
        """
        Get trust analytics for a specific entity
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            Entity trust analytics data
        """
        if entity_id not in self.trust_ledger:
            raise ValueError(f"Entity not found: {entity_id}")
        
        current_balance = self.trust_ledger[entity_id]
        
        # Transaction history
        transactions = self.get_transaction_history(entity_id=entity_id, limit=1000)
        
        # Trust earned/spent
        trust_earned = sum([t.get("amount", 0) for t in transactions if t.get("type") == TrustTransactionType.EARN.value])
        trust_spent = sum([t.get("amount", 0) for t in transactions if t.get("type") == TrustTransactionType.SPEND.value])
        
        # Trust transferred
        trust_transferred_out = sum([t.get("amount", 0) for t in transactions if t.get("type") == TrustTransactionType.TRANSFER.value and 
                                    t.get("from_entity_id") == entity_id])
        trust_transferred_in = sum([t.get("transfer_amount", 0) for t in transactions if t.get("type") == TrustTransactionType.TRANSFER.value and 
                                   t.get("to_entity_id") == entity_id])
        
        # Trust staked
        active_stakes = [s for s in self.staking_registry.values() if s.get("entity_id") == entity_id and s.get("status") == "active"]
        total_staked = sum([s.get("amount", 0) for s in active_stakes])
        
        # Trust verifications
        verifications = [v for v in self.verification_registry.values() if v.get("entity_id") == entity_id]
        successful_verifications = len([v for v in verifications if v.get("has_sufficient_trust")])
        failed_verifications = len(verifications) - successful_verifications
        
        return {
            "entity_id": entity_id,
            "current_balance": current_balance,
            "trust_earned": trust_earned,
            "trust_spent": trust_spent,
            "trust_transferred_out": trust_transferred_out,
            "trust_transferred_in": trust_transferred_in,
            "total_staked": total_staked,
            "active_stakes_count": len(active_stakes),
            "verification_success_rate": successful_verifications / len(verifications) if verifications else 0,
            "successful_verifications": successful_verifications,
            "failed_verifications": failed_verifications,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _apply_trust_policies(self, entity_id: str, amount: float, 
                             transaction_type: TrustTransactionType) -> float:
        """
        Apply trust policies to adjust transaction amount
        
        Args:
            entity_id: Unique identifier for the entity
            amount: Original amount
            transaction_type: Type of transaction
            
        Returns:
            Adjusted amount
        """
        adjusted_amount = amount
        
        # Apply entity-specific policies
        entity_policies = self.trust_policies.get("entity", {}).get(entity_id, {})
        if entity_policies:
            multiplier = entity_policies.get(f"{transaction_type.value}_multiplier", 1.0)
            adjusted_amount *= multiplier
        
        # Apply global transaction type policies
        global_policies = self.trust_policies.get("global", {})
        if global_policies:
            multiplier = global_policies.get(f"{transaction_type.value}_multiplier", 1.0)
            adjusted_amount *= multiplier
        
        return adjusted_amount
    
    def _get_operation_trust_requirement(self, operation: str, context: Dict[str, Any] = None) -> float:
        """
        Get trust requirement for a specific operation
        
        Args:
            operation: Operation name
            context: Operation context
            
        Returns:
            Required trust amount
        """
        operation_policies = self.trust_policies.get("operations", {})
        base_requirement = operation_policies.get(operation, {}).get("base_requirement", 0)
        
        # Apply context-specific adjustments
        if context and "risk_level" in context:
            risk_multipliers = operation_policies.get(operation, {}).get("risk_multipliers", {})
            risk_level = context["risk_level"]
            multiplier = risk_multipliers.get(risk_level, 1.0)
            base_requirement *= multiplier
        
        return base_requirement
    
    def _verify_stake_conditions(self, conditions: Dict[str, Any], 
                                verification_data: Dict[str, Any]) -> bool:
        """
        Verify if stake conditions are met
        
        Args:
            conditions: Stake conditions
            verification_data: Verification data
            
        Returns:
            True if conditions are met, False otherwise
        """
        for condition_key, condition_value in conditions.items():
            if condition_key not in verification_data:
                return False
            
            if isinstance(condition_value, dict) and "operator" in condition_value:
                operator = condition_value["operator"]
                value = condition_value["value"]
                
                if operator == "eq" and verification_data[condition_key] != value:
                    return False
                elif operator == "gt" and verification_data[condition_key] <= value:
                    return False
                elif operator == "lt" and verification_data[condition_key] >= value:
                    return False
                elif operator == "gte" and verification_data[condition_key] < value:
                    return False
                elif operator == "lte" and verification_data[condition_key] > value:
                    return False
            elif verification_data[condition_key] != condition_value:
                return False
        
        return True
    
    def _hash_evidence(self, evidence: Dict[str, Any]) -> str:
        """
        Create a hash of evidence data
        
        Args:
            evidence: Evidence data
            
        Returns:
            Hash of evidence
        """
        if not evidence:
            return None
        
        # Simple hash implementation - in production, use a cryptographic hash function
        evidence_str = json.dumps(evidence, sort_keys=True)
        return str(hash(evidence_str))
    
    def apply_trust_decay(self):
        """
        Apply trust decay to all entities
        
        This method applies the configured trust decay rate to all entity trust balances.
        It should be called periodically (e.g., daily) to simulate trust decay over time.
        """
        for entity_id in self.trust_ledger:
            current_balance = self.trust_ledger[entity_id]
            decay_amount = current_balance * self.trust_decay_rate
            new_balance = max(current_balance - decay_amount, self.min_trust_threshold)
            self.trust_ledger[entity_id] = new_balance
        
        logger.info(f"Applied trust decay with rate {self.trust_decay_rate} to all entities")
    
    def export_trust_ledger(self) -> Dict[str, float]:
        """
        Export the current trust ledger
        
        Returns:
            Copy of the current trust ledger
        """
        return self.trust_ledger.copy()
    
    def import_trust_ledger(self, ledger: Dict[str, float]):
        """
        Import a trust ledger
        
        Args:
            ledger: Trust ledger to import
        """
        self.trust_ledger = ledger.copy()
        logger.info(f"Imported trust ledger with {len(ledger)} entities")
