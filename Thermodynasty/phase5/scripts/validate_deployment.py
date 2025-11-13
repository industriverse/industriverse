#!/usr/bin/env python3
"""
Phase 5 EIL Deployment Validation Script

Validates that all Phase 5 components are properly deployed and functional.

Usage:
    python validate_deployment.py [--verbose]
"""

import sys
import os
import argparse
from pathlib import Path
import time

# Add Thermodynasty to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def validate_imports(verbose=False):
    """Validate all Phase 5 imports"""
    print_header("VALIDATING IMPORTS")

    checks = []

    # Core components
    try:
        from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer
        checks.append(("EnergyIntelligenceLayer", True, None))
    except Exception as e:
        checks.append(("EnergyIntelligenceLayer", False, str(e)))

    try:
        from phase5.core.proof_validator import ProofValidator
        checks.append(("ProofValidator", True, None))
    except Exception as e:
        checks.append(("ProofValidator", False, str(e)))

    try:
        from phase5.core.market_engine import MarketEngine
        checks.append(("MarketEngine", True, None))
    except Exception as e:
        checks.append(("MarketEngine", False, str(e)))

    try:
        from phase5.core.feedback_trainer import FeedbackTrainer
        checks.append(("FeedbackTrainer", True, None))
    except Exception as e:
        checks.append(("FeedbackTrainer", False, str(e)))

    # MicroAdapt
    try:
        from phase5.core.microadapt import DynamicDataCollection, ModelUnitAdaptation, ModelUnitSearch
        checks.append(("MicroAdapt", True, None))
    except Exception as e:
        checks.append(("MicroAdapt", False, str(e)))

    # Monitoring
    try:
        from phase5.monitoring import get_metrics
        checks.append(("Prometheus Metrics", True, None))
    except Exception as e:
        checks.append(("Prometheus Metrics", False, str(e)))

    # Print results
    failed = 0
    for name, success, error in checks:
        if success:
            print_success(f"{name} import successful")
        else:
            print_error(f"{name} import failed: {error if verbose else 'See error log'}")
            failed += 1

    return failed == 0


def validate_components(verbose=False):
    """Validate component initialization"""
    print_header("VALIDATING COMPONENT INITIALIZATION")

    import numpy as np
    from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer
    from phase5.core.proof_validator import ProofValidator
    from phase5.core.market_engine import MarketEngine
    from phase5.core.feedback_trainer import FeedbackTrainer
    from phase5.monitoring import get_metrics

    checks = []

    # EIL
    try:
        eil = EnergyIntelligenceLayer(
            regime_detector_checkpoint=None,
            microadapt_config={'max_units': 10, 'initial_units': 3}
        )
        checks.append(("EIL initialization", True, None))
    except Exception as e:
        checks.append(("EIL initialization", False, str(e)))

    # Proof Validator
    try:
        pv = ProofValidator()
        checks.append(("ProofValidator initialization", True, None))
    except Exception as e:
        checks.append(("ProofValidator initialization", False, str(e)))

    # Market Engine
    try:
        me = MarketEngine()
        checks.append(("MarketEngine initialization", True, None))
    except Exception as e:
        checks.append(("MarketEngine initialization", False, str(e)))

    # Feedback Trainer
    try:
        ft = FeedbackTrainer()
        checks.append(("FeedbackTrainer initialization", True, None))
    except Exception as e:
        checks.append(("FeedbackTrainer initialization", False, str(e)))

    # Prometheus Metrics
    try:
        metrics = get_metrics("validation_test")
        checks.append(("Prometheus Metrics initialization", True, None))
    except Exception as e:
        checks.append(("Prometheus Metrics initialization", False, str(e)))

    # Print results
    failed = 0
    for name, success, error in checks:
        if success:
            print_success(f"{name}")
        else:
            print_error(f"{name}: {error if verbose else 'Failed'}")
            failed += 1

    return failed == 0


