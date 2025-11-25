# Shadow Twin Viewer

Production-ready 3D Gaussian Splatting viewer with real-time capsule overlays for AR/VR environments.

---

## Features

- **Photorealistic Rendering:** Powered by Reall3DViewer + 3D Gaussian Splatting
- **Real-Time Capsule Overlays:** Live data visualization on Shadow Twin models
- **WebSocket Integration:** Real-time capsule updates from Capsule Gateway
- **AR/VR Support:** Mobile AR (ARCore/ARKit) and VR headsets (Quest, Vision Pro)
- **Interactive:** Tap/click capsules to view details and execute actions
- **Metrics Dashboard:** Real-time capsule statistics (critical, warning, active)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ ShadowTwinViewer (TypeScript)                               │
│ ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│ │ Reall3DViewer   │  │ Capsule Overlays │  │  WebSocket  │ │
│ │ (.spx models)   │  │ (Three.js meshes)│  │  (Gateway)  │ │
│ └─────────────────┘  └──────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Shadow Twin 3DGS Models (.spx)                              │
│ - Photorealistic 3D models from LiDAR/photogrammetry        │
│ - Compressed format (10-50 MB per asset)                    │
│ - Stored in S3 for distribution                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Capsule Gateway (WebSocket)                                 │
│ - Real-time capsule updates (new, update, removed)          │
│ - Authentication and authorization                          │
│ - Multi-tenant support                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
npm install @industriverse/shadow-twin-viewer
```

**Dependencies:**
- `@reall3d/reall3dviewer` (3DGS viewer)
- `three` (Three.js for 3D rendering)

---

## Usage

### Basic Example

```typescript
import ShadowTwinViewer from '@industriverse/shadow-twin-viewer';

const viewer = new ShadowTwinViewer({
  container: document.getElementById('viewer'),
  shadowTwinId: 'motor_001',
  capsuleGatewayUrl: 'wss://capsule-gateway.industriverse.io/ws',
  modelBaseUrl: 'https://s3.industriverse.io/shadow-twins',
  qualityLevel: 7
});

await viewer.initialize();
```

### Add Capsule Overlay

```typescript
import * as THREE from 'three';

const capsule = {
  id: 'cap-001',
  title: 'Motor Overheating',
  description: 'Temperature spike detected',
  status: 'critical',
  priority: 5,
  timestamp: new Date().toISOString(),
  source: 'thermal_sensor',
  metadata: { temperature: '95°C' },
  actions: ['acknowledge', 'escalate']
};

const position = new THREE.Vector3(1, 0.5, 0);

viewer.addCapsuleOverlay(capsule, position);
```

### Listen for Capsule Selection

```typescript
container.addEventListener('capsule-selected', (event) => {
  const capsule = event.detail;
  console.log('Capsule selected:', capsule);
  
  // Show details, execute action, etc.
});
```

### Get Capsule Metrics

```typescript
const metrics = viewer.getCapsuleMetrics();

console.log('Total capsules:', metrics.total);
console.log('Critical:', metrics.critical);
console.log('Warning:', metrics.warning);
console.log('Active:', metrics.active);
```

---

## API Reference

### `ShadowTwinViewer`

#### Constructor

```typescript
new ShadowTwinViewer(config: ShadowTwinViewerConfig)
```

**Config Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `container` | `HTMLElement` | ✅ | - | DOM container for viewer |
| `shadowTwinId` | `string` | ✅ | - | Shadow Twin unique identifier |
| `capsuleGatewayUrl` | `string` | ✅ | - | WebSocket URL for Capsule Gateway |
| `modelBaseUrl` | `string` | ❌ | `https://s3.industriverse.io/shadow-twins` | S3 base URL for .spx models |
| `qualityLevel` | `number` | ❌ | `7` | Rendering quality (1-9) |
| `enableAR` | `boolean` | ❌ | `false` | Enable AR mode (mobile) |
| `enableVR` | `boolean` | ❌ | `false` | Enable VR mode (headset) |
| `authToken` | `string` | ❌ | `''` | WebSocket authentication token |

#### Methods

##### `initialize(): Promise<void>`

Initialize viewer and load Shadow Twin model.

```typescript
await viewer.initialize();
```

##### `addCapsuleOverlay(capsule: Capsule, position: THREE.Vector3): void`

Add capsule overlay to scene.

```typescript
viewer.addCapsuleOverlay(capsule, new THREE.Vector3(1, 0.5, 0));
```

##### `removeCapsuleOverlay(capsuleId: string): void`

Remove capsule overlay from scene.

```typescript
viewer.removeCapsuleOverlay('cap-001');
```

##### `getCapsuleMetrics(): CapsuleMetrics`

Get capsule statistics.

```typescript
const metrics = viewer.getCapsuleMetrics();
```

##### `dispose(): void`

Dispose viewer and clean up resources.

```typescript
viewer.dispose();
```

#### Events

##### `capsule-selected`

Emitted when user taps/clicks a capsule.

```typescript
container.addEventListener('capsule-selected', (event) => {
  const capsule = event.detail;
});
```

---

## Types

### `Capsule`

