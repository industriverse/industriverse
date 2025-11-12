#!/bin/bash
# bootstrap.sh
# Industriverse Phase 4-5 Environment Setup Script
# Sets up Python environment, dependencies, Neo4j, and validates workspace

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0:31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if script is run from correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "Industriverse Phase 4-5 Bootstrap"
log_info "Workspace: $WORKSPACE_ROOT"
echo ""

# Step 1: Verify directory structure
log_info "Step 1: Verifying directory structure..."
REQUIRED_DIRS=(
    "docs"
    "phase4/core"
    "phase4/data"
    "phase4/nvp"
    "phase4/agents"
    "phase4/tests"
    "phase5/consensus"
    "phase5/dgm"
    "phase5/integrations"
    "phase5/eil"
    "phase5/economy"
    "phase5/tests"
    "data/energy_maps/pyramids"
    "data/telemetry"
    "data/catalogs"
    "deploy"
)

cd "$WORKSPACE_ROOT"

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        log_error "Missing directory: $dir"
        exit 1
    fi
done

log_success "Directory structure verified"
echo ""

# Step 2: Check Python version
log_info "Step 2: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    log_success "Python $PYTHON_VERSION (>= 3.11) found"
else
    log_error "Python 3.11+ required. Found: $PYTHON_VERSION"
    log_info "Install with: apt-get install python3.11 python3.11-venv"
    exit 1
fi
echo ""

# Step 3: Create virtual environment
log_info "Step 3: Creating Python virtual environment..."
VENV_DIR="$WORKSPACE_ROOT/venv"

if [ -d "$VENV_DIR" ]; then
    log_warning "Virtual environment already exists at $VENV_DIR"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment recreated"
    else
        log_info "Using existing virtual environment"
    fi
else
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created at $VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
log_info "Virtual environment activated"
echo ""

# Step 4: Upgrade pip
log_info "Step 4: Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
log_success "pip upgraded"
echo ""

# Step 5: Install Phase 4 dependencies
log_info "Step 5: Installing Phase 4 dependencies..."
cat > "$WORKSPACE_ROOT/deploy/requirements_phase4.txt" << 'EOF'
# Phase 4: Next Vector Prediction (NVP)
# Core ML/Scientific Computing
jax[cuda12]>=0.4.20
flax>=0.7.5
optax>=0.1.7
numpy>=1.26.0
scipy>=1.11.0
h5py>=3.10.0

# Data and Storage
py2neo>=2021.2.3
pandas>=2.1.0

# Visualization (optional)
matplotlib>=3.8.0
seaborn>=0.13.0

# Monitoring (optional)
wandb>=0.15.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Development
black>=23.11.0
flake8>=6.1.0
mypy>=1.7.0
EOF

pip install -r "$WORKSPACE_ROOT/deploy/requirements_phase4.txt"
log_success "Phase 4 dependencies installed"
echo ""

# Step 6: Install Phase 5 dependencies
log_info "Step 6: Installing Phase 5 dependencies..."
cat > "$WORKSPACE_ROOT/deploy/requirements_phase5.txt" << 'EOF'
# Phase 5: Energy Intelligence Layer (EIL)
# Extends Phase 4 with consensus, evolution, and economy

# Graph Neural Networks
torch>=2.1.0
torch-geometric>=2.4.0

# Network and Protocol
networkx>=3.2.0

# Economic Simulation
simpy>=4.1.0

# Additional utilities
pydantic>=2.5.0
jsonschema>=4.20.0
EOF

pip install -r "$WORKSPACE_ROOT/deploy/requirements_phase5.txt"
log_success "Phase 5 dependencies installed"
echo ""

# Step 7: Verify Neo4j availability
log_info "Step 7: Checking Neo4j availability..."
if command -v neo4j &> /dev/null; then
    NEO4J_VERSION=$(neo4j version 2>&1 | head -n1 || echo "Unknown")
    log_success "Neo4j found: $NEO4J_VERSION"
else
    log_warning "Neo4j not found in PATH"
    log_info "To install Neo4j:"
    log_info "  - Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=none neo4j:5"
    log_info "  - Native: apt-get install neo4j"
    log_info ""
    log_info "Schema file ready at: deploy/neo4j_schema.cypher"
    log_info "Apply with: cypher-shell < deploy/neo4j_schema.cypher"
fi
echo ""

# Step 8: Create __init__.py files
log_info "Step 8: Creating Python package structure..."
find "$WORKSPACE_ROOT/phase4" -type d -exec touch {}/__init__.py \; 2>/dev/null || true
find "$WORKSPACE_ROOT/phase5" -type d -exec touch {}/__init__.py \; 2>/dev/null || true
log_success "Python packages initialized"
echo ""

