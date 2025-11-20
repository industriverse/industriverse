#!/bin/bash
# Phase 5 EIL Integration Test Runner

set -e

echo "======================================================================"
echo "PHASE 5 EIL INTEGRATION TESTS"
echo "======================================================================"

# Set PYTHONPATH
export PYTHONPATH=/home/user/industriverse/Thermodynasty:$PYTHONPATH

cd "$(dirname "$0")"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Install with: pip install pytest"
    exit 1
fi

# Run tests based on argument
case "${1:-all}" in
    phase5)
        echo "Running Phase 5 EIL tests..."
        pytest test_phase5_eil_integration.py -v
        ;;
    full_stack)
        echo "Running Full Stack Phase 0-5 tests..."
        pytest test_full_stack_phase0_5.py -v
        ;;
    all)
        echo "Running all integration tests..."
        pytest . -v
        ;;
    *)
        echo "Usage: $0 [phase5|full_stack|all]"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "✅ TESTS COMPLETE"
echo "======================================================================"
