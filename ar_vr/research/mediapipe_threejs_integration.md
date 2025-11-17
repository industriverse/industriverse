# MediaPipe + Three.js Integration Insights

**Source:** https://tympanus.net/codrops/2024/10/24/creating-a-3d-hand-controller-using-a-webcam-with-mediapipe-and-three-js/

---

## Key Innovation: 2D to 3D Depth Conversion

**Problem:** MediaPipe Hands provides 21 landmarks in 2D space (x, y) with limited z-axis information.

**Solution:** Calculate distance between two landmark points in 2D screen space and use it as depth (z-axis) in 3D scene.

### Implementation Pattern

```javascript
// Select two reference points
const wrist = landmarks.multiHandLandmarks[0][0];  // WRIST
const middleFinger = landmarks.multiHandLandmarks[0][10];  // MIDDLE_FINGER_PIP

// Convert 3D positions to 2D screen space
const depthA = to2D(wrist);
const depthB = to2D(middleFinger);

// Calculate 2D distance
const depthDistance = depthA.distanceTo(depthB);

// Map to 3D depth range
const depthZ = THREE.MathUtils.clamp(
  THREE.MathUtils.mapLinear(depthDistance, 0, 1000, -3, 5),
  -2,
  4
);

// Apply inverted depth (hand near camera = cursor far from camera)
cursor.position.z = -depthZ;
```

**Result:** Full 3D hand tracking with depth control using only a 2D webcam!

---

## MediaPipe Hands API

### Setup

```javascript
import { Hands } from '@mediapipe/hands';

const hands = new Hands({
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
  },
});

hands.setOptions({
  maxNumHands: 1,              // Track single hand
  modelComplexity: 1,          // 0 (lite), 1 (full)
  minDetectionConfidence: 0.5, // Detection threshold
  minTrackingConfidence: 0.5   // Tracking threshold
});

hands.onResults((results) => {
  // Process landmarks
  if (results.multiHandLandmarks.length > 0) {
    const landmarks = results.multiHandLandmarks[0];
    // landmarks[0-20] = 21 hand keypoints
  }
});
```

### 21 Hand Landmarks

| Index | Landmark | Use Case |
|-------|----------|----------|
| 0 | WRIST | Depth reference point |
| 4 | THUMB_TIP | Pinch gesture |
| 8 | INDEX_FINGER_TIP | Pointing gesture |
| 9 | MIDDLE_FINGER_MCP | Center point (x/y control) |
| 10 | MIDDLE_FINGER_PIP | Depth reference point |
| 12 | MIDDLE_FINGER_TIP | Closed fist detection |
| 20 | PINKY_TIP | Gesture recognition |

---

## Gesture Recognition (Custom)

**Closed Fist Detection:**

```javascript
// Get middle finger base and tip
const fingerBase = landmarks.multiHandLandmarks[0][9];  // MCP
const fingerTip = landmarks.multiHandLandmarks[0][12];  // TIP

// Calculate 3D distance
const distance = new THREE.Vector3(
  fingerBase.x - fingerTip.x,
  fingerBase.y - fingerTip.y,
  fingerBase.z - fingerTip.z
).length();

// Detect closed fist
const isClosedFist = distance < 0.35;
```

**Why not use MediaPipe GestureRecognizer?**
- Saves load time and memory
- Custom gestures for specific use cases
- More control over thresholds

---

## Three.js Integration

### Coordinate System Mapping

```javascript
// MediaPipe coordinates: [0, 1] normalized
// Three.js coordinates: [-∞, +∞] world space

// Map MediaPipe to Three.js
for (let i = 0; i < 21; i++) {
  const landmark = landmarks.multiHandLandmarks[0][i];
  
  handMesh.children[i].position.set(
    -landmark.x + 0.5,  // Invert X, center at 0
    -landmark.y + 0.5,  // Invert Y, center at 0
    -landmark.z          // Invert Z for correct depth
  );
}
```

### Collision Detection (AABB)

```javascript
// Axis-Aligned Bounding Box (faster than raycasting)
const cursorBox = new THREE.Box3().setFromObject(cursor);
const objectBox = new THREE.Box3().setFromObject(object);

if (cursorBox.intersectsBox(objectBox)) {
  // Collision detected!
  if (isClosedFist) {
    grabObject(object);
  }
}
```

---

## Performance Optimization

### Targets
- **Hand Tracking:** 30 fps (MediaPipe)
- **Rendering:** 60 fps (Three.js)
- **Latency:** <50ms (hand to cursor)

### Techniques
1. **Model Complexity:** Use `modelComplexity: 1` (full) for accuracy, `0` (lite) for performance
2. **Max Hands:** Set `maxNumHands: 1` unless multi-hand required
3. **Confidence Thresholds:** Balance `minDetectionConfidence` and `minTrackingConfidence`
4. **AABB over Raycasting:** Faster collision detection for simple shapes

---

## Production Integration for Capsule Pins

### Use Case 1: Gesture-Free Capsule Selection

```javascript
// Point at capsule with index finger
const indexTip = landmarks.multiHandLandmarks[0][8];

// Map to 3D cursor
cursor.position.set(
  -indexTip.x + 0.5,
  -indexTip.y + 0.5,
  -depthZ
);

// Detect collision with capsule
if (cursorBox.intersectsBox(capsuleBox)) {
  if (isPinchGesture) {
    selectCapsule(capsule);
  }
}
```

### Use Case 2: Hand Pose for Capsule Actions

```javascript
// Closed fist = Execute capsule
if (isClosedFist && selectedCapsule) {
  executeCapsule(selectedCapsule);
}

// Open palm = Dismiss capsule
if (isOpenPalm && selectedCapsule) {
  dismissCapsule(selectedCapsule);
}

// Thumbs up = Acknowledge capsule
if (isThumbsUp && selectedCapsule) {
  acknowledgeCapsule(selectedCapsule);
}
```

### Use Case 3: Two-Hand Gestures

```javascript
// Track two hands
hands.setOptions({ maxNumHands: 2 });

// Pinch with both hands = Zoom
if (isPinchLeft && isPinchRight) {
  const distance = leftPinch.distanceTo(rightPinch);
  camera.zoom = mapLinear(distance, 0, 1, 0.5, 2);
}

// Rotate with both hands = Rotate Shadow Twin
if (isGrabLeft && isGrabRight) {
  const angle = calculateAngle(leftHand, rightHand);
  shadowTwin.rotation.y = angle;
}
```

---

## Key Takeaways

1. **Accessible Technology:** No expensive hardware required (just webcam)
2. **2D to 3D Magic:** Distance-based depth calculation unlocks full 3D control
3. **Custom Gestures:** Faster and more efficient than pre-built recognizers
4. **AABB Collision:** Simpler and faster than raycasting for basic shapes
5. **Production-Ready:** 30 fps hand tracking + 60 fps rendering achievable

---

## Next Steps for Capsule Pins

1. **Integrate MediaPipe Hands** into ARVRInteractionController
2. **Implement gesture-free capsule selection** (point + pinch)
3. **Add hand pose recognition** (fist, palm, thumbs up)
4. **Test on mobile AR** (iOS/Android webcam)
5. **Optimize for factory environments** (gloves, lighting, occlusion)

---

**Status:** MediaPipe + Three.js integration pattern identified. Ready for implementation.
