# Phase 5 EIL - Research Integration

This document describes the Priority 1 research integrations for Phase 5 Energy Intelligence Layer, implementing insights from 4 research papers to enhance EIL capabilities.

## Overview

**Status**: Priority 1 (Foundation) - Implementation Complete ✅
**Integration Date**: 2025-11-13
**Components**: 4 modules + 1 integration layer

## Research Papers Integrated

1. **LeJEPA** (arXiv:2511.08544v2)
   - Optimal self-supervised learning with isotropic Gaussian embeddings
   - O(N) SIGReg loss for theoretically optimal representations
   - Encoder pretraining for regime detection

2. **Egocentric-10K** (HuggingFace: builddotai/Egocentric-10K)
   - 10,050 hours of factory videos from 85 factories
   - 1.08 billion frames, 16.4TB dataset
   - Physics pattern extraction for industrial regimes

3. **PhysWorld** (arXiv:2511.07416v1)
   - 4D video reconstruction (3D space + time)
   - Physics-grounded validation with signed distance fields (SDF)
   - 82% success rate on contact-rich manipulation

4. **RealDeepResearch** (arXiv:2510.20809v1)
   - Continuous ArXiv paper ingestion
   - Perspective-based decomposition (I-M-O-W-R framework)
   - Knowledge graph construction for continuous learning

## Directory Structure

```
phase5/
├── pretraining/
│   ├── lejêpa_encoder.py              # LeJEPA implementation
│   └── egocentric_10k_pipeline.py     # Egocentric-10K data loader
├── reconstruction/
│   └── physworld_4d.py                # PhysWorld 4D reconstruction
├── research/
│   └── realdeepresearch_crawler.py    # ArXiv paper crawler
├── integration/
│   └── research_enhanced_eil.py       # Integration layer
├── config/
│   └── research_integration_config.yaml  # Configuration
├── docs/
│   └── research_integration_analysis.md  # Full analysis (1,200 lines)
├── research_requirements.txt           # Dependencies
└── RESEARCH_INTEGRATION_README.md      # This file
```

## Components

### 1. LeJEPA Encoder (`lejêpa_encoder.py`)

**Purpose**: Optimal self-supervised learning for regime detection

**Key Features**:
- Vision Transformer backbone (ViT-B/16 or ViT-L/14)
- SIGReg loss with O(N) complexity
- Isotropic Gaussian embeddings
- Epps-Pulley statistical test for isotropy validation

**Usage**:
```python
from phase5.pretraining.lejêpa_encoder import LeJEPA, LeJEPAConfig, LeJEPATrainer

# Initialize
config = LeJEPAConfig(
    backbone='ViT-B/16',
    hidden_dim=768,
    embedding_dim=256,
    sigreg_lambda=0.01
)
trainer = LeJEPATrainer(config)
state = trainer.create_train_state(learning_rate=1e-4)

# Encode images
images = jnp.ones((batch_size, 224, 224, 3))
embeddings = trainer.model.apply({'params': state.params}, images, train=False)
```

**Test**:
```bash
cd Thermodynasty
python phase5/pretraining/lejêpa_encoder.py
```

### 2. Egocentric-10K Pipeline (`egocentric_10k_pipeline.py`)

**Purpose**: Stream factory videos and extract physics patterns

**Key Features**:
- Streaming API for 16.4TB dataset (no full download needed)
- Factory-specific filtering (85 factories)
- Contact density estimation via optical flow
- Energy map proxy extraction from motion

**Usage**:
```python
from phase5.pretraining.egocentric_10k_pipeline import EgocentricDataLoader, EgocentricConfig

# Initialize
config = EgocentricConfig(
    cache_dir="/mnt/20tb_drive/egocentric10k",  # Your 20TB drive
    streaming=True
)
loader = EgocentricDataLoader(config)
loader.initialize()

# Stream factory videos
for video in loader.stream_factory(factory_id=0, num_videos=100):
    print(f"Video: {video.video_id}, Frames: {video.frames.shape}")

# Extract physics
from phase5.pretraining.egocentric_10k_pipeline import FactoryPhysicsExtractor
extractor = FactoryPhysicsExtractor(loader)
training_samples = extractor.process_factory_for_eil(factory_id=0, num_videos=100)
```

**Test**:
```bash
python phase5/pretraining/egocentric_10k_pipeline.py
```

### 3. PhysWorld 4D Reconstruction (`physworld_4d.py`)

**Purpose**: Physics-grounded scene reconstruction from video

**Key Features**:
- Depth estimation from RGB (monocular/stereo)
- Gravity alignment for canonical scenes
- Signed Distance Field (SDF) for collision detection
- Physical property estimation (mass, friction, contact density)

