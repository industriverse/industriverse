# Industriverse Project Structure

## Overview

This document describes the unified project structure after the Grand Unification integration.

## Directory Structure

```
industriverse/
├── .github/
│   └── workflows/
│       └── discovery-loop-ci.yml          # CI/CD for discovery loop
│
├── Thermodynasty/                         # TOP LAYER: Energy Intelligence Layer
│   ├── phase4/                            # Phase 4: ACE/NVP
│   │   ├── ace/                           # Agentic Context Engineering
│   │   └── nvp/                           # Neural Vector Processor
│   └── phase5/                            # Phase 5: EIL (Current)
│       ├── core/
│       │   ├── energy_intelligence_layer.py    # Master orchestrator
│       │   ├── market_engine.py                # Proof economy
│       │   └── regime_detector.py              # Regime detection
│       ├── diffusion/                     # Energy-based diffusion
│       ├── api/                           # FastAPI gateway
│       └── deploy/                        # Kubernetes/Helm configs
│
├── src/                                   # BOTTOM LAYER: Industriverse Foundation
│   ├── data_layer/                        # Layer 1: Data infrastructure
│   ├── core_ai_layer/                     # Layer 2: AI services
│   │   ├── discovery_loop/                # MIDDLE LAYER: Discovery services
│   │   │   ├── orchestrator.py            # 6-phase orchestrator
│   │   │   └── services/
│   │   │       ├── dgm_service.py         # Deep Genetic Modification
│   │   │       ├── t2l_service.py         # Text-to-LoRA
│   │   │       ├── asal_service.py        # Consciousness scoring
│   │   │       └── trifecta_service.py    # UserLM + RND1 + ACE
│   │   ├── distributed_intelligence/      # Distributed agents
│   │   └── llm_service/                   # LLM infrastructure
│   ├── generative_layer/                  # Layer 3: Generative services
│   ├── application_layer/                 # Layer 4: Domain applications
│   ├── protocol_layer/                    # Layer 5: Protocols
│   │   ├── protocols/
│   │   │   ├── genetic/
│   │   │   │   └── pk_alpha.py            # Operational genetic algorithm
│   │   │   └── obmi/                      # NEW: Quantum validation
│   │   │       └── obmi_service.py        # 5 quantum operators
│   │   └── blockchain/                    # UTID anchoring
│   ├── workflow_automation_layer/         # Layer 6: Workflows
│   ├── ui_ux_layer/                       # Layer 7: UI components
│   ├── security_compliance_layer/         # Layer 8: Security
│   ├── deployment_operations_layer/       # Layer 9: Deployment
│   └── overseer_system/                   # Layer 10: Overseer
│       └── intelligence_market/           # Proof economy
│
├── docs/                                  # Documentation
│   ├── DISCOVERY_LOOP_INTEGRATION.md      # Integration guide
│   ├── INTEGRATION_ASSESSMENT.md          # Assessment document
│   └── GITHUB_ENHANCEMENT_STRATEGY.md     # Strategy document
│
├── tests/                                 # Test suite
│   ├── unit/                              # Unit tests
│   ├── integration/                       # Integration tests
│   └── e2e/                               # End-to-end tests
│
├── deployments/                           # Deployment configurations
│   ├── kubernetes/                        # K8s manifests
│   ├── docker/                            # Dockerfiles
│   └── helm/                              # Helm charts
│
└── PROJECT_STRUCTURE.md                   # This file
```

## Layer Interactions

### Top → Middle
```
Thermodynasty EIL
    ↓ (receives final results)
Discovery Loop Orchestrator
```

### Middle → Bottom
```
Discovery Loop Services
    ↓ (uses infrastructure)
Industriverse 10 Layers
```

### Service Dependencies

**Discovery Loop Orchestrator depends on:**
- DGM Service → pk_alpha (protocol_layer)
- T2L Service → LLM Service (core_ai_layer)
- ASAL Service → Monitoring (core_ai_layer)
- OBMI Service → (protocol_layer)
- Trifecta → Distributed Intelligence (core_ai_layer)

**Thermodynasty EIL depends on:**
- Discovery Loop Orchestrator (core_ai_layer)
- Market Engine → Intelligence Market (overseer_system)
- Proof Validator → Blockchain (protocol_layer)

## Key Files

### Configuration
- `Thermodynasty/phase5/config.yaml` - EIL configuration
- `src/core_ai_layer/discovery_loop/config.py` - Discovery loop config

### Entry Points
- `Thermodynasty/phase5/api/eil_gateway.py` - EIL API
- `src/core_ai_layer/discovery_loop/orchestrator.py` - Discovery loop entry

### Documentation
- `DISCOVERY_LOOP_INTEGRATION.md` - Complete integration guide
- `COLLABORATION_WORKFLOW.md` - Development workflow
- `PROJECT_STRUCTURE.md` - This file

## Development Workflow

1. **Local Development:**
   - Clone repository
   - Install dependencies: `pip install -r requirements.txt`
   - Run tests: `pytest tests/`

2. **Making Changes:**
   - Create feature branch from `feature/grand-unification`
   - Make changes
   - Run linters: `black .` and `isort .`
   - Commit and push

3. **CI/CD:**
   - GitHub Actions runs automatically
   - Linting, type checking, and tests
   - Build Docker images
   - Deploy to staging (if on integration branch)

4. **Pull to Local:**
   - `git pull origin feature/grand-unification`
   - Test locally
   - Provide feedback

## Next Steps

1. **Wire up MacBook services** to actual endpoints
2. **Deploy to AWS EKS** for production
3. **Set up Manus.im scheduled tasks** for automation
4. **Create client adaptation templates**

## References

- GitHub Repository: `https://github.com/industriverse/industriverse`
- Branch: `feature/grand-unification`
- Documentation: `/docs/`