# Step 9: Validate manifests
log_info "Step 9: Validating manifest files..."
MANIFESTS=(
    "docs/PROJECT_OVERVIEW.md"
    "docs/phase4.md"
    "docs/phase5.md"
    "docs/REPOSITORY_MAP.md"
)

for manifest in "${MANIFESTS[@]}"; do
    if [ -f "$WORKSPACE_ROOT/$manifest" ]; then
        echo "  ✓ $manifest"
    else
        log_error "Missing manifest: $manifest"
        exit 1
    fi
done
log_success "All manifests present"
echo ""

# Step 10: Create data catalog audit script
log_info "Step 10: Creating data catalog audit script..."
cat > "$WORKSPACE_ROOT/data/catalogs/audit_data.py" << 'EOF'
#!/usr/bin/env python3
"""
Data Catalog Audit Script
Scans data directories and generates catalog.json
"""
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

def audit_data_directory(base_path: Path):
    """Audit all data files and generate catalog."""
    catalog = {
        'generated_at': datetime.now().isoformat(),
        'base_path': str(base_path),
        'maps': [],
        'telemetry': [],
        'stats': {
            'total_maps': 0,
            'total_size_mb': 0,
            'domains': set()
        }
    }

    # Scan energy maps
    maps_dir = base_path / 'energy_maps'
    if maps_dir.exists():
        for file_path in maps_dir.rglob('*.npy'):
            stat = file_path.stat()
            catalog['maps'].append({
                'path': str(file_path.relative_to(base_path)),
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'sha256': hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
            })
            catalog['stats']['total_maps'] += 1
            catalog['stats']['total_size_mb'] += stat.st_size / (1024 * 1024)

    # Scan telemetry
    telemetry_dir = base_path / 'telemetry'
    if telemetry_dir.exists():
        for file_path in telemetry_dir.rglob('*.*'):
            stat = file_path.stat()
            catalog['telemetry'].append({
                'path': str(file_path.relative_to(base_path)),
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    # Convert set to list for JSON serialization
    catalog['stats']['domains'] = sorted(list(catalog['stats']['domains']))

    return catalog

if __name__ == '__main__':
    workspace_root = Path(__file__).parent.parent.parent
    data_dir = workspace_root / 'data'

    print(f"Auditing data directory: {data_dir}")
    catalog = audit_data_directory(data_dir)

    # Save catalog
    catalog_path = data_dir / 'catalogs' / 'catalog.json'
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"\nCatalog saved to: {catalog_path}")
    print(f"Total maps: {catalog['stats']['total_maps']}")
    print(f"Total size: {catalog['stats']['total_size_mb']:.2f} MB")
EOF

chmod +x "$WORKSPACE_ROOT/data/catalogs/audit_data.py"
log_success "Data audit script created"
echo ""

# Step 11: Run initial data audit
log_info "Step 11: Running initial data audit..."
python3 "$WORKSPACE_ROOT/data/catalogs/audit_data.py"
log_success "Data catalog generated"
echo ""

# Step 12: Create run scripts
log_info "Step 12: Creating convenience run scripts..."

# Phase 4 training script
cat > "$WORKSPACE_ROOT/run_phase4_training.sh" << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 phase4/nvp/trainer.py "$@"
EOF
chmod +x "$WORKSPACE_ROOT/run_phase4_training.sh"

# Phase 5 simulation script
cat > "$WORKSPACE_ROOT/run_phase5_simulation.sh" << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 phase5/economy/sim.py "$@"
EOF
chmod +x "$WORKSPACE_ROOT/run_phase5_simulation.sh"

# Test runner
cat > "$WORKSPACE_ROOT/run_tests.sh" << 'EOF'
#!/bin/bash
source venv/bin/activate
pytest phase4/tests/ phase5/tests/ -v --cov=phase4 --cov=phase5 "$@"
EOF
chmod +x "$WORKSPACE_ROOT/run_tests.sh"

log_success "Run scripts created"
echo ""

# Final summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "Bootstrap complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Review manifests:"
echo "     cat docs/PROJECT_OVERVIEW.md"
echo "     cat docs/phase4.md"
echo "     cat docs/phase5.md"
echo ""
echo "  3. Set up Neo4j (if not already running):"
echo "     docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=none neo4j:5"
echo "     cypher-shell < deploy/neo4j_schema.cypher"
echo ""
echo "  4. Run tests:"
echo "     ./run_tests.sh"
echo ""
echo "  5. Start Phase 4 development:"
echo "     Review docs/phase4.md and begin implementing atlas_loader.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
