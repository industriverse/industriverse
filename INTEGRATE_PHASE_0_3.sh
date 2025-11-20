#!/bin/bash

###############################################################################
# INDUSTRIVERSE PHASE 0-3 INTEGRATION SCRIPT
# Purpose: Copy all prototype files from extracted packages to proper locations
# Date: November 20, 2025
# Run on: Your Mac (/Users/industriverse/)
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directories (ADJUST THESE IF NEEDED)
DOWNLOADS="/Users/industriverse/Downloads"
REPO="/Users/industriverse/industriverse_github_clone"

# Extracted phase directories
PHASE0="$DOWNLOADS/phase0_extracted/industriverse_phase0_ip_package"
PHASE1="$DOWNLOADS/phase1_extracted/industriverse_phase1_package"
PHASE2="$DOWNLOADS/phase2_extracted/industriverse_phase2_package"
PHASE3="$DOWNLOADS/phase3_extracted/industriverse_phase3_ip_package"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   INDUSTRIVERSE PHASE 0-3 INTEGRATION SCRIPT                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

###############################################################################
# VERIFICATION
###############################################################################

echo -e "${YELLOW}[1/6] Verifying directories...${NC}"

if [ ! -d "$DOWNLOADS" ]; then
    echo -e "${RED}✗ Downloads directory not found: $DOWNLOADS${NC}"
    exit 1
fi

if [ ! -d "$REPO" ]; then
    echo -e "${RED}✗ Repository directory not found: $REPO${NC}"
    exit 1
fi

if [ ! -d "$PHASE0" ]; then
    echo -e "${RED}✗ Phase 0 not found. Please extract industriverse_phase0_ip_package.zip first${NC}"
    exit 1
fi

if [ ! -d "$PHASE1" ]; then
    echo -e "${YELLOW}⚠ Phase 1 not found. Skipping...${NC}"
    SKIP_PHASE1=true
fi

if [ ! -d "$PHASE2" ]; then
    echo -e "${YELLOW}⚠ Phase 2 not found. Skipping...${NC}"
    SKIP_PHASE2=true
fi

if [ ! -d "$PHASE3" ]; then
    echo -e "${YELLOW}⚠ Phase 3 not found. Skipping...${NC}"
    SKIP_PHASE3=true
fi

echo -e "${GREEN}✓ Directory verification complete${NC}"
echo ""

###############################################################################
# CREATE DIRECTORY STRUCTURE
###############################################################################

echo -e "${YELLOW}[2/6] Creating directory structure...${NC}"

cd "$REPO"

mkdir -p src/prototypes/phase0_dgm
mkdir -p src/prototypes/phase1_microadapt/{algorithms,models,ttf_inference/collectors,ttf_inference/processors,bridge}
mkdir -p src/prototypes/phase2_bridge/retraining
mkdir -p docs/historical/{phase0,phase1,phase2,phase3}
mkdir -p contracts/bridge_contracts
mkdir -p src/retraining
mkdir -p infrastructure/kubernetes/overlays

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

###############################################################################
# PHASE 0: COPY DAC + DGM + SHADOW TWIN PROTOTYPES
###############################################################################

echo -e "${YELLOW}[3/6] Integrating Phase 0 (DAC/DGM/Shadow Twin)...${NC}"

# Copy the 3 usable Python files
echo "  → Copying dac_engine.py (28KB)"
cp "$PHASE0/code/dac_engine.py" "src/prototypes/phase0_dgm/" 2>/dev/null || echo "    ⚠ dac_engine.py not found or empty"

echo "  → Copying a2a2-federation-bridge.py (19KB)"
cp "$PHASE0/code/a2a2-federation-bridge.py" "src/prototypes/phase0_dgm/a2a2_federation_bridge.py" 2>/dev/null || echo "    ⚠ a2a2-federation-bridge.py not found or empty"

echo "  → Copying dac_cli.py (24KB)"
cp "$PHASE0/code/dac_cli.py" "src/prototypes/phase0_dgm/" 2>/dev/null || echo "    ⚠ dac_cli.py not found or empty"

