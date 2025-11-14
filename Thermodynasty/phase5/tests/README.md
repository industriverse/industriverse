# EIL Platform - Test Suite

Comprehensive testing suite for the Energy Intelligence Layer platform.

## Overview

This test suite provides extensive coverage across multiple dimensions:

- **Unit Tests** - Individual component testing
- **Integration Tests** - API endpoint testing
- **Security Tests** - Authentication, authorization, input validation
- **Physics Tests** - Thermodynamic constraint validation
- **Performance Tests** - Load testing and benchmarks

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_energy_field.py     # Energy field unit tests
├── test_api_endpoints.py    # API integration tests
├── test_security.py         # Security tests
└── README.md                # This file
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_energy_field.py

# Run specific test class
pytest tests/test_api_endpoints.py::TestHealthEndpoints

# Run specific test
pytest tests/test_security.py::TestAuthentication::test_create_access_token
```

### By Marker

Tests are organized with markers for selective execution:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only security tests
pytest -m security

# Run only physics tests
pytest -m physics

# Run fast tests (exclude slow)
pytest -m "not slow"

# Run performance tests
pytest -m performance
```

### With Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Generate HTML report
pytest --html=report.html --self-contained-html
```

## Test Categories

### 1. Unit Tests

**Location**: `test_energy_field.py`

**Coverage**:
- Energy field initialization
- Total energy calculation
- Energy gradient computation
- Shannon entropy calculation
- Boltzmann weighting
- Thermodynamic state creation
- Conservation validation
- Temperature effects

**Run**:
```bash
pytest -m unit
```

---

### 2. Integration Tests

**Location**: `test_api_endpoints.py`

**Coverage**:
- Health check endpoints
- `/v1/predict` - Energy map prediction
- `/v1/diffuse` - Diffusion sampling
- `/v1/proof` - Proof validation
- `/v1/market/pricing` - Market pricing
- Error handling
- CORS headers
- Response times

**Run**:
```bash
pytest -m integration
```

---

### 3. Security Tests

**Location**: `test_security.py`

**Coverage**:
- JWT token creation/verification
- Password hashing
- Token expiration
- Token revocation
- RBAC permission checks
- Role inheritance
- Rate limiting (token bucket)
- Input sanitization (SQL, XSS, path traversal)
- Security middleware
- Attack resistance (timing, replay, brute force)

**Run**:
```bash
pytest -m security
```

---

### 4. Physics Tests

**Coverage**:
- Energy conservation (ΔE < tolerance)
- Entropy monotonicity (ΔS ≥ 0)
- Thermodynamic state transitions
- Boltzmann distribution
- Temperature effects

**Run**:
```bash
pytest -m physics
```

---

### 5. Performance Tests

**Coverage**:
- Large energy map processing
- Batch operations
- Concurrent requests
- Response time benchmarks

**Run**:
```bash
pytest -m performance
```

---

## Test Fixtures

Common fixtures available in `conftest.py`:

### API Client
- `client` - FastAPI test client

### Energy Field
- `energy_field_config` - Standard configuration
- `energy_field` - Energy field instance
- `sample_energy_map` - 32x32 random map
- `small_energy_map` - 2x2 test map

### Diffusion
- `diffusion_config` - Standard configuration
- `forward_diffusion` - Forward process
- `reverse_diffusion` - Reverse process

### Security
- `auth_manager` - Authentication manager
- `test_user` - Developer role user
- `admin_user` - Admin role user
- `test_access_token` - Valid token
- `auth_headers` - Authorization headers

### Request Data
- `predict_request_data` - Sample predict payload
- `diffuse_request_data` - Sample diffuse payload
- `proof_request_data` - Sample proof payload

## Code Coverage

### Generating Coverage Reports

```bash
# Terminal report
pytest --cov --cov-report=term-missing

# HTML report
pytest --cov --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov --cov-report=xml

