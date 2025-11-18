#!/bin/bash
#
# Week 17 Test Runner
# Runs all Week 17 integration and unit tests
#

set -e

echo "=========================================="
echo "Week 17 Test Suite"
echo "=========================================="
echo ""

# Colors
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

# Run tests
echo -e "${YELLOW}Running Week 17 Tests...${NC}"
echo ""

# Day 1: Database Setup
echo "----------------------------------------"
echo "Day 1: Database Setup Tests"
echo "----------------------------------------"
pytest tests/week17/test_database_setup.py -v || echo -e "${YELLOW}Note: Database tests may require running database${NC}"
echo ""

# Day 2: Behavioral Tracking API
echo "----------------------------------------"
echo "Day 2: Behavioral Tracking API Tests"
echo "----------------------------------------"
pytest tests/week17/test_behavioral_tracking_api.py -v
echo ""

# Day 3: A2A Task Execution
echo "----------------------------------------"
echo "Day 3: A2A Task Execution Tests"
echo "----------------------------------------"
pytest tests/week17/test_a2a_task_execution.py -v
echo ""

# Day 4: DTSL Schema Validation
echo "----------------------------------------"
echo "Day 4: DTSL Schema Validation Tests"
echo "----------------------------------------"
pytest tests/week17/test_dtsl_schema_validation.py -v
echo ""

# Day 5: Error Handling
echo "----------------------------------------"
echo "Day 5: Error Handling Tests"
echo "----------------------------------------"
pytest tests/week17/test_error_handling.py -v
echo ""

echo "=========================================="
echo -e "${GREEN}Week 17 Test Suite Complete!${NC}"
echo "=========================================="