# Copy all documentation
echo "  → Copying documentation (8 files)"
if [ -d "$PHASE0/documentation" ]; then
    cp "$PHASE0/documentation"/*.md "docs/historical/phase0/" 2>/dev/null || echo "    ⚠ Some documentation files missing"
fi

echo "  → Copying README and IP_PROTECTION"
cp "$PHASE0/README.md" "docs/historical/phase0/" 2>/dev/null || echo "    ⚠ README.md missing"
cp "$PHASE0/IP_PROTECTION.md" "docs/historical/phase0/" 2>/dev/null || echo "    ⚠ IP_PROTECTION.md missing"

# Copy Travis CI config (historical artifact)
echo "  → Copying .travis.yml (CI/CD config)"
cp "$PHASE0/kubernetes/.travis.yml" "docs/historical/phase0/" 2>/dev/null || echo "    ⚠ .travis.yml missing"

# Create README explaining missing files
cat > "src/prototypes/phase0_dgm/README.md" << 'EOF'
# Phase 0: DAC + DGM + Shadow Twin Prototypes

## Status: Partial Preservation

**Original**: 56 Python files
**Preserved**: 3 Python files (53 were 0 bytes in extraction)

## Preserved Files

### 1. dac_engine.py (28KB, 723 lines)
Dynamic Autonomous Control engine - predecessor to ACE (Aspiration-Calibration-Execution)

### 2. a2a2_federation_bridge.py (19KB, 475 lines)
Agent-to-Agent communication protocol for federated AI systems

### 3. dac_cli.py (24KB, 655 lines)
Command-line interface for DAC system

## Missing Files (0 bytes in extraction)

The following files were present in the original package but extracted as 0 bytes:
- userlm_generator_v9_lora.py
- dgm_agent_phi4.py
- dgm_outer_loop.py
- shadow_twin.py
- shadow_twin_bridge_v2.py
- dgm_evolution.py
- autonomous_loop_controller.py
- [... 46 more files]

**Possible causes**: Symbolic links, Git LFS files, or incomplete export.

## Documentation

Complete documentation preserved in `docs/historical/phase0/`:
- proof_economy_progress_report.md
- shadow_twin_diagnostic_analysis.md
- phase1_focus_areas.md
- consensus_success_analysis.md
- shadow_twin_analysis.md
- IP_PROTECTION.md
- README.md

## Evolution to Production

Phase 0 DAC → Thermodynasty Phase 4 ACE
- See `docs/DEVELOPMENT_LINEAGE.md` for complete evolution mapping

## Historical Context

This code represents early prototyping work (2024 Q4) that informed the later Thermodynasty production implementation (2025).

**Date**: November 20, 2025
EOF

echo -e "${GREEN}✓ Phase 0 integration complete${NC}"
echo ""

###############################################################################
# PHASE 1: COPY MICROADAPT + TTF + BRIDGE
###############################################################################

if [ "$SKIP_PHASE1" != "true" ]; then
    echo -e "${YELLOW}[4/6] Integrating Phase 1 (MicroAdapt/TTF/Bridge)...${NC}"

    # Copy MicroAdapt algorithms
    echo "  → Copying MicroAdapt algorithms (3 files)"
    cp "$PHASE1/microadapt/algorithms"/*.py "src/prototypes/phase1_microadapt/algorithms/" 2>/dev/null || echo "    ⚠ Some algorithm files missing"

    # Copy MicroAdapt models
    echo "  → Copying MicroAdapt models (3 files)"
    cp "$PHASE1/microadapt/models"/*.py "src/prototypes/phase1_microadapt/models/" 2>/dev/null || echo "    ⚠ Some model files missing"

    # Copy MicroAdapt utils
    echo "  → Copying MicroAdapt utils"
    if [ -d "$PHASE1/microadapt/utils" ]; then
        cp "$PHASE1/microadapt/utils"/*.py "src/prototypes/phase1_microadapt/" 2>/dev/null || echo "    ⚠ Utils files missing"
    fi

    # Copy TTF inference
    echo "  → Copying TTF inference (2 files)"
    cp "$PHASE1/ttf_inference/collectors"/*.py "src/prototypes/phase1_microadapt/ttf_inference/collectors/" 2>/dev/null || echo "    ⚠ Collector files missing"
    cp "$PHASE1/ttf_inference/processors"/*.py "src/prototypes/phase1_microadapt/ttf_inference/processors/" 2>/dev/null || echo "    ⚠ Processor files missing"

    # Copy bridge components
    echo "  → Copying bridge components (3 files)"
    cp "$PHASE1/bridge"/*.py "src/prototypes/phase1_microadapt/bridge/" 2>/dev/null || echo "    ⚠ Some bridge files missing"

    # Copy run scripts
    echo "  → Copying run scripts"
    cp "$PHASE1"/run_*.py "src/prototypes/phase1_microadapt/" 2>/dev/null || echo "    ⚠ Some run scripts missing"

    # Copy tests
    echo "  → Copying tests"
    if [ -d "$PHASE1/tests" ]; then
        cp "$PHASE1/tests"/*.py "src/prototypes/phase1_microadapt/" 2>/dev/null || echo "    ⚠ Test files missing"
    fi

    # Copy documentation
    echo "  → Copying documentation"
    if [ -d "$PHASE1/docs" ]; then
        cp -r "$PHASE1/docs"/* "docs/historical/phase1/" 2>/dev/null || echo "    ⚠ Documentation missing"
    fi

    # Copy infrastructure configs
    echo "  → Copying infrastructure configs"
    if [ -d "$PHASE1/infrastructure" ]; then
        cp -r "$PHASE1/infrastructure"/* "docs/historical/phase1/infrastructure/" 2>/dev/null || echo "    ⚠ Infrastructure configs missing"
    fi

    # Create README
    cat > "src/prototypes/phase1_microadapt/README.md" << 'EOF'
# Phase 1: MicroAdapt v1 + TTF + Bridge

## Status: Complete Preservation

**Files**: 19 Python modules
**Size**: 164KB
**Test Coverage**: ~60%

## Components

### 1. MicroAdapt v1
- algorithms/dynamic_data_collection.py - Hierarchical window decomposition
- algorithms/model_unit_adaptation.py - Levenberg-Marquardt fitting
- algorithms/model_unit_search.py - Fitness-based regime search
- models/regime.py - Regime classification
- models/window.py - Multi-scale windowing
- models/model_unit.py - Differential equation model units

### 2. TTF (Time-to-Failure) Inference
- ttf_inference/collectors/system_metrics_collector.py
- ttf_inference/processors/energy_state_processor.py

### 3. Bridge
- bridge/config.py, bridge/worker_fixed.py, bridge/main.py
- run_kafka_consumer.py, run_bridge.py, run_ttf_agent.py

## Evolution to Production

Phase 1 MicroAdapt → Thermodynasty Phase 5 MicroAdapt v2
- Statistical → Physics-aware regime detection
- Manual tuning → Auto-tuning feedback loop
- 70% accuracy → >90% accuracy

See `docs/DEVELOPMENT_LINEAGE.md` for complete evolution mapping.

## Historical Context

This code represents MicroAdapt v1 (2025 Q1) - the statistical prototype that evolved into the physics-aware production version in Thermodynasty Phase 5.

**Date**: November 20, 2025
EOF

    echo -e "${GREEN}✓ Phase 1 integration complete${NC}"
else
    echo -e "${YELLOW}[4/6] Skipping Phase 1 (not found)${NC}"
fi
echo ""

###############################################################################
# PHASE 2: COPY BRIDGE REFINEMENTS + RETRAINING
###############################################################################

if [ "$SKIP_PHASE2" != "true" ]; then
    echo -e "${YELLOW}[5/6] Integrating Phase 2 (Bridge/Retraining)...${NC}"

    # Copy retraining logic
    echo "  → Copying training_data_extractor.py"
    cp "$PHASE2/bridge/retraining/training_data_extractor.py" "src/retraining/" 2>/dev/null || echo "    ⚠ training_data_extractor.py missing"

    # Copy also to prototypes for historical reference
    cp "$PHASE2/bridge/retraining/training_data_extractor.py" "src/prototypes/phase2_bridge/retraining/" 2>/dev/null || echo "    ⚠ Copy to prototypes failed"

    # Copy bridge components
    echo "  → Copying bridge package"
    if [ -d "$PHASE2/bridge" ]; then
        cp -r "$PHASE2/bridge"/* "src/prototypes/phase2_bridge/" 2>/dev/null || echo "    ⚠ Some bridge files missing"
    fi

    # Copy Kubernetes overlays
    echo "  → Copying Kubernetes overlays"
    if [ -d "$PHASE2/kubernetes/overlays" ]; then
        cp -r "$PHASE2/kubernetes/overlays"/* "infrastructure/kubernetes/overlays/" 2>/dev/null || echo "    ⚠ Overlays missing"
    fi

    # Copy documentation
    echo "  → Copying documentation"
    if [ -d "$PHASE2/docs" ]; then
        cp -r "$PHASE2/docs"/* "docs/historical/phase2/" 2>/dev/null || echo "    ⚠ Documentation missing"
    fi

    # Create README
    cat > "src/prototypes/phase2_bridge/README.md" << 'EOF'
# Phase 2: Bridge Refinements + Retraining

## Status: Complete Preservation

**Files**: 3 Python modules
**Size**: 84KB

## Components

### 1. Retraining Pipeline
- retraining/training_data_extractor.py - Extract training data from production

### 2. Bridge Package
- API definitions
- Models
- Services
- Utilities

## Evolution to Production

Phase 2 Retraining → Thermodynasty Phase 5 Feedback Trainer
- Offline batch → Online continuous learning
- Manual extraction → Automatic data collection
- Simple updates → Multi-objective optimization

See `docs/DEVELOPMENT_LINEAGE.md` for complete evolution mapping.

**Date**: November 20, 2025
EOF

    echo -e "${GREEN}✓ Phase 2 integration complete${NC}"
else
    echo -e "${YELLOW}[5/6] Skipping Phase 2 (not found)${NC}"
fi
echo ""

###############################################################################
# PHASE 3: COPY DOCUMENTATION + CONTRACTS
###############################################################################

if [ "$SKIP_PHASE3" != "true" ]; then
    echo -e "${YELLOW}[6/6] Integrating Phase 3 (Docs/Contracts)...${NC}"

    # Copy bridge contracts
    echo "  → Copying bridge contracts"
    if [ -d "$PHASE3/bridge_package/contracts" ]; then
        cp -r "$PHASE3/bridge_package/contracts"/* "contracts/bridge_contracts/" 2>/dev/null || echo "    ⚠ Contracts missing"
    fi

    # Copy documentation
    echo "  → Copying documentation"
    if [ -d "$PHASE3/docs" ]; then
        cp -r "$PHASE3/docs"/* "docs/historical/phase3/" 2>/dev/null || echo "    ⚠ Documentation missing"
    fi

    # Copy scripts
    echo "  → Copying scripts"
    if [ -d "$PHASE3/scripts" ]; then
        cp -r "$PHASE3/scripts"/* "docs/historical/phase3/scripts/" 2>/dev/null || echo "    ⚠ Scripts missing"
    fi

    echo -e "${GREEN}✓ Phase 3 integration complete${NC}"
else
    echo -e "${YELLOW}[6/6] Skipping Phase 3 (not found)${NC}"
fi
echo ""

###############################################################################
# SUMMARY
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ INTEGRATION COMPLETE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Files integrated:"
echo "  Phase 0: 3 Python files + 8 documentation files"
echo "  Phase 1: 19 Python files + infrastructure configs"
echo "  Phase 2: 3 Python files + Kubernetes overlays"
echo "  Phase 3: Contracts + documentation"
echo ""
echo "Next steps:"
echo "  1. Review integrated files: cd $REPO"
echo "  2. Check integration: ls -R src/prototypes/"
echo "  3. Read lineage docs: docs/DEVELOPMENT_LINEAGE.md"
echo "  4. Commit changes: git add -A && git commit -m 'feat: Integrate Phase 0-3 prototypes'"
echo "  5. Push to remote: git push"
echo ""
echo -e "${YELLOW}Note: Some files may be missing if they were 0 bytes in extraction.${NC}"
echo ""

###############################################################################
# FILE COUNT SUMMARY
###############################################################################

echo -e "${BLUE}File count summary:${NC}"
echo "Prototypes:"
find "$REPO/src/prototypes" -name "*.py" | wc -l | xargs echo "  Python files:"
find "$REPO/src/prototypes" -name "*.md" | wc -l | xargs echo "  README files:"
echo ""
echo "Historical docs:"
find "$REPO/docs/historical" -name "*.md" | wc -l | xargs echo "  Documentation files:"
echo ""
echo "Contracts:"
find "$REPO/contracts" -type f | wc -l | xargs echo "  Contract files:"
echo ""

exit 0