# Multiple formats
pytest --cov --cov-report=html --cov-report=term --cov-report=xml
```

### Coverage Goals

- **Overall**: ≥80%
- **Core modules**: ≥90%
- **API endpoints**: ≥85%
- **Security**: ≥95%

### Viewing Coverage

After running with `--cov-report=html`:

```bash
open htmlcov/index.html
```

Navigate through files to see line-by-line coverage.

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest -m "not slow" --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Writing New Tests

### Test Structure

```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Test my new feature"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = my_function()
        assert result == expected

    def test_edge_case(self):
        """Test edge case"""
        with pytest.raises(ValueError):
            my_function(invalid_input)

    @pytest.mark.slow
    def test_performance(self):
        """Test performance (marked as slow)"""
        import time
        start = time.time()
        my_expensive_function()
        assert time.time() - start < 1.0
```

### Best Practices

1. **Descriptive Names**: Test names should clearly describe what they test
2. **Single Responsibility**: Each test should test one thing
3. **Use Fixtures**: Reuse setup code via fixtures
4. **Mark Appropriately**: Use markers for organization
5. **Isolate Tests**: Tests should not depend on each other
6. **Mock External Services**: Don't depend on external APIs
7. **Test Edge Cases**: Test boundaries and error conditions

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result == expected
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input, expected):
    assert multiply(input, 2) == expected
```

## Troubleshooting

### Tests Not Found

```bash
# Check test discovery
pytest --collect-only
```

### Import Errors

```bash
# Ensure path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Fixture Errors

```bash
# List available fixtures
pytest --fixtures

# Show fixture setup
pytest --setup-show
```

### Slow Tests

```bash
# Show slowest 10 tests
pytest --durations=10

# Skip slow tests
pytest -m "not slow"
```

### Debugging Tests

```bash
# Drop into pdb on failure
pytest --pdb

# Drop into pdb on error
pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

## Performance Benchmarking

### Using pytest-benchmark

```bash
pip install pytest-benchmark

# Run benchmarks
pytest --benchmark-only

# Compare to baseline
pytest --benchmark-compare=baseline
```

### Example Benchmark

```python
def test_energy_computation_benchmark(benchmark, energy_field, sample_energy_map):
    """Benchmark energy computation"""
    energy_tensor = torch.from_numpy(sample_energy_map)
    result = benchmark(energy_field.compute_total_energy, energy_tensor)
    assert result > 0
```

## Test Data

### Generating Test Data

```python
import numpy as np

# Energy maps
random_map = np.random.randn(32, 32)
constant_map = np.ones((16, 16)) * 5.0
sparse_map = np.zeros((64, 64))
sparse_map[::4, ::4] = 1.0

# Edge cases
empty_map = np.zeros((8, 8))
negative_map = -np.abs(np.random.randn(16, 16))
large_map = np.random.randn(256, 256)
```

### Test Data Files

Store large test datasets in `tests/data/`:

```python
import json
from pathlib import Path

test_data_dir = Path(__file__).parent / "data"
with open(test_data_dir / "sample_energy_map.json") as f:
    test_data = json.load(f)
```

## Reporting

### JUnit XML (for CI/CD)

```bash
pytest --junit-xml=junit.xml
```

### HTML Report

```bash
pip install pytest-html
pytest --html=report.html --self-contained-html
```

### Allure Report

```bash
pip install allure-pytest
pytest --alluredir=allure-results
allure serve allure-results
```

## Test Metrics

Target metrics for high-quality test suite:

- **Coverage**: ≥80%
- **Test Count**: ≥100 tests
- **Test Execution Time**: <2 minutes (excluding slow tests)
- **Flaky Tests**: 0
- **Test Maintenance Ratio**: <10% of development time

## Support

- **Documentation**: https://docs.eil-platform.io/testing
- **Pytest Docs**: https://docs.pytest.org/
- **GitHub**: https://github.com/industriverse/eil-platform/issues
- **Email**: support@eil-platform.io
