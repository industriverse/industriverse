# Reall3DViewer Repository Overview

**Repository:** https://github.com/reall3d-com/Reall3dViewer  
**NPM Package:** `@reall3d/reall3dviewer`  
**Stars:** 407 | **Forks:** 43 | **Latest:** v2.3.0

---

## Key Features

1. **Format Support:**
   - `.ply` (standard point cloud)
   - `.splat` (Gaussian Splatting format)
   - `.spx` (Reall3D compressed format - **PRODUCTION TARGET**)
   - `.spz` (v2, v3)
   - `.sog` (v1, v2)

2. **Built on Three.js:**
   - Full Three.js scene integration
   - Custom SplatMesh for 3DGS rendering
   - WebGL 2.0 rendering

3. **Features:**
   - Mark and measurement tools
   - Text watermarking
   - 1st to 3rd degree spherical harmonics
   - Map-integrated model rendering
   - Per-model settings via `*.meta.json`
   - Built-in rendering quality levels (v2.0.0+)
   - Optimized sorting types for performance (v2.0.0+)

---

## Production API (NPM Package)

### Installation
```bash
npm install @reall3d/reall3dviewer
```

### Usage Pattern 1: Built-in Viewer
```typescript
const viewer = new Reall3dViewer({ root: '#gsviewer' });
viewer.addModel(`https://reall3d.com/demo-models/yz.spx`);
```

### Usage Pattern 2: SplatMesh (Three.js Integration)
```typescript
const splatMesh = new SplatMesh({ renderer, scene, controls });
splatMesh.addModel({ url: 'https://reall3d.com/demo-models/yz.spx' });
scene.add(splatMesh);
```

---

## Key Configuration Parameters

| Parameter | Purpose | Recommendation |
|-----------|---------|----------------|
| `maxRenderCountOfMobile` | Rendering limits for low-end devices | Adjust from default if needed |
| `maxRenderCountOfPc` | Rendering limits for high-end devices | Adjust from default if needed |
| `qualityLevel` | Choose based on target device and model | Adaptive adjustment supported |
| `sortType` | Choose optimal sorting algorithm for scenario | No single algorithm optimal for all cases |

---

## .spx Format (CRITICAL)

**Format Specification:** https://github.com/reall3d-com/Reall3dViewer/blob/main/SPX_EN.md  
**Conversion Tool:** https://github.com/gotoeasy/gsbox

### Conversion Command
```bash
gsbox p2x -i /path/to/input.ply -o /path/to/output.spx
```

**Why .spx?**
- Compressed format (smaller file size)
- Optimized for web streaming
- Native Reall3DViewer support
- Production-ready

---

## Live Demo

**URL:** https://reall3d.com/reall3dviewer/index.html

**Query Parameter:**
```
http://hostname:port/index.html?url=your-model-link-address
```

---

## Sample Project

**Reference:** https://github.com/reall3d-com/Reall3dViewer (sample project link in README)

---

## Acknowledgments

Reall3DViewer references these projects:
- https://github.com/antimatter15/splat
- https://github.com/mkkellogg/GaussianSplats3D
- https://github.com/huggingface/gsplat.js
- https://github.com/playcanvas/supersplat
- https://github.com/sxguojf/three-tile

---

## Next Steps for Integration

1. **Install NPM package:** `npm install @reall3d/reall3dviewer`
2. **Study SplatMesh API:** Understand Three.js integration
3. **Read .spx spec:** Understand format structure
4. **Test with demo model:** https://reall3d.com/demo-models/yz.spx
5. **Implement capsule overlay:** Add Three.js objects to scene
6. **WebSocket integration:** Real-time capsule updates

---

**Status:** Repository overview complete. Ready to study source code and API.
