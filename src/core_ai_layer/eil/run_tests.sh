#!/bin/bash

# EIL Platform Test Runner
# Comprehensive test execution with multiple modes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Display usage
usage() {
    cat <<EOF
EIL Platform Test Runner

Usage: $0 [OPTIONS]

Options:
    -h, --help          Show this help message
    -a, --all           Run all tests (default)
    -u, --unit          Run only unit tests
    -i, --integration   Run only integration tests
    -s, --security      Run only security tests
    -p, --physics       Run only physics tests
    -f, --fast          Run fast tests only (exclude slow)
    -c, --coverage      Run with coverage report
    -v, --verbose       Verbose output
    -x, --exitfirst     Exit on first failure
    -k EXPRESSION       Run tests matching expression
    --html              Generate HTML report
    --parallel          Run tests in parallel
    --benchmark         Run performance benchmarks

Examples:
    $0                          # Run all tests
    $0 --unit --coverage        # Unit tests with coverage
    $0 --fast -v                # Fast tests, verbose
    $0 -k test_energy           # Tests matching 'test_energy'
    $0 --security --html        # Security tests with HTML report

EOF
}

# Default values
RUN_MODE="all"
COVERAGE=false
VERBOSE=false
EXITFIRST=false
HTML_REPORT=false
PARALLEL=false
BENCHMARK=false
EXPRESSION=""
PYTEST_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -a|--all)
            RUN_MODE="all"
            shift
            ;;
        -u|--unit)
            RUN_MODE="unit"
            shift
            ;;
        -i|--integration)
            RUN_MODE="integration"
            shift
            ;;
        -s|--security)
            RUN_MODE="security"
            shift
            ;;
        -p|--physics)
            RUN_MODE="physics"
            shift
            ;;
        -f|--fast)
            RUN_MODE="fast"
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -x|--exitfirst)
            EXITFIRST=true
            shift
            ;;
        -k)
            EXPRESSION="$2"
            shift 2
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --benchmark)
            BENCHMARK=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Build pytest arguments
case $RUN_MODE in
    all)
        print_info "Running all tests..."
        ;;
    unit)
        print_info "Running unit tests..."
        PYTEST_ARGS="$PYTEST_ARGS -m unit"
        ;;
    integration)
        print_info "Running integration tests..."
        PYTEST_ARGS="$PYTEST_ARGS -m integration"
        ;;
    security)
        print_info "Running security tests..."
        PYTEST_ARGS="$PYTEST_ARGS -m security"
        ;;
    physics)
        print_info "Running physics tests..."
        PYTEST_ARGS="$PYTEST_ARGS -m physics"
        ;;
    fast)
        print_info "Running fast tests (excluding slow)..."
        PYTEST_ARGS="$PYTEST_ARGS -m 'not slow'"
        ;;
esac

if [ "$COVERAGE" = true ]; then
    print_info "Enabling coverage reporting..."
    PYTEST_ARGS="$PYTEST_ARGS --cov --cov-report=term-missing --cov-report=html"
fi

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -v"
fi

if [ "$EXITFIRST" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -x"
fi

if [ -n "$EXPRESSION" ]; then
    print_info "Running tests matching: $EXPRESSION"
    PYTEST_ARGS="$PYTEST_ARGS -k '$EXPRESSION'"
fi

if [ "$HTML_REPORT" = true ]; then
    print_info "Generating HTML report..."
    PYTEST_ARGS="$PYTEST_ARGS --html=test-report.html --self-contained-html"
fi

if [ "$PARALLEL" = true ]; then
    print_info "Running tests in parallel..."
    PYTEST_ARGS="$PYTEST_ARGS -n auto"
fi

if [ "$BENCHMARK" = true ]; then
    print_info "Running performance benchmarks..."
    PYTEST_ARGS="$PYTEST_ARGS --benchmark-only"
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
fi

# Run tests
print_info "Executing: pytest $PYTEST_ARGS"
echo ""

if eval pytest $PYTEST_ARGS; then
    echo ""
    print_success "All tests passed!"

    if [ "$COVERAGE" = true ]; then
        print_info "Coverage report generated at: htmlcov/index.html"
    fi

    if [ "$HTML_REPORT" = true ]; then
        print_info "HTML report generated at: test-report.html"
    fi

    exit 0
else
    echo ""
    print_error "Tests failed!"
    exit 1
fi