def validate_workflows(verbose=False):
    """Validate end-to-end workflows"""
    print_header("VALIDATING END-TO-END WORKFLOWS")

    import numpy as np
    from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer
    from phase5.core.proof_validator import ProofValidator
    from phase5.core.market_engine import MarketEngine

    eil = EnergyIntelligenceLayer(
        regime_detector_checkpoint=None,
        microadapt_config={'max_units': 10, 'initial_units': 3}
    )
    pv = ProofValidator()
    me = MarketEngine()

    checks = []

    # Workflow 1: Regime Detection
    try:
        energy_map = np.random.randn(64, 64) * 0.1 + 1.0
        decision = eil.process(
            energy_map=energy_map,
            domain="validation_test",
            cluster="test-cluster",
            node="test-node"
        )
        assert decision.regime is not None, "Regime is None"
        assert decision.confidence >= 0, f"Confidence is negative: {decision.confidence}"
        checks.append(("Regime Detection Workflow", True, None))
    except Exception as e:
        checks.append(("Regime Detection Workflow", False, str(e)))

    # Workflow 2: Proof Validation
    try:
        predicted = np.random.randn(64, 64) * 0.1 + 1.0
        observed = predicted + np.random.randn(64, 64) * 0.01

        proof = pv.create_proof(
            domain="validation_test",
            predicted_energy_map=predicted,
            regime="stable_confirmed",
            regime_approved=True
        )

        result = pv.validate(proof, observed)
        assert result.passed is not None
        checks.append(("Proof Validation Workflow", True, None))
    except Exception as e:
        checks.append(("Proof Validation Workflow", False, str(e)))

    # Workflow 3: Market Engine Pricing
    try:
        ceu_cost = me.calculate_ceu_cost(
            energy_consumption=1.0,
            regime="stable_confirmed",
            regime_approved=True,
            num_steps=10
        )
        assert ceu_cost.total_ceu > 0

        pft_reward = me.calculate_pft_reward(
            proof_quality=0.95,
            regime="stable_confirmed",
            regime_approved=True,
            regime_confidence=0.90
        )
        assert pft_reward.total_pft > 0

        checks.append(("Market Engine Pricing Workflow", True, None))
    except Exception as e:
        checks.append(("Market Engine Pricing Workflow", False, str(e)))

    # Workflow 4: AMM Swaps
    try:
        pft_out, rate = me.swap_ceu_for_pft(100.0)
        assert pft_out > 0
        assert rate > 0

        checks.append(("AMM Swap Workflow", True, None))
    except Exception as e:
        checks.append(("AMM Swap Workflow", False, str(e)))

    # Print results
    failed = 0
    for name, success, error in checks:
        if success:
            print_success(f"{name}")
        else:
            print_error(f"{name}: {error if verbose else 'Failed'}")
            failed += 1

    return failed == 0


def validate_performance(verbose=False):
    """Validate performance targets"""
    print_header("VALIDATING PERFORMANCE TARGETS")

    import numpy as np
    from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer

    eil = EnergyIntelligenceLayer(
        regime_detector_checkpoint=None,
        microadapt_config={'max_units': 10, 'initial_units': 3}
    )

    checks = []

    # Test 1: Regime Detection Latency (<1s target)
    try:
        energy_map = np.random.randn(64, 64) * 0.1 + 1.0

        start = time.time()
        decision = eil.process(
            energy_map=energy_map,
            domain="perf_test",
            cluster="test",
            node="test"
        )
        latency_ms = (time.time() - start) * 1000

        target_ms = 1000  # 1 second
        passed = latency_ms < target_ms

        checks.append((
            f"Regime Detection Latency (<{target_ms}ms)",
            passed,
            f"{latency_ms:.2f}ms"
        ))
    except Exception as e:
        checks.append(("Regime Detection Latency", False, str(e)))

    # Test 2: Throughput (>1 req/s minimum)
    try:
        num_requests = 10
        start = time.time()

        for i in range(num_requests):
            energy_map = np.random.randn(64, 64) * 0.1 + 1.0
            decision = eil.process(
                energy_map=energy_map,
                domain=f"perf_test_{i}",
                cluster="test",
                node="test"
            )

        elapsed = time.time() - start
        throughput = num_requests / elapsed

        target_throughput = 1.0  # 1 req/s minimum
        passed = throughput >= target_throughput

        checks.append((
            f"Throughput (>{target_throughput:.0f} req/s)",
            passed,
            f"{throughput:.2f} req/s"
        ))
    except Exception as e:
        checks.append(("Throughput", False, str(e)))

    # Print results
    failed = 0
    for name, success, metric in checks:
        if success:
            print_success(f"{name}: {metric}")
        else:
            print_error(f"{name}: {metric if verbose else 'Failed'}")
            failed += 1

    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Validate Phase 5 EIL Deployment")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    args = parser.parse_args()

    print_header("PHASE 5 EIL DEPLOYMENT VALIDATION")
    print_info(f"Validation started at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # Run validations
    results.append(("Imports", validate_imports(args.verbose)))
    results.append(("Components", validate_components(args.verbose)))
    results.append(("Workflows", validate_workflows(args.verbose)))
    results.append(("Performance", validate_performance(args.verbose)))

    # Summary
    print_header("VALIDATION SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        if success:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")

    print()
    if passed == total:
        print_success(f"All {total} validation checks PASSED ✅")
        print()
        return 0
    else:
        print_error(f"{total - passed}/{total} validation checks FAILED ❌")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
