# Gaussian-Splatting-Monitor Insights

**Repository:** https://github.com/RongLiu-Leo/Gaussian-Splatting-Monitor  
**Stars:** 246 | **Forks:** 16  
**Purpose:** Monitor Gaussian Splatting with additional real-time viewable and differentiable outputs

---

## Key Insights for Capsule Overlays

This repository demonstrates **production-ready patterns** for extending 3DGS with custom overlays and real-time monitoring - exactly what we need for capsule visualization!

---

## Architecture Patterns

### 1. Expandable Viewer System

**Pattern:** Customizable render items list

```python
# arguments/__init__.py
self.render_items = ['RGB', 'Alpha', 'Depth', 'Normal', 'Curvature', 'Edge']
```

**Implementation:** `utils/image_utils.py` - `render_net_image()` function

**Key Insight:** We can add 'Capsules' to render_items and implement capsule overlay rendering in the same pattern!

### 2. Metrics Viewer Integration

**Pattern:** Real-time metrics display in viewer (no terminal switching)

```python
# train.py or view.py
metrics_dict = {
    "iteration": iteration,
    "number of gaussians": gaussians.get_xyz.shape[0],
    "loss": loss,
    # Add more metrics as needed
}
```

**Key Insight:** We can display capsule metrics (count, status, priority) in the viewer using the same pattern!

### 3. Five Additional Features

**Implemented Features:**
1. **Alpha:** Transparency/opacity visualization
2. **Depth:** Distance from camera
3. **Normal:** Surface normal vectors
4. **Curvature:** Surface curvature analysis
5. **Edge:** Edge detection

**Key Insight:** These demonstrate how to render additional data layers on top of 3DGS - we'll use this for capsule overlays!

---

## Applications (Production Examples)

### 1. AtomGS
- **Paper:** "Atomizing Gaussian Splatting for High-Fidelity Radiance Field"
- **Relevance:** High-fidelity rendering for industrial equipment

### 2. 2D Gaussian Splatting
- **Paper:** "2D Gaussian Splatting for Geometrically Accurate Radiance Fields"
- **Relevance:** Geometric accuracy for precise capsule positioning

### 3. Feature 3DGS
- **Paper:** "Feature 3DGS: Supercharging 3D Gaussian Splatting to Enable Distilled Feature Fields"
- **Relevance:** Feature fields for capsule semantic understanding

---

## Technical Implementation

### Viewer Architecture

**Components:**
1. **SIBR_remoteGaussian_app_rwdi.exe** - Interactive viewer
2. **train.py** - Training with real-time monitoring
3. **view.py** - Viewing trained models with custom overlays

**Workflow:**
```bash
# 1. Start viewer
<path>/bin/SIBR_remoteGaussian_app_rwdi.exe

# 2. Monitor training
python train.py -s <dataset_path>

# 3. View trained model
python view.py -s <dataset_path> -m <model_path>
```

### Custom Render Items

**Format Requirements:**
- Single-channel: `(1, h, w)` → auto-converts to turbo colormap
- RGB: `(3, h, w)` → direct rendering

**Implementation Location:**
- Configuration: `arguments/__init__.py`
- Rendering logic: `utils/image_utils.py` - `render_net_image()`

---

## Production Patterns for Capsule Overlays

### Pattern 1: Capsule as Render Item

```python
# arguments/__init__.py
self.render_items = ['RGB', 'Alpha', 'Depth', 'Capsules']
```

```python
# utils/image_utils.py
def render_net_image(render_pkg, render_items, gaussians, pipe, background):
    # ... existing code ...
    
    if 'Capsules' in render_items:
        # Render capsule overlays at 3D positions
        capsule_overlay = render_capsules(
            gaussians,
            capsule_positions,
            capsule_data,
            viewpoint_camera
        )
        net_image_dict['Capsules'] = capsule_overlay
    
    return net_image_dict
```

### Pattern 2: Capsule Metrics in Viewer

```python
# view.py
metrics_dict = {
    "iteration": iteration,
    "gaussians": gaussians.get_xyz.shape[0],
    "capsules_total": len(capsules),
    "capsules_critical": len([c for c in capsules if c.status == 'critical']),
    "capsules_warning": len([c for c in capsules if c.status == 'warning']),
    "capsules_active": len([c for c in capsules if c.status == 'active']),
}
```

### Pattern 3: Real-Time Capsule Updates

**WebSocket Integration:**
```python
# view.py
import asyncio
import websockets

async def capsule_update_handler(websocket):
    async for message in websocket:
        capsule_update = json.loads(message)
        update_capsule_overlay(capsule_update)
        refresh_viewer()

# Run alongside viewer
asyncio.run(capsule_update_handler(ws_url))
```

---

## Setup Requirements

### CUDA Version
- **Required:** CUDA SDK 11 (not 12)
- **Reason:** Compatibility with diff-gaussian-rasterization

### Dependencies
```bash
# Ubuntu 22.04
sudo apt install -y \
  libglew-dev \
  libassimp-dev \
  libboost-all-dev \
  libgtk-3-dev \
  libopencv-dev \
  libglfw3-dev \
  libavdevice-dev \
  libavcodec-dev \
  libeigen3-dev \
  libxxf86vm-dev \
  libembree-dev

# Build viewer
cd SIBR_viewers
cmake -Bbuild . -DCMAKE_BUILD_TYPE=Release
cmake --build build -j24 --target install
```

---

## Key Takeaways for Week 15

1. **Expandable Viewer Pattern:** Add 'Capsules' to render_items
2. **Metrics Integration:** Display capsule stats in viewer
3. **Custom Render Layers:** Implement capsule overlay rendering
4. **Real-Time Updates:** WebSocket integration for live capsule updates
5. **Production-Ready:** Multiple papers using this codebase (proven pattern)

---

## Implementation Strategy

### Phase 1: Integrate Reall3DViewer (Week 15 Day 3-4)
- Use Reall3DViewer NPM package (Three.js-based)
- Load .spx models from Shadow Twins
- Add capsule overlay rendering to scene

### Phase 2: Add Capsule Render Layer (Week 15 Day 5-6)
- Implement capsule overlay system (inspired by GS Monitor)
- Add capsule metrics to viewer
- WebSocket integration for real-time updates

### Phase 3: AR/VR Interaction (Week 15 Day 7)
- Add raycasting for capsule selection
- Implement gesture controls
- Test on mobile AR and VR headsets

---

**Status:** Research complete. Ready to implement Week 15 Day 3-4 with production-ready patterns.
