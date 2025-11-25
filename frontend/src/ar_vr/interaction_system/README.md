# AR/VR Interaction System

Production-ready gesture controls and platform-specific handlers for mobile AR and VR headsets.

---

## Features

### **Touch Gestures (Mobile AR)**
- ✅ Tap (single, double, triple)
- ✅ Long press (with haptic feedback)
- ✅ Swipe (4 directions with velocity detection)
- ✅ Pinch (zoom in/out)
- ✅ Rotate (two-finger rotation)
- ✅ Pan (two-finger pan)

### **VR Controller Input**
- ✅ Gaze + trigger (point and select)
- ✅ Ray pointing (laser pointer from controller)
- ✅ Controller squeeze (grip button)
- ✅ Hand tracking (Quest 3, Vision Pro)

### **Voice Commands**
- ✅ Speech recognition (Web Speech API)
- ✅ Command parsing ("execute", "hide", "show", "acknowledge")
- ✅ Continuous listening mode
- ✅ Hands-free interaction

### **Spatial Anchoring (AR)**
- ✅ Persist capsule positions across sessions
- ✅ XRAnchor API integration
- ✅ Multi-capsule anchor management

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ ARVRInteractionController                                   │
│ ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│ │   Touch     │  │ VR Controller│  │ Voice Commands   │    │
│ │  Gestures   │  │   Input      │  │ (Speech API)     │    │
│ └─────────────┘  └──────────────┘  └──────────────────┘    │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Spatial Anchoring (XRAnchor API)                    │    │
│ └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ GestureRecognizer                                           │
│ - Advanced touch pattern detection                          │
│ - Multi-touch support (pinch, rotate, pan)                  │
│ - Haptic feedback integration                               │
│ - Velocity-based swipe detection                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
npm install @industriverse/ar-vr-interaction
```

**Dependencies:**
- `three` (Three.js for 3D rendering)
- WebXR Device API (browser support)
- Web Speech API (browser support)

---

## Usage

### Basic Example

```typescript
import ARVRInteractionController from '@industriverse/ar-vr-interaction';
import * as THREE from 'three';

const controller = new ARVRInteractionController({
  scene: scene,
  camera: camera,
  renderer: renderer,
  enableAR: true,
  enableVR: true,
  enableVoice: true,
  onCapsuleSelect: (capsule) => {
    console.log('Capsule selected:', capsule);
  },
  onCapsuleLongPress: (capsule) => {
    console.log('Long press on capsule:', capsule);
  },
  onCapsuleSwipe: (capsule, direction) => {
    console.log(`Swipe ${direction} on capsule:`, capsule);
  },
  onVoiceCommand: (command) => {
    console.log('Voice command:', command);
  }
});
```

### Start AR Session

```typescript
const success = await controller.startARSession();

if (success) {
  console.log('AR session started');
} else {
  console.error('AR not supported or permission denied');
}
```

### Start VR Session

```typescript
const success = await controller.startVRSession();

if (success) {
  console.log('VR session started');
} else {
  console.error('VR not supported or permission denied');
}
```

### Voice Recognition

```typescript
// Start listening
controller.startVoiceRecognition();

// Stop listening
controller.stopVoiceRecognition();
```

### Spatial Anchoring

```typescript
// Create anchor at capsule position
const success = await controller.createSpatialAnchor(
  'capsule-001',
  new THREE.Vector3(1, 0.5, 0)
);

// Remove anchor
controller.removeSpatialAnchor('capsule-001');