```typescript
interface Capsule {
  id: string;
  title: string;
  description: string;
  status: 'critical' | 'warning' | 'active' | 'resolved' | 'dismissed';
  priority: 1 | 2 | 3 | 4 | 5;
  timestamp: string;
  source: string;
  metadata: Record<string, any>;
  actions: string[];
  position?: THREE.Vector3;
  componentId?: string;
}
```

### `CapsuleMetrics`

```typescript
interface CapsuleMetrics {
  total: number;
  critical: number;
  warning: number;
  active: number;
  resolved: number;
  dismissed: number;
}
```

---

## WebSocket Protocol

### Connection

```
wss://capsule-gateway.industriverse.io/ws?shadowTwinId=motor_001
```

### Authentication

```json
{
  "type": "auth",
  "token": "your-auth-token"
}
```

### Messages

#### New Capsule

```json
{
  "type": "capsule_new",
  "capsule": {
    "id": "cap-001",
    "title": "Motor Overheating",
    "status": "critical",
    ...
  }
}
```

#### Capsule Update

```json
{
  "type": "capsule_update",
  "capsule": {
    "id": "cap-001",
    "status": "resolved",
    ...
  }
}
```

#### Capsule Removed

```json
{
  "type": "capsule_removed",
  "capsuleId": "cap-001"
}
```

---

## Performance

### Targets

- **Rendering:** ≥30 fps at 1080p
- **Model Size:** ≤50 MB per Shadow Twin (.spx compressed)
- **Latency:** ≤100ms capsule update (WebSocket)
- **Memory:** ≤500 MB per Shadow Twin model

### Optimization

1. **Quality Level:** Use `qualityLevel: 7` for production (balance size/quality)
2. **Model Compression:** Use `.spx` format (10x smaller than `.ply`)
3. **Capsule Culling:** Remove off-screen capsules from render loop
4. **WebSocket Throttling:** Batch capsule updates (max 10/second)

---

## AR/VR Support

### Mobile AR (iOS/Android)

```typescript
const viewer = new ShadowTwinViewer({
  ...config,
  enableAR: true
});
```

**Requirements:**
- iOS 12+ (ARKit)
- Android 7+ (ARCore)
- WebXR API support

### VR Headsets (Quest, Vision Pro)

```typescript
const viewer = new ShadowTwinViewer({
  ...config,
  enableVR: true
});
```

**Requirements:**
- Meta Quest 2/3/Pro
- Apple Vision Pro
- HTC Vive
- WebXR API support

---

## Examples

### Example 1: Factory Floor AR

```typescript
// Load factory floor Shadow Twin
const viewer = new ShadowTwinViewer({
  container: document.getElementById('viewer'),
  shadowTwinId: 'factory_floor_01',
  capsuleGatewayUrl: 'wss://capsule-gateway.industriverse.io/ws',
  enableAR: true
});

await viewer.initialize();

// Capsules appear on equipment in AR
// Technician can tap to view details and execute actions
```

### Example 2: Remote VR Walkthrough

```typescript
// Load entire factory in VR
const viewer = new ShadowTwinViewer({
  container: document.getElementById('viewer'),
  shadowTwinId: 'factory_complete',
  capsuleGatewayUrl: 'wss://capsule-gateway.industriverse.io/ws',
  enableVR: true
});

await viewer.initialize();

// Manager can walk through virtual factory
// Point controller at capsules to view details
```

### Example 3: Desktop Monitoring

```typescript
// Load equipment Shadow Twin on desktop
const viewer = new ShadowTwinViewer({
  container: document.getElementById('viewer'),
  shadowTwinId: 'motor_001',
  capsuleGatewayUrl: 'wss://capsule-gateway.industriverse.io/ws'
});

await viewer.initialize();

// Real-time capsule updates displayed on 3D model
// Click capsules to view details
```

---

## Development

### Build

```bash
npm run build
```

### Watch Mode

```bash
npm run dev
```

### Test

```bash
npm test
```

### Lint

```bash
npm run lint
```

---

## Troubleshooting

### Issue: Model not loading

**Solution:** Verify .spx file exists at S3 URL and is accessible

```bash
curl -I https://s3.industriverse.io/shadow-twins/motor_001/motor_001.spx
```

### Issue: WebSocket connection failed

**Solution:** Check Capsule Gateway URL and authentication token

```javascript
console.log('WebSocket URL:', config.capsuleGatewayUrl);
console.log('Auth token:', config.authToken);
```

### Issue: Capsules not appearing

**Solution:** Verify capsule positions are within model bounding box

```javascript
console.log('Capsule position:', capsule.position);
console.log('Model bounds:', viewer.getModelBounds());
```

### Issue: Low frame rate

**Solution:** Reduce quality level or capsule count

```javascript
const viewer = new ShadowTwinViewer({
  ...config,
  qualityLevel: 5  // Lower quality for better performance
});
```

---

## License

MIT

---

## Credits

- **Reall3DViewer:** https://github.com/reall3d-com/Reall3dViewer
- **3D Gaussian Splatting:** https://github.com/graphdeco-inria/gaussian-splatting
- **Three.js:** https://threejs.org

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/industriverse/industriverse/issues
- Email: support@industriverse.io

---

**Status:** Production-ready. Tested on mobile AR, VR headsets, and desktop browsers.
