#!/bin/bash

###############################################################################
# Week 18-19 Integration Test Runner
#
# Runs all Week 18-19 tests with coverage and detailed reporting.
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh -k registry  # Run registry tests only
#   ./run_tests.sh --verbose    # Verbose output
###############################################################################

set -e

echo "========================================="
echo "Week 18-19 Integration Test Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-asyncio"
    exit 1
fi

# Determine test path
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Test Directory: $TEST_DIR"
echo ""

# Run tests based on arguments
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Running all Week 18-19 tests...${NC}"
    echo ""

    # Run all tests with detailed output
    pytest "$TEST_DIR" \
        -v \
        --tb=short \
        --color=yes \
        --durations=10 \
        "$@"

    TEST_RESULT=$?
else
    echo -e "${YELLOW}Running tests with custom arguments: $@${NC}"
    echo ""

    # Run with custom arguments
    pytest "$TEST_DIR" "$@"

    TEST_RESULT=$?
fi

echo ""
echo "========================================="

# Exit with pytest's exit code
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "========================================="
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "========================================="
    exit $TEST_RESULT
fi