// Get all anchors
const anchors = controller.getSpatialAnchors();
```

---

## API Reference

### `ARVRInteractionController`

#### Constructor

```typescript
new ARVRInteractionController(config: ARVRInteractionConfig)
```

**Config Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `scene` | `THREE.Scene` | ✅ | - | Three.js scene |
| `camera` | `THREE.Camera` | ✅ | - | Three.js camera |
| `renderer` | `THREE.WebGLRenderer` | ✅ | - | Three.js renderer |
| `enableAR` | `boolean` | ❌ | `false` | Enable AR mode |
| `enableVR` | `boolean` | ❌ | `false` | Enable VR mode |
| `enableVoice` | `boolean` | ❌ | `false` | Enable voice commands |
| `enableAnchoring` | `boolean` | ❌ | `false` | Enable spatial anchoring |
| `onCapsuleSelect` | `(capsule: any) => void` | ❌ | - | Capsule tap callback |
| `onCapsuleLongPress` | `(capsule: any) => void` | ❌ | - | Capsule long press callback |
| `onCapsuleSwipe` | `(capsule: any, direction: string) => void` | ❌ | - | Capsule swipe callback |
| `onVoiceCommand` | `(command: string) => void` | ❌ | - | Voice command callback |

#### Methods

##### `startARSession(): Promise<boolean>`

Start AR session with WebXR.

```typescript
const success = await controller.startARSession();
```

##### `startVRSession(): Promise<boolean>`

Start VR session with WebXR.

```typescript
const success = await controller.startVRSession();
```

##### `endXRSession(): Promise<void>`

End current XR session.

```typescript
await controller.endXRSession();
```

##### `startVoiceRecognition(): void`

Start listening for voice commands.

```typescript
controller.startVoiceRecognition();
```

##### `stopVoiceRecognition(): void`

Stop listening for voice commands.

```typescript
controller.stopVoiceRecognition();
```

##### `createSpatialAnchor(capsuleId: string, position: THREE.Vector3): Promise<boolean>`

Create spatial anchor at position.

```typescript
await controller.createSpatialAnchor('cap-001', new THREE.Vector3(1, 0.5, 0));
```

##### `removeSpatialAnchor(capsuleId: string): void`

Remove spatial anchor.

```typescript
controller.removeSpatialAnchor('cap-001');
```

##### `getSpatialAnchors(): Map<string, XRAnchor>`

Get all spatial anchors.

```typescript
const anchors = controller.getSpatialAnchors();
```

##### `dispose(): void`

Dispose controller and clean up resources.

```typescript
controller.dispose();
```

---

### `GestureRecognizer`

#### Constructor

```typescript
new GestureRecognizer(config: GestureRecognizerConfig)
```

**Config Options:**

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `element` | `HTMLElement` | ✅ | - | DOM element to attach listeners |
| `onGesture` | `(event: GestureEvent) => void` | ❌ | - | Gesture callback |
| `tapThreshold` | `number` | ❌ | `300` | Tap threshold (ms) |
| `longPressThreshold` | `number` | ❌ | `500` | Long press threshold (ms) |
| `swipeVelocityThreshold` | `number` | ❌ | `0.5` | Swipe velocity threshold (px/ms) |
| `enableHaptics` | `boolean` | ❌ | `true` | Enable haptic feedback |

#### Methods

##### `dispose(): void`

Dispose gesture recognizer.

```typescript
recognizer.dispose();
```

---

## Gesture Types

### Touch Gestures

| Gesture | Description | Trigger |
|---------|-------------|---------|
| `tap` | Single tap | Touch < 300ms, no movement |
| `double-tap` | Double tap | Two taps within 300ms |
| `triple-tap` | Triple tap | Three taps within 300ms |
| `long-press` | Long press | Touch > 500ms, no movement |
| `swipe-left` | Swipe left | Fast horizontal movement left |
| `swipe-right` | Swipe right | Fast horizontal movement right |
| `swipe-up` | Swipe up | Fast vertical movement up |
| `swipe-down` | Swipe down | Fast vertical movement down |
| `pinch-in` | Pinch to zoom in | Two-finger pinch closer |
| `pinch-out` | Pinch to zoom out | Two-finger pinch apart |
| `rotate-cw` | Rotate clockwise | Two-finger rotation CW |
| `rotate-ccw` | Rotate counter-clockwise | Two-finger rotation CCW |
| `pan` | Two-finger pan | Two-finger drag |

### Voice Commands

| Command | Variations | Action |
|---------|-----------|--------|
| `execute` | "execute", "run" | Execute capsule action |
| `hide` | "hide", "dismiss" | Hide capsule |
| `show` | "show", "display" | Show capsule |
| `acknowledge` | "acknowledge", "confirm" | Acknowledge capsule |

---

## Platform Support

### Mobile AR

| Platform | Version | Status |
|----------|---------|--------|
| iOS (ARKit) | 12+ | ✅ Supported |
| Android (ARCore) | 7+ | ✅ Supported |

**Requirements:**
- WebXR Device API support
- Camera permission
- Motion sensors

### VR Headsets

| Device | Status |
|--------|--------|
| Meta Quest 2 | ✅ Supported |
| Meta Quest 3 | ✅ Supported |
| Meta Quest Pro | ✅ Supported |
| Apple Vision Pro | ✅ Supported |
| HTC Vive | ✅ Supported |
| Valve Index | ✅ Supported |

**Requirements:**
- WebXR Device API support
- VR headset with controllers

### Voice Recognition

| Browser | Status |
|---------|--------|
| Chrome | ✅ Supported |
| Edge | ✅ Supported |
| Safari | ⚠️ Limited (iOS 14.5+) |
| Firefox | ❌ Not supported |

**Requirements:**
- Web Speech API support
- Microphone permission

---

## Examples

### Example 1: Mobile AR with Gestures

```typescript
const controller = new ARVRInteractionController({
  scene, camera, renderer,
  enableAR: true,
  onCapsuleSelect: (capsule) => {
    // Show capsule details
    showCapsuleModal(capsule);
  },
  onCapsuleSwipe: (capsule, direction) => {
    // Swipe left to dismiss, right to execute
    if (direction === 'left') {
      dismissCapsule(capsule);
    } else if (direction === 'right') {
      executeCapsule(capsule);
    }
  }
});

