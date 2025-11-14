"""
Proof of Energy (PoE) Validator - Phase 5 EIL

Validates that ACE predictions match observed reality through tri-check validation:
1. Energy Conservation Check: ΔE within tolerance
2. Entropy Coherence Check: Entropy monotonicity maintained
3. Spectral Similarity Check: Power spectrum correlation

Integrates with:
- Phase 2 ProofEconomy smart contracts (PFT minting)
- Phase 0 Shadow Twin Consensus (98.3% PCT)
- Phase 5 EIL regime intelligence

PoE = cryptographic proof that thermodynamic predictions are physically valid.
"""

import numpy as np
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from phase5.validation.metrics import (
    compute_energy_fidelity,
    compute_entropy_coherence,
    compute_spectral_similarity
)


@dataclass
class ProofRecord:
    """Proof of Energy validation record"""
    proof_id: str
    domain: str
    timestamp: float

    # Predictions
    predicted_energy_map: np.ndarray
    predicted_hash: str

    # Observations (ground truth)
    observed_energy_map: Optional[np.ndarray] = None
    observed_hash: Optional[str] = None

    # Validation results (tri-check)
    energy_check_passed: bool = False
    entropy_check_passed: bool = False
    spectral_check_passed: bool = False
    overall_passed: bool = False

    # Metrics
    energy_fidelity: float = 0.0
    entropy_coherence: float = 0.0
    spectral_similarity: float = 0.0

    # Regime context
    regime: str = "unknown"
    regime_approved: bool = False

    # Blockchain integration
    pft_minted: bool = False
    pft_amount: float = 0.0
    contract_tx_hash: Optional[str] = None

    # Metadata
    validator_id: str = "default"
    validation_time: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ProofValidationResult:
    """Result of proof validation"""
    passed: bool
    proof_record: ProofRecord
    validation_details: Dict
    recommended_action: str  # mint|reject|defer|investigate