**Usage**:
```python
from phase5.reconstruction.physworld_4d import PhysWorldReconstructor, ReconstructionConfig

# Initialize
config = ReconstructionConfig(
    grid_resolution=64,
    gravity_alignment=True
)
reconstructor = PhysWorldReconstructor(config)

# Reconstruct scene
video_frames = np.random.randint(0, 255, (30, 224, 224, 3), dtype=np.uint8)
scene_4d = reconstructor.reconstruct_scene_4d(video_frames)

# Extract physics-grounded energy map
energy_map = reconstructor.extract_energy_map(scene_4d, grid_size=64)
```

**Test**:
```bash
python phase5/reconstruction/physworld_4d.py
```

### 4. RealDeepResearch Crawler (`realdeepresearch_crawler.py`)

**Purpose**: Continuous research paper integration from ArXiv

**Key Features**:
- Daily ArXiv crawling (cs.LG, cs.AI, cs.RO, cs.CV, physics.comp-ph)
- Perspective decomposition (Introduction, Methods, Observations, What next, Related work)
- Embedding-based clustering
- Knowledge graph export

**Usage**:
```python
from phase5.research.realdeepresearch_crawler import ResearchIntegrator

# Initialize
integrator = ResearchIntegrator(cache_dir="./arxiv_cache")

# Daily update
stats = integrator.daily_update(
    categories=["cs.LG", "cs.AI"],
    days_back=7,
    max_papers=50
)

# Search relevant papers
results = integrator.find_relevant_papers(
    query="self-supervised learning physics prediction",
    top_k=5
)

# Export knowledge graph
integrator.export_knowledge_graph("./knowledge_graph.json")
```

**Test**:
```bash
python phase5/research/realdeepresearch_crawler.py
```

### 5. Research-Enhanced EIL (`research_enhanced_eil.py`)

**Purpose**: Integration layer connecting all research components with EIL

**Key Features**:
- Wraps base EIL with research enhancements
- Confidence boosting from multiple sources
- Pretraining pipeline for LeJEPA on Egocentric-10K
- Research update integration

**Usage**:
```python
from phase5.integration.research_enhanced_eil import (
    ResearchEnhancedEIL,
    ResearchEnhancementConfig
)
from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer

# Create base EIL
base_eil = EnergyIntelligenceLayer(regime_detector_checkpoint=None, ...)

# Create research enhancement config
config = ResearchEnhancementConfig(
    use_lejêpa_encoder=True,
    use_factory_physics=True,
    use_physworld=True,
    use_research_updates=True
)

# Create research-enhanced EIL
enhanced_eil = ResearchEnhancedEIL(base_eil=base_eil, config=config)

# Process with enhancements
decision = enhanced_eil.process(
    energy_map=energy_map,
    domain="factory_assembly",
    cluster="cluster-1",
    node="node-1",
    video_frames=video_frames  # Optional for PhysWorld
)
```

**Test**:
```bash
python phase5/integration/research_enhanced_eil.py
```

## Installation

### Step 1: Install Dependencies

```bash
cd Thermodynasty
pip install -r phase5/research_requirements.txt
```

**Note**: Some dependencies are large:
- `torch` + `torchvision`: ~2GB
- `open3d`: ~500MB
- `transformers` + `datasets`: ~1GB

### Step 2: Configure Research Integration

Edit `phase5/config/research_integration_config.yaml`:

```yaml
# Enable components as needed
lejêpa:
  enabled: false  # Enable after pretraining

egocentric_10k:
  enabled: false  # Enable when dataset downloaded
  cache_dir: "/mnt/20tb_drive/egocentric10k"  # Your path

physworld:
  enabled: false  # Enable for video inputs

realdeepresearch:
  enabled: false  # Enable for continuous learning
```

### Step 3: Test Individual Components

Run tests for each component:

```bash
python phase5/pretraining/lejêpa_encoder.py
python phase5/pretraining/egocentric_10k_pipeline.py
python phase5/reconstruction/physworld_4d.py
python phase5/research/realdeepresearch_crawler.py
python phase5/integration/research_enhanced_eil.py
```

## Implementation Roadmap

Based on `phase5/docs/research_integration_analysis.md`:

### ✅ Priority 1 (Complete) - Foundation
- [x] Implement LeJEPA encoder architecture
- [x] Set up Egocentric-10K data pipeline (streaming)
- [x] Create PhysWorld reconstruction module
- [x] Build RealDeepResearch paper crawler
- [x] Integration layer connecting all components

### 🔄 Priority 2 (Next) - Integration
- [ ] Pretrain LeJEPA on Egocentric-10K subset (10 factories)
- [ ] Extract physics from 1,000 factory videos
- [ ] Integrate pretrained encoder into RegimeDetector
- [ ] Deploy research crawler for daily paper ingestion

### 📋 Priority 3 (Future) - Enhancement
- [ ] Full Egocentric-10K pretraining (85 factories, 10K hours)
- [ ] Physics-grounded proof validator enhancement
- [ ] Knowledge graph with 10K+ research papers
- [ ] Feedback trainer with research-guided adaptation