await controller.startARSession();
```

### Example 2: VR with Voice Commands

```typescript
const controller = new ARVRInteractionController({
  scene, camera, renderer,
  enableVR: true,
  enableVoice: true,
  onCapsuleSelect: (capsule) => {
    // Highlight selected capsule
    highlightCapsule(capsule);
  },
  onVoiceCommand: (command) => {
    // Execute voice command on selected capsule
    if (command === 'execute') {
      executeSelectedCapsule();
    }
  }
});

await controller.startVRSession();
controller.startVoiceRecognition();
```

### Example 3: Spatial Anchoring

```typescript
const controller = new ARVRInteractionController({
  scene, camera, renderer,
  enableAR: true,
  enableAnchoring: true
});

await controller.startARSession();

// Create anchor when capsule is placed
const success = await controller.createSpatialAnchor(
  capsule.id,
  capsule.position
);

if (success) {
  console.log('Capsule position anchored in AR space');
}

// Restore anchors on next session
const anchors = controller.getSpatialAnchors();
anchors.forEach((anchor, capsuleId) => {
  restoreCapsule(capsuleId, anchor);
});
```

---

## Performance

### Targets

- **Gesture Recognition:** ≤10ms latency
- **Voice Recognition:** ≤500ms latency
- **Haptic Feedback:** ≤50ms latency
- **Frame Rate:** ≥60 fps (AR/VR)

### Optimization

1. **Debounce Gestures:** Prevent duplicate gesture events
2. **Throttle Voice:** Limit voice command processing to 1/second
3. **Lazy Raycasting:** Only raycast on user interaction
4. **Spatial Anchor Caching:** Cache anchor positions locally

---

## Troubleshooting

### Issue: AR session not starting

**Solution:** Check WebXR support and camera permissions

```javascript
if (!navigator.xr) {
  console.error('WebXR not supported');
}

// Request camera permission
navigator.mediaDevices.getUserMedia({ video: true });
```

### Issue: Voice recognition not working

**Solution:** Check browser support and microphone permissions

```javascript
if (!('webkitSpeechRecognition' in window)) {
  console.error('Speech recognition not supported');
}

// Request microphone permission
navigator.mediaDevices.getUserMedia({ audio: true });
```

### Issue: Gestures not detected

**Solution:** Ensure `touch-action: none` on canvas

```css
canvas {
  touch-action: none;
}
```

### Issue: VR controllers not appearing

**Solution:** Verify WebXR VR session and controller connection

```javascript
renderer.xr.enabled = true;
const session = await navigator.xr.requestSession('immersive-vr');
```

---

## License

MIT

---

## Credits

- **WebXR Device API:** https://immersiveweb.dev
- **Web Speech API:** https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Three.js:** https://threejs.org
- **Hammer.js:** https://hammerjs.github.io (gesture pattern inspiration)

---

**Status:** Production-ready. Tested on iOS ARKit, Android ARCore, Meta Quest 3, and Apple Vision Pro.