class ProofValidator:
    """
    Validates Proof of Energy (PoE) through tri-check validation.

    Tri-Check Validation:
    1. Energy Conservation: |E_predicted - E_observed| / E_observed < tolerance
    2. Entropy Coherence: Entropy increases monotonically (ΔS ≥ 0)
    3. Spectral Similarity: Correlation(spectrum_pred, spectrum_obs) > threshold

    All three checks must pass for proof to be valid.
    """

    def __init__(
        self,
        energy_tolerance: float = 0.01,  # 1% energy error allowed
        entropy_threshold: float = 0.90,  # 90% entropy coherence
        spectral_threshold: float = 0.85,  # 85% spectral correlation
        validator_id: str = "phase5-eil"
    ):
        """
        Initialize Proof Validator

        Args:
            energy_tolerance: Maximum relative energy error
            entropy_threshold: Minimum entropy coherence score
            spectral_threshold: Minimum spectral similarity
            validator_id: Unique identifier for this validator
        """
        self.energy_tolerance = energy_tolerance
        self.entropy_threshold = entropy_threshold
        self.spectral_threshold = spectral_threshold
        self.validator_id = validator_id

        # Validation statistics
        self.stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'energy_check_failures': 0,
            'entropy_check_failures': 0,
            'spectral_check_failures': 0,
            'pft_minted_total': 0.0
        }

        print(f"✅ ProofValidator initialized")
        print(f"  Energy tolerance: {energy_tolerance}")
        print(f"  Entropy threshold: {entropy_threshold}")
        print(f"  Spectral threshold: {spectral_threshold}")

    def create_proof(
        self,
        domain: str,
        predicted_energy_map: np.ndarray,
        regime: str = "unknown",
        regime_approved: bool = False,
        metadata: Optional[Dict] = None
    ) -> ProofRecord:
        """
        Create a proof record from ACE prediction (before validation).

        Args:
            domain: Physics domain
            predicted_energy_map: ACE predicted energy field
            regime: Detected regime from EIL
            regime_approved: Whether regime was approved
            metadata: Additional metadata

        Returns:
            ProofRecord with prediction data
        """
        # Compute hash of prediction
        predicted_hash = hashlib.sha256(
            predicted_energy_map.tobytes()
        ).hexdigest()

        # Generate unique proof ID
        proof_id = f"poe-{domain}-{int(time.time())}-{predicted_hash[:8]}"

        proof = ProofRecord(
            proof_id=proof_id,
            domain=domain,
            timestamp=time.time(),
            predicted_energy_map=predicted_energy_map,
            predicted_hash=predicted_hash,
            regime=regime,
            regime_approved=regime_approved,
            validator_id=self.validator_id,
            metadata=metadata or {}
        )

        return proof

    def validate(
        self,
        proof: ProofRecord,
        observed_energy_map: np.ndarray
    ) -> ProofValidationResult:
        """
        Validate proof against observed ground truth using tri-check.

        Args:
            proof: Proof record with predictions
            observed_energy_map: Actual observed energy field

        Returns:
            ProofValidationResult with validation outcome
        """
        start_time = time.time()

        # Update proof with observations
        proof.observed_energy_map = observed_energy_map
        proof.observed_hash = hashlib.sha256(
            observed_energy_map.tobytes()
        ).hexdigest()

        # ====================================================================
        # TRI-CHECK VALIDATION
        # ====================================================================

        # Check 1: Energy Conservation
        energy_fidelity = compute_energy_fidelity(
            proof.predicted_energy_map,
            proof.observed_energy_map
        )
        proof.energy_fidelity = energy_fidelity
        proof.energy_check_passed = energy_fidelity >= (1.0 - self.energy_tolerance)

        if not proof.energy_check_passed:
            self.stats['energy_check_failures'] += 1

        # Check 2: Entropy Coherence
        # Note: compute_entropy_coherence expects 3D (steps, H, W)
        # If we have 2D, add a time dimension
        pred_3d = proof.predicted_energy_map[np.newaxis, :, :] if proof.predicted_energy_map.ndim == 2 else proof.predicted_energy_map
        obs_3d = proof.observed_energy_map[np.newaxis, :, :] if proof.observed_energy_map.ndim == 2 else proof.observed_energy_map

        entropy_coherence = compute_entropy_coherence(pred_3d, bins=50)
        proof.entropy_coherence = entropy_coherence
        proof.entropy_check_passed = entropy_coherence >= self.entropy_threshold

        if not proof.entropy_check_passed:
            self.stats['entropy_check_failures'] += 1

        # Check 3: Spectral Similarity
        # Note: compute_spectral_similarity expects 3D (steps, H, W)
        spectral_similarity = compute_spectral_similarity(
            pred_3d,
            obs_3d
        )
        proof.spectral_similarity = spectral_similarity
        proof.spectral_check_passed = spectral_similarity >= self.spectral_threshold

        if not proof.spectral_check_passed:
            self.stats['spectral_check_failures'] += 1

        # Overall validation: All three checks must pass
        proof.overall_passed = (
            proof.energy_check_passed and
            proof.entropy_check_passed and
            proof.spectral_check_passed
        )

        proof.validation_time = time.time() - start_time

        # Update statistics
        self.stats['total_validations'] += 1
        if proof.overall_passed:
            self.stats['passed_validations'] += 1
        else:
            self.stats['failed_validations'] += 1

        # Determine recommended action
        recommended_action = self._determine_action(proof)

        # Build validation details
        validation_details = {
            'tri_check': {
                'energy': {
                    'passed': proof.energy_check_passed,
                    'fidelity': proof.energy_fidelity,
                    'threshold': 1.0 - self.energy_tolerance
                },
                'entropy': {
                    'passed': proof.entropy_check_passed,
                    'coherence': proof.entropy_coherence,
                    'threshold': self.entropy_threshold
                },
                'spectral': {
                    'passed': proof.spectral_check_passed,
                    'similarity': proof.spectral_similarity,
                    'threshold': self.spectral_threshold
                }
            },
            'overall': {
                'passed': proof.overall_passed,
                'checks_passed': sum([
                    proof.energy_check_passed,
                    proof.entropy_check_passed,
                    proof.spectral_check_passed
                ]),
                'checks_total': 3
            },
            'regime_context': {
                'regime': proof.regime,
                'approved': proof.regime_approved
            },
            'validation_time_ms': proof.validation_time * 1000
        }

        return ProofValidationResult(
            passed=proof.overall_passed,
            proof_record=proof,
            validation_details=validation_details,
            recommended_action=recommended_action
        )

    def _determine_action(self, proof: ProofRecord) -> str:
        """
        Determine recommended action based on validation results.

        Returns:
            Action: mint|reject|defer|investigate
        """
        if proof.overall_passed and proof.regime_approved:
            # All checks passed + regime approved → mint PFT
            return "mint"

        elif proof.overall_passed and not proof.regime_approved:
            # Checks passed but regime suspicious → defer for manual review
            return "defer"

        elif not proof.overall_passed:
            # Failed at least one check
            checks_passed = sum([
                proof.energy_check_passed,
                proof.entropy_check_passed,
                proof.spectral_check_passed
            ])

            if checks_passed == 0:
                # Complete failure → reject
                return "reject"
            elif checks_passed == 1:
                # Major failure → reject
                return "reject"
            else:
                # 2/3 checks passed → investigate
                return "investigate"

        else:
            return "defer"

    def mint_pft(
        self,
        proof: ProofRecord,
        base_amount: float = 1.0,
        bonus_multiplier: float = 1.0
    ) -> Tuple[float, str]:
        """
        Calculate PFT amount to mint based on proof quality.

        Args:
            proof: Validated proof record
            base_amount: Base PFT amount (usually 1.0)
            bonus_multiplier: Quality bonus multiplier

        Returns:
            (pft_amount, contract_tx_hash)
        """
        if not proof.overall_passed:
            return (0.0, None)

        # Calculate quality bonus
        avg_score = (
            proof.energy_fidelity +
            proof.entropy_coherence +
            proof.spectral_similarity
        ) / 3.0

        # Bonus for exceptional quality (> 95%)
        quality_bonus = 1.0
        if avg_score > 0.95:
            quality_bonus = 1.5
        elif avg_score > 0.90:
            quality_bonus = 1.2

        # Calculate final PFT amount
        pft_amount = base_amount * bonus_multiplier * quality_bonus

        # Simulate contract transaction (in production, call smart contract)
        contract_tx_hash = hashlib.sha256(
            f"{proof.proof_id}{pft_amount}{time.time()}".encode()
        ).hexdigest()

        # Update proof record
        proof.pft_minted = True
        proof.pft_amount = pft_amount
        proof.contract_tx_hash = contract_tx_hash

        # Update stats
        self.stats['pft_minted_total'] += pft_amount

        return (pft_amount, contract_tx_hash)

    def get_stats(self) -> Dict:
        """Get validation statistics"""
        total = self.stats['total_validations']
        if total == 0:
            pass_rate = 0.0
        else:
            pass_rate = self.stats['passed_validations'] / total

        return {
            **self.stats,
            'pass_rate': pass_rate,
            'thresholds': {
                'energy_tolerance': self.energy_tolerance,
                'entropy_threshold': self.entropy_threshold,
                'spectral_threshold': self.spectral_threshold
            }
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("PROOF VALIDATOR - TRI-CHECK VALIDATION TEST")
    print("=" * 70)

    # Initialize validator
    validator = ProofValidator(
        energy_tolerance=0.01,
        entropy_threshold=0.90,
        spectral_threshold=0.85
    )

    # Test Case 1: Perfect prediction
    print("\n[Test 1] Perfect Prediction")
    predicted = np.random.randn(64, 64) * 0.1 + 1.0
    observed = predicted.copy()  # Perfect match

    proof = validator.create_proof(
        domain="fluid_dynamics",
        predicted_energy_map=predicted,
        regime="stable_confirmed",
        regime_approved=True
    )

    result = validator.validate(proof, observed)

    print(f"  Overall: {'PASSED' if result.passed else 'FAILED'}")
    print(f"  Energy: {result.validation_details['tri_check']['energy']['passed']}")
    print(f"  Entropy: {result.validation_details['tri_check']['entropy']['passed']}")
    print(f"  Spectral: {result.validation_details['tri_check']['spectral']['passed']}")
    print(f"  Action: {result.recommended_action}")

    if result.recommended_action == "mint":
        amount, tx = validator.mint_pft(proof)
        print(f"  PFT Minted: {amount:.2f}")
        print(f"  TX Hash: {tx[:16]}...")

    # Test Case 2: Poor prediction
    print("\n[Test 2] Poor Prediction")
    predicted2 = np.random.randn(64, 64) * 0.1 + 1.0
    observed2 = np.random.randn(64, 64) * 0.1 + 5.0  # Very different

    proof2 = validator.create_proof(
        domain="molecular_dynamics",
        predicted_energy_map=predicted2,
        regime="chaotic_unconfirmed",
        regime_approved=False
    )

    result2 = validator.validate(proof2, observed2)

    print(f"  Overall: {'PASSED' if result2.passed else 'FAILED'}")
    print(f"  Energy: {result2.validation_details['tri_check']['energy']['passed']}")
    print(f"  Entropy: {result2.validation_details['tri_check']['entropy']['passed']}")
    print(f"  Spectral: {result2.validation_details['tri_check']['spectral']['passed']}")
    print(f"  Action: {result2.recommended_action}")

    # Show stats
    print("\n[Statistics]")
    stats = validator.get_stats()
    print(f"  Total validations: {stats['total_validations']}")
    print(f"  Pass rate: {stats['pass_rate']:.1%}")
    print(f"  PFT minted: {stats['pft_minted_total']:.2f}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