### 🚀 Priority 4 (Production) - Deployment
- [ ] Multi-modal fusion (egocentric + energy maps + research)
- [ ] Real-time factory deployment with PhysWorld
- [ ] Automated research discovery → EIL update pipeline
- [ ] Continuous learning from factory deployments

## Hardware Requirements

### Priority 1 (Testing)
- **GPU**: 1x RTX 4090 / A100 (16GB+ VRAM)
- **RAM**: 32GB
- **Storage**: 1TB (for code + small dataset samples)

### Priority 2 (Initial Pretraining)
- **GPU**: 2-4x A100 40GB
- **RAM**: 128GB
- **Storage**: 5TB (10 factories + checkpoints)
- **Time**: ~3 days

### Priority 3 (Full Pretraining)
- **GPU**: 8x A100 80GB (distributed training)
- **RAM**: 512GB
- **Storage**: 25TB (20TB dataset + 5TB checkpoints)
- **Time**: ~14 days

## Dataset Information

### Egocentric-10K
- **Size**: 16.4TB (H.265 compressed)
- **Frames**: 1.08 billion
- **Duration**: 10,050 hours
- **Factories**: 85
- **Workers**: 2,138
- **Tasks**: 450+ types
- **Format**: WebDataset (streaming-friendly)
- **Access**: HuggingFace (`builddotai/Egocentric-10K`)

**Download** (when ready):
```python
from datasets import load_dataset

# Streaming (no download)
dataset = load_dataset("builddotai/Egocentric-10K", streaming=True)

# Full download (16.4TB!)
dataset = load_dataset(
    "builddotai/Egocentric-10K",
    cache_dir="/mnt/20tb_drive/egocentric10k"
)
```

## Performance Metrics

### LeJEPA
- **Isotropy Score**: Target < 0.1 (Epps-Pulley test)
- **Training Loss**: SIGReg + prediction loss
- **Downstream Accuracy**: Regime detection improvement

### Egocentric-10K
- **Contact Density**: 0.0-1.0 (optical flow variance)
- **Energy Map Quality**: Correlation with ground truth
- **Processing Speed**: ~1 video/sec

### PhysWorld
- **Reconstruction Accuracy**: Mean IoU on 3D scenes
- **Physics Fidelity**: % trajectories matching real data
- **Inference Speed**: ~2 FPS for 1080p video

### RealDeepResearch
- **Papers Ingested**: Target 50/day
- **Clustering Quality**: Silhouette score
- **Relevance**: Top-K precision for EIL queries

## Troubleshooting

### Issue: Egocentric-10K download too slow
**Solution**: Use streaming API, don't download full 16.4TB
```python
config = EgocentricConfig(streaming=True)  # Default
```

### Issue: Out of GPU memory during LeJEPA pretraining
**Solution**: Reduce batch size or use ViT-B/16 instead of ViT-L/14
```yaml
lejêpa:
  backbone: "ViT-B/16"  # Smaller model
  training:
    batch_size: 16  # Reduce from 32
    gradient_checkpointing: true
```

### Issue: PhysWorld reconstruction too slow
**Solution**: Reduce grid resolution
```yaml
physworld:
  reconstruction:
    grid_resolution: 32  # Reduce from 64
```

### Issue: ArXiv API rate limiting
**Solution**: Add delays between requests (already implemented)
```python
time.sleep(3)  # 3 seconds between API calls
```

## Citation

If you use this research integration in your work, please cite the original papers:

```bibtex
@article{lejêpa2025,
  title={LeJEPA: Optimal Self-Supervised Learning with Isotropic Gaussians},
  journal={arXiv:2511.08544v2},
  year={2025}
}

@dataset{egocentric10k2025,
  title={Egocentric-10K: 10,000 Hours of Factory Videos},
  url={https://huggingface.co/datasets/builddotai/Egocentric-10K},
  year={2025}
}

@article{physworld2025,
  title={PhysWorld: Physics-Grounded Robot Learning},
  journal={arXiv:2511.07416v1},
  year={2025}
}

@article{realdeepresearch2025,
  title={RealDeepResearch: Continuous Research Integration},
  journal={arXiv:2510.20809v1},
  year={2025}
}
```

## Next Steps

1. **Test all components** with the provided test scripts
2. **Configure** `research_integration_config.yaml` for your environment
3. **Download Egocentric-10K** (optional, streaming works without download)
4. **Run Priority 2 pretraining** when ready (see roadmap above)
5. **Monitor metrics** to validate improvements

## Support

- **Full Analysis**: See `phase5/docs/research_integration_analysis.md` (1,200 lines)
- **Deployment Commands**: See `DEPLOYMENT_COMMANDS.md`
- **Executive Summary**: See `PHASE5_EXECUTIVE_SUMMARY.md`

---

**Status**: Priority 1 Implementation Complete ✅
**Date**: 2025-11-13
**Ready for**: Priority 2 (Initial Pretraining)
