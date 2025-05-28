"""
Trust Evaluation Agent for the Security & Compliance Layer

This agent evaluates and manages trust scores for entities, systems, and operations
across the Industriverse platform. It provides dynamic trust assessment based on
behavior, compliance, and security posture.

Key capabilities:
1. Trust score calculation and management
2. Trust factor evaluation
3. Trust-based access decisions
4. Trust history tracking
5. Trust attestation generation

The Trust Evaluation Agent enables dynamic, context-aware trust decisions
throughout the Industriverse platform.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TrustEvaluationAgent")

class TrustEvaluationAgent:
    """
    Trust Evaluation Agent for calculating and managing trust scores
    across the Industriverse platform.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Trust Evaluation Agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        self.trust_factors = self._load_trust_factors()
        self.trust_scores = {}
        self.trust_history = {}
        self.attestations = {}
        
        self.logger.info("Trust Evaluation Agent initialized")
        
    def _load_config(self, config_path: str) -> Dict:
        """
        Load the agent configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing the configuration
        """
        default_config = {
            "default_trust_score": 50,  # 0-100 scale
            "trust_threshold": {
                "high": 80,
                "medium": 60,
                "low": 40
            },
            "score_decay_rate": 0.1,  # Score decay per day of inactivity
            "history_retention_days": 90,
            "attestation_validity_days": 7,
            "integration": {
                "identity_provider": True,
                "access_control": True,
                "data_security": True,
                "protocol_security": True,
                "policy_governance": True
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    
                self.logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {str(e)}")
                self.logger.info("Using default configuration")
        
        return default_config
    
    def _load_trust_factors(self) -> Dict:
        """
        Load trust factors.
        
        Returns:
            Dict containing trust factors
        """
        # In production, this would load from a database or configuration file
        # For now, we'll use a simple dictionary
        return {
            "identity": {
                "authentication_strength": {
                    "weight": 15,
                    "levels": {
                        "multi_factor": 100,
                        "single_factor_strong": 70,
                        "single_factor_weak": 40,
                        "none": 0
                    }
                },
                "identity_verification": {
                    "weight": 10,
                    "levels": {
                        "verified": 100,
                        "partial": 60,
                        "unverified": 20
                    }
                },
                "account_age": {
                    "weight": 5,
                    "levels": {
                        "years": 100,
                        "months": 70,
                        "weeks": 40,
                        "days": 20,
                        "hours": 10
                    }
                }
            },
            "behavior": {
                "activity_pattern": {
                    "weight": 10,
                    "levels": {
                        "normal": 100,
                        "unusual": 50,
                        "suspicious": 10
                    }
                },
                "policy_violations": {
                    "weight": 15,
                    "levels": {
                        "none": 100,
                        "minor": 60,
                        "major": 20,
                        "critical": 0
                    }
                },
                "resource_usage": {
                    "weight": 5,
                    "levels": {
                        "normal": 100,
                        "high": 70,
                        "excessive": 30
                    }
                }
            },
            "device": {
                "security_posture": {
                    "weight": 10,
                    "levels": {
                        "hardened": 100,
                        "standard": 70,
                        "vulnerable": 30,
                        "compromised": 0
                    }
                },
                "patch_level": {
                    "weight": 8,
                    "levels": {
                        "current": 100,
                        "recent": 80,
                        "outdated": 40,
                        "obsolete": 10
                    }
                },
                "known_device": {
                    "weight": 7,
                    "levels": {
                        "registered": 100,
                        "recognized": 70,
                        "unknown": 30
                    }
                }
            },
            "network": {
                "connection_security": {
                    "weight": 10,
                    "levels": {
                        "encrypted_verified": 100,
                        "encrypted": 80,
                        "unencrypted": 20
                    }
                },
                "network_location": {
                    "weight": 5,
                    "levels": {
                        "internal": 100,
                        "trusted": 80,
                        "external": 50,
                        "high_risk": 10
                    }
                }
            }
        }
    
    def evaluate_trust(self, entity_id: str, context: Dict) -> Dict:
        """
        Evaluate trust for an entity.
        
        Args:
            entity_id: Unique identifier for the entity
            context: Context information for trust evaluation
            
        Returns:
            Dict containing trust evaluation result
        """
        self.logger.info(f"Evaluating trust for entity {entity_id}")
        
        # Get current trust score or use default
        current_score = self.trust_scores.get(entity_id, self.config["default_trust_score"])
        
        # Calculate new trust score based on factors
        factor_scores = {}
        category_scores = {}
        total_weight = 0
        weighted_score_sum = 0
        
        for category, factors in self.trust_factors.items():
            category_score = 0
            category_weight = 0
            
            for factor_name, factor_config in factors.items():
                # Get factor value from context or use lowest level
                factor_value = context.get(category, {}).get(factor_name)
                factor_weight = factor_config["weight"]
                
                if factor_value in factor_config["levels"]:
                    factor_score = factor_config["levels"][factor_value]
                else:
                    # Use the lowest level if factor value is not provided
                    factor_score = min(factor_config["levels"].values())
                
                factor_scores[f"{category}.{factor_name}"] = factor_score
                category_score += factor_score * factor_weight
                category_weight += factor_weight
                
                total_weight += factor_weight
                weighted_score_sum += factor_score * factor_weight
            
            if category_weight > 0:
                category_scores[category] = category_score / category_weight
        
        # Calculate new trust score
        if total_weight > 0:
            new_score = weighted_score_sum / total_weight
        else:
            new_score = current_score
        
        # Apply score smoothing (don't change too drastically)
        smoothed_score = (current_score * 0.3) + (new_score * 0.7)
        
        # Ensure score is within bounds
        final_score = max(0, min(100, smoothed_score))
        
        # Determine trust level
        trust_level = self._get_trust_level(final_score)
        
        # Update trust score
        self.trust_scores[entity_id] = final_score
        
        # Record trust history
        self._record_trust_history(entity_id, final_score, factor_scores, context)
        
        # Generate trust attestation if needed
        attestation = None
        if context.get("generate_attestation", False):
            attestation = self.generate_attestation(entity_id, final_score, trust_level)
        
        return {
            "entity_id": entity_id,
            "trust_score": final_score,
            "trust_level": trust_level,
            "previous_score": current_score,
            "factor_scores": factor_scores,
            "category_scores": category_scores,
            "attestation": attestation,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_trust_level(self, score: float) -> str:
        """
        Get the trust level for a score.
        
        Args:
            score: Trust score
            
        Returns:
            Trust level (high, medium, low, minimal)
        """
        if score >= self.config["trust_threshold"]["high"]:
            return "high"
        elif score >= self.config["trust_threshold"]["medium"]:
            return "medium"
        elif score >= self.config["trust_threshold"]["low"]:
            return "low"
        else:
            return "minimal"
    
    def _record_trust_history(self, entity_id: str, score: float, factor_scores: Dict, context: Dict):
        """
        Record trust history for an entity.
        
        Args:
            entity_id: Entity ID
            score: Trust score
            factor_scores: Factor scores
            context: Evaluation context
        """
        if entity_id not in self.trust_history:
            self.trust_history[entity_id] = []
        
        # Add new history entry
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "factor_scores": factor_scores,
            "context_summary": {
                key: value for key, value in context.items()
                if key not in ["generate_attestation"]
            }
        }
        
        self.trust_history[entity_id].append(history_entry)
        
        # Trim history if it exceeds retention period
        retention_seconds = self.config["history_retention_days"] * 86400
        cutoff_time = datetime.now().timestamp() - retention_seconds
        
        self.trust_history[entity_id] = [
            entry for entry in self.trust_history[entity_id]
            if datetime.fromisoformat(entry["timestamp"]).timestamp() >= cutoff_time
        ]
    
    def generate_attestation(self, entity_id: str, score: float, trust_level: str) -> Dict:
        """
        Generate a trust attestation.
        
        Args:
            entity_id: Entity ID
            score: Trust score
            trust_level: Trust level
            
        Returns:
            Dict containing the attestation
        """
        # Generate attestation ID
        attestation_id = self._generate_attestation_id(entity_id)
        
        # Create attestation
        attestation = {
            "id": attestation_id,
            "entity_id": entity_id,
            "trust_score": score,
            "trust_level": trust_level,
            "issuer": "trust_evaluation_agent",
            "issued_at": datetime.now().isoformat(),
            "expires_at": (datetime.now().timestamp() + (self.config["attestation_validity_days"] * 86400)),
            "signature": self._generate_attestation_signature(entity_id, score, trust_level)
        }
        
        # Store attestation
        self.attestations[attestation_id] = attestation
        
        return attestation
    
    def _generate_attestation_id(self, entity_id: str) -> str:
        """
        Generate a unique attestation ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Unique attestation ID
        """
        timestamp = datetime.now().isoformat()
        random_value = random.randint(1000, 9999)
        hash_input = f"{entity_id}-{timestamp}-{random_value}"
        return f"att-{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"
    
    def _generate_attestation_signature(self, entity_id: str, score: float, trust_level: str) -> str:
        """
        Generate a signature for an attestation.
        
        Args:
            entity_id: Entity ID
            score: Trust score
            trust_level: Trust level
            
        Returns:
            Attestation signature
        """
        # In a real implementation, this would use cryptographic signing
        # For now, we'll just generate a hash
        timestamp = datetime.now().isoformat()
        hash_input = f"{entity_id}-{score}-{trust_level}-{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def verify_attestation(self, attestation_id: str) -> Dict:
        """
        Verify a trust attestation.
        
        Args:
            attestation_id: Attestation ID
            
        Returns:
            Dict containing verification result
        """
        if attestation_id not in self.attestations:
            return {
                "valid": False,
                "reason": "Unknown attestation ID",
                "timestamp": datetime.now().isoformat()
            }
        
        attestation = self.attestations[attestation_id]
        
        # Check if attestation has expired
        if attestation["expires_at"] < datetime.now().timestamp():
            return {
                "valid": False,
                "reason": "Attestation has expired",
                "attestation": attestation,
                "timestamp": datetime.now().isoformat()
            }
        
        # In a real implementation, this would verify the cryptographic signature
        # For now, we'll just assume it's valid
        
        return {
            "valid": True,
            "attestation": attestation,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_trust_score(self, entity_id: str) -> Dict:
        """
        Get the current trust score for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Dict containing the trust score
        """
        if entity_id not in self.trust_scores:
            return {
                "entity_id": entity_id,
                "trust_score": self.config["default_trust_score"],
                "trust_level": self._get_trust_level(self.config["default_trust_score"]),
                "message": "No trust score available, using default",
                "timestamp": datetime.now().isoformat()
            }
        
        score = self.trust_scores[entity_id]
        
        return {
            "entity_id": entity_id,
            "trust_score": score,
            "trust_level": self._get_trust_level(score),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_trust_history(self, entity_id: str, limit: int = None) -> Dict:
        """
        Get the trust history for an entity.
        
        Args:
            entity_id: Entity ID
            limit: Maximum number of history entries to return
            
        Returns:
            Dict containing the trust history
        """
        if entity_id not in self.trust_history:
            return {
                "entity_id": entity_id,
                "history": [],
                "message": "No trust history available",
                "timestamp": datetime.now().isoformat()
            }
        
        history = self.trust_history[entity_id]
        
        # Sort by timestamp (newest first)
        sorted_history = sorted(
            history,
            key=lambda h: datetime.fromisoformat(h["timestamp"]).timestamp(),
            reverse=True
        )
        
        if limit:
            sorted_history = sorted_history[:limit]
        
        return {
            "entity_id": entity_id,
            "history": sorted_history,
            "timestamp": datetime.now().isoformat()
        }
    
    def adjust_trust_score(self, entity_id: str, adjustment: float, reason: str) -> Dict:
        """
        Manually adjust the trust score for an entity.
        
        Args:
            entity_id: Entity ID
            adjustment: Score adjustment (positive or negative)
            reason: Reason for adjustment
            
        Returns:
            Dict containing the adjustment result
        """
        current_score = self.trust_scores.get(entity_id, self.config["default_trust_score"])
        
        # Apply adjustment
        new_score = current_score + adjustment
        
        # Ensure score is within bounds
        new_score = max(0, min(100, new_score))
        
        # Update trust score
        self.trust_scores[entity_id] = new_score
        
        # Record adjustment in history
        if entity_id not in self.trust_history:
            self.trust_history[entity_id] = []
        
        self.trust_history[entity_id].append({
            "timestamp": datetime.now().isoformat(),
            "score": new_score,
            "adjustment": adjustment,
            "reason": reason,
            "previous_score": current_score
        })
        
        return {
            "entity_id": entity_id,
            "previous_score": current_score,
            "adjustment": adjustment,
            "new_score": new_score,
            "trust_level": self._get_trust_level(new_score),
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_trust_for_access(self, entity_id: str, resource: Dict, required_level: str = None) -> Dict:
        """
        Check if an entity has sufficient trust for accessing a resource.
        
        Args:
            entity_id: Entity ID
            resource: Resource information
            required_level: Required trust level (if not specified, use resource default)
            
        Returns:
            Dict containing the access decision
        """
        # Get current trust score and level
        trust_info = self.get_trust_score(entity_id)
        trust_score = trust_info["trust_score"]
        trust_level = trust_info["trust_level"]
        
        # Determine required trust level
        if not required_level:
            required_level = resource.get("required_trust_level", "medium")
        
        # Get threshold for required level
        if required_level not in self.config["trust_threshold"]:
            return {
                "access_granted": False,
                "reason": f"Invalid required trust level: {required_level}",
                "entity_id": entity_id,
                "resource": resource,
                "timestamp": datetime.now().isoformat()
            }
        
        required_threshold = self.config["trust_threshold"][required_level]
        
        # Make access decision
        access_granted = trust_score >= required_threshold
        
        return {
            "access_granted": access_granted,
            "entity_id": entity_id,
            "resource": resource,
            "trust_score": trust_score,
            "trust_level": trust_level,
            "required_level": required_level,
            "required_threshold": required_threshold,
            "timestamp": datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    agent = TrustEvaluationAgent()
    
    # Evaluate trust for an entity
    context = {
        "identity": {
            "authentication_strength": "multi_factor",
            "identity_verification": "verified",
            "account_age": "months"
        },
        "behavior": {
            "activity_pattern": "normal",
            "policy_violations": "none",
            "resource_usage": "normal"
        },
        "device": {
            "security_posture": "standard",
            "patch_level": "current",
            "known_device": "registered"
        },
        "network": {
            "connection_security": "encrypted_verified",
            "network_location": "internal"
        },
        "generate_attestation": True
    }
    
    result = agent.evaluate_trust("user-123", context)
    print(f"Trust evaluation result: {result}")
    
    # Get trust score
    score = agent.get_trust_score("user-123")
    print(f"Trust score: {score}")
    
    # Check trust for access
    resource = {
        "id": "resource-456",
        "name": "Sensitive Data",
        "required_trust_level": "high"
    }
    
    access = agent.check_trust_for_access("user-123", resource)
    print(f"Access decision: {access}")
    
    # Adjust trust score
    adjustment = agent.adjust_trust_score("user-123", -10, "Suspicious activity detected")
    print(f"Trust adjustment: {adjustment}")
    
    # Get trust history
    history = agent.get_trust_history("user-123")
    print(f"Trust history: {history}")
    
    # Verify attestation
    if "attestation" in result and result["attestation"]:
        verification = agent.verify_attestation(result["attestation"]["id"])
        print(f"Attestation verification: {verification}")
